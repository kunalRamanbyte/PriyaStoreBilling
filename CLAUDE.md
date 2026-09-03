# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
python main.py
```

Default credentials: `admin` / `admin123`, `cashier` / `cash123` (seeded on first `init_db()`).

## Installing Dependencies

```bash
pip install -r requirements.txt
```

Core packages (in `requirements.txt`): `customtkinter>=5.2.0`, `Pillow>=10.0.0`, `openpyxl>=3.1.0`, `reportlab>=4.0.0`, `tkcalendar>=1.6.0` (date picker), `opencv-contrib-python>=4.8.0` (webcam scanner — note the `-contrib` build, which bundles the QR/barcode detector).

Optional (not in `requirements.txt`, guarded by try/import): `python-escpos`, `pywin32` (thermal printer).

## Running Tests

```bash
python verify_screens.py
```

This is the only test suite. It instantiates every screen with the **real** `billing_data.db`, calls `on_show()`, and asserts on the result. It runs headless (the root window is `withdraw()`n). Exit code is 0 on all pass, 1 on any failure.

Coverage is uneven, and worth knowing before you trust a green run:
- **`ROW_COLORS` tags are asserted on 7 screens only** — Billing, Bill History, Products, Inventory, Suppliers, Purchase/GRN, Customers. Categories, Reports, Settings, Users, Activity Log and Dashboard are "loads without error" only, so a treeview on one of those can skip the tagging pattern and still pass.
- **Every treeview's `style=` name is checked** against `styles.STYLE_NAMES` (`test_tree_styles_registered` walks the built widget tree), so a missing style registration fails loudly.

There is no per-test CLI filter — to test one screen in isolation, replicate both stubs from `verify_screens.py`. `FakeApp` must carry `current_lang` and `current_theme`, because screens read them during construction; the user dict must carry `name`, because screens read `current_user["name"]`:

```python
user = {"user_id": 1, "username": "admin", "name": "Admin", "role": "admin"}

class FakeApp:
    screens = {}
    current_role = "admin"
    current_lang = "English"
    current_theme = "Light"
    def navigate_to(self, *a, **kw): pass
    def rebuild_screen(self, *a, **kw): pass
```

## Building the Executable

```bash
python run_build.py
```

Runs PyInstaller with `PriyaStore.spec`, then **seeds a fresh empty `billing_data.db`** and creates `backups/` in `dist/PriyaStore/`. stdout/stderr land in `build_log.txt`; the return code lands in `build_done.txt`. Output is `dist/PriyaStore/`.

> `run_build.py` must never copy the live `billing_data.db` into `dist/`. The installer packages whatever sits there, so copying it ships this shop's real bills, customer names and phone numbers, udhaar balances and the `users` table (password hashes included) inside every Setup `.exe`. `seed_fresh_db()` deletes any stale file (plus `-wal`/`-shm`) and calls `init_db()`, which creates the schema and seeds the default accounts.

Alternatively:
```bash
pyinstaller PriyaStore.spec --noconfirm
```

New third-party imports usually need to be added to `hiddenimports` (and often `collect_all`) in `PriyaStore.spec` — a missing entry builds fine and crashes only at runtime in the frozen app.

### Windows Installer

`PriyaStore_installer.iss` is an Inno Setup script that packages `dist/PriyaStore/` into `installer/PriyaStore_Setup_v<N>.exe`. It installs to `C:\PriyaStore` with `PrivilegesRequired=lowest`, and ships the freshly seeded `billing_data.db` with `onlyifdoesntexist` so an upgrade never clobbers live shop data. All its paths are **relative to the `.iss` file**, so it builds from any checkout — never reintroduce an absolute `C:\Users\...` prefix.

Releasing means bumping three things together: `AppVersion`, `OutputBaseFilename`, and `config.APP_VERSION` (shown in the window title, so a shop can report which build it runs).

> The script deliberately has **no `[UninstallDelete]` section**. A blanket `Type: filesandordirs; Name: "{app}"` also deletes `billing_data.db` (with its `-wal`/`-shm` sidecars) and the default `backups/` folder beside it — wiping every bill, customer, udhaar balance and local backup the shop has. Uninstall must remove only what Setup installed.

Built installers are gitignored (`installer/*.exe`) — they are ~68 MB each and must not enter git history.

> `KunalBilling.spec` and `billing.spec` are older/unused specs. `database_fixed.py` and `main_fixed.py` are stale intermediate files — do not use them. `AGENTS.md` is now just a pointer to this file; CLAUDE.md is the only place project guidance lives.

## Architecture

### Entry Point & Navigation

`main.py` → `BillingApp(ctk.CTk)` is the root window. After login it builds a header + sidebar + `content_area` frame. Navigation goes through `navigate_to(screen_name)`, which:

1. **Enforces role access** against `self._screen_roles` (built from the `NAV` list in `_build_sidebar`) and shows an "Access Denied" warning on failure — so non-sidebar entry points (dashboard quick actions, resume-draft) cannot escalate.
2. Calls `on_hide()` on the outgoing screen if it defines one.
3. Lazily instantiates the target screen on first visit and caches it in `self.screens`.
4. `pack_forget()`s the others and `pack()`s the target, then calls `on_show()`.

Screens are **never destroyed** between visits unless `rebuild_screen()` is called explicitly (which destroys and re-instantiates). `apply_language()` and `apply_theme()` destroy every cached screen and rebuild the whole main window.

### Screen Construction Contract

Every screen (e.g. `screen_billing.py`) follows the same pattern:
- Constructor: build all widgets once; receives `(parent, db, current_user, app)` where `current_user` is `{"user_id": int, "username": str, "name": str, "role": str}`
- `on_show()`: reload data from DB and refresh the UI
- `on_hide()` (optional): tear down floating `CTkToplevel` overlays — the billing/GRN search-suggestion popups stay on top of the next screen otherwise
- Use `self.app.navigate_to(key)` to switch screens. Use `self.app.rebuild_screen(key)` only when the constructor must re-run (e.g. a setting changed the widget layout).

> `ReportScreen` is the exception: it loads on construction and has no `on_show()`.

### Popup / Dialog Pattern

Every `CTkToplevel` dialog **must** call `place_popup(dlg, logical_w, logical_h, parent)` from `ui_utils.py` right after creation instead of calling `dlg.geometry()` directly. This corrects for widget-scaling vs window-scaling mismatch on high-DPI displays, clamps to the screen, and centres over the parent window.

### Database Layer (`database.py`)

Raw `sqlite3` — no ORM. All queries live in `Database`.

`get_conn()` is a **`@contextmanager`** — always `with self.get_conn() as conn:`. It commits on clean exit, rolls back on exception, and always closes (so WAL checkpoints promptly instead of waiting on GC). `PRAGMA foreign_keys=ON` and `synchronous=NORMAL` are set per connection; `journal_mode=WAL` is persistent and set once in `init_db()`.

Key invariants:
- **Document numbers are claimed inside the write transaction.** `save_bill()`, `save_draft_bill()`, `save_purchase()`, and `save_return()` each open `BEGIN IMMEDIATE` and call `_claim_number(conn, setting_key, prefix, fallback_sql)`, which reads and bumps the counter atomically. `next_bill_number()` / `next_grn_number()` are **display-only previews** — never use them to assign a number, and don't reintroduce a post-commit `increment_bill_number()` (deleted; two tills could claim the same number) into a save path.
- `save_bill()` deducts stock, `save_purchase()` increases stock and updates `purchase_price`, `void_bill()` restores stock, `save_return()` restocks per line (only where `restocked=1`) — all in the same transaction as their document row.
- `save_return()` re-validates returnable quantities *inside* the transaction against `sales_return_items` and raises `ValueError` if a line over-returns (guards a stale dialog).
- `void_bill()` refuses (`return False`) when `bill_has_returns()` is true — returns have already restocked/refunded, so a full reversal would double-count.
- Schema changes: add `CREATE TABLE IF NOT EXISTS` to the `executescript` block, new columns to the `migrations` list (`try/except` ALTER TABLE), and new indexes to the `Performance indexes` list — all inside `init_db()`.

DB path: `billing_data.db` next to the script (or next to the `.exe` when frozen). `config.DB_PATH` resolves this correctly for both environments.

**Tables:** `users`, `categories`, `customers`, `products`, `bills`, `bill_items`, `settings`, `activity_log`, `suppliers`, `purchase_entries`, `purchase_items`, `stock_adjustments`, `customer_transactions`, `supplier_payments`, `sales_returns`, `sales_return_items`

### Customer Money Model (Udhaar / Change)

A customer carries two balances: `credit_balance` (udhaar owed to the shop) and `change_balance` (change the shop owes back). Every movement writes a `customer_transactions` row with `txn_type` in `Credit`, `Payment`, `Change Deposit`, `Change Clear`, `Store Credit`, `Refund`.

**Invariant: a customer can never hold positive credit *and* positive change at once.** `_net_customer_balances(conn, customer_id, user_id, reference)` offsets them and logs both sides of the netting. Call it at the end of any transaction that touches either balance — `save_bill()`, `void_bill()`, and `add_customer_transaction()` all do.

`void_bill()` mirrors the exact credit/change arithmetic that `save_bill()` applied and writes reversing transactions, so keep the two in sync if you change either.

### Sales Returns / Refunds

Returns are driven from **Bill History** (`_return_bill`, admin-only), not a dedicated screen. `get_returnable_items(bill_id)` annotates each bill line with `already_returned` / `returnable`; `save_return()` records the return and routes the refund by `refund_mode`: `Cash` (log only), `Credit Adjust` (reduce udhaar), or `Store Credit` (increase change balance). Receipts print via `print_thermal_return()` / `generate_return_pdf()`.

### Auth & Passwords

Passwords are salted **PBKDF2-HMAC-SHA256** (200k iterations), stored as `pbkdf2_sha256$iters$salt$hash` — see `hash_password()` / `verify_password()` in `database.py`. `authenticate()` also accepts legacy bare SHA-256 hashes (constant-time compare) and **transparently re-hashes them to PBKDF2 on successful login**; never widen this fallback. It strips `password_hash` before returning the user dict.

`is_default_admin_active()` reports whether `admin` still uses `admin123` — the login screen only shows the credentials hint while that is true.

### Row Coloring Pattern (all treeviews)

Every treeview uses a rotating 6-colour pastel palette defined as `COLORS["ROW_COLORS"]` in `config.py`. The pattern is:

1. After inserting each row, tag it with `f"row{i % 6}"` where `i` is the row index.
2. After populating the tree, configure each tag's background:
   ```python
   for i, color in enumerate(COLORS["ROW_COLORS"]):
       tree.tag_configure(f"row{i}", background=color)
   ```

Special rows (low-stock, void bills, etc.) use override tags like `"low_stock"`, `"void"`, `"draft"` which are configured separately and take precedence. `verify_screens.py` asserts this pattern on **7 of the 13 screens** (see Running Tests above) — a new treeview on one of the untested screens will pass anyway, so apply the pattern on your own account. Activity Log is a deliberate exception: it colours rows by action rather than by index.

### Internationalisation (`lang.py`)

The app supports English, Bengali, and Hindi. Every visible UI string must go through `t(key, lang)` from `lang.py`, where `key` is the English string and `lang` is `app.current_lang`. New strings must be added to the `T` dict with all three translations (index 0 = English, 1 = Bengali, 2 = Hindi). An unknown key falls back to returning the key itself, so a missing translation looks fine in English and silently breaks Bengali/Hindi.

The language setting is stored in the `settings` table as `app_language` with values `"English"`, `"Bengali"`, or `"Hindi"` (`lang.LANG_DB_VALUES`); `lang.LANGUAGES` holds the display labels.

### Dark / Light Theme

Theme is stored in the `settings` table as `app_theme`. On startup, `main.py` applies it via `ctk.set_appearance_mode()` and then calls `apply_theme_mode(mode)` from `config.py`, which swaps the global `COLORS` dict between `LIGHT_COLORS` and `DARK_COLORS`. All screen files read colours from `COLORS` at widget-creation time, so theme changes take effect on a full rebuild. Never read from `LIGHT_COLORS` or `DARK_COLORS` directly in screen files — always use `COLORS`.

### Shared UI Helpers (`ui_utils.py`)

Two helpers beyond `place_popup`:

- **`open_date_picker(parent, var, title)`** — opens a `tkcalendar` popup and writes the selected date (YYYY-MM-DD) into a `tk.StringVar`. Requires `tkcalendar`; shows an install error if missing.
- **`WebcamScanner`** in `webcam_scanner.py` — a reusable `CTkToplevel` that opens a live webcam feed, decodes QR/barcodes via `cv2`, and fires a callback on success.

### Activity Logging

Call `db.log_activity(user_id, action, details)` after every meaningful state change.

`screen_activity_log._row_colors(action)` colour-codes rows by **prefix match only** — it walks `COLORS["LOG_ROW_COLORS"]` and returns the first key that `action.startswith()`, falling back to `COLORS["LOG_ROW_DEFAULT"]`. There is no exact-match stage, so a map key must be *at or shorter than* the action it needs to catch: keying on `BILL_VOID` catches both `BILL_VOID` and `BILL_VOIDED`, but keying on `BILL_VOIDED` catches neither shorter form.

The palette lives in `config.py` (one `LOG_ROW_COLORS` map inside `LIGHT_COLORS`, one inside `DARK_COLORS`, swapped by `apply_theme_mode()`) — never hardcode these colours in the screen. Add a new action's key to **both** maps; keep the key sets identical.

Coloured keys: `LOGIN`, `LOGOUT`, `BILL_SAVED`, `BILL_VOID`, `RETURN_SAVED`, `CUSTOMER_CHANGE_CLEAR`, `USER_*`, `SETTINGS_SAVED`, `PWD_CHANGED`, `FORMAT_DATA` (factory reset — deliberately the loudest red in both themes).

Actions written elsewhere that are *not* in the map — `PURCHASE_SAVED`, `CUSTOMER_ADDED/UPDATED/DELETED`, `SUPPLIER_ADDED/UPDATED/DELETED/DEACTIVATED`, `SUPPLIER_PAYMENT` — fall through to the default row colour, which is deliberately distinct from `BILL_SAVED` in both themes.

> **Known gap:** `screen_products.py`, `screen_inventory.py` and `screen_purchase.py` call `log_activity` **nowhere**, so product add/edit/delete and stock adjustments leave no audit trail at all. Only keys some code actually writes belong in the map — don't add a `PRODUCT_*` colour without first adding the logging calls.

### Config & Styling

- **`config.py`** — single source of truth for `COLORS`, `FONTS`, `RADII`, `APP_TITLE`, `APP_VERSION`, `SHOP_NAME`, `WINDOW_WIDTH/HEIGHT`, `SIDEBAR_WIDTH`, `UNITS`, `PAYMENT_MODES`, `CAT_COLORS`, `SHORTCUTS`. Never hardcode colors or font sizes in screen files.
- **`styles.py`** — `setup_ttk_styles(mode="light")` registers every named `ttk.Treeview` and `TScrollbar` style once at startup, and again on theme switch. Each screen references its pre-registered style by name (e.g. `"Bill.Treeview"`). Never create a new `ttk.Style()` inside a screen. Style prefixes: `Dash`, `Bill`, `Prod`, `Inv`, `Adj`, `Sup`, `Cust`, `Rpt`, `Purch`, `Pur`, `GRN`, `User`, `Log`, `Cat`, `Exp`, `Cart`, `Led`. `Exp` (dashboard expiry panel) and `Cart` (POS) intentionally override the shared header colours.
  **Any name a screen passes as `style="X.Treeview"` must be in `styles.STYLE_NAMES`** (module-level, so tests can import it). ttk resolves an unknown style name to the base `Treeview` style *without raising*, so the table would silently render with clam's grey header and default row height instead of the 48px/near-black design. `verify_screens.test_tree_styles_registered` walks every built screen and fails on an unregistered name, so this no longer fails silently. (`Purch` and `Cat` are currently registered but referenced by no screen.)
- **`config.resource_path(*parts)`** — use this for any asset path (icons, images) so it works both in source and PyInstaller builds.

### Role-Based Access

Three roles: `admin`, `cashier`, `stock_manager`. The `NAV` list in `main.py:_build_sidebar` is the authoritative screen→roles map: it both filters the sidebar and populates `_screen_roles`, which `navigate_to()` checks on every navigation. Adding a screen means adding it to `NAV` *and* to the `klasses` dict in `navigate_to()`. Screens still don't enforce access internally — in-screen privileged actions (e.g. Return/Refund in Bill History) check `current_user["role"]` themselves.

### Bill Printing (`bill_printer.py`)

- `generate_pdf_bill(bill, items, settings)` / `generate_return_pdf(...)` → ReportLab A4 PDF written to a temp dir (pruned after 7 days), then opened with the OS default viewer via `open_file()`
- `print_thermal(bill, items, settings, paper_width)` / `print_thermal_return(...)` → ESC/POS, guarded by try/import; both return `(ok, msg)`
- Receipt content is built as `(text, style)` row tuples — **never pre-centre text**, so the ESC/POS path can centre in hardware while the plain-text fallback centres with spaces
- Character width is derived from the `paper_width` setting: 32 chars for `58mm`, 48 for `80mm`
- Virtual/non-thermal default printers are detected (`_looks_non_thermal`) and shown a readable text preview instead of raw bytes, which would otherwise produce a corrupt file

### Backup & Restore

`screen_settings._run_backup(db, label=None)` copies the live DB to the `backup_folder` setting (or `backups/` next to the DB) as `billing_backup[_label]_<timestamp>.db`, and prunes to the **10 most recent** files matching that pattern by mtime — it deliberately never touches unrelated `.db` files in a user-chosen USB/Drive folder. Called on app close and every 24 h via `BillingApp._schedule_daily_backup()`; the `auto_backup_enabled` setting is read live at each tick.

Restore validates the chosen file with `_is_valid_sqlite()` (header magic + `PRAGMA schema_version`), takes a `pre_restore` safety backup, copies over the live DB, then **deletes the `-wal` and `-shm` sidecars** so the old DB's uncheckpointed frames aren't replayed into the restored file.

## UI Conventions

- Font sizes: `FONTS["body"]=16`, `FONTS["heading"]=27`. Keep large for 60+ users.
- Sidebar: deep navy gradient (`COLORS["sidebar_grad_start"]` → `sidebar_grad_end`), drawn with a `tk.Canvas` gradient loop debounced on `<Configure>`. Nav buttons live in a `CTkScrollableFrame` so they never overflow on short screens.
- Cards: white with `COLORS["glass_border"]` borders — glassmorphism aesthetic.
- Tables: all use `ttk.Treeview` with 48px row height. Always use the screen-specific named style and the ROW_COLORS tagging pattern described above.
- Shop name is always "Priya Store" — enforced on every startup via `db.set_setting("shop_name", "Priya Store")`, which is why Settings deliberately has no shop-name field.
- Billing screen keyboard shortcuts: `F2` search product, `F8` hold bill, `F10` print & save, `Ctrl+N` new bill, `Esc` close popup or clear cart — all bound on the **toplevel**, so they are armed in `on_show()` (`_bind_root_keys`) and disarmed in `on_hide()` (`_unbind_root_keys`). Never bind them in the constructor: screens are cached and never destroyed, so a leftover binding keeps firing on every other screen — F10 would save and print a bill, and Esc would clear the cart, while the user is looking at Products. `Del` (remove item) is bound on `cart_tree` itself and needs no teardown.
- Responsive window: `_compute_fit()` scales from a 1280×720 floor to a 4K ceiling inside a 16:10–16:9 aspect band. Widget scaling is set once via `ctk.set_widget_scaling()` — never call it again after startup.

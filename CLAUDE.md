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

There are three suites:

```bash
python verify_screens.py    # 16 checks — screens build, ROW_COLORS, styles
python verify_motion.py     # 23 checks — the motion layer and navigation
python verify_sidebar.py    # 24 checks — the collapsible sidebar
```

`verify_screens.py` instantiates every screen with the **real** `billing_data.db`, calls `on_show()`, and asserts on the result. It stubs a `FakeApp` (see below), so it never exercises the real sidebar or `navigate_to()` — it runs headless (the root window is `withdraw()`n). `verify_motion.py` and `verify_sidebar.py` both build the real `BillingApp` instead, to cover what the stub cannot: navigation, the motion layer, and the collapsible sidebar. All three exit 0 on success, 1 on any failure.

> `verify_motion.py` writes to the `settings` table and restores it in a
> `finally:` block. Keep that block — an earlier version crashed mid-run and
> left the shop's live database on a different language and theme.

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

`main.py` → `BillingApp(ctk.CTk)` is the root window. After login it builds a sidebar + `content_area` frame. There is **no global header band**: the brand lives in the sidebar and every screen draws its own title header. Navigation goes through `navigate_to(screen_name)`, which:

1. **Enforces role access** against `self._screen_roles` (built from the `NAV` list in `_build_sidebar`) and shows an "Access Denied" warning on failure — so non-sidebar entry points (dashboard quick actions, resume-draft) cannot escalate.
2. Calls `on_hide()` on the outgoing screen if it defines one.
3. **`place_forget()`s every other cached screen.** Tk's focus ring (Tab / Shift-Tab) skips **unmapped** widgets only — a screen that is merely covered by the one on top of it is still fully Tab-reachable. Before this, Tab could walk a cashier out of the visible screen and into any of the twelve cached-but-hidden ones (worst case: Billing's `cart_tree`, which binds `<Delete>` to removing a cart line — an invisible focus there could silently edit a held bill). Any in-flight slide animation on the screen being forgotten is landed first via `motion.cancel()`, because a slide's tween keeps calling `place_configure()` on every tick — including its own last one — which would otherwise silently re-map a screen already forgotten.
4. Lazily instantiates the target screen on first visit and caches it in `self.screens`.
5. `place()`s the target at `x=0, relwidth=1, relheight=1` on its first
   visit (or re-places it if this run's `place_forget()` pass unmapped it),
   then calls `on_show()`, parks the screen 28px right, `lift()`s it,
   forces the repaint, and only then starts the slide home.

> The order matters and is not arbitrary. `on_show()`'s reload and the first
> repaint are both paid *before* a single animation frame is scheduled, so
> the slide runs on a clean budget instead of stuttering on frame one. The
> park must also happen before the repaint: park after it and Tk paints the
> screen at home first, so the opening frame snaps it sideways.

> Screens are managed by **`place`, not `pack`**. `pack_forget()`/`pack()` made
> Tk relayout the incoming screen's entire widget tree on every visit —
> measured at 60–125ms of frozen UI per navigation, against ~9ms for
> `on_show()`'s database reload. `lift()` is a stacking-order change and does
> no geometry work. Never reintroduce `pack()` for a screen: it silently
> restores the freeze.

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

Every treeview uses a rotating 6-entry palette defined as `COLORS["ROW_COLORS"]` in `config.py`. Under Direction B this is a **whisper zebra** (white / `#F7F9FD`, alternating) rather than the old pastels — the design spends colour on *coding*, not on fills behind numbers, so meaning arrives through the override tags instead. The pattern is:

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

### Motion (`motion.py`)

`config.MOTION` holds every timing: `slide_px` 28, `slide_ms` 160, `fade_ms`
120, `blend_ms` 120. Never hardcode a duration in a screen.

Two measurements govern this module:

- **Translating is cheap, resizing is not.** `place_configure(x=…)` costs
  5–9ms a frame; changing any width that participates in layout costs
  32–126ms, because the geometry manager re-solves the containing window.
  Animate position and window `-alpha` only. This is why the sidebar collapse
  is *not* animated — a width tween on the rail measured 126ms per frame.
- **Tweens are time-driven, never frame-driven.** Each tick computes
  `t = elapsed / duration`. A `for i in range(20)` loop stretches a 160ms
  animation into a 600ms crawl on slow hardware.

`motion.cancel(widget)` lands a superseded animation on its end state rather
than abandoning it, so rapid navigation cannot strand a screen off-position.
Starting a second tween on the same widget cancels the first automatically.

Popups fade through `place_popup()`, the single chokepoint for 21 dialog
sites. The billing/GRN search-suggestion dropdowns are hand-built
`tk.Toplevel`s that never call it, so they stay instant — which is what a
dropdown appearing mid-keystroke needs. Don't route them through
`place_popup()`.

The `animations_enabled` setting (Settings → Language & Theme) turns all of it
off; every helper then applies its final state immediately.

### Categories reload guard (`screen_categories.py`)

`_load_categories()` (called from `on_show()`) used to destroy and rebuild
every category card on every visit — profiled at ~449ms, almost none of it
the query. It now computes a signature tuple —
`(category_id, name, colour_code, is_active)` per row — and returns
immediately when the signature matches the previous visit's, leaving the
existing card widgets untouched. `_cards_sig` is only written *after* the
rebuild loop completes, not before, so a card-build exception can't cache a
half-built grid and lock it in for the rest of the screen's life.

> **Side effect worth knowing:** an unchanged revisit now returns before the
> `yview_moveto(0)` call, so the card list keeps whatever scroll position the
> user left it at instead of always snapping back to the top. This shipped as
> a side effect of the reload guard, not a deliberate UX decision — arguably
> an improvement, but undocumented until now.

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
  **Any name a screen passes as `style="X.Treeview"` must be in `styles.STYLE_NAMES`** (module-level, so tests can import it). ttk resolves an unknown style name to the base `Treeview` style *without raising*, so the table would silently render with clam's grey header and default row height instead of the Direction B header and row height. `verify_screens.test_tree_styles_registered` walks every built screen and fails on an unregistered name, so this no longer fails silently. (`Purch` and `Cat` are currently registered but referenced by no screen.)
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

- **Design system: Direction B** — "soft, rounded, colour with a job", imported from the Claude Design project `Priya Store - Before & After.dc.html`. One vivid blue carries every action; four hues are each locked to a single meaning and never used decoratively: violet counts, teal money-in, amber expiry, coral stock risk, plus a destructive red. Use the `accent_*` tokens, never a raw hex.
- Every surface is a **solid fill, a hairline border or a corner radius**. No gradient, blur, shadow or translucency — CustomTkinter cannot draw them, so anything of the sort is a bug, not a stylistic choice.
- **Dark text on tinted surfaces only.** A vivid hue is an icon, a pill or an accent on its own pale tint; body text on a tint takes the dark variant of the same family (`accent_expiry_fg`, `accent_stock_fg`, `accent_counts_fg`). Every foreground clears 4.5:1. `btn_warning` and `btn_purple` are deliberately deepened because existing code puts white text on them.
- Type: a strict three-step scale — 13px captions, 14–15px labels, 16–17px body **and every figure**. Headings and figures step up from there (`FONTS["heading"]=26`, `subheading`=19, `num_md`=28, `num_xl`=42). Nothing sits between the steps.
- Geometry comes from `RADII` and `METRICS`: 24px cards, 44px pill controls (radius = half the height), 14px nav items and icon bubbles, 36px on the login card.
- Sidebar: a **white surface**, 236px, with a rounded brand mark and 44px nav pills. A solid `sidebar_active` fill marks the current screen — there is no gradient and no glow border. The `sidebar_grad_*` tokens survive only so old readers resolve; both ends are the flat surface colour. Nav buttons live in a `CTkScrollableFrame` so they never overflow on short screens.
- Cards: solid `bg_card` with a 1px `hairline` border and `RADII["card"]` corners.
- Tables: `ttk.Treeview` with a quiet uppercase 13px header on the card surface (no dark band) and per-table row heights from `styles.ROW_HEIGHTS` — 62 Bill History, 60 POS cart, 58 Reports, 56 elsewhere. `Exp` (dashboard expiry panel) is the **one** deliberate header override, on the amber tint. Always use the screen-specific named style and the ROW_COLORS tagging pattern above.
- Buttons rank by weight: exactly one solid fill per screen for the primary action; everything else is a tint with dark ink. Most screens keep a local `_pill(parent, text, kind=...)` helper for this.

> **Beware `CTkFrame`'s default 200×200.** An empty frame, or one with
> `pack_propagate(False)` and no explicit height, holds that size and leaks it
> into the layout. This caused five separate defects during the Direction B
> work: 200px-tall settings rows, a 150px gap in the Bill History filter bar,
> clipped login chips, and KPI cards overflowing 1366. Prefer a `CTkLabel` with
> `fg_color`+`corner_radius` for a chip, and pass `width=1` when a card should
> take its share of a row rather than demand 200px.

> **`side="bottom"` does not reserve space.** Pack a footer bar *before* any
> sibling packed with `expand=True`, or the expanding widget takes everything
> and the footer never appears. Same within a bar: a `side="right"` button only
> gets what earlier widgets leave.

> **`CTkEntry` suppresses `placeholder_text` once a `textvariable` is set.** The
> POS and Bill History search fields both need a variable to drive their filter
> traces, so each draws its hint as a muted `CTkLabel` placed over the empty
> field and hidden on the first keystroke — never by writing into the variable,
> which would fire the filter.
- Shop name is always "Priya Store" — enforced on every startup via `db.set_setting("shop_name", "Priya Store")`, which is why Settings deliberately has no shop-name field.
- Billing screen keyboard shortcuts: `F2` search product, `F8` hold bill, `F10` print & save, `Ctrl+N` new bill, `Esc` close popup or clear cart — all bound on the **toplevel**, so they are armed in `on_show()` (`_bind_root_keys`) and disarmed in `on_hide()` (`_unbind_root_keys`). Never bind them in the constructor: screens are cached and never destroyed, so a leftover binding keeps firing on every other screen — F10 would save and print a bill, and Esc would clear the cart, while the user is looking at Products. `Del` (remove item) is bound on `cart_tree` itself and needs no teardown.
- Responsive window: `_compute_fit()` scales from a 1280×720 floor to a 4K ceiling inside a 16:10–16:9 aspect band. Widget scaling is set once via `ctk.set_widget_scaling()` — never call it again after startup.

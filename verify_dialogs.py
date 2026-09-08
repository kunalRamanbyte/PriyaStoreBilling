"""
verify_dialogs.py — a geometry manager never receives a widget option.

Run:  python verify_dialogs.py   (exit 0 on all pass, 1 on any failure)

`pack()` and `grid()` accept *placement* options only. `width` and `height`
are **widget** options and belong on the constructor. Tk does not ignore the
stray one — it raises:

    _tkinter.TclError: bad option "-width": must be -after, -anchor, -before,
    -expand, -fill, -in, -ipadx, -ipady, -padx, -pady, or -side

and because that call is the last statement in a dialog builder, the dialog
opens with no Cancel button and the shopkeeper gets a crash box on top of it.
Eight such calls shipped — the Cancel button of Add/Edit Product, Add/Edit
Customer, Add/Edit Supplier, Record Payment, Add Udhaar, Stock Adjustment and
both Purchase/GRN dialogs — i.e. the exit from nearly every data-entry form in
the app. `place()` is *not* covered here: it genuinely takes width/height.

Three kinds of check, because no one of them is enough:

  * **oracle** — prove Tk really does reject `pack(width=…)`. Without this the
    structural check below could be enforcing a rule that does not exist, and
    would keep passing if it were quietly testing nothing.
  * **structural** — an AST scan of every project source file. This is the one
    that travels: it covers all eight sites and every dialog added later,
    including the ones the behavioural check cannot reach.
  * **behavioural** — open the real dialogs and confirm each builds. Six are
    reachable from real database rows. Two are not, and are named as gaps
    below rather than faked, because a mocked selection would prove only that
    the mock works.

Nothing here writes: the dialogs are opened and immediately destroyed.
"""

import ast
import os
import sys
import traceback

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

import tkinter as tk
import customtkinter as ctk

from database import Database
from styles import setup_ttk_styles

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f" {'PASS' if cond else 'FAIL'}  {name}" + (f"  -- {detail}" if detail and not cond else ""))


# Tk's own option lists, from the pack(n) and grid(n) manual pages. `in_` is
# tkinter's spelling of Tcl's `-in`; both are accepted by the binding.
PACK_OPTIONS = {"after", "anchor", "before", "expand", "fill",
                "in", "in_", "ipadx", "ipady", "padx", "pady", "side"}
GRID_OPTIONS = {"column", "columnspan", "in", "in_", "ipadx", "ipady",
                "padx", "pady", "row", "rowspan", "sticky"}
LEGAL = {"pack": PACK_OPTIONS, "pack_configure": PACK_OPTIONS,
         "grid": GRID_OPTIONS, "grid_configure": GRID_OPTIONS}

# Not the app: build output, the scratch drafts these bugs were pasted from,
# and the suites themselves.
SKIP_DIRS = {"build", "dist", "installer", "logs", "output", "backups",
             "scratch", "docs", "assets", "skills", "__pycache__", ".git"}


def source_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in sorted(filenames):
            if fn.endswith(".py"):
                yield os.path.join(dirpath, fn)


# ── 1. Oracle: the rule this suite enforces is a real Tk rule ────────────────
root = ctk.CTk()
# Parked offscreen, not withdrawn. These dialogs call grab_set(), and Tk
# refuses a grab on a window that is not viewable — the same lesson
# verify_applog.py records for event delivery.
root.geometry("900x600+3000+3000")
root.update()
setup_ttk_styles()

_probe = tk.Frame(root)
try:
    _probe.pack(**{"side": "left", "width": 100})
    check("Tk rejects width= on pack()", False,
          "pack(width=100) was accepted — the structural check below would be vacuous")
except tk.TclError as e:
    check("Tk rejects width= on pack()", 'bad option "-width"' in str(e), str(e))
_probe.destroy()

_probe2 = tk.Frame(root)
try:
    _probe2.grid(**{"row": 0, "height": 40})
    check("Tk rejects height= on grid()", False, "grid(height=40) was accepted")
except tk.TclError as e:
    check("Tk rejects height= on grid()", 'bad option "-height"' in str(e), str(e))
_probe2.destroy()


# ── 2. Structural: no geometry call anywhere carries a widget option ─────────
offenders = []
unparsed = []
for path in source_files():
    rel = os.path.relpath(path, ROOT)
    try:
        with open(path, encoding="utf-8") as fh:
            tree = ast.parse(fh.read(), filename=rel)
    except (SyntaxError, UnicodeDecodeError) as e:
        unparsed.append(f"{rel}: {e}")
        continue
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        legal = LEGAL.get(node.func.attr)
        if legal is None:
            continue
        for kw in node.keywords:
            if kw.arg is not None and kw.arg not in legal:
                line = getattr(node.func, "end_lineno", None) or node.lineno
                offenders.append(f"{rel}:{line}  {node.func.attr}({kw.arg}=...)")

check("every source file parses", not unparsed, "; ".join(unparsed))
check("no pack()/grid() call passes a widget option",
      not offenders,
      f"{len(offenders)} site(s):\n        " + "\n        ".join(offenders))


# ── 3. Behavioural: the real dialogs open ───────────────────────────────────
db = Database()
user = {"user_id": 1, "username": "admin", "name": "Admin", "role": "admin"}


class FakeApp:
    screens = {}
    current_role = "admin"
    current_lang = "English"
    current_theme = "Light"
    def navigate_to(self, *a, **kw): pass
    def rebuild_screen(self, *a, **kw): pass


app = FakeApp()
_built = {}


def screen(module_name, class_name):
    """Build a screen once, on show, parented to the offscreen root."""
    if class_name not in _built:
        mod = __import__(module_name)
        frame = ctk.CTkFrame(root)
        frame.pack(fill="both", expand=True)
        s = getattr(mod, class_name)(frame, db, user, app)
        s.pack(fill="both", expand=True)
        if hasattr(s, "on_show"):
            s.on_show()
        root.update()
        _built[class_name] = s
    return _built[class_name]


def opens(name, module_name, class_name, call):
    """Assert a dialog builder runs to completion, then close what it opened."""
    try:
        s = screen(module_name, class_name)
        before = set(root.winfo_children())
        call(s)
        root.update()
    except Exception:
        check(name, False, traceback.format_exc(limit=3).strip().replace("\n", "\n        "))
        return
    for w in set(root.winfo_children()) - before:
        try:
            w.grab_release()
            w.destroy()
        except tk.TclError:
            pass
    root.update()
    check(name, True)


def a_product():
    rows = db.get_products()
    return dict(rows[0]) if rows else None


opens("Products - Add Product form opens",
      "screen_products", "ProductScreen", lambda s: s._open_form(None))

opens("Customers - Add Customer form opens",
      "screen_customers", "CustomerScreen", lambda s: s._open_form(None))

opens("Suppliers - Add Supplier form opens",
      "screen_suppliers", "SupplierScreen", lambda s: s._open_form(None))

opens("Purchase/GRN - Add New Product form opens",
      "screen_purchase", "PurchaseScreen", lambda s: s._open_new_product_form())

prod = a_product()
if prod is None:
    check("Inventory - Stock Adjustment dialog opens", False,
          "no products in billing_data.db to adjust")
    check("Purchase/GRN - edit cart item dialog opens", False,
          "no products in billing_data.db to add")
else:
    opens("Inventory - Stock Adjustment dialog opens",
          "screen_inventory", "InventoryScreen",
          lambda s: s._open_adjustment_dialog(prod["product_id"]))

    opens("Purchase/GRN - edit cart item dialog opens",
          "screen_purchase", "PurchaseScreen",
          lambda s: s._edit_item_dialog(
              {"product_id": prod["product_id"], "name": prod["name"],
               "unit": prod["unit"], "purchase_price": prod["purchase_price"]},
              new=True))

# Not reached behaviourally, by choice:
#   CustomerScreen._transaction_dialog — needs a treeview selection
#   SupplierScreen._record_payment     — needs a supplier holding an unpaid
#                                        invoice, which a given database may
#                                        simply not contain
# Both are covered by the structural check above. Faking the selection would
# assert that the fake works, not that the dialog does.

root.destroy()

print("-" * 66)
print(f"  {len(PASS)} passed  |  {len(FAIL)} failed  |  {len(PASS) + len(FAIL)} total")
print("=" * 66)
sys.exit(1 if FAIL else 0)

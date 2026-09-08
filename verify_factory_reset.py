"""
verify_factory_reset.py — a wipe stays wiped.

Run:  python verify_factory_reset.py   (exit 0 on all pass, 1 on any failure)

`factory_reset()` empties the catalogue, but `init_db()` runs on every launch
and used to re-seed the demo categories and the twelve sample products
whenever those tables were empty — and "empty" is indistinguishable from
"deliberately emptied". A shopkeeper who formatted to start clean reopened
the till to find Aashirvaad Atta and Coca Cola back on the shelf, to be
deleted one by one.

The seed is therefore gated on a `initial_seed_done` setting rather than on
emptiness. `factory_reset(keep_settings=True)` keeps that flag, so the wipe
holds; `keep_settings=False` drops it along with everything else, which
deliberately makes the database behave like a fresh install again.

Nothing here touches the shop's database — it builds throwaway ones in the
temp directory.
"""

import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

from database import Database

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f" {'PASS' if cond else 'FAIL'}  {name}" + (f"  -- {detail}" if detail and not cond else ""))


def counts(db, *tables):
    with db.get_conn() as conn:
        return {t: conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in tables}


print("=" * 66)
print("  factory reset")
print("=" * 66)

tmpdir = tempfile.mkdtemp(prefix="priya_fr_")

try:
    # ── A fresh install still gets its starter catalogue ─────────────
    db = Database()
    db.db_path = os.path.join(tmpdir, "fresh.db")
    db.init_db()
    seeded = counts(db, "products", "categories", "users")
    check("a new database is seeded", seeded["products"] == 12 and seeded["categories"] == 10,
          str(seeded))
    check("the seed is recorded, not inferred from empty tables",
          db.get_setting("initial_seed_done", "") != "",
          "initial_seed_done is not set after the first init_db()")

    db.init_db()          # a second ordinary launch must not duplicate anything
    again = counts(db, "products", "categories")
    check("relaunching does not duplicate the seed",
          again == {"products": 12, "categories": 10}, str(again))

    # ── The wipe ─────────────────────────────────────────────────────
    admin_before = db.authenticate("admin", "admin123")
    db.set_setting("bill_prefix", "SHOP")          # a setting the shop chose
    db.factory_reset(keep_settings=True)
    wiped = counts(db, "bills", "bill_items", "customers", "products",
                   "categories", "suppliers", "activity_log", "users")
    check("factory reset empties the catalogue",
          wiped["products"] == 0 and wiped["categories"] == 0, str(wiped))
    check("factory reset empties the ledger",
          wiped["bills"] == 0 and wiped["customers"] == 0 and wiped["activity_log"] == 0,
          str(wiped))
    check("admin accounts survive the wipe", wiped["users"] >= 1, str(wiped))

    # ── Reopening the app: the point of the whole file ───────────────
    db.init_db()          # exactly what the next launch does
    after = counts(db, "products", "categories", "bills", "customers")
    check("reopening does not restore the demo products",
          after["products"] == 0, f"{after['products']} product(s) came back")
    check("reopening does not restore the demo categories",
          after["categories"] == 0, f"{after['categories']} categor(y/ies) came back")
    check("reopening restores no bills or customers",
          after["bills"] == 0 and after["customers"] == 0, str(after))

    check("the shop's own settings survive", db.get_setting("bill_prefix", "") == "SHOP",
          f"bill_prefix is {db.get_setting('bill_prefix', '')!r}")
    check("the bill counter is reset", db.get_setting("next_bill_no", "") == "1",
          f"next_bill_no is {db.get_setting('next_bill_no', '')!r}")
    check("admin can still log in after the reset",
          db.authenticate("admin", "admin123") is not None
          and admin_before is not None)

    # ── Upgrading a shop that predates the marker ────────────────────
    # Its settings have no `initial_seed_done`, but its shelves are full.
    # Adopt the catalogue; never pour twelve demo rows into a live shop.
    shop = Database()
    shop.db_path = os.path.join(tmpdir, "existing_shop.db")
    shop.init_db()
    with shop.get_conn() as conn:
        conn.execute("DELETE FROM products")
        conn.execute("DELETE FROM settings WHERE key='initial_seed_done'")
        conn.execute(
            "INSERT INTO products (product_code, name, unit, selling_price, current_stock)"
            " VALUES ('SHOP-1', 'Real Stock Item', 'piece', 10.0, 3)")
    shop.init_db()          # first launch of the new build
    shelf = counts(shop, "products")
    check("an existing shop keeps its own catalogue on upgrade",
          shelf["products"] == 1, f"{shelf['products']} products — demo rows were injected")
    check("the upgrade records the marker so it is asked once",
          shop.get_setting("initial_seed_done", "") != "")

    # ── keep_settings=False is a deliberate exception ────────────────
    # It drops every setting including the seed marker, which is what makes
    # the database indistinguishable from a brand-new one.
    db2 = Database()
    db2.db_path = os.path.join(tmpdir, "wipe_all.db")
    db2.init_db()
    db2.factory_reset(keep_settings=False)
    db2.init_db()
    reborn = counts(db2, "products", "categories")
    check("a settings-included wipe starts over as a fresh install",
          reborn == {"products": 12, "categories": 10}, str(reborn))

finally:
    shutil.rmtree(tmpdir, ignore_errors=True)

print("-" * 66)
print(f"  {len(PASS)} passed  |  {len(FAIL)} failed  |  {len(PASS) + len(FAIL)} total")
print("=" * 66)
sys.exit(1 if FAIL else 0)

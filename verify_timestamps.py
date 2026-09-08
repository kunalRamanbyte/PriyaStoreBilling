"""
verify_timestamps.py — every stored timestamp is the shop's wall clock.

Run:  python verify_timestamps.py   (exit 0 on all pass, 1 on any failure)

SQLite's CURRENT_TIMESTAMP is **UTC**, so a schema default of
`DATETIME DEFAULT CURRENT_TIMESTAMP` files a bill made at 16:24 IST as
10:54. The whole app then reads that value back as if it were local time —
the receipt prints 10:54, the A4 footer prints "Printed: 16:24" from
datetime.now() two inches below it, and the day-report boundary sits 5h30m
into the wrong day. Every timestamp the shop can see must be local.

Two kinds of check here, because one alone is not enough:

  * **structural** — no table may declare CURRENT_TIMESTAMP, and no query may
    compare a stored timestamp against a bare SQL 'now'. These fail on any
    machine, including a developer sitting at UTC+0 where the behavioural
    checks below pass even when the bug is fully present.
  * **behavioural** — write through the real save paths and compare what
    landed against datetime.now().

Nothing here touches the shop's database: it builds a throwaway one in the
temp directory and points a Database instance at it.
"""

import os
import re
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

import bill_printer
from database import Database

PASS, FAIL = [], []
TOLERANCE_S = 120          # generous: the suite only needs to catch a 30+ min skew


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f" {'PASS' if cond else 'FAIL'}  {name}" + (f"  -- {detail}" if detail and not cond else ""))


def skew(stored):
    """Seconds between a stored 'YYYY-MM-DD HH:MM:SS' and the system clock."""
    if stored is None:
        return None
    try:
        ts = datetime.strptime(str(stored)[:19], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
    return abs((datetime.now() - ts).total_seconds())


def is_local(name, stored):
    s = skew(stored)
    check(name, s is not None and s <= TOLERANCE_S,
          f"stored {stored!r}, system clock {datetime.now():%Y-%m-%d %H:%M:%S}"
          + (f", off by {s / 60:.0f} min" if s is not None else " (unparseable)"))


print("=" * 66)
print("  stored timestamps follow the system clock")
print("=" * 66)

offset_h = round((datetime.now() - datetime.utcnow()).total_seconds() / 3600, 2)
print(f"  this machine is UTC{offset_h:+g}"
      + ("  (behavioural checks cannot tell UTC from local here — "
         "the structural ones can)" if offset_h == 0 else ""))
print("-" * 66)

tmpdir = tempfile.mkdtemp(prefix="priya_ts_")
db = Database()
db.db_path = os.path.join(tmpdir, "billing_data.db")

try:
    db.init_db()

    # ── Structural: the schema itself ───────────────────────────────
    with db.get_conn() as conn:
        schema = [(r["name"], r["sql"] or "") for r in conn.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='table'")]
    offenders = [n for n, sql in schema if "CURRENT_TIMESTAMP" in sql.upper()]
    check("no table defaults to CURRENT_TIMESTAMP (it is UTC)",
          not offenders, "still UTC: " + ", ".join(sorted(offenders)))

    localised = [n for n, sql in schema if "localtime" in sql.lower()]
    check("timestamp defaults ask for localtime",
          len(localised) >= 10, f"only {len(localised)}: {sorted(localised)}")

    # ── Structural: queries that compare against SQL 'now' ──────────
    # DATE('now') is UTC too, so a stored-local column compared against it
    # slips a day for anything written before the UTC offset each morning.
    with open(os.path.join(ROOT, "database.py"), encoding="utf-8") as fh:
        src = fh.read()
    bare_now = [m.group(0) for m in re.finditer(
        r"(?:JULIANDAY|DATE|DATETIME)\(\s*'now'\s*(?:,\s*(?!'localtime')[^)]*)?\)",
        src, re.IGNORECASE)]
    check("no query compares against a bare SQL 'now'",
          not bare_now, f"{len(bare_now)} left: {bare_now[:4]}")

    # ── Structural: no INSERT may fall through to a schema default ──
    # A shop already running the app has tables created with the old UTC
    # default, and SQLite cannot ALTER a column default. The fix therefore
    # only reaches those databases if every INSERT names its timestamp
    # column explicitly.
    TS_COLUMN = {
        "users": "created_at", "customers": "created_at", "products": "created_at",
        "suppliers": "created_at", "bills": "bill_date",
        "purchase_entries": "purchase_date", "sales_returns": "return_date",
        "activity_log": "timestamp", "stock_adjustments": "created_at",
        "customer_transactions": "created_at", "supplier_payments": "paid_date",
    }
    missing = []
    inserts = re.findall(r"INSERT(?:\s+OR\s+\w+)?\s+INTO\s+(\w+)\s*\(([^)]*)\)", src, re.S)
    check("the insert scan found every write path",
          len(inserts) >= 30, f"only {len(inserts)} INSERTs matched — the pattern has drifted")
    for table, cols in inserts:
        want = TS_COLUMN.get(table)
        named = [c.strip() for c in cols.split(',')]
        if want and want not in named:
            missing.append(f"{table}.{want}")
    check("every INSERT names its timestamp column",
          not missing, f"relying on the schema default: {sorted(set(missing))}")

    # ── Behavioural: every write path a shopkeeper can see ──────────
    admin = db.authenticate("admin", "admin123")
    uid = admin["user_id"]

    cats = db.get_categories()
    cat_id = cats[0]["category_id"] if cats else None
    pid = db.add_product({
        "product_code": "TS-1", "name": "Test Item", "category_id": cat_id,
        "brand": "T", "unit": "piece", "selling_price": 50.0,
        "purchase_price": 30.0, "current_stock": 100.0, "reorder_level": 5.0,
        "expiry_date": None,
    })
    cust_id = db.add_customer({"name": "Test Cust", "phone": "9000000001", "address": ""})
    sup_id = db.add_supplier({"name": "Test Supp", "contact_person": "", "phone": "",
                              "email": "", "city": "", "gst_number": "", "notes": ""})

    bill_data = {
        "customer_id": cust_id, "customer_name": "Test Cust", "subtotal": 100.0,
        "discount": 0.0, "grand_total": 100.0, "payment_mode": "Cash",
        "amount_paid": 100.0, "change_due": 0.0,
        "udhaar_adjustment": 0.0, "change_adjustment": 0.0,
    }
    items = [{"product_id": pid, "product_name": "Test Item", "unit": "piece",
              "quantity": 2.0, "unit_price": 50.0, "discount": 0.0, "line_total": 100.0}]
    bill_id = db.save_bill(bill_data, items, uid)
    bill, bill_items = db.get_bill_by_id(bill_id)
    is_local("bills.bill_date is the system clock", bill["bill_date"])

    draft_id = db.save_draft_bill(bill_data, items, uid)
    with db.get_conn() as conn:
        draft = conn.execute("SELECT bill_date FROM bills WHERE bill_id=?",
                             (draft_id,)).fetchone()
    is_local("a held bill's bill_date is the system clock", draft["bill_date"])

    with db.get_conn() as conn:
        bi = conn.execute("SELECT item_id FROM bill_items WHERE bill_id=?",
                          (bill_id,)).fetchone()
    ret_id, ret_no = db.save_return(
        {"bill_id": bill_id, "bill_number": bill["bill_number"], "customer_id": cust_id,
         "customer_name": "Test Cust", "refund_mode": "Cash", "reason": "test"},
        [{"bill_item_id": bi["item_id"], "product_id": pid, "product_name": "Test Item",
          "unit": "piece", "quantity": 1.0, "unit_price": 50.0, "line_total": 50.0,
          "restocked": 1}], uid)
    ret, ret_items = db.get_return_by_id(ret_id)
    is_local("sales_returns.return_date is the system clock", ret["return_date"])

    pur_id = db.save_purchase(
        {"supplier_id": sup_id, "supplier_name": "Test Supp",
         "total_amount": 60.0, "notes": ""},
        [{"product_id": pid, "product_name": "Test Item", "unit": "piece",
          "quantity": 2.0, "unit_price": 30.0, "line_total": 60.0}], uid)
    with db.get_conn() as conn:
        pur = conn.execute("SELECT purchase_date FROM purchase_entries WHERE purchase_id=?",
                           (pur_id,)).fetchone()
    is_local("purchase_entries.purchase_date is the system clock", pur["purchase_date"])

    db.record_supplier_payment(pur_id, 60.0, "test", uid)
    db.log_activity(uid, "TS_TEST", "timestamp check")
    db.do_stock_adjustment(pid, "Add", 5.0, "test", uid)
    db.add_customer_transaction(cust_id, "Payment", 10.0, "TS", "test", uid)
    db.add_user("Test User", "ts_user", "ts_pass_1", "cashier")

    with db.get_conn() as conn:
        rows = {
            "supplier_payments.paid_date": conn.execute(
                "SELECT paid_date v FROM supplier_payments ORDER BY payment_id DESC").fetchone(),
            "activity_log.timestamp": conn.execute(
                "SELECT timestamp v FROM activity_log ORDER BY log_id DESC").fetchone(),
            "stock_adjustments.created_at": conn.execute(
                "SELECT created_at v FROM stock_adjustments ORDER BY adj_id DESC").fetchone(),
            "customer_transactions.created_at": conn.execute(
                "SELECT created_at v FROM customer_transactions ORDER BY txn_id DESC").fetchone(),
            "customers.created_at": conn.execute(
                "SELECT created_at v FROM customers ORDER BY customer_id DESC").fetchone(),
            "products.created_at": conn.execute(
                "SELECT created_at v FROM products ORDER BY product_id DESC").fetchone(),
            "suppliers.created_at": conn.execute(
                "SELECT created_at v FROM suppliers ORDER BY supplier_id DESC").fetchone(),
            "users.created_at": conn.execute(
                "SELECT created_at v FROM users ORDER BY user_id DESC").fetchone(),
        }
    for label, row in rows.items():
        is_local(f"{label} is the system clock", row["v"] if row else None)

    # ── What actually reaches the paper ─────────────────────────────
    settings = db.get_all_settings()
    today = datetime.now()

    receipt = "\n".join(bill_printer._build_receipt_lines(bill, bill_items, settings, 48))
    check("the thermal receipt prints today's date",
          today.strftime("%d/%m/%y") in receipt,
          f"expected {today:%d/%m/%y}, receipt has "
          f"{re.search(r'Date: *([0-9/]+)', receipt).group(1) if re.search(r'Date: *([0-9/]+)', receipt) else '??'}")

    hhmm = re.search(r"Payment:.*?\|\s*(\d{2}:\d{2})", receipt)
    printed = skew(f"{today:%Y-%m-%d} {hhmm.group(1)}:00") if hhmm else None
    check("the thermal receipt prints the current time",
          printed is not None and printed <= TOLERANCE_S + 60,
          f"receipt says {hhmm.group(1) if hhmm else '??:??'}, clock says {today:%H:%M}")

    r_lines = "\n".join(bill_printer._build_return_lines(ret, ret_items, settings, 48))
    check("the return receipt prints today's date",
          today.strftime("%d/%m/%y") in r_lines,
          f"expected {today:%d/%m/%y} in the return note")

    # The A4 PDF prints bill_date in its header and datetime.now() in its
    # footer. They must agree to the hour, or one sheet shows two clocks.
    check("the A4 header date agrees with its own printed-at footer",
          str(bill["bill_date"])[:13] == today.strftime("%Y-%m-%d %H"),
          f"header {str(bill['bill_date'])[:16]}, footer {today:%Y-%m-%d %H:%M}")


    # ── An existing shop database, created with the UTC defaults ────
    # Rebuilt here from the live schema with the localtime default wound
    # back, which is exactly what an installed till is running today.
    with db.get_conn() as conn:
        ddl = [r["sql"] for r in conn.execute(
            "SELECT sql FROM sqlite_master "
            "WHERE sql IS NOT NULL AND name NOT LIKE 'sqlite_%'")]
    legacy_path = os.path.join(tmpdir, "legacy.db")
    legacy_conn = sqlite3.connect(legacy_path)
    for stmt in ddl:
        legacy_conn.execute(stmt.replace("(datetime('now','localtime'))", "CURRENT_TIMESTAMP"))
    # One bill and one log line as a pre-fix build would have left them: UTC.
    UTC_BILL = "2026-01-15 03:30:00"
    legacy_conn.execute(
        "INSERT INTO bills (bill_number, bill_date, customer_name, grand_total, status) "
        "VALUES ('BILL-OLD-1', ?, 'Walk-in Customer', 100.0, 'Active')", (UTC_BILL,))
    legacy_conn.execute(
        "INSERT INTO activity_log (user_id, action, details, timestamp) "
        "VALUES (1, 'BILL_SAVED', 'legacy', ?)", (UTC_BILL,))
    legacy_conn.commit()
    legacy_conn.close()

    old = Database()
    old.db_path = legacy_path
    with old.get_conn() as conn:
        stale = [r["name"] for r in conn.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='table' AND sql LIKE '%CURRENT_TIMESTAMP%'")]
    check("the legacy fixture really does default to UTC",
          len(stale) >= 10, f"only {len(stale)} table(s) rebuilt as UTC")

    old.init_db()          # seeds users/settings; CREATE IF NOT EXISTS leaves the UTC defaults

    # ── Rows written before the fix are left exactly as they are ────
    # A deliberate decision, not an oversight: upgrading a till converts
    # nothing. Only the times written from now on follow the clock.
    def legacy_value(table, col, where):
        with old.get_conn() as conn:
            r = conn.execute(f"SELECT {col} v FROM {table} WHERE {where}").fetchone()
        return r["v"] if r else None

    kept = legacy_value("bills", "bill_date", "bill_number = 'BILL-OLD-1'")
    check("a pre-fix bill is left untouched by the upgrade",
          kept == UTC_BILL, f"got {kept!r}, expected it to stay {UTC_BILL!r}")

    kept_log = legacy_value("activity_log", "timestamp", "details = 'legacy'")
    check("a pre-fix log line is left untouched too",
          kept_log == UTC_BILL, f"got {kept_log!r}, expected it to stay {UTC_BILL!r}")

    old_uid = old.authenticate("admin", "admin123")["user_id"]
    old_pid = old.add_product({
        "product_code": "TS-L1", "name": "Legacy Item", "category_id": None,
        "brand": "T", "unit": "piece", "selling_price": 50.0, "purchase_price": 30.0,
        "current_stock": 100.0, "reorder_level": 5.0, "expiry_date": None})
    old_bill_id = old.save_bill(
        {"customer_id": None, "customer_name": "Walk-in Customer", "subtotal": 50.0,
         "discount": 0.0, "grand_total": 50.0, "payment_mode": "Cash",
         "amount_paid": 50.0, "change_due": 0.0,
         "udhaar_adjustment": 0.0, "change_adjustment": 0.0},
        [{"product_id": old_pid, "product_name": "Legacy Item", "unit": "piece",
          "quantity": 1.0, "unit_price": 50.0, "discount": 0.0, "line_total": 50.0}],
        old_uid)
    old_bill, _ = old.get_bill_by_id(old_bill_id)
    is_local("a bill saved into an upgraded database is the system clock",
             old_bill["bill_date"])
    old.log_activity(old_uid, "TS_TEST", "legacy")
    with old.get_conn() as conn:
        row = conn.execute(
            "SELECT timestamp v FROM activity_log ORDER BY log_id DESC").fetchone()
    is_local("an upgraded database's activity log is the system clock", row["v"])

    # ── Every write path, against the pre-fix schema ─────────────────
    # Each INSERT now names a timestamp column explicitly. If one of those
    # names were wrong, it would raise "no such column" — in a shop, at the
    # till, on the first sale after an upgrade. Drive them all here.
    old_cust = old.add_customer({"name": "Legacy Cust", "phone": "9333333333", "address": ""})
    old_sup = old.add_supplier({"name": "Legacy Sup", "contact_person": "", "phone": "",
                                "email": "", "city": "", "gst_number": "", "notes": ""})
    old_line = [{"product_id": old_pid, "product_name": "Legacy Item", "unit": "piece",
                 "quantity": 1.0, "unit_price": 50.0, "discount": 0.0, "line_total": 50.0}]
    old_bill_data = {"customer_id": old_cust, "customer_name": "Legacy Cust",
                     "subtotal": 50.0, "discount": 0.0, "grand_total": 50.0,
                     "payment_mode": "Cash", "amount_paid": 30.0, "change_due": 0.0,
                     "udhaar_adjustment": 0.0, "change_adjustment": 0.0}

    broken = []
    def drive(name, fn):
        try:
            return fn()
        except Exception as exc:
            broken.append(f"{name}: {type(exc).__name__}: {exc}")

    old.save_draft_bill(old_bill_data, old_line, old_uid)
    credit_bill = drive("save_bill", lambda: old.save_bill(old_bill_data, old_line, old_uid))
    old_pur = drive("save_purchase", lambda: old.save_purchase(
        {"supplier_id": old_sup, "supplier_name": "Legacy Sup",
         "total_amount": 30.0, "notes": ""},
        [{"product_id": old_pid, "product_name": "Legacy Item", "unit": "piece",
          "quantity": 1.0, "unit_price": 30.0, "line_total": 30.0}], old_uid))
    drive("record_supplier_payment",
          lambda: old.record_supplier_payment(old_pur, 30.0, "n", old_uid))
    drive("do_stock_adjustment",
          lambda: old.do_stock_adjustment(old_pid, "Add", 5.0, "r", old_uid))
    drive("add_customer_transaction",
          lambda: old.add_customer_transaction(old_cust, "Payment", 5.0, "R", "n", old_uid))
    drive("add_user", lambda: old.add_user("Legacy U", "legacy_u", "pw_12345", "cashier"))

    def old_return():
        with old.get_conn() as conn:
            bi = conn.execute("SELECT item_id FROM bill_items WHERE bill_id=?",
                              (credit_bill,)).fetchone()["item_id"]
        b, _ = old.get_bill_by_id(credit_bill)
        return old.save_return(
            {"bill_id": credit_bill, "bill_number": b["bill_number"],
             "customer_id": old_cust, "customer_name": "Legacy Cust",
             "refund_mode": "Cash", "reason": "r"},
            [{"bill_item_id": bi, "product_id": old_pid, "product_name": "Legacy Item",
              "unit": "piece", "quantity": 1.0, "unit_price": 50.0,
              "line_total": 50.0, "restocked": 1}], old_uid)
    drive("save_return", old_return)
    drive("void_bill", lambda: old.void_bill(
        old.save_bill(old_bill_data, old_line, old_uid), "test", old_uid))

    check("every write path runs against a pre-fix database",
          not broken, "; ".join(broken))

    with old.get_conn() as conn:
        drifted = []
        for table, col in TS_COLUMN.items():
            r = conn.execute(
                f"SELECT {col} v FROM {table} ORDER BY rowid DESC LIMIT 1").fetchone()
            if r and r["v"] and skew(r["v"]) is not None and skew(r["v"]) > TOLERANCE_S:
                drifted.append(f"{table}.{col}={r['v']}")
    check("and every row it writes carries the system clock",
          not drifted, ", ".join(drifted))

finally:
    shutil.rmtree(tmpdir, ignore_errors=True)

print("-" * 66)
print(f"  {len(PASS)} passed  |  {len(FAIL)} failed  |  {len(PASS) + len(FAIL)} total")
print("=" * 66)
sys.exit(1 if FAIL else 0)

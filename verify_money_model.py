"""
verify_money_model.py — the customer money model holds on every write path.

Run:  python verify_money_model.py   (exit 0 on all pass, 1 on any failure)

A customer carries two balances: `credit_balance` (udhaar owed to the shop) and
`change_balance` (change the shop owes back). **The invariant is that they can
never both be positive at once** — `_net_customer_balances()` offsets them, and
every transaction that touches either balance must end by calling it.

That invariant had no test. `save_bill()`, `void_bill()` and
`add_customer_transaction()` all call it; `save_return()` did not, so a
store-credit refund to a customer who owed money left them holding both.

The second case here is the same shape of omission one table over: a held bill
went through an INSERT whose column list had quietly lost `udhaar_adjustment`,
so a bill held after the cashier accepted "collect this due" resumed with the
due set to zero and collected nothing — while the badge, which reads the live
balance by a different route, still showed it owing.

Both are silent. Neither raises, logs, or shows a dialog; they only change what
a customer owes. That is why they are asserted here rather than left to be
noticed at a counter.

Nothing here touches the shop's database — it builds a throwaway one in the
temp directory and points a Database instance at it.
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


def balances(db, customer_id):
    with db.get_conn() as conn:
        r = conn.execute(
            "SELECT credit_balance, change_balance FROM customers WHERE customer_id=?",
            (customer_id,)).fetchone()
    return round(float(r["credit_balance"] or 0), 2), round(float(r["change_balance"] or 0), 2)


def build_shop(tmpdir, name):
    """A database with one product, one customer and an admin, ready to bill."""
    db = Database()
    db.db_path = os.path.join(tmpdir, name)
    db.init_db()
    uid = db.authenticate("admin", "admin123")["user_id"]
    pid = db.add_product({
        "product_code": "MM-1", "name": "Test Item", "category_id": None,
        "brand": "T", "unit": "piece", "selling_price": 200.0,
        "purchase_price": 150.0, "current_stock": 100.0, "reorder_level": 5.0,
        "expiry_date": None})
    cid = db.add_customer({"name": "Test Cust", "phone": "9000000001", "address": ""})
    return db, uid, pid, cid


def sell(db, uid, pid, cid, total=200.0, paid=200.0, udhaar_adj=0.0, change_adj=0.0):
    """One bill for one unit, paid as told. Returns (bill_id, bill_item_id)."""
    bill_id = db.save_bill(
        {"customer_id": cid, "customer_name": "Test Cust", "subtotal": total,
         "discount": 0.0, "grand_total": total, "payment_mode": "Cash",
         "amount_paid": paid, "change_due": 0.0,
         "udhaar_adjustment": udhaar_adj, "change_adjustment": change_adj},
        [{"product_id": pid, "product_name": "Test Item", "unit": "piece",
          "quantity": 1.0, "unit_price": total, "discount": 0.0,
          "line_total": total}], uid)
    with db.get_conn() as conn:
        item_id = conn.execute(
            "SELECT item_id FROM bill_items WHERE bill_id=?", (bill_id,)).fetchone()["item_id"]
    return bill_id, item_id


print("=" * 66)
print("  customer money model")
print("=" * 66)

tmpdir = tempfile.mkdtemp(prefix="priya_mm_")

try:
    # ── 1. A store-credit refund must not leave both balances positive ───
    db, uid, pid, cid = build_shop(tmpdir, "returns.db")

    # The customer owes 500, through the app's own path.
    db.add_customer_transaction(cid, "Credit", 500.0, "OPENING", "opening udhaar", uid)
    credit, change = balances(db, cid)
    check("fixture: the customer owes 500 and holds no change",
          (credit, change) == (500.0, 0.0), f"got credit={credit}, change={change}")

    # A bill paid in full — no balance movement of its own.
    bill_id, item_id = sell(db, uid, pid, cid, total=200.0, paid=200.0)
    credit, change = balances(db, cid)
    check("fixture: a fully paid bill moves neither balance",
          (credit, change) == (500.0, 0.0), f"got credit={credit}, change={change}")

    # Refund it as store credit. This is the case that used to break.
    bill, _ = db.get_bill_by_id(bill_id)
    db.save_return(
        {"bill_id": bill_id, "bill_number": bill["bill_number"], "customer_id": cid,
         "customer_name": "Test Cust", "refund_mode": "Store Credit", "reason": "test"},
        [{"bill_item_id": item_id, "product_id": pid, "product_name": "Test Item",
          "unit": "piece", "quantity": 1.0, "unit_price": 200.0,
          "line_total": 200.0, "restocked": 1}], uid)

    credit, change = balances(db, cid)
    check("a store-credit refund never leaves udhaar AND change both positive",
          not (credit > 0 and change > 0),
          f"customer holds credit={credit} AND change={change} at once")
    check("the refund is offset against what the customer owed",
          (credit, change) == (300.0, 0.0),
          f"expected credit=300.0, change=0.0; got credit={credit}, change={change}")

    # The offset must be visible in the ledger, not applied silently.
    with db.get_conn() as conn:
        notes = [r["notes"] for r in conn.execute(
            "SELECT notes FROM customer_transactions WHERE customer_id=?", (cid,))]
    check("the offset is written to the customer's ledger",
          any(n and "Auto-adjusted" in n for n in notes),
          f"no auto-adjust rows among {notes}")

    # ── 2. A refund to a customer who owes nothing still behaves ─────────
    db2, uid2, pid2, cid2 = build_shop(tmpdir, "plain_return.db")
    bill_id2, item_id2 = sell(db2, uid2, pid2, cid2, total=200.0, paid=200.0)
    bill2, _ = db2.get_bill_by_id(bill_id2)
    db2.save_return(
        {"bill_id": bill_id2, "bill_number": bill2["bill_number"], "customer_id": cid2,
         "customer_name": "Test Cust", "refund_mode": "Store Credit", "reason": "test"},
        [{"bill_item_id": item_id2, "product_id": pid2, "product_name": "Test Item",
          "unit": "piece", "quantity": 1.0, "unit_price": 200.0,
          "line_total": 200.0, "restocked": 1}], uid2)
    credit2, change2 = balances(db2, cid2)
    check("with nothing owed, store credit is kept in full",
          (credit2, change2) == (0.0, 200.0),
          f"expected credit=0.0, change=200.0; got credit={credit2}, change={change2}")

    # ── 3. A held bill must remember the udhaar it was told to collect ───
    db3, uid3, pid3, cid3 = build_shop(tmpdir, "drafts.db")
    draft_id = db3.save_draft_bill(
        {"customer_id": cid3, "customer_name": "Test Cust", "subtotal": 200.0,
         "discount": 0.0, "grand_total": 200.0, "payment_mode": "Cash",
         "amount_paid": 0.0, "change_due": 0.0,
         "udhaar_adjustment": 500.0, "change_adjustment": 25.0},
        [{"product_id": pid3, "product_name": "Test Item", "unit": "piece",
          "quantity": 1.0, "unit_price": 200.0, "discount": 0.0,
          "line_total": 200.0}], uid3)
    with db3.get_conn() as conn:
        d = conn.execute(
            "SELECT udhaar_adjustment, change_adjustment, status FROM bills WHERE bill_id=?",
            (draft_id,)).fetchone()
    check("a held bill keeps the udhaar it was told to collect",
          round(float(d["udhaar_adjustment"] or 0), 2) == 500.0,
          f"resumed with udhaar_adjustment={d['udhaar_adjustment']!r}, expected 500.0")
    check("a held bill keeps its change adjustment too",
          round(float(d["change_adjustment"] or 0), 2) == 25.0,
          f"got {d['change_adjustment']!r}")
    check("fixture: the held bill really is a draft", d["status"] == "Draft", d["status"])

    # Control: the completed-bill path has always stored this. If this ever
    # fails, the check above is passing for the wrong reason.
    done_id, _ = sell(db3, uid3, pid3, cid3, total=200.0, paid=700.0, udhaar_adj=500.0)
    with db3.get_conn() as conn:
        b = conn.execute("SELECT udhaar_adjustment FROM bills WHERE bill_id=?",
                         (done_id,)).fetchone()
    check("control: a completed bill stores its udhaar adjustment",
          round(float(b["udhaar_adjustment"] or 0), 2) == 500.0,
          f"got {b['udhaar_adjustment']!r}")

finally:
    shutil.rmtree(tmpdir, ignore_errors=True)

print("-" * 66)
print(f"  {len(PASS)} passed  |  {len(FAIL)} failed  |  {len(PASS) + len(FAIL)} total")
print("=" * 66)
sys.exit(1 if FAIL else 0)

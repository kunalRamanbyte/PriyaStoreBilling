import os
import sys

# Ensure correct path import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database

db = Database()
db.init_db()

# Create a test customer
cust_id = db.add_customer({"name": "Test Partial Customer", "phone": "8888888888", "address": "Test Address"})
print(f"Created customer with ID: {cust_id}")

# ─────────────────────────────────────────────────────────────────────────────
# Test Case 1: Underpayment (Bill 100, paid 80 -> 20 goes to Udhaar)
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- Test Case 1: Underpayment ---")
bill_data_1 = {
    "customer_id": cust_id,
    "customer_name": "Test Partial Customer",
    "subtotal": 100.0,
    "discount": 0.0,
    "grand_total": 100.0,
    "udhaar_adjustment": 0.0,
    "change_adjustment": 0.0,
    "payment_mode": "Credit (Udhaar)", # Underpayment triggers Credit payment mode
    "amount_paid": 80.0,
    "change_due": 0.0,
}

cart_items = [
    {
        "product_id": 1,
        "product_name": "Aashirvaad Atta 5kg",
        "unit": "piece",
        "quantity": 1,
        "unit_price": 100.0,
        "discount": 0.0,
        "line_total": 100.0
    }
]

bill_id_1 = db.save_bill(bill_data_1, cart_items, 1)
print(f"Saved underpayment bill ID: {bill_id_1}")

# Verify credit balance is exactly 20.0
cust = db.get_customer_by_id(cust_id)
print("Customer Credit Balance:", cust["credit_balance"])
assert cust["credit_balance"] == 20.0, f"Expected 20.0 credit_balance, got {cust['credit_balance']}"

# Verify transactions
txns = db.get_customer_transactions(cust_id)
print("Transactions after underpayment:")
for t in txns:
    print("  -", dict(t))
assert txns[0]["txn_type"] == "Credit", "Expected Credit transaction"
assert txns[0]["amount"] == 20.0, f"Expected Credit amount 20.0, got {txns[0]['amount']}"

# Void Case 1
print("Voiding Case 1 bill...")
void_ok = db.void_bill(bill_id_1, "Void testing", 1)
assert void_ok

# Verify credit balance restored to 0.0
cust = db.get_customer_by_id(cust_id)
print("Customer Credit Balance after void:", cust["credit_balance"])
assert cust["credit_balance"] == 0.0, f"Expected 0.0 credit_balance after void, got {cust['credit_balance']}"

# ─────────────────────────────────────────────────────────────────────────────
# Test Case 2: Overpayment (Bill 100, paid 150 -> 50 goes to Change)
# ─────────────────────────────────────────────────────────────────────────────
print("\n--- Test Case 2: Overpayment ---")
bill_data_2 = {
    "customer_id": cust_id,
    "customer_name": "Test Partial Customer",
    "subtotal": 100.0,
    "discount": 0.0,
    "grand_total": 100.0,
    "udhaar_adjustment": 0.0,
    "change_adjustment": 0.0,
    "payment_mode": "Cash",
    "amount_paid": 150.0,
    "change_due": 50.0,
}

bill_id_2 = db.save_bill(bill_data_2, cart_items, 1)
print(f"Saved overpayment bill ID: {bill_id_2}")

# Verify change balance is exactly 50.0
cust = db.get_customer_by_id(cust_id)
print("Customer Change Balance:", cust["change_balance"])
assert cust["change_balance"] == 50.0, f"Expected 50.0 change_balance, got {cust['change_balance']}"

# Verify transactions
txns = db.get_customer_transactions(cust_id)
print("Transactions after overpayment:")
for t in txns:
    print("  -", dict(t))
assert txns[0]["txn_type"] == "Change Deposit", "Expected Change Deposit transaction"
assert txns[0]["amount"] == 50.0, f"Expected Change Deposit amount 50.0, got {txns[0]['amount']}"

# Void Case 2
print("Voiding Case 2 bill...")
void_ok = db.void_bill(bill_id_2, "Void testing", 1)
assert void_ok

# Verify change balance restored to 0.0
cust = db.get_customer_by_id(cust_id)
print("Customer Change Balance after void:", cust["change_balance"])
assert cust["change_balance"] == 0.0, f"Expected 0.0 change_balance after void, got {cust['change_balance']}"

# ─────────────────────────────────────────────────────────────────────────────
# Cleanup
# ─────────────────────────────────────────────────────────────────────────────
with db.get_conn() as conn:
    conn.execute("DELETE FROM customer_transactions WHERE customer_id = ?", (cust_id,))
    conn.execute("DELETE FROM bill_items WHERE bill_id IN (?, ?)", (bill_id_1, bill_id_2))
    conn.execute("DELETE FROM bills WHERE customer_id = ?", (cust_id,))
    conn.execute("DELETE FROM customers WHERE customer_id = ?", (cust_id,))
    conn.commit()

print("\nAll partial credit and overpayment test assertions passed successfully!")

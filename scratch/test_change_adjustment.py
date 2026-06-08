import os
import sys

# Ensure correct path import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database

db = Database()
db.init_db()

# Create a test customer
cust_id = db.add_customer({"name": "Test Adjust Customer", "phone": "9999999999", "address": "Test Address"})
print(f"Created customer with ID: {cust_id}")

# Deposit 50 change initially
db.add_customer_transaction(cust_id, "Change Deposit", 50.0, "INITIAL", "Initial change deposit", 1)
cust = db.get_customer_by_id(cust_id)
print("Initial Change Balance:", cust["change_balance"])
assert cust["change_balance"] == 50.0, "Initial change deposit failed"

# Create a bill with change adjustment
bill_data = {
    "customer_id": cust_id,
    "customer_name": "Test Adjust Customer",
    "subtotal": 200.0,
    "discount": 0.0,
    "grand_total": 200.0, # item total
    "udhaar_adjustment": 0.0,
    "change_adjustment": 50.0, # we adjust/use 50 change
    "payment_mode": "Cash",
    "amount_paid": 150.0, # remaining to collect
    "change_due": 0.0,
}

cart_items = [
    {
        "product_id": 1, # Aashirvaad Atta
        "product_name": "Aashirvaad Atta 5kg",
        "unit": "piece",
        "quantity": 1,
        "unit_price": 200.0,
        "discount": 0.0,
        "line_total": 200.0
    }
]

# Save the bill
bill_id = db.save_bill(bill_data, cart_items, 1)
print(f"Saved bill ID: {bill_id}")

# Check customer change balance after save
cust = db.get_customer_by_id(cust_id)
print("Change Balance after save:", cust["change_balance"])
assert cust["change_balance"] == 0.0, f"Expected change balance to be 0, got {cust['change_balance']}"

# Check that the change adjustment is stored in the bill record
bill, _ = db.get_bill_by_id(bill_id)
print("Bill record in DB:", dict(bill))
assert bill["change_adjustment"] == 50.0, f"Expected bill change_adjustment to be 50.0, got {bill['change_adjustment']}"

# Verify transaction ledger has the Change Clear entry
txns = db.get_customer_transactions(cust_id)
print("Transactions after save:")
for t in txns:
    print("  -", dict(t))

# The most recent transaction should be the Change Clear of 50.0
assert txns[0]["txn_type"] == "Change Clear", "Expected Change Clear transaction"
assert txns[0]["amount"] == 50.0, "Expected Change Clear amount of 50.0"

# Now void the bill
print("Voiding the bill...")
void_ok = db.void_bill(bill_id, "Testing refund", 1)
assert void_ok, "Voiding bill failed"

# Check customer change balance after void
cust = db.get_customer_by_id(cust_id)
print("Change Balance after void:", cust["change_balance"])
assert cust["change_balance"] == 50.0, f"Expected change balance to be refunded to 50.0, got {cust['change_balance']}"

# Verify transaction ledger has the Change Deposit entry from the void
txns = db.get_customer_transactions(cust_id)
print("Transactions after void:")
for t in txns:
    print("  -", dict(t))
assert txns[0]["txn_type"] == "Change Deposit", "Expected Change Deposit transaction from void"
assert txns[0]["amount"] == 50.0, "Expected Change Deposit amount of 50.0 from void"

# Cleanup customer and transactions
with db.get_conn() as conn:
    conn.execute("DELETE FROM customer_transactions WHERE customer_id = ?", (cust_id,))
    conn.execute("DELETE FROM bill_items WHERE bill_id = ?", (bill_id,))
    conn.execute("DELETE FROM bills WHERE customer_id = ?", (cust_id,))
    conn.execute("DELETE FROM customers WHERE customer_id = ?", (cust_id,))
    conn.commit()

print("All change adjustment test assertions passed successfully!")

import os
import sys

# Ensure correct path import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database

db = Database()
db.init_db()

# Create a test customer
cust_id = db.add_customer({"name": "Test Credit Mode Customer", "phone": "7777777777", "address": "Test Address"})
print(f"Created customer with ID: {cust_id}")

# Set initial credit balance (previous udhaar is 50)
db.add_customer_transaction(cust_id, "Credit", 50.0, "INIT", "Initial Udhaar", 1)
cust = db.get_customer_by_id(cust_id)
print(f"Initial Credit Balance: {cust['credit_balance']}")
assert cust["credit_balance"] == 50.0, f"Expected 50.0 credit_balance, got {cust['credit_balance']}"

# Now save a bill of total 200, previous udhaar is 50, payment_mode = "Credit (Udhaar)" directly.
# In the UI, if payment_mode is "Credit (Udhaar)" directly, _get_bill_data sets:
# "amount_paid" = total_to_collect (which is 250.0)
bill_data = {
    "customer_id": cust_id,
    "customer_name": "Test Credit Mode Customer",
    "subtotal": 200.0,
    "discount": 0.0,
    "grand_total": 200.0,
    "udhaar_adjustment": 50.0,
    "change_adjustment": 0.0,
    "payment_mode": "Credit (Udhaar)",
    "amount_paid": 0.0, # 0.0 cash paid at counter in pure Credit mode
    "change_due": 0.0,
}

cart_items = [
    {
        "product_id": 1,
        "product_name": "Aashirvaad Atta 5kg",
        "unit": "piece",
        "quantity": 2,
        "unit_price": 100.0,
        "discount": 0.0,
        "line_total": 200.0
    }
]

bill_id = db.save_bill(bill_data, cart_items, 1)
print(f"Saved bill ID: {bill_id}")

# Get final credit balance
cust = db.get_customer_by_id(cust_id)
print("Customer Credit Balance:", cust["credit_balance"])

# Verify transactions
txns = db.get_customer_transactions(cust_id)
print("Transactions in database:")
for t in txns:
    print("  -", dict(t))

# Assertions
assert cust["credit_balance"] == 250.0, f"Expected 250.0 credit_balance, got {cust['credit_balance']}"

# Test Void
print("\nVoiding the bill...")
void_ok = db.void_bill(bill_id, "Void credit scenario", 1)
assert void_ok, "Expected void_bill to succeed"

cust = db.get_customer_by_id(cust_id)
print("Customer Credit Balance after void:", cust["credit_balance"])
assert cust["credit_balance"] == 50.0, f"Expected 50.0 credit_balance after void, got {cust['credit_balance']}"

txns_after = db.get_customer_transactions(cust_id)
print("Transactions in database after void:")
for t in txns_after:
    print("  -", dict(t))

# Cleanup
with db.get_conn() as conn:
    conn.execute("DELETE FROM customer_transactions WHERE customer_id = ?", (cust_id,))
    conn.execute("DELETE FROM bill_items WHERE bill_id = ?", (bill_id,))
    conn.execute("DELETE FROM bills WHERE customer_id = ?", (cust_id,))
    conn.execute("DELETE FROM customers WHERE customer_id = ?", (cust_id,))
    conn.commit()

print("\nCredit Mode verification complete (Save & Void passed)!")


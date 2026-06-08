from database import Database

db = Database()
db.init_db()

# Create customer
cust_id = db.add_customer({"name": "Netting Test Cust", "phone": "2222222222", "address": "Address"})

# Case 1: Start with 100 Udhaar
db.add_customer_transaction(cust_id, "Credit", 100.0, "REF-C1", "Initial Credit", 1)
cust = db.get_customer_by_id(cust_id)
print("Initial Credit state:", dict(cust))
assert cust["credit_balance"] == 100.0
assert cust["change_balance"] == 0.0

# Add 30 Change Deposit (should automatically net out to 70 Udhaar, 0 Change)
db.add_customer_transaction(cust_id, "Change Deposit", 30.0, "REF-D1", "Change Deposit", 1)
cust = db.get_customer_by_id(cust_id)
print("After Change Deposit state:", dict(cust))
assert cust["credit_balance"] == 70.0, f"Expected 70 Udhaar, got {cust['credit_balance']}"
assert cust["change_balance"] == 0.0, f"Expected 0 Change, got {cust['change_balance']}"

# Case 2: Clear outstanding balance and add 50 Change
db.add_customer_transaction(cust_id, "Payment", 70.0, "REF-P1", "Pay off Udhaar", 1)
db.add_customer_transaction(cust_id, "Change Deposit", 50.0, "REF-D2", "Add Change", 1)
cust = db.get_customer_by_id(cust_id)
print("With 50 Change state:", dict(cust))
assert cust["credit_balance"] == 0.0
assert cust["change_balance"] == 50.0

# Add 120 Udhaar (should net out to 70 Udhaar, 0 Change)
db.add_customer_transaction(cust_id, "Credit", 120.0, "REF-C2", "Add more Udhaar", 1)
cust = db.get_customer_by_id(cust_id)
print("After adding 120 Udhaar state:", dict(cust))
assert cust["credit_balance"] == 70.0, f"Expected 70 Udhaar, got {cust['credit_balance']}"
assert cust["change_balance"] == 0.0, f"Expected 0 Change, got {cust['change_balance']}"

# Verify transactions list
txns = db.get_customer_transactions(cust_id)
print("Transactions in ledger:")
for t in txns:
    print(dict(t))

# Cleanup
with db.get_conn() as conn:
    conn.execute("DELETE FROM customer_transactions WHERE customer_id = ?", (cust_id,))
    conn.execute("DELETE FROM customers WHERE customer_id = ?", (cust_id,))
    conn.commit()

print("Netting logic verification test passed successfully!")

from database import Database

db = Database()
db.init_db()

# Create customer
cust_id = db.add_customer({"name": "Surplus Test Cust", "phone": "1111111111", "address": "Address"})

# Case 1: Customer has 0 Udhaar, pays 50 (should all go to change_balance)
db.add_customer_transaction(cust_id, "Payment", 50.0, "REF-P1", "Payment test 1", 1)
cust = db.get_customer_by_id(cust_id)
print("Case 1 state:", dict(cust))
assert cust["credit_balance"] == 0, f"Expected 0 Udhaar, got {cust['credit_balance']}"
assert cust["change_balance"] == 50.0, f"Expected 50.0 change, got {cust['change_balance']}"

# Case 2: Customer gets 40 Udhaar (credit_balance becomes 40)
db.add_customer_transaction(cust_id, "Credit", 40.0, "REF-C1", "Credit test 1", 1)
cust = db.get_customer_by_id(cust_id)
print("Case 2 state:", dict(cust))
assert cust["credit_balance"] == 40.0, f"Expected 40.0 Udhaar, got {cust['credit_balance']}"

# Case 3: Customer pays 100 (40 should clear Udhaar, 60 should be added to change)
db.add_customer_transaction(cust_id, "Payment", 100.0, "REF-P2", "Payment test 2", 1)
cust = db.get_customer_by_id(cust_id)
print("Case 3 state:", dict(cust))
assert cust["credit_balance"] == 0.0, f"Expected 0.0 Udhaar, got {cust['credit_balance']}"
assert cust["change_balance"] == 110.0, f"Expected 110.0 change (50 from Case 1 + 60 surplus from Case 3), got {cust['change_balance']}"

# Verify transactions in ledger
txns = db.get_customer_transactions(cust_id)
print("Transactions in ledger:")
for t in txns:
    print(dict(t))

# Cleanup
with db.get_conn() as conn:
    conn.execute("DELETE FROM customer_transactions WHERE customer_id = ?", (cust_id,))
    conn.execute("DELETE FROM customers WHERE customer_id = ?", (cust_id,))
    conn.commit()

print("Payment surplus test passed successfully!")

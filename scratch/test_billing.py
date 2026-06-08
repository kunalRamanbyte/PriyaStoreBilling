from database import Database

db = Database()
db.init_db()

# Create test customer
cust_id = db.add_customer({"name": "Billing Test Cust", "phone": "9999999999", "address": "Address"})

# Prepare mock bill data where grand_total is 480, but customer paid 500 (20 change)
bill_data = {
    "customer_id": cust_id,
    "customer_name": "Billing Test Cust",
    "subtotal": 480.0,
    "discount": 0.0,
    "grand_total": 480.0,
    "udhaar_adjustment": 0.0,
    "payment_mode": "Cash",
    "amount_paid": 500.0,
    "change_due": 20.0
}

# Mock items
items = [
    {"product_id": 1, "product_name": "Aashirvaad Atta 5kg", "unit": "piece", "quantity": 1, "unit_price": 280, "discount": 0, "line_total": 280},
    {"product_id": 2, "product_name": "Fortune Sunflower Oil 1L", "unit": "litre", "quantity": 1, "unit_price": 200, "discount": 0, "line_total": 200}
]

# Save bill
bill_id = db.save_bill(bill_data, items, 1)
print(f"Saved bill ID: {bill_id}")

# Check customer's change_balance
cust = db.get_customer_by_id(cust_id)
print("Customer state after bill save:", dict(cust))

# Assert that change_balance is updated to 20
assert cust["change_balance"] == 20.0, f"Expected 20.0, got {cust['change_balance']}"

# Cleanup
with db.get_conn() as conn:
    conn.execute("DELETE FROM bill_items WHERE bill_id = ?", (bill_id,))
    conn.execute("DELETE FROM bills WHERE bill_id = ?", (bill_id,))
    conn.execute("DELETE FROM customer_transactions WHERE customer_id = ?", (cust_id,))
    conn.execute("DELETE FROM customers WHERE customer_id = ?", (cust_id,))
    conn.commit()

print("Bill save test passed successfully!")

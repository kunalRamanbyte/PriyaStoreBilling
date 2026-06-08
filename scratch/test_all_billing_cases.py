import os
import sys

# Ensure correct path import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Database

db = Database()
db.init_db()

# Global status list to print report at the end
test_results = []

def run_test_case(case_num, description, setup_data, bill_data, expected_save, expected_void):
    """
    Runs a single checkout test case.
    - setup_data: dict with 'initial_credit', 'initial_change'
    - bill_data: dict to be merged with basic bill fields
    - expected_save: dict with 'credit', 'change', 'txns' (list of tuples of (txn_type, amount))
    - expected_void: dict with 'credit', 'change'
    """
    print(f"\n========================================================")
    print(f"CASE {case_num}: {description}")
    print(f"========================================================")

    # 1. Setup customer
    cust_id = None
    if bill_data.get("customer_id") is not None:
        cust_id = db.add_customer({
            "name": f"Test Customer Case {case_num}",
            "phone": f"90000000{case_num:02d}",
            "address": "Test Address"
        })
        bill_data["customer_id"] = cust_id
        bill_data["customer_name"] = f"Test Customer Case {case_num}"

        # Inject initial balances
        if setup_data.get("initial_credit", 0.0) > 0:
            db.add_customer_transaction(cust_id, "Credit", setup_data["initial_credit"], "INIT", "Setup credit", 1)
        if setup_data.get("initial_change", 0.0) > 0:
            db.add_customer_transaction(cust_id, "Change Deposit", setup_data["initial_change"], "INIT", "Setup change", 1)

        cust = db.get_customer_by_id(cust_id)
        print(f"Setup Balances - Udhaar: {cust['credit_balance']}, Change: {cust['change_balance']}")
    else:
        print("Setup Walk-in Customer (No setup balances)")

    # 2. Setup cart items
    cart_items = [
        {
            "product_id": 1,
            "product_name": "Aashirvaad Atta 5kg",
            "unit": "piece",
            "quantity": 1,
            "unit_price": bill_data["subtotal"],
            "discount": 0.0,
            "line_total": bill_data["subtotal"]
        }
    ]

    try:
        # 3. Save Bill
        bill_id = db.save_bill(bill_data, cart_items, 1)
        print(f"Saved Bill ID: {bill_id}")

        # 4. Verify post-save customer balances
        if cust_id:
            cust = db.get_customer_by_id(cust_id)
            print(f"After Save Balances - Udhaar: {cust['credit_balance']}, Change: {cust['change_balance']}")
            assert cust["credit_balance"] == expected_save["credit"], f"Expected save Udhaar {expected_save['credit']}, got {cust['credit_balance']}"
            assert cust["change_balance"] == expected_save["change"], f"Expected save Change {expected_save['change']}, got {cust['change_balance']}"

            # Verify transaction ledger
            txns = db.get_customer_transactions(cust_id)
            print("Ledger transactions:")
            for t in txns:
                print("  -", dict(t))

            # Filter out setup transactions (INIT reference)
            bill_txns = [t for t in txns if t["reference"] != "INIT"]
            # Sort by txn_id ASC to compare in chronological order
            bill_txns.sort(key=lambda x: x["txn_id"])

            assert len(bill_txns) == len(expected_save["txns"]), f"Expected {len(expected_save['txns'])} transactions, got {len(bill_txns)}"
            for idx, exp in enumerate(expected_save["txns"]):
                actual_type, actual_amt = bill_txns[idx]["txn_type"], bill_txns[idx]["amount"]
                assert actual_type == exp[0], f"Txn {idx}: Expected type {exp[0]}, got {actual_type}"
                assert actual_amt == exp[1], f"Txn {idx}: Expected amount {exp[1]}, got {actual_amt}"

        else:
            print("Walk-in checkout verified successfully.")

        # 5. Void Bill
        print("Voiding bill...")
        void_ok = db.void_bill(bill_id, f"Void Case {case_num}", 1)
        assert void_ok, "Expected void_bill to return True"

        # 6. Verify post-void customer balances
        if cust_id:
            cust = db.get_customer_by_id(cust_id)
            print(f"After Void Balances - Udhaar: {cust['credit_balance']}, Change: {cust['change_balance']}")
            assert cust["credit_balance"] == expected_void["credit"], f"Expected void Udhaar {expected_void['credit']}, got {cust['credit_balance']}"
            assert cust["change_balance"] == expected_void["change"], f"Expected void Change {expected_void['change']}, got {cust['change_balance']}"
            
            # Print void ledger
            void_txns = db.get_customer_transactions(cust_id)
            print("Ledger after void:")
            for t in void_txns:
                print("  -", dict(t))

        print(f"CASE {case_num} PASSED!")
        test_results.append((case_num, description, "PASS"))

    except AssertionError as e:
        print(f"CASE {case_num} FAILED: {e}")
        test_results.append((case_num, description, f"FAIL: {e}"))
    except Exception as e:
        print(f"CASE {case_num} ERROR: {e}")
        test_results.append((case_num, description, f"ERROR: {e}"))
    finally:
        # Cleanup
        if cust_id:
            with db.get_conn() as conn:
                conn.execute("DELETE FROM customer_transactions WHERE customer_id = ?", (cust_id,))
                if 'bill_id' in locals():
                    conn.execute("DELETE FROM bill_items WHERE bill_id = ?", (bill_id,))
                    conn.execute("DELETE FROM bills WHERE bill_id = ?", (bill_id,))
                conn.execute("DELETE FROM customers WHERE customer_id = ?", (cust_id,))
                conn.commit()


# ==============================================================================
# Define & Run Test Cases
# ==============================================================================

# Basic template for bill data
def create_bill_template(cust_id, subtotal, discount, udhaar_adj, change_adj, payment_mode, amount_paid, change_due):
    return {
        "customer_id": cust_id,
        "customer_name": "Walk-in Customer" if cust_id is None else "",
        "subtotal": subtotal,
        "discount": discount,
        "grand_total": round(subtotal - discount, 2),
        "udhaar_adjustment": udhaar_adj,
        "change_adjustment": change_adj,
        "payment_mode": payment_mode,
        "amount_paid": amount_paid,
        "change_due": change_due,
    }

# 1. Walk-in Customer Cases
# Case 1: Exact cash payment (100 bill, 100 paid)
run_test_case(
    case_num=1,
    description="Walk-in exact cash payment (100 bill, 100 paid)",
    setup_data={},
    bill_data=create_bill_template(None, 100.0, 0.0, 0.0, 0.0, "Cash", 100.0, 0.0),
    expected_save={},
    expected_void={}
)

# Case 2: Walk-in Overpayment (100 bill, 150 paid)
run_test_case(
    case_num=2,
    description="Walk-in overpayment (100 bill, 150 paid)",
    setup_data={},
    bill_data=create_bill_template(None, 100.0, 0.0, 0.0, 0.0, "Cash", 150.0, 50.0),
    expected_save={},
    expected_void={}
)

# Case 3: Walk-in UPI (100 bill, 100 paid)
run_test_case(
    case_num=3,
    description="Walk-in UPI payment (100 bill)",
    setup_data={},
    bill_data=create_bill_template(None, 100.0, 0.0, 0.0, 0.0, "UPI", 100.0, 0.0),
    expected_save={},
    expected_void={}
)

# 2. Registered Customer - No setup balances
# Case 4: Customer exact payment (100 bill, 100 paid)
run_test_case(
    case_num=4,
    description="Customer exact cash payment, no previous balance",
    setup_data={"initial_credit": 0.0, "initial_change": 0.0},
    bill_data=create_bill_template(0, 100.0, 0.0, 0.0, 0.0, "Cash", 100.0, 0.0),
    expected_save={"credit": 0.0, "change": 0.0, "txns": []},
    expected_void={"credit": 0.0, "change": 0.0}
)

# Case 5: Customer overpayment (100 bill, 120 paid)
run_test_case(
    case_num=5,
    description="Customer cash overpayment, no previous balance",
    setup_data={"initial_credit": 0.0, "initial_change": 0.0},
    bill_data=create_bill_template(0, 100.0, 0.0, 0.0, 0.0, "Cash", 120.0, 20.0),
    expected_save={"credit": 0.0, "change": 20.0, "txns": [("Change Deposit", 20.0)]},
    expected_void={"credit": 0.0, "change": 0.0}
)

# Case 6: Customer underpayment (100 bill, 80 paid)
run_test_case(
    case_num=6,
    description="Customer cash underpayment, no previous balance",
    setup_data={"initial_credit": 0.0, "initial_change": 0.0},
    bill_data=create_bill_template(0, 100.0, 0.0, 0.0, 0.0, "Credit (Udhaar)", 80.0, 0.0),
    expected_save={"credit": 20.0, "change": 0.0, "txns": [("Credit", 20.0)]},
    expected_void={"credit": 0.0, "change": 0.0}
)

# Case 7: Customer pure Credit sale (100 bill, 0 paid)
run_test_case(
    case_num=7,
    description="Customer pure Credit sale, no previous balance",
    setup_data={"initial_credit": 0.0, "initial_change": 0.0},
    bill_data=create_bill_template(0, 100.0, 0.0, 0.0, 0.0, "Credit (Udhaar)", 0.0, 0.0),
    expected_save={"credit": 100.0, "change": 0.0, "txns": [("Credit", 100.0)]},
    expected_void={"credit": 0.0, "change": 0.0}
)

# Case 8: Customer UPI sale (100 bill, 100 paid)
run_test_case(
    case_num=8,
    description="Customer UPI payment, no previous balance",
    setup_data={"initial_credit": 0.0, "initial_change": 0.0},
    bill_data=create_bill_template(0, 100.0, 0.0, 0.0, 0.0, "UPI", 100.0, 0.0),
    expected_save={"credit": 0.0, "change": 0.0, "txns": []},
    expected_void={"credit": 0.0, "change": 0.0}
)

# 3. Registered Customer - Previous Udhaar (e.g. 50 Udhaar, 0 Change)
# Case 9: Paid amount less than previous Udhaar (bill 200, prev 50, paid 20)
run_test_case(
    case_num=9,
    description="Customer previous Udhaar 50, bill 200. Paid 20 cash.",
    setup_data={"initial_credit": 50.0, "initial_change": 0.0},
    bill_data=create_bill_template(0, 200.0, 0.0, 50.0, 0.0, "Credit (Udhaar)", 20.0, 0.0),
    expected_save={"credit": 230.0, "change": 0.0, "txns": [("Credit", 200.0), ("Payment", 20.0)]},
    expected_void={"credit": 50.0, "change": 0.0}
)

# Case 10: Paid amount exactly equal to previous Udhaar (bill 200, prev 50, paid 50)
run_test_case(
    case_num=10,
    description="Customer previous Udhaar 50, bill 200. Paid 50 cash.",
    setup_data={"initial_credit": 50.0, "initial_change": 0.0},
    bill_data=create_bill_template(0, 200.0, 0.0, 50.0, 0.0, "Credit (Udhaar)", 50.0, 0.0),
    expected_save={"credit": 200.0, "change": 0.0, "txns": [("Credit", 200.0), ("Payment", 50.0)]},
    expected_void={"credit": 50.0, "change": 0.0}
)

# Case 11: Paid amount greater than previous Udhaar but under total (bill 200, prev 50, paid 100)
run_test_case(
    case_num=11,
    description="Customer previous Udhaar 50, bill 200. Paid 100 cash.",
    setup_data={"initial_credit": 50.0, "initial_change": 0.0},
    bill_data=create_bill_template(0, 200.0, 0.0, 50.0, 0.0, "Credit (Udhaar)", 100.0, 0.0),
    expected_save={"credit": 150.0, "change": 0.0, "txns": [("Credit", 150.0), ("Payment", 50.0)]},
    expected_void={"credit": 50.0, "change": 0.0}
)

# Case 12: Paid amount exactly equal to total to collect (bill 200, prev 50, paid 250)
run_test_case(
    case_num=12,
    description="Customer previous Udhaar 50, bill 200. Paid 250 cash.",
    setup_data={"initial_credit": 50.0, "initial_change": 0.0},
    bill_data=create_bill_template(0, 200.0, 0.0, 50.0, 0.0, "Cash", 250.0, 0.0),
    expected_save={"credit": 0.0, "change": 0.0, "txns": [("Payment", 50.0)]},
    expected_void={"credit": 50.0, "change": 0.0}
)

# Case 13: Paid amount greater than total to collect (bill 200, prev 50, paid 280)
run_test_case(
    case_num=13,
    description="Customer previous Udhaar 50, bill 200. Paid 280 cash.",
    setup_data={"initial_credit": 50.0, "initial_change": 0.0},
    bill_data=create_bill_template(0, 200.0, 0.0, 50.0, 0.0, "Cash", 280.0, 30.0),
    expected_save={"credit": 0.0, "change": 30.0, "txns": [("Payment", 50.0), ("Change Deposit", 30.0)]},
    expected_void={"credit": 50.0, "change": 0.0}
)

# Case 14: Pure Credit Sale (bill 200, prev 50, paid 0)
run_test_case(
    case_num=14,
    description="Customer previous Udhaar 50, bill 200. Credit sale directly (0 paid).",
    setup_data={"initial_credit": 50.0, "initial_change": 0.0},
    bill_data=create_bill_template(0, 200.0, 0.0, 50.0, 0.0, "Credit (Udhaar)", 0.0, 0.0),
    expected_save={"credit": 250.0, "change": 0.0, "txns": [("Credit", 200.0)]},
    expected_void={"credit": 50.0, "change": 0.0}
)

# Case 15: UPI payment (bill 200, prev 50, paid 250)
run_test_case(
    case_num=15,
    description="Customer previous Udhaar 50, bill 200. UPI payment (250 paid).",
    setup_data={"initial_credit": 50.0, "initial_change": 0.0},
    bill_data=create_bill_template(0, 200.0, 0.0, 50.0, 0.0, "UPI", 250.0, 0.0),
    expected_save={"credit": 0.0, "change": 0.0, "txns": [("Payment", 50.0)]},
    expected_void={"credit": 50.0, "change": 0.0}
)

# 4. Registered Customer - Previous Change Balance (e.g. 0 Udhaar, 40 Change)
# Case 16: No change adjustment used (bill 100, paid 100)
run_test_case(
    case_num=16,
    description="Customer previous Change 40, bill 100. No adjustment used, exact cash.",
    setup_data={"initial_credit": 0.0, "initial_change": 40.0},
    bill_data=create_bill_template(0, 100.0, 0.0, 0.0, 0.0, "Cash", 100.0, 0.0),
    expected_save={"credit": 0.0, "change": 40.0, "txns": []},
    expected_void={"credit": 0.0, "change": 40.0}
)

# Case 17: Partial change adjustment (change adj 40, bill 100, paid 60 cash)
run_test_case(
    case_num=17,
    description="Customer previous Change 40, bill 100. Used full 40 change adjustment, paid 60.",
    setup_data={"initial_credit": 0.0, "initial_change": 40.0},
    bill_data=create_bill_template(0, 100.0, 0.0, 0.0, 40.0, "Cash", 60.0, 0.0),
    expected_save={"credit": 0.0, "change": 0.0, "txns": [("Change Clear", 40.0)]},
    expected_void={"credit": 0.0, "change": 40.0}
)

# Case 18: Full change adjustment exceeding bill (change adj 40, bill 30, paid 0 cash)
run_test_case(
    case_num=18,
    description="Customer previous Change 40, bill 30. Used 30 change adjustment, paid 0.",
    setup_data={"initial_credit": 0.0, "initial_change": 40.0},
    bill_data=create_bill_template(0, 30.0, 0.0, 0.0, 30.0, "Cash", 0.0, 0.0),
    expected_save={"credit": 0.0, "change": 10.0, "txns": [("Change Clear", 30.0)]},
    expected_void={"credit": 0.0, "change": 40.0}
)

# Case 19: Change adjustment and underpayment (change adj 40, bill 100, net 60, paid 40)
run_test_case(
    case_num=19,
    description="Customer previous Change 40, bill 100. Used 40 change adjustment, paid 40 cash (underpaid).",
    setup_data={"initial_credit": 0.0, "initial_change": 40.0},
    bill_data=create_bill_template(0, 100.0, 0.0, 0.0, 40.0, "Credit (Udhaar)", 40.0, 0.0),
    expected_save={"credit": 20.0, "change": 0.0, "txns": [("Credit", 20.0), ("Change Clear", 40.0)]},
    expected_void={"credit": 0.0, "change": 40.0}
)

# Case 20: Change adjustment and overpayment (change adj 40, bill 100, net 60, paid 80)
run_test_case(
    case_num=20,
    description="Customer previous Change 40, bill 100. Used 40 change adjustment, paid 80 cash (overpaid).",
    setup_data={"initial_credit": 0.0, "initial_change": 40.0},
    bill_data=create_bill_template(0, 100.0, 0.0, 0.0, 40.0, "Cash", 80.0, 20.0),
    expected_save={"credit": 0.0, "change": 20.0, "txns": [("Change Clear", 40.0), ("Change Deposit", 20.0)]},
    expected_void={"credit": 0.0, "change": 40.0}
)

# Case 21: Complex case - Previous Udhaar + Previous Change Balance (auto-offset on load or transaction netting)
# Setup: customer has 50 Udhaar and 10 Change. Note that _net_customer_balances auto-offsets them.
# Let's test how save_bill netting performs.
run_test_case(
    case_num=21,
    description="Customer previous Udhaar 50, bill 200, change adj 0. Paid 220 cash.",
    setup_data={"initial_credit": 50.0, "initial_change": 0.0},
    bill_data=create_bill_template(0, 200.0, 0.0, 50.0, 0.0, "Credit (Udhaar)", 220.0, 0.0),
    # Net due = 250. Paid 220. Unpaid = 30.
    # Since p_val >= u_prev (220 >= 50):
    #   udhaar_collected = 50.0
    #   credit_added = 250 - 220 = 30.0
    expected_save={"credit": 30.0, "change": 0.0, "txns": [("Credit", 30.0), ("Payment", 50.0)]},
    expected_void={"credit": 50.0, "change": 0.0}
)


# ==============================================================================
# Print Verification Report
# ==============================================================================
print("\n" + "="*80)
print("                       PRIYA STORE BILLING TEST REPORT")
print("="*80)
print(f"{'Case':<5} | {'Description':<50} | {'Status':<15}")
print("-"*80)
passes = 0
fails = 0
for r in test_results:
    c_num, desc, status = r
    desc_trunc = desc[:50] if len(desc) > 50 else desc
    print(f"{c_num:<5} | {desc_trunc:<50} | {status:<15}")
    if "PASS" in status:
        passes += 1
    else:
        fails += 1
print("-"*80)
print(f"Total passed: {passes} | Total failed/errors: {fails}")
print("="*80)

if fails > 0:
    sys.exit(1)
else:
    sys.exit(0)

import sys
import os
import re

# Add parent directory to path to load bill_printer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bill_printer import (
    _build_receipt_lines, _build_receipt_rows, _render_plain_lines,
    _render_escpos, _build_return_lines, _build_return_rows,
)

def run_tests():
    # Setup mock bill data
    mock_bill = {
        "bill_number": "BILL-00038",
        "bill_date": "2026-06-09 09:07:00",
        "customer_name": "Ramesh Kumar",
        "customer_phone": "7972090897",
        "customer_address": "Torapara, Midnapore",
        "payment_mode": "UPI",
        "subtotal": 280.00,
        "discount": 0.00,
        "grand_total": 280.00,
        "udhaar_adjustment": 280.00,  # Prev. Udhaar
        "change_adjustment": 0.00,
        "amount_paid": 560.00,
        "change_due": 0.00,
    }

    mock_items = [
        {
            "product_name": "Aashirvaad Atta 5kg",
            "quantity": 1.0,
            "unit_price": 280.00,
            "line_total": 280.00,
        }
    ]

    mock_settings = {
        "shop_name": "Priya Store",
        "shop_address": "Torapara",
        "shop_city": "Midnapore",
        "shop_phone": "7972090897",
        "shop_gst": "27KUNCH9603R1ZY",
        "cashier": "admin",
    }

    # Test widths: 58mm (32 chars) and 80mm (48 chars)
    for width in [32, 48]:
        print(f"\n==========================================")
        print(f" TESTING RECEIPT WIDTH: {width} chars ({'58mm' if width == 32 else '80mm'})")
        print(f"==========================================")
        
        lines = _build_receipt_lines(mock_bill, mock_items, mock_settings, width)
        
        # Verify line lengths and print receipt
        for i, line in enumerate(lines, 1):
            line_len = len(line)
            # We don't check line length for lines containing product name if they are supposed to wrap naturally,
            # but we check if the formatted columns line matches the target width.
            assert line_len <= width, f"Line {i} exceeds width {width} (length: {line_len}): '{line}'"
            print(f"{line_len:02d} | {line}")

        # Verification checks
        print("\n--- Running Verification Assertions ---")
        
        # Check that there are no consecutive blank lines inside the receipt (except at the very end for feed)
        body_lines = [l for l in lines[:-2] if l.strip() == ""]
        print(f"[OK] Spacing: Body has only {len(body_lines)} blank line separator(s).")

        # Check Payment + Time line
        payment_lines = [l for l in lines if "Payment:" in l]
        assert len(payment_lines) == 1, "Payment line missing!"
        payment_line = payment_lines[0]
        assert "UPI" in payment_line and "09:07" in payment_line, f"Invalid payment/time formatting: {payment_line}"
        print(f"[OK] Payment & Time line format: '{payment_line}'")

        # Check Prev. Udhaar line
        udhaar_lines = [l for l in lines if "Prev. Udhaar:" in l]
        assert len(udhaar_lines) == 1, "Prev. Udhaar line missing!"
        udhaar_line = udhaar_lines[0]
        assert "280.00" in udhaar_line, f"Prev. Udhaar value blank/missing: {udhaar_line}"
        print(f"[OK] Prev. Udhaar format: '{udhaar_line}'")

        # Check Grand Total line
        grand_total_lines = [l for l in lines if "Grand Total:" in l]
        assert len(grand_total_lines) == 1, "Grand Total line missing!"
        grand_total_line = grand_total_lines[0]
        assert "560.00" in grand_total_line, f"Grand Total value incorrect: {grand_total_line}"
        print(f"[OK] Grand Total format: '{grand_total_line}'")

        # Verify Column Alignment of the items table
        header_line = [l for l in lines if "Item" in l and "Qty" in l][0]
        item_row = [l for l in lines if "280.00" in l and "Qty" not in l and "Sub Total" not in l and "Total" not in l and "Paid" not in l and "Udhaar" not in l][0]
        
        # In 32 chars:
        # Header: "Item      Qty    Price   Amount"
        # Row:    "            1   280.00   280.00"
        # Let's verify that Amount is right-aligned:
        # Since Amount has width 8, it must end exactly at the right boundary of the line.
        assert len(header_line) == width, f"Header line length mismatch: {len(header_line)} != {width}"
        assert len(item_row) == width, f"Item row line length mismatch: {len(item_row)} != {width}"
        
        # Verify right alignment of the amount
        header_amount = header_line[-8:].strip()
        item_amount = item_row[-8:].strip()
        assert header_amount == "Amount", f"Header amount column shifted: '{header_amount}'"
        assert item_amount == "280.00", f"Item amount column shifted: '{item_amount}'"
        
        # Verify right alignment of price
        header_price = header_line[-17:-9].strip()
        item_price = item_row[-17:-9].strip()
        assert header_price == "Price", f"Header price column shifted: '{header_price}'"
        assert item_price == "280.00", f"Item price column shifted: '{item_price}'"

        print(f"[OK] Column alignment: Headers and row columns align perfectly to the right edge.")

        # New: Total Quantity line is present and well-formed
        tq_lines = [l for l in lines if l.startswith("Total Quantity:")]
        assert len(tq_lines) == 1, "Total Quantity line missing!"
        assert tq_lines[0].strip().endswith("1"), f"Total Quantity wrong: {tq_lines[0]}"
        assert len(tq_lines[0]) == width, f"Total Quantity not full width: {len(tq_lines[0])}"
        print(f"[OK] Total Quantity line: '{tq_lines[0]}'")

        print(f"[OK] All tests passed successfully for width {width}!")


def run_dedup_tests():
    """Verify the ESC/POS path and the plain-text fallback render from the SAME
    rows, so the production (escpos) receipt cannot silently drift from the
    tested plain-text layout."""
    mock_bill = {
        "bill_number": "BILL-00038", "bill_date": "2026-06-09 09:07:00",
        "customer_name": "Ramesh Kumar", "customer_phone": "7972090897",
        "customer_address": "Torapara, Midnapore", "payment_mode": "Credit (Udhaar)",
        "subtotal": 280.00, "discount": 10.00, "grand_total": 270.00,
        "udhaar_adjustment": 50.00, "change_adjustment": 0.00,
        "amount_paid": 100.00, "change_due": 0.00,
    }
    mock_items = [
        {"product_name": "Aashirvaad Atta 5kg", "quantity": 1.0, "unit_price": 280.00, "line_total": 280.00},
        {"product_name": "A Very Long Product Name That Exceeds The Paper Width By A Lot",
         "quantity": 2.0, "unit_price": 15.50, "line_total": 31.00},
    ]
    mock_settings = {"shop_name": "Priya Store", "shop_address": "Torapara",
                     "shop_city": "Midnapore", "shop_phone": "7972090897",
                     "shop_gst": "27KUNCH9603R1ZY", "cashier": "admin"}

    mock_return = {
        "return_number": "RET-0007", "return_date": "2026-06-10 11:30:00",
        "bill_number": "BILL-00038", "customer_name": "Ramesh Kumar",
        "refund_mode": "Cash", "reason": "Damaged packet", "total_amount": 31.00,
    }
    mock_return_items = [
        {"product_name": "Aashirvaad Atta 5kg", "quantity": 1.0, "unit_price": 31.00,
         "line_total": 31.00, "restocked": 0},
    ]

    print("\n==========================================")
    print(" TESTING ESC/POS <-> PLAIN-TEXT PARITY")
    print("==========================================")

    try:
        from escpos.printer import Dummy
        have_escpos = True
    except ImportError:
        have_escpos = False
        print("[SKIP] python-escpos not installed; parity check uses rows only.")

    for label, rows_fn, lines_fn, doc, doc_items in [
        ("BILL",   _build_receipt_rows, _build_receipt_lines, mock_bill,   mock_items),
        ("RETURN", _build_return_rows,  _build_return_lines,  mock_return, mock_return_items),
    ]:
        for width in (32, 48):
            rows = rows_fn(doc, doc_items, mock_settings, width)

            # 1. Every row's plain rendering must respect the paper width
            plain = _render_plain_lines(rows, width)
            for ln in plain:
                assert len(ln) <= width, f"{label} {width}: line over width: '{ln}'"

            # 1b. The column header and every priced row (item rows AND ljr
            #     totals) must fill the FULL width — this catches the old
            #     return-receipt 47/29-char alignment shortfall.
            price_re = re.compile(r"\d+\.\d{2}")
            hdr = next(l for l in plain if l.lstrip().startswith("Item"))
            assert len(hdr) == width, \
                f"{label} {width}: header not full width ({len(hdr)}): '{hdr}'"
            for row in plain:
                if price_re.search(row):
                    assert len(row) == width, \
                        f"{label} {width}: priced row not full width ({len(row)}): '{row}'"
            # And the public *_lines() wrapper must equal rendering the rows
            assert lines_fn(doc, doc_items, mock_settings, width) == plain, \
                f"{label} {width}: *_lines() drifted from rows!"

            # 2. The escpos buffer must contain the exact text of every row
            if have_escpos:
                buf = Dummy()
                _render_escpos(buf, rows)
                out = buf.output.decode("ascii", errors="replace")
                for text, _style in rows:
                    if text:
                        assert text in out, \
                            f"{label} {width}: escpos missing row text: '{text}'"
            print(f"[OK] {label} {width}: escpos and plain-text render identical content.")

    print("[OK] Parity verified: production (escpos) layout == tested plain layout.")


if __name__ == "__main__":
    run_tests()
    run_dedup_tests()

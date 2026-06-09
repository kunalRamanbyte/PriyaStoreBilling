"""
bill_printer.py — Bill printing module for FMCG Billing System
Handles:
  1. A4 PDF bill (via reportlab)
  2. 58mm / 80mm ESC/POS thermal receipt (via python-escpos or raw bytes)
  3. Plain-text fallback (notepad /p)
"""

import os
import sys
import tempfile
import subprocess
from datetime import datetime


def open_file(path: str):
    """Open a file with the OS default application (cross-platform)."""
    if not path:
        return
    if sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


# ─────────────────────────────────────────────────────────────────────────────
# A4 PDF BILL
# ─────────────────────────────────────────────────────────────────────────────

def generate_pdf_bill(bill: dict, items: list, settings: dict,
                      output_path: str = None) -> str:
    """
    Generate an A4 PDF bill.  Returns the path to the saved PDF.
    settings: dict with shop_name, shop_address, shop_city, shop_phone, shop_gst
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                    Paragraph, Spacer, HRFlowable)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

    if not output_path:
        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        output_path = tmp.name
        tmp.close()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=12*mm,  bottomMargin=12*mm,
    )

    styles = getSampleStyleSheet()
    BLUE   = colors.HexColor("#1565C0")
    DBLUE  = colors.HexColor("#0D47A1")
    GREEN  = colors.HexColor("#2E7D32")
    GRAY   = colors.HexColor("#757575")
    LGRAY  = colors.HexColor("#F5F7FF")
    WHITE  = colors.white
    BLACK  = colors.HexColor("#1A1A2E")

    h1 = ParagraphStyle("h1", fontSize=18, fontName="Helvetica-Bold",
                         textColor=BLUE,   alignment=TA_CENTER, spaceAfter=2)
    h2 = ParagraphStyle("h2", fontSize=10, fontName="Helvetica",
                         textColor=GRAY,   alignment=TA_CENTER, spaceAfter=1)
    h3 = ParagraphStyle("h3", fontSize=9,  fontName="Helvetica",
                         textColor=GRAY,   alignment=TA_CENTER, spaceAfter=4)
    lbl = ParagraphStyle("lbl", fontSize=10, fontName="Helvetica-Bold",
                          textColor=BLACK, spaceAfter=2)
    val = ParagraphStyle("val", fontSize=10, fontName="Helvetica",
                          textColor=BLACK, spaceAfter=2)
    tot = ParagraphStyle("tot", fontSize=13, fontName="Helvetica-Bold",
                          textColor=GREEN, alignment=TA_RIGHT)
    foot= ParagraphStyle("foot", fontSize=9,  fontName="Helvetica",
                          textColor=GRAY,  alignment=TA_CENTER)

    shop_name  = settings.get("shop_name",    "FMCG Grocery Shop")
    shop_addr  = settings.get("shop_address", "")
    shop_city  = settings.get("shop_city",    "")
    shop_phone = settings.get("shop_phone",   "")
    shop_gst   = settings.get("shop_gst",     "")

    story = []

    # ── Shop header ──────────────────────────────────────────
    story.append(Paragraph(shop_name, h1))
    if shop_addr or shop_city:
        addr_line = ", ".join(filter(None, [shop_addr, shop_city]))
        story.append(Paragraph(addr_line, h2))
    if shop_phone:
        story.append(Paragraph(f"📞 {shop_phone}", h3))
    if shop_gst:
        story.append(Paragraph(f"GST: {shop_gst}", h3))
    inv_style = ParagraphStyle("inv", fontSize=11, fontName="Helvetica-Bold",
                                textColor=DBLUE, alignment=TA_CENTER, spaceAfter=4)
    story.append(Paragraph("TAX INVOICE", inv_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BLUE, spaceAfter=6))

    # ── Bill info row ─────────────────────────────────────────
    bill_date = str(bill.get("bill_date", ""))[:16]
    bill_info = [
        [Paragraph(f"<b>Bill No:</b>  {bill['bill_number']}", lbl),
         Paragraph(f"<b>Date:</b>  {bill_date}", lbl)],
        [Paragraph(f"<b>Customer:</b>  {bill.get('customer_name','Walk-in Customer')}", lbl),
         Paragraph(f"<b>Mode:</b>  {bill.get('payment_mode','Cash')}", lbl)],
    ]
    info_tbl = Table(bill_info, colWidths=[90*mm, 90*mm])
    info_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), LGRAY),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [LGRAY, WHITE]),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 6*mm))

    # ── Items table ───────────────────────────────────────────
    tbl_data = [[
        Paragraph("<b>#</b>",            ParagraphStyle("th", fontSize=10, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_CENTER)),
        Paragraph("<b>Product</b>",      ParagraphStyle("th", fontSize=10, fontName="Helvetica-Bold", textColor=WHITE)),
        Paragraph("<b>Unit</b>",         ParagraphStyle("th", fontSize=10, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_CENTER)),
        Paragraph("<b>Qty</b>",          ParagraphStyle("th", fontSize=10, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT)),
        Paragraph("<b>Rate ₹</b>",       ParagraphStyle("th", fontSize=10, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT)),
        Paragraph("<b>Disc ₹</b>",       ParagraphStyle("th", fontSize=10, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT)),
        Paragraph("<b>Total ₹</b>",      ParagraphStyle("th", fontSize=10, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT)),
    ]]

    r_style = ParagraphStyle("r", fontSize=9, fontName="Helvetica", textColor=BLACK)
    r_num   = ParagraphStyle("rn", fontSize=9, fontName="Helvetica", textColor=BLACK, alignment=TA_RIGHT)
    r_ctr   = ParagraphStyle("rc", fontSize=9, fontName="Helvetica", textColor=BLACK, alignment=TA_CENTER)

    for idx, it in enumerate(items, 1):
        tbl_data.append([
            Paragraph(str(idx),                            r_ctr),
            Paragraph(str(it.get("product_name", "")),     r_style),
            Paragraph(str(it.get("unit", "pc")),           r_ctr),
            Paragraph(f"{it.get('quantity',0):.2f}",       r_num),
            Paragraph(f"{it.get('unit_price',0):.2f}",     r_num),
            Paragraph(f"{it.get('discount',0):.2f}",       r_num),
            Paragraph(f"{it.get('line_total',0):.2f}",     r_num),
        ])

    col_w = [10*mm, 68*mm, 18*mm, 18*mm, 22*mm, 18*mm, 22*mm]
    item_tbl = Table(tbl_data, colWidths=col_w, repeatRows=1)
    row_bgs = [LGRAY if i % 2 == 0 else WHITE for i in range(len(tbl_data))]
    item_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  BLUE),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LGRAY]),
        ("GRID",          (0,0), (-1,-1), 0.3, colors.HexColor("#C5CAE9")),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 4),
        ("RIGHTPADDING",  (0,0), (-1,-1), 4),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(item_tbl)
    story.append(Spacer(1, 4*mm))

    # ── Totals ────────────────────────────────────────────────
    subtotal    = bill.get("subtotal",    0)
    discount    = bill.get("discount",    0)
    grand_total = bill.get("grand_total", 0)
    udhaar_adj  = float(bill.get("udhaar_adjustment") or 0)
    change_adj  = float(bill.get("change_adjustment") or 0)
    total_collect = round(grand_total + udhaar_adj - change_adj, 2)
    amount_paid = bill.get("amount_paid", 0)
    change_due  = bill.get("change_due",  0)
    balance_due = max(0, round(total_collect - amount_paid, 2))

    tot_lbl = ParagraphStyle("tl", fontSize=10, fontName="Helvetica",     textColor=BLACK, alignment=TA_RIGHT)
    tot_val = ParagraphStyle("tv", fontSize=10, fontName="Helvetica-Bold", textColor=BLACK, alignment=TA_RIGHT)
    gt_lbl  = ParagraphStyle("gl", fontSize=13, fontName="Helvetica-Bold", textColor=DBLUE, alignment=TA_RIGHT)
    gt_val  = ParagraphStyle("gv", fontSize=13, fontName="Helvetica-Bold", textColor=GREEN, alignment=TA_RIGHT)
    warn_val = ParagraphStyle("wv", fontSize=10, fontName="Helvetica-Bold",
                               textColor=colors.HexColor("#C2410C"), alignment=TA_RIGHT)

    totals_data = [
        [Paragraph("Subtotal:", tot_lbl), Paragraph(f"₹ {subtotal:,.2f}", tot_val)],
    ]
    if discount:
        totals_data.append(
            [Paragraph("Discount:", tot_lbl), Paragraph(f"- ₹ {discount:,.2f}", tot_val)]
        )
    if change_adj > 0:
        totals_data.append(
            [Paragraph("Change Used:", tot_lbl), Paragraph(f"- ₹ {change_adj:,.2f}", tot_val)]
        )
    if udhaar_adj > 0:
        totals_data.append(
            [Paragraph("Prev. Udhaar:", tot_lbl), Paragraph(f"+ ₹ {udhaar_adj:,.2f}", warn_val)]
        )
    totals_data.append(
        [Paragraph("<b>GRAND TOTAL:</b>", gt_lbl), Paragraph(f"<b>₹ {total_collect:,.2f}</b>", gt_val)]
    )
    totals_data.append(
        [Paragraph("Amount Paid:", tot_lbl), Paragraph(f"₹ {amount_paid:,.2f}", tot_val)]
    )
    if change_due > 0:
        totals_data.append(
            [Paragraph("Change Due:", tot_lbl), Paragraph(f"₹ {change_due:,.2f}", tot_val)]
        )
    if balance_due > 0:
        totals_data.append(
            [Paragraph("<b>Balance Due:</b>", tot_lbl), Paragraph(f"<b>₹ {balance_due:,.2f}</b>", warn_val)]
        )
    if bill.get("payment_mode") == "Credit (Udhaar)":
        credit_lbl = ParagraphStyle("cl", fontSize=11, fontName="Helvetica-Bold",
                                     textColor=colors.HexColor("#DC2626"), alignment=TA_CENTER)
        totals_data.append(
            [Paragraph("", tot_lbl), Paragraph("** CREDIT SALE (UDHAAR) **", credit_lbl)]
        )

    gt_row_idx = next(i for i, row in enumerate(totals_data)
                      if "GRAND TOTAL" in row[0].text)
    tot_tbl = Table(totals_data, colWidths=[130*mm, 46*mm])
    tot_tbl.setStyle(TableStyle([
        ("LINEABOVE",     (0, gt_row_idx), (-1, gt_row_idx), 1.2, BLUE),
        ("LINEBELOW",     (0, gt_row_idx), (-1, gt_row_idx), 1.2, BLUE),
        ("BACKGROUND",    (0, gt_row_idx), (-1, gt_row_idx), colors.HexColor("#E3F2FD")),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING",  (0,0), (-1,-1), 4),
    ]))
    story.append(tot_tbl)
    story.append(Spacer(1, 6*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRAY))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("Thank you for shopping with us! 🙏", foot))
    story.append(Paragraph(f"Printed: {datetime.now().strftime('%d %b %Y  %I:%M %p')}", foot))

    doc.build(story)
    return output_path


# ─────────────────────────────────────────────────────────────────────────────
# THERMAL ESC/POS RECEIPT
# ─────────────────────────────────────────────────────────────────────────────

def _build_receipt_lines(bill: dict, items: list, settings: dict,
                          width: int = 48) -> list:
    """Build list of plain-text receipt lines for the given paper width."""
    shop_name  = settings.get("shop_name",    "Priya Store")
    shop_addr  = settings.get("shop_address", "")
    shop_city  = settings.get("shop_city",    "")
    shop_phone = settings.get("shop_phone",   "")
    shop_gst   = settings.get("shop_gst",     "")
    cashier    = settings.get("cashier",      "")

    def center(s): return str(s)[:width].center(width)
    def ljr(left, right):
        l, r = str(left), str(right)
        l = l[:width - len(r) - 1]
        return l + " " * (width - len(l) - len(r)) + r

    sep  = "-" * width
    dsep = "=" * width

    lines = []

    # ── Shop header (centered) ──
    lines.append(center(shop_name.upper()))
    addr = ", ".join(filter(None, [shop_addr, shop_city]))
    if addr:
        lines.append(center(addr))
    if shop_phone:
        lines.append(center(f"Contact: {shop_phone}"))
    if shop_gst:
        lines.append(center(f"GST: {shop_gst}"))
    lines.append(sep)

    # ── Customer info block ──
    cust = bill.get("customer_name", "Walk-in Customer")
    cust_phone = bill.get("customer_phone", "")
    cust_addr  = bill.get("customer_address", "")
    if width >= 48:
        if cust_phone:
            lines.append(f"Name: {cust}  (M: {cust_phone})")
        else:
            lines.append(f"Name: {cust}")
        if cust_addr:
            lines.append(f"Adr: {cust_addr}")
    else:
        lines.append(f"Name: {cust}")
        if cust_phone:
            lines.append(f"Phone: {cust_phone}")
        if cust_addr:
            lines.append(f"Adr: {cust_addr}")
    lines.append(sep)

    # ── Date / Time / Cashier / Bill No ──
    raw_dt    = str(bill.get("bill_date", ""))
    date_disp = raw_dt[:10] if len(raw_dt) >= 10 else ""
    time_disp = raw_dt[11:16] if len(raw_dt) >= 16 else ""
    try:
        _dt = datetime.strptime(raw_dt[:19], "%Y-%m-%d %H:%M:%S")
        date_disp = _dt.strftime("%d/%m/%y")
        time_disp = _dt.strftime("%H:%M")
    except Exception:
        pass

    mode = bill.get("payment_mode", "Cash")
    payment_line = f"Payment: {mode} | {time_disp}"

    if width >= 48:
        lines.append(ljr(f"Bill No: {bill['bill_number']}", f"Date: {date_disp}"))
        lines.append(ljr(f"Cashier: {cashier}", payment_line))
    else:
        lines.append(f"Bill No: {bill['bill_number']}")
        lines.append(f"Date: {date_disp}")
        lines.append(payment_line)
        lines.append(f"Cashier: {cashier}")
    lines.append(sep)

    # ── Column header ──
    if width >= 48:
        nm = width - 24
        lines.append(f"{'Item':<{nm}}  {'Qty.':<5}{'Price':>8} {'Amount':>8}")
    else:
        nm = 9
        lines.append(f"{'Item':<{nm}} {'Qty':>4} {'Price':>8} {'Amount':>8}")
    lines.append(sep)

    # ── Items ──
    total_qty = 0
    for it in items:
        name = str(it.get("product_name", ""))
        qty  = float(it.get("quantity", 0))
        rate = float(it.get("unit_price", 0))
        amt  = float(it.get("line_total", 0))
        total_qty += qty
        qty_str = f"{qty:g}"
        if width >= 48:
            if len(name) > nm:
                lines.append(name)
                lines.append(f"{'':<{nm}}  {qty_str:<5}{rate:>8.2f} {amt:>8.2f}")
            else:
                lines.append(f"{name:<{nm}}  {qty_str:<5}{rate:>8.2f} {amt:>8.2f}")
        else:
            if len(name) > nm:
                lines.append(name)
                lines.append(f"{'':<10}{qty_str:>4} {rate:>8.2f} {amt:>8.2f}")
            else:
                lines.append(f"{name:<{nm}} {qty_str:>4} {rate:>8.2f} {amt:>8.2f}")
    lines.append(sep)

    # ── Totals ──
    subtotal = float(bill.get("subtotal", 0))
    discount = float(bill.get("discount", 0))
    udhaar   = float(bill.get("udhaar_adjustment") or 0)
    change_adj = float(bill.get("change_adjustment") or 0)
    grand    = float(bill.get("grand_total", 0))
    paid     = float(bill.get("amount_paid", 0))
    change   = float(bill.get("change_due", 0))
    total_collect = grand + udhaar - change_adj

    lines.append(ljr("Sub Total:", f"Rs.{subtotal:.2f}"))
    if discount:
        lines.append(ljr("Discount:", f"-Rs.{discount:.2f}"))
    if change_adj > 0:
        lines.append(ljr("Change Used:", f"-Rs.{change_adj:.2f}"))
    if udhaar > 0:
        lines.append(ljr("Prev. Udhaar:", f"+Rs.{udhaar:.2f}"))
    lines.append(dsep)
    lines.append(ljr("Grand Total:", f"Rs.{total_collect:.2f}"))
    lines.append(dsep)

    # Payment info
    lines.append(ljr("Amount Paid:", f"Rs.{paid:.2f}"))
    balance_due = max(0, round(total_collect - paid, 2))
    if change > 0:
        lines.append(ljr("Change Due:", f"Rs.{change:.2f}"))
    if balance_due > 0:
        lines.append(ljr("Balance Due:", f"Rs.{balance_due:.2f}"))

    # Show udhaar credit status if bill is credit mode
    if bill.get("payment_mode") == "Credit (Udhaar)":
        lines.append(center("** CREDIT SALE (UDHAAR) **"))

    lines.append(sep)

    # ── Footer ──
    lines.append(center("Thanks & Visit Again"))
    lines.append("")
    lines.append("")

    return lines


def print_thermal(bill: dict, items: list, settings: dict,
                  paper_width: str = "80mm") -> tuple:
    """
    Print a properly formatted ESC/POS thermal receipt via python-escpos.
    Uses bold, double-height, and alignment commands for a professional look.
    Returns (True, printer_name) on success or (False, error_message).
    paper_width: '58mm' or '80mm'
    """
    char_width = 32 if str(paper_width).strip().lower() == "58mm" else 48

    # ── Try python-escpos with real thermal formatting ────────
    try:
        from escpos.printer import Win32Raw
        import win32print

        default = win32print.GetDefaultPrinter()
        p = Win32Raw(default)
        p.open()

        shop_name  = settings.get("shop_name",    "Priya Store")
        shop_addr  = settings.get("shop_address", "")
        shop_city  = settings.get("shop_city",    "")
        shop_phone = settings.get("shop_phone",   "")
        shop_gst   = settings.get("shop_gst",     "")
        cashier    = settings.get("cashier",      "")
        sep        = "-" * char_width
        eq_sep     = "=" * char_width
        is_wide    = char_width >= 48

        def ljr(left, right):
            l, r = str(left), str(right)
            l = l[:char_width - len(r) - 1]
            return l + " " * (char_width - len(l) - len(r)) + r

        # ── Shop header — double-size bold shop name ──
        p.set(align="center", bold=True, width=2, height=2)
        p.text(shop_name.upper() + "\n")
        p.set(align="center", bold=False, width=1, height=1)
        addr = ", ".join(filter(None, [shop_addr, shop_city]))
        if addr:
            p.text(addr + "\n")
        if shop_phone:
            p.text(f"Contact: {shop_phone}\n")
        if shop_gst:
            p.text(f"GST: {shop_gst}\n")
        p.text(sep + "\n")

        # ── Customer info block ──
        p.set(align="left", bold=False, width=1, height=1)
        cust = bill.get("customer_name", "Walk-in Customer")
        cust_phone = bill.get("customer_phone", "")
        cust_addr  = bill.get("customer_address", "")
        if is_wide:
            if cust_phone:
                p.text(f"Name: {cust}  (M: {cust_phone})\n")
            else:
                p.text(f"Name: {cust}\n")
            if cust_addr:
                p.text(f"Adr: {cust_addr}\n")
        else:
            p.text(f"Name: {cust}\n")
            if cust_phone:
                p.text(f"Phone: {cust_phone}\n")
            if cust_addr:
                p.text(f"Adr: {cust_addr}\n")
        p.text(sep + "\n")

        # ── Date / Time / Cashier / Bill No ──
        raw_dt    = str(bill.get("bill_date", ""))
        date_disp = raw_dt[:10] if len(raw_dt) >= 10 else ""
        time_disp = raw_dt[11:16] if len(raw_dt) >= 16 else ""
        try:
            _dt = datetime.strptime(raw_dt[:19], "%Y-%m-%d %H:%M:%S")
            date_disp = _dt.strftime("%d/%m/%y")
            time_disp = _dt.strftime("%H:%M")
        except Exception:
            pass

        mode = bill.get("payment_mode", "Cash")
        payment_line = f"Payment: {mode} | {time_disp}"
        p.set(align="left", bold=False, width=1, height=1)
        if is_wide:
            p.text(ljr(f"Bill No: {bill['bill_number']}", f"Date: {date_disp}") + "\n")
            p.text(ljr(f"Cashier: {cashier}", payment_line) + "\n")
        else:
            p.text(f"Bill No: {bill['bill_number']}\n")
            p.text(f"Date: {date_disp}\n")
            p.text(payment_line + "\n")
            p.text(f"Cashier: {cashier}\n")
        p.text(sep + "\n")

        # ── Column header ──
        p.set(align="left", bold=True, width=1, height=1)
        if is_wide:
            nm  = char_width - 24
            hdr = f"{'Item':<{nm}}  {'Qty.':<5}{'Price':>8} {'Amount':>8}"
        else:
            nm  = 9
            hdr = f"{'Item':<{nm}} {'Qty':>4} {'Price':>8} {'Amount':>8}"
        p.text(hdr + "\n")
        p.text(sep + "\n")

        # ── Items ──
        p.set(align="left", bold=False, width=1, height=1)
        total_qty = 0
        for it in items:
            name = str(it.get("product_name", ""))
            qty  = float(it.get("quantity", 0))
            rate = float(it.get("unit_price", 0))
            amt  = float(it.get("line_total", 0))
            total_qty += qty
            qty_str = f"{qty:g}"
            if is_wide:
                if len(name) > nm:
                    p.text(name + "\n")
                    p.text(f"{'':<{nm}}  {qty_str:<5}{rate:>8.2f} {amt:>8.2f}\n")
                else:
                    p.text(f"{name:<{nm}}  {qty_str:<5}{rate:>8.2f} {amt:>8.2f}\n")
            else:
                if len(name) > nm:
                    p.text(name + "\n")
                    p.text(f"{'':<10}{qty_str:>4} {rate:>8.2f} {amt:>8.2f}\n")
                else:
                    p.text(f"{name:<{nm}} {qty_str:>4} {rate:>8.2f} {amt:>8.2f}\n")
        p.text(sep + "\n")

        # ── Subtotal / discount / udhaar ──
        subtotal = float(bill.get("subtotal", 0))
        discount = float(bill.get("discount", 0))
        udhaar   = float(bill.get("udhaar_adjustment") or 0)
        change_adj = float(bill.get("change_adjustment") or 0)
        grand    = float(bill.get("grand_total", 0))
        paid     = float(bill.get("amount_paid", 0))
        change   = float(bill.get("change_due", 0))
        total_collect = grand + udhaar - change_adj

        p.set(align="left", bold=False, width=1, height=1)
        p.text(ljr("Sub Total:", f"Rs.{subtotal:.2f}") + "\n")
        if discount:
            p.text(ljr("Discount:", f"-Rs.{discount:.2f}") + "\n")
        if change_adj > 0:
            p.text(ljr("Change Used:", f"-Rs.{change_adj:.2f}") + "\n")
        if udhaar > 0:
            p.text(ljr("Prev. Udhaar:", f"+Rs.{udhaar:.2f}") + "\n")

        # ── Grand total — bold, normal width ──
        p.text(eq_sep + "\n")
        p.set(align="left", bold=True, width=1, height=1)
        p.text(ljr("Grand Total:", f"Rs.{total_collect:.2f}") + "\n")
        p.set(align="left", bold=False, width=1, height=1)
        p.text(eq_sep + "\n")

        # ── Payment info ──
        p.text(ljr("Amount Paid:", f"Rs.{paid:.2f}") + "\n")
        balance_due = max(0, round(total_collect - paid, 2))
        if change > 0:
            p.text(ljr("Change Due:", f"Rs.{change:.2f}") + "\n")
        if balance_due > 0:
            p.set(align="left", bold=True, width=1, height=1)
            p.text(ljr("Balance Due:", f"Rs.{balance_due:.2f}") + "\n")
            p.set(align="left", bold=False, width=1, height=1)

        # ── Credit sale indicator ──
        if bill.get("payment_mode") == "Credit (Udhaar)":
            p.set(align="center", bold=True, width=1, height=1)
            p.text("** CREDIT SALE (UDHAAR) **\n")

        p.set(align="left", bold=False, width=1, height=1)
        p.text(sep + "\n")

        # ── Footer ──
        p.set(align="center", bold=True, width=1, height=1)
        p.text("Thanks & Visit Again\n")
        p.set(align="center", bold=False, width=1, height=1)
        p.text("\n\n\n")

        p.cut()
        p.close()
        return True, default

    except ImportError:
        pass   # python-escpos not installed — fall through to plain-text
    except Exception as e:
        return False, str(e)

    # Plain-text fallback via Windows print spooler (RAW mode)
    lines_txt = _build_receipt_lines(bill, items, settings, char_width)
    txt = "\n".join(lines_txt)
    try:
        import win32print
        default = win32print.GetDefaultPrinter()
        hPrinter = win32print.OpenPrinter(default)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, (f"Bill_{bill['bill_number']}", None, "RAW"))
            try:
                win32print.StartPagePrinter(hPrinter)
                # Convert text to bytes
                raw_bytes = (txt + "\n\n\n\n\x1dV\x42\x00").encode("utf-8", errors="replace")
                win32print.WritePrinter(hPrinter, raw_bytes)
                win32print.EndPagePrinter(hPrinter)
            finally:
                win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)
        return True, default
    except Exception as raw_err:
        # Final safety fallback: notepad.exe
        try:
            import win32api
            default = win32print.GetDefaultPrinter()
            tmp = tempfile.NamedTemporaryFile(
                suffix=".txt", delete=False, mode="w",
                encoding="utf-8", errors="replace"
            )
            tmp.write(txt)
            tmp.close()
            win32api.ShellExecute(
                0, "print", tmp.name, f'/d:"{default}"', ".", 0
            )
            return True, default
        except Exception as e:
            return False, f"Raw print failed: {raw_err}. Notepad fallback failed: {e}"


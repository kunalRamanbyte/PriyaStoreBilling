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
    amount_paid = bill.get("amount_paid", 0)
    change_due  = bill.get("change_due",  0)

    tot_lbl = ParagraphStyle("tl", fontSize=10, fontName="Helvetica",     textColor=BLACK, alignment=TA_RIGHT)
    tot_val = ParagraphStyle("tv", fontSize=10, fontName="Helvetica-Bold", textColor=BLACK, alignment=TA_RIGHT)
    gt_lbl  = ParagraphStyle("gl", fontSize=13, fontName="Helvetica-Bold", textColor=DBLUE, alignment=TA_RIGHT)
    gt_val  = ParagraphStyle("gv", fontSize=13, fontName="Helvetica-Bold", textColor=GREEN, alignment=TA_RIGHT)

    totals_data = [
        [Paragraph("Subtotal:", tot_lbl), Paragraph(f"₹ {subtotal:,.2f}", tot_val)],
    ]
    if discount:
        totals_data.append(
            [Paragraph("Discount:", tot_lbl), Paragraph(f"- ₹ {discount:,.2f}", tot_val)]
        )
    totals_data += [
        [Paragraph("<b>GRAND TOTAL:</b>", gt_lbl), Paragraph(f"<b>₹ {grand_total:,.2f}</b>", gt_val)],
        [Paragraph("Amount Paid:", tot_lbl),        Paragraph(f"₹ {amount_paid:,.2f}", tot_val)],
        [Paragraph("Change Due:", tot_lbl),         Paragraph(f"₹ {change_due:,.2f}", tot_val)],
    ]
    gt_row = len(totals_data) - 3   # index of the GRAND TOTAL row
    tot_tbl = Table(totals_data, colWidths=[130*mm, 46*mm])
    tot_tbl.setStyle(TableStyle([
        ("LINEABOVE",     (0, gt_row), (-1, gt_row), 1.2, BLUE),
        ("LINEBELOW",     (0, gt_row), (-1, gt_row), 1.2, BLUE),
        ("BACKGROUND",    (0, gt_row), (-1, gt_row), colors.HexColor("#E3F2FD")),
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
    shop_name  = settings.get("shop_name",    "FMCG Shop")
    shop_addr  = settings.get("shop_address", "")
    shop_phone = settings.get("shop_phone",   "")
    shop_gst   = settings.get("shop_gst",     "")

    def center(s): return s[:width].center(width)
    def ljr(left, right):
        left  = str(left)[:width - len(str(right)) - 1]
        return left + " " * (width - len(left) - len(str(right))) + str(right)

    sep  = "-" * width
    dsep = "=" * width

    lines = [
        dsep,
        center(shop_name.upper()),
    ]
    if shop_addr:
        lines.append(center(shop_addr))
    if shop_phone:
        lines.append(center(shop_phone))
    if shop_gst:
        lines.append(center(f"GST: {shop_gst}"))
    lines.append(center("--- TAX INVOICE ---"))
    lines.append(dsep)

    # Bill info
    lines.append(ljr(f"Bill: {bill['bill_number']}", str(bill.get('bill_date',''))[:10]))
    lines.append(ljr(f"Cust: {bill.get('customer_name','Walk-in')[:20]}", bill.get('payment_mode','Cash')))
    lines.append(sep)

    # Column header — adapt columns to paper width
    if width >= 48:
        # 80mm: #(3) Name(20) Qty(4) Rate(7) Disc(5) Amt(7) = 48 with spaces
        hdr = f"{'#':>3} {'Item':<{width-28}} {'Qty':>4} {'Rate':>7} {'Disc':>5} {'Amt':>7}"
    else:
        # 58mm: #(3) Name(10) Qty(3) Rate(5) Amt(7) = ~32
        hdr = f"{'#':>2} {'Item':<{width-21}} {'Qty':>3} {'Rate':>5} {'Amt':>7}"
    lines.append(hdr)
    lines.append(sep)

    # Items
    for idx, it in enumerate(items, 1):
        name = str(it.get("product_name",""))
        qty  = f"{it.get('quantity',0):.0f}"
        rate = f"{it.get('unit_price',0):.0f}"
        disc = f"{it.get('discount',0):.0f}"
        amt  = f"{it.get('line_total',0):.2f}"

        if width >= 48:
            max_name = width - 28
            name = name[:max_name]
            lines.append(f"{idx:>3} {name:<{max_name}} {qty:>4} {rate:>7} {disc:>5} {amt:>7}")
        else:
            max_name = width - 21
            name = name[:max_name]
            lines.append(f"{idx:>2} {name:<{max_name}} {qty:>3} {rate:>5} {amt:>7}")

    lines.append(sep)

    # Totals
    lines.append(ljr("Subtotal:",    f"Rs.{bill.get('subtotal',0):>8.2f}"))
    if bill.get("discount", 0):
        lines.append(ljr("Discount:",  f" - {bill.get('discount',0):>8.2f}"))
    lines.append(dsep)
    lines.append(ljr("GRAND TOTAL:", f"Rs.{bill.get('grand_total',0):>8.2f}"))
    lines.append(dsep)
    lines.append(ljr("Amount Paid:", f"Rs.{bill.get('amount_paid',0):>8.2f}"))
    lines.append(ljr("Change Due:",  f"Rs.{bill.get('change_due',0):>8.2f}"))
    lines.append(sep)

    # Footer
    lines.append(center("Thank you! Come again"))
    lines.append(center(datetime.now().strftime("%d %b %Y  %I:%M %p")))
    lines.append("")
    lines.append("")  # paper feed

    return lines


def print_thermal(bill: dict, items: list, settings: dict,
                  paper_width: str = "80mm") -> tuple:
    """
    Print a properly formatted ESC/POS thermal receipt via python-escpos.
    Uses bold, double-height, and alignment commands for a professional look.
    Returns (True, printer_name) on success or (False, error_message).
    paper_width: '58mm' or '80mm'
    """
    char_width = 32 if paper_width == "58mm" else 48

    # ── Try python-escpos with real thermal formatting ────────
    try:
        from escpos.printer import Win32Raw
        import win32print

        default = win32print.GetDefaultPrinter()
        p = Win32Raw(default)
        p.open()

        shop_name  = settings.get("shop_name",    "FMCG Shop")
        shop_addr  = settings.get("shop_address",  "")
        shop_phone = settings.get("shop_phone",    "")
        shop_gst   = settings.get("shop_gst",      "")
        sep        = "-" * char_width
        eq_sep     = "=" * char_width
        is_wide    = char_width >= 48   # 80mm paper

        def ljr(left, right):
            left  = str(left)[:char_width - len(str(right)) - 1]
            return left + " " * (char_width - len(left) - len(str(right))) + str(right)

        # ── Shop Header — bold, double-size, centered ──
        p.set(align="center", bold=True, width=2, height=2)
        p.text(shop_name + "\n")

        p.set(align="center", bold=False, width=1, height=1)
        if shop_addr:
            p.text(shop_addr + "\n")
        if shop_phone:
            p.text(shop_phone + "\n")
        if shop_gst:
            p.text("GST: " + shop_gst + "\n")

        p.set(align="center", bold=True, width=1, height=1)
        p.text("--- TAX INVOICE ---\n")

        p.set(align="left", bold=False, width=1, height=1)
        p.text(eq_sep + "\n")

        # ── Bill info — bold bill number ──
        p.set(align="left", bold=True, width=1, height=1)
        p.text(ljr("Bill: " + bill["bill_number"],
                    str(bill.get("bill_date", ""))[:10]) + "\n")
        p.set(align="left", bold=False, width=1, height=1)
        p.text(ljr("Cust: " + bill.get("customer_name", "Walk-in")[:20],
                    bill.get("payment_mode", "Cash")) + "\n")
        p.text(sep + "\n")

        # ── Column header — bold, with numbering ──
        p.set(align="left", bold=True, width=1, height=1)
        if is_wide:
            hdr = f"{'#':>3} {'Item':<{char_width-28}} {'Qty':>4} {'Rate':>7} {'Disc':>5} {'Amt':>7}"
        else:
            hdr = f"{'#':>2} {'Item':<{char_width-21}} {'Qty':>3} {'Rate':>5} {'Amt':>7}"
        p.text(hdr + "\n")
        p.text(sep + "\n")

        # ── Items — normal, numbered ──
        p.set(align="left", bold=False, width=1, height=1)
        for idx, it in enumerate(items, 1):
            name = str(it.get("product_name", ""))
            qty  = f"{it.get('quantity', 0):.0f}"
            rate = f"{it.get('unit_price', 0):.0f}"
            disc = f"{it.get('discount', 0):.0f}"
            amt  = f"{it.get('line_total', 0):.2f}"

            if is_wide:
                max_name = char_width - 28
                name = name[:max_name]
                p.text(f"{idx:>3} {name:<{max_name}} {qty:>4} {rate:>7} {disc:>5} {amt:>7}\n")
            else:
                max_name = char_width - 21
                name = name[:max_name]
                p.text(f"{idx:>2} {name:<{max_name}} {qty:>3} {rate:>5} {amt:>7}\n")

        p.text(sep + "\n")

        # ── Totals ──
        p.set(align="left", bold=False, width=1, height=1)
        p.text(ljr("Subtotal:", f"Rs.{bill.get('subtotal', 0):>8.2f}") + "\n")
        if bill.get("discount", 0):
            p.text(ljr("Discount:", f" - {bill.get('discount', 0):>8.2f}") + "\n")

        # Grand total — bold + double height, sandwiched between double lines
        p.text(eq_sep + "\n")
        p.set(align="left", bold=True, width=1, height=2)
        p.text(ljr("GRAND TOTAL:", f"Rs.{bill.get('grand_total', 0):>8.2f}") + "\n")
        p.set(align="left", bold=False, width=1, height=1)
        p.text(eq_sep + "\n")

        p.text(ljr("Amount Paid:", f"Rs.{bill.get('amount_paid', 0):>8.2f}") + "\n")
        p.text(ljr("Change Due:",  f"Rs.{bill.get('change_due', 0):>8.2f}") + "\n")

        p.text(sep + "\n")

        # ── Footer — centered ──
        p.set(align="center", bold=True, width=1, height=1)
        p.text("Thank you! Come again\n")
        p.set(align="center", bold=False, width=1, height=1)
        p.text(datetime.now().strftime("%d %b %Y  %I:%M %p") + "\n")
        p.text("\n\n\n")   # paper feed

        p.cut()
        p.close()
        return True, default

    except ImportError:
        pass   # python-escpos not installed — fall through to plain-text
    except Exception as e:
        return False, str(e)

    # Plain-text fallback via Windows print spooler
    lines_txt = _build_receipt_lines(bill, items, settings, char_width)
    txt = "\n".join(lines_txt)
    try:
        import win32print, win32api
        default = win32print.GetDefaultPrinter()
        tmp = tempfile.NamedTemporaryFile(
            suffix=".txt", delete=False, mode="w",
            encoding="cp1252", errors="replace"
        )
        tmp.write(txt)
        tmp.close()
        win32api.ShellExecute(
            0, "print", tmp.name, f'/d:"{default}"', ".", 0
        )
        return True, default
    except Exception as e:
        return False, f"Plain-text fallback failed: {e}"

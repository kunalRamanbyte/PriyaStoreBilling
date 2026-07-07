"""
bill_printer.py — Bill printing module for FMCG Billing System
Handles:
  1. A4 PDF bill (via reportlab)
  2. 58mm / 80mm ESC/POS thermal receipt (via python-escpos or raw bytes)
  3. Plain-text fallback (notepad /p)
"""

import os
import sys
import time
import tempfile
import subprocess
from datetime import datetime

_TEMP_SUBDIR = "priyastore_prints"


def _temp_dir() -> str:
    d = os.path.join(tempfile.gettempdir(), _TEMP_SUBDIR)
    os.makedirs(d, exist_ok=True)
    return d


def _prune_temp(days: int = 7):
    """Delete previously generated print files older than `days` so bill PDFs
    (which contain customer data) don't accumulate forever in %TEMP%."""
    try:
        cutoff = time.time() - days * 86400
        d = os.path.join(tempfile.gettempdir(), _TEMP_SUBDIR)
        if not os.path.isdir(d):
            return
        for f in os.listdir(d):
            p = os.path.join(d, f)
            try:
                if os.path.isfile(p) and os.path.getmtime(p) < cutoff:
                    os.remove(p)
            except Exception:
                pass
    except Exception:
        pass


def _new_temp(suffix: str, text: bool = False):
    """NamedTemporaryFile in a dedicated, self-pruning app temp folder."""
    _prune_temp()
    kwargs = dict(suffix=suffix, delete=False, dir=_temp_dir())
    if text:
        kwargs.update(mode="w", encoding="utf-8", errors="replace")
    return tempfile.NamedTemporaryFile(**kwargs)


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
        tmp = _new_temp(".pdf")
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
        story.append(Paragraph(f"Ph: {shop_phone}", h3))
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
        Paragraph("<b>Rate Rs.</b>",       ParagraphStyle("th", fontSize=10, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT)),
        Paragraph("<b>Disc Rs.</b>",       ParagraphStyle("th", fontSize=10, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT)),
        Paragraph("<b>Total Rs.</b>",      ParagraphStyle("th", fontSize=10, fontName="Helvetica-Bold", textColor=WHITE, alignment=TA_RIGHT)),
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
        [Paragraph("Subtotal:", tot_lbl), Paragraph(f"Rs. {subtotal:,.2f}", tot_val)],
    ]
    if discount:
        totals_data.append(
            [Paragraph("Discount:", tot_lbl), Paragraph(f"- Rs. {discount:,.2f}", tot_val)]
        )
    if change_adj > 0:
        totals_data.append(
            [Paragraph("Change Used:", tot_lbl), Paragraph(f"- Rs. {change_adj:,.2f}", tot_val)]
        )
    if udhaar_adj > 0:
        totals_data.append(
            [Paragraph("Prev. Udhaar:", tot_lbl), Paragraph(f"+ Rs. {udhaar_adj:,.2f}", warn_val)]
        )
    totals_data.append(
        [Paragraph("<b>GRAND TOTAL:</b>", gt_lbl), Paragraph(f"<b>Rs. {total_collect:,.2f}</b>", gt_val)]
    )
    totals_data.append(
        [Paragraph("Amount Paid:", tot_lbl), Paragraph(f"Rs. {amount_paid:,.2f}", tot_val)]
    )
    if change_due > 0:
        totals_data.append(
            [Paragraph("Change Due:", tot_lbl), Paragraph(f"Rs. {change_due:,.2f}", tot_val)]
        )
    if balance_due > 0:
        totals_data.append(
            [Paragraph("<b>Balance Due:</b>", tot_lbl), Paragraph(f"<b>Rs. {balance_due:,.2f}</b>", warn_val)]
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
    story.append(Paragraph("Thank you for shopping with us!", foot))
    story.append(Paragraph(f"Printed: {datetime.now().strftime('%d %b %Y  %I:%M %p')}", foot))

    doc.build(story)
    return output_path


# ─────────────────────────────────────────────────────────────────────────────
# A4 PDF RETURN / REFUND NOTE
# ─────────────────────────────────────────────────────────────────────────────

def generate_return_pdf(return_doc: dict, items: list, settings: dict,
                        output_path: str = None) -> str:
    """
    Generate an A4 PDF return/refund note. Returns the path to the saved PDF.
    return_doc: dict with return_number, return_date, bill_number, customer_name,
                refund_mode, reason, total_amount.
    items: sales_return_items rows (product_name, unit, quantity, unit_price,
           line_total, restocked).
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                    Paragraph, Spacer, HRFlowable)
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

    if not output_path:
        tmp = _new_temp(".pdf")
        output_path = tmp.name
        tmp.close()

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=12*mm, bottomMargin=12*mm,
    )

    RED   = colors.HexColor("#C2410C")
    DRED  = colors.HexColor("#9A3412")
    GRAY  = colors.HexColor("#757575")
    LGRAY = colors.HexColor("#FFF7ED")
    WHITE = colors.white
    BLACK = colors.HexColor("#1A1A2E")

    h1 = ParagraphStyle("h1", fontSize=18, fontName="Helvetica-Bold",
                        textColor=DRED, alignment=TA_CENTER, spaceAfter=2)
    h2 = ParagraphStyle("h2", fontSize=10, fontName="Helvetica",
                        textColor=GRAY, alignment=TA_CENTER, spaceAfter=1)
    lbl = ParagraphStyle("lbl", fontSize=10, fontName="Helvetica-Bold",
                         textColor=BLACK, spaceAfter=2)

    shop_name  = settings.get("shop_name",    "Priya Store")
    shop_addr  = settings.get("shop_address", "")
    shop_city  = settings.get("shop_city",    "")
    shop_phone = settings.get("shop_phone",   "")

    story = []
    story.append(Paragraph(shop_name, h1))
    addr_line = ", ".join(filter(None, [shop_addr, shop_city]))
    if addr_line:
        story.append(Paragraph(addr_line, h2))
    if shop_phone:
        story.append(Paragraph(f"Phone: {shop_phone}", h2))
    title = ParagraphStyle("title", fontSize=12, fontName="Helvetica-Bold",
                           textColor=DRED, alignment=TA_CENTER, spaceAfter=4)
    story.append(Paragraph("RETURN / REFUND NOTE", title))
    story.append(HRFlowable(width="100%", thickness=1.5, color=RED, spaceAfter=6))

    rdate = str(return_doc.get("return_date", ""))[:16]
    info = [
        [Paragraph(f"<b>Return No:</b> {return_doc.get('return_number','')}", lbl),
         Paragraph(f"<b>Date:</b> {rdate}", lbl)],
        [Paragraph(f"<b>Against Bill:</b> {return_doc.get('bill_number','')}", lbl),
         Paragraph(f"<b>Refund:</b> {return_doc.get('refund_mode','Cash')}", lbl)],
        [Paragraph(f"<b>Customer:</b> {return_doc.get('customer_name') or 'Walk-in Customer'}", lbl),
         Paragraph(f"<b>Reason:</b> {return_doc.get('reason') or '-'}", lbl)],
    ]
    info_tbl = Table(info, colWidths=[90*mm, 90*mm])
    info_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), LGRAY),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 6*mm))

    def th(txt, al=TA_RIGHT):
        return Paragraph(f"<b>{txt}</b>", ParagraphStyle(
            "th", fontSize=10, fontName="Helvetica-Bold", textColor=WHITE, alignment=al))

    tbl_data = [[th("#", TA_CENTER), th("Product", TA_LEFT), th("Unit", TA_CENTER),
                 th("Qty"), th("Rate Rs."), th("Refund Rs."), th("Restock", TA_CENTER)]]
    r_style = ParagraphStyle("r",  fontSize=9, fontName="Helvetica", textColor=BLACK)
    r_num   = ParagraphStyle("rn", fontSize=9, fontName="Helvetica", textColor=BLACK, alignment=TA_RIGHT)
    r_ctr   = ParagraphStyle("rc", fontSize=9, fontName="Helvetica", textColor=BLACK, alignment=TA_CENTER)
    for idx, it in enumerate(items, 1):
        tbl_data.append([
            Paragraph(str(idx), r_ctr),
            Paragraph(str(it.get("product_name", "")), r_style),
            Paragraph(str(it.get("unit", "pc")), r_ctr),
            Paragraph(f"{it.get('quantity',0):.2f}", r_num),
            Paragraph(f"{it.get('unit_price',0):.2f}", r_num),
            Paragraph(f"{it.get('line_total',0):.2f}", r_num),
            Paragraph("Yes" if it.get("restocked", 1) else "No", r_ctr),
        ])
    col_w = [10*mm, 66*mm, 18*mm, 20*mm, 22*mm, 24*mm, 20*mm]
    item_tbl = Table(tbl_data, colWidths=col_w, repeatRows=1)
    item_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  RED),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LGRAY]),
        ("GRID",          (0,0), (-1,-1), 0.3, colors.HexColor("#FED7AA")),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(item_tbl)
    story.append(Spacer(1, 4*mm))

    total = float(return_doc.get("total_amount") or 0)
    gt_lbl = ParagraphStyle("gl", fontSize=13, fontName="Helvetica-Bold", textColor=DRED, alignment=TA_RIGHT)
    tot_tbl = Table([[Paragraph("<b>TOTAL REFUND:</b>", gt_lbl),
                      Paragraph(f"<b>Rs. {total:,.2f}</b>", gt_lbl)]],
                    colWidths=[130*mm, 46*mm])
    tot_tbl.setStyle(TableStyle([
        ("LINEABOVE",     (0,0), (-1,0), 1.2, RED),
        ("LINEBELOW",     (0,0), (-1,0), 1.2, RED),
        ("BACKGROUND",    (0,0), (-1,0), colors.HexColor("#FFEDD5")),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING",  (0,0), (-1,-1), 4),
    ]))
    story.append(tot_tbl)
    story.append(Spacer(1, 6*mm))
    foot = ParagraphStyle("foot", fontSize=9, fontName="Helvetica", textColor=GRAY, alignment=TA_CENTER)
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRAY))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("This is a return/refund acknowledgement.", foot))
    story.append(Paragraph(f"Printed: {datetime.now().strftime('%d %b %Y  %I:%M %p')}", foot))

    doc.build(story)
    return output_path


# ─────────────────────────────────────────────────────────────────────────────
# THERMAL ESC/POS RECEIPT
# ─────────────────────────────────────────────────────────────────────────────

# Receipt rows are (text, style) tuples. `text` is the RAW content — never
# pre-centered — so the ESC/POS path can centre it with hardware alignment
# (and apply double-width safely) while the plain-text fallback centres it with
# spaces. Styles: 'title', 'center', 'center_bold', 'left', 'left_bold'.

# Virtual / non-thermal printers cannot interpret raw ESC/POS bytes — sending a
# receipt to them produces a corrupt file (e.g. an unopenable .pdf). When one of
# these is the default printer we show a readable text preview instead.
_NON_THERMAL_PRINTERS = (
    "microsoft print to pdf", "microsoft xps document writer", "xps document",
    "onenote", "send to onenote", "fax", "pdfcreator", "cutepdf", "foxit",
    "adobe pdf", "print to pdf",
    # Common physical laser/inkjet families — these would spew ESC/POS control
    # codes as garbage pages, so route them to the readable text preview too.
    "laserjet", "officejet", "deskjet", "inkjet", "laser", "ecosys",
    "pixma", "workforce", "envy", "smart tank",
)


def _looks_non_thermal(name: str) -> bool:
    """True if the printer name looks like a virtual / non-ESC/POS printer."""
    n = (name or "").lower()
    return any(k in n for k in _NON_THERMAL_PRINTERS)


def _thermal_text_preview(rows: list, width: int, default_name: str) -> tuple:
    """Save the receipt as a .txt and open it. Used when the default printer is
    virtual (Print-to-PDF etc.), so the user still sees the exact receipt instead
    of an unopenable file. Returns (True, message)."""
    txt = "\n".join(_render_plain_lines(rows, width))
    tmp = _new_temp(".txt", text=True)
    tmp.write(txt)
    tmp.close()
    open_file(tmp.name)
    return True, (f"No thermal printer connected (default is '{default_name}'). "
                  f"Opened a text preview instead:\n{tmp.name}")


def _render_plain_lines(rows: list, width: int) -> list:
    """Render (text, style) rows to plain-text lines for a dumb spooler/notepad.
    Centered styles are padded with spaces; left styles are emitted as-is."""
    out = []
    for text, style in rows:
        if style in ("title", "center", "center_bold"):
            out.append(str(text)[:width].center(width))
        else:
            out.append(str(text))
    return out


def _render_escpos(p, rows: list):
    """Apply ESC/POS styling per row to a python-escpos printer (or Dummy buffer)."""
    for text, style in rows:
        if style == "title":
            p.set(align="center", bold=True,  width=2, height=2)
        elif style == "center":
            p.set(align="center", bold=False, width=1, height=1)
        elif style == "center_bold":
            p.set(align="center", bold=True,  width=1, height=1)
        elif style == "left_bold":
            p.set(align="left",   bold=True,  width=1, height=1)
        else:  # 'left'
            p.set(align="left",   bold=False, width=1, height=1)
        p.text(str(text) + "\n")
    p.set(align="left", bold=False, width=1, height=1)


def _build_receipt_rows(bill: dict, items: list, settings: dict,
                        width: int = 48) -> list:
    """Single source of truth for the receipt layout. Returns (text, style)
    rows consumed by both the ESC/POS path and the plain-text fallback."""
    shop_name  = settings.get("shop_name",    "Priya Store")
    shop_addr  = settings.get("shop_address", "")
    shop_city  = settings.get("shop_city",    "")
    shop_phone = settings.get("shop_phone",   "")
    shop_gst   = settings.get("shop_gst",     "")
    cashier    = settings.get("cashier",      "")

    def ljr(left, right):
        l, r = str(left), str(right)
        l = l[:max(0, width - len(r) - 1)]
        return l + " " * max(1, width - len(l) - len(r)) + r

    sep     = "-" * width
    dsep    = "=" * width
    is_wide = width >= 48
    rows = []

    # ── Shop header ──
    rows.append((shop_name.upper(), "title"))
    addr = ", ".join(filter(None, [shop_addr, shop_city]))
    if addr:
        rows.append((addr, "center"))
    if shop_phone:
        rows.append((f"Contact: {shop_phone}", "center"))
    if shop_gst:
        rows.append((f"GST: {shop_gst}", "center"))
    rows.append((sep, "left"))

    # ── Customer info block ──
    cust = bill.get("customer_name", "Walk-in Customer")
    cust_phone = bill.get("customer_phone", "")
    cust_addr  = bill.get("customer_address", "")
    if is_wide:
        if cust_phone:
            rows.append((f"Name: {cust}  (M: {cust_phone})", "left"))
        else:
            rows.append((f"Name: {cust}", "left"))
        if cust_addr:
            rows.append((f"Adr: {cust_addr}", "left"))
    else:
        rows.append((f"Name: {cust}", "left"))
        if cust_phone:
            rows.append((f"Phone: {cust_phone}", "left"))
        if cust_addr:
            rows.append((f"Adr: {cust_addr}", "left"))
    rows.append((sep, "left"))

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

    if is_wide:
        rows.append((ljr(f"Bill No: {bill['bill_number']}", f"Date: {date_disp}"), "left"))
        rows.append((ljr(f"Cashier: {cashier}", payment_line), "left"))
    else:
        rows.append((f"Bill No: {bill['bill_number']}", "left"))
        rows.append((f"Date: {date_disp}", "left"))
        rows.append((payment_line, "left"))
        rows.append((f"Cashier: {cashier}", "left"))
    rows.append((sep, "left"))

    # ── Column header ──
    if is_wide:
        nm = width - 24
        rows.append((f"{'Item':<{nm}}  {'Qty.':<5}{'Price':>8} {'Amount':>8}", "left_bold"))
    else:
        nm = 9
        rows.append((f"{'Item':<{nm}} {'Qty':>4} {'Price':>8} {'Amount':>8}", "left_bold"))
    rows.append((sep, "left"))

    # ── Items ──
    total_qty = 0.0
    for it in items:
        name = str(it.get("product_name", ""))[:width]
        qty  = float(it.get("quantity", 0))
        rate = float(it.get("unit_price", 0))
        amt  = float(it.get("line_total", 0))
        total_qty += qty
        qty_str = f"{qty:g}"
        if is_wide:
            if len(name) > nm:
                rows.append((name, "left"))
                rows.append((f"{'':<{nm}}  {qty_str:<5}{rate:>8.2f} {amt:>8.2f}", "left"))
            else:
                rows.append((f"{name:<{nm}}  {qty_str:<5}{rate:>8.2f} {amt:>8.2f}", "left"))
        else:
            if len(name) > nm:
                rows.append((name, "left"))
                rows.append((f"{'':<10}{qty_str:>4} {rate:>8.2f} {amt:>8.2f}", "left"))
            else:
                rows.append((f"{name:<{nm}} {qty_str:>4} {rate:>8.2f} {amt:>8.2f}", "left"))
    rows.append((sep, "left"))
    rows.append((ljr("Total Quantity:", f"{total_qty:g}"), "left"))

    # ── Totals ──
    subtotal = float(bill.get("subtotal", 0))
    discount = float(bill.get("discount", 0))
    udhaar   = float(bill.get("udhaar_adjustment") or 0)
    change_adj = float(bill.get("change_adjustment") or 0)
    grand    = float(bill.get("grand_total", 0))
    paid     = float(bill.get("amount_paid", 0))
    change   = float(bill.get("change_due", 0))
    total_collect = round(grand + udhaar - change_adj, 2)

    rows.append((ljr("Sub Total:", f"Rs.{subtotal:.2f}"), "left"))
    if discount:
        rows.append((ljr("Discount:", f"-Rs.{discount:.2f}"), "left"))
    if change_adj > 0:
        rows.append((ljr("Change Used:", f"-Rs.{change_adj:.2f}"), "left"))
    if udhaar > 0:
        rows.append((ljr("Prev. Udhaar:", f"+Rs.{udhaar:.2f}"), "left"))
    rows.append((dsep, "left"))
    rows.append((ljr("Grand Total:", f"Rs.{total_collect:.2f}"), "left_bold"))
    rows.append((dsep, "left"))

    # Payment info
    rows.append((ljr("Amount Paid:", f"Rs.{paid:.2f}"), "left"))
    balance_due = max(0, round(total_collect - paid, 2))
    if change > 0:
        rows.append((ljr("Change Due:", f"Rs.{change:.2f}"), "left"))
    if balance_due > 0:
        rows.append((ljr("Balance Due:", f"Rs.{balance_due:.2f}"), "left_bold"))

    # Show udhaar credit status if bill is credit mode
    if bill.get("payment_mode") == "Credit (Udhaar)":
        rows.append(("** CREDIT SALE (UDHAAR) **", "center_bold"))

    rows.append((sep, "left"))

    # ── Footer ──
    rows.append(("Thanks & Visit Again", "center_bold"))
    rows.append(("", "left"))
    rows.append(("", "left"))

    return rows


def _build_receipt_lines(bill: dict, items: list, settings: dict,
                          width: int = 48) -> list:
    """Plain-text receipt lines (spooler/notepad fallback). Thin wrapper over the
    canonical layout in `_build_receipt_rows` so both paths stay in lockstep."""
    return _render_plain_lines(_build_receipt_rows(bill, items, settings, width), width)


def print_thermal(bill: dict, items: list, settings: dict,
                  paper_width: str = "80mm") -> tuple:
    """
    Print a properly formatted ESC/POS thermal receipt.
    Uses bold, double-height, and alignment commands for a professional look.
    Returns (True, printer_name) on success or (False, error_message).
    paper_width: '58mm' or '80mm'

    The layout comes from `_build_receipt_rows` (the same rows the tested
    plain-text path uses). The ESC/POS bytes are rendered into an in-memory
    buffer and written to the spooler in a SINGLE atomic call, so a failure
    can never leave a half-printed slip, and any runtime error falls through
    to the plain-text fallback below.
    """
    char_width = 32 if str(paper_width).strip().lower() == "58mm" else 48
    rows = _build_receipt_rows(bill, items, settings, char_width)

    # ── Guard: a virtual default printer can't render ESC/POS — preview instead ──
    try:
        import win32print
        _default_name = win32print.GetDefaultPrinter()
    except Exception:
        _default_name = ""
    if _default_name and _looks_non_thermal(_default_name):
        return _thermal_text_preview(rows, char_width, _default_name)

    # ── Try python-escpos: render to a buffer, then one atomic RAW write ──
    wrote = False   # set once bytes are on the wire, to avoid a double-print
    try:
        from escpos.printer import Dummy
        import win32print

        buf = Dummy()
        _render_escpos(buf, rows)
        buf.cut()
        data = buf.output

        default = win32print.GetDefaultPrinter()
        hPrinter = win32print.OpenPrinter(default)
        try:
            win32print.StartDocPrinter(hPrinter, 1, (f"Bill_{bill['bill_number']}", None, "RAW"))
            try:
                win32print.StartPagePrinter(hPrinter)
                win32print.WritePrinter(hPrinter, data)
                wrote = True   # job spooled; a later cleanup error must NOT re-print
                win32print.EndPagePrinter(hPrinter)
            finally:
                win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)
        return True, default

    except ImportError:
        pass   # python-escpos / pywin32 not installed — fall through
    except Exception as escpos_err:
        # If the receipt bytes already reached the printer, a post-write cleanup
        # failure must not trigger the fallback (that would print a 2nd copy).
        if wrote:
            return True, _default_name or "printer"
        try:
            print(f"[bill_printer] ESC/POS path failed, using plain-text fallback: {escpos_err}")
        except Exception:
            pass

    # Plain-text fallback via Windows print spooler (RAW mode)
    txt = "\n".join(_render_plain_lines(rows, char_width))
    try:
        import win32print
        default = win32print.GetDefaultPrinter()
        hPrinter = win32print.OpenPrinter(default)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, (f"Bill_{bill['bill_number']}", None, "RAW"))
            try:
                win32print.StartPagePrinter(hPrinter)
                # ESC/POS printers interpret a single-byte codepage (CP437), not
                # UTF-8. Encoding as cp437 degrades unsupported glyphs to '?'
                # one-for-one so column alignment is preserved (UTF-8 would emit
                # multi-byte mojibake and shift every following column).
                raw_bytes = (txt + "\n\n\n\n\x1dV\x42\x00").encode("cp437", errors="replace")
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
            tmp = _new_temp(".txt", text=True)
            tmp.write(txt)
            tmp.close()
            win32api.ShellExecute(
                0, "print", tmp.name, f'/d:"{default}"', ".", 0
            )
            return True, default
        except Exception as e:
            return False, f"Raw print failed: {raw_err}. Notepad fallback failed: {e}"


# ─────────────────────────────────────────────────────────────────────────────
# THERMAL ESC/POS RETURN / REFUND RECEIPT
# ─────────────────────────────────────────────────────────────────────────────

def _build_return_rows(return_doc: dict, items: list, settings: dict,
                       width: int = 48) -> list:
    """Single source of truth for the return/refund receipt layout. Returns
    (text, style) rows consumed by both the ESC/POS path and the fallback."""
    shop_name  = settings.get("shop_name",    "Priya Store")
    shop_addr  = settings.get("shop_address", "")
    shop_city  = settings.get("shop_city",    "")
    shop_phone = settings.get("shop_phone",   "")
    cashier    = settings.get("cashier",      "")

    def ljr(left, right):
        l, r = str(left), str(right)
        l = l[:max(0, width - len(r) - 1)]
        return l + " " * max(1, width - len(l) - len(r)) + r

    sep, dsep = "-" * width, "=" * width
    is_wide   = width >= 48
    rows = []

    rows.append((shop_name.upper(), "title"))
    addr = ", ".join(filter(None, [shop_addr, shop_city]))
    if addr:
        rows.append((addr, "center"))
    if shop_phone:
        rows.append((f"Contact: {shop_phone}", "center"))
    rows.append(("*** RETURN / REFUND ***", "center_bold"))
    rows.append((sep, "left"))

    cust = return_doc.get("customer_name") or "Walk-in Customer"
    rows.append((f"Name: {cust}", "left"))

    raw_dt = str(return_doc.get("return_date", ""))
    date_disp = raw_dt[:10] if len(raw_dt) >= 10 else ""
    time_disp = raw_dt[11:16] if len(raw_dt) >= 16 else ""
    try:
        _dt = datetime.strptime(raw_dt[:19], "%Y-%m-%d %H:%M:%S")
        date_disp = _dt.strftime("%d/%m/%y")
        time_disp = _dt.strftime("%H:%M")
    except Exception:
        pass

    if is_wide:
        rows.append((ljr(f"Return: {return_doc.get('return_number','')}", f"Date: {date_disp}"), "left"))
        rows.append((ljr(f"Bill: {return_doc.get('bill_number','')}", time_disp), "left"))
    else:
        rows.append((f"Return: {return_doc.get('return_number','')}", "left"))
        rows.append((f"Bill: {return_doc.get('bill_number','')}", "left"))
        rows.append((f"Date: {date_disp} {time_disp}", "left"))
    if cashier:
        rows.append((f"Cashier: {cashier}", "left"))
    rows.append((sep, "left"))

    if is_wide:
        nm = width - 24
        rows.append((f"{'Item':<{nm}}  {'Qty':<5}{'Rate':>8} {'Refund':>8}", "left_bold"))
    else:
        nm = 9
        rows.append((f"{'Item':<{nm}} {'Qty':>4} {'Rate':>8} {'Refund':>8}", "left_bold"))
    rows.append((sep, "left"))

    any_damaged = False
    for it in items:
        name = str(it.get("product_name", ""))
        qty  = float(it.get("quantity", 0))
        rate = float(it.get("unit_price", 0))
        amt  = float(it.get("line_total", 0))
        if not it.get("restocked", 1):
            any_damaged = True
            name = "*" + name
        name = name[:width]
        qty_str = f"{qty:g}"
        if is_wide:
            if len(name) > nm:
                rows.append((name, "left"))
                rows.append((f"{'':<{nm}}  {qty_str:<5}{rate:>8.2f} {amt:>8.2f}", "left"))
            else:
                rows.append((f"{name:<{nm}}  {qty_str:<5}{rate:>8.2f} {amt:>8.2f}", "left"))
        else:
            if len(name) > nm:
                rows.append((name, "left"))
                rows.append((f"{'':<10}{qty_str:>4} {rate:>8.2f} {amt:>8.2f}", "left"))
            else:
                rows.append((f"{name:<{nm}} {qty_str:>4} {rate:>8.2f} {amt:>8.2f}", "left"))
    rows.append((sep, "left"))

    total = float(return_doc.get("total_amount") or 0)
    rows.append((dsep, "left"))
    rows.append((ljr("TOTAL REFUND:", f"Rs.{total:.2f}"), "left_bold"))
    rows.append((dsep, "left"))
    rows.append((ljr("Refund Mode:", return_doc.get("refund_mode", "Cash")), "left"))
    if return_doc.get("reason"):
        rows.append((f"Reason: {return_doc.get('reason')}", "left"))
    if any_damaged:
        rows.append(("* = not restocked (damaged)", "left"))
    rows.append((sep, "left"))
    rows.append(("Return Acknowledgement", "center_bold"))
    rows.append(("", "left"))
    rows.append(("", "left"))
    return rows


def _build_return_lines(return_doc: dict, items: list, settings: dict,
                        width: int = 48) -> list:
    """Plain-text return receipt lines (spooler/notepad fallback). Thin wrapper
    over `_build_return_rows` so both paths stay in lockstep."""
    return _render_plain_lines(_build_return_rows(return_doc, items, settings, width), width)


def print_thermal_return(return_doc: dict, items: list, settings: dict,
                         paper_width: str = "80mm") -> tuple:
    """Print an ESC/POS thermal return/refund receipt, with a spooler/notepad
    fallback. The layout comes from `_build_return_rows`; the ESC/POS bytes are
    rendered to a buffer and written in a SINGLE atomic call, so a failure can
    never half-print, and any runtime error falls through to the fallback.
    Returns (True, printer_name) or (False, error)."""
    char_width = 32 if str(paper_width).strip().lower() == "58mm" else 48
    rows = _build_return_rows(return_doc, items, settings, char_width)

    # ── Guard: a virtual default printer can't render ESC/POS — preview instead ──
    try:
        import win32print
        _default_name = win32print.GetDefaultPrinter()
    except Exception:
        _default_name = ""
    if _default_name and _looks_non_thermal(_default_name):
        return _thermal_text_preview(rows, char_width, _default_name)

    wrote = False   # set once bytes are on the wire, to avoid a double-print
    try:
        from escpos.printer import Dummy
        import win32print

        buf = Dummy()
        _render_escpos(buf, rows)
        buf.cut()
        data = buf.output

        default = win32print.GetDefaultPrinter()
        hPrinter = win32print.OpenPrinter(default)
        try:
            win32print.StartDocPrinter(
                hPrinter, 1, (f"Return_{return_doc.get('return_number','')}", None, "RAW"))
            try:
                win32print.StartPagePrinter(hPrinter)
                win32print.WritePrinter(hPrinter, data)
                wrote = True   # job spooled; a later cleanup error must NOT re-print
                win32print.EndPagePrinter(hPrinter)
            finally:
                win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)
        return True, default

    except ImportError:
        pass
    except Exception as escpos_err:
        if wrote:
            return True, _default_name or "printer"
        try:
            print(f"[bill_printer] ESC/POS return path failed, using fallback: {escpos_err}")
        except Exception:
            pass

    # Plain-text fallback via Windows spooler (RAW), then notepad
    txt = "\n".join(_render_plain_lines(rows, char_width))
    try:
        import win32print
        default = win32print.GetDefaultPrinter()
        hPrinter = win32print.OpenPrinter(default)
        try:
            hJob = win32print.StartDocPrinter(
                hPrinter, 1, (f"Return_{return_doc.get('return_number','')}", None, "RAW"))
            try:
                win32print.StartPagePrinter(hPrinter)
                # cp437 (single-byte ESC/POS codepage), not UTF-8 — see print_thermal.
                raw_bytes = (txt + "\n\n\n\n\x1dV\x42\x00").encode("cp437", errors="replace")
                win32print.WritePrinter(hPrinter, raw_bytes)
                win32print.EndPagePrinter(hPrinter)
            finally:
                win32print.EndDocPrinter(hPrinter)
        finally:
            win32print.ClosePrinter(hPrinter)
        return True, default
    except Exception as raw_err:
        try:
            import win32api, win32print
            default = win32print.GetDefaultPrinter()
            tmp = tempfile.NamedTemporaryFile(
                suffix=".txt", delete=False, mode="w",
                encoding="utf-8", errors="replace")
            tmp.write(txt)
            tmp.close()
            win32api.ShellExecute(0, "print", tmp.name, f'/d:"{default}"', ".", 0)
            return True, default
        except Exception as e:
            return False, f"Raw print failed: {raw_err}. Notepad fallback failed: {e}"


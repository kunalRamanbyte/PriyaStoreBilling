from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
IMG_DIR = ROOT / "output" / "userguide" / "screenshots"
OUT_DIR = ROOT / "output" / "userguide"
OUT_PDF = OUT_DIR / "Priya_Store_User_Guide.pdf"


SECTIONS = [
    {
        "title": "Login",
        "image": "login.png",
        "notes": [
            "Enter the username and password.",
            "Default admin access is shown on the login screen.",
            "Press Sign In to open the main application.",
        ],
    },
    {
        "title": "Dashboard",
        "image": "dashboard.png",
        "notes": [
            "Use this screen to review sales, bills, low stock, expiring items, and recent bills.",
            "Quick Action buttons open the main workflow screens.",
            "The sidebar is always available for navigation.",
        ],
    },
    {
        "title": "New Bill",
        "image": "new_bill.png",
        "notes": [
            "Search or scan products and add them to the cart.",
            "Review totals, discounts, payment mode, and cash received.",
            "Use F10 to print and save, F8 to hold a bill, and Esc to clear the cart.",
        ],
    },
    {
        "title": "Bill History",
        "image": "bill_history.png",
        "notes": [
            "Filter bills by date or search by bill number/customer.",
            "Open a bill to view details, reprint, resume a draft, or void it when permitted.",
        ],
    },
    {
        "title": "Products and Categories",
        "image": "products.png",
        "notes": [
            "Add and maintain product master data.",
            "Use categories to keep products organized for billing and reporting.",
            "Search, edit, deactivate, or delete records from the action buttons.",
        ],
    },
    {
        "title": "Inventory",
        "image": "inventory.png",
        "notes": [
            "Track stock levels and enter adjustments when physical stock changes.",
            "Review adjustment history from the history view.",
        ],
    },
    {
        "title": "Suppliers and Purchase",
        "image": "suppliers.png",
        "notes": [
            "Maintain supplier details and record payments.",
            "Use Purchase/GRN to receive goods and update stock through purchase entries.",
        ],
    },
    {
        "title": "Customers",
        "image": "customers.png",
        "notes": [
            "Add customers, record payments, and review ledger activity.",
            "Customer balances are visible for credit-tracking workflows.",
        ],
    },
    {
        "title": "Reports",
        "image": "reports.png",
        "notes": [
            "Generate sales, stock, purchase, and other operational reports.",
            "Export the selected report as Excel, CSV, or PDF when needed.",
        ],
    },
    {
        "title": "Settings, Users, Activity Log",
        "image": "settings.png",
        "notes": [
            "Settings controls application preferences and backup options.",
            "Users manages operator accounts and roles.",
            "Activity Log records major actions such as login, billing, stock changes, and logouts.",
        ],
    },
]


def bullet_paragraphs(items):
    return [Paragraph(f"- {text}", BODY) for text in items]


def section_story(section):
    items = []
    img_path = IMG_DIR / section["image"]
    items.append(Paragraph(section["title"], SECTION_TITLE))
    items.append(Spacer(1, 0.12 * inch))

    if img_path.exists():
        img = Image(str(img_path))
        max_w = 9.95 * inch
        max_h = 5.2 * inch
        scale = min(max_w / img.imageWidth, max_h / img.imageHeight)
        img.drawWidth = img.imageWidth * scale
        img.drawHeight = img.imageHeight * scale
        items.append(img)
    else:
        items.append(Paragraph(f"Missing screenshot: {img_path.name}", BODY))

    items.append(Spacer(1, 0.14 * inch))
    items.extend(bullet_paragraphs(section["notes"]))
    return items


def cover_story():
    box = Table(
        [[
            Paragraph("Priya Store User Guide", COVER_TITLE),
        ]],
        colWidths=[10.5 * inch],
    )
    box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#0F172A")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 28),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 28),
                ("LEFTPADDING", (0, 0), (-1, -1), 18),
                ("RIGHTPADDING", (0, 0), (-1, -1), 18),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#2563EB")),
                ("ROUNDEDCORNERS", [16, 16, 16, 16]),
            ]
        )
    )
    intro = Paragraph(
        "A screenshot-based walkthrough of the main workflows in the billing application.",
        INTRO,
    )
    meta = Table(
        [
            ["Scope", "Login, billing, master data, inventory, suppliers, customers, reports, settings"],
            ["Audience", "Store operators and admins"],
            ["Version", "Generated from the current workspace build"],
        ],
        colWidths=[1.6 * inch, 8.9 * inch],
    )
    meta.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#111827")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("LEADING", (0, 0), (-1, -1), 12),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return [
        Spacer(1, 0.7 * inch),
        box,
        Spacer(1, 0.35 * inch),
        intro,
        Spacer(1, 0.2 * inch),
        meta,
        Spacer(1, 0.25 * inch),
        Paragraph(
            "The guide uses real screenshots captured from the application and follows the normal left-sidebar workflow.",
            BODY,
        ),
    ]


def build_pdf():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=landscape(A4),
        leftMargin=0.45 * inch,
        rightMargin=0.45 * inch,
        topMargin=0.4 * inch,
        bottomMargin=0.4 * inch,
        title="Priya Store User Guide",
        author="Codex",
    )
    story = cover_story()
    story.append(PageBreak())
    for i, section in enumerate(SECTIONS):
        story.extend(section_story(section))
        if i != len(SECTIONS) - 1:
            story.append(PageBreak())
    doc.build(story, onFirstPage=decorate_page, onLaterPages=decorate_page)


def decorate_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#0F172A"))
    canvas.rect(0, A4[1] - 30, A4[0], 30, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(24, A4[1] - 20, "Priya Store User Guide")
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(A4[0] - 24, 12, f"Page {doc.page}")
    canvas.restoreState()


styles = getSampleStyleSheet()
COVER_TITLE = ParagraphStyle(
    "CoverTitle",
    parent=styles["Title"],
    fontName="Helvetica-Bold",
    fontSize=30,
    leading=34,
    alignment=TA_CENTER,
    textColor=colors.white,
)
INTRO = ParagraphStyle(
    "Intro",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=13,
    leading=17,
    alignment=TA_CENTER,
    textColor=colors.HexColor("#0F172A"),
)
SECTION_TITLE = ParagraphStyle(
    "SectionTitle",
    parent=styles["Heading1"],
    fontName="Helvetica-Bold",
    fontSize=20,
    leading=24,
    alignment=TA_LEFT,
    textColor=colors.HexColor("#0F172A"),
)
BODY = ParagraphStyle(
    "Body",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=11,
    leading=14,
    alignment=TA_LEFT,
    textColor=colors.HexColor("#111827"),
)


if __name__ == "__main__":
    build_pdf()
    print(OUT_PDF)

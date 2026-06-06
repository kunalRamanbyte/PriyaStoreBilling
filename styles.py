"""
styles.py — Centralised ttk.Style configuration
Call setup_ttk_styles() ONCE at app startup (before any screen is built).
Fixes the problem of 15 separate Style() instantiations across screens.

Apple-standard design system:
  · Near-black table headers  (#1D1D1F)
  · 48px row height for 60+ readability
  · Soft blue selection
  · Clean white backgrounds with subtle zebra rows
"""

from tkinter import ttk
from config import COLORS, FONTS


def setup_ttk_styles(mode="light"):
    """Register every Treeview and Scrollbar style used across the app."""
    s = ttk.Style()
    s.theme_use("clam")   # clam allows the most colour overrides

    # ── Shared heading style (all tables) ────────────────────
    _heading = dict(
        font=FONTS["table_hdr"],
        background=COLORS["tbl_header_bg"],
        foreground=COLORS["tbl_header_fg"],
        relief="flat",
        padding=(10, 0),
    )

    # ── Shared row style ─────────────────────────────────────
    _row = dict(
        font=FONTS["table"],
        rowheight=48,                  # 60+ friendly row height
        background=COLORS["bg_white"],
        foreground=COLORS["text_dark"],
        fieldbackground=COLORS["bg_white"],
        borderwidth=0,
        relief="flat",
    )

    _select = dict(
        background=[("selected", COLORS["tbl_select"])],
        foreground=[("selected", COLORS["text_dark"])],
    )

    # ── Register every named style used in the app ────────────
    STYLE_NAMES = [
        "Dash",        # Dashboard recent bills
        "Bill",        # Bill History
        "Prod",        # Products
        "Inv",         # Inventory
        "Sup",         # Suppliers
        "Cust",        # Customers
        "Rpt",         # Reports
        "Purch",       # Purchase/GRN
        "User",        # Users
        "Log",         # Activity Log
        "Cat",         # Categories
        "Exp",         # Expiry alert panel (dashboard)
        "Cart",        # POS Cart
        "Led",         # Customer Ledger
    ]

    for name in STYLE_NAMES:
        tv  = f"{name}.Treeview"
        hdr = f"{name}.Treeview.Heading"

        s.configure(tv, **_row)
        s.configure(hdr, **_heading)
        s.map(tv, **_select)

        # Scrollbar — thin, modern, macOS-style
        sb = f"{name}.Vertical.TScrollbar"
        s.configure(sb,
            background=COLORS["glass_border"],
            troughcolor=COLORS["bg_main"],
            arrowcolor=COLORS["text_muted"],
            borderwidth=0, relief="flat",
        )

    # ── Expiry panel uses a warm header ──────────────────────
    exp_bg = "#FFF9F0" if mode.lower() == "light" else "#2D1E10"
    s.configure("Exp.Treeview",
        background=exp_bg,
        fieldbackground=exp_bg,
        font=FONTS["table"],
        rowheight=44,
    )

    s.configure("Exp.Treeview.Heading",
        font=FONTS["table_hdr"],
        background=COLORS["btn_warning"],
        foreground="#FFFFFF",
        relief="flat",
    )

    # ── Cart table gets a vibrant violet header ──────────────
    s.configure("Cart.Treeview.Heading",
        font=FONTS["table_hdr"],
        background="#4C1D95",
        foreground="#FFFFFF",
        relief="flat",
        padding=(10, 0),
    )

    # ── Global Scrollbar (horizontal + vertical fallback) ─────
    s.configure("TScrollbar",
        background=COLORS["glass_border"],
        troughcolor=COLORS["bg_main"],
        arrowcolor=COLORS["text_muted"],
        borderwidth=0, relief="flat",
    )

    # ── Combobox / OptionMenu base ────────────────────────────
    s.configure("TCombobox",
        fieldbackground=COLORS["bg_input"],
        background=COLORS["bg_input"],
        foreground=COLORS["text_dark"],
        arrowcolor=COLORS["btn_primary"],
        bordercolor=COLORS["border"],
        relief="flat",
    )

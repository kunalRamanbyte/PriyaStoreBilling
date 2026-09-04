"""
styles.py — Centralised ttk.Style configuration
Call setup_ttk_styles() ONCE at app startup (before any screen is built).
Fixes the problem of 15 separate Style() instantiations across screens.

Direction B table system:
  · Quiet uppercase 13px column headers on the card surface — the old
    near-black header band is gone, so the card reads as one surface
  · 56px rows (62 on Bill History, 60 in the POS cart, 58 on Reports)
  · Pale blue selection (#EAF1FF) with dark ink, never a dark fill
  · Hairline borders and solid fills only — no gradient, no shadow
"""

from tkinter import ttk
from config import COLORS, FONTS, METRICS


# ── Every named style used in the app ────────────────────────
# Every name a screen passes as style="X.Treeview" MUST appear here.
# ttk resolves an unregistered name to the base Treeview style without
# raising, so a missing entry silently loses the row height and the
# Direction B header — it looks wrong rather than failing loudly.
# verify_screens.py walks the built screens and fails on any tree whose
# style is not listed.
STYLE_NAMES = [
    "Dash",        # Dashboard recent bills
    "Bill",        # Bill History
    "Prod",        # Products
    "Inv",         # Inventory
    "Adj",         # Inventory — stock adjustment history
    "Sup",         # Suppliers
    "Cust",        # Customers
    "Rpt",         # Reports
    "Purch",       # Purchase/GRN
    "Pur",         # Purchase/GRN — GRN cart
    "GRN",         # Purchase/GRN — GRN history
    "User",        # Users
    "Log",         # Activity Log
    "Cat",         # Categories
    "Exp",         # Expiry alert panel (dashboard)
    "Cart",        # POS Cart
    "Led",         # Customer Ledger
]

# Row heights the design pins down per table. Anything not listed uses
# METRICS["row"].
ROW_HEIGHTS = {
    "Bill": METRICS["row_lg"],   # 62 — Bill History carries an avatar
    "Cart": 60,                  # POS cart rows hold a stepper control
    "Rpt" : 58,                  # Reports rows carry a share-of-period bar
    "Exp" : 44,                  # Compact dashboard side panel
}


def setup_ttk_styles(mode="light"):
    """Register every Treeview and Scrollbar style used across the app.

    `mode` is accepted for call-site compatibility; every colour now comes
    from COLORS, which config.apply_theme_mode() has already swapped to the
    right theme by the time this runs.
    """
    s = ttk.Style()
    s.theme_use("clam")   # clam allows the most colour overrides

    # Scrollbars resolve to the bare TScrollbar name unless a screen passes
    # style=, and most do not — so the shared look has to live on the base.
    _scroll = dict(
        background=COLORS["hairline"],
        troughcolor=COLORS["bg_card"],
        bordercolor=COLORS["bg_card"],
        lightcolor=COLORS["hairline"],
        darkcolor=COLORS["hairline"],
        arrowcolor=COLORS["text_muted"],
        arrowsize=12,
        borderwidth=0, relief="flat",
    )

    # ── Shared heading style (all tables) ────────────────────
    # Direction B: the header is part of the card, not a band across it.
    _heading = dict(
        font=FONTS["table_hdr"],
        background=COLORS["tbl_header_bg"],
        foreground=COLORS["tbl_header_fg"],
        relief="flat",
        borderwidth=0,
        padding=(12, 6),
    )

    # ── Shared row style ─────────────────────────────────────
    _row = dict(
        font=FONTS["table"],
        rowheight=METRICS["row"],
        background=COLORS["bg_white"],
        foreground=COLORS["text_dark"],
        fieldbackground=COLORS["bg_white"],
        borderwidth=0,
        relief="flat",
    )

    # Selection must be unmistakable: Bill History's Void button acts on it.
    # The old pairing was tbl_select on bg_white -- 1.13:1 against an
    # unselected row, with no foreground change. A solid accent fill with
    # white ink is the only state a shopkeeper can be sure of before
    # destroying a bill.
    _select = dict(
        background=[("selected", COLORS["accent_action"])],
        foreground=[("selected", COLORS["on_accent"])],
    )

    # A header must not flash a raised 3-D box when hovered or clicked;
    # clam does that by default and it breaks the flat surface.
    _heading_map = dict(
        background=[("active", COLORS["tbl_header_bg"])],
        relief=[("active", "flat"), ("pressed", "flat")],
    )

    # ── Register every named style used in the app (see STYLE_NAMES above) ──
    for name in STYLE_NAMES:
        tv  = f"{name}.Treeview"
        hdr = f"{name}.Treeview.Heading"

        s.configure(tv, **{**_row, "rowheight": ROW_HEIGHTS.get(name, METRICS["row"])})
        # clam draws a raised 3-D rectangle inside the card that holds the
        # table; flatten it so the rounded card is the only frame.
        s.layout(tv, [(f"{name}.Treeview.treearea", {"sticky": "nswe"})])
        s.configure(hdr, **_heading)
        s.map(tv, **_select)
        s.map(hdr, **_heading_map)

        # Scrollbar — thin, hairline, no arrows competing for attention.
        # Both orientations: there was no horizontal style at all, so every
        # horizontal bar in the app fell back to clam's grey 3-D default.
        for orient in ("Vertical", "Horizontal"):
            sb = f"{name}.{orient}.TScrollbar"
            s.configure(sb, **_scroll)
            s.map(sb, background=[("active", COLORS["text_muted"])])

    # ── Expiry panel — the one deliberate header override ────
    # Expiry owns amber in Direction B, so the panel sits on the amber
    # tint and takes the dark amber ink (never white on amber, which
    # cannot reach 4.5:1).
    s.configure("Exp.Treeview",
        background=COLORS["accent_expiry_tint"],
        fieldbackground=COLORS["accent_expiry_tint"],
        foreground=COLORS["text_dark"],
        font=FONTS["table"],
        rowheight=ROW_HEIGHTS["Exp"],
        borderwidth=0,
        relief="flat",
    )

    s.configure("Exp.Treeview.Heading",
        font=FONTS["table_hdr"],
        background=COLORS["accent_expiry_tint"],
        foreground=COLORS["accent_expiry_fg"],
        relief="flat",
        borderwidth=0,
        padding=(12, 6),
    )
    s.map("Exp.Treeview.Heading",
        background=[("active", COLORS["accent_expiry_tint"])],
        relief=[("active", "flat"), ("pressed", "flat")],
    )

    # ── Global Scrollbar (what an unstyled bar actually gets) ─
    for base in ("TScrollbar", "Vertical.TScrollbar", "Horizontal.TScrollbar"):
        s.configure(base, **_scroll)
        s.map(base, background=[("active", COLORS["text_muted"])])

    # ── Combobox / OptionMenu base ────────────────────────────
    s.configure("TCombobox",
        fieldbackground=COLORS["bg_input"],
        background=COLORS["bg_input"],
        foreground=COLORS["text_dark"],
        arrowcolor=COLORS["btn_primary"],
        bordercolor=COLORS["border"],
        relief="flat",
    )

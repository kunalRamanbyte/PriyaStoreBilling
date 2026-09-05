"""
config.py — App-wide constants: colors, fonts, dimensions
Design: Direction B — soft, rounded, colour with a job
Imported from Claude Design: "Priya Store - Before & After.dc.html"

Three-step text scale (13 caption / 14-15 label / 16-17 body and every
figure), 44px pill controls, 24px card corners, and five accent hues each
locked to one meaning. Solid fills, hairline borders and corner radii only —
no gradient, blur or shadow, since CustomTkinter cannot draw them.
"""

import sys as _sys, os as _os

# ─── App Info ───────────────────────────────────────────────
APP_TITLE   = "Priya Store — Billing System"
# Keep in step with AppVersion / OutputBaseFilename in PriyaStore_installer.iss
APP_VERSION = "5.0"
SHOP_NAME   = "Priya Store"

# ─── DB Path — always absolute & writable ───────────────────
# When frozen (EXE): store next to the executable
# When running from source: store in the script's directory
if getattr(_sys, 'frozen', False):
    _BASE = _os.path.dirname(_sys.executable)
else:
    _BASE = _os.path.dirname(_os.path.abspath(__file__))

DB_PATH = _os.path.join(_BASE, "billing_data.db")


def resource_path(*parts):
    """Absolute path to a bundled read-only resource (e.g. images in assets/).

    Works both when running from source and inside a PyInstaller build:
    when frozen, bundled data lives under sys._MEIPASS, not next to the exe.
    """
    if getattr(_sys, 'frozen', False):
        base = getattr(_sys, '_MEIPASS', _BASE)
    else:
        base = _os.path.dirname(_os.path.abspath(__file__))
    return _os.path.join(base, *parts)

# ─── Window ─────────────────────────────────────────────────
WINDOW_WIDTH  = 1366
WINDOW_HEIGHT = 768
SIDEBAR_WIDTH = 236
# Icon-only sidebar. The nav pills live in a CTkScrollableFrame (13 of
# them never fit a 720p rail), and that frame reserves a fixed column
# for its scrollbar — so the pills centre on a narrower axis than the
# brand mark above them. The rail is therefore a 44px nav square, plus
# that column, plus 8px either side, and every non-scrolling block is
# padded right by the same amount to keep ONE optical centre running
# down the rail. Measured, not guessed: without it the icons sit 8px
# left of the brand mark and the avatar.
SIDEBAR_SCROLLBAR_W    = 16
SIDEBAR_WIDTH_COLLAPSED = 76

# ─── Direction B Palette — "soft, rounded, colour with a job" ───────
#
#  Imported from Claude Design: "Priya Store - Before & After.dc.html".
#
#  One vivid blue carries every action; four supporting hues are each
#  locked to a single meaning and never used decoratively:
#      blue   #2F6BD8  action          violet #7B61FF  counts
#      teal   #0B7268  money in        amber  #F0B429  expiry
#      coral  #FF7A4D  stock risk      red    #C23A3A  destructive
#
#  Every surface is a solid fill, a hairline border or a corner radius —
#  no gradient, blur or translucency anywhere, because CustomTkinter
#  cannot draw them. Vivid hues appear as icons, pills and accents on
#  their own pale tint; body text on a tint is always the dark variant,
#  so every foreground clears 4.5:1.
#
LIGHT_COLORS = {
    # ── Backgrounds ──────────────────────────────────────────
    "bg_main"       : "#F4F6FB",   # App canvas — cool near-white
    "bg_sidebar"    : "#FFFFFF",   # Sidebar is a white surface now
    "bg_header"     : "#FFFFFF",
    "bg_white"      : "#FFFFFF",
    "bg_card"       : "#FFFFFF",   # Solid card + hairline border
    "bg_input"      : "#F4F6FB",   # Filled pill inputs

    # ── Text ─────────────────────────────────────────────────
    "text_dark"     : "#16224A",   # Ink — primary
    "text_light"    : "#FFFFFF",
    "text_muted"    : "#5F6880",   # Secondary — 5.6:1 on white
    "text_blue"     : "#2558B4",
    "text_green"    : "#0B7268",
    "text_red"      : "#C23A3A",

    # ── Buttons — solid fills that carry white text at 4.9:1+ ─
    "btn_primary"   : "#2F6BD8",
    "btn_primary_h" : "#2558B4",
    "btn_success"   : "#0B7268",
    "btn_success_h" : "#095C54",
    "btn_danger"    : "#C23A3A",
    "btn_danger_h"  : "#A32F2F",
    "btn_warning"   : "#9A6510",   # Deepened amber — white text needs 4.5:1
    "btn_warning_h" : "#7A5210",
    "btn_secondary" : "#5F6880",
    "btn_secondary_h": "#4A5266",
    "btn_purple"    : "#5340BB",   # Deepened violet, same reason
    "btn_purple_h"  : "#43349A",

    # ── Sidebar — white surface, blue pill marks the active screen ──
    # The gradient is gone; the *_grad_* keys stay so any reader still
    # resolves, and both ends are the flat surface colour.
    "sidebar_grad_start": "#FFFFFF",
    "sidebar_grad_end"  : "#FFFFFF",
    "sidebar_active": "#2F6BD8",   # Active pill fill
    "sidebar_hover" : "#F4F6FB",
    "sidebar_text"  : "#5F6880",
    "sidebar_accent": "#2F6BD8",
    "sidebar_glow"  : "#2F6BD8",
    "sidebar_divider": "#E8EBF3",

    # ── Status Badges — pale tint, dark ink ──────────────────
    "badge_active"  : "#E6FAF7",
    "badge_void"    : "#FFECEC",
    "badge_draft"   : "#F1EDFF",
    "badge_low"     : "#FFF0EA",
    "badge_ok"      : "#E6FAF7",

    # ── Tables — white field, quiet uppercase header ─────────
    "tbl_header_bg" : "#FFFFFF",
    "tbl_header_fg" : "#5F6880",
    "tbl_row_alt"   : "#F7F9FD",
    "tbl_select"    : "#EAF1FF",
    "tbl_low_stock" : "#FFF0EA",

    # ── KPI accents — one hue per meaning. No gradients, so each
    #    *_end key mirrors its base and stays a valid colour. ──
    "kpi_blue"      : "#2F6BD8",
    "kpi_blue_end"  : "#2F6BD8",
    "kpi_green"     : "#0B7268",
    "kpi_green_end" : "#0B7268",
    "kpi_orange"    : "#FF7A4D",
    "kpi_orange_end": "#FF7A4D",
    "kpi_purple"    : "#7B61FF",
    "kpi_purple_end": "#7B61FF",
    "kpi_red"       : "#C23A3A",
    "kpi_red_end"   : "#C23A3A",
    "kpi_teal"      : "#0B7268",
    "kpi_pink"      : "#7B61FF",
    "kpi_yellow"    : "#F0B429",

    # ── Surface tokens (formerly "glass" — now solid + hairline) ──
    "glass_card"    : "#FFFFFF",
    "glass_border"  : "#E8EBF3",
    "glass_glow"    : "#EAF1FF",

    # -- Border / Divider --
    "border"        : "#E8EBF3",
    "border_focus"  : "#2F6BD8",

    # -- Category default --
    "cat_default"   : "#5F6880",

    # ── Direction B semantic accents ─────────────────────────
    # Each vivid hue with its pale tint and the dark ink to put on it.
    "accent_action"      : "#2F6BD8",
    "accent_action_deep" : "#2558B4",
    "accent_action_tint" : "#EAF1FF",
    "accent_action_fg"   : "#2558B4",
    "accent_money_fg"    : "#0B7268",
    "accent_danger_fg"   : "#A32F2F",
    "accent_counts"      : "#7B61FF",
    "accent_counts_fg"   : "#5340BB",
    "accent_counts_tint" : "#F1EDFF",
    "accent_money"       : "#0B7268",
    "accent_money_tint"  : "#E6FAF7",
    "accent_expiry"      : "#F0B429",
    "accent_expiry_fg"   : "#7A5210",
    "accent_expiry_tint" : "#FFF7E6",
    "accent_stock"       : "#FF7A4D",
    "accent_stock_fg"    : "#B8431F",
    "accent_stock_tint"  : "#FFF0EA",
    "accent_danger"      : "#C23A3A",
    "accent_danger_tint" : "#FFECEC",
    "on_accent"          : "#FFFFFF",
    "on_accent_soft"     : "#DBE6FA",   # Muted text on a deep blue panel
    "text_secondary"     : "#5B6480",
    "hairline"           : "#E8EBF3",
    "row_sep"            : "#F0F2F8",

    # ── Rotating row palette (all treeviews) ─────────────────
    # Direction B uses colour as *coding*, not as fills behind numbers,
    # so the rotation is a whisper zebra that only helps the eye track a
    # row across the width. Meaning still arrives via the override tags
    # below (low stock, void, draft...), which take precedence.
    "ROW_COLORS": [
        "#FFFFFF",
        "#F7F9FD",
        "#FFFFFF",
        "#F7F9FD",
        "#FFFFFF",
        "#F7F9FD",
    ],

    # ── Activity-log row colors, keyed by action PREFIX (Light) ──
    # Matched with str.startswith(), first hit wins — so a key must be at or
    # shorter than the action it catches ("BILL_VOID" catches "BILL_VOIDED").
    # Only list prefixes some code actually writes via db.log_activity().
    "LOG_ROW_COLORS": {
        "LOGIN"                 : ("#E6FAF7", "#16224A"),   # Teal
        "LOGOUT"                : ("#F4F6FB", "#16224A"),   # Neutral
        "BILL_SAVED"            : ("#EAF1FF", "#16224A"),   # Action blue
        "BILL_VOID"             : ("#FFECEC", "#16224A"),   # Destructive
        "RETURN_SAVED"          : ("#FFF0EA", "#16224A"),   # Coral
        "CUSTOMER_CHANGE_CLEAR" : ("#FDF2F8", "#16224A"),   # Pink — money movement
        "USER_"                 : ("#F1EDFF", "#16224A"),   # Violet
        "SETTINGS_SAVED"        : ("#EFF9F8", "#16224A"),   # Pale teal
        "PWD_CHANGED"           : ("#FFF7E6", "#16224A"),   # Amber
        "FORMAT_DATA"           : ("#FFD9D9", "#16224A"),   # Loudest red — factory reset
    },
    "LOG_ROW_DEFAULT" : ("#FFFFFF", "#16224A"),

    # ── Table row alert/tag colors (Light) ───────────────────
    "row_expired"     : "#FFECEC",
    "row_expiring"    : "#FFF7E6",
    "row_low_stock"   : "#FFF0EA",
    "row_ok"          : "#E6FAF7",
    "row_credit"      : "#FFF7E6",
    "row_payment"     : "#E6FAF7",
    "row_void"        : "#FFECEC",
    "row_draft"       : "#F1EDFF",
    "row_inactive"    : "#F4F6FB",
    "row_admin"       : "#F1EDFF",
    "fg_inactive"     : "#646C82",
    "fg_void"         : "#C23A3A",
    "bg_expiry_alert" : "#FFF7E6",
    "fg_expiry_alert" : "#7A5210",
    "bg_popup_item"   : "#F4F6FB",
    "bg_summary_panel": "#FFFFFF",
    "border_summary_panel": "#E8EBF3",
    "bg_summary_card": "#FFFFFF",
    "border_summary_card": "#E8EBF3",
    "fg_summary_entry": "#F4F6FB",
    "border_summary_entry": "#E8EBF3",
    "fg_summary_pm_btn": "#FFFFFF",
    "text_summary_row": "#16224A",
    "bg_summary_udhaar": "#FFF7E6",
    "border_summary_udhaar": "#F0DDB0",
    "text_summary_udhaar": "#7A5210",
    "bg_summary_change": "#E6FAF7",
    "border_summary_change": "#B7E6DF",
    "text_summary_change": "#0B7268",
    "text_summary_pm_btn": "#2558B4",
    "dropdown_fg_summary_pm": "#FFFFFF",
    "dropdown_text_summary_pm": "#16224A",
    "bg_summary_cash": "#E6FAF7",
    "border_summary_cash": "#B7E6DF",
    "text_summary_cash": "#0B7268",
    "bg_customer_entry": "#F4F6FB",
    "border_customer_entry": "#E8EBF3",
    "bg_chip_new_bill": "#F1EDFF",
    "fg_chip_new_bill": "#5340BB",
}

# Direction B after dark: the same six meanings, re-grounded on deep navy
# surfaces. Accents lift slightly so they still read against the dark field;
# tints become low-luminance versions of the same hue, and ink flips to a
# near-white so every pairing keeps its 4.5:1.
DARK_COLORS = {
    # ── Backgrounds ──────────────────────────────────────────
    "bg_main"       : "#0E1220",
    "bg_sidebar"    : "#151A2B",
    "bg_header"     : "#151A2B",
    "bg_white"      : "#151A2B",
    "bg_card"       : "#151A2B",
    "bg_input"      : "#1D2437",

    # ── Text ─────────────────────────────────────────────────
    "text_dark"     : "#EAEEF8",   # "dark" = primary ink; light in dark mode
    "text_light"    : "#FFFFFF",
    "text_muted"    : "#98A2BD",
    "text_blue"     : "#7FA9F0",
    "text_green"    : "#4FC3B4",
    "text_red"      : "#F08A8A",

    # ── Buttons ──────────────────────────────────────────────
    "btn_primary"   : "#2F6BD8",
    "btn_primary_h" : "#2555AE",
    "btn_success"   : "#0B7268",
    "btn_success_h" : "#08564F",
    "btn_danger"    : "#C23A3A",
    "btn_danger_h"  : "#9E2F2F",
    "btn_warning"   : "#9A6510",
    "btn_warning_h" : "#7A5210",
    "btn_secondary" : "#3A4359",
    "btn_secondary_h": "#4A5570",
    "btn_purple"    : "#5340BB",
    "btn_purple_h"  : "#6A55D6",

    # ── Sidebar ──────────────────────────────────────────────
    "sidebar_grad_start": "#151A2B",
    "sidebar_grad_end"  : "#151A2B",
    "sidebar_active": "#2F6BD8",
    "sidebar_hover" : "#1D2437",
    "sidebar_text"  : "#98A2BD",
    "sidebar_accent": "#7FA9F0",
    "sidebar_glow"  : "#2F6BD8",
    "sidebar_divider": "#232B40",

    # ── Status Badges ────────────────────────────────────────
    "badge_active"  : "#123A35",
    "badge_void"    : "#3B1A1A",
    "badge_draft"   : "#241E45",
    "badge_low"     : "#3A2015",
    "badge_ok"      : "#123A35",

    # ── Tables ───────────────────────────────────────────────
    "tbl_header_bg" : "#151A2B",
    "tbl_header_fg" : "#98A2BD",
    "tbl_row_alt"   : "#192031",
    "tbl_select"    : "#1E3358",
    "tbl_low_stock" : "#3A2015",

    # ── KPI accents ──────────────────────────────────────────
    "kpi_blue"      : "#4880E4",
    "kpi_blue_end"  : "#4880E4",
    "kpi_green"     : "#2FA093",
    "kpi_green_end" : "#2FA093",
    "kpi_orange"    : "#FF7A4D",
    "kpi_orange_end": "#FF7A4D",
    "kpi_purple"    : "#8E78FF",
    "kpi_purple_end": "#8E78FF",
    "kpi_red"       : "#E05555",
    "kpi_red_end"   : "#E05555",
    "kpi_teal"      : "#2FA093",
    "kpi_pink"      : "#8E78FF",
    "kpi_yellow"    : "#F0B429",

    # ── Surface tokens ───────────────────────────────────────
    "glass_card"    : "#151A2B",
    "glass_border"  : "#232B40",
    "glass_glow"    : "#1E3358",

    # -- Border / Divider --
    "border"        : "#232B40",
    "border_focus"  : "#4880E4",
    "cat_default"   : "#98A2BD",

    # ── Direction B semantic accents ─────────────────────────
    "accent_action"      : "#2F6BD8",
    "accent_action_deep" : "#24539F",
    "accent_action_tint" : "#18243F",
    "accent_action_fg"   : "#9EC1FF",
    "accent_money_fg"    : "#5FD3C2",
    "accent_danger_fg"   : "#F09A9A",
    "accent_counts"      : "#8E78FF",
    "accent_counts_fg"   : "#B9AAFF",
    "accent_counts_tint" : "#221D3D",
    "accent_money"       : "#0B7268",
    "accent_money_tint"  : "#10322E",
    "accent_expiry"      : "#F0B429",
    "accent_expiry_fg"   : "#E8C46B",
    "accent_expiry_tint" : "#2E2411",
    "accent_stock"       : "#FF7A4D",
    "accent_stock_fg"    : "#FFA383",
    "accent_stock_tint"  : "#331D13",
    "accent_danger"      : "#C23A3A",
    "accent_danger_tint" : "#331616",
    "on_accent"          : "#FFFFFF",
    "on_accent_soft"     : "#C3D3F2",
    "text_secondary"     : "#98A2BD",
    "hairline"           : "#232B40",
    "row_sep"            : "#1E2537",

    # ── Rotating row palette (whisper zebra, dark) ───────────
    "ROW_COLORS": [
        "#151A2B",
        "#192031",
        "#151A2B",
        "#192031",
        "#151A2B",
        "#192031",
    ],

    # ── Activity-log row colors, keyed by action PREFIX (Dark) ──
    # Key set is kept identical to LIGHT_COLORS on purpose.
    "LOG_ROW_COLORS": {
        "LOGIN"                 : ("#10322E", "#EAEEF8"),
        "LOGOUT"                : ("#1D2437", "#EAEEF8"),
        "BILL_SAVED"            : ("#18243F", "#EAEEF8"),
        "BILL_VOID"             : ("#331616", "#EAEEF8"),
        "RETURN_SAVED"          : ("#331D13", "#EAEEF8"),
        "CUSTOMER_CHANGE_CLEAR" : ("#331B29", "#EAEEF8"),
        "USER_"                 : ("#221D3D", "#EAEEF8"),
        "SETTINGS_SAVED"        : ("#122E2C", "#EAEEF8"),
        "PWD_CHANGED"           : ("#2E2411", "#EAEEF8"),
        "FORMAT_DATA"           : ("#4A1A1A", "#FFFFFF"),
    },
    "LOG_ROW_DEFAULT" : ("#151A2B", "#EAEEF8"),

    # ── Table row alert/tag colors (Dark) ────────────────────
    "row_expired"     : "#331616",
    "row_expiring"    : "#2E2411",
    "row_low_stock"   : "#331D13",
    "row_ok"          : "#10322E",
    "row_credit"      : "#2E2411",
    "row_payment"     : "#10322E",
    "row_void"        : "#331616",
    "row_draft"       : "#221D3D",
    "row_inactive"    : "#1D2437",
    "row_admin"       : "#221D3D",
    "fg_inactive"     : "#9AA3BC",
    "fg_void"         : "#F08A8A",
    "bg_expiry_alert" : "#2E2411",
    "fg_expiry_alert" : "#E8C46B",
    "bg_popup_item"   : "#1D2437",
    "bg_summary_panel": "#151A2B",
    "border_summary_panel": "#232B40",
    "bg_summary_card": "#151A2B",
    "border_summary_card": "#232B40",
    "fg_summary_entry": "#1D2437",
    "border_summary_entry": "#232B40",
    "fg_summary_pm_btn": "#FFFFFF",
    "text_summary_row": "#EAEEF8",
    "bg_summary_udhaar": "#2E2411",
    "border_summary_udhaar": "#4A3A16",
    "text_summary_udhaar": "#E8C46B",
    "bg_summary_change": "#10322E",
    "border_summary_change": "#1C5049",
    "text_summary_change": "#4FC3B4",
    "text_summary_pm_btn": "#7FA9F0",
    "dropdown_fg_summary_pm": "#FFFFFF",
    "dropdown_text_summary_pm": "#EAEEF8",
    "bg_summary_cash": "#10322E",
    "border_summary_cash": "#1C5049",
    "text_summary_cash": "#4FC3B4",
    "bg_customer_entry": "#1D2437",
    "border_customer_entry": "#232B40",
    "bg_chip_new_bill": "#221D3D",
    "fg_chip_new_bill": "#B9AAFF",
}

COLORS = dict(LIGHT_COLORS)

def apply_theme_mode(mode: str):
    """In-place update of COLORS dictionary values to switch themes."""
    COLORS.clear()
    source = LIGHT_COLORS if mode.lower() == "light" else DARK_COLORS
    COLORS.update(source)


# --- Category Color Wheel (Modern vibrant) ---
CAT_COLORS = [
    "#EF4444",   # Red
    "#F59E0B",   # Amber
    "#EAB308",   # Yellow
    "#10B981",   # Emerald
    "#3B82F6",   # Blue
    "#06B6D4",   # Cyan
    "#8B5CF6",   # Violet
    "#EC4899",   # Pink
    "#78716C",   # Stone
    "#64748B",   # Slate
]

# --- Typography ---
# Direction B keeps a strict three-step scale: 13px captions, 14-15px
# labels, 16-17px body and every figure. Headings and figures step up
# from there; nothing sits between the steps.
F  = "Segoe UI"
FB = "Segoe UI Semibold"

FONTS = {
    "heading"     : (F,  26, "bold"),   # Screen title
    "subheading"  : (FB, 19, "bold"),   # Card / section title
    "body"        : (F,  16),
    "body_bold"   : (FB, 16, "bold"),
    "button"      : (FB, 15, "bold"),   # Pill control label
    "label_form"  : (F,  15),
    "input"       : (F,  16),
    "small"       : (F,  14),
    "small_bold"  : (FB, 14, "bold"),
    "caption"     : (F,  13),
    "sidebar"     : (F,  15),           # Nav label — weight comes from state
    "sidebar_sm"  : (F,  13),
    "table"       : (F,  15),
    "table_hdr"   : (FB, 13, "bold"),   # Quiet uppercase column header
    "num_sm"      : (FB, 22, "bold"),
    "num_md"      : (FB, 28, "bold"),   # KPI value
    "num_lg"      : (FB, 32, "bold"),   # Report hero figure
    "num_xl"      : (FB, 42, "bold"),   # POS grand total
}

# --- Corner Radii (Direction B: generous, pill-first) ---
# A pill's radius is always half its height, so a 44px control takes 22.
RADII = {
    "card"    : 24,   # Cards, tables, panels
    "button"  : 22,   # 44px pill control
    "input"   : 22,   # 44px pill field
    "badge"   : 14,   # 28px status pill
    "sidebar" : 14,   # 44px nav item
    "pill_sm" : 17,   # 34px segmented-control chip
    "pill_lg" : 28,   # 56px primary CTA / search bar
    "bubble"  : 14,   # 40px icon square
    "hero"    : 36,   # Login card
}

# --- Control metrics (Direction B) ---
# Heights the design pins down, so screens stop inventing their own.
METRICS = {
    "nav_item"   : 44,
    "control"    : 44,   # Standard pill button / field
    "control_lg" : 56,   # Primary CTA, POS search
    "control_sm" : 34,   # Segmented-control chip
    "bubble"     : 40,   # KPI / avatar icon square
    "header"     : 76,   # Screen header band
    "row"        : 56,   # Table row
    "row_lg"     : 62,   # Bill-history row
    "hairline"   : 1,
}

# --- Responsive breakpoints ---
# Measured on the LOGICAL width (window px / widget scaling), because every
# widget size in this app is expressed in logical units. A 1366px window at
# the 1.0 baseline is "standard"; the same window on a machine that scaled up
# for a tall screen can be "compact", which is exactly the case that used to
# clip the cart and the report header.
BREAKPOINTS = {
    "compact":  0,      # < 1180 logical - 720p panels, or a resized window
    "standard": 1180,   # the 1366x768 shop PC at scale 1.0
    "wide":     1560,   # 1600x900 and up
}


def breakpoint_for(logical_width: float) -> str:
    """Name the layout class for a logical content width."""
    if logical_width >= BREAKPOINTS["wide"]:
        return "wide"
    if logical_width >= BREAKPOINTS["standard"]:
        return "standard"
    return "compact"


# Page gutter per breakpoint. One source, so screens stop inventing 12/20/
# 24/25/26/28 independently.
GUTTERS = {"compact": 18, "standard": 28, "wide": 36}

# --- Units ---
UNITS = ["piece", "kg", "gram", "litre", "ml", "box", "pack", "dozen", "bottle"]

# --- Payment modes ---
PAYMENT_MODES = ["Cash", "Credit (Udhaar)", "UPI", "Card"]

# --- Keyboard shortcuts ---
SHORTCUTS = {
    "F2"  : "Search Product",
    "F8"  : "Hold Bill",
    "F10" : "Print & Save Bill",
    "Del" : "Remove Selected Item",
}

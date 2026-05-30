"""
config.py — App-wide constants: colors, fonts, dimensions
Design: Apple-standard, modern, vibrant — optimised for 60+ age users
Color philosophy: macOS Ventura palette · SF-Pro scale · vivid accents
"""

import sys as _sys, os as _os

# ─── App Info ───────────────────────────────────────────────
APP_TITLE   = "Priya Store — Billing System"
APP_VERSION = "1.0"
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
SIDEBAR_WIDTH = 240

# ─── Apple-Standard Color Palette ───────────────────────────
#
#  UPGRADED: Modern glassmorphism + gradient design system
#  Sidebar   : Deep navy gradient feel (#0F172A)
#  Background: Warm blue-tinted off-white (#EEF2FF)
#  Cards     : Semi-transparent glass white
#  Accents   : Vivid gradients with Apple system colors
#
COLORS = {
    # ── Backgrounds ──────────────────────────────────────────
    "bg_main"       : "#EEF2FF",   # Warm blue-tinted off-white
    "bg_sidebar"    : "#1B2A4E",   # Deep gradient blue fallback
    "bg_header"     : "#FFFFFF",   # Clean white header
    "bg_white"      : "#FFFFFF",
    "bg_card"       : "#FFFFFF",   # White card (glass overlay via border)
    "bg_input"      : "#F1F5F9",   # Cool slate input bg

    # ── Text ─────────────────────────────────────────────────
    "text_dark"     : "#0F172A",   # Deep navy primary text
    "text_light"    : "#FFFFFF",
    "text_muted"    : "#64748B",   # Slate secondary text
    "text_blue"     : "#3B82F6",   # Vivid Blue
    "text_green"    : "#10B981",   # Emerald Green
    "text_red"      : "#EF4444",   # Modern Red

    # ── Modern Gradient Buttons ──────────────────────────────
    "btn_primary"   : "#3B82F6",   # Blue 500
    "btn_primary_h" : "#2563EB",   # Blue 600 (hover)
    "btn_success"   : "#10B981",   # Emerald 500
    "btn_success_h" : "#059669",   # Emerald 600
    "btn_danger"    : "#EF4444",   # Red 500
    "btn_danger_h"  : "#DC2626",   # Red 600
    "btn_warning"   : "#F59E0B",   # Amber 500
    "btn_warning_h" : "#D97706",   # Amber 600
    "btn_secondary" : "#64748B",   # Slate 500
    "btn_secondary_h": "#475569",  # Slate 600
    "btn_purple"    : "#8B5CF6",   # Violet 500
    "btn_purple_h"  : "#7C3AED",   # Violet 600

    # ── Sidebar (dark navy glassmorphism) ────────────────────
    "sidebar_active": "#1E3A5F",   # Active item — deep blue glass
    "sidebar_hover" : "#1E293B",   # Hover — subtle lighten
    "sidebar_text"  : "#E2E8F0",   # Slate 200 — soft white
    "sidebar_accent": "#60A5FA",   # Blue 400 — brand accent
    "sidebar_glow"  : "#3B82F6",   # Active glow indicator
    "sidebar_divider": "#1E293B",  # Subtle divider

    # ── Status Badges ────────────────────────────────────────
    "badge_active"  : "#D1FAE5",   # Emerald 100
    "badge_void"    : "#FEE2E2",   # Red 100
    "badge_draft"   : "#FEF3C7",   # Amber 100
    "badge_low"     : "#FEE2E2",
    "badge_ok"      : "#D1FAE5",

    # ── Tables ───────────────────────────────────────────────
    "tbl_header_bg" : "#0F172A",   # Deep navy header
    "tbl_header_fg" : "#F8FAFC",   # Near white
    "tbl_row_alt"   : "#F8FAFC",   # Barely-there zebra (Slate 50)
    "tbl_select"    : "#DBEAFE",   # Blue 100 — soft selection
    "tbl_low_stock" : "#FEE2E2",   # Soft red

    # ── KPI Card Gradient Colors (start → end) ──────────────
    "kpi_blue"      : "#3B82F6",
    "kpi_blue_end"  : "#6366F1",   # Blue → Indigo gradient
    "kpi_green"     : "#10B981",
    "kpi_green_end" : "#14B8A6",   # Emerald → Teal gradient
    "kpi_orange"    : "#F59E0B",
    "kpi_orange_end": "#EF4444",   # Amber → Red gradient
    "kpi_purple"    : "#8B5CF6",
    "kpi_purple_end": "#EC4899",   # Violet → Pink gradient
    "kpi_red"       : "#EF4444",
    "kpi_red_end"   : "#F97316",   # Red → Orange gradient
    "kpi_teal"      : "#14B8A6",
    "kpi_pink"      : "#EC4899",
    "kpi_yellow"    : "#EAB308",

    # ── Glass Effect Tokens ──────────────────────────────────
    "glass_card"    : "#FFFFFF",   # Glass card background
    "glass_border"  : "#E2E8F0",   # Subtle glass border
    "glass_glow"    : "#BFDBFE",   # Blue glow accent

    # -- Border / Divider --
    "border"        : "#CBD5E1",   # Slate 300 — refined separator
    "border_focus"  : "#3B82F6",   # Blue focus ring

    # -- Category default --
    "cat_default"   : "#64748B",
}

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
F  = "Segoe UI"
FB = "Segoe UI Semibold"

FONTS = {
    "heading"     : (F,  27, "bold"),
    "subheading"  : (F,  21, "bold"),
    "body"        : (F,  16),
    "body_bold"   : (F,  16, "bold"),
    "button"      : (F,  16, "bold"),
    "label_form"  : (FB, 15),
    "input"       : (F,  15),
    "small"       : (F,  14),
    "small_bold"  : (F,  14, "bold"),
    "caption"     : (F,  13),
    "sidebar"     : (F,  15, "bold"),
    "sidebar_sm"  : (F,  13),
    "table"       : (F,  14),
    "table_hdr"   : (F,  14, "bold"),
    "num_sm"      : (FB, 22, "bold"),
    "num_md"      : (FB, 30, "bold"),
    "num_lg"      : (FB, 42, "bold"),
    "num_xl"      : (FB, 56, "bold"),
}

# --- Corner Radii (Modern squircle feel) ---
RADII = {
    "card"    : 20,
    "button"  : 14,
    "input"   : 12,
    "badge"   : 8,
    "sidebar" : 12,
}

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

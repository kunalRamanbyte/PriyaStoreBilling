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
LIGHT_COLORS = {
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
    "sidebar_grad_start": "#1E3A8A", # Royal Blue
    "sidebar_grad_end"  : "#0F172A", # Navy Blue
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

    # ── Rotating row palette (6 soft pastels, used across all treeviews) ──
    "ROW_COLORS": [
        "#E3F2FD",   # Light Blue
        "#E8F5E9",   # Light Green
        "#F3E5F5",   # Light Purple
        "#FFF3E0",   # Light Orange
        "#E0F7FA",   # Light Teal
        "#FCE4EC",   # Light Pink
    ],
}

DARK_COLORS = {
    # ── Backgrounds ──────────────────────────────────────────
    "bg_main"       : "#0F172A",   # Slate 900
    "bg_sidebar"    : "#070A13",   # Very dark navy
    "bg_header"     : "#1E293B",   # Slate 800
    "bg_white"      : "#1E293B",
    "bg_card"       : "#1E293B",   # Slate 800 card
    "bg_input"      : "#0F172A",   # Slate 900 input

    # ── Text ─────────────────────────────────────────────────
    "text_dark"     : "#F8FAFC",   # Slate 50 white text
    "text_light"    : "#FFFFFF",
    "text_muted"    : "#94A3B8",   # Slate 400 muted text
    "text_blue"     : "#60A5FA",
    "text_green"    : "#34D399",
    "text_red"      : "#F87171",

    # ── Modern Accent Buttons ────────────────────────────────
    "btn_primary"   : "#2563EB",   # Vibrant Blue
    "btn_primary_h" : "#1D4ED8",
    "btn_success"   : "#059669",   # Emerald Green
    "btn_success_h" : "#047857",
    "btn_danger"    : "#DC2626",   # Crimson Red
    "btn_danger_h"  : "#B91C1C",
    "btn_warning"   : "#D97706",   # Amber
    "btn_warning_h" : "#B45309",
    "btn_secondary" : "#475569",   # Slate Grey
    "btn_secondary_h": "#334155",
    "btn_purple"    : "#7C3AED",   # Violet Accent
    "btn_purple_h"  : "#6D28D9",

    # ── Sidebar (dark navy glassmorphism) ────────────────────
    "sidebar_grad_start": "#0F172A", # Navy
    "sidebar_grad_end"  : "#070B14", # Vantablack Blue
    "sidebar_active": "#1E293B",   # Slate 800
    "sidebar_hover" : "#334155",   # Slate 700
    "sidebar_text"  : "#F3F4F6",   # Soft white
    "sidebar_accent": "#93C5FD",   # Soft blue
    "sidebar_glow"  : "#60A5FA",
    "sidebar_divider": "#334155",

    # ── Status Badges ────────────────────────────────────────
    "badge_active"  : "#064E3B",   # Dark green
    "badge_void"    : "#7F1D1D",   # Dark red
    "badge_draft"   : "#78350F",   # Dark amber
    "badge_low"     : "#7F1D1D",
    "badge_ok"      : "#064E3B",

    # ── Tables ───────────────────────────────────────────────
    "tbl_header_bg" : "#1E293B",   # Slate 800 header
    "tbl_header_fg" : "#F8FAFC",
    "tbl_row_alt"   : "#1E293B",
    "tbl_select"    : "#374151",   # Soft grey selection
    "tbl_low_stock" : "#451A1A",   # Muted red row

    # ── KPI Card Colors ──────────────────────────────────────
    "kpi_blue"      : "#2563EB",
    "kpi_blue_end"  : "#4F46E5",
    "kpi_green"     : "#059669",
    "kpi_green_end" : "#0D9488",
    "kpi_orange"    : "#D97706",
    "kpi_orange_end": "#DC2626",
    "kpi_purple"    : "#7C3AED",
    "kpi_purple_end": "#DB2777",
    "kpi_red"       : "#DC2626",
    "kpi_red_end"   : "#EA580C",
    "kpi_teal"      : "#0D9488",
    "kpi_pink"      : "#DB2777",
    "kpi_yellow"    : "#CA8A04",

    # ── Glass Effect Tokens ──────────────────────────────────
    "glass_card"    : "#1E293B",
    "glass_border"  : "#334155",
    "glass_glow"    : "#1E3A8A",

    # -- Border / Divider --
    "border"        : "#334155",
    "border_focus"  : "#60A5FA",
    "cat_default"   : "#94A3B8",

    # ── Muted dark table colors ──────────────────────────────
    "ROW_COLORS": [
        "#1E293B",   # Dark slate
        "#143A26",   # Muted Green
        "#2D1D3A",   # Muted Purple
        "#3D271A",   # Muted Orange
        "#173A3C",   # Muted Teal
        "#3C1D2A",   # Muted Pink
    ],
}

# The active color map — dynamically populated
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

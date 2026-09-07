"""
main.py — Kunal's FMCG Grocery Billing System
Phase 1+2+3+4: Login • Dashboard • POS Billing • Bill History • Products • Categories
               Inventory • Suppliers • Purchase/GRN • Customers • Reports
               Settings • Users • Activity Log  (Phase 4)

Run:  python main.py
Login: admin / admin123  (cashier: cashier / cash123)
"""

import os
import sys
import shutil
import ctypes
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# ── DPI awareness (must be set BEFORE any window is created) ──
# Prevents window appearing off-screen on high-DPI / multi-monitor setups
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)   # PROCESS_SYSTEM_DPI_AWARE
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# Set theme BEFORE importing screens
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

from config import (COLORS, FONTS, RADII, METRICS, MOTION, APP_TITLE, APP_VERSION, SHOP_NAME,
                    WINDOW_WIDTH, WINDOW_HEIGHT, SIDEBAR_WIDTH,
                    SIDEBAR_WIDTH_COLLAPSED, SIDEBAR_SCROLLBAR_W,
                    resource_path)
from database import Database
from lang import t
import motion
from ui_utils import attach_tooltip
from screen_login import LoginScreen
from screen_dashboard import DashboardScreen
from screen_billing import BillingScreen
from screen_bill_history import BillHistoryScreen
from screen_products import ProductScreen
from screen_categories import CategoryScreen
from screen_inventory import InventoryScreen
from screen_suppliers import SupplierScreen
from screen_purchase import PurchaseScreen
from screen_customers import CustomerScreen
from screen_reports import ReportScreen
from screen_settings import SettingsScreen, _run_backup
from styles import setup_ttk_styles
from screen_users import UserScreen
from screen_activity_log import ActivityLogScreen


class BillingApp(ctk.CTk):
    """Main application window — manages navigation between screens."""

    def __init__(self):
        super().__init__()
        self.db           = Database()
        self.db.init_db()
        self.db.set_setting("shop_name", "Priya Store") # Always enforce Priya Store globally
        self.current_user = None
        self.current_role = None
        self.current_lang = self.db.get_setting("app_language", "English")
        self.current_theme = self.db.get_setting("app_theme", "System")
        # Icon-only sidebar. Off by default: a shopkeeper who has never
        # seen the rail should meet the labelled menu first.
        self.sidebar_collapsed = self.db.get_setting("sidebar_collapsed", "0") == "1"
        # Motion reads its own preference once; the tween loop must never
        # touch the database.
        motion.init(self.db)

        # Apply theme setting on startup
        ctk.set_appearance_mode(self.current_theme)
        from config import apply_theme_mode
        apply_theme_mode(ctk.get_appearance_mode().lower())

        self.screens      = {}
        self.nav_buttons  = {}
        self.nav_icons    = {}

        setup_ttk_styles(ctk.get_appearance_mode().lower())              # register all ttk styles once
        self._setup_window()
        self._show_login()
        self._schedule_daily_backup()   # start 24-hour backup timer

    # ─────────────────────────────────────────────────────────────
    # Window setup
    # ─────────────────────────────────────────────────────────────
    def _setup_window(self):
        # Version in the title bar so a shop can report which build it runs
        self.title(f"{APP_TITLE}   v{APP_VERSION}")

        # ── Responsive fit: adapt to the real screen work area ──
        # Supported range: 1280x720 (floor) up to 3840x2160 / 4K (ceiling),
        # kept inside a widescreen 16:10..16:9 aspect band. The window grows
        # to fill larger displays and shrinks toward the floor on smaller
        # ones, while widgets scale proportionally so nothing is hidden and
        # the UI never looks sparse on a 4K panel.
        self._fit_w, self._fit_h, self._fit_scale = self._compute_fit()

        # Apply proportional widget scaling (the desktop analog of a
        # fluid grid) — scales the UI up on 4K and down on 720p. Window
        # scaling stays at 1.0 so geometry remains in raw pixels and we
        # control the window size directly.
        if abs(self._fit_scale - 1.0) > 0.001:
            try:
                ctk.set_widget_scaling(self._fit_scale)
            except Exception:
                pass

        self.geometry(f"{self._fit_w}x{self._fit_h}")
        # Hard 1280x720 floor; the window can grow up to 4K via _compute_fit.
        self.minsize(self._MIN_W, self._MIN_H)
        self.resizable(True, True)
        self.configure(fg_color=COLORS["bg_main"])
        self._center_window()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Load custom high-resolution window icon
        try:
            icon_path = resource_path("assets", "app_icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass

    # Reserved vertical space for OS taskbar + window title bar
    _SCREEN_CHROME_PX = 72

    # Responsive envelope
    _MIN_W, _MIN_H = 1280, 720          # smallest supported (16:9)
    _MAX_W, _MAX_H = 3840, 2160         # largest supported (4K UHD, 16:9)
    _RATIO_WIDE    = 16 / 9             # 1.778 — widest allowed
    _RATIO_TALL    = 16 / 10            # 1.600 — tallest (least wide) allowed
    # Widget-scaling bounds, relative to the 1366x768 design baseline
    _SCALE_MIN, _SCALE_MAX = 0.80, 1.50

    def _compute_fit(self):
        """Return (width, height, scale) fitted to the usable screen area.

        The window grows from a 1280x720 floor up to a 3840x2160 (4K)
        ceiling, always staying inside a widescreen 16:10..16:9 ratio band
        so it looks right on both 16:9 and 16:10 monitors. `scale` is a
        proportional widget factor (relative to the 1366x768 design
        baseline) that enlarges the UI on big/4K panels and shrinks it on
        small ones, bounded to keep text legible for 60+ users.
        """
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        # Guard against bogus DPI / multi-monitor readings
        if not (800 <= sw <= 7680):
            sw = 1366
        if not (600 <= sh <= 4320):
            sh = 768

        # Usable area, capped at the 4K ceiling
        avail_w = min(sw, self._MAX_W)
        avail_h = min(max(400, sh - self._SCREEN_CHROME_PX), self._MAX_H)

        # Constrain the box into the 16:10..16:9 aspect band
        w, h = avail_w, avail_h
        ratio = w / h
        if ratio > self._RATIO_WIDE:        # too wide -> trim width
            w = int(h * self._RATIO_WIDE)
        elif ratio < self._RATIO_TALL:      # too tall -> trim height
            h = int(w / self._RATIO_TALL)

        # Honour the 1280x720 floor — 720p is the minimum supported resolution.
        win_w = max(self._MIN_W, w)
        win_h = max(self._MIN_H, h)

        # Proportional widget scaling, driven by the tighter vertical axis
        scale = win_h / WINDOW_HEIGHT       # WINDOW_HEIGHT = 768 design baseline
        scale = max(self._SCALE_MIN, min(self._SCALE_MAX, scale))
        return win_w, win_h, scale

    def _center_window(self):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        # Clamp to sensible screen bounds (guards against DPI/multi-monitor issues)
        if sw < 800 or sw > 7680:
            sw = 1366
        if sh < 600 or sh > 4320:
            sh = 768
        x = max(0, (sw - self._fit_w)  // 2)
        y = max(0, (sh - self._fit_h - self._SCREEN_CHROME_PX) // 2)
        self.geometry(f"{self._fit_w}x{self._fit_h}+{x}+{y}")

    def _on_close(self):
        if messagebox.askyesno(t("Exit", self.current_lang),
                               t("Exit the billing system?", self.current_lang)):
            self._auto_backup()
            self.destroy()

    def _auto_backup(self):
        """Silently backup DB on close — uses shared helper from screen_settings."""
        try:
            _run_backup(self.db)
            ts_display = datetime.now().strftime("%d %b %Y  %I:%M %p")
            self.db.set_setting("last_backup", ts_display)
        except Exception:
            pass  # Never block close due to backup failure

    # ── Scheduled daily backup ───────────────────────────────────────
    _BACKUP_INTERVAL_MS = 24 * 60 * 60 * 1000   # 24 hours in milliseconds

    def _schedule_daily_backup(self):
        """Fire a backup every 24 h while the app is running."""
        self._daily_backup_job = self.after(
            self._BACKUP_INTERVAL_MS, self._daily_backup_tick
        )

    def _daily_backup_tick(self):
        """Called by tkinter's after() every 24 hours."""
        enabled = self.db.get_setting("auto_backup_enabled", "1")
        if enabled == "1":
            try:
                _run_backup(self.db)
                ts_display = datetime.now().strftime("%d %b %Y  %I:%M %p")
                self.db.set_setting("last_backup", ts_display)
                # Refresh the settings screen label if it's visible
                if "settings" in self.screens:
                    try:
                        scr = self.screens["settings"]
                        scr._last_backup_label.configure(text=ts_display)
                    except Exception:
                        pass
            except Exception:
                pass
        # Reschedule for next 24 hours
        self._daily_backup_job = self.after(
            self._BACKUP_INTERVAL_MS, self._daily_backup_tick
        )

    def update_auto_backup_schedule(self):
        """Called by the Settings screen when the toggle changes."""
        pass   # Toggle is read live in _daily_backup_tick; no restart needed

    # ─────────────────────────────────────────────────────────────
    # Login / Logout
    # ─────────────────────────────────────────────────────────────
    def _show_login(self):
        for w in self.winfo_children():
            w.destroy()
        self.screens = {}
        login = LoginScreen(self, self._on_login_success)
        login.pack(fill="both", expand=True)

    def _on_login_success(self, user_data: dict):
        self.current_user = user_data
        self.current_role = user_data["role"]
        self.db.log_activity(
            user_data["user_id"], "LOGIN",
            f"{user_data['name']} logged in"
        )
        self._build_main_window()

    def logout(self):
        if messagebox.askyesno(t("Logout", self.current_lang),
                               t("Are you sure you want to logout?", self.current_lang)):
            if self.current_user:
                self.db.log_activity(
                    self.current_user["user_id"], "LOGOUT",
                    f"{self.current_user['name']} logged out"
                )
            self.current_user = None
            self.current_role = None
            self.screens      = {}
            self.nav_buttons  = {}
            self.nav_icons    = {}
            self._show_login()

    # ─────────────────────────────────────────────────────────────
    # Main window (sidebar + content)
    # ─────────────────────────────────────────────────────────────
    def _build_main_window(self):
        for w in self.winfo_children():
            w.destroy()

        # Direction B has no global header band: the brand lives in the
        # sidebar and each screen owns its own title header, so the content
        # area starts at the top of the window.
        body = ctk.CTkFrame(self, fg_color=COLORS["bg_main"], corner_radius=0)
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(2, weight=1)
        body.grid_rowconfigure(0, weight=1)

        # Kept so _toggle_sidebar() can rebuild the rail alone, without
        # disturbing the content area or any cached screen.
        self._body = body
        self._sidebar = self._build_sidebar(body)
        self._sidebar.grid(row=0, column=0, sticky="nsew")

        # Hairline between sidebar and content — a solid 1px frame, since a
        # CTkFrame border would draw on all four sides.
        ctk.CTkFrame(body, fg_color=COLORS["hairline"], corner_radius=0,
                     width=1).grid(row=0, column=1, sticky="ns")

        self.content_area = ctk.CTkFrame(body, fg_color=COLORS["bg_main"],
                                          corner_radius=0)
        self.content_area.grid(row=0, column=2, sticky="nsew")

        self.navigate_to("dashboard")

    def _nav_font(self, active: bool):
        """Direction B weights the active nav label bold and the rest regular."""
        family, size = FONTS["sidebar"][0], FONTS["sidebar"][1]
        return (family, size, "bold") if active else (family, size)

    def _build_sidebar(self, parent):
        """Direction B sidebar: a white surface, a rounded brand mark, and
        44px nav pills where a solid blue fill — not a glow or a border —
        marks the screen you are on.

        When self.sidebar_collapsed is set the same rail is built icon-only at
        SIDEBAR_WIDTH_COLLAPSED: every pill becomes a centred 44px square and
        the label it lost moves into a hover tooltip."""
        narrow  = self.sidebar_collapsed
        sidebar = ctk.CTkFrame(
            parent, fg_color=COLORS["bg_sidebar"], corner_radius=0,
            width=SIDEBAR_WIDTH_COLLAPSED if narrow else SIDEBAR_WIDTH)
        sidebar.pack_propagate(False)

        # Rebuilt from scratch on every toggle, so drop the old widget handles
        # rather than leaving _paint_nav() to configure destroyed buttons.
        self.nav_buttons = {}
        self.nav_icons   = {}

        NAV = [
            ("🏠", "Dashboard",    "dashboard",    ["admin", "cashier", "stock_manager"]),
            ("🧾", "New Bill",     "billing",      ["admin", "cashier"]),
            ("📋", "Bill History", "bill_history", ["admin", "cashier", "stock_manager"]),
            ("📦", "Products",     "products",     ["admin", "stock_manager"]),
            ("🏷️", "Categories",  "categories",   ["admin", "stock_manager"]),
            ("📊", "Inventory",    "inventory",    ["admin", "stock_manager"]),
            ("🏭", "Suppliers",    "suppliers",    ["admin", "stock_manager"]),
            ("🛒", "Purchase/GRN", "purchase",     ["admin", "stock_manager"]),
            ("👥", "Customers",    "customers",    ["admin", "cashier"]),
            ("📈", "Reports",      "reports",      ["admin", "stock_manager"]),
            ("⚙️", "Settings",    "settings",     ["admin"]),
            ("👤", "Users",        "users",        ["admin"]),
            # 🕐, not the 📋 Bill History already owns: with the labels
            # gone, a duplicated glyph is the whole label.
            ("🕐", "Activity Log", "activity_log", ["admin"]),
        ]

        # Authoritative screen->roles map, consulted by navigate_to() so that
        # non-sidebar entry points (dashboard quick actions, resume-draft, etc.)
        # cannot escalate a role past what the sidebar allows.
        self._screen_roles = {key: roles for _, _, key, roles in NAV}

        # -- Brand block ------------------------------------------
        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.pack(fill="x",
                   padx=(0, SIDEBAR_SCROLLBAR_W) if narrow else 20,
                   pady=(18, 10) if narrow else (18, 14))

        mark = ctk.CTkFrame(brand, fg_color=COLORS["accent_action"],
                            corner_radius=RADII["bubble"],
                            width=METRICS["bubble"], height=METRICS["bubble"])
        if narrow:
            mark.pack()
        else:
            mark.pack(side="left", padx=(0, 11))
        mark.pack_propagate(False)
        ctk.CTkLabel(mark, text=SHOP_NAME[0].upper(),
                     font=("Segoe UI Semibold", 17, "bold"),
                     text_color=COLORS["on_accent"]
                    ).place(relx=0.5, rely=0.5, anchor="center")

        if not narrow:
            brand_text = ctk.CTkFrame(brand, fg_color="transparent")
            brand_text.pack(side="left")
            ctk.CTkLabel(brand_text, text=SHOP_NAME,
                         font=("Segoe UI Semibold", 15, "bold"),
                         text_color=COLORS["text_dark"]).pack(anchor="w")
            ctk.CTkLabel(brand_text, text=f"Billing {APP_VERSION}",
                         font=FONTS["caption"],
                         text_color=COLORS["text_muted"]).pack(anchor="w")

        # -- Collapse / expand toggle -----------------------------
        # Expanded it rides the right edge of the brand row; collapsed there is
        # no room beside the mark, so it sits centred underneath it.
        toggle = ctk.CTkButton(
            sidebar if narrow else brand,
            text="»" if narrow else "«",
            font=("Segoe UI", 16, "bold"),
            width=30, height=30,
            fg_color="transparent",
            hover_color=COLORS["sidebar_hover"],
            text_color=COLORS["sidebar_text"],
            corner_radius=RADII["badge"],
            border_width=0,
            command=self._toggle_sidebar,
        )
        if narrow:
            toggle.pack(pady=(0, 8), padx=(0, SIDEBAR_SCROLLBAR_W))
        else:
            toggle.pack(side="right")
        attach_tooltip(toggle,
                       t("Expand menu" if narrow else "Collapse menu",
                         self.current_lang),
                       side="right" if narrow else "bottom")

        # -- Nav pills — inside a scrollable area so they never overflow on
        # low-res or short screens (mousewheel scrolls the nav list).
        nav_scroll = ctk.CTkScrollableFrame(
            sidebar,
            fg_color="transparent",
            scrollbar_fg_color=COLORS["bg_sidebar"],
            scrollbar_button_color=COLORS["hairline"],
            scrollbar_button_hover_color=COLORS["text_muted"],
            corner_radius=0,
        )
        nav_scroll.pack(fill="both", expand=True, padx=0, pady=0)

        for icon, label, screen, roles in NAV:
            if self.current_role not in roles:
                continue
            text = t(label, self.current_lang)
            btn = ctk.CTkButton(
                nav_scroll,
                text="" if narrow else f"            {text}",
                font=self._nav_font(False),
                fg_color="transparent",
                hover_color=COLORS["sidebar_hover"],
                text_color=COLORS["sidebar_text"],
                anchor="center" if narrow else "w",
                width=METRICS["nav_item"] if narrow else 140,
                height=METRICS["nav_item"],
                corner_radius=RADII["sidebar"],
                border_width=0,
                command=lambda s=screen: self.navigate_to(s),
            )
            if narrow:
                btn.pack(pady=1)
            else:
                btn.pack(fill="x", padx=12, pady=1)
            self.nav_buttons[screen] = btn

            icon_lbl = ctk.CTkLabel(
                btn,
                text=icon,
                font=("Segoe UI", 16),
                text_color=COLORS["sidebar_text"],
                fg_color="transparent"
            )
            if narrow:
                icon_lbl.place(relx=0.5, rely=0.5, anchor="center")
            else:
                icon_lbl.place(x=16, rely=0.5, anchor="w")
            icon_lbl.bind("<Button-1>", lambda e, s=screen: self.navigate_to(s))
            self.nav_icons[screen] = icon_lbl

            if narrow:
                attach_tooltip(btn, text)

        # -- Divider ----------------------------------------------
        ctk.CTkFrame(sidebar, fg_color=COLORS["sidebar_divider"],
                     height=1).pack(
            fill="x",
            padx=(12, 12 + SIDEBAR_SCROLLBAR_W) if narrow else 20,
            pady=(8, 10))

        # -- Signed-in user ---------------------------------------
        # Direction B parks identity on the violet "counts" tint, the one
        # place that hue appears outside a count.
        who = ctk.CTkFrame(sidebar, fg_color="transparent")
        who.pack(fill="x",
                 padx=(0, SIDEBAR_SCROLLBAR_W) if narrow else 20,
                 pady=(0, 8))

        avatar = ctk.CTkFrame(who, fg_color=COLORS["accent_counts_tint"],
                              corner_radius=20, width=40, height=40)
        if narrow:
            avatar.pack()
        else:
            avatar.pack(side="left", padx=(0, 11))
        avatar.pack_propagate(False)
        ctk.CTkLabel(avatar, text=self.current_user["name"][:1].upper(),
                     font=("Segoe UI Semibold", 15, "bold"),
                     text_color=COLORS["accent_counts_fg"]
                    ).place(relx=0.5, rely=0.5, anchor="center")

        role_text = self.current_role.replace("_", " ").title()
        if narrow:
            attach_tooltip(avatar, f"{self.current_user['name']}\n{role_text}")
        else:
            who_text = ctk.CTkFrame(who, fg_color="transparent")
            who_text.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(who_text, text=self.current_user["name"],
                         font=("Segoe UI Semibold", 15, "bold"),
                         text_color=COLORS["text_dark"], anchor="w",
                         justify="left").pack(anchor="w", fill="x")
            ctk.CTkLabel(who_text, text=role_text,
                         font=FONTS["caption"],
                         text_color=COLORS["text_muted"], anchor="w",
                         justify="left").pack(anchor="w", fill="x")

        # -- Sign out ---------------------------------------------
        signout = t("Sign Out", self.current_lang)
        logout_btn = ctk.CTkButton(
            sidebar,
            text="" if narrow else f"            {signout}",
            font=self._nav_font(False),
            fg_color="transparent",
            hover_color=COLORS["accent_danger_tint"],
            text_color=COLORS["accent_danger"],
            anchor="center" if narrow else "w",
            width=METRICS["nav_item"] if narrow else 140,
            height=METRICS["nav_item"],
            corner_radius=RADII["sidebar"],
            border_width=0,
            command=self.logout,
        )
        if narrow:
            logout_btn.pack(pady=(0, 14), padx=(0, SIDEBAR_SCROLLBAR_W))
        else:
            logout_btn.pack(fill="x", padx=12, pady=(0, 14))

        logout_icon = ctk.CTkLabel(
            logout_btn,
            text="🚪",
            font=("Segoe UI", 16),
            text_color=COLORS["accent_danger"],
            fg_color="transparent"
        )
        if narrow:
            logout_icon.place(relx=0.5, rely=0.5, anchor="center")
        else:
            logout_icon.place(x=16, rely=0.5, anchor="w")
        logout_icon.bind("<Button-1>", lambda e: self.logout())

        if narrow:
            attach_tooltip(logout_btn, signout)

        return sidebar

    def _toggle_sidebar(self):
        """Swap the rail between the labelled 236px sidebar and the icon-only one.

        Rebuilds the sidebar frame alone — the content area and every cached
        screen are untouched, so a half-rung bill survives the toggle. The
        active pill is repainted with _paint_nav() rather than by re-navigating,
        which would re-run on_show() and reload the screen under the cashier."""
        self.sidebar_collapsed = not self.sidebar_collapsed
        self.db.set_setting("sidebar_collapsed",
                            "1" if self.sidebar_collapsed else "0")

        if getattr(self, "_sidebar", None) is not None:
            self._sidebar.destroy()
        self._sidebar = self._build_sidebar(self._body)
        self._sidebar.grid(row=0, column=0, sticky="nsew")
        self._paint_nav(getattr(self, "current_screen", "dashboard"))

    def _set_pill(self, btn, icon, is_active):
        """Put a nav pill in its final state, no animation."""
        btn.configure(
            fg_color=COLORS["sidebar_active"] if is_active else "transparent",
            border_width=0,
            hover_color=(COLORS["sidebar_active"] if is_active
                         else COLORS["sidebar_hover"]),
            text_color=(COLORS["on_accent"] if is_active
                        else COLORS["sidebar_text"]),
            font=self._nav_font(is_active),
        )
        if icon is not None:
            # The icon's fg_color must move with the pill. CTkLabel resolves
            # "transparent" against its parent's fill at CREATION time, and
            # these buttons are created transparent on the white sidebar — so
            # an active icon kept a stale white background that covered the
            # glyph entirely.
            icon.configure(
                text_color=COLORS["on_accent"] if is_active
                else COLORS["sidebar_text"],
                fg_color=COLORS["sidebar_active"] if is_active
                else "transparent")

    def _blend_pill(self, btn, icon, is_active):
        """Fade a pill between its resting and active colours.

        "transparent" cannot be interpolated, so the tween runs against the
        sidebar's actual fill and _set_pill() restores the literal token on
        the final frame. Font weight is a discrete change — no curve helps —
        so it is applied up front.
        """
        base, fill = COLORS["bg_sidebar"], COLORS["sidebar_active"]
        ink, on_fill = COLORS["sidebar_text"], COLORS["on_accent"]
        c_from, c_to = (base, fill) if is_active else (fill, base)
        k_from, k_to = (ink, on_fill) if is_active else (on_fill, ink)

        btn.configure(font=self._nav_font(is_active), border_width=0,
                      hover_color=(fill if is_active
                                   else COLORS["sidebar_hover"]))

        def apply(p):
            c = motion.blend(c_from, c_to, p)
            k = motion.blend(k_from, k_to, p)
            btn.configure(fg_color=c, text_color=k)
            if icon is not None:
                icon.configure(fg_color=c, text_color=k)

        motion.tween(btn, MOTION["blend_ms"], apply,
                     on_done=lambda: self._set_pill(btn, icon, is_active))

    def _paint_nav(self, screen_name: str):
        """Mark *screen_name* as the active pill and reset every other one.

        Only the two pills that change are blended; the other eleven are set
        instantly, because animating widgets whose appearance is identical
        before and after is pure cost.
        """
        prev = getattr(self, "current_screen", None)
        for name, btn in self.nav_buttons.items():
            is_active = name == screen_name
            icon = self.nav_icons.get(name)
            if prev != screen_name and name in (prev, screen_name):
                self._blend_pill(btn, icon, is_active)
            else:
                self._set_pill(btn, icon, is_active)


    # ─────────────────────────────────────────────────────────────
    # Navigation
    # ─────────────────────────────────────────────────────────────
    def navigate_to(self, screen_name: str):
        # Enforce role-based access on every navigation, not just the sidebar.
        allowed = getattr(self, "_screen_roles", {}).get(screen_name)
        if allowed is not None and self.current_role not in allowed:
            messagebox.showwarning(
                "Access Denied",
                "You do not have permission to open this screen.",
                parent=self)
            return

        # Let the outgoing screen tear down any floating overlays (e.g. the
        # billing/GRN search-suggestion Toplevels, which otherwise stay on top).
        prev = self.screens.get(getattr(self, "current_screen", None))
        if prev is not None and hasattr(prev, "on_hide"):
            try:
                prev.on_hide()
            except Exception:
                pass

        # Unmap every other cached screen. Tk's focus ring (Tab / Shift-Tab)
        # only skips UNMAPPED widgets, not merely covered ones — a screen left
        # placed-but-hidden under the current one stays fully Tab-reachable.
        # place_forget() unmaps a widget without discarding anything; the
        # target below is re-placed cheaply (and only when it wasn't already
        # placed from a previous visit).
        for name, scr in self.screens.items():
            if name != screen_name and scr.winfo_manager() == "place":
                # A screen navigated away from before its own 160ms slide-in
                # finished still has a live tween ticking via after(). That
                # tween's apply() calls place_configure() on every frame —
                # including its own final one — which silently re-invokes the
                # place geometry manager and re-maps a screen we just forgot.
                # Land it first so nothing is left to resurrect the mapping.
                motion.cancel(scr)
                scr.place_forget()

        self._paint_nav(screen_name)

        if screen_name not in self.screens:
            klasses = {
                "dashboard"   : DashboardScreen,
                "billing"     : BillingScreen,
                "bill_history": BillHistoryScreen,
                "products"    : ProductScreen,
                "categories"  : CategoryScreen,
                "inventory"   : InventoryScreen,
                "suppliers"   : SupplierScreen,
                "purchase"    : PurchaseScreen,
                "customers"   : CustomerScreen,
                "reports"     : ReportScreen,
                "settings"    : SettingsScreen,
                "users"       : UserScreen,
                "activity_log": ActivityLogScreen,
            }
            klass = klasses.get(screen_name)
            if klass is None:
                return
            scr = klass(self.content_area, self.db,
                        self.current_user, self)
            self.screens[screen_name] = scr

        screen = self.screens[screen_name]

        # Screens are placed once and then swapped with lift(). The old
        # pack_forget()/pack() pair forced Tk to relayout the incoming
        # screen's entire widget tree on every visit - 60-125ms of frozen UI
        # per navigation, measured, against ~9ms for on_show()'s DB reload.
        # lift() is a stacking-order change and does no geometry work.
        if screen.winfo_manager() != "place":
            screen.place(x=0, y=0, relwidth=1, relheight=1)

        if hasattr(screen, "on_show"):
            screen.on_show()

        # Park the screen before it is painted, so its first frame is already
        # offset — otherwise Tk paints it home and the slide snaps sideways.
        px = motion.slide_start(screen, MOTION["slide_px"])
        screen.lift()

        # Pay on_show()'s reload and the first repaint here, before a single
        # frame is scheduled, so the slide runs on a clean budget.
        self.update_idletasks()

        motion.slide_home(screen, px, MOTION["slide_ms"])

        self.current_screen = screen_name

    def rebuild_screen(self, screen_name: str):
        """Force rebuild a screen (e.g. after data change)."""
        if screen_name in self.screens:
            self.screens[screen_name].destroy()
            del self.screens[screen_name]
        self.navigate_to(screen_name)

    def apply_language(self, lang: str):
        """Switch UI language: save, rebuild sidebar + current screen."""
        self.current_lang = lang
        self.db.set_setting("app_language", lang)
        # Destroy all cached screens so they rebuild with new language
        current = getattr(self, "current_screen", "dashboard")
        for name, scr in list(self.screens.items()):
            try:
                scr.destroy()
            except Exception:
                pass
        self.screens = {}
        self.nav_buttons = {}
        # Rebuild the entire main window (sidebar + header + content)
        self._build_main_window()

    def apply_theme(self, theme: str):
        """Switch theme: save, set appearance, update config COLORS, update styles, and rebuild UI."""
        self.current_theme = theme
        self.db.set_setting("app_theme", theme)
        ctk.set_appearance_mode(theme)
        
        # Get active mode ("light" or "dark") and update config.COLORS
        from config import apply_theme_mode
        actual_mode = ctk.get_appearance_mode().lower()
        apply_theme_mode(actual_mode)
        
        # Reinitialize styles with new theme colors
        setup_ttk_styles(actual_mode)
        
        # Clear screen cache and nav buttons so widgets are rebuilt with correct colors
        for name, scr in list(self.screens.items()):
            try:
                scr.destroy()
            except Exception:
                pass
        self.screens = {}
        self.nav_buttons = {}
        
        # Rebuild layout
        self._build_main_window()


if __name__ == "__main__":
    app = BillingApp()
    app.mainloop()

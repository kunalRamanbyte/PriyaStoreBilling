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

# The black box goes in before every other import. A missing bundled module
# raises during the imports below, and in the windowed build that used to end
# the process with no window and no message -- the single hardest failure to
# support remotely, because the shopkeeper has nothing to send.
import applog
applog.install()

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
        applog.set_language(self.current_lang)
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
            # Never block close on a backup failure -- but never lose it
            # either. A shop whose closing backup has been failing for weeks
            # has no other way to find out.
            applog.swallow("backup on close", applog.ERROR)

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
                        applog.swallow("refresh last-backup label", applog.DEBUG)
            except Exception:
                applog.swallow("daily auto-backup", applog.ERROR)
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
            self.current_screen = None
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

        Every widget is built ONCE here, in either mode, and the collapsed /
        expanded difference is applied afterwards by _apply_sidebar_mode().
        This used to rebuild the whole rail on every toggle — 13 pills, their
        icons and tooltips, the brand block and the avatar — which froze the
        UI for ~136ms of the ~313ms a collapse cost. Reconfiguring in place is
        the same fix already applied to the Categories card grid."""
        sidebar = ctk.CTkFrame(parent, fg_color=COLORS["bg_sidebar"],
                               corner_radius=0, width=SIDEBAR_WIDTH)
        sidebar.pack_propagate(False)

        self.nav_buttons = {}
        self.nav_icons   = {}
        self._nav_tips   = {}

        NAV = [
            ("\U0001F3E0", "Dashboard",    "dashboard",    ["admin", "cashier", "stock_manager"]),
            ("\U0001F9FE", "New Bill",     "billing",      ["admin", "cashier"]),
            ("\U0001F4CB", "Bill History", "bill_history", ["admin", "cashier", "stock_manager"]),
            ("\U0001F4E6", "Products",     "products",     ["admin", "stock_manager"]),
            ("\U0001F3F7\uFE0F", "Categories",  "categories",   ["admin", "stock_manager"]),
            ("\U0001F4CA", "Inventory",    "inventory",    ["admin", "stock_manager"]),
            ("\U0001F3ED", "Suppliers",    "suppliers",    ["admin", "stock_manager"]),
            ("\U0001F6D2", "Purchase/GRN", "purchase",     ["admin", "stock_manager"]),
            ("\U0001F465", "Customers",    "customers",    ["admin", "cashier"]),
            ("\U0001F4C8", "Reports",      "reports",      ["admin", "stock_manager"]),
            ("\u2699\uFE0F", "Settings",    "settings",     ["admin"]),
            ("\U0001F464", "Users",        "users",        ["admin"]),
            # \U0001F550, not the \U0001F4CB Bill History already owns: with the labels
            # gone, a duplicated glyph is the whole label.
            ("\U0001F550", "Activity Log", "activity_log", ["admin"]),
        ]

        # Authoritative screen->roles map, consulted by navigate_to() so that
        # non-sidebar entry points (dashboard quick actions, resume-draft, etc.)
        # cannot escalate a role past what the sidebar allows.
        self._screen_roles = {key: roles for _, _, key, roles in NAV}
        # English label per screen; _nav_label() runs it through t() so a
        # mode switch re-reads the current language rather than caching it.
        self._screen_labels = {key: label for _, label, key, _ in NAV}

        # -- Brand block ------------------------------------------
        # Mark, wordmark and toggle all live in this one row. The toggle is
        # NOT reparented between modes — Tk cannot reparent — it just switches
        # from packing right to packing below the mark.
        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.pack(fill="x")

        mark = ctk.CTkFrame(brand, fg_color=COLORS["accent_action"],
                            corner_radius=RADII["bubble"],
                            width=METRICS["bubble"], height=METRICS["bubble"])
        mark.pack(side="left", padx=(0, 11))
        mark.pack_propagate(False)
        ctk.CTkLabel(mark, text=SHOP_NAME[0].upper(),
                     font=("Segoe UI Semibold", 17, "bold"),
                     text_color=COLORS["on_accent"]
                    ).place(relx=0.5, rely=0.5, anchor="center")

        brand_text = ctk.CTkFrame(brand, fg_color="transparent")
        brand_text.pack(side="left")
        ctk.CTkLabel(brand_text, text=SHOP_NAME,
                     font=("Segoe UI Semibold", 15, "bold"),
                     text_color=COLORS["text_dark"]).pack(anchor="w")
        ctk.CTkLabel(brand_text, text=f"Billing {APP_VERSION}",
                     font=FONTS["caption"],
                     text_color=COLORS["text_muted"]).pack(anchor="w")

        toggle = ctk.CTkButton(
            brand, text="\u00AB",
            font=("Segoe UI", 16, "bold"),
            width=30, height=30,
            fg_color="transparent",
            hover_color=COLORS["sidebar_hover"],
            text_color=COLORS["sidebar_text"],
            corner_radius=RADII["badge"],
            border_width=0,
            command=self._toggle_sidebar,
        )
        toggle.pack(side="right")
        toggle_tip = attach_tooltip(toggle, "", side="bottom", active=False)

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
                text=f"            {text}",
                font=self._nav_font(False),
                fg_color="transparent",
                hover_color=COLORS["sidebar_hover"],
                text_color=COLORS["sidebar_text"],
                anchor="w",
                width=140,
                height=METRICS["nav_item"],
                corner_radius=RADII["sidebar"],
                border_width=0,
                command=lambda s=screen: self.navigate_to(s),
            )
            btn.pack(fill="x", padx=12, pady=1)
            self.nav_buttons[screen] = btn

            icon_lbl = ctk.CTkLabel(
                btn, text=icon, font=("Segoe UI", 16),
                text_color=COLORS["sidebar_text"], fg_color="transparent")
            icon_lbl.place(x=16, rely=0.5, anchor="w")
            icon_lbl.bind("<Button-1>", lambda e, s=screen: self.navigate_to(s))
            self.nav_icons[screen] = icon_lbl
            self._nav_tips[screen] = attach_tooltip(btn, text, active=False)

        # -- Divider ----------------------------------------------
        divider = ctk.CTkFrame(sidebar, fg_color=COLORS["sidebar_divider"],
                               height=1)
        divider.pack(fill="x", padx=20, pady=(8, 10))

        # -- Signed-in user ---------------------------------------
        # Direction B parks identity on the violet "counts" tint, the one
        # place that hue appears outside a count.
        who = ctk.CTkFrame(sidebar, fg_color="transparent")
        who.pack(fill="x", padx=20, pady=(0, 8))

        avatar = ctk.CTkFrame(who, fg_color=COLORS["accent_counts_tint"],
                              corner_radius=20, width=40, height=40)
        avatar.pack(side="left", padx=(0, 11))
        avatar.pack_propagate(False)
        ctk.CTkLabel(avatar, text=self.current_user["name"][:1].upper(),
                     font=("Segoe UI Semibold", 15, "bold"),
                     text_color=COLORS["accent_counts_fg"]
                    ).place(relx=0.5, rely=0.5, anchor="center")

        role_text = self.current_role.replace("_", " ").title()
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
        avatar_tip = attach_tooltip(
            avatar, f"{self.current_user['name']}\n{role_text}", active=False)

        # -- Sign out ---------------------------------------------
        signout = t("Sign Out", self.current_lang)
        logout_btn = ctk.CTkButton(
            sidebar,
            text=f"            {signout}",
            font=self._nav_font(False),
            fg_color="transparent",
            hover_color=COLORS["accent_danger_tint"],
            text_color=COLORS["accent_danger"],
            anchor="w",
            width=140,
            height=METRICS["nav_item"],
            corner_radius=RADII["sidebar"],
            border_width=0,
            command=self.logout,
        )
        logout_btn.pack(fill="x", padx=12, pady=(0, 14))

        logout_icon = ctk.CTkLabel(
            logout_btn, text="\U0001F6AA", font=("Segoe UI", 16),
            text_color=COLORS["accent_danger"], fg_color="transparent")
        logout_icon.place(x=16, rely=0.5, anchor="w")
        logout_icon.bind("<Button-1>", lambda e: self.logout())
        logout_tip = attach_tooltip(logout_btn, signout, active=False)

        # Everything the mode switch needs to reach, so _apply_sidebar_mode()
        # never has to walk the widget tree looking for it.
        self._sb = {
            "sidebar": sidebar, "brand": brand, "mark": mark,
            "nav_scroll": nav_scroll,
            "brand_text": brand_text, "toggle": toggle,
            "toggle_tip": toggle_tip, "divider": divider,
            "who": who, "avatar": avatar, "who_text": who_text,
            "avatar_tip": avatar_tip, "logout_btn": logout_btn,
            "logout_icon": logout_icon, "logout_tip": logout_tip,
            "signout_text": signout,
        }
        self._apply_sidebar_mode()
        return sidebar

    def _apply_sidebar_mode(self):
        """Switch the existing rail between labelled and icon-only.

        Reconfigures in place — no widget is created or destroyed — because
        rebuilding the rail cost ~136ms of frozen UI on every toggle.

        Everything is re-packed with pack(), never pack_configure(), and in
        explicit order. CustomTkinter scales padx/pady by the widget-scaling
        factor inside pack() but NOT inside pack_configure(), so a
        pack_configure(padx=16) lands 16 RAW pixels where pack(padx=16) lands
        21 — which pushed the pills ~2px off every other block's centre.
        pack() re-appends to the parent's pack order, so each parent's
        children are re-packed top to bottom in one pass."""
        sb = getattr(self, "_sb", None)
        if not sb:
            return
        narrow = self.sidebar_collapsed
        pad_r = SIDEBAR_SCROLLBAR_W      # the scrollbar column the nav reserves

        sb["sidebar"].configure(
            width=SIDEBAR_WIDTH_COLLAPSED if narrow else SIDEBAR_WIDTH)

        # -- Brand row: mark, wordmark, toggle --------------------
        sb["mark"].pack_forget()
        sb["brand_text"].pack_forget()
        sb["toggle"].pack_forget()
        if narrow:
            sb["mark"].pack(side="top")
            sb["toggle"].pack(side="top", pady=(8, 0))
        else:
            sb["mark"].pack(side="left", padx=(0, 11))
            sb["brand_text"].pack(side="left")
            sb["toggle"].pack(side="right")

        sb["toggle"].configure(text="\u00BB" if narrow else "\u00AB")
        sb["toggle_tip"].text = t("Expand menu" if narrow else "Collapse menu",
                                  self.current_lang)
        sb["toggle_tip"].side = "right" if narrow else "bottom"

        # -- Nav pills --------------------------------------------
        for screen, btn in self.nav_buttons.items():
            label = self._nav_label(screen)
            btn.configure(
                text="" if narrow else f"            {label}",
                anchor="center" if narrow else "w",
                width=METRICS["nav_item"] if narrow else 140)
            btn.pack_forget()
            if narrow:
                btn.pack(pady=1)
            else:
                btn.pack(fill="x", padx=12, pady=1)

            icon = self.nav_icons.get(screen)
            if icon is not None:
                icon.place_forget()
                if narrow:
                    icon.place(relx=0.5, rely=0.5, anchor="center")
                else:
                    icon.place(x=16, rely=0.5, anchor="w")
                # The btn.configure() above makes CustomTkinter re-draw the
                # button's own canvas and text label. Those are SIBLINGS of
                # this icon, and the redraw raises them above it -- so after
                # one collapse/expand the icon was still the right size, in
                # the right place, the right colour and mapped, and simply
                # painted over. Re-placing does not restore the stacking
                # order; only lift() does.
                icon.lift()
            tip = self._nav_tips.get(screen)
            if tip is not None:
                tip.text = label
                tip.set_active(narrow)

        # -- Identity block: avatar, name+role --------------------
        sb["avatar"].pack_forget()
        sb["who_text"].pack_forget()
        if narrow:
            sb["avatar"].pack(side="top")
        else:
            sb["avatar"].pack(side="left", padx=(0, 11))
            sb["who_text"].pack(side="left", fill="x", expand=True)
        sb["avatar_tip"].set_active(narrow)

        # -- Sign out ---------------------------------------------
        signout = sb["signout_text"]
        sb["logout_btn"].configure(
            text="" if narrow else f"            {signout}",
            anchor="center" if narrow else "w",
            width=METRICS["nav_item"] if narrow else 140)
        sb["logout_icon"].place_forget()
        if narrow:
            sb["logout_icon"].place(relx=0.5, rely=0.5, anchor="center")
        else:
            sb["logout_icon"].place(x=16, rely=0.5, anchor="w")
        sb["logout_icon"].lift()          # same burial as the nav icons above
        sb["logout_tip"].set_active(narrow)

        # -- Re-pack the rail's own children, top to bottom -------
        # pack() appends, so the whole column is re-packed in one ordered
        # pass rather than each block trying to hold its place.
        for w in (sb["brand"], sb["nav_scroll"], sb["divider"],
                  sb["who"], sb["logout_btn"]):
            w.pack_forget()
        sb["brand"].pack(fill="x",
                         padx=(0, pad_r) if narrow else 20,
                         pady=(18, 10) if narrow else (18, 14))
        sb["nav_scroll"].pack(fill="both", expand=True, padx=0, pady=0)
        sb["divider"].pack(fill="x",
                           padx=(12, 12 + pad_r) if narrow else 20,
                           pady=(8, 10))
        sb["who"].pack(fill="x",
                       padx=(0, pad_r) if narrow else 20,
                       pady=(0, 8))
        if narrow:
            sb["logout_btn"].pack(pady=(0, 14), padx=(0, pad_r))
        else:
            sb["logout_btn"].pack(fill="x", padx=12, pady=(0, 14))

    def _nav_label(self, screen):
        """The translated label a pill carries when the rail is expanded."""
        return t(self._screen_labels.get(screen, screen), self.current_lang)

    def _toggle_sidebar(self):
        """Swap the rail between the labelled sidebar and the icon-only one.

        Reconfigures the existing widgets rather than rebuilding them. The
        rebuild cost ~136ms of frozen UI per toggle on top of the layout pass
        the width change forces; the rail is the same 13 pills either way, so
        there was never anything to rebuild."""
        self.sidebar_collapsed = not self.sidebar_collapsed
        self.db.set_setting("sidebar_collapsed",
                            "1" if self.sidebar_collapsed else "0")
        self._apply_sidebar_mode()
        # prev == screen_name here, so _paint_nav takes its instant
        # all-pills path — a mode switch must not animate.
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

        Only the two pills that change are blended; the other eleven are
        touched not at all, because animating (or even re-configuring)
        widgets whose appearance is identical before and after is pure cost.
        Measured: 23.4ms for a full 13-pill `_set_pill` pass, 1.4ms for the
        2 pills that actually transition — repainting the untouched eleven
        was roughly half the cost of a navigation for zero visible change.

        `_paint_nav` is also called from `_toggle_sidebar()` after the whole
        sidebar has been rebuilt from scratch, where every pill is a brand
        new widget that has never been painted — there `prev == screen_name`
        (the current screen is being repainted, not navigated away from), so
        every pill must be set. The very first navigation after login, when
        no pill has ever been painted (`prev is None`), is handled the same
        way.
        """
        prev = getattr(self, "current_screen", None)
        if prev is None or prev == screen_name:
            for name, btn in self.nav_buttons.items():
                self._set_pill(btn, self.nav_icons.get(name), name == screen_name)
            return

        # A real navigation: only the outgoing and incoming pills change
        # state, and both already take the blend path. The other eleven
        # need nothing — skip them entirely rather than just skipping the
        # animation on them.
        for name in (prev, screen_name):
            btn = self.nav_buttons.get(name)
            if btn is None:
                continue
            self._blend_pill(btn, self.nav_icons.get(name), name == screen_name)


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
                applog.swallow(f"on_hide for screen {self.current_screen!r}")

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

        # Building the screen is the expensive half of a first visit —
        # 100-800ms of Tcl round-trips, measured. Remember whether we paid it
        # here, because the slide below depends on it.
        just_built = screen_name not in self.screens
        if just_built:
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
        #
        # A screen built on THIS visit does not slide at all. Its constructor
        # has just spent 100-800ms (Settings 534ms, Categories 357ms) and
        # whatever repaint work spills past the update_idletasks() below then
        # lands on the animation's opening frames — measured as gaps of
        # 25-146ms against a 16ms budget, on first visits and nowhere else.
        # Animating over that reads as a stutter, so the first visit gets a
        # clean cut and every revisit (median 26ms) still slides.
        # slide_home() with px=0 places the screen home without a tween.
        px = 0 if just_built else motion.slide_start(screen, MOTION["slide_px"])
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
        applog.set_language(lang)
        self.db.set_setting("app_language", lang)
        # Destroy all cached screens so they rebuild with new language
        current = getattr(self, "current_screen", "dashboard")
        # _paint_nav() blends FROM current_screen — leaving it set to the
        # Settings screen this rebuild is driven from would blend the freshly
        # rebuilt (transparent) Settings pill away from sidebar_active on the
        # next navigate_to(), instead of painting it plainly.
        self.current_screen = None
        for name, scr in list(self.screens.items()):
            try:
                scr.destroy()
            except Exception:
                applog.swallow(f"destroy screen {name!r} on rebuild", applog.DEBUG)
        self.screens = {}
        self.nav_buttons = {}
        # Rebuild the entire main window (sidebar + header + content)
        self._build_main_window()

    def apply_theme(self, theme: str):
        """Switch theme: save, set appearance, update config COLORS, update styles, and rebuild UI."""
        self.current_theme = theme
        self.db.set_setting("app_theme", theme)

        # Park focus on the root BEFORE the appearance change, not after.
        #
        # On Windows CustomTkinter recolours the title bar by withdrawing and
        # re-showing the root window. It captures focus_get() first, then
        # schedules `after(1, widget.focus)` to put focus back
        # (ctk_tk.py::_windows_set_titlebar_color). The rebuild below destroys
        # every cached screen -- so a cashier who switched theme with the
        # cursor in a POS field left that 1ms timer holding a destroyed widget:
        #   TclError: bad window path name "...!billingscreen...!ctkentry.!entry"
        # Handing CustomTkinter the root gives it a widget that still exists
        # when the timer fires. apply_language() needs none of this: it runs
        # the same destroy loop but never touches the appearance mode.
        try:
            self.focus_set()
        except Exception:
            applog.swallow("park focus before theme rebuild", applog.DEBUG)

        ctk.set_appearance_mode(theme)
        
        # Get active mode ("light" or "dark") and update config.COLORS
        from config import apply_theme_mode
        actual_mode = ctk.get_appearance_mode().lower()
        apply_theme_mode(actual_mode)
        
        # Reinitialize styles with new theme colors
        setup_ttk_styles(actual_mode)

        # Clear screen cache and nav buttons so widgets are rebuilt with correct colors
        # _paint_nav() blends FROM current_screen — leaving it set to the
        # Settings screen this rebuild is driven from would blend the freshly
        # rebuilt (transparent) Settings pill away from sidebar_active on the
        # next navigate_to(), instead of painting it plainly.
        self.current_screen = None
        for name, scr in list(self.screens.items()):
            try:
                scr.destroy()
            except Exception:
                applog.swallow(f"destroy screen {name!r} on rebuild", applog.DEBUG)
        self.screens = {}
        self.nav_buttons = {}
        
        # Rebuild layout
        self._build_main_window()


if __name__ == "__main__":
    # One till per database. A second copy cannot mint a duplicate bill number
    # -- _claim_number() already guarantees that inside BEGIN IMMEDIATE -- but
    # it CAN overwrite the file during a Restore, and it can commit into the
    # WAL while the other copy is taking a backup, producing a backup that
    # silently omits those bills. See single_instance.py.
    #
    # This lives inside __main__ on purpose: every verify_*.py builds
    # BillingApp directly, and a claim taken at import time would make the
    # test suites fight each other.
    import single_instance
    from config import DB_PATH

    if not single_instance.acquire(DB_PATH):
        applog.log.info("second instance refused; database already open")
        if not single_instance.focus_existing(f"{APP_TITLE}   v{APP_VERSION}"):
            # Nothing to raise -- the owner may still be starting up. Say so
            # rather than exiting silently, which reads as "the icon is broken".
            _lang = "English"
            try:
                _lang = Database().get_setting("app_language", "English")
            except Exception:
                applog.swallow("read language for the already-running notice",
                               applog.DEBUG)
            messagebox.showinfo(APP_TITLE,
                                t("Priya Store is already running.", _lang))
        sys.exit(0)

    app = BillingApp()
    app.mainloop()
    applog.log.info("clean exit")

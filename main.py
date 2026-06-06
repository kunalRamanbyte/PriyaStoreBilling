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

from config import (COLORS, FONTS, RADII, APP_TITLE, SHOP_NAME,
                    WINDOW_WIDTH, WINDOW_HEIGHT, SIDEBAR_WIDTH, resource_path)
from database import Database
from lang import t
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
        self.screens      = {}
        self.nav_buttons  = {}

        setup_ttk_styles()              # register all ttk styles once
        self._setup_window()
        self._show_login()
        self._schedule_daily_backup()   # start 24-hour backup timer

    # ─────────────────────────────────────────────────────────────
    # Window setup
    # ─────────────────────────────────────────────────────────────
    def _setup_window(self):
        self.title(APP_TITLE)

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
            self._show_login()

    # ─────────────────────────────────────────────────────────────
    # Main window (sidebar + content)
    # ─────────────────────────────────────────────────────────────
    def _build_main_window(self):
        for w in self.winfo_children():
            w.destroy()

        self._build_header()

        body = ctk.CTkFrame(self, fg_color=COLORS["bg_main"], corner_radius=0)
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        sidebar = self._build_sidebar(body)
        sidebar.grid(row=0, column=0, sticky="nsew")

        self.content_area = ctk.CTkFrame(body, fg_color=COLORS["bg_main"],
                                          corner_radius=0)
        self.content_area.grid(row=0, column=1, sticky="nsew")

        self.navigate_to("dashboard")

    def _build_header(self):
        """Modern frosted-glass header with gradient accent."""
        hdr = ctk.CTkFrame(self, fg_color=COLORS["bg_header"],
                            corner_radius=0, height=64)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        # Gradient accent line at bottom (simulated with layered frames)
        accent_outer = ctk.CTkFrame(hdr, fg_color=COLORS["btn_primary"],
                                     corner_radius=0, height=3)
        accent_outer.pack(side="bottom", fill="x")

        ctk.CTkLabel(
            hdr, text="🛒  Priya Store",
            font=("Segoe UI Semibold", 19, "bold"),
            text_color=COLORS["text_dark"],
        ).pack(side="left", padx=28, pady=14)

        # User badge — modern pill with glass effect
        user_badge = ctk.CTkFrame(hdr, fg_color=COLORS["btn_primary"],
                                   corner_radius=18,
                                   border_width=2,
                                   border_color=COLORS["glass_glow"])
        user_badge.pack(side="right", padx=24, pady=13)
        ctk.CTkLabel(
            user_badge,
            text=f"  👤  {self.current_user['name']}  •  {self.current_role.title()}  ",
            font=FONTS["small_bold"],
            text_color="white",
        ).pack(padx=10, pady=5)

    def _build_sidebar(self, parent):
        """Modern dark-navy glassmorphic sidebar with glow active states."""
        sidebar = ctk.CTkFrame(parent, fg_color=COLORS["bg_sidebar"],
                                corner_radius=0, width=SIDEBAR_WIDTH)
        sidebar.pack_propagate(False)

        # Draw dynamic royal-blue-to-navy-blue gradient on sidebar
        sidebar_canvas = tk.Canvas(sidebar, borderwidth=0, highlightthickness=0)
        sidebar_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        def _draw_sidebar_grad(event):
            sidebar_canvas.delete("grad")
            w, h = event.width, event.height
            if w <= 1 or h <= 1:
                return
            # Gorgeous vertical blue gradient (deep royal blue -> dark navy blue)
            r1, g1, b1 = 30, 58, 138    # #1E3A8A
            r2, g2, b2 = 15, 23, 42     # #0F172A
            for y in range(h):
                t = y / h
                r = int(r1 + (r2 - r1) * t)
                g = int(g1 + (g2 - g1) * t)
                b = int(b1 + (b2 - b1) * t)
                sidebar_canvas.create_line(0, y, w, y, fill=f"#{r:02x}{g:02x}{b:02x}", tags="grad")

        sidebar_canvas.bind("<Configure>", _draw_sidebar_grad)

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
            ("📋", "Activity Log", "activity_log", ["admin"]),
        ]

        # ── App brand block (premium) ────────────────────
        brand = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand.pack(fill="x", padx=18, pady=(12, 6)) # Reduced padding to fit small screens

        # Glow circle behind icon
        icon_frame = ctk.CTkFrame(brand, fg_color=COLORS["sidebar_active"],
                                   corner_radius=22, width=44, height=44,
                                   border_width=2, border_color=COLORS["sidebar_glow"])
        icon_frame.pack(side="left", padx=(0, 12))
        icon_frame.pack_propagate(False)
        ctk.CTkLabel(icon_frame, text="🛒",
                     font=("Segoe UI", 20), text_color=COLORS["sidebar_accent"]
                    ).place(relx=0.5, rely=0.5, anchor="center")

        brand_text = ctk.CTkFrame(brand, fg_color="transparent")
        brand_text.pack(side="left")
        ctk.CTkLabel(brand_text, text="FMCG Billing",
                     font=("Segoe UI Semibold", 16, "bold"),
                     text_color="#F1F5F9").pack(anchor="w")
        ctk.CTkLabel(brand_text, text="v1.0  •  Modern",
                     font=FONTS["caption"],
                     text_color="#475569").pack(anchor="w")

        # Divider
        ctk.CTkFrame(sidebar, fg_color=COLORS["sidebar_divider"],
                     height=1).pack(fill="x", padx=18, pady=(0, 10))

        # ── Nav buttons — inside a scrollable area so they never overflow
        # on low-res or short screens (mousewheel scrolls the nav list).
        nav_scroll = ctk.CTkScrollableFrame(
            sidebar,
            fg_color="transparent",
            scrollbar_fg_color=COLORS["bg_sidebar"],
            scrollbar_button_color=COLORS["sidebar_hover"],
            scrollbar_button_hover_color=COLORS["sidebar_active"],
            corner_radius=0,
        )
        nav_scroll.pack(fill="both", expand=True, padx=0, pady=0)

        for icon, label, screen, roles in NAV:
            if self.current_role not in roles:
                continue
            btn = ctk.CTkButton(
                nav_scroll,
                text=f"          {t(label, self.current_lang)}",
                font=FONTS["sidebar"],
                fg_color="transparent",
                hover_color=COLORS["sidebar_hover"],
                text_color=COLORS["sidebar_text"],
                anchor="w",
                height=38,
                corner_radius=RADII["sidebar"],
                command=lambda s=screen: self.navigate_to(s),
            )
            btn.pack(fill="x", padx=12, pady=1)
            self.nav_buttons[screen] = btn

            icon_lbl = ctk.CTkLabel(
                btn,
                text=icon,
                font=("Segoe UI", 16),
                text_color=COLORS["sidebar_text"],
                fg_color="transparent"
            )
            icon_lbl.place(x=16, rely=0.5, anchor="w")
            icon_lbl.bind("<Button-1>", lambda e, s=screen: self.navigate_to(s))

        # ── Logout ───────────────────────────────────
        ctk.CTkFrame(sidebar, fg_color=COLORS["sidebar_divider"],
                     height=1).pack(fill="x", padx=18, pady=(0, 6))

        logout_btn = ctk.CTkButton(
            sidebar,
            text=f"          {t('Sign Out', self.current_lang)}",
            font=FONTS["sidebar"],
            fg_color="transparent",
            hover_color=COLORS["btn_danger"],
            text_color=COLORS["sidebar_text"],
            anchor="w",
            height=38,                         # Compacted height
            corner_radius=RADII["sidebar"],
            command=self.logout,
        )
        logout_btn.pack(fill="x", padx=12, pady=(2, 6)) # Aligned and reduced padding

        logout_icon = ctk.CTkLabel(
            logout_btn,
            text="🚪",
            font=("Segoe UI", 16),
            text_color=COLORS["sidebar_text"],
            fg_color="transparent"
        )
        logout_icon.place(x=16, rely=0.5, anchor="w")
        logout_icon.bind("<Button-1>", lambda e: self.logout())

        return sidebar

    # ─────────────────────────────────────────────────────────────
    # Navigation
    # ─────────────────────────────────────────────────────────────
    def navigate_to(self, screen_name: str):
        for name, btn in self.nav_buttons.items():
            is_active = name == screen_name
            btn.configure(
                fg_color=COLORS["sidebar_active"] if is_active else "transparent",
                border_width=2 if is_active else 0,
                border_color=COLORS["sidebar_glow"] if is_active else COLORS["bg_sidebar"],
                text_color="#FFFFFF" if is_active else COLORS["sidebar_text"],
            )

        for w in self.content_area.winfo_children():
            w.pack_forget()
            w.place_forget()

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

        # 1. Cache old screens
        old_screens = [w for w in self.content_area.winfo_children() if w != screen]

        # 2. Unpack old screens
        for w in old_screens:
            w.pack_forget()
            w.place_forget()

        # 3. Pack target screen instantly (single atomic redraw)
        screen.pack(fill="both", expand=True)

        if hasattr(screen, "on_show"):
            screen.on_show()

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


if __name__ == "__main__":
    app = BillingApp()
    app.mainloop()

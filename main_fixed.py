"""
main.py — Kunal's FMCG Grocery Billing System
Phase 1+2+3: Login • Dashboard • POS Billing • Bill History • Products • Categories
             Inventory • Suppliers • Purchase/GRN • Customers • Reports

Run:  python main.py
Login: admin / admin123  (cashier: cashier / cash123)
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

# Set theme BEFORE importing screens
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

from config import (COLORS, FONTS, APP_TITLE, SHOP_NAME,
                    WINDOW_WIDTH, WINDOW_HEIGHT, SIDEBAR_WIDTH)
from database import Database
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


class BillingApp(ctk.CTk):
    """Main application window — manages navigation between screens."""

    def __init__(self):
        super().__init__()
        self.db           = Database()
        self.db.init_db()
        self.current_user = None
        self.current_role = None
        self.screens      = {}
        self.nav_buttons  = {}

        self._setup_window()
        self._show_login()

    # ─────────────────────────────────────────────────────────────
    # Window setup
    # ─────────────────────────────────────────────────────────────
    def _setup_window(self):
        self.title(APP_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(1100, 680)
        self.configure(fg_color=COLORS["bg_main"])
        self._center_window()

        # Window close confirmation
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _center_window(self):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x  = (sw - WINDOW_WIDTH)  // 2
        y  = (sh - WINDOW_HEIGHT) // 2
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

    def _on_close(self):
        if messagebox.askyesno("Exit", "Exit the billing system?"):
            self.destroy()

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
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
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

        # ── Top header bar ────────────────────────────────────
        self._build_header()

        # ── Body (sidebar | content) ──────────────────────────
        body = ctk.CTkFrame(self, fg_color=COLORS["bg_main"], corner_radius=0)
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        sidebar = self._build_sidebar(body)
        sidebar.grid(row=0, column=0, sticky="nsew")

        self.content_area = ctk.CTkFrame(body, fg_color=COLORS["bg_main"], corner_radius=0)
        self.content_area.grid(row=0, column=1, sticky="nsew")

        self.navigate_to("dashboard")

    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color=COLORS["bg_header"],
                            corner_radius=0, height=58)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        # Shop name
        ctk.CTkLabel(
            hdr, text=f"🛒   {SHOP_NAME}",
            font=("Segoe UI", 18, "bold"),
            text_color="white"
        ).pack(side="left", padx=24, pady=10)

        # Logged-in user badge
        ctk.CTkLabel(
            hdr,
            text=f"👤  {self.current_user['name']}  [{self.current_role.title()}]",
            font=FONTS["body"],
            text_color="#E3F2FD"
        ).pack(side="right", padx=24)

    def _build_sidebar(self, parent):
        sidebar = ctk.CTkFrame(parent, fg_color=COLORS["bg_sidebar"],
                                corner_radius=0, width=SIDEBAR_WIDTH)
        sidebar.pack_propagate(False)

        # Nav items: (emoji, label, screen, allowed_roles)
        NAV = [
            ("🏠", "Dashboard",    "dashboard",    ["admin", "cashier", "stock_manager"]),
            ("🧾", "New Bill",     "billing",      ["admin", "cashier"]),
            ("📋", "Bill History", "bill_history", ["admin", "cashier", "stock_manager"]),
            ("📦", "Products",     "products",     ["admin", "stock_manager"]),
            ("🏷️","Categories",   "categories",   ["admin", "stock_manager"]),
            ("📊", "Inventory",    "inventory",    ["admin", "stock_manager"]),
            ("🏭", "Suppliers",    "suppliers",    ["admin", "stock_manager"]),
            ("🛒", "Purchase/GRN", "purchase",     ["admin", "stock_manager"]),
            ("👥", "Customers",    "customers",    ["admin", "cashier"]),
            ("📈", "Reports",      "reports",      ["admin", "stock_manager"]),
        ]

        # App label
        ctk.CTkFrame(sidebar, fg_color="transparent", height=14).pack()
        ctk.CTkLabel(sidebar, text="BILLING\nSYSTEM",
                     font=("Segoe UI", 13, "bold"),
                     text_color=COLORS["sidebar_accent"],
                     justify="center").pack(pady=(2, 10))
        ctk.CTkFrame(sidebar, fg_color="#3949AB", height=1).pack(fill="x", padx=14)
        ctk.CTkFrame(sidebar, fg_color="transparent", height=8).pack()

        for icon, label, screen, roles in NAV:
            if self.current_role not in roles:
                continue
            btn = ctk.CTkButton(
                sidebar,
                text=f"  {icon}   {label}",
                font=FONTS["sidebar"],
                fg_color="transparent",
                hover_color=COLORS["sidebar_hover"],
                text_color=COLORS["sidebar_text"],
                anchor="w",
                height=48,
                corner_radius=8,
                command=lambda s=screen: self.navigate_to(s),
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[screen] = btn

        # Spacer
        ctk.CTkFrame(sidebar, fg_color="transparent").pack(fill="y", expand=True)

        # Phase label
        ctk.CTkLabel(sidebar, text="Phase 3 — Customers & Reports",
                     font=FONTS["sidebar_sm"],
                     text_color="#5C6BC0").pack(pady=(4, 4))
        ctk.CTkFrame(sidebar, fg_color="#3949AB", height=1).pack(fill="x", padx=14)

        # Logout
        ctk.CTkButton(
            sidebar,
            text="  🚪   Logout",
            font=FONTS["sidebar"],
            fg_color="transparent",
            hover_color="#B71C1C",
            text_color=COLORS["sidebar_text"],
            anchor="w",
            height=48,
            corner_radius=8,
            command=self.logout,
        ).pack(fill="x", padx=10, pady=10)

        return sidebar

    # ─────────────────────────────────────────────────────────────
    # Navigation
    # ─────────────────────────────────────────────────────────────
    def navigate_to(self, screen_name: str):
        # Highlight active nav button
        for name, btn in self.nav_buttons.items():
            btn.configure(
                fg_color=COLORS["sidebar_active"] if name == screen_name
                         else "transparent"
            )

        # Hide all current content
        for w in self.content_area.winfo_children():
            w.pack_forget()

        # Build screen on first visit
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
            }
            klass = klasses.get(screen_name)
            if klass:
                self.screens[screen_name] = klass(
                    self.content_area, self.db, self.current_user, self
                )

        if screen_name in self.screens:
            screen = self.screens[screen_name]
            screen.pack(fill="both", expand=True)
            if hasattr(screen, "on_show"):
                screen.on_show()


    def refresh_screen(self, screen_name: str):
        """Force rebuild a screen (e.g. after data change)."""
        if screen_name in self.screens:
            self.screens[screen_name].destroy()
            del self.screens[screen_name]
        self.navigate_to(screen_name)


# --- Entry point ---
if __name__ == "__main__":
    app = BillingApp()
    app.mainloop()

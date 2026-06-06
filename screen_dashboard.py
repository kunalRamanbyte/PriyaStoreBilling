"""
screen_dashboard.py — Dashboard/Home screen
Shows today's sales KPIs, low-stock alert, recent bills, quick-action buttons.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from config import COLORS, FONTS
from lang import t


class DashboardScreen(ctk.CTkFrame):
    def __init__(self, parent, db, current_user, app):
        super().__init__(parent, fg_color=COLORS["bg_main"], corner_radius=0)
        self.db = db
        self.current_user = current_user
        self.app = app
        self._build()

    def _build(self):
        # ── Page header ──────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, text=f"🏠  {t('Dashboard', self.app.current_lang)}",
            font=FONTS["heading"], text_color=COLORS["text_dark"]
        ).pack(side="left", padx=25, pady=15)
        ctk.CTkFrame(header, fg_color=COLORS["glass_border"],
                     corner_radius=0, height=1).pack(side="bottom", fill="x")

        # Date/time
        self.dt_label = ctk.CTkLabel(
            header, text="", font=FONTS["small"], text_color=COLORS["text_muted"]
        )
        self.dt_label.pack(side="right", padx=25)
        self._update_clock()

        # ── Scrollable body ──────────────────────────────────
        body = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_main"], corner_radius=0)
        body.pack(fill="both", expand=True, padx=20, pady=10)

        # ── KPI Cards Row ────────────────────────────────────
        kpi_row = ctk.CTkFrame(body, fg_color="transparent")
        kpi_row.pack(fill="x", pady=(0, 16))

        L = self.app.current_lang
        self.kpi_sales   = self._kpi_card(kpi_row, "💰", t("Today's Sales", L),    "₹ 0.00", COLORS["kpi_blue"])
        self.kpi_bills   = self._kpi_card(kpi_row, "🧾", t("Bills Today", L),      "0",      COLORS["kpi_green"])
        self.kpi_low     = self._kpi_card(kpi_row, "⚠️",  t("Low Stock Items", L),  "0",      COLORS["kpi_red"])
        self.kpi_expiry  = self._kpi_card(kpi_row, "📅", t("Expiring (30 days)", L),"0",     COLORS["kpi_orange"])
        self.kpi_disc    = self._kpi_card(kpi_row, "🏷️", t("Discount Given", L),   "₹ 0.00", COLORS["kpi_purple"])

        for card in (self.kpi_sales, self.kpi_bills, self.kpi_low, self.kpi_expiry, self.kpi_disc):
            card.pack(side="left", fill="x", expand=True, padx=6)

        # ── Quick Actions ────────────────────────────────────
        ctk.CTkLabel(body, text=t("Quick Actions", L),
                     font=FONTS["subheading"], text_color=COLORS["text_dark"]
                    ).pack(anchor="w", pady=(0, 8))

        qa_row = ctk.CTkFrame(body, fg_color="transparent")
        qa_row.pack(fill="x", pady=(0, 16))

        actions = [
            (t("New Bill_qa", L),       COLORS["btn_primary"],  COLORS["btn_primary_h"], "billing"),
            (t("Add Product_qa", L),    COLORS["btn_success"],  COLORS["btn_success_h"], "products"),
            (t("Bill History_qa", L),   COLORS["btn_purple"],   COLORS["btn_purple_h"], "bill_history"),
            (t("Categories_qa", L),    COLORS["btn_warning"],  COLORS["btn_warning_h"], "categories"),
        ]
        for text, fg, hov, screen in actions:
            ctk.CTkButton(
                qa_row, text=text,
                font=FONTS["button"],
                fg_color=fg, hover_color=hov,
                text_color="white",
                height=84, corner_radius=20,
                border_width=2, border_color=COLORS["glass_glow"],
                command=lambda s=screen: self.app.navigate_to(s)
            ).pack(side="left", fill="x", expand=True, padx=6)

        # ── Expiry Alert Panel ───────────────────────────────
        self.expiry_frame = ctk.CTkFrame(body, fg_color="#FFF4E6", corner_radius=16)
        # shown/hidden dynamically in _load_data

        expiry_hdr = ctk.CTkFrame(self.expiry_frame, fg_color="transparent")
        expiry_hdr.pack(fill="x", padx=14, pady=(10, 4))
        ctk.CTkLabel(expiry_hdr, text=f"📅  {t('Products Expiring Within 30 Days', L)}",
                     font=FONTS["subheading"], text_color="#E65100"
                    ).pack(side="left")

        # Exp.Treeview style registered globally in styles.py
        exp_cols = ("name", "category", "stock", "expiry_date", "days_left")
        self.exp_tree = ttk.Treeview(
            self.expiry_frame, columns=exp_cols, show="headings",
            height=6, style="Exp.Treeview", selectmode="none"
        )
        for col, head, w in zip(
            exp_cols,
            (t("Product Name", L), t("Category", L), t("Stock", L), t("Expiry Date", L), t("Days Left", L)),
            (240, 130, 70, 110, 90)
        ):
            self.exp_tree.heading(col, text=head)
            self.exp_tree.column(col, width=w, anchor="w" if col in ("name","category") else "center")
        self.exp_tree.tag_configure("expired",  background="#FFEBEE")
        self.exp_tree.tag_configure("expiring", background="#FFF8E1")
        self.exp_tree.pack(fill="x", padx=10, pady=(0, 10))

        # ── Recent Bills table ───────────────────────────────
        self._recent_bills_label = ctk.CTkLabel(body, text=t("Recent Bills", L),
                     font=FONTS["subheading"], text_color=COLORS["text_dark"])
        self._recent_bills_label.pack(anchor="w", pady=(0, 6))

        tbl_frame = ctk.CTkFrame(body, fg_color=COLORS["bg_card"], corner_radius=20,
                                  border_width=2, border_color=COLORS["glass_border"])
        tbl_frame.pack(fill="x")

        # Styles registered globally in styles.py
        cols = ("bill_number", "date_time", "customer", "amount", "mode", "status")
        self.recent_tree = ttk.Treeview(
            tbl_frame, columns=cols, show="headings",
            height=10, style="Dash.Treeview", selectmode="browse"
        )
        heads = (t("Bill No.", L), t("Date & Time", L), t("Customer", L),
                 t("Amount (₹)", L), t("Mode", L), t("Status", L))
        widths = (110, 160, 180, 110, 90, 80)
        for col, head, w in zip(cols, heads, widths):
            self.recent_tree.heading(col, text=head)
            anchor = "e" if col in ("amount",) else "w"
            self.recent_tree.column(col, width=w, anchor=anchor)

        scroll = ttk.Scrollbar(tbl_frame, orient="vertical",
                               command=self.recent_tree.yview)
        self.recent_tree.configure(yscrollcommand=scroll.set)
        self.recent_tree.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        scroll.pack(side="right", fill="y", pady=4)

    # ── KPI card helper (modern gradient-style) ────────────────
    def _kpi_card(self, parent, icon, title, value, color):
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=20,
                             height=118, border_width=2,
                             border_color=COLORS["glass_glow"])
        card.pack_propagate(False)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=14)

        # Icon + title row
        title_row = ctk.CTkFrame(inner, fg_color="transparent")
        title_row.pack(anchor="w", fill="x")
        ctk.CTkLabel(title_row, text=icon, font=("Segoe UI", 22),
                     text_color="white").pack(side="left", padx=(0, 8))
        ctk.CTkLabel(title_row, text=title, font=FONTS["small"],
                     text_color="#E2E8F0").pack(side="left")

        val_lbl = ctk.CTkLabel(inner, text=value,
                                font=FONTS["num_md"], text_color="white")
        val_lbl.pack(anchor="w", pady=(4, 0))

        card._val_lbl = val_lbl
        return card

    # ── Data refresh ─────────────────────────────────────────
    def on_show(self):
        self._load_data()

    def _load_data(self):
        stats    = self.db.get_today_stats()
        low      = self.db.get_low_stock_count()
        expiring = self.db.get_expiring_products(30)
        exp_cnt  = len(expiring)

        self.kpi_sales._val_lbl.configure(text=f"₹ {stats['total_sales']:,.2f}")
        self.kpi_bills._val_lbl.configure(text=str(stats["bill_count"]))
        self.kpi_low._val_lbl.configure(
            text=str(low),
            text_color="#C62828" if low > 0 else "#2E7D32"
        )
        self.kpi_expiry._val_lbl.configure(
            text=str(exp_cnt),
            text_color="#C62828" if exp_cnt > 0 else "#2E7D32"
        )
        self.kpi_disc._val_lbl.configure(text=f"₹ {stats['total_discount']:,.2f}")

        # Expiry alert panel — show only if there are expiring products
        if exp_cnt > 0:
            self.exp_tree.delete(*self.exp_tree.get_children())
            for item in expiring:
                dl = item.get("days_left", 0)
                tag = "expired" if dl < 0 else "expiring"
                days_text = "EXPIRED" if dl < 0 else f"{dl} days"
                self.exp_tree.insert("", "end", values=(
                    item["name"],
                    item.get("category_name", ""),
                    f"{item.get('current_stock', 0):.1f}",
                    item.get("expiry_date", ""),
                    days_text,
                ), tags=(tag,))
            self.expiry_frame.pack(fill="x", pady=(0, 16),
                                   before=self._recent_bills_label)
        else:
            self.expiry_frame.pack_forget()

        # Recent bills
        self.recent_tree.delete(*self.recent_tree.get_children())
        for b in self.db.get_recent_bills(12):
            dt = b["bill_date"][:16] if b["bill_date"] else ""
            tag = "void" if b["status"] == "Void" else "draft" if b["status"] == "Draft" else ""
            self.recent_tree.insert("", "end", values=(
                b["bill_number"], dt,
                b.get("customer_name", "Walk-in"),
                f"₹ {b['grand_total']:,.2f}",
                b["payment_mode"],
                b["status"],
            ), tags=(tag,))

        self.recent_tree.tag_configure("void",  background="#FFEBEE")
        self.recent_tree.tag_configure("draft", background="#FFF8E1")

    def _update_clock(self):
        now = datetime.now().strftime("%A, %d %B %Y   %I:%M %p")
        self.dt_label.configure(text=now)
        self.after(30000, self._update_clock)   # refresh every 30 s

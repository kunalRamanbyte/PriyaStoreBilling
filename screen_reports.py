"""
screen_reports.py — Reports Hub (Phase 3)
8 reports with date range filter, treeview display, Excel export.
Designed for 60+ age users: large buttons, clear layout.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, timedelta
import os

from config import COLORS, FONTS, RADII, METRICS
from ui_utils import place_popup
from lang import t

# ── Report catalogue ──────────────────────────────────────────
REPORTS = [
    {"key": "daily_sales",     "title": "Daily Sales",      "emoji": "📅",
     "needs_dates": True,  "needs_cust": False,
     "cols": [("date","Date",120),("bills","Bills",70),("subtotal","Subtotal ₹",130),
               ("discount","Discount ₹",120),("total","Total ₹",130)],
     "summary_col": "total"},
    {"key": "sales_returns",   "title": "Sales Returns",    "emoji": "↩️",
     "needs_dates": True,  "needs_cust": False,
     "cols": [("date","Date",150),("return_number","Return No",120),
               ("bill_number","Bill No",120),("customer","Customer",170),
               ("items","Items",70),("refund_mode","Refund Mode",130),
               ("total","Refund ₹",120)],
     "summary_col": "total"},
    {"key": "itemwise",        "title": "Item-wise Sales",  "emoji": "📦",
     "needs_dates": True,  "needs_cust": False,
     "cols": [("product_name","Product",220),("qty_sold","Qty",80),
               ("avg_price","Avg Price ₹",120),("discount","Discount ₹",110),
               ("total_sales","Total Sales ₹",140)],
     "summary_col": "total_sales"},
    {"key": "top_products",    "title": "Top Products",     "emoji": "🏆",
     "needs_dates": True,  "needs_cust": False,
     "cols": [("rank","#",50),("product_name","Product",240),
               ("qty_sold","Qty Sold",100),("revenue","Revenue ₹",140)],
     "summary_col": "revenue"},
    {"key": "low_stock",       "title": "Low Stock Alert",  "emoji": "⚠️",
     "needs_dates": False, "needs_cust": False,
     "cols": [("product_code","Code",100),("name","Product",200),
               ("category","Category",130),("stock","Stock",90),
               ("reorder","Reorder",90),("shortage","Shortage",90),
               ("status","Status",120)],
     "summary_col": None},
    {"key": "purchase",        "title": "Purchase / GRN",   "emoji": "🛒",
     "needs_dates": True,  "needs_cust": False,
     "cols": [("date","Date",110),("grn_number","GRN No",120),
               ("supplier_name","Supplier",200),("items","Items",70),
               ("total","Total ₹",130)],
     "summary_col": "total"},
    {"key": "profit_margin",   "title": "Profit & Margin",  "emoji": "💰",
     "needs_dates": True,  "needs_cust": False,
     "cols": [("product_name","Product",200),("qty_sold","Qty",70),
               ("sell_price","Sell ₹",100),("cost_price","Cost ₹",100),
               ("margin_per_unit","Margin ₹",110),("margin_pct","Margin %",100),
               ("total_profit","Total Profit ₹",140)],
     "summary_col": "total_profit"},
    {"key": "stock_valuation", "title": "Stock Valuation",  "emoji": "📋",
     "needs_dates": False, "needs_cust": False,
     "cols": [("product_code","Code",90),("name","Product",180),
               ("category","Category",120),("stock","Stock",80),
               ("cost_price","Cost ₹",100),("sell_price","Sell ₹",100),
               ("cost_value","Cost Value ₹",130),("retail_value","Retail Value ₹",140)],
     "summary_col": "cost_value"},
    {"key": "customer_ledger", "title": "Customer Ledger",  "emoji": "👥",
     "needs_dates": True,  "needs_cust": True,
     "cols": [("created_at","Date & Time",160),("customer","Customer",160),
               ("txn_type","Type",110),("amount","Amount ₹",120),
               ("reference","Reference",150),("notes","Notes",160)],
     # No grand total: the amount column mixes Credit/Payment/Refund/Change types,
     # so a single unsigned sum would be meaningless.
     "summary_col": None},
    {"key": "slow_moving",     "title": "Slow-Moving Items", "emoji": "🐌",
     "needs_dates": False, "needs_cust": False,
     "cols": [("product_code","Code",90),("name","Product",200),
               ("category","Category",120),("unit","Unit",70),
               ("current_stock","Stock",90),("selling_price","Price ₹",100),
               ("last_sold","Last Sold",130),("total_qty_30d","Qty(30d)",90)],
     "summary_col": None},
    {"key": "supplier_payables","title": "Supplier Payables","emoji": "🏭",
     "needs_dates": False, "needs_cust": False,
     "cols": [("supplier_name","Supplier",180),("grn_number","GRN",110),
               ("purchase_date","Date",110),("invoice_amount","Invoice ₹",120),
               ("paid_amount","Paid ₹",110),("balance","Balance ₹",120),
               ("age_days","Age (days)",90),("ageing","Bucket",100)],
     "summary_col": "balance"},
    {"key": "customer_ageing",  "title": "Customer Ageing",  "emoji": "📆",
     "needs_dates": False, "needs_cust": False,
     "cols": [("customer","Customer",180),("phone","Phone",130),
               ("total_due","Total Due ₹",130),("due_0_30","0-30 days ₹",120),
               ("due_31_60","31-60 days ₹",120),("due_60plus","60+ days ₹",120),
               ("last_txn_date","Last Txn",110)],
     "summary_col": "total_due"},
]


class ReportScreen(ctk.CTkFrame):
    def __init__(self, parent, db, current_user, app):
        super().__init__(parent, fg_color=COLORS["bg_main"], corner_radius=0)
        self.db           = db
        self.current_user = current_user
        self.app          = app
        self._active_key  = None
        self._report_data = []
        self._report_def  = None
        self._cust_map    = {}   # name → id for customer ledger
        self._build()

    # -- Direction B primitives ------------------------------
    def _card(self, parent, **kw):
        return ctk.CTkFrame(parent, fg_color=COLORS["bg_card"],
                            corner_radius=RADII["card"], border_width=1,
                            border_color=COLORS["hairline"], **kw)

    def _pill(self, parent, text, kind="plain", command=None, width=None,
              height=None):
        tints = {
            "primary": (COLORS["accent_action"], COLORS["btn_primary_h"], COLORS["on_accent"]),
            "action":  (COLORS["accent_action_tint"], COLORS["glass_glow"], COLORS["accent_action_deep"]),
            "money":   (COLORS["accent_money_tint"], COLORS["accent_money_tint"], COLORS["accent_money"]),
            "counts":  (COLORS["accent_counts_tint"], COLORS["accent_counts_tint"], COLORS["accent_counts_fg"]),
            "plain":   (COLORS["bg_white"], COLORS["bg_main"], COLORS["text_dark"]),
        }
        fg, hov, ink = tints.get(kind, tints["plain"])
        h = height or METRICS["control"]
        kw = {"width": width} if width else {}
        return ctk.CTkButton(parent, text=text, font=FONTS["button"],
                             fg_color=fg, hover_color=hov, text_color=ink,
                             height=h, corner_radius=h // 2, border_width=0,
                             command=command, **kw)

    def _stat_card(self, parent, label, hero=False):
        """A stat tile. The hero is the deep blue panel the artboard uses for
        the headline figure; the rest are white cards with a hairline."""
        if hero:
            card = ctk.CTkFrame(parent, fg_color=COLORS["accent_action_deep"],
                                corner_radius=RADII["card"])
            label_ink, value_ink = COLORS["on_accent_soft"], COLORS["on_accent"]
            value_font = FONTS["num_lg"]
        else:
            card = self._card(parent)
            label_ink, value_ink = COLORS["text_muted"], COLORS["text_dark"]
            value_font = FONTS["num_md"]

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=16)
        lbl = ctk.CTkLabel(inner, text=label, font=FONTS["small"],
                           text_color=label_ink, anchor="w")
        lbl.pack(anchor="w")
        val = ctk.CTkLabel(inner, text="\u2014", font=value_font,
                           text_color=value_ink, anchor="w")
        val.pack(anchor="w")
        card._lbl, card._val = lbl, val
        return card

    def _build(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        L = self.app.current_lang

        # -- Report list (second sidebar column) --------------
        left = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_sidebar"],
                                      corner_radius=0, width=244)
        left.grid(row=0, column=0, rowspan=2, sticky="nsew")
        ctk.CTkLabel(left, text=t("SELECT REPORT", L),
                     font=FONTS["table_hdr"], text_color=COLORS["text_muted"]
                     ).pack(pady=(18, 10), padx=14, anchor="w")

        self._rpt_btns = {}
        for rpt in REPORTS:
            btn = ctk.CTkButton(
                left,
                text=f"  {rpt['emoji']}  {t(rpt['title'], L)}",
                font=FONTS["sidebar"],
                fg_color="transparent",
                hover_color=COLORS["sidebar_hover"],
                text_color=COLORS["sidebar_text"],
                anchor="w",
                height=METRICS["nav_item"],
                corner_radius=RADII["sidebar"],
                border_width=0,
                command=lambda r=rpt: self._select_report(r),
            )
            btn.pack(fill="x", padx=10, pady=2)
            self._rpt_btns[rpt["key"]] = btn

        # -- Header band --------------------------------------
        hdr = ctk.CTkFrame(self, fg_color="transparent", height=METRICS["header"])
        hdr.grid(row=0, column=1, sticky="ew", padx=26)
        hdr.grid_propagate(False)

        titles = ctk.CTkFrame(hdr, fg_color="transparent")
        titles.pack(side="left", fill="y")
        self._title_lbl = ctk.CTkLabel(
            titles, text=t("Reports & Analytics", L),
            font=("Segoe UI Semibold", 26, "bold"),
            text_color=COLORS["text_dark"], anchor="w")
        self._title_lbl.pack(anchor="w", pady=(16, 0))
        self._range_lbl = ctk.CTkLabel(
            titles, text=t("\u2190 Select a report from the left panel", L),
            font=FONTS["small"], text_color=COLORS["text_muted"], anchor="w")
        self._range_lbl.pack(anchor="w")

        acts = ctk.CTkFrame(hdr, fg_color="transparent")
        acts.pack(side="right", fill="y")
        self._pill(acts, "\u25b6  " + t("Generate", L), kind="primary", width=130,
                   command=self._generate).pack(side="right", pady=16)
        self._pill(acts, t("PDF", L), kind="counts", width=76,
                   command=self._export_pdf).pack(side="right", padx=(0, 8), pady=16)
        self._pill(acts, t("CSV", L), kind="plain", width=76,
                   command=self._export_csv).pack(side="right", padx=(0, 8), pady=16)
        self._pill(acts, t("Excel", L), kind="money", width=86,
                   command=self._export_excel).pack(side="right", padx=(0, 8), pady=16)

        # -- Right content panel ------------------------------
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=1, column=1, sticky="nsew", padx=26, pady=(0, 20))
        right.grid_rowconfigure(2, weight=1)
        right.grid_columnconfigure(0, weight=1)

        # Filters row: dates + optional customer selector
        ctrl = ctk.CTkFrame(right, fg_color="transparent")
        ctrl.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        ctk.CTkLabel(ctrl, text=t("From:", L), font=FONTS["label_form"],
                     text_color=COLORS["text_muted"]).pack(side="left", padx=(0, 6))
        self.date_from = ctk.CTkEntry(ctrl, width=128, font=FONTS["label_form"],
                                      height=METRICS["control"],
                                      corner_radius=RADII["input"], border_width=1,
                                      border_color=COLORS["hairline"],
                                      fg_color=COLORS["bg_white"],
                                      text_color=COLORS["text_dark"], justify="center")
        self.date_from.pack(side="left", padx=(0, 12))
        self.date_from.insert(0, (date.today() - timedelta(days=30)).isoformat())

        ctk.CTkLabel(ctrl, text=t("To:", L), font=FONTS["label_form"],
                     text_color=COLORS["text_muted"]).pack(side="left", padx=(0, 6))
        self.date_to = ctk.CTkEntry(ctrl, width=128, font=FONTS["label_form"],
                                    height=METRICS["control"],
                                    corner_radius=RADII["input"], border_width=1,
                                    border_color=COLORS["hairline"],
                                    fg_color=COLORS["bg_white"],
                                    text_color=COLORS["text_dark"], justify="center")
        self.date_to.pack(side="left", padx=(0, 12))
        self.date_to.insert(0, date.today().isoformat())

        self._cust_frame = ctk.CTkFrame(ctrl, fg_color="transparent")
        self._cust_frame.pack(side="left")
        ctk.CTkLabel(self._cust_frame, text=t("Customer:", L),
                     font=FONTS["label_form"], text_color=COLORS["text_muted"]
                     ).pack(side="left", padx=(0, 6))
        self._cust_var = tk.StringVar(value=t("All Customers", L))
        self._cust_menu = ctk.CTkComboBox(self._cust_frame, variable=self._cust_var,
                                          values=[t("All Customers", L)], width=180,
                                          font=FONTS["label_form"],
                                          height=METRICS["control"],
                                          corner_radius=RADII["input"],
                                          border_width=1,
                                          border_color=COLORS["hairline"],
                                          fg_color=COLORS["bg_white"],
                                          button_color=COLORS["accent_action"],
                                          button_hover_color=COLORS["btn_primary_h"],
                                          text_color=COLORS["text_dark"])
        self._cust_menu.pack(side="left")
        self._cust_frame.pack_forget()   # hidden by default

        # Stat row — replaces the old one-line summary label
        stats = ctk.CTkFrame(right, fg_color="transparent")
        stats.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        self._stat_hero  = self._stat_card(stats, t("Grand Total", L), hero=True)
        self._stat_rows  = self._stat_card(stats, t("Total rows:", L))
        self._stat_avg   = self._stat_card(stats, t("Average", L))
        self._stat_disc  = self._stat_card(stats, t("Discount", L))
        self._stat_hero.pack(side="left", fill="both", expand=True)
        for c in (self._stat_rows, self._stat_avg, self._stat_disc):
            c.pack(side="left", fill="both", expand=True, padx=(10, 0))

        # Table card
        tbl_frame = self._card(right)
        tbl_frame.grid(row=2, column=0, sticky="nsew")
        tbl_frame.grid_rowconfigure(0, weight=1)
        tbl_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            tbl_frame, columns=[], show="headings",
            style="Rpt.Treeview", selectmode="browse"
        )
        vsb = ttk.Scrollbar(tbl_frame, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(tbl_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=(10, 0))
        vsb.grid(row=0, column=1, sticky="ns",  pady=(10, 0), padx=(0, 8))
        hsb.grid(row=1, column=0, sticky="ew",  padx=(10, 0), pady=(0, 8))
        self.tree.tag_configure("danger",  background=COLORS["row_low_stock"],
                                foreground=COLORS["text_dark"])
        self.tree.tag_configure("warning", background=COLORS["row_expiring"],
                                foreground=COLORS["text_dark"])
        self.tree.tag_configure("alt",     background=COLORS["ROW_COLORS"][1],
                                foreground=COLORS["text_dark"])
        self.tree.bind("<Double-1>", self._on_tree_drilldown)

    # -- Stat row --------------------------------------------
    def _sum_col(self, data, col):
        total = 0.0
        for row in data:
            try:
                total += float(row.get(col) or 0)
            except (TypeError, ValueError):
                pass
        return total

    def _update_stats(self, rpt, data):
        """Direction B replaces the old 'Total rows | Grand Total' line with a
        stat row: the headline figure on the blue hero, then the supporting
        counts. Cards with nothing to say are hidden rather than showing 0."""
        L = self.app.current_lang
        n = len(data)
        summary_col = rpt.get("summary_col")
        col_keys = [c[0] for c in rpt["cols"]]

        if summary_col and summary_col in col_keys:
            total = self._sum_col(data, summary_col)
            head = t(rpt["cols"][col_keys.index(summary_col)][1], L)
            self._stat_hero._lbl.configure(text=head)
            self._stat_hero._val.configure(text=f"\u20b9 {total:,.0f}")
            self._stat_avg._val.configure(
                text=f"\u20b9 {(total / n if n else 0):,.0f}")
            self._stat_avg.pack(side="left", fill="both", expand=True, padx=(10, 0))
        else:
            total = 0.0
            self._stat_hero._lbl.configure(text=t("Total rows:", L))
            self._stat_hero._val.configure(text=str(n))
            self._stat_avg.pack_forget()

        self._stat_rows._val.configure(text=str(n))

        # A discount column is common but not universal.
        disc_col = next((k for k in col_keys if "disc" in k), None)
        if disc_col:
            self._stat_disc._val.configure(
                text=f"\u20b9 {self._sum_col(data, disc_col):,.0f}")
            self._stat_disc.pack(side="left", fill="both", expand=True, padx=(10, 0))
        else:
            self._stat_disc.pack_forget()

    def _select_report(self, rpt: dict):
        """Called when user clicks a report button on the left panel."""
        L = self.app.current_lang
        self._report_def  = rpt
        self._active_key  = rpt["key"]
        self._report_data = []

        # Active report takes the solid blue pill, like the sidebar
        for key, btn in self._rpt_btns.items():
            on = key == rpt["key"]
            btn.configure(
                fg_color=COLORS["sidebar_active"] if on else "transparent",
                text_color=COLORS["on_accent"] if on else COLORS["sidebar_text"],
                hover_color=(COLORS["sidebar_active"] if on
                             else COLORS["sidebar_hover"]),
            )

        # The header keeps one ink colour; the report is identified by the
        # active pill, not by recolouring the title.
        self._title_lbl.configure(text=f"{rpt['emoji']}  {t(rpt['title'], L)}",
                                  text_color=COLORS["text_dark"])

        # Refresh customer list if needed
        if rpt["needs_cust"]:
            custs = self.db.get_customers(active_only=True)
            self._cust_map = {c["name"]: c["customer_id"] for c in custs}
            names = [t("All Customers", L)] + list(self._cust_map.keys())
            self._cust_menu.configure(values=names)
            self._cust_var.set(t("All Customers", L))

        # Show/hide date inputs
        if rpt["needs_dates"]:
            self.date_from.configure(state="normal")
            self.date_to.configure(state="normal")
        else:
            self.date_from.configure(state="disabled")
            self.date_to.configure(state="disabled")

        # Show/hide customer selector
        if rpt["needs_cust"]:
            self._cust_frame.pack(side="left")
        else:
            self._cust_frame.pack_forget()

        # Auto-generate immediately
        self._generate()

    def _generate(self):
        if not self._report_def:
            return
        L = self.app.current_lang
        rpt = self._report_def
        df  = self.date_from.get().strip()
        dt  = self.date_to.get().strip()

        try:
            if rpt["needs_dates"]:
                from datetime import date as dt_
                date.fromisoformat(df)
                date.fromisoformat(dt)
        except ValueError:
            messagebox.showwarning(t("Date Error", L),
                                   t("Enter valid dates in YYYY-MM-DD format.", L),
                                   parent=self.winfo_toplevel())
            return

        # Fetch data
        try:
            if   rpt["key"] == "daily_sales":     data = self.db.report_daily_sales(df, dt)
            elif rpt["key"] == "sales_returns":    data = self.db.report_returns(df, dt)
            elif rpt["key"] == "itemwise":         data = self.db.report_itemwise_sales(df, dt)
            elif rpt["key"] == "top_products":     data = self.db.report_top_products(df, dt)
            elif rpt["key"] == "low_stock":        data = self.db.report_low_stock()
            elif rpt["key"] == "purchase":         data = self.db.report_purchase(df, dt)
            elif rpt["key"] == "profit_margin":    data = self.db.report_profit_margin(df, dt)
            elif rpt["key"] == "stock_valuation":  data = self.db.report_stock_valuation()
            elif rpt["key"] == "customer_ledger":
                cust_name = self._cust_var.get()
                if cust_name == t("All Customers", L):
                    cust_id = None
                else:
                    cust_id = self._cust_map.get(cust_name)
                data = self.db.report_customer_ledger(cust_id, df, dt)
            elif rpt["key"] == "slow_moving":      data = self.db.report_slow_moving()
            elif rpt["key"] == "supplier_payables": data = self.db.report_supplier_payables()
            elif rpt["key"] == "customer_ageing":   data = self.db.report_customer_ageing()
            else:
                data = []
        except Exception as e:
            messagebox.showerror(t("Error", L), str(e), parent=self.winfo_toplevel())
            return

        self._report_data = data
        self._render_table(rpt, data)

        # Header subtitle: say what range this result actually covers.
        if rpt["needs_dates"]:
            self._range_lbl.configure(text=f"{df} – {dt}")
        else:
            self._range_lbl.configure(text=t("Current stock position", L))

    def _render_table(self, rpt: dict, data: list):
        L = self.app.current_lang
        # Rebuild columns
        self.tree.delete(*self.tree.get_children())
        cols = [c[0] for c in rpt["cols"]]
        self.tree.configure(columns=cols)
        for key, head, w in rpt["cols"]:
            # Align columns and headings consistently: right-align numeric/currency, center-align codes/dates, left-align text
            anch = "w"
            if any(term in key for term in ["total", "sales", "revenue", "price", "cost", "margin", "profit", "amount", "due", "balance", "value", "val", "disc", "rate"]):
                anch = "e"
            elif any(term in key for term in ["qty", "count", "bills", "items", "rank", "age", "phone", "date", "grn", "code", "status", "unit", "txn", "created", "at", "time", "sold", "stock", "reorder", "shortage"]):
                anch = "center"
            self.tree.heading(key, text=t(head, L), anchor=anch)
            self.tree.column(key, width=w, anchor=anch, minwidth=50)

        # Row colouring for certain reports
        danger_keys  = {"out_of_stock", "Out of Stock"}
        warning_keys = {"Low Stock"}

        total = 0.0
        summary_col = rpt.get("summary_col")

        for i, row in enumerate(data):
            vals = [str(row.get(c[0], "")) for c in rpt["cols"]]

            # Pick tag
            tag = ""
            if rpt["key"] == "low_stock":
                tag = "danger" if row.get("status") == "Out of Stock" else "warning"
            elif rpt["key"] == "customer_ledger":
                tag = "danger" if row.get("txn_type") == "Credit" else "alt"
            else:
                tag = "alt" if i % 2 == 0 else ""

            self.tree.insert("", "end", iid=str(i), values=vals, tags=(tag,))

            if summary_col:
                try:
                    total += float(row.get(summary_col) or 0)
                except Exception:
                    pass

        # Stat row (Direction B) replaces the old single summary label.
        self._update_stats(rpt, data)

    # ── Excel export ──────────────────────────────────────────
    def _export_excel(self):
        L = self.app.current_lang
        if not self._report_data or not self._report_def:
            messagebox.showinfo(t("No Data", L), t("Generate a report first.", L),
                                parent=self.winfo_toplevel())
            return
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment
        except ImportError:
            messagebox.showerror(
                t("Missing Library", L),
                t("openpyxl is required for Excel export.\n\n", L) +
                "Run:  pip install openpyxl",
                parent=self.winfo_toplevel())
            return

        rpt  = self._report_def
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel file", "*.xlsx")],
            initialfile=f"{rpt['key']}.xlsx",
            parent=self.winfo_toplevel()
        )
        if not path:
            return

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = t(rpt["title"], L)

        hdr_font = Font(bold=True, color="FFFFFF", size=12)
        hdr_fill = PatternFill("solid", fgColor="1565C0")
        headers  = [t(c[1], L) for c in rpt["cols"]]
        for ci, h in enumerate(headers, 1):
            cell = ws.cell(row=1, column=ci, value=h)
            cell.font      = hdr_font
            cell.fill      = hdr_fill
            cell.alignment = Alignment(horizontal="center")

        for ri, row in enumerate(self._report_data, 2):
            for ci, (key, _, _) in enumerate(rpt["cols"], 1):
                ws.cell(row=ri, column=ci, value=row.get(key, ""))

        for col in ws.columns:
            max_len = max((len(str(c.value)) for c in col if c.value), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 40)

        wb.save(path)
        messagebox.showinfo(t("Exported", L), t("Saved to:", L) + f"\n{path}", parent=self.winfo_toplevel())
        try:
            os.startfile(path)
        except Exception:
            pass

    # ── CSV export ────────────────────────────────────────────
    def _export_csv(self):
        L = self.app.current_lang
        if not self._report_data or not self._report_def:
            messagebox.showinfo(t("No Data", L), t("Generate a report first.", L),
                                parent=self.winfo_toplevel())
            return

        rpt  = self._report_def
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV file", "*.csv")],
            initialfile=f"{rpt['key']}.csv",
            parent=self.winfo_toplevel()
        )
        if not path:
            return

        import csv
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([t(c[1], L) for c in rpt["cols"]])
            for row in self._report_data:
                writer.writerow([row.get(c[0], "") for c in rpt["cols"]])

        messagebox.showinfo(t("Exported", L), t("Saved to:", L) + f"\n{path}",
                            parent=self.winfo_toplevel())
        try:
            import os
            os.startfile(path)
        except Exception:
            pass

    # ── PDF export ────────────────────────────────────────────
    def _export_pdf(self):
        L = self.app.current_lang
        if not self._report_data or not self._report_def:
            messagebox.showwarning(t("No Data", L),
                                   t("Generate a report first.", L),
                                   parent=self.winfo_toplevel())
            return
        rpt  = self._report_def
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF file", "*.pdf")],
            initialfile=f"{rpt['key']}.pdf",
            parent=self.winfo_toplevel()
        )
        if not path:
            return
        try:
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib.units import mm
            from reportlab.lib import colors
            from reportlab.platypus import (SimpleDocTemplate, Table,
                                            TableStyle, Paragraph, Spacer)
            from reportlab.lib.styles import ParagraphStyle
            from reportlab.lib.enums import TA_CENTER, TA_LEFT

            BLUE  = colors.HexColor(COLORS["btn_primary"])
            WHITE = colors.white
            LGRAY = colors.HexColor("#F5F7FF")

            # Use landscape for wide reports
            ncols = len(rpt["cols"])
            psize = landscape(A4) if ncols > 6 else A4

            doc = SimpleDocTemplate(path, pagesize=psize,
                                    leftMargin=12*mm, rightMargin=12*mm,
                                    topMargin=10*mm,  bottomMargin=10*mm)

            hdr_style = ParagraphStyle("h", fontSize=14, fontName="Helvetica-Bold",
                                        textColor=BLUE, alignment=TA_CENTER)
            sub_style = ParagraphStyle("s", fontSize=9,  fontName="Helvetica",
                                        textColor=colors.HexColor(COLORS["text_muted"]),
                                        alignment=TA_CENTER, spaceAfter=6)
            cell_s    = ParagraphStyle("c", fontSize=8, fontName="Helvetica",
                                        textColor=colors.HexColor("#1A1A2E"))
            th_s      = ParagraphStyle("t", fontSize=8, fontName="Helvetica-Bold",
                                        textColor=WHITE)

            story = [
                Paragraph(t(rpt["title"], L), hdr_style),
                Paragraph(f"Generated: {__import__('datetime').datetime.now().strftime('%d %b %Y  %I:%M %p')}",
                          sub_style),
                Spacer(1, 4*mm),
            ]

            # Header row
            tbl_data = [[Paragraph(t(c[1], L), th_s) for c in rpt["cols"]]]
            for row in self._report_data:
                tbl_data.append([
                    Paragraph(str(row.get(c[0], "")), cell_s)
                    for c in rpt["cols"]
                ])

            # Auto column widths
            page_w = (psize[0] - 24*mm)
            cw = page_w / ncols
            col_widths = [cw] * ncols

            tbl = Table(tbl_data, colWidths=col_widths, repeatRows=1)
            tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0,0), (-1,0),  BLUE),
                ("ROWBACKGROUNDS",(0,1), (-1,-1),  [WHITE, LGRAY]),
                ("GRID",          (0,0), (-1,-1),  0.3, colors.HexColor(COLORS["border"])),
                ("TOPPADDING",    (0,0), (-1,-1),  3),
                ("BOTTOMPADDING", (0,0), (-1,-1),  3),
                ("LEFTPADDING",   (0,0), (-1,-1),  4),
                ("RIGHTPADDING",  (0,0), (-1,-1),  4),
                ("VALIGN",        (0,0), (-1,-1),  "MIDDLE"),
            ]))
            story.append(tbl)

            if rpt.get("summary_col") and self._report_data:
                try:
                    total = sum(float(r.get(rpt["summary_col"], 0) or 0)
                                for r in self._report_data)
                    # Translate the human-readable column header, not the raw
                    # dict key (which has no lang.py entry).
                    keys = [c[0] for c in rpt["cols"]]
                    col_label = t(rpt["cols"][keys.index(rpt["summary_col"])][1], L)
                    story.append(Spacer(1, 4*mm))
                    story.append(Paragraph(
                        f"<b>Total rows: {len(self._report_data)}  |  "
                        f"Grand Total ({col_label}): {total:,.2f}</b>",
                        ParagraphStyle("sum", fontSize=9, fontName="Helvetica-Bold",
                                       textColor=BLUE, alignment=TA_LEFT)
                    ))
                except Exception:
                    pass

            doc.build(story)
            messagebox.showinfo(t("PDF Exported", L), t("Saved to:", L) + f"\n{path}",
                                parent=self.winfo_toplevel())
            # Open PDF — try multiple methods (RPT-2 fix)
            try:
                import os; os.startfile(path)
            except Exception:
                try:
                    import subprocess; subprocess.Popen(["start", "", path], shell=True)
                except Exception:
                    try:
                        import webbrowser; webbrowser.open(path)
                    except Exception:
                        pass

        except ImportError:
            messagebox.showerror(t("Missing Library", L),
                                 "reportlab is required.\nRun: pip install reportlab",
                                 parent=self.winfo_toplevel())
        except Exception as e:
            messagebox.showerror(t("PDF Error", L), str(e),
                                 parent=self.winfo_toplevel())

    # ── Drill-down ────────────────────────────────────────────
    def _on_tree_drilldown(self, event=None):
        if not self._active_key or not self._report_data:
            return
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        row_data = self._report_data[idx]
        if self._active_key == "daily_sales":
            self._show_daily_sales_detail(str(row_data.get("date", "")))

    def _show_daily_sales_detail(self, date_str: str):
        L = self.app.current_lang
        if not date_str:
            return
        # High limit so the drilldown never truncates below the report's own
        # count (default get_bills limit is only 200).
        bills = self.db.get_bills(date_from=date_str, date_to=date_str,
                                  status="Active", limit=100000)

        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title(t("Bills", L) + f" — {date_str}")
        place_popup(dlg, 840, 520, self.winfo_toplevel())
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        # Header
        hdr = ctk.CTkFrame(dlg, fg_color=COLORS["btn_primary"], corner_radius=0, height=58)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text=f"📅  " + t("Bills for", L) + f" {date_str}",
                     font=FONTS["subheading"], text_color="white"
                    ).pack(side="left", padx=20, pady=10)
        active = [b for b in bills if b.get("status") == "Active"]
        grand  = sum(float(b.get("grand_total", 0)) for b in active)
        ctk.CTkLabel(hdr,
                     text=f"{len(active)} " + t("bill(s)   |   Total ₹", L) + f"{grand:,.2f}",
                     font=FONTS["body_bold"], text_color=COLORS["on_accent_soft"]
                    ).pack(side="right", padx=20)

        # Table
        frame = ctk.CTkFrame(dlg, fg_color=COLORS["bg_card"], corner_radius=16)
        frame.pack(fill="both", expand=True, padx=12, pady=8)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        cols   = ("bill_no", "time", "customer", "total", "payment", "status")
        heads  = (t("Bill #", L),  t("Time", L), t("Customer", L), t("Total ₹", L), t("Payment Mode", L), t("Status", L))
        widths = (110, 75, 220, 110, 140, 80)
        tree = ttk.Treeview(frame, columns=cols, show="headings",
                             style="Rpt.Treeview", selectmode="browse")
        for col, head, w in zip(cols, heads, widths):
            anch = "center" if col in ("bill_no", "time", "status") else ("e" if col == "total" else "w")
            tree.heading(col, text=head, anchor=anch)
            tree.column(col, width=w, anchor=anch, minwidth=50)

        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=6)
        vsb.grid(row=0, column=1, sticky="ns", pady=6)

        _row_colors = COLORS["ROW_COLORS"]
        for i, b in enumerate(bills):
            raw_dt   = str(b.get("bill_date", ""))
            time_str = raw_dt[11:16] if len(raw_dt) >= 16 else ""
            is_void  = b.get("status") == "Void"
            tag      = "void" if is_void else f"row{i % len(_row_colors)}"
            tree.insert("", "end", iid=str(b["bill_id"]), values=(
                b.get("bill_number", ""),
                time_str,
                b.get("customer_name", "Walk-in Customer"),
                f"{b.get('grand_total', 0):,.2f}",
                b.get("payment_mode", ""),
                b.get("status", "Active"),
            ), tags=(tag,))

        tree.tag_configure("void", background=COLORS["badge_void"])
        for idx, color in enumerate(_row_colors):
            tree.tag_configure(f"row{idx}", background=color)

        ctk.CTkButton(dlg, text=t("Close", L), font=FONTS["button"],
                      fg_color=COLORS["btn_secondary"], height=44, corner_radius=12,
                      command=dlg.destroy
                     ).pack(padx=20, pady=(0, 12))

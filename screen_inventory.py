"""
screen_inventory.py — Inventory Manager (Phase 2)
Real-time stock levels, low-stock alerts, manual stock adjustments.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from config import COLORS, FONTS


class InventoryScreen(ctk.CTkFrame):
    def __init__(self, parent, db, current_user, app):
        super().__init__(parent, fg_color=COLORS["bg_main"], corner_radius=0)
        self.db           = db
        self.current_user = current_user
        self.app          = app
        self._build()

    def _build(self):
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Header ───────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0, height=70)
        header.grid(row=0, column=0, sticky="ew")
        header.pack_propagate(False)
        header.grid_propagate(False)
        ctk.CTkLabel(header, text="📊   Inventory Manager",
                     font=FONTS["heading"], text_color=COLORS["text_dark"]
                    ).pack(side="left", padx=25, pady=15)
        ctk.CTkButton(header, text="🔧  Adjust Stock",
                      font=FONTS["button"], fg_color=COLORS["btn_warning"],
                      height=44, corner_radius=10,
                      command=self._open_adjustment_dialog
                     ).pack(side="right", padx=10, pady=13)
        ctk.CTkButton(header, text="📋  Adj. History",
                      font=FONTS["button"], fg_color=COLORS["btn_secondary"],
                      height=44, corner_radius=10,
                      command=self._show_adj_history
                     ).pack(side="right", padx=(0, 4), pady=13)

        # ── KPI Cards ─────────────────────────────────────────
        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.grid(row=1, column=0, sticky="ew", padx=12, pady=(10, 0))
        kpi_row.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.kpi_vars = {}
        kpi_defs = [
            ("total_products", "📦 Total Products", COLORS["kpi_blue"],   "0"),
            ("low_stock",      "⚠️  Low Stock",      COLORS["kpi_orange"], "0"),
            ("out_of_stock",   "🚫 Out of Stock",   COLORS["kpi_blue"],   "0"),
            ("stock_value",    "💰 Stock Value",     COLORS["kpi_green"],  "₹0"),
        ]
        for col, (key, label, color, default) in enumerate(kpi_defs):
            card = ctk.CTkFrame(kpi_row, fg_color=COLORS["bg_card"], corner_radius=16)
            card.grid(row=0, column=col, sticky="ew", padx=5, pady=6, ipady=10)
            ctk.CTkFrame(card, fg_color=color, corner_radius=0, height=5
                        ).pack(fill="x")
            ctk.CTkLabel(card, text=label, font=FONTS["small_bold"],
                         text_color=COLORS["text_muted"]).pack(pady=(12, 2))
            var = tk.StringVar(value=default)
            self.kpi_vars[key] = var
            ctk.CTkLabel(card, textvariable=var, font=FONTS["num_md"],
                         text_color=color).pack(pady=(0, 12))

        # ── Filter bar ────────────────────────────────────────
        fbar = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=16, height=58)
        fbar.grid(row=2, column=0, sticky="new", padx=12, pady=(8, 0))
        fbar.grid_propagate(False)
        fbar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(fbar, text="🔍", font=FONTS["body"],
                     text_color=COLORS["btn_primary"]).grid(row=0, column=0, padx=(16, 4), pady=10)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._load_products())
        ctk.CTkEntry(fbar, textvariable=self.search_var,
                     placeholder_text="Search by product name, code or brand…",
                     font=FONTS["input"], height=40,
                     border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"]
                    ).grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=9)

        ctk.CTkLabel(fbar, text="Category:", font=FONTS["body"],
                     text_color=COLORS["text_dark"]).grid(row=0, column=2, padx=(0, 6))
        self.cat_var = tk.StringVar(value="All")
        self.cat_menu = ctk.CTkOptionMenu(
            fbar, variable=self.cat_var, values=["All"],
            font=FONTS["body"], height=40, width=160,
            fg_color=COLORS["btn_primary"], button_color="#005BBE",
            command=lambda _: self._load_products()
        )
        self.cat_menu.grid(row=0, column=3, padx=(0, 10), pady=9)

        self.filter_var = tk.StringVar(value="All")
        ctk.CTkSegmentedButton(
            fbar,
            values=["All", "Low Stock", "Out of Stock"],
            variable=self.filter_var,
            font=FONTS["small_bold"],
            height=38,
            command=lambda _: self._load_products()
        ).grid(row=0, column=4, padx=(0, 16), pady=9)

        # ── Table ─────────────────────────────────────────────
        tbl_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=16)
        tbl_frame.grid(row=3, column=0, sticky="nsew", padx=12, pady=8)
        tbl_frame.grid_rowconfigure(0, weight=1)
        tbl_frame.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # ttk styles applied globally via styles.py

        cols = ("code", "name", "category", "brand", "unit",
                "stock", "reorder", "status", "value")
        self.tree = ttk.Treeview(
            tbl_frame, columns=cols, show="headings",
            style="Inv.Treeview", selectmode="browse"
        )
        heads  = ("Code", "Product Name", "Category", "Brand", "Unit",
                  "Stock", "Reorder", "Status", "Stock Value ₹")
        widths = (90, 240, 120, 110, 70, 80, 70, 110, 100)
        for col, head, w in zip(cols, heads, widths):
            self.tree.heading(col, text=head)
            anch = "e" if col in ("stock", "reorder", "value") else "w"
            self.tree.column(col, width=w, anchor=anch, minwidth=50)

        vsb = ttk.Scrollbar(tbl_frame, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(tbl_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=(6, 0))
        vsb.grid(row=0, column=1, sticky="ns",  pady=(6, 0))
        hsb.grid(row=1, column=0, sticky="ew",  padx=(6, 0))

        self.tree.bind("<Double-1>", lambda e: self._open_adjustment_dialog())
        self.tree.tag_configure("out",  background=COLORS["tbl_low_stock"])
        self.tree.tag_configure("low",  background="#FFF9C4")
        self.tree.tag_configure("ok",   background="#E8F5E9")
        self.tree.tag_configure("alt",  background=COLORS["tbl_row_alt"])

    def on_show(self):
        self._load_cat_filter()
        self._load_stats()
        self._load_products()

    def _load_cat_filter(self):
        cats = self.db.get_categories()
        names = ["All"] + [c["name"] for c in cats]
        self.cat_menu.configure(values=names)
        self._cats_map = {c["name"]: c["category_id"] for c in cats}

    def _load_stats(self):
        s = self.db.get_inventory_stats()
        self.kpi_vars["total_products"].set(str(s.get("total_products", 0)))
        self.kpi_vars["low_stock"].set(str(s.get("low_stock", 0)))
        self.kpi_vars["out_of_stock"].set(str(s.get("out_of_stock", 0)))
        val = s.get("stock_value", 0)
        self.kpi_vars["stock_value"].set(f"₹{val:,.0f}")

    def _load_products(self):
        search   = self.search_var.get().strip()
        cat_sel  = self.cat_var.get()
        cat_id   = self._cats_map.get(cat_sel) if hasattr(self, "_cats_map") and cat_sel != "All" else None
        flt      = self.filter_var.get()

        prods = self.db.get_products(active_only=True, search=search, category_id=cat_id)

        if flt == "Low Stock":
            prods = [p for p in prods if 0 < p["current_stock"] <= p["reorder_level"]]
        elif flt == "Out of Stock":
            prods = [p for p in prods if p["current_stock"] <= 0]

        self.tree.delete(*self.tree.get_children())
        for i, p in enumerate(prods):
            stk = p["current_stock"]
            ror = p["reorder_level"]
            if stk <= 0:
                tag    = "out"
                status = "🚫 Out of Stock"
            elif stk <= ror:
                tag    = "low"
                status = "⚠️  Low Stock"
            else:
                tag    = "ok" if i % 2 == 0 else "alt"
                status = "✅ In Stock"

            val = stk * p.get("purchase_price", 0)
            self.tree.insert("", "end", iid=str(p["product_id"]), values=(
                p.get("product_code", ""),
                p["name"],
                p.get("category_name", ""),
                p.get("brand", ""),
                p.get("unit", ""),
                f"{stk:.1f}",
                f"{ror:.0f}",
                status,
                f"{val:.2f}",
            ), tags=(tag,))

    def _get_selected_pid(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select Product", "Please select a product first.",
                                parent=self.winfo_toplevel())
            return None
        return int(sel[0])

    def _open_adjustment_dialog(self, product_id=None):
        if not product_id:
            product_id = self._get_selected_pid()
        if not product_id:
            return

        prod = self.db.get_product_by_id(product_id)
        if not prod:
            return

        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title("Adjust Stock")
        dlg.geometry("500x480")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        # Header
        ctk.CTkFrame(dlg, fg_color=COLORS["btn_warning"], height=6, corner_radius=0).pack(fill="x")
        ctk.CTkLabel(dlg, text="🔧   Adjust Stock",
                     font=FONTS["heading"], text_color=COLORS["text_dark"]
                    ).pack(pady=(18, 4), padx=24, anchor="w")

        # Product info card
        info = ctk.CTkFrame(dlg, fg_color=COLORS["bg_main"], corner_radius=16)
        info.pack(fill="x", padx=24, pady=(0, 16))
        ctk.CTkLabel(info, text=prod["name"],
                     font=FONTS["body_bold"], text_color=COLORS["text_dark"]
                    ).pack(anchor="w", padx=16, pady=(10, 2))
        ctk.CTkLabel(info,
                     text=f"Current Stock:  {prod['current_stock']:.1f}  {prod.get('unit','piece')}   |   "
                          f"Reorder Level: {prod['reorder_level']:.0f}",
                     font=FONTS["small"], text_color=COLORS["text_muted"]
                    ).pack(anchor="w", padx=16, pady=(0, 10))

        # Adjustment type
        ctk.CTkLabel(dlg, text="Adjustment Type",
                     font=FONTS["label_form"], text_color=COLORS["text_dark"]
                    ).pack(anchor="w", padx=24, pady=(0, 4))
        adj_type = tk.StringVar(value="Add")
        type_frame = ctk.CTkFrame(dlg, fg_color="transparent")
        type_frame.pack(fill="x", padx=24, pady=(0, 14))
        for t, col in [("Add", COLORS["btn_success"]),
                       ("Remove", COLORS["btn_danger"]),
                       ("Set", COLORS["btn_primary"])]:
            ctk.CTkRadioButton(
                type_frame, text=t, variable=adj_type, value=t,
                font=FONTS["body_bold"], text_color=COLORS["text_dark"],
                fg_color=col, hover_color=col
            ).pack(side="left", padx=(0, 20))

        # Quantity
        ctk.CTkLabel(dlg, text="Quantity *",
                     font=FONTS["label_form"], text_color=COLORS["text_dark"]
                    ).pack(anchor="w", padx=24)
        qty_var = tk.StringVar()
        ctk.CTkEntry(dlg, textvariable=qty_var,
                     placeholder_text="e.g. 10",
                     font=FONTS["input"], height=50,
                     border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"]
                    ).pack(fill="x", padx=24, pady=(4, 14))

        # Reason
        ctk.CTkLabel(dlg, text="Reason *",
                     font=FONTS["label_form"], text_color=COLORS["text_dark"]
                    ).pack(anchor="w", padx=24)
        reasons = ["New Stock Received", "Damaged / Expired", "Theft / Loss",
                   "Physical Count Correction", "Return to Supplier", "Other"]
        reason_var = tk.StringVar(value=reasons[0])
        ctk.CTkOptionMenu(dlg, variable=reason_var, values=reasons,
                          font=FONTS["input"], height=46, fg_color=COLORS["btn_primary"],
                          button_color="#005BBE"
                         ).pack(fill="x", padx=24, pady=(4, 0))

        err_lbl = ctk.CTkLabel(dlg, text="", font=FONTS["small"],
                                text_color=COLORS["btn_danger"])
        err_lbl.pack(pady=(6, 0), padx=24, anchor="w")

        def save():
            try:
                qty = float(qty_var.get())
                if qty <= 0:
                    raise ValueError
            except ValueError:
                err_lbl.configure(text="⚠  Enter a valid positive quantity.")
                return
            t = adj_type.get()
            if t == "Remove" and qty > prod["current_stock"]:
                err_lbl.configure(
                    text=f"⚠  Cannot remove more than current stock ({prod['current_stock']:.1f})."
                )
                return
            self.db.do_stock_adjustment(
                product_id, t, qty, reason_var.get(),
                self.current_user["user_id"]
            )
            messagebox.showinfo("Done", f"Stock adjusted successfully!", parent=dlg)
            dlg.destroy()
            self._load_stats()
            self._load_products()

        btn_row = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=14)
        ctk.CTkButton(btn_row, text="✅  Save Adjustment",
                      font=FONTS["button"], fg_color=COLORS["btn_success"],
                      height=52, corner_radius=16,
                      command=save).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(btn_row, text="Cancel",
                      font=FONTS["button"], fg_color=COLORS["btn_secondary"],
                      height=52, corner_radius=16,
                      command=dlg.destroy).pack(side="left", width=110)

    def _show_adj_history(self):
        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title("Stock Adjustment History")
        dlg.geometry("860x520")
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        ctk.CTkLabel(dlg, text="📋   Stock Adjustment History",
                     font=FONTS["subheading"], text_color=COLORS["text_dark"]
                    ).pack(pady=(18, 8), padx=20, anchor="w")

        frame = ctk.CTkFrame(dlg, fg_color=COLORS["bg_card"], corner_radius=16)
        frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # ttk styles applied globally via styles.py

        cols = ("date", "product", "type", "before", "change", "after", "reason")
        tree = ttk.Treeview(frame, columns=cols, show="headings",
                            style="Adj.Treeview", selectmode="browse")
        heads  = ("Date & Time", "Product", "Type", "Before", "Change", "After", "Reason")
        widths = (150, 220, 80, 70, 70, 70, 200)
        for col, head, w in zip(cols, heads, widths):
            tree.heading(col, text=head)
            tree.column(col, width=w, minwidth=50)

        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=6)
        vsb.grid(row=0, column=1, sticky="ns", pady=6)

        records = self.db.get_stock_adjustments(limit=200)
        for r in records:
            tree.insert("", "end", values=(
                r["created_at"][:16],
                r["product_name"],
                r["adj_type"],
                f"{r['qty_before']:.1f}",
                f"+{r['qty_change']:.1f}" if r["adj_type"] == "Add"
                    else (f"-{r['qty_change']:.1f}" if r["adj_type"] == "Remove"
                          else f"→{r['qty_change']:.1f}"),
                f"{r['qty_after']:.1f}",
                r.get("reason", ""),
            ))

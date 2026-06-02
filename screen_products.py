"""
screen_products.py — Product Master screen
Add, edit, deactivate products. Search and filter by category.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from config import COLORS, FONTS, UNITS


class ProductScreen(ctk.CTkFrame):
    def __init__(self, parent, db, current_user, app):
        super().__init__(parent, fg_color=COLORS["bg_main"], corner_radius=0)
        self.db           = db
        self.current_user = current_user
        self.app          = app
        self._editing_id  = None   # None = add mode, int = edit mode
        self._build()

    def _build(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Header ───────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0, height=70)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        ctk.CTkLabel(header, text="📦   Product Master",
                     font=FONTS["heading"], text_color=COLORS["text_dark"]
                    ).pack(side="left", padx=25, pady=15)
        ctk.CTkButton(header, text="➕  Add New Product",
                      font=FONTS["button"], fg_color=COLORS["btn_success"],
                      height=44, corner_radius=10,
                      command=self._open_add_form
                     ).pack(side="right", padx=20, pady=13)

        # ── Body ─────────────────────────────────────────────
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=12, pady=8)
        body.grid_rowconfigure(1, weight=1)
        body.grid_columnconfigure(0, weight=1)

        # Filter bar
        fbar = ctk.CTkFrame(body, fg_color=COLORS["bg_card"], corner_radius=16, height=58)
        fbar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        fbar.grid_propagate(False)
        fbar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(fbar, text="🔍", font=FONTS["body"],
                     text_color=COLORS["btn_primary"]).grid(row=0, column=0, padx=(16, 4), pady=9)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._load_products())
        ctk.CTkEntry(fbar, textvariable=self.search_var,
                     placeholder_text="Search products by name, code, or brand…",
                     font=FONTS["input"], height=40,
                     border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"]
                    ).grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=9)

        ctk.CTkLabel(fbar, text="Category:",
                     font=FONTS["body"], text_color=COLORS["text_dark"]
                    ).grid(row=0, column=2, padx=(0, 6))
        self.cat_filter_var = tk.StringVar(value="All Categories")
        self.cat_filter_menu = ctk.CTkOptionMenu(
            fbar, variable=self.cat_filter_var,
            values=["All Categories"],
            font=FONTS["body"], height=40, width=170,
            fg_color=COLORS["btn_primary"], button_color="#005BBE",
            command=lambda _: self._load_products()
        )
        self.cat_filter_menu.grid(row=0, column=3, padx=(0, 12), pady=9)

        # Stock filter
        self.low_stock_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(fbar, text="Low Stock Only",
                        variable=self.low_stock_var,
                        font=FONTS["small"], text_color=COLORS["text_dark"],
                        fg_color=COLORS["btn_danger"],
                        command=self._load_products
                       ).grid(row=0, column=4, padx=(0, 16), pady=9)

        # Product count
        self.count_label = ctk.CTkLabel(fbar, text="",
                                         font=FONTS["small"], text_color=COLORS["text_muted"])
        self.count_label.grid(row=0, column=5, padx=(0, 16))

        # ── Table ─────────────────────────────────────────────
        tbl_frame = ctk.CTkFrame(body, fg_color=COLORS["bg_card"], corner_radius=16)
        tbl_frame.grid(row=1, column=0, sticky="nsew")
        tbl_frame.grid_rowconfigure(0, weight=1)
        tbl_frame.grid_columnconfigure(0, weight=1)

        # ttk styles applied globally via styles.py

        cols = ("code", "name", "category", "brand", "unit",
                "sell_price", "buy_price", "stock", "reorder", "expiry", "status")
        self.tree = ttk.Treeview(
            tbl_frame, columns=cols, show="headings",
            style="Prod.Treeview", selectmode="browse"
        )
        heads  = ("Code", "Product Name", "Category", "Brand", "Unit",
                  "Sell ₹", "Cost ₹", "Stock", "Reorder", "Expiry Date", "Status")
        widths = (90, 200, 110, 100, 60, 75, 75, 65, 65, 100, 65)
        for col, head, w in zip(cols, heads, widths):
            self.tree.heading(col, text=head)
            anch = "e" if col in ("sell_price","buy_price","stock","reorder") else "w"
            # stretch=False keeps fixed column width so horizontal scroll works (PROD-4 fix)
            self.tree.column(col, width=w, anchor=anch, minwidth=50, stretch=False)

        vsb = ttk.Scrollbar(tbl_frame, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(tbl_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(6,0), pady=(6,0))
        vsb.grid(row=0, column=1, sticky="ns",  pady=(6,0))
        hsb.grid(row=1, column=0, sticky="ew",  padx=(6,0))

        self.tree.bind("<Double-1>", lambda e: self._open_edit_form())

        # ── Action bar ───────────────────────────────────────
        act = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0, height=58)
        act.grid(row=2, column=0, sticky="ew")
        act.grid_propagate(False)
        ctk.CTkButton(act, text="✏️  Edit",
                      font=FONTS["button"], fg_color=COLORS["btn_primary"],
                      height=42, width=100, corner_radius=10,
                      command=self._open_edit_form
                     ).pack(side="left", padx=(20, 6), pady=8)
        ctk.CTkButton(act, text="🚫  Deactivate",
                      font=FONTS["button"], fg_color="#FF8C00",
                      height=42, width=130, corner_radius=10,
                      command=self._deactivate_product
                     ).pack(side="left", padx=(0, 6), pady=8)
        ctk.CTkButton(act, text="🗑️  Delete",
                      font=FONTS["button"], fg_color=COLORS["btn_danger"],
                      height=42, width=100, corner_radius=10,
                      command=self._delete_product
                     ).pack(side="left", padx=(0, 6), pady=8)

    def on_show(self):
        self._load_categories_filter()
        self._load_products()

    def _load_categories_filter(self):
        cats = self.db.get_categories()
        names = ["All Categories"] + [c["name"] for c in cats]
        self.cat_filter_menu.configure(values=names)
        self._cats_map = {c["name"]: c["category_id"] for c in cats}

    def _load_products(self):
        search  = self.search_var.get().strip()
        cat_sel = self.cat_filter_var.get()
        cat_id  = self._cats_map.get(cat_sel) if hasattr(self, "_cats_map") and cat_sel != "All Categories" else None
        low     = self.low_stock_var.get()

        prods = self.db.get_products(active_only=not low, search=search, category_id=cat_id)
        if low:
            prods = [p for p in prods if p["current_stock"] <= p["reorder_level"]]

        today = date.today()
        self.tree.delete(*self.tree.get_children())
        for i, p in enumerate(prods):
            exp_str = p.get("expiry_date") or ""
            exp_tag = ""
            if exp_str:
                try:
                    exp_date = date.fromisoformat(exp_str)
                    days_left = (exp_date - today).days
                    if days_left < 0:
                        exp_tag = "expired"
                    elif days_left <= 30:
                        exp_tag = "expiring"
                except ValueError:
                    pass

            low_tag = "low" if p["current_stock"] <= p["reorder_level"] else ""
            tags = tuple(t for t in (exp_tag or low_tag or ("alt" if i % 2 == 0 else ""),) if t)
            self.tree.insert("", "end", iid=str(p["product_id"]), values=(
                p.get("product_code", ""),
                p["name"],
                p.get("category_name", ""),
                p.get("brand", ""),
                p.get("unit", ""),
                f"{p['selling_price']:.2f}",
                f"{p.get('purchase_price', 0):.2f}",
                f"{p['current_stock']:.1f}",
                f"{p['reorder_level']:.0f}",
                exp_str or "—",
                "✅ Active" if p["is_active"] else "❌ Off",
            ), tags=tags)

        self.tree.tag_configure("expired",  background="#FFEBEE")   # red tint
        self.tree.tag_configure("expiring", background="#FFF8E1")   # amber tint
        self.tree.tag_configure("low",      background=COLORS["tbl_low_stock"])
        self.tree.tag_configure("alt",      background=COLORS["tbl_row_alt"])
        self.count_label.configure(text=f"{len(prods)} product(s)")

    def _get_selected_product_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select Product",
                                "Please select a product first.",
                                parent=self.winfo_toplevel())
            return None
        return int(sel[0])

    def _open_add_form(self):
        self._editing_id = None
        self._open_form(None)

    def _open_edit_form(self):
        pid = self._get_selected_product_id()
        if not pid:
            return
        prod = self.db.get_product_by_id(pid)
        if prod:
            self._editing_id = pid
            self._open_form(prod)

    def _open_form(self, product):
        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        title = "Edit Product" if product else "Add New Product"
        dlg.title(title)
        dlg.geometry("540x640")
        dlg.resizable(False, True)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        scroll = ctk.CTkScrollableFrame(dlg, fg_color=COLORS["bg_main"])
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll, text=f"{'✏️  Edit' if product else '➕  Add'} Product",
                     font=FONTS["heading"], text_color=COLORS["btn_primary"]
                    ).pack(pady=(16, 10), padx=24, anchor="w")

        cats  = self.db.get_categories()
        c_map = {c["name"]: c["category_id"] for c in cats}
        c_names = list(c_map.keys())

        entries = {}

        def field(label, key, default="", placeholder="", wide=False):
            f = ctk.CTkFrame(scroll, fg_color="transparent")
            f.pack(fill="x", padx=24, pady=5)
            ctk.CTkLabel(f, text=label, font=FONTS["label_form"],
                         text_color=COLORS["text_dark"],
                         width=165, anchor="w").pack(side="left")
            var = tk.StringVar(value=str(default) if default not in (None, "") else "")
            entry = ctk.CTkEntry(f, textvariable=var,
                                 placeholder_text=placeholder,
                                 font=FONTS["input"], height=40,
                                 border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"],
                                 width=290 if wide else 220)
            entry.pack(side="left")
            entries[key] = var
            return var

        def dropdown(label, key, values, default=""):
            f = ctk.CTkFrame(scroll, fg_color="transparent")
            f.pack(fill="x", padx=24, pady=5)
            ctk.CTkLabel(f, text=label, font=FONTS["label_form"],
                         text_color=COLORS["text_dark"],
                         width=165, anchor="w").pack(side="left")
            var = tk.StringVar(value=default if default else (values[0] if values else ""))
            ctk.CTkOptionMenu(f, variable=var, values=values,
                              font=FONTS["input"], height=40, width=220,
                              fg_color=COLORS["btn_primary"], button_color="#005BBE"
                             ).pack(side="left")
            entries[key] = var

        p = product or {}

        field("Product Name *",      "name",          p.get("name",""),        "e.g. Aashirvaad Atta 5kg", wide=True)
        field("Product Code",        "product_code",  p.get("product_code",""),"Auto-generated if blank")
        dropdown("Category *",       "category",      c_names,                 p.get("category_name", c_names[0] if c_names else ""))
        field("Brand",               "brand",         p.get("brand",""),       "Optional")
        dropdown("Unit *",           "unit",          UNITS,                   p.get("unit","piece"))
        field("Selling Price (₹) *", "selling_price", p.get("selling_price",""),"e.g. 45.50")
        field("Purchase Price (₹)",  "purchase_price",p.get("purchase_price",""),"For margin calc")
        field("Current Stock",       "current_stock", p.get("current_stock",0), "Quantity in hand")
        field("Reorder Level",       "reorder_level", p.get("reorder_level",5),  "Alert threshold")
        field("Expiry Date",         "expiry_date",   p.get("expiry_date","") or "", "YYYY-MM-DD  (leave blank if N/A)")

        err_lbl = ctk.CTkLabel(scroll, text="", font=FONTS["small"],
                                text_color=COLORS["btn_danger"])
        err_lbl.pack(pady=(4, 0), padx=24, anchor="w")

        def save():
            name = entries["name"].get().strip()
            if not name:
                err_lbl.configure(text="⚠  Product Name is required.")
                return
            try:
                sell = float(entries["selling_price"].get() or 0)
                buy  = float(entries["purchase_price"].get() or 0)
                stk  = float(entries["current_stock"].get() or 0)
                ror  = float(entries["reorder_level"].get() or 5)
            except ValueError:
                err_lbl.configure(text="⚠  Prices and stock must be numbers.")
                return

            exp_raw = entries["expiry_date"].get().strip()
            expiry  = None
            if exp_raw:
                try:
                    date.fromisoformat(exp_raw)   # validate format
                    expiry = exp_raw
                except ValueError:
                    err_lbl.configure(text="⚠  Expiry Date must be YYYY-MM-DD (e.g. 2026-12-31).")
                    return

            cat_name = entries["category"].get()
            cat_id   = c_map.get(cat_name)

            code = entries["product_code"].get().strip()

            data = {
                "product_code" : code or None,
                "name"         : name,
                "category_id"  : cat_id,
                "brand"        : entries["brand"].get().strip() or None,
                "unit"         : entries["unit"].get(),
                "selling_price": sell,
                "purchase_price": buy,
                "current_stock": stk,
                "reorder_level": ror,
                "expiry_date"  : expiry,
            }

            if self._editing_id:
                self.db.update_product(self._editing_id, data)
                messagebox.showinfo("Saved", f"Product '{name}' updated.", parent=dlg)
            else:
                self.db.add_product(data)
                messagebox.showinfo("Added", f"Product '{name}' added.", parent=dlg)

            dlg.destroy()
            self._load_products()

        dlg.bind("<Return>", lambda e: save())  # SUP-2/global: Enter submits form

        btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=12)
        ctk.CTkButton(btn_row, text="💾  Save Product",
                      font=FONTS["button"], fg_color=COLORS["btn_success"],
                      height=48, corner_radius=16,
                      command=save).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(btn_row, text="Cancel",
                      font=FONTS["button"], fg_color=COLORS["btn_secondary"],
                      height=48, corner_radius=16,
                      command=dlg.destroy).pack(side="left", width=100)

    def _deactivate_product(self):
        pid = self._get_selected_product_id()
        if not pid:
            return
        prod = self.db.get_product_by_id(pid)
        if not prod:
            return
        if messagebox.askyesno(
            "Deactivate Product",
            f"Deactivate  '{prod['name']}'?\n\n"
            f"It will no longer appear in billing search.",
            parent=self.winfo_toplevel()
        ):
            self.db.deactivate_product(pid)
            self._load_products()

    def _delete_product(self):
        """Permanently delete product (PROD-1). Deactivates if used in bills."""
        pid = self._get_selected_product_id()
        if not pid:
            return
        prod = self.db.get_product_by_id(pid)
        if not prod:
            return
        if not messagebox.askyesno(
            "Delete Product",
            f"Permanently DELETE  '{prod['name']}'?\n\n"
            "⚠️  This cannot be undone.\n"
            "If the product has billing history it will be deactivated instead.",
            parent=self.winfo_toplevel()
        ):
            return
        ok, msg = self.db.delete_product(pid)
        if ok:
            messagebox.showinfo("Deleted", msg, parent=self.winfo_toplevel())
        else:
            messagebox.showwarning("Cannot Delete", msg, parent=self.winfo_toplevel())
            self.db.deactivate_product(pid)
        self._load_products()

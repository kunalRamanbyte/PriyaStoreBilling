"""
screen_products.py — Product Master screen
Add, edit, deactivate products. Search and filter by category.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from config import COLORS, FONTS, RADII, METRICS, UNITS, GUTTERS
from responsive import (ResponsiveMixin, fit_columns, widget_scaling,
                        autohide_scrollbar)
from ui_utils import place_popup, open_date_picker
from lang import t
from ui_utils import EmptyState
from webcam_scanner import WebcamScanner


class ProductScreen(ResponsiveMixin, ctk.CTkFrame):
    def __init__(self, parent, db, current_user, app):
        super().__init__(parent, fg_color=COLORS["bg_main"], corner_radius=0)
        self.db           = db
        self.current_user = current_user
        self.app          = app
        self._editing_id  = None   # None = add mode, int = edit mode
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
            "action":  (COLORS["accent_action_tint"], COLORS["glass_glow"], COLORS["accent_action_fg"]),
            "expiry":  (COLORS["accent_expiry_tint"], COLORS["accent_expiry_tint"], COLORS["accent_expiry_fg"]),
            "danger":  (COLORS["accent_danger_tint"], COLORS["accent_danger_tint"], COLORS["accent_danger_fg"]),
            "plain":   (COLORS["bg_main"], COLORS["glass_glow"], COLORS["text_dark"]),
        }
        fg, hov, ink = tints.get(kind, tints["plain"])
        h = height or METRICS["control"]
        kw = {"width": width} if width else {}
        return ctk.CTkButton(parent, text=text, font=FONTS["button"],
                             fg_color=fg, hover_color=hov, text_color=ink,
                             height=h, corner_radius=h // 2, border_width=0,
                             command=command, **kw)

    def _build(self):
        L = self.app.current_lang
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # -- Header band (transparent, like every other screen) --
        header = ctk.CTkFrame(self, fg_color="transparent",
                              height=METRICS["header"])
        self._header = header
        header.grid(row=0, column=0, sticky="ew", padx=28)
        header.grid_propagate(False)

        titles = ctk.CTkFrame(header, fg_color="transparent")
        titles.pack(side="left", fill="y")
        ctk.CTkLabel(titles, text=t("Product Master", L),
                     font=("Segoe UI Semibold", 26, "bold"),
                     text_color=COLORS["text_dark"], anchor="w"
                     ).pack(anchor="w", pady=(16, 0))
        self.count_label = ctk.CTkLabel(
            titles, text="", font=FONTS["small"],
            text_color=COLORS["text_muted"], anchor="w")
        self.count_label.pack(anchor="w")

        # Create is an action, so it takes the action blue - not the
        # money-in teal it used to wear.
        self._pill(header, "\uff0b  " + t("Add New Product", L),
                   kind="primary", width=190, height=46,
                   command=self._open_add_form).pack(side="right", pady=15)

        # -- Body ---------------------------------------------
        body = ctk.CTkFrame(self, fg_color="transparent")
        self._body = body
        body.grid(row=1, column=0, sticky="nsew", padx=28, pady=(0, 12))
        body.grid_rowconfigure(1, weight=1)
        body.grid_columnconfigure(0, weight=1)

        # -- Filter row ----------------------------------------
        fbar = ctk.CTkFrame(body, fg_color="transparent")
        fbar.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._load_products())
        self.search_entry = ctk.CTkEntry(
            fbar, textvariable=self.search_var,
            font=FONTS["label_form"], width=320,
            height=METRICS["control"], corner_radius=RADII["input"],
            border_width=1, border_color=COLORS["hairline"],
            fg_color=COLORS["bg_white"], text_color=COLORS["text_dark"])
        self.search_entry.pack(side="left")
        # A textvariable suppresses CTkEntry's placeholder, so draw the hint.
        self._search_hint = ctk.CTkLabel(
            self.search_entry,
            text="\U0001F50D  " + t("Search products\u2026", L),
            font=FONTS["label_form"], text_color=COLORS["text_muted"],
            fg_color="transparent")
        self._search_hint.place(x=18, rely=0.5, anchor="w")
        self._search_hint.bind("<Button-1>",
                               lambda _e: self.search_entry.focus_set())

        # A filter is not the loudest thing on the screen: neutral surface,
        # not the solid blue that used to outshout every real action here.
        self.cat_filter_var = tk.StringVar(value=t("All Categories", L))
        self.cat_filter_menu = ctk.CTkOptionMenu(
            fbar, variable=self.cat_filter_var,
            values=[t("All Categories", L)],
            font=FONTS["label_form"], height=METRICS["control"], width=190,
            corner_radius=RADII["input"],
            fg_color=COLORS["bg_white"],
            button_color=COLORS["bg_white"],
            button_hover_color=COLORS["glass_glow"],
            text_color=COLORS["text_dark"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_text_color=COLORS["text_dark"],
            dropdown_hover_color=COLORS["accent_action_tint"],
            command=lambda _: self._load_products())
        self.cat_filter_menu.pack(side="left", padx=(10, 0))

        # Low stock is a stock-risk filter, so it wears coral - the hue that
        # already means stock risk. It was destructive red, which taught the
        # operator that red can mean "filter".
        self.low_stock_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(fbar, text=t("Low Stock Only", L),
                        variable=self.low_stock_var,
                        font=FONTS["label_form"],
                        text_color=COLORS["text_dark"],
                        fg_color=COLORS["accent_stock"],
                        hover_color=COLORS["accent_stock_fg"],
                        checkmark_color=COLORS["on_accent"],
                        border_color=COLORS["hairline"],
                        corner_radius=6,
                        command=self._load_products
                        ).pack(side="left", padx=(14, 0))

        # -- Table ---------------------------------------------
        tbl_frame = self._card(body)
        self._tbl = tbl_frame
        tbl_frame.grid(row=1, column=0, sticky="nsew")
        tbl_frame.grid_rowconfigure(0, weight=1)
        tbl_frame.grid_columnconfigure(0, weight=1)

        cols = ("code", "name", "category", "brand", "unit",
                "sell_price", "buy_price", "stock", "reorder", "expiry", "status")
        self.tree = ttk.Treeview(
            tbl_frame, columns=cols, show="headings",
            style="Prod.Treeview", selectmode="browse"
        )
        heads = (t("Code", L), t("Product Name", L), t("Category", L),
                 t("Brand", L), t("Unit", L), t("Sell", L), t("Cost", L),
                 t("Stock", L), t("Reorder", L), t("Expiry Date", L),
                 t("Status", L))
        # Name and category absorb the surplus; every other column keeps a
        # floor wide enough for its widest real value.
        self.PROD_COLSPEC = [
            ("code", 0, 100), ("name", 3, 180), ("category", 1, 130),
            ("brand", 1, 110), ("unit", 0, 62), ("sell_price", 0, 82),
            ("buy_price", 0, 82), ("stock", 0, 74), ("reorder", 0, 82),
            ("expiry", 0, 104), ("status", 0, 104),
        ]
        for (col, _w, m), head in zip(self.PROD_COLSPEC, heads):
            anch = "e" if col in ("sell_price", "buy_price", "stock", "reorder") else "w"
            # Heading shares its column's alignment; ttk centres by default,
            # which left every left-aligned column with a centred label.
            self.tree.heading(col, text=head, anchor=anch)
            self.tree.column(col, width=m, anchor=anch, minwidth=m,
                             stretch=(col in ("name", "category")))

        vsb = ttk.Scrollbar(tbl_frame, orient="vertical",
                            command=self.tree.yview, style="Prod.Vertical.TScrollbar")
        hsb = ttk.Scrollbar(tbl_frame, orient="horizontal", command=self.tree.xview)
        _hgrid = dict(row=1, column=0, sticky="ew", padx=(10, 0), pady=(0, 8))
        _vgrid = dict(row=0, column=1, sticky="ns", pady=(10, 0), padx=(0, 8))
        self.tree.configure(
            yscrollcommand=autohide_scrollbar(self.tree, vsb, _vgrid),
            xscrollcommand=autohide_scrollbar(self.tree, hsb, _hgrid))
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=(10, 0))
        vsb.grid(row=0, column=1, sticky="ns", pady=(10, 0), padx=(0, 8))

        self.tree.bind("<Double-1>", lambda e: self._open_edit_form())
        tbl_frame.bind("<Configure>", lambda _e: self._fit_prod_columns(), add="+")

        # -- Footer action bar ---------------------------------
        # Same pattern as Bill History: destructive packed first so it always
        # keeps its place, then the safe actions from the left.
        act = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0,
                           height=METRICS["header"])
        act.grid(row=2, column=0, sticky="ew")
        act.grid_propagate(False)
        ctk.CTkFrame(act, fg_color=COLORS["hairline"], height=1,
                     corner_radius=0).pack(fill="x", side="top")

        self._pill(act, t("\U0001F5D1\uFE0F  Delete", L), kind="danger",
                   width=118, height=46, command=self._delete_product
                   ).pack(side="right", padx=(0, 28), pady=15)
        self._pill(act, t("\u270F\uFE0F  Edit", L), kind="primary", width=108,
                   height=46, command=self._open_edit_form
                   ).pack(side="left", padx=(28, 8), pady=15)
        self._pill(act, "\U0001F6AB  " + t("Deactivate", L), kind="expiry",
                   width=140, height=46, command=self._deactivate_product
                   ).pack(side="left", pady=15)

        self._empty = EmptyState(tbl_frame, t("No products found", L),
                                 t("Add your first product, or clear the filters.", L))
        self.bind_responsive()

    def _fit_prod_columns(self):
        tree = getattr(self, "tree", None)
        if tree is None or tree.winfo_width() <= 1:
            return
        spec = getattr(self, "_visible_colspec", None) or self.PROD_COLSPEC
        fit_columns(tree, spec, tree.winfo_width(), widget_scaling(self))

    # Secondary columns by breakpoint. Eleven columns cannot fit ~1000px
    # without every one of them clipping, and the honest answer is fewer
    # columns, not narrower ones. A shopkeeper scanning stock needs name,
    # price and stock; brand and reorder level are reference data.
    _HIDE = {
        "compact":  ("brand", "reorder", "buy_price"),
        "standard": ("brand", "reorder"),
        "wide":     (),
    }

    def on_breakpoint(self, bp, logical_w):
        g = GUTTERS[bp]
        self._header.grid_configure(padx=g)
        self._body.grid_configure(padx=g)
        self.search_entry.configure(width=240 if bp == "compact" else 320)
        hidden = self._HIDE[bp]
        self._visible_colspec = [(c, w, m) for c, w, m in self.PROD_COLSPEC
                                 if c not in hidden]
        self.tree.configure(displaycolumns=[c for c, _w, _m in self._visible_colspec])
        self._fit_prod_columns()

    def on_show(self):
        self._load_categories_filter()
        self._load_products()

    def _load_categories_filter(self):
        cats = self.db.get_categories()
        names = ["All Categories"] + [c["name"] for c in cats]
        self.cat_filter_menu.configure(values=names)
        self._cats_map = {c["name"]: c["category_id"] for c in cats}

    def _load_products(self):
        L = self.app.current_lang
        search  = self.search_var.get().strip()
        cat_sel = self.cat_filter_var.get()
        cat_id  = self._cats_map.get(cat_sel) if hasattr(self, "_cats_map") and cat_sel != t("All Categories", L) else None
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
            if exp_tag:
                tags = (exp_tag,)
            elif low_tag:
                tags = (low_tag,)
            else:
                tags = (f"row{i % len(COLORS['ROW_COLORS'])}",)
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
                ("✅ " + t("Active", L)) if p["is_active"] else ("❌ " + t("Deactivate", L)),
            ), tags=tags)

        self.tree.tag_configure("expired",  background=COLORS["row_expired"], foreground=COLORS["text_dark"])
        self.tree.tag_configure("expiring", background=COLORS["row_expiring"], foreground=COLORS["text_dark"])
        self.tree.tag_configure("low",      background=COLORS["tbl_low_stock"], foreground=COLORS["text_dark"])
        for idx, color in enumerate(COLORS["ROW_COLORS"]):
            self.tree.tag_configure(f"row{idx}", background=color, foreground=COLORS["text_dark"])
        self._empty.sync(len(prods))
        self.count_label.configure(text=t("product(s)", L).format(n=len(prods)))

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
        L = self.app.current_lang
        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        title = t("Edit Product" if product else "Add New Product", L)
        dlg.title(title)
        place_popup(dlg, 540, 640)
        dlg.resizable(False, True)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        scroll = ctk.CTkScrollableFrame(dlg, fg_color=COLORS["bg_main"])
        scroll.pack(fill="both", expand=True)

        header_prefix = t("✏️  Edit", L) if product else ("➕  " + t("Add", L))
        ctk.CTkLabel(scroll, text=f"{header_prefix} {t('Product', L)}",
                     font=FONTS["heading"], text_color=COLORS["btn_primary"]
                    ).pack(pady=(16, 10), padx=24, anchor="w")

        cats  = self.db.get_categories()
        c_map = {c["name"]: c["category_id"] for c in cats}
        c_names = list(c_map.keys())

        entries = {}

        def field(label, key, default="", placeholder="", wide=False, show_scan=False):
            f = ctk.CTkFrame(scroll, fg_color="transparent")
            f.pack(fill="x", padx=24, pady=5)
            ctk.CTkLabel(f, text=label, font=FONTS["label_form"],
                         text_color=COLORS["text_dark"],
                         width=165, anchor="w").pack(side="left")
            var = tk.StringVar(value=str(default) if default not in (None, "") else "")
            entry_width = 290 if wide else (160 if show_scan else 220)
            entry = ctk.CTkEntry(f, textvariable=var,
                                 placeholder_text=placeholder,
                                 font=FONTS["input"], height=40,
                                 border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"],
                                 width=entry_width)
            entry.pack(side="left")
            if show_scan:
                scan_btn = ctk.CTkButton(
                    f, text="📷", font=("Segoe UI", 16),
                    width=50, height=40, corner_radius=10,
                    fg_color=COLORS.get("btn_primary", "#3B82F6"), hover_color=COLORS["btn_primary_h"],
                    command=lambda: WebcamScanner(dlg, self.app, callback=lambda val: var.set(val))
                )
                scan_btn.pack(side="left", padx=(6, 0))
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
                              fg_color=COLORS["btn_primary"], button_color=COLORS["btn_primary_h"]
                              ).pack(side="left")
            entries[key] = var

        p = product or {}

        field(t("Product Name *", L),      "name",          p.get("name",""),        "e.g. Aashirvaad Atta 5kg", wide=True)
        field(t("Product Code", L),        "product_code",  p.get("product_code",""),"Auto-generated if blank", show_scan=True)
        dropdown(t("Category *", L),       "category",      c_names,                 p.get("category_name", c_names[0] if c_names else ""))
        field(t("Brand", L),               "brand",         p.get("brand",""),       t("Optional", L))
        dropdown(t("Unit *", L),           "unit",          UNITS,                   p.get("unit","piece"))
        field(t("Selling Price (₹) *", L), "selling_price", p.get("selling_price",""),"e.g. 45.50")
        field(t("Purchase Price (₹)", L),  "purchase_price",p.get("purchase_price",""),"For margin calc")
        field(t("Current Stock", L),       "current_stock", p.get("current_stock",0), "Quantity in hand")
        field(t("Reorder Level", L),       "reorder_level", p.get("reorder_level",5),  "Alert threshold")
        # Expiry date — entry + calendar button
        exp_f = ctk.CTkFrame(scroll, fg_color="transparent")
        exp_f.pack(fill="x", padx=24, pady=5)
        ctk.CTkLabel(exp_f, text=t("Expiry Date", L), font=FONTS["label_form"],
                     text_color=COLORS["text_dark"],
                     width=165, anchor="w").pack(side="left")
        exp_var = tk.StringVar(value=p.get("expiry_date", "") or "")
        entries["expiry_date"] = exp_var
        ctk.CTkEntry(exp_f, textvariable=exp_var,
                     placeholder_text=t("Click calendar →", L),
                     font=FONTS["input"], height=40, width=170,
                     border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"]
                    ).pack(side="left", padx=(0, 6))
        ctk.CTkButton(exp_f, text="📅", width=44, height=40,
                      font=("Segoe UI", 18), corner_radius=10,
                      fg_color=COLORS["btn_primary"],
                      command=lambda: open_date_picker(exp_f, exp_var, t("Select Expiry Date", L))
                     ).pack(side="left")

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
        ctk.CTkButton(btn_row, text=t("Save Product", L),
                      font=FONTS["button"], fg_color=COLORS["btn_success"],
                      height=48, corner_radius=16,
                      command=save).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(btn_row, text=t("Cancel", L),
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

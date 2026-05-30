"""
screen_purchase.py — Purchase / GRN Entry (Phase 2)
Record goods received from suppliers, auto-increases stock.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from config import COLORS, FONTS


class PurchaseScreen(ctk.CTkFrame):
    def __init__(self, parent, db, current_user, app):
        super().__init__(parent, fg_color=COLORS["bg_main"], corner_radius=0)
        self.db           = db
        self.current_user = current_user
        self.app          = app
        self._cart        = []          # list of purchase line items
        self._supplier_map = {}         # name → supplier_id
        self._build()

    # ─────────────────────────────────────────────────────────────
    # Build UI
    # ─────────────────────────────────────────────────────────────
    def _build(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        paned = ctk.CTkFrame(self, fg_color="transparent")
        paned.grid(row=0, column=0, sticky="nsew")
        paned.grid_rowconfigure(0, weight=1)
        paned.grid_columnconfigure(0, weight=1)
        paned.grid_columnconfigure(1, weight=0)

        # ── Left: new GRN entry ───────────────────────────────
        left = ctk.CTkFrame(paned, fg_color=COLORS["bg_main"], corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew")
        left.grid_rowconfigure(3, weight=1)
        left.grid_columnconfigure(0, weight=1)

        # Header
        hdr = ctk.CTkFrame(left, fg_color=COLORS["bg_card"], corner_radius=0, height=70)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)
        ctk.CTkLabel(hdr, text="🛒   New Purchase / GRN",
                     font=FONTS["heading"], text_color=COLORS["text_dark"]
                    ).pack(side="left", padx=25, pady=15)

        # GRN meta row (supplier + notes)
        meta = ctk.CTkFrame(left, fg_color=COLORS["bg_card"], corner_radius=16, height=70)
        meta.grid(row=1, column=0, sticky="ew", padx=12, pady=(8, 4))
        meta.grid_propagate(False)
        meta.grid_columnconfigure(1, weight=1)
        meta.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(meta, text="Supplier:", font=FONTS["body_bold"],
                     text_color=COLORS["text_dark"]
                    ).grid(row=0, column=0, padx=(16, 8), pady=12)
        self.supplier_var = tk.StringVar(value="Direct Purchase")
        self.supplier_menu = ctk.CTkOptionMenu(
            meta, variable=self.supplier_var,
            values=["Direct Purchase"],
            font=FONTS["body"], height=42, width=220,
            fg_color=COLORS["btn_primary"], button_color="#005BBE"
        )
        self.supplier_menu.grid(row=0, column=1, padx=(0, 16), pady=12, sticky="w")

        ctk.CTkLabel(meta, text="Notes:", font=FONTS["body_bold"],
                     text_color=COLORS["text_dark"]
                    ).grid(row=0, column=2, padx=(0, 8))
        self.notes_var = tk.StringVar()
        ctk.CTkEntry(meta, textvariable=self.notes_var,
                     placeholder_text="Optional notes for this GRN",
                     font=FONTS["input"], height=42,
                     border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"]
                    ).grid(row=0, column=3, padx=(0, 16), pady=12, sticky="ew")

        # Product search bar
        sbar = ctk.CTkFrame(left, fg_color=COLORS["bg_card"], corner_radius=16, height=58)
        sbar.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 4))
        sbar.grid_propagate(False)
        sbar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(sbar, text="🔍  Add Product:",
                     font=FONTS["body_bold"], text_color=COLORS["text_dark"]
                    ).grid(row=0, column=0, padx=(16, 8))
        self.prod_search_var = tk.StringVar()
        self.prod_search_var.trace_add("write", self._on_search_change)
        self.prod_entry = ctk.CTkEntry(
            sbar, textvariable=self.prod_search_var,
            placeholder_text="Type product name to add…",
            font=FONTS["input"], height=42,
            border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"]
        )
        self.prod_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=8)
        self.prod_entry.bind("<Return>", lambda e: self._search_product())
        self._popup = None

        ctk.CTkButton(sbar, text="➕  Add Item",
                      font=FONTS["button"], fg_color=COLORS["btn_success"],
                      height=42, width=130, corner_radius=10,
                      command=self._search_product
                     ).grid(row=0, column=2, padx=(0, 16), pady=8)

        # Cart table
        tbl_frame = ctk.CTkFrame(left, fg_color=COLORS["bg_card"], corner_radius=16)
        tbl_frame.grid(row=3, column=0, sticky="nsew", padx=12, pady=(0, 4))
        tbl_frame.grid_rowconfigure(0, weight=1)
        tbl_frame.grid_columnconfigure(0, weight=1)

        # ttk styles applied globally via styles.py

        cols   = ("#", "name", "unit", "qty", "price", "total")
        heads  = ("#", "Product Name", "Unit", "Qty", "Buy Price ₹", "Total ₹")
        widths = (40, 280, 70, 70, 100, 100)
        self.cart_tree = ttk.Treeview(tbl_frame, columns=cols, show="headings",
                                       style="Pur.Treeview", selectmode="browse")
        for col, head, w in zip(cols, heads, widths):
            self.cart_tree.heading(col, text=head)
            anch = "e" if col in ("qty", "price", "total") else "w"
            self.cart_tree.column(col, width=w, anchor=anch, minwidth=40)
        vsb = ttk.Scrollbar(tbl_frame, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=vsb.set)
        self.cart_tree.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=6)
        vsb.grid(row=0, column=1, sticky="ns", pady=6)
        self.cart_tree.tag_configure("alt", background=COLORS["tbl_row_alt"])
        self.cart_tree.bind("<Double-1>", lambda e: self._edit_cart_item())
        self.cart_tree.bind("<Delete>",   lambda e: self._remove_cart_item())

        # Action row
        act = ctk.CTkFrame(left, fg_color=COLORS["bg_card"], corner_radius=0, height=58)
        act.grid(row=4, column=0, sticky="ew")
        act.grid_propagate(False)
        ctk.CTkButton(act, text="✏️  Edit Item",
                      font=FONTS["button"], fg_color=COLORS["btn_primary"],
                      height=42, width=120, corner_radius=10,
                      command=self._edit_cart_item
                     ).pack(side="left", padx=(20, 6), pady=8)
        ctk.CTkButton(act, text="🗑️  Remove",
                      font=FONTS["button"], fg_color=COLORS["btn_danger"],
                      height=42, width=120, corner_radius=10,
                      command=self._remove_cart_item
                     ).pack(side="left", padx=(0, 6), pady=8)
        ctk.CTkButton(act, text="🧹  Clear All",
                      font=FONTS["button"], fg_color=COLORS["btn_secondary"],
                      height=42, width=120, corner_radius=10,
                      command=self._clear_cart
                     ).pack(side="left", padx=(0, 6), pady=8)

        # ── Right: summary + save ─────────────────────────────
        right = ctk.CTkFrame(paned, fg_color=COLORS["bg_card"], corner_radius=0, width=300)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_propagate(False)
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(right, text="GRN Summary",
                     font=FONTS["subheading"], text_color=COLORS["text_dark"]
                    ).pack(pady=(24, 4), padx=20, anchor="w")
        ctk.CTkFrame(right, fg_color=COLORS["tbl_select"], height=2).pack(fill="x", padx=20, pady=(0, 16))

        # Total items
        ctk.CTkLabel(right, text="Total Items:", font=FONTS["body"],
                     text_color=COLORS["text_muted"]).pack(anchor="w", padx=20)
        self.items_var = tk.StringVar(value="0")
        ctk.CTkLabel(right, textvariable=self.items_var,
                     font=FONTS["num_md"], text_color=COLORS["kpi_blue"]
                    ).pack(anchor="w", padx=20, pady=(0, 16))

        ctk.CTkLabel(right, text="Grand Total:", font=FONTS["body"],
                     text_color=COLORS["text_muted"]).pack(anchor="w", padx=20)
        self.total_var = tk.StringVar(value="₹ 0.00")
        ctk.CTkLabel(right, textvariable=self.total_var,
                     font=FONTS["num_lg"], text_color=COLORS["kpi_green"]
                    ).pack(anchor="w", padx=20, pady=(0, 24))

        ctk.CTkFrame(right, fg_color=COLORS["tbl_select"], height=2).pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkButton(right, text="✅  Save GRN\n(Update Stock)",
                      font=FONTS["button"], fg_color=COLORS["btn_success"],
                      height=70, corner_radius=16,
                      command=self._save_grn
                     ).pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkButton(right, text="🧹  Clear Form",
                      font=FONTS["button"], fg_color=COLORS["btn_secondary"],
                      height=50, corner_radius=16,
                      command=self._clear_all
                     ).pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkFrame(right, fg_color=COLORS["tbl_select"], height=2).pack(fill="x", padx=20, pady=(0, 16))
        ctk.CTkLabel(right, text="📋  GRN History",
                     font=FONTS["subheading"], text_color=COLORS["text_dark"]
                    ).pack(anchor="w", padx=20, pady=(0, 8))
        ctk.CTkButton(right, text="View All GRNs",
                      font=FONTS["button"], fg_color=COLORS["btn_purple"],
                      height=44, corner_radius=10,
                      command=self._show_grn_history
                     ).pack(fill="x", padx=20)

    # ─────────────────────────────────────────────────────────────
    # on_show: refresh suppliers
    # ─────────────────────────────────────────────────────────────
    def on_show(self):
        self._load_suppliers()

    def _load_suppliers(self):
        sups = self.db.get_suppliers()
        names = ["Direct Purchase"] + [s["name"] for s in sups]
        self._supplier_map = {s["name"]: s["supplier_id"] for s in sups}
        self.supplier_menu.configure(values=names)

    # ─────────────────────────────────────────────────────────────
    # Product search popup
    # ─────────────────────────────────────────────────────────────
    def _on_search_change(self, *_):
        q = self.prod_search_var.get().strip()
        if len(q) < 1:
            self._close_popup()
            return
        results = self.db.search_products_billing(q)
        if not results:
            self._close_popup()
            return
        self._show_popup(results)

    def _show_popup(self, results):
        self._close_popup()
        x = self.prod_entry.winfo_rootx()
        y = self.prod_entry.winfo_rooty() + self.prod_entry.winfo_height()
        w = self.prod_entry.winfo_width() + 130

        popup = tk.Toplevel(self.winfo_toplevel())
        popup.wm_overrideredirect(True)
        popup.geometry(f"{w}x{min(len(results)*46+4, 300)}+{x}+{y}")
        popup.attributes("-topmost", True)
        self._popup = popup

        lb = tk.Listbox(popup, font=FONTS["body"],
                        selectbackground=COLORS["tbl_select"], selectforeground="#1A1A2E",
                        borderwidth=0, highlightthickness=0,
                        activestyle="none")
        lb.pack(fill="both", expand=True)

        for p in results:
            lb.insert("end",
                f"  {p['name']}  —  ₹{p['selling_price']:.2f}  [Stock: {p['current_stock']} {p['unit']}]")

        def select(event=None):
            idx = lb.curselection()
            if idx:
                self._add_product_to_cart(results[idx[0]])
            self._close_popup()

        lb.bind("<Double-1>", select)
        lb.bind("<Return>",   select)
        popup.bind("<Escape>", lambda e: self._close_popup())

    def _close_popup(self):
        if self._popup:
            try:
                self._popup.destroy()
            except Exception:
                pass
            self._popup = None

    def _search_product(self):
        q = self.prod_search_var.get().strip()
        if not q:
            return
        results = self.db.search_products_billing(q)
        if len(results) == 1:
            self._add_product_to_cart(results[0])
        elif results:
            self._show_popup(results)
        else:
            messagebox.showinfo("Not Found",
                                f"No product found matching '{q}'.",
                                parent=self.winfo_toplevel())

    def _add_product_to_cart(self, prod):
        self._close_popup()
        self.prod_search_var.set("")
        # Check if already in cart
        for item in self._cart:
            if item["product_id"] == prod["product_id"]:
                item["quantity"] += 1
                item["line_total"] = round(item["quantity"] * item["unit_price"], 2)
                self._refresh_cart()
                return

        # Ask for qty + price
        self._edit_item_dialog(prod, new=True)

    def _edit_item_dialog(self, prod=None, new=False):
        if prod is None:
            sel = self.cart_tree.selection()
            if not sel:
                return
            idx = int(sel[0])
            prod_data = self._cart[idx]
            prod = {"product_id": prod_data["product_id"],
                    "name": prod_data["product_name"],
                    "unit": prod_data["unit"],
                    "purchase_price": prod_data["unit_price"]}
        else:
            prod_data = None

        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title("Add Item" if new else "Edit Item")
        dlg.geometry("420x360")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        ctk.CTkLabel(dlg, text=prod["name"],
                     font=FONTS["subheading"], text_color=COLORS["text_dark"]
                    ).pack(pady=(20, 4), padx=24, anchor="w")
        ctk.CTkLabel(dlg, text=f"Unit: {prod.get('unit','piece')}",
                     font=FONTS["small"], text_color=COLORS["text_muted"]
                    ).pack(anchor="w", padx=24, pady=(0, 16))

        # Qty
        ctk.CTkLabel(dlg, text="Quantity *", font=FONTS["label_form"],
                     text_color=COLORS["text_dark"]).pack(anchor="w", padx=24)
        qty_var = tk.StringVar(value="1" if new else str(prod_data["quantity"]))
        ctk.CTkEntry(dlg, textvariable=qty_var, font=FONTS["input"],
                     height=50, border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"]
                    ).pack(fill="x", padx=24, pady=(4, 14))

        # Buy price
        ctk.CTkLabel(dlg, text="Purchase Price (₹) *", font=FONTS["label_form"],
                     text_color=COLORS["text_dark"]).pack(anchor="w", padx=24)
        buy_default = prod_data["unit_price"] if not new else prod.get("purchase_price", 0)
        price_var = tk.StringVar(value=str(buy_default))
        ctk.CTkEntry(dlg, textvariable=price_var, font=FONTS["input"],
                     height=50, border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"]
                    ).pack(fill="x", padx=24, pady=(4, 6))

        err_lbl = ctk.CTkLabel(dlg, text="", font=FONTS["small"],
                                text_color=COLORS["btn_danger"])
        err_lbl.pack(pady=(0, 6), padx=24, anchor="w")

        def confirm():
            try:
                qty   = float(qty_var.get())
                price = float(price_var.get())
                if qty <= 0 or price < 0:
                    raise ValueError
            except ValueError:
                err_lbl.configure(text="⚠  Enter valid quantity and price.")
                return

            if new:
                self._cart.append({
                    "product_id"  : prod["product_id"],
                    "product_name": prod["name"],
                    "unit"        : prod.get("unit", "piece"),
                    "quantity"    : qty,
                    "unit_price"  : price,
                    "line_total"  : round(qty * price, 2),
                })
            else:
                sel = self.cart_tree.selection()
                if sel:
                    idx = int(sel[0])
                    self._cart[idx]["quantity"]   = qty
                    self._cart[idx]["unit_price"]  = price
                    self._cart[idx]["line_total"]  = round(qty * price, 2)
            dlg.destroy()
            self._refresh_cart()

        btn_row = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=10)
        ctk.CTkButton(btn_row, text="✅  Confirm",
                      font=FONTS["button"], fg_color=COLORS["btn_success"],
                      height=50, corner_radius=16,
                      command=confirm).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(btn_row, text="Cancel",
                      font=FONTS["button"], fg_color=COLORS["btn_secondary"],
                      height=50, corner_radius=16,
                      command=dlg.destroy).pack(side="left", width=100)

    def _edit_cart_item(self):
        sel = self.cart_tree.selection()
        if not sel:
            return
        self._edit_item_dialog(new=False)

    def _remove_cart_item(self):
        sel = self.cart_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        del self._cart[idx]
        self._refresh_cart()

    def _clear_cart(self):
        if self._cart and messagebox.askyesno(
            "Clear Items", "Remove all items from this GRN?",
            parent=self.winfo_toplevel()
        ):
            self._cart.clear()
            self._refresh_cart()

    def _refresh_cart(self):
        self.cart_tree.delete(*self.cart_tree.get_children())
        total = 0.0
        for i, item in enumerate(self._cart):
            tag = "alt" if i % 2 == 0 else ""
            self.cart_tree.insert("", "end", iid=str(i), values=(
                i + 1,
                item["product_name"],
                item["unit"],
                f"{item['quantity']:.2f}",
                f"{item['unit_price']:.2f}",
                f"{item['line_total']:.2f}",
            ), tags=(tag,))
            total += item["line_total"]
        self.items_var.set(str(len(self._cart)))
        self.total_var.set(f"₹ {total:,.2f}")

    # ─────────────────────────────────────────────────────────────
    # Save GRN
    # ─────────────────────────────────────────────────────────────
    def _save_grn(self):
        if not self._cart:
            messagebox.showwarning("Empty GRN",
                                   "Please add at least one product.",
                                   parent=self.winfo_toplevel())
            return

        sup_name = self.supplier_var.get()
        sup_id   = self._supplier_map.get(sup_name)
        total    = sum(i["line_total"] for i in self._cart)

        purchase_data = {
            "supplier_id"  : sup_id,
            "supplier_name": sup_name,
            "total_amount" : total,
            "notes"        : self.notes_var.get().strip(),
        }

        if not messagebox.askyesno(
            "Save GRN",
            f"Save GRN from  '{sup_name}'?\n\n"
            f"  Items  : {len(self._cart)}\n"
            f"  Total  : ₹{total:,.2f}\n\n"
            f"Stock will be increased for all items.",
            parent=self.winfo_toplevel()
        ):
            return

        purchase_id = self.db.save_purchase(
            purchase_data, self._cart,
            self.current_user["user_id"]
        )
        self._show_grn_receipt(purchase_id)
        self._clear_all()
        # Refresh inventory if open
        if "inventory" in self.app.screens:
            self.app.screens["inventory"].on_show()

    def _clear_all(self):
        self._cart.clear()
        self._refresh_cart()
        self.supplier_var.set("Direct Purchase")
        self.notes_var.set("")
        self.prod_search_var.set("")

    # ─────────────────────────────────────────────────────────────
    # GRN Receipt popup
    # ─────────────────────────────────────────────────────────────
    def _show_grn_receipt(self, purchase_id):
        p, items = self.db.get_purchase_by_id(purchase_id)
        if not p:
            return

        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title("GRN Saved ✅")
        dlg.geometry("520x520")
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        ctk.CTkFrame(dlg, fg_color=COLORS["btn_success"], height=6, corner_radius=0).pack(fill="x")

        scroll = ctk.CTkScrollableFrame(dlg, fg_color=COLORS["bg_card"])
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        ctk.CTkLabel(scroll, text="✅  GRN Saved Successfully!",
                     font=FONTS["subheading"], text_color=COLORS["btn_success"]
                    ).pack(pady=(18, 4), padx=24, anchor="w")
        ctk.CTkLabel(scroll, text=f"GRN Number:  {p['grn_number']}",
                     font=FONTS["body_bold"], text_color=COLORS["text_dark"]
                    ).pack(anchor="w", padx=24)
        ctk.CTkLabel(scroll, text=f"Supplier:  {p['supplier_name']}",
                     font=FONTS["body"], text_color=COLORS["text_muted"]
                    ).pack(anchor="w", padx=24, pady=(2, 16))

        ctk.CTkFrame(scroll, fg_color=COLORS["tbl_select"], height=2).pack(fill="x", padx=24)

        # Items list
        for item in items:
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", padx=24, pady=4)
            ctk.CTkLabel(row, text=f"• {item['product_name']}",
                         font=FONTS["body"], text_color=COLORS["text_dark"]
                        ).pack(side="left")
            ctk.CTkLabel(row,
                         text=f"{item['quantity']:.1f} {item['unit']}  ×  ₹{item['unit_price']:.2f}  =  ₹{item['line_total']:.2f}",
                         font=FONTS["body"], text_color=COLORS["text_muted"]
                        ).pack(side="right")

        ctk.CTkFrame(scroll, fg_color=COLORS["tbl_select"], height=2).pack(fill="x", padx=24, pady=8)
        ctk.CTkLabel(scroll,
                     text=f"Total Amount:  ₹{p['total_amount']:,.2f}",
                     font=FONTS["num_md"], text_color=COLORS["kpi_green"]
                    ).pack(anchor="e", padx=24, pady=(0, 16))

        ctk.CTkLabel(scroll,
                     text="📦  Stock has been updated for all items.",
                     font=FONTS["body_bold"], text_color=COLORS["btn_success"]
                    ).pack(pady=(0, 16), padx=24)

        ctk.CTkButton(dlg, text="Close",
                      font=FONTS["button"], fg_color=COLORS["btn_primary"],
                      height=48, corner_radius=16,
                      command=dlg.destroy
                     ).pack(fill="x", padx=24, pady=16)

    # ─────────────────────────────────────────────────────────────
    # GRN History
    # ─────────────────────────────────────────────────────────────
    def _show_grn_history(self):
        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title("GRN History")
        dlg.geometry("900x560")
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        # Header + search
        top = ctk.CTkFrame(dlg, fg_color=COLORS["bg_main"], corner_radius=0)
        top.pack(fill="x", padx=12, pady=(12, 4))
        ctk.CTkLabel(top, text="📋   GRN History",
                     font=FONTS["subheading"], text_color=COLORS["text_dark"]
                    ).pack(side="left")

        search_var = tk.StringVar()
        ctk.CTkEntry(top, textvariable=search_var,
                     placeholder_text="Search GRN no. or supplier…",
                     font=FONTS["input"], height=40, width=260,
                     border_color=COLORS["border_focus"], fg_color=COLORS["bg_card"]
                    ).pack(side="right")

        frame = ctk.CTkFrame(dlg, fg_color=COLORS["bg_card"], corner_radius=16)
        frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # ttk styles applied globally via styles.py

        cols   = ("grn", "date", "supplier", "items", "total")
        heads  = ("GRN Number", "Date", "Supplier", "Items", "Total ₹")
        widths = (120, 150, 260, 70, 120)
        tree   = ttk.Treeview(frame, columns=cols, show="headings",
                               style="GRN.Treeview", selectmode="browse")
        for col, head, w in zip(cols, heads, widths):
            tree.heading(col, text=head)
            anch = "e" if col in ("items", "total") else "w"
            tree.column(col, width=w, anchor=anch, minwidth=50)

        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=6)
        vsb.grid(row=0, column=1, sticky="ns", pady=6)
        tree.tag_configure("alt", background=COLORS["tbl_row_alt"])

        def load(q=""):
            purchases = self.db.get_purchases(search=q)
            tree.delete(*tree.get_children())
            for i, p in enumerate(purchases):
                _, pitems = self.db.get_purchase_by_id(p["purchase_id"])
                tag = "alt" if i % 2 == 0 else ""
                tree.insert("", "end", iid=str(p["purchase_id"]), values=(
                    p["grn_number"],
                    p["purchase_date"][:16],
                    p["supplier_name"],
                    len(pitems),
                    f"{p['total_amount']:,.2f}",
                ), tags=(tag,))

        search_var.trace_add("write", lambda *_: load(search_var.get().strip()))
        load()

        def view_detail(event=None):
            sel = tree.selection()
            if not sel:
                return
            self._show_grn_receipt(int(sel[0]))

        tree.bind("<Double-1>", view_detail)
        ctk.CTkButton(dlg, text="👁  View GRN Details",
                      font=FONTS["button"], fg_color=COLORS["btn_primary"],
                      height=44, corner_radius=10,
                      command=view_detail
                     ).pack(side="left", padx=16, pady=8)

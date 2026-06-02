"""
screen_billing.py — POS Billing Screen (Phase 1 Core)
Keyboard shortcuts: F2=Search, F8=Hold, F10=Print & Save, ESC=Clear Cart, Del=Remove Item
Large fonts, colorful, designed for 60+ age users.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from config import COLORS, FONTS, PAYMENT_MODES


class BillingScreen(ctk.CTkFrame):
    def __init__(self, parent, db, current_user, app):
        super().__init__(parent, fg_color=COLORS["bg_main"], corner_radius=0)
        self.db           = db
        self.current_user = current_user
        self.app          = app
        self.cart         = []          # list of cart item dicts
        self.search_results = []
        self.search_popup = None
        self.cust_results = []          # customer-name autocomplete results
        self.cust_popup   = None
        self._pending_udhaar        = 0.0   # BIL-5: outstanding due of selected customer
        self._selected_customer_id  = None  # BIL-5: customer id
        self._build()
        self._bind_keys()

    # ─────────────────────────────────────────────────────────────
    # Build UI
    # ─────────────────────────────────────────────────────────────
    def _build(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self._build_top_bar()
        self._build_body()
        self._build_status_bar()

    def _build_top_bar(self):
        top = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0, height=70)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_propagate(False)
        top.grid_columnconfigure(1, weight=1)

        # Title
        ctk.CTkLabel(
            top, text="🧾   New Bill",
            font=FONTS["heading"], text_color=COLORS["text_dark"]
        ).grid(row=0, column=0, padx=20, pady=12, sticky="w")

        # Bill number badge
        bill_no = self.db.next_bill_number()
        self.bill_no_label = ctk.CTkLabel(
            top,
            text=f"Bill: {bill_no}",
            font=FONTS["body_bold"],
            text_color="white",
            fg_color=COLORS["btn_primary"],
            corner_radius=10,
            padx=14, pady=6,
        )
        self.bill_no_label.grid(row=0, column=2, padx=10, pady=12)

        # Customer name (optional)
        ctk.CTkLabel(top, text="Customer:", font=FONTS["body"],
                     text_color=COLORS["text_muted"]).grid(row=0, column=3, padx=(10, 4))
        self.customer_entry = ctk.CTkEntry(
            top, placeholder_text="Walk-in Customer",
            font=FONTS["input"], width=200, height=40,
            border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"],
        )
        self.customer_entry.grid(row=0, column=4, padx=(0, 8))
        # Autocomplete: show matching saved customers as you type
        self.customer_entry.bind("<KeyRelease>", self._on_customer_search)
        self.customer_entry.bind("<Down>", lambda e: self._focus_cust_popup())

        # Udhaar badge — shown only when selected customer has pending credit
        self.udhaar_badge = ctk.CTkLabel(
            top,
            text="",
            font=FONTS["small_bold"],
            text_color="white",
            fg_color=COLORS["btn_warning"],
            corner_radius=8,
            padx=10, pady=4,
        )
        # not gridded here — shown/hidden dynamically in _select_customer

    def _build_body(self):
        body = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        body.grid(row=1, column=0, sticky="nsew", padx=12, pady=8)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=0)
        body.grid_rowconfigure(1, weight=1)

        # ── Search bar ───────────────────────────────────────
        search_frame = ctk.CTkFrame(body, fg_color=COLORS["bg_card"], corner_radius=16, height=62)
        search_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        search_frame.grid_propagate(False)
        search_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(search_frame, text="🔍  F2", font=FONTS["body_bold"],
                     text_color=COLORS["btn_primary"]).grid(row=0, column=0, padx=16, pady=10)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)
        self.search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Type product name or code to search…",
            font=("Segoe UI", 18),
            height=44,
            border_width=2,
            border_color=COLORS["border_focus"],
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_dark"],
            corner_radius=16,
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=9)


        # ── Cart + Right panel ───────────────────────────────
        # Cart table
        cart_frame = ctk.CTkFrame(body, fg_color=COLORS["bg_card"], corner_radius=16)
        cart_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        cart_frame.grid_rowconfigure(0, weight=1)
        cart_frame.grid_columnconfigure(0, weight=1)

        self._build_cart_table(cart_frame)

        # Action buttons — horizontal bar directly beneath the cart list
        self._build_action_buttons(body)

        # Right panel (totals + payment) — spans the cart + button rows
        right_panel = ctk.CTkFrame(body, fg_color="transparent", corner_radius=0,
                                    width=300)
        right_panel.grid(row=1, column=1, rowspan=2, sticky="nsew")
        right_panel.grid_propagate(False)
        right_panel.grid_rowconfigure(0, weight=1)

        self._build_totals_panel(right_panel)

    def _build_cart_table(self, parent):
        # ttk styles applied globally via styles.py

        cols = ("#", "product", "unit", "qty", "price", "disc", "total", "action")
        self.cart_tree = ttk.Treeview(
            parent, columns=cols, show="headings",
            style="Cart.Treeview", selectmode="browse"
        )
        heads  = ("#", "Product Name", "Unit", "Qty", "Price ₹", "Disc ₹", "Total ₹", "")
        widths = (40,  280,           70,     70,    90,       80,       100,      70)
        for col, h, w in zip(cols, heads, widths):
            self.cart_tree.heading(col, text=h)
            anch = "e" if col in ("qty", "price", "disc", "total") else "center"
            self.cart_tree.column(col, width=w, anchor=anch, minwidth=w)

        vsb = ttk.Scrollbar(parent, orient="vertical",   command=self.cart_tree.yview)
        hsb = ttk.Scrollbar(parent, orient="horizontal", command=self.cart_tree.xview)
        self.cart_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.cart_tree.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=(6, 0))
        vsb.grid(row=0, column=1, sticky="ns",  pady=(6, 0), padx=(0, 4))
        hsb.grid(row=1, column=0, sticky="ew",  padx=(6, 0), pady=(0, 4))

        # Double-click to edit qty
        self.cart_tree.bind("<Double-1>", self._edit_cart_item)
        self.cart_tree.bind("<Delete>",   lambda e: self._remove_selected())

        # Cart empty label
        self.cart_empty_label = ctk.CTkLabel(
            parent, text="🛒\n\nCart is empty.\nSearch and add products above.",
            font=("Segoe UI", 16), text_color="#BDBDBD",
            justify="center"
        )

    def _build_totals_panel(self, parent):
        # Scrollable panel so Payment Mode / Cash / Change are always visible
        # on any screen resolution (fixes BIL-4)
        panel = ctk.CTkScrollableFrame(
            parent, fg_color=COLORS["bg_card"],
            corner_radius=14,
            scrollbar_button_color=COLORS["btn_primary"],
        )
        panel.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(panel, text="Bill Summary",
                     font=FONTS["subheading"], text_color=COLORS["btn_primary"]
                    ).pack(pady=(10, 4), padx=16, anchor="w")

        ctk.CTkFrame(panel, fg_color=COLORS["tbl_select"], height=2).pack(fill="x", padx=12)

        # Row helper
        def row(lbl, val_attr, color="#1A1A2E", big=False):
            f = ctk.CTkFrame(panel, fg_color="transparent")
            f.pack(fill="x", padx=16, pady=3)
            font_l = FONTS["body_bold"] if big else FONTS["body"]
            font_v = FONTS["num_sm"]    if big else FONTS["body_bold"]
            ctk.CTkLabel(f, text=lbl, font=font_l, text_color=COLORS["text_muted"]
                        ).pack(side="left")
            lbl_w = ctk.CTkLabel(f, text="₹ 0.00", font=font_v, text_color=color)
            lbl_w.pack(side="right")
            setattr(self, val_attr, lbl_w)

        row("Subtotal :",      "lbl_subtotal")
        row("Discount (₹) :", "lbl_discount", COLORS["btn_warning"])

        ctk.CTkFrame(panel, fg_color=COLORS["btn_primary"], height=2).pack(fill="x", padx=12, pady=4)

        # Grand total — very large
        gt_frame = ctk.CTkFrame(panel, fg_color=COLORS["tbl_select"], corner_radius=16)
        gt_frame.pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(gt_frame, text="TOTAL",
                     font=("Segoe UI", 14, "bold"),
                     text_color=COLORS["btn_primary"]).pack(side="left", padx=12, pady=10)
        self.lbl_grand_total = ctk.CTkLabel(
            gt_frame, text="₹  0.00",
            font=FONTS["num_md"], text_color=COLORS["btn_primary"]
        )
        self.lbl_grand_total.pack(side="right", padx=12)

        ctk.CTkFrame(panel, fg_color=COLORS["tbl_select"], height=2).pack(fill="x", padx=12, pady=(4, 0))

        # Discount entry
        disc_f = ctk.CTkFrame(panel, fg_color="transparent")
        disc_f.pack(fill="x", padx=16, pady=(8, 4))
        ctk.CTkLabel(disc_f, text="Bill Discount (₹):", font=FONTS["body"],
                     text_color=COLORS["text_dark"]).pack(side="left")
        self.discount_var = tk.StringVar(value="0")
        self.discount_var.trace_add("write", lambda *_: self._recalculate())
        self.discount_entry = ctk.CTkEntry(
            disc_f, textvariable=self.discount_var,
            width=90, height=36, font=FONTS["body_bold"],
            border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"]
        )
        self.discount_entry.pack(side="right")

        ctk.CTkFrame(panel, fg_color="#E0E0E0", height=1).pack(fill="x", padx=12, pady=6)

        # Payment mode
        pm_f = ctk.CTkFrame(panel, fg_color="transparent")
        pm_f.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(pm_f, text="Payment Mode:", font=FONTS["body"],
                     text_color=COLORS["text_dark"]).pack(side="left")
        self.payment_mode_var = tk.StringVar(value="Cash")
        pm_menu = ctk.CTkOptionMenu(
            pm_f, variable=self.payment_mode_var,
            values=PAYMENT_MODES,
            font=FONTS["body"], width=130, height=36,
            fg_color=COLORS["btn_primary"], button_color="#005BBE",
            command=self._on_payment_mode_change,
        )
        pm_menu.pack(side="right")

        # Cash tendered & change
        self.cash_frame = ctk.CTkFrame(panel, fg_color="transparent")
        self.cash_frame.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(self.cash_frame, text="Cash Received (₹):", font=FONTS["body"],
                     text_color=COLORS["text_dark"]).pack(side="left")
        self.cash_var = tk.StringVar(value="0")
        self.cash_var.trace_add("write", lambda *_: self._calc_change())
        ctk.CTkEntry(
            self.cash_frame, textvariable=self.cash_var,
            width=90, height=36, font=FONTS["body_bold"],
            border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"]
        ).pack(side="right")

        change_f = ctk.CTkFrame(panel, fg_color="#E8F5E9", corner_radius=10)
        change_f.pack(fill="x", padx=12, pady=(4, 8))
        ctk.CTkLabel(change_f, text="Change Due :", font=FONTS["body_bold"],
                     text_color=COLORS["btn_success"]).pack(side="left", padx=10, pady=8)
        self.lbl_change = ctk.CTkLabel(change_f, text="₹  0.00",
                                        font=FONTS["num_sm"], text_color=COLORS["btn_success"])
        self.lbl_change.pack(side="right", padx=10)

    def _build_action_buttons(self, parent):
        # Horizontal action bar beneath the cart list (row 2, left column)
        btn_panel = ctk.CTkFrame(parent, fg_color="transparent")
        btn_panel.grid(row=2, column=0, sticky="ew", padx=(0, 8), pady=(8, 0))
        for i in range(3):
            btn_panel.grid_columnconfigure(i, weight=1)

        btns = [
            ("🖨️  F10  Print & Save", COLORS["btn_success"], "#28A745", self._save_and_print),
            ("✋  F8   Hold Bill",     COLORS["btn_warning"], "#CC7700", self._hold_bill),
            ("🗑️  ESC  Clear Cart",    COLORS["btn_secondary"],"#263238", self._clear_cart),
        ]
        for idx, (text, fg, hov, cmd) in enumerate(btns):
            ctk.CTkButton(
                btn_panel, text=text,
                font=FONTS["button"],
                fg_color=fg, hover_color=hov,
                height=54, corner_radius=16,
                command=cmd
            ).grid(row=0, column=idx, sticky="ew",
                   padx=(0 if idx == 0 else 8, 0))

    def _build_status_bar(self):
        bar = ctk.CTkFrame(self, fg_color="#1A237E", corner_radius=0, height=30)
        bar.grid(row=2, column=0, sticky="ew")
        bar.grid_propagate(False)

        shortcuts = "  |  ".join([f"{k} = {v}" for k, v in {
            "F2": "Search",  "F8": "Hold",
            "F10": "Print & Save",  "ESC": "Clear Cart",
            "Del": "Remove Item",  "Ctrl+N": "New Bill"
        }.items()])
        ctk.CTkLabel(
            bar, text=f"⌨️  Shortcuts:  {shortcuts}",
            font=("Segoe UI", 12), text_color=COLORS["border_focus"]
        ).pack(side="left", padx=16)

        self.status_label = ctk.CTkLabel(
            bar, text="Ready ✅", font=("Segoe UI", 12), text_color="#A5D6A7"
        )
        self.status_label.pack(side="right", padx=16)

    # ─────────────────────────────────────────────────────────────
    # Keyboard bindings
    # ─────────────────────────────────────────────────────────────
    def _bind_keys(self):
        root = self.winfo_toplevel()
        root.bind("<F2>",        lambda e: self._focus_search())
        root.bind("<F8>",        lambda e: self._hold_bill())
        root.bind("<F10>",       lambda e: self._save_and_print())
        root.bind("<Escape>",    lambda e: self._close_popup_or_clear())
        root.bind("<Control-n>", lambda e: self._new_bill_shortcut())
        root.bind("<Control-N>", lambda e: self._new_bill_shortcut())
        self.search_entry.bind("<Down>",   lambda e: self._focus_popup())
        self.search_entry.bind("<Return>", lambda e: self._focus_popup())

    def _new_bill_shortcut(self):
        """Ctrl+N — clear cart and start a fresh bill."""
        if self.cart:
            if not messagebox.askyesno(
                "New Bill",
                "Start a new bill? Current cart items will be cleared.",
                parent=self.winfo_toplevel()
            ):
                return
        self._clear_cart_silent()
        self._refresh_bill_number()
        self._set_status("🆕  New bill started  (Ctrl+N)")
        self._focus_search()

    def _new_bill_shortcut(self):
        """Ctrl+N — start a fresh bill (BIL-1)."""
        if self.cart:
            if not messagebox.askyesno("New Bill",
                                        "Start a new bill? Current cart items will be cleared.",
                                        parent=self.winfo_toplevel()):
                return
        self._clear_cart_silent()
        self._refresh_bill_number()
        self._set_status("🆕  New bill started  (Ctrl+N)")
        self._focus_search()

    def on_show(self):
        """Called each time we navigate to this screen."""
        if not hasattr(self, "_draft_bill_id"):
            self._draft_bill_id = None
        self._refresh_bill_number()
        self._focus_search()

    # ─────────────────────────────────────────────────────────────
    # Draft resume (called from Bill History)
    # ─────────────────────────────────────────────────────────────
    def load_draft(self, draft_bill_id: int, bill: dict, items: list):
        """Load a held (Draft) bill back into the cart."""
        self._clear_cart_silent()
        self._draft_bill_id = draft_bill_id

        cname = bill.get("customer_name", "")
        if cname and cname != "Walk-in Customer":
            self.customer_entry.delete(0, "end")
            self.customer_entry.insert(0, cname)

        self.discount_var.set(str(int(bill.get("discount", 0)) if float(bill.get("discount", 0)) == int(float(bill.get("discount", 0))) else bill.get("discount", 0)))

        mode = bill.get("payment_mode", "Cash")
        self.payment_mode_var.set(mode)
        self._on_payment_mode_change(mode)

        for it in items:
            self.cart.append({
                "product_id"  : it["product_id"],
                "product_name": it["product_name"],
                "unit"        : it.get("unit", "piece"),
                "quantity"    : it["quantity"],
                "unit_price"  : it["unit_price"],
                "discount"    : it.get("discount", 0),
                "line_total"  : it["line_total"],
            })

        orig_no = bill["bill_number"]
        new_no  = self.db.next_bill_number()
        self.bill_no_label.configure(text=f"Bill: {new_no}  [▶ {orig_no}]")
        self._refresh_cart_tree()
        self._recalculate()
        self._set_status(f"▶️  Draft {orig_no} resumed — press F10 to save.")

    def _refresh_bill_number(self):
        bill_no = self.db.next_bill_number()
        self.bill_no_label.configure(text=f"Bill: {bill_no}")

    # ─────────────────────────────────────────────────────────────
    # Search
    # ─────────────────────────────────────────────────────────────
    def _focus_search(self):
        self.search_entry.focus_set()
        self.search_entry.select_range(0, "end")

    def _on_search_change(self, *_):
        query = self.search_var.get().strip()
        if len(query) < 1:
            self._close_popup()
            return
        results = self.db.search_products_billing(query)
        self.search_results = results
        if results:
            self._show_popup(results)
        else:
            self._close_popup()

    def _show_popup(self, results):
        self._close_popup()

        popup = tk.Toplevel(self.winfo_toplevel())
        popup.overrideredirect(True)
        popup.configure(bg="white")
        popup.attributes("-topmost", True)

        # Position below search entry
        self.search_entry.update_idletasks()
        x = self.search_entry.winfo_rootx()
        y = self.search_entry.winfo_rooty() + self.search_entry.winfo_height() + 2
        w = self.search_entry.winfo_width() + 140
        popup.geometry(f"{w}x{min(len(results)*52+8, 420)}+{x}+{y}")

        listbox = tk.Listbox(
            popup,
            font=("Segoe UI", 15),
            selectbackground=COLORS["btn_primary"],
            selectforeground="white",
            activestyle="none",
            borderwidth=0,
            highlightthickness=1,
            highlightcolor=COLORS["border_focus"],
            cursor="hand2",
        )
        listbox.pack(fill="both", expand=True, padx=2, pady=2)

        for i, p in enumerate(results):
            stock_info = f"  [Stock: {p['current_stock']} {p['unit']}]"
            stock_color = COLORS["btn_danger"] if p["current_stock"] <= 0 else COLORS["btn_success"]
            listbox.insert("end", f"  {p['name']}  —  ₹{p['selling_price']:.2f}{stock_info}")
            if p["current_stock"] <= 0:
                listbox.itemconfig(i, foreground=COLORS["btn_danger"])

        listbox.bind("<Return>",      lambda e: self._select_from_popup(listbox))
        listbox.bind("<Double-1>",    lambda e: self._select_from_popup(listbox))
        listbox.bind("<Escape>",      lambda e: self._close_popup())
        listbox.bind("<FocusOut>",    lambda e: self.after(150, self._close_popup_maybe))

        # Tab or arrow back to search
        self.search_entry.bind("<Escape>", lambda e: self._close_popup())

        self.search_popup   = popup
        self.search_listbox = listbox

    def _focus_popup(self):
        if self.search_popup and self.search_results:
            self.search_listbox.focus()
            self.search_listbox.selection_set(0)

    def _close_popup(self):
        if self.search_popup:
            try:
                self.search_popup.destroy()
            except Exception:
                pass
            self.search_popup   = None
            self.search_listbox = None

    def _close_popup_maybe(self):
        try:
            if self.search_popup and \
               self.search_popup.focus_get() is None:
                self._close_popup()
        except Exception:
            self._close_popup()

    def _select_from_popup(self, listbox):
        sel = listbox.curselection()
        if not sel:
            return
        product = self.search_results[sel[0]]
        self._close_popup()
        self._add_to_cart(product)

    def _close_popup_or_clear(self):
        if self.search_popup:
            self._close_popup()
            self._focus_search()
        else:
            self._clear_cart()

    # ─────────────────────────────────────────────────────────────
    # Customer name autocomplete
    # ─────────────────────────────────────────────────────────────
    def _on_customer_search(self, event=None):
        # Ignore navigation / commit keys so they don't re-open the popup
        if event is not None and event.keysym in (
            "Up", "Down", "Return", "Escape", "Tab"
        ):
            return
        query = self.customer_entry.get().strip()
        if len(query) < 1 or query == "Walk-in Customer":
            self._close_cust_popup()
            self.udhaar_badge.grid_remove()
            return
        self.udhaar_badge.grid_remove()  # hide until a customer is confirmed via autocomplete
        results = self.db.search_customers_billing(query)
        self.cust_results = results
        if results:
            self._show_cust_popup(results)
        else:
            self._close_cust_popup()

    def _show_cust_popup(self, results):
        self._close_cust_popup()

        popup = tk.Toplevel(self.winfo_toplevel())
        popup.overrideredirect(True)
        popup.configure(bg="white")
        popup.attributes("-topmost", True)

        self.customer_entry.update_idletasks()
        x = self.customer_entry.winfo_rootx()
        y = self.customer_entry.winfo_rooty() + self.customer_entry.winfo_height() + 2
        w = max(self.customer_entry.winfo_width(), 260)
        popup.geometry(f"{w}x{min(len(results) * 44 + 8, 360)}+{x}+{y}")

        listbox = tk.Listbox(
            popup,
            font=("Segoe UI", 14),
            selectbackground=COLORS["btn_primary"],
            selectforeground="white",
            activestyle="none",
            borderwidth=0,
            highlightthickness=1,
            highlightcolor=COLORS["border_focus"],
            cursor="hand2",
        )
        listbox.pack(fill="both", expand=True, padx=2, pady=2)

        for c in results:
            phone = f"   📞 {c['phone']}" if c.get("phone") else ""
            bal = c.get("credit_balance") or 0
            bal_txt = f"   • Udhaar ₹{bal:.0f}" if bal else ""
            listbox.insert("end", f"  {c['name']}{phone}{bal_txt}")

        listbox.bind("<Return>",   lambda e: self._select_customer(listbox))
        listbox.bind("<Double-1>", lambda e: self._select_customer(listbox))
        listbox.bind("<Escape>",   lambda e: self._close_cust_popup())
        listbox.bind("<FocusOut>", lambda e: self.after(150, self._close_cust_popup))

        self.cust_popup   = popup
        self.cust_listbox = listbox

    def _focus_cust_popup(self):
        if getattr(self, "cust_popup", None) and self.cust_results:
            self.cust_listbox.focus()
            self.cust_listbox.selection_set(0)

    def _close_cust_popup(self):
        if getattr(self, "cust_popup", None):
            try:
                self.cust_popup.destroy()
            except Exception:
                pass
            self.cust_popup   = None
            self.cust_listbox = None

    def _select_customer(self, listbox):
        sel = listbox.curselection()
        if not sel:
            return
        c = self.cust_results[sel[0]]
        self._close_cust_popup()
        self.customer_entry.delete(0, "end")
        self.customer_entry.insert(0, c["name"])
        # Store selected customer id for due auto-attach
        self._selected_customer_id = c.get("customer_id")

        bal = float(c.get("credit_balance") or 0)
        if bal > 0:
            self.udhaar_badge.configure(text=f"⚠️  Udhaar Pending: ₹{bal:,.2f}")
            self.udhaar_badge.grid(row=0, column=5, padx=(0, 16), pady=12)
            # BIL-5: Auto-attach previous due to bill discount field (show as warning)
            if messagebox.askyesno(
                "Previous Udhaar Detected",
                f"Customer '{c['name']}' has a pending due of ₹{bal:,.2f}.\n\n"
                f"Would you like to collect this due with the new bill?\n\n"
                f"(The due amount will be shown on the bill. Collect separately.)",
                parent=self.winfo_toplevel()
            ):
                self._pending_udhaar = bal
                self._set_status(
                    f"⚠️  Udhaar ₹{bal:,.2f} will be shown on the bill."
                )
            else:
                self._pending_udhaar = 0
        else:
            self.udhaar_badge.grid_remove()
            self._pending_udhaar = 0

        self.search_entry.focus_set()

    # ─────────────────────────────────────────────────────────────
    # Cart management
    # ─────────────────────────────────────────────────────────────
    def _add_to_cart(self, product):
        # Check if already in cart — just increase qty
        for item in self.cart:
            if item["product_id"] == product["product_id"]:
                item["quantity"] += 1
                item["line_total"] = round(
                    item["quantity"] * item["unit_price"] - item["discount"], 2
                )
                self._refresh_cart_tree()
                self._recalculate()
                self.search_var.set("")
                self._focus_search()
                self._set_status(f"✅  Added: {product['name']}")
                return

        # New item
        self.cart.append({
            "product_id"  : product["product_id"],
            "product_name": product["name"],
            "unit"        : product["unit"],
            "quantity"    : 1.0,
            "unit_price"  : product["selling_price"],
            "discount"    : 0.0,
            "line_total"  : product["selling_price"],
        })
        self._refresh_cart_tree()
        self._recalculate()
        self.search_var.set("")
        self._focus_search()
        self._set_status(f"✅  Added: {product['name']}")

    def _refresh_cart_tree(self):
        self.cart_tree.delete(*self.cart_tree.get_children())

        if not self.cart:
            self.cart_tree.grid_remove()
            self.cart_empty_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self.cart_empty_label.place_forget()
            self.cart_tree.grid()

        for i, item in enumerate(self.cart, 1):
            tag = "alt" if i % 2 == 0 else ""
            self.cart_tree.insert("", "end", iid=str(i-1), values=(
                i,
                item["product_name"],
                item["unit"],
                f"{item['quantity']:.2f}",
                f"{item['unit_price']:.2f}",
                f"{item['discount']:.2f}",
                f"{item['line_total']:.2f}",
                "✏️ Edit",
            ), tags=(tag,))

        self.cart_tree.tag_configure("alt", background=COLORS["tbl_row_alt"])

    def _edit_cart_item(self, event):
        sel = self.cart_tree.selection()
        if not sel:
            return
        idx  = int(sel[0])
        item = self.cart[idx]

        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title(f"Edit: {item['product_name']}")
        dlg.geometry("380x300")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        ctk.CTkLabel(dlg, text=item["product_name"],
                     font=FONTS["subheading"], text_color=COLORS["btn_primary"],
                     wraplength=340).pack(pady=(20, 8), padx=20)

        def field(parent, label, default):
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.pack(fill="x", padx=20, pady=4)
            ctk.CTkLabel(f, text=label, font=FONTS["body"],
                         text_color=COLORS["text_dark"], width=120, anchor="w").pack(side="left")
            var = tk.StringVar(value=str(default))
            ctk.CTkEntry(f, textvariable=var, font=FONTS["body_bold"],
                         height=38, width=140,
                         border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"]
                        ).pack(side="right")
            return var

        qty_var   = field(dlg, f"Quantity ({item['unit']}):", item["quantity"])
        price_var = field(dlg, "Unit Price (₹):",            item["unit_price"])
        disc_var  = field(dlg, "Item Discount (₹):",         item["discount"])

        def apply_edit():
            try:
                qty   = float(qty_var.get())
                price = float(price_var.get())
                disc  = float(disc_var.get())
                if qty <= 0:
                    messagebox.showerror("Error", "Quantity must be greater than 0.", parent=dlg)
                    return
                if price < 0:
                    messagebox.showerror("Error", "Price cannot be negative.", parent=dlg)
                    return
                item["quantity"]   = qty
                item["unit_price"] = price
                item["discount"]   = disc
                item["line_total"] = round(qty * price - disc, 2)
                self._refresh_cart_tree()
                self._recalculate()
                dlg.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers.", parent=dlg)

        def remove_item():
            self.cart.pop(idx)
            self._refresh_cart_tree()
            self._recalculate()
            dlg.destroy()

        btn_row = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=12)
        ctk.CTkButton(btn_row, text="✅  Update", font=FONTS["button"],
                      fg_color=COLORS["btn_success"], command=apply_edit,
                      height=44).pack(side="left", fill="x", expand=True, padx=(0,6))
        ctk.CTkButton(btn_row, text="🗑️  Remove", font=FONTS["button"],
                      fg_color=COLORS["btn_danger"], command=remove_item,
                      height=44).pack(side="left", fill="x", expand=True)

    def _remove_selected(self):
        sel = self.cart_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        name = self.cart[idx]["product_name"]
        if messagebox.askyesno("Remove Item",
                               f"Remove  '{name}'  from cart?",
                               parent=self.winfo_toplevel()):
            self.cart.pop(idx)
            self._refresh_cart_tree()
            self._recalculate()

    def _clear_cart(self):
        if self.cart:
            if not messagebox.askyesno("Clear Cart",
                                       "Clear all items from cart?",
                                       parent=self.winfo_toplevel()):
                return
        self.cart = []
        self.discount_var.set("0")
        self.cash_var.set("0")
        self.customer_entry.delete(0, "end")
        self.udhaar_badge.grid_remove()
        self.payment_mode_var.set("Cash")
        self._refresh_cart_tree()
        self._recalculate()
        self._refresh_bill_number()
        self._set_status("🗑️  Cart cleared.")
        self._focus_search()

    # ─────────────────────────────────────────────────────────────
    # Calculations
    # ─────────────────────────────────────────────────────────────
    def _recalculate(self):
        subtotal = sum(item["line_total"] for item in self.cart)
        try:
            discount = float(self.discount_var.get() or 0)
        except ValueError:
            discount = 0
        discount   = min(discount, subtotal)
        grand_total = max(0, round(subtotal - discount, 2))

        self.lbl_subtotal.configure(text=f"₹ {subtotal:,.2f}")
        self.lbl_discount.configure(text=f"₹ {discount:,.2f}")
        self.lbl_grand_total.configure(text=f"₹  {grand_total:,.2f}")

        self._calc_change()

    def _calc_change(self):
        try:
            grand = float(self.lbl_grand_total.cget("text").replace("₹", "").replace(",", "").strip())
            cash  = float(self.cash_var.get() or 0)
        except ValueError:
            cash = grand = 0
        change = max(0, round(cash - grand, 2))
        self.lbl_change.configure(text=f"₹  {change:,.2f}",
                                   text_color=COLORS["btn_success"] if change >= 0 else COLORS["btn_danger"])

    def _on_payment_mode_change(self, mode):
        if mode == "Cash":
            self.cash_frame.pack(fill="x", padx=16, pady=4)
        else:
            self.cash_frame.pack_forget()

    def _get_bill_data(self):
        """Return dict with current bill totals."""
        subtotal = sum(item["line_total"] for item in self.cart)
        try:
            discount = float(self.discount_var.get() or 0)
        except ValueError:
            discount = 0
        discount    = min(discount, subtotal)
        grand_total = max(0, round(subtotal - discount, 2))
        try:
            amount_paid = float(self.cash_var.get() or 0)
        except ValueError:
            amount_paid = grand_total
        change_due  = max(0, round(amount_paid - grand_total, 2))
        mode        = self.payment_mode_var.get()

        return {
            "customer_name": self.customer_entry.get().strip() or "Walk-in Customer",
            "subtotal"     : subtotal,
            "discount"     : discount,
            "grand_total"  : grand_total,
            "payment_mode" : mode,
            "amount_paid"  : amount_paid if mode == "Cash" else grand_total,
            "change_due"   : change_due,
        }

    # ─────────────────────────────────────────────────────────────
    # Bill actions
    # ─────────────────────────────────────────────────────────────
    def _save_and_print(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart",
                                   "Please add at least one product to the bill.",
                                   parent=self.winfo_toplevel())
            return

        bill_data = self._get_bill_data()

        # Confirm payment for Cash mode
        mode = self.payment_mode_var.get()
        if mode == "Cash":
            try:
                paid = float(self.cash_var.get() or 0)
            except ValueError:
                paid = 0
            if paid < bill_data["grand_total"]:
                if not messagebox.askyesno(
                    "Underpayment",
                    f"Cash received ₹{paid:.2f} is less than total ₹{bill_data['grand_total']:.2f}.\n"
                    f"Save as credit?",
                    parent=self.winfo_toplevel()
                ):
                    self._focus_search()
                    return
                bill_data["payment_mode"] = "Credit (Udhaar)"

        bill_id = self.db.save_bill(
            bill_data, self.cart, self.current_user["user_id"]
        )

        # If this was a resumed draft, delete the original draft now
        if getattr(self, "_draft_bill_id", None):
            self.db.delete_draft(self._draft_bill_id)
            self._draft_bill_id = None

        # Show receipt
        self._show_receipt(bill_id)

        # Clear for next bill
        self._clear_cart_silent()
        self._refresh_bill_number()
        self._set_status("✅  Bill saved successfully!")

        # Refresh dashboard if cached
        if "dashboard" in self.app.screens:
            self.app.screens["dashboard"].on_show()

    def _hold_bill(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart",
                                   "Nothing to hold — cart is empty.",
                                   parent=self.winfo_toplevel())
            return
        bill_data = self._get_bill_data()
        bill_id   = self.db.save_draft_bill(
            bill_data, self.cart, self.current_user["user_id"]
        )
        messagebox.showinfo("Bill Held",
                            f"Bill saved as draft.\nYou can resume it from Bill History.",
                            parent=self.winfo_toplevel())
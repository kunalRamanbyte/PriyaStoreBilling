"""
screen_billing.py — POS Billing Screen (Phase 1 Core)
Keyboard shortcuts: F2=Search, F8=Hold, F10=Print & Save, ESC=Clear Cart, Del=Remove Item
Large fonts, colorful, designed for 60+ age users.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from config import COLORS, FONTS, PAYMENT_MODES
from ui_utils import place_popup
from lang import t
from webcam_scanner import WebcamScanner


class BillingScreen(ctk.CTkFrame):
    _RESPONSIVE_SUMMARY_BREAK = 1000
    _RESPONSIVE_BUTTON_BREAK = 860

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
        self._change_adjusted       = 0.0   # available change of selected customer
        self._selected_customer_id  = None  # BIL-5: customer id
        self._selected_customer_name = None
        self._inline_entry   = None   # active inline-edit Entry widget
        self._build()
        self._bind_keys()
        self.bind("<Configure>", self._on_resize)

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
        top = ctk.CTkFrame(self, fg_color=COLORS.get("bg_header", "#FDFBFF"), corner_radius=0, height=58)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_propagate(False)
        top.grid_columnconfigure(1, weight=1)
        self.top_bar = top

        title_box = ctk.CTkFrame(top, fg_color="transparent")
        title_box.grid(row=0, column=0, padx=16, pady=8, sticky="w")
        ctk.CTkLabel(
            title_box, text="Priya Store",
            font=("Segoe UI Semibold", 15, "bold"), text_color="#F43F8C"
        ).pack(anchor="w")
        L = self.app.current_lang
        ctk.CTkLabel(
            title_box, text=t("Bright Billing Dashboard", L),
            font=("Segoe UI", 11), text_color="#64748B"
        ).pack(anchor="w")

        self.clock_label = ctk.CTkLabel(
            top,
            text="",
            font=("Segoe UI", 12),
            text_color=COLORS.get("text_muted", "#475569"),
        )
        self.clock_label.grid(row=0, column=1, padx=8, sticky="e")
        self._update_clock()

        _user_name = self.current_user.get("name") or self.current_user.get("username", "User")
        _user_role = (self.current_user.get("role") or "").title()
        self.user_badge = ctk.CTkLabel(
            top,
            text=f"◉  {_user_name}  •  {_user_role}",
            font=("Segoe UI", 12, "bold"),
            text_color="white",
            fg_color="#A855F7",
            corner_radius=14,
            padx=14,
            pady=7,
        )
        self.user_badge.grid(row=0, column=2, padx=16, pady=10, sticky="e")

    def _build_body(self):
        body = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        body.grid(row=1, column=0, sticky="nsew", padx=12, pady=8)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=0)
        body.grid_rowconfigure(2, weight=1)
        self.body_frame = body

        self.context_frame = ctk.CTkFrame(body, fg_color="transparent")
        self.context_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        self.context_frame.grid_columnconfigure(0, weight=1)
        self.context_left = ctk.CTkFrame(self.context_frame, fg_color="transparent")
        self.context_left.grid(row=0, column=0, sticky="w")

        bill_no = self.db.next_bill_number()
        self.bill_no_label = self._make_chip(
            self.context_left, f"Bill: {bill_no}", "#0EA5E9", "white", 44
        )
        self.bill_no_label.pack(side="left", padx=(0, 8))

        self.customer_entry = ctk.CTkEntry(
            self.context_left,
            placeholder_text=t("Customer: Search or type customer name...", self.app.current_lang),
            font=("Segoe UI", 14),
            width=260,
            height=42,
            border_width=1,
            border_color=COLORS.get("border_customer_entry", "#99F6E4"),
            fg_color=COLORS.get("bg_customer_entry", "#F8FFFE"),
            text_color=COLORS["text_dark"],
            corner_radius=14,
        )
        self.customer_entry.pack(side="left", fill="x", expand=False, padx=(0, 8))
        self.customer_entry.bind("<KeyRelease>", self._on_customer_search)
        self.customer_entry.bind("<Down>", lambda e: self._focus_cust_popup())

        ctk.CTkButton(
            self.context_left,
            text="+ New",
            font=("Segoe UI", 11, "bold"),
            fg_color="#10B981",
            hover_color="#059669",
            height=42,
            width=72,
            corner_radius=14,
            command=self._add_new_customer_dialog,
        ).pack(side="left", padx=(0, 8))

        # Walk-in indicator — shown when no saved customer is linked
        self.walkin_badge = self._make_chip(
            self.context_left, "Walk-in", "#94A3B8", "white", 44
        )
        self.walkin_badge.pack(side="left", padx=(0, 4))

        # Gridded dynamically in _select_customer; hidden until a credit customer is picked
        self.udhaar_badge = self._make_chip(
            self.context_frame, "", "#FF9800", "white", 42
        )

        # Gridded dynamically in _select_customer; hidden until customer has change balance
        self.change_badge = self._make_chip(
            self.context_frame, "", "#10B981", "white", 42
        )

        search_frame = ctk.CTkFrame(
            body,
            fg_color=COLORS.get("bg_summary_panel", "#FFF8FB"),
            corner_radius=18,
            height=62,
            border_width=1,
            border_color=COLORS.get("border_summary_panel", "#E9D5FF"),
        )
        search_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        search_frame.grid_propagate(False)
        search_frame.grid_columnconfigure(0, weight=1)
        self.search_frame = search_frame

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)
        self.search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text=t("Scan barcode or search product…   (F2)", self.app.current_lang),
            font=("Segoe UI", 15),
            height=44,
            border_width=1,
            border_color=COLORS.get("border_summary_card", "#E9D5FF"),
            fg_color=COLORS.get("bg_summary_card", "#FFFFFF"),
            text_color=COLORS.get("text_summary_row", "#1A1A2E"),
            corner_radius=16,
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=12, pady=9)

        self.scan_btn = ctk.CTkButton(
            search_frame,
            text=t("Scan", self.app.current_lang),
            font=("Segoe UI", 13, "bold"),
            fg_color=COLORS.get("btn_primary", "#3B82F6"),
            hover_color="#2563EB",
            width=100,
            height=44,
            corner_radius=16,
            command=self._open_webcam_scanner
        )
        self.scan_btn.grid(row=0, column=1, padx=(0, 12), pady=9)

        cart_frame = ctk.CTkFrame(
            body,
            fg_color=COLORS.get("bg_summary_card", "#FFFFFF"),
            corner_radius=18,
            border_width=1,
            border_color=COLORS.get("border_summary_card", "#DDD6FE")
        )
        cart_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 10))
        cart_frame.grid_rowconfigure(0, weight=1)
        cart_frame.grid_columnconfigure(0, weight=1)
        self.cart_frame = cart_frame

        self._build_cart_table(cart_frame)
        self._build_action_buttons(body)

        right_panel = ctk.CTkFrame(body, fg_color="transparent", corner_radius=0, width=290)
        right_panel.grid(row=2, column=1, rowspan=2, sticky="nsew")
        right_panel.grid_propagate(False)
        right_panel.grid_rowconfigure(0, weight=1)
        self.right_panel = right_panel

        self._build_totals_panel(right_panel)

    def _build_cart_table(self, parent):
        # ttk styles applied globally via styles.py

        cols = ("#", "product", "unit", "qty", "price", "disc", "total", "action")
        self.cart_tree = ttk.Treeview(
            parent, columns=cols, show="headings",
            style="Cart.Treeview", selectmode="browse"
        )
        L = self.app.current_lang
        heads  = ("#", t("Product Name_col", L), t("Unit", L), t("Qty", L),
                  t("Price ₹", L), t("Disc ₹", L), t("Total ₹", L), "")
        widths = (40,  200,           65,     65,    85,       75,       90,       50)
        for col, h, w in zip(cols, heads, widths):
            self.cart_tree.heading(col, text=h)
            anch = "e" if col in ("qty", "price", "disc", "total") else "center"
            self.cart_tree.column(col, width=w, anchor=anch, minwidth=w)

        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=vsb.set)

        self.cart_tree.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=(6, 6))
        vsb.grid(row=0, column=1, sticky="ns", pady=(6, 6), padx=(0, 4))

        # Click Qty/Price to inline-edit; double-click other cols for full dialog
        self.cart_tree.bind("<Button-1>", self._on_cart_click)
        self.cart_tree.bind("<Double-1>", self._on_cart_double_click)
        self.cart_tree.bind("<Delete>",   lambda e: self._remove_selected())

        # Cart empty label
        self.cart_empty_label = ctk.CTkLabel(
            parent, text=t("Cart is empty.\nSearch and add products above.", self.app.current_lang),
            font=("Segoe UI", 16), text_color="#BDBDBD",
            justify="center"
        )

    def _build_totals_panel(self, parent):
        panel = ctk.CTkFrame(
            parent,
            fg_color=COLORS.get("bg_summary_panel", "#FFF4F8"),
            corner_radius=18,
            border_width=1,
            border_color=COLORS.get("border_summary_panel", "#F5D0FE"),
        )
        panel.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        panel.grid_columnconfigure(0, weight=1)
        self.summary_panel = panel

        _font_lbl = ("Segoe UI", 12)
        _font_lbl_b = ("Segoe UI", 12, "bold")
        _font_val = ("Segoe UI", 13, "bold")
        _font_total = ("Segoe UI Semibold", 20, "bold")
        _font_entry = ("Segoe UI", 12, "bold")

        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(10, 2))
        ctk.CTkLabel(header, text=t("Summary", self.app.current_lang), font=("Segoe UI", 15, "bold"),
                     text_color="#F43F8C").pack(side="left")
        ctk.CTkFrame(panel, fg_color=COLORS.get("border_summary_panel", "#F5D0FE"), height=2).pack(fill="x", padx=10)

        def row(lbl, val_attr, color=None):
            if color is None:
                color = COLORS.get("text_summary_row", "#1A1A2E")
            f = ctk.CTkFrame(panel, fg_color=COLORS.get("bg_summary_card", "#FFFFFF"), corner_radius=12, border_width=1,
                             border_color=COLORS.get("border_summary_card", "#E9D5FF"))
            f.pack(fill="x", padx=12, pady=3)
            f.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(f, text=lbl, font=_font_lbl, text_color=COLORS["text_muted"],
                         anchor="w").grid(row=0, column=0, sticky="w", padx=10, pady=6)
            lbl_w = ctk.CTkLabel(f, text="₹ 0.00", font=_font_val, text_color=color, anchor="e")
            lbl_w.grid(row=0, column=1, sticky="e", padx=10, pady=6)
            setattr(self, val_attr, lbl_w)

        row(t("Subtotal :", self.app.current_lang), "lbl_subtotal")
        row(t("Discount (₹) :", self.app.current_lang), "lbl_discount", "#EF4444")

        # Udhaar row — hidden until a customer with pending udhaar is selected
        udhaar_row = ctk.CTkFrame(
            panel,
            fg_color=COLORS.get("bg_summary_udhaar", "#FFF7ED"),
            corner_radius=12,
            border_width=1,
            border_color=COLORS.get("border_summary_udhaar", "#FED7AA")
        )
        udhaar_row.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(udhaar_row, text=t("Prev. Udhaar", self.app.current_lang), font=_font_lbl,
                     text_color=COLORS.get("text_summary_udhaar", "#C2410C"), anchor="w").grid(row=0, column=0, sticky="w", padx=10, pady=6)
        self.lbl_udhaar_adj = ctk.CTkLabel(
            udhaar_row, text="₹ 0.00", font=_font_val,
            text_color=COLORS.get("text_summary_udhaar", "#C2410C"), anchor="e"
        )
        self.lbl_udhaar_adj.grid(row=0, column=1, sticky="e", padx=10, pady=6)
        self.udhaar_row_frame = udhaar_row   # shown/hidden dynamically; do NOT pack yet

        # Change Used row — hidden until a customer with change balance is selected and adjusted
        change_row = ctk.CTkFrame(
            panel,
            fg_color=COLORS.get("bg_summary_change", "#F0FDF4"),
            corner_radius=12,
            border_width=1,
            border_color=COLORS.get("border_summary_change", "#BBF7D0")
        )
        change_row.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(change_row, text=t("Change Used", self.app.current_lang), font=_font_lbl,
                     text_color=COLORS.get("text_summary_change", "#15803D"), anchor="w").grid(row=0, column=0, sticky="w", padx=10, pady=6)
        self.lbl_change_adj = ctk.CTkLabel(
            change_row, text="₹ 0.00", font=_font_val,
            text_color=COLORS.get("text_summary_change", "#15803D"), anchor="e"
        )
        self.lbl_change_adj.grid(row=0, column=1, sticky="e", padx=10, pady=6)
        self.change_row_frame = change_row   # shown/hidden dynamically; do NOT pack yet

        self._totals_divider = ctk.CTkFrame(panel, fg_color=COLORS.get("border_summary_card", "#E9D5FF"), height=2)
        self._totals_divider.pack(fill="x", padx=10, pady=4)

        gt_frame = ctk.CTkFrame(panel, fg_color="#B91CFF", corner_radius=14)
        gt_frame.pack(fill="x", padx=10, pady=3)
        gt_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(gt_frame, text=t("TOTAL", self.app.current_lang),
                     font=("Segoe UI", 13, "bold"),
                     text_color="white").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.lbl_grand_total = ctk.CTkLabel(
            gt_frame, text="₹  0.00",
            font=_font_total, text_color="white", anchor="e"
        )
        self.lbl_grand_total.grid(row=0, column=1, padx=10, pady=8, sticky="e")

        disc_f = ctk.CTkFrame(
            panel,
            fg_color=COLORS.get("bg_summary_card", "#FFFFFF"),
            corner_radius=12,
            border_width=1,
            border_color=COLORS.get("border_summary_entry", "#FDE68A")
        )
        disc_f.pack(fill="x", padx=12, pady=(6, 3))
        disc_f.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(disc_f, text=t("Bill Discount (₹):", self.app.current_lang), font=_font_lbl,
                     text_color=COLORS["text_dark"], anchor="w").grid(row=0, column=0, sticky="w", padx=10, pady=6)
        self.discount_var = tk.StringVar(value="0")
        self.discount_var.trace_add("write", lambda *_: self._recalculate())
        self.discount_entry = ctk.CTkEntry(
            disc_f, textvariable=self.discount_var,
            height=30, width=84, font=_font_entry,
            border_width=0,
            fg_color=COLORS.get("fg_summary_entry", "#FEFCE8"),
            text_color=COLORS.get("text_summary_row", "#1A1A2E"),
            justify="right"
        )
        self.discount_entry.grid(row=0, column=1, sticky="e", padx=(8, 10), pady=6)

        pm_f = ctk.CTkFrame(
            panel,
            fg_color=COLORS.get("bg_summary_card", "#FFFFFF"),
            corner_radius=12,
            border_width=1,
            border_color=COLORS.get("border_summary_card", "#E9D5FF")
        )
        pm_f.pack(fill="x", padx=12, pady=3)
        pm_f.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(pm_f, text=t("Payment Mode", self.app.current_lang), font=_font_lbl,
                     text_color=COLORS["text_dark"], anchor="w").grid(row=0, column=0, sticky="w", padx=10, pady=6)
        self.payment_mode_var = tk.StringVar(value="Cash")
        self.payment_mode_menu = ctk.CTkOptionMenu(
            pm_f, variable=self.payment_mode_var,
            values=PAYMENT_MODES,
            font=_font_lbl, height=30, width=116, corner_radius=10,
            fg_color=COLORS.get("fg_summary_pm_btn", "#FFFFFF"),
            button_color=COLORS.get("fg_summary_pm_btn", "#FFFFFF"),
            button_hover_color=COLORS.get("border_summary_card", "#F3E8FF"),
            text_color=COLORS.get("text_summary_pm_btn", "#7C3AED"),
            dropdown_fg_color=COLORS.get("dropdown_fg_summary_pm", "#FFFFFF"),
            dropdown_text_color=COLORS.get("dropdown_text_summary_pm", "#334155"),
            command=self._on_payment_mode_change,
        )
        self.payment_mode_menu.grid(row=0, column=1, sticky="e", padx=(8, 10), pady=6)

        self.cash_frame = ctk.CTkFrame(
            panel,
            fg_color=COLORS.get("bg_summary_card", "#FFFFFF"),
            corner_radius=12,
            border_width=1,
            border_color=COLORS.get("border_summary_cash", "#A7F3D0")
        )
        self.cash_frame.pack(fill="x", padx=12, pady=3)
        self.cash_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(self.cash_frame, text=t("Cash Received (₹)", self.app.current_lang), font=_font_lbl,
                     text_color=COLORS["text_dark"], anchor="w").grid(row=0, column=0, sticky="w", padx=10, pady=6)
        self.cash_var = tk.StringVar(value="0")
        self.cash_var.trace_add("write", lambda *_: self._calc_change())
        self.cash_entry = ctk.CTkEntry(
            self.cash_frame, textvariable=self.cash_var,
            height=30, width=84, font=_font_entry,
            border_width=0,
            fg_color=COLORS.get("bg_summary_cash", "#ECFDF5"),
            text_color=COLORS.get("text_summary_cash", "#059669"),
            justify="right"
        )
        self.cash_entry.grid(row=0, column=1, sticky="e", padx=(8, 10), pady=6)

        change_f = ctk.CTkFrame(panel, fg_color="#14CBA8", corner_radius=12)
        change_f.pack(fill="x", padx=10, pady=(5, 8))
        change_f.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(change_f, text=t("Change Due :", self.app.current_lang), font=_font_lbl_b,
                     text_color="white", anchor="w").grid(row=0, column=0, padx=10, pady=6, sticky="w")
        self.lbl_change = ctk.CTkLabel(change_f, text="₹  0.00",
                                       font=("Segoe UI Semibold", 16, "bold"), text_color="white",
                                       anchor="e")
        self.lbl_change.grid(row=0, column=1, padx=10, pady=8, sticky="e")


    def _build_action_buttons(self, parent):
        btn_panel = ctk.CTkFrame(parent, fg_color="transparent")
        btn_panel.grid(row=3, column=0, sticky="ew", padx=(0, 10), pady=(10, 0))
        self.action_panel = btn_panel

        L = self.app.current_lang
        btns = [
            (t("F10 Print & Save", L), "#10B981", "#059669", self._save_and_print),
            (t("F8 Hold Bill", L), "#F59E0B", "#D97706", self._hold_bill),
            (t("ESC Clear Cart", L), "#F43F5E", "#E11D48", self._clear_cart),
        ]
        self.action_buttons = []
        for text, fg, hov, cmd in btns:
            btn = ctk.CTkButton(
                btn_panel, text=text,
                font=("Segoe UI", 13, "bold"),
                fg_color=fg, hover_color=hov,
                height=44, corner_radius=14,
                command=cmd
            )
            self.action_buttons.append(btn)

        self._layout_action_buttons(stacked=False)

    def _build_status_bar(self):
        bar = ctk.CTkFrame(self, fg_color="#7E22CE", corner_radius=0, height=30)
        bar.grid(row=2, column=0, sticky="ew")
        bar.grid_propagate(False)

        shortcuts = "  |  ".join([f"{k} = {v}" for k, v in {
            "F2": "Search",  "F8": "Hold",
            "F10": "Print & Save",  "ESC": "Clear Cart",
            "Del": "Remove Item",  "Ctrl+N": "New Bill"
        }.items()])
        ctk.CTkLabel(
            bar, text=f"Shortcuts:  {shortcuts}",
            font=("Segoe UI", 11), text_color="#E9D5FF"
        ).pack(side="left", padx=16)

        self.status_label = ctk.CTkLabel(
            bar, text="Ready", font=("Segoe UI", 11, "bold"), text_color="#A7F3D0"
        )
        self.status_label.pack(side="right", padx=16)

    def _make_chip(self, parent, text, fg_color, text_color, height):
        return ctk.CTkLabel(
            parent,
            text=text,
            font=("Segoe UI", 12, "bold"),
            text_color=text_color,
            fg_color=fg_color,
            corner_radius=14,
            height=height,
            padx=14,
            pady=6,
        )

    def _on_resize(self, _event=None):
        self.after_idle(self._apply_responsive_layout)

    def _apply_responsive_layout(self):
        width = self.winfo_width()
        if width <= 1 or not hasattr(self, "right_panel"):
            return

        summary_below = width < self._RESPONSIVE_SUMMARY_BREAK
        buttons_stacked = width < self._RESPONSIVE_BUTTON_BREAK

        if summary_below:
            self.cart_frame.grid_configure(row=2, column=0, columnspan=2, padx=(0, 0), pady=(0, 10))
            self.right_panel.grid_configure(row=3, column=0, columnspan=2, rowspan=1, sticky="ew", pady=(0, 0))
            self.action_panel.grid_configure(row=4, column=0, columnspan=2, padx=(0, 0), pady=(10, 0))
            self.right_panel.configure(width=0)
        else:
            self.cart_frame.grid_configure(row=2, column=0, columnspan=1, padx=(0, 10), pady=(0, 0))
            self.right_panel.grid_configure(row=2, column=1, columnspan=1, rowspan=2, sticky="nsew", pady=(0, 0))
            self.action_panel.grid_configure(row=3, column=0, columnspan=1, padx=(0, 10), pady=(10, 0))
            self.right_panel.configure(width=290)

        if width < 980:
            self.context_left.grid_configure(row=0, column=0, sticky="ew")
            self.customer_entry.configure(width=220)
        else:
            self.context_left.grid_configure(row=0, column=0, sticky="w")
            self.customer_entry.configure(width=260)

        self._layout_action_buttons(stacked=buttons_stacked)

    def _layout_action_buttons(self, stacked: bool):
        for i in range(3):
            self.action_panel.grid_columnconfigure(i, weight=0)
        for btn in self.action_buttons:
            btn.grid_forget()

        if stacked:
            self.action_panel.grid_columnconfigure(0, weight=1)
            for idx, btn in enumerate(self.action_buttons):
                btn.grid(row=idx, column=0, sticky="ew", pady=(0 if idx == 0 else 8, 0))
        else:
            for i in range(3):
                self.action_panel.grid_columnconfigure(i, weight=1)
            for idx, btn in enumerate(self.action_buttons):
                btn.grid(row=0, column=idx, sticky="ew", padx=(0 if idx == 0 else 8, 0))

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
        self.search_entry.bind("<Return>", self._on_search_enter)

    def _new_bill_shortcut(self):
        """Ctrl+N — start a fresh bill."""
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
        self._selected_customer_id = bill.get("customer_id")
        self._selected_customer_name = cname if self._selected_customer_id else None
        if cname and cname != "Walk-in Customer":
            self.customer_entry.delete(0, "end")
            self.customer_entry.insert(0, cname)

        if self._selected_customer_id:
            cust = self.db.get_customer_by_id(self._selected_customer_id)
            if cust:
                self._pending_udhaar = float(bill.get("udhaar_adjustment") or 0)
                self._change_adjusted = float(bill.get("change_adjustment") or 0)

                cur_credit = float(cust.get("credit_balance") or 0)
                cur_change = float(cust.get("change_balance") or 0)
                if cur_credit > 0:
                    self.udhaar_badge.configure(text=f"⚠️  Udhaar Pending: ₹{cur_credit:,.2f}")
                    self.udhaar_badge.grid(row=0, column=1, sticky="e", padx=(12, 0), pady=2)
                else:
                    self.udhaar_badge.grid_remove()

                if cur_change > 0:
                    self.change_badge.configure(text=f"💰  Change Available: ₹{cur_change:,.2f}")
                    self.change_badge.grid(row=0, column=2, sticky="e", padx=(12, 0), pady=2)
                else:
                    self.change_badge.grid_remove()
        else:
            self._pending_udhaar = 0.0
            self._change_adjusted = 0.0
            self.udhaar_badge.grid_remove()
            self.change_badge.grid_remove()

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

    def _on_search_enter(self, event=None):
        query = self.search_var.get().strip()
        if not query:
            return
        
        # Exact barcode match
        product = self.db.get_product_by_code(query)
        if product:
            self._close_popup()
            self._add_to_cart(product)
            return
            
        # Only 1 result in search popup
        if len(self.search_results) == 1:
            self._close_popup()
            self._add_to_cart(self.search_results[0])
            return
            
        self._focus_popup()

    def _open_webcam_scanner(self):
        WebcamScanner(self, self.app, callback=self._on_webcam_scanned)

    def _on_webcam_scanned(self, code):
        if not code:
            return
        product = self.db.get_product_by_code(code)
        if product:
            self._add_to_cart(product)
            self._set_status(f"✅ Scanned and added: {product['name']}")
        else:
            messagebox.showwarning(
                t("Warning", self.app.current_lang),
                t("No product found for code", self.app.current_lang).format(code=code),
                parent=self.winfo_toplevel()
            )

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
        if self._selected_customer_id and query != self._selected_customer_name:
            self._clear_selected_customer()
        if len(query) < 1 or query == "Walk-in Customer":
            self._close_cust_popup()
            self._clear_selected_customer()
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
            change_bal = c.get("change_balance") or 0
            bal_txt = f"   • Udhaar ₹{bal:.0f}" if bal else ""
            change_txt = f"   • Change ₹{change_bal:.0f}" if change_bal else ""
            listbox.insert("end", f"  {c['name']}{phone}{bal_txt}{change_txt}")

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
        self._selected_customer_name = c["name"]

        bal = float(c.get("credit_balance") or 0)
        if bal > 0:
            self.udhaar_badge.configure(text=f"⚠️  Udhaar Pending: ₹{bal:,.2f}")
            self.udhaar_badge.grid(row=0, column=1, sticky="e", padx=(12, 0), pady=2)
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

        # Available change balance
        change_bal = float(c.get("change_balance") or 0)
        if change_bal > 0:
            self.change_badge.configure(text=f"💰  Change Available: ₹{change_bal:,.2f}")
            self.change_badge.grid(row=0, column=2, sticky="e", padx=(12, 0), pady=2)
            if messagebox.askyesno(
                t("Change Balance Detected", self.app.current_lang),
                f"Customer '{c['name']}' has an available change balance of ₹{change_bal:,.2f}.\n\n"
                f"Would you like to adjust/use this change balance in the new bill?",
                parent=self.winfo_toplevel()
            ):
                self._change_adjusted = change_bal
                self._set_status(f"💰  Change ₹{change_bal:,.2f} will be adjusted in the bill.")
            else:
                self._change_adjusted = 0.0
        else:
            self.change_badge.grid_remove()
            self._change_adjusted = 0.0

        self._update_walkin_badge()
        self.search_entry.focus_set()

    def _update_walkin_badge(self):
        """Show 'Walk-in' badge if no saved customer linked, hide it otherwise."""
        try:
            if self._selected_customer_id:
                self.walkin_badge.pack_forget()
            else:
                if not self.walkin_badge.winfo_ismapped():
                    self.walkin_badge.pack(side="left", padx=(0, 4))
        except Exception:
            pass

    def _add_new_customer_dialog(self):
        """Open a small dialog to create a new customer and auto-select them."""
        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title("Add New Customer")
        place_popup(dlg, 380, 280)
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        ctk.CTkLabel(dlg, text="Add New Customer",
                     font=FONTS["subheading"], text_color=COLORS["btn_primary"]
                     ).pack(pady=(18, 10), padx=20, anchor="w")

        def field(parent, label, placeholder=""):
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.pack(fill="x", padx=20, pady=4)
            ctk.CTkLabel(f, text=label, font=FONTS["body"],
                         text_color=COLORS["text_dark"], width=90, anchor="w").pack(side="left")
            var = tk.StringVar()
            ctk.CTkEntry(f, textvariable=var, placeholder_text=placeholder,
                         font=FONTS["body"], height=36, width=200,
                         border_color=COLORS["border_focus"],
                         fg_color=COLORS["bg_input"]).pack(side="left", padx=(6, 0))
            return var

        name_var    = field(dlg, "Name *",    "Full name")
        phone_var   = field(dlg, "Phone",     "Mobile number")
        address_var = field(dlg, "Address",   "Shop / area")

        def save():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("Required", "Customer name is required.", parent=dlg)
                return
            try:
                cid = self.db.add_customer({
                    "name":    name,
                    "phone":   phone_var.get().strip(),
                    "address": address_var.get().strip(),
                })
                dlg.destroy()
                # Auto-select the newly created customer
                self.customer_entry.delete(0, "end")
                self.customer_entry.insert(0, name)
                self._selected_customer_id   = cid
                self._selected_customer_name = name
                self._pending_udhaar         = 0.0
                self._change_adjusted        = 0.0
                self._update_walkin_badge()
                self._set_status(f"✅  New customer '{name}' added and selected.")
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=dlg)

        btn_row = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=12)
        ctk.CTkButton(btn_row, text="✅  Save Customer", font=FONTS["button"],
                      fg_color=COLORS["btn_success"], height=42,
                      command=save).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(btn_row, text="Cancel", font=FONTS["button"],
                      fg_color=COLORS["btn_secondary"], height=42,
                      command=dlg.destroy).pack(side="left", fill="x", expand=True)
        dlg.bind("<Return>", lambda e: save())

    def _clear_selected_customer(self):
        self._selected_customer_id = None
        self._selected_customer_name = None
        self._pending_udhaar = 0.0
        self._change_adjusted = 0.0
        try:
            self.udhaar_badge.grid_remove()
            self.change_badge.grid_remove()
        except Exception:
            pass
        self._update_walkin_badge()

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
        self._cancel_inline_edit()
        self.cart_tree.delete(*self.cart_tree.get_children())

        if not self.cart:
            self.cart_tree.grid_remove()
            self.cart_empty_label.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self.cart_empty_label.place_forget()
            self.cart_tree.grid()

        _row_colors = COLORS["ROW_COLORS"]
        for i, item in enumerate(self.cart, 1):
            tag = f"row{(i-1) % len(_row_colors)}"
            qty_disp = (f"{item['quantity']:.3f}" if item["unit"] == "kg"
                        else f"{item['quantity']:.2f}")
            self.cart_tree.insert("", "end", iid=str(i-1), values=(
                i,
                item["product_name"],
                item["unit"],
                qty_disp,
                f"{item['unit_price']:.2f}",
                f"{item['discount']:.2f}",
                f"{item['line_total']:.2f}",
                "✏️ Edit",
            ), tags=(tag,))

        for idx, color in enumerate(_row_colors):
            self.cart_tree.tag_configure(f"row{idx}", background=color, foreground=COLORS["text_dark"])

    # ─────────────────────────────────────────────────────────────
    # Inline cell editing (Qty / Price) — click a cell to type
    # ─────────────────────────────────────────────────────────────
    _INLINE_COL_MAP = {"#4": ("qty", "quantity"), "#5": ("price", "unit_price")}

    def _on_cart_click(self, event):
        """Single-click: inline-edit Qty/Price, or open full dialog for ✏️."""
        region = self.cart_tree.identify_region(event.x, event.y)
        col = self.cart_tree.identify_column(event.x)
        item_iid = self.cart_tree.identify_row(event.y)

        if region != "cell" or not item_iid:
            if self._inline_entry:
                self._commit_inline_edit()
            return

        if col in self._INLINE_COL_MAP:
            # Already editing this exact cell? keep focus
            if (self._inline_entry
                    and getattr(self, "_inline_iid", None) == item_iid
                    and getattr(self, "_inline_col", None) == col):
                return
            if self._inline_entry:
                self._commit_inline_edit()
            self.after(10, lambda iid=item_iid, c=col:
                       self._start_inline_edit(iid, c))
        elif col == "#8":                               # ✏️ action column
            if self._inline_entry:
                self._commit_inline_edit()
            self.cart_tree.selection_set(item_iid)
            self.after(10, lambda: self._edit_cart_item(None))
        else:
            if self._inline_entry:
                self._commit_inline_edit()

    def _on_cart_double_click(self, event):
        """Double-click: full edit dialog (skip for Qty/Price — inline handles those)."""
        col = self.cart_tree.identify_column(event.x)
        if col in self._INLINE_COL_MAP:
            return                                      # inline edit already active
        self._cancel_inline_edit()
        self._edit_cart_item(event)

    def _start_inline_edit(self, item_iid, col_id):
        """Overlay a temporary Entry widget on the clicked Qty or Price cell."""
        self._cancel_inline_edit()

        tree_col, col_key = self._INLINE_COL_MAP[col_id]

        try:
            bbox = self.cart_tree.bbox(item_iid, tree_col)
        except Exception:
            return
        if not bbox:
            return

        x, y, w, h = bbox
        idx = int(item_iid)
        if idx >= len(self.cart):
            return

        current_val = self.cart[idx][col_key]

        entry = tk.Entry(
            self.cart_tree,
            font=("Segoe UI", 15),
            justify="right",
            bg="#FEFCE8",
            fg="#1A1A2E",
            relief="solid",
            bd=1,
            highlightthickness=2,
            highlightcolor="#A855F7",
            highlightbackground="#E9D5FF",
            selectbackground="#DDD6FE",
            selectforeground="#1A1A2E",
        )

        # Format display value
        if col_key == "quantity" and self.cart[idx]["unit"] == "kg":
            display_val = f"{current_val:.3f}"
        else:
            display_val = f"{current_val:g}"

        entry.insert(0, display_val)
        entry.select_range(0, "end")
        entry.place(x=x, y=y, width=max(w, 70), height=h)
        entry.focus_set()

        self._inline_entry   = entry
        self._inline_iid     = item_iid
        self._inline_col     = col_id
        self._inline_col_key = col_key

        entry.bind("<Return>",   lambda e: self._commit_inline_edit())
        entry.bind("<KP_Enter>", lambda e: self._commit_inline_edit())
        entry.bind("<Escape>",   lambda e: self._cancel_inline_edit())

        def _tab(e):
            self._commit_and_advance()
            return "break"
        entry.bind("<Tab>", _tab)

        # FocusOut — commit only if *this* entry is still active
        _ref = entry
        entry.bind("<FocusOut>",
                    lambda e, ref=_ref: self.after(
                        50, lambda: self._commit_if_same(ref)))

    def _commit_if_same(self, expected_entry):
        """Commit only when the active inline entry matches *expected_entry*."""
        if self._inline_entry is expected_entry:
            self._commit_inline_edit()

    def _commit_inline_edit(self):
        """Validate and apply the value from the inline edit Entry."""
        if not self._inline_entry:
            return

        entry = self._inline_entry
        try:
            new_val = float(entry.get().strip())
        except (ValueError, AttributeError):
            self._cancel_inline_edit()
            return

        idx     = int(self._inline_iid)
        col_key = self._inline_col_key

        if col_key == "quantity" and new_val <= 0:
            self._cancel_inline_edit()
            return
        if col_key == "unit_price" and new_val < 0:
            self._cancel_inline_edit()
            return

        self.cart[idx][col_key]      = new_val
        self.cart[idx]["line_total"] = round(
            self.cart[idx]["quantity"] * self.cart[idx]["unit_price"]
            - self.cart[idx]["discount"], 2
        )

        self._inline_entry = None
        try:
            entry.destroy()
        except Exception:
            pass

        self._refresh_cart_tree()
        self._recalculate()

    def _commit_and_advance(self):
        """Commit, then move to the next editable cell or the search bar."""
        if not self._inline_entry:
            return

        entry   = self._inline_entry
        iid     = self._inline_iid
        col     = self._inline_col
        col_key = self._inline_col_key

        try:
            new_val = float(entry.get().strip())
        except (ValueError, AttributeError):
            self._cancel_inline_edit()
            return

        idx = int(iid)
        if col_key == "quantity" and new_val <= 0:
            self._cancel_inline_edit()
            return
        if col_key == "unit_price" and new_val < 0:
            self._cancel_inline_edit()
            return

        self.cart[idx][col_key]      = new_val
        self.cart[idx]["line_total"] = round(
            self.cart[idx]["quantity"] * self.cart[idx]["unit_price"]
            - self.cart[idx]["discount"], 2
        )

        self._inline_entry = None
        try:
            entry.destroy()
        except Exception:
            pass

        self._refresh_cart_tree()
        self._recalculate()

        # Advance: qty (#4) → price (#5) of same row; price → search bar
        if col == "#4":
            self.after(50, lambda: self._start_inline_edit(str(idx), "#5"))
        else:
            self._focus_search()

    def _cancel_inline_edit(self):
        """Discard the inline edit without saving."""
        if self._inline_entry:
            try:
                self._inline_entry.destroy()
            except Exception:
                pass
            self._inline_entry = None

    def _edit_cart_item(self, event):
        sel = self.cart_tree.selection()
        if not sel:
            return
        idx  = int(sel[0])
        item = self.cart[idx]

        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title(f"Edit: {item['product_name']}")
        place_popup(dlg, 380, 340)
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

        is_kg = item["unit"] == "kg"
        if is_kg:
            kg_int = int(item["quantity"])
            gm_int = round((item["quantity"] - kg_int) * 1000)
            kg_var = field(dlg, "Kilograms:",       kg_int)
            gm_var = field(dlg, "Grams (0–999):",   gm_int)
            qty_var = None
        else:
            qty_var = field(dlg, f"Quantity ({item['unit']}):", item["quantity"])
            kg_var = gm_var = None
        price_var = field(dlg, "Unit Price (₹):",            item["unit_price"])
        disc_var  = field(dlg, "Item Discount (₹):",         item["discount"])

        def apply_edit():
            try:
                if is_kg:
                    qty = float(kg_var.get() or 0) + float(gm_var.get() or 0) / 1000
                else:
                    qty = float(qty_var.get())
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
        self._clear_selected_customer()
        self.discount_var.set("0")
        self.cash_var.set("0")
        self.customer_entry.delete(0, "end")
        self.payment_mode_var.set("Cash")
        self._on_payment_mode_change("Cash")
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
        discount    = min(discount, subtotal)
        bill_total  = max(0, round(subtotal - discount, 2))
        udhaar      = self._pending_udhaar
        change_adj  = min(self._change_adjusted, bill_total)
        grand_total = round(bill_total + udhaar - change_adj, 2)

        self.lbl_subtotal.configure(text=f"₹ {subtotal:,.2f}")
        self.lbl_discount.configure(text=f"₹ {discount:,.2f}")

        if udhaar > 0:
            self.lbl_udhaar_adj.configure(text=f"₹ {udhaar:,.2f}")
            self.udhaar_row_frame.pack(fill="x", padx=12, pady=3,
                                       before=self._totals_divider)
        else:
            self.udhaar_row_frame.pack_forget()

        if change_adj > 0:
            self.lbl_change_adj.configure(text=f"₹ {change_adj:,.2f}")
            self.change_row_frame.pack(fill="x", padx=12, pady=3,
                                       before=self._totals_divider)
        else:
            self.change_row_frame.pack_forget()

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
                                   text_color="white")
        if self._selected_customer_id:
            if cash < grand and cash > 0:
                self._set_status(f"ℹ️  Unpaid ₹{grand - cash:,.2f} will go to Udhaar.")
            elif cash > grand:
                self._set_status(f"ℹ️  Surplus ₹{cash - grand:,.2f} will go to Change Balance.")

    def _on_payment_mode_change(self, mode):
        if mode == "Cash":
            self.cash_frame.pack(fill="x", padx=12, pady=3)
        else:
            self.cash_frame.pack_forget()
        # Warn immediately if Udhaar chosen with no linked customer
        if mode == "Credit (Udhaar)" and not self._selected_customer_id:
            self._set_status("⚠️  Credit (Udhaar) requires a saved customer — search and select one.")

    def _get_bill_data(self):
        """Return dict with current bill totals."""
        subtotal = sum(item["line_total"] for item in self.cart)
        try:
            discount = float(self.discount_var.get() or 0)
        except ValueError:
            discount = 0
        discount         = min(discount, subtotal)
        bill_total       = max(0, round(subtotal - discount, 2))
        udhaar_adj       = self._pending_udhaar
        change_adj       = min(self._change_adjusted, bill_total)
        total_to_collect = round(bill_total + udhaar_adj - change_adj, 2)
        try:
            amount_paid = float(self.cash_var.get() or 0)
        except ValueError:
            amount_paid = total_to_collect
        change_due  = max(0, round(amount_paid - total_to_collect, 2))
        mode        = self.payment_mode_var.get()
        customer_name = self.customer_entry.get().strip() or "Walk-in Customer"
        customer_id = (
            self._selected_customer_id
            if self._selected_customer_id and customer_name == self._selected_customer_name
            else None
        )

        if mode == "Credit (Udhaar)":
            amt_paid_val = 0.0
            change_due_val = 0.0
        elif mode == "Cash":
            amt_paid_val = amount_paid
            change_due_val = change_due
        else:
            amt_paid_val = total_to_collect
            change_due_val = 0.0

        return {
            "customer_id"      : customer_id,
            "customer_name"    : customer_name,
            "subtotal"         : subtotal,
            "discount"         : discount,
            "grand_total"      : bill_total,         # items total only (no udhaar inflation)
            "udhaar_adjustment": udhaar_adj,
            "change_adjustment": change_adj,
            "payment_mode"     : mode,
            "amount_paid"      : amt_paid_val,
            "change_due"       : change_due_val,
        }


    # ─────────────────────────────────────────────────────────────
    # Bill actions
    # ─────────────────────────────────────────────────────────────
    def _check_stock(self) -> bool:
        """Warn if any cart line exceeds the live stock on hand.

        Returns True to proceed with the sale, False to abort. Stock is
        re-read from the DB at save time (not the cached search results) so a
        bill held earlier or a concurrent GRN is reflected. The operator can
        still confirm an oversell — this only prevents silent negative stock.
        """
        shortfalls = []
        for item in self.cart:
            pid = item.get("product_id")
            if pid is None:
                continue
            prod = self.db.get_product_by_id(pid)
            if not prod:
                continue
            on_hand = float(prod.get("current_stock") or 0)
            if float(item["quantity"]) > on_hand:
                shortfalls.append(
                    f"  • {item['product_name']}: need {item['quantity']}, "
                    f"in stock {on_hand:g}"
                )
        if not shortfalls:
            return True
        return messagebox.askyesno(
            "Insufficient Stock",
            "These items exceed available stock:\n\n"
            + "\n".join(shortfalls)
            + "\n\nSelling them will make stock go negative.\nSave the bill anyway?",
            parent=self.winfo_toplevel(),
        )

    def _save_and_print(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart",
                                   "Please add at least one product to the bill.",
                                   parent=self.winfo_toplevel())
            return

        if not self._check_stock():
            return

        bill_data = self._get_bill_data()
        is_walk_in = not bill_data.get("customer_id")
        total_to_collect = round(bill_data["grand_total"] + bill_data.get("udhaar_adjustment", 0), 2)

        # Cash mode: if walk-in and cash field untouched (0), assume exact payment
        mode = self.payment_mode_var.get()
        if mode == "Cash":
            try:
                paid = float(self.cash_var.get() or 0)
            except ValueError:
                paid = 0
            if paid == 0 and is_walk_in:
                # Walk-in exact cash — no prompt needed
                bill_data["amount_paid"] = total_to_collect
                bill_data["change_due"]  = 0.0
            elif paid < total_to_collect:
                if is_walk_in:
                    # Walk-in underpayment — can't save as credit without a customer
                    messagebox.showwarning(
                        "Underpayment",
                        f"Cash received ₹{paid:.2f} is less than total ₹{total_to_collect:.2f}.\n\n"
                        f"Please enter the correct cash amount, or select a saved customer to save as credit.",
                        parent=self.winfo_toplevel()
                    )
                    self.cash_entry.focus_set()
                    return
                else:
                    if not messagebox.askyesno(
                        "Underpayment",
                        f"Cash received ₹{paid:.2f} is less than total ₹{total_to_collect:.2f}.\n"
                        f"Save as credit (Udhaar) for {bill_data['customer_name']}?",
                        parent=self.winfo_toplevel()
                    ):
                        self._focus_search()
                        return
                    bill_data["payment_mode"] = "Credit (Udhaar)"

        if bill_data["payment_mode"] == "Credit (Udhaar)" and not bill_data.get("customer_id"):
            messagebox.showwarning(
                "Select Customer",
                "Credit bills must be linked to a saved customer.\n\n"
                "Select the customer from the Customer search dropdown, then save again.",
                parent=self.winfo_toplevel()
            )
            self.customer_entry.focus_set()
            return

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
        self._clear_cart_silent()
        self._refresh_bill_number()
        self._set_status("✋  Bill held. Cart cleared for next bill.")

    # ─────────────────────────────────────────────────────────────
    # Status bar
    # ─────────────────────────────────────────────────────────────
    def _update_clock(self):
        try:
            now = datetime.now().strftime("%d %b %Y  •  %I:%M:%S %p")
            self.clock_label.configure(text=now)
            self.after(1000, self._update_clock)
        except Exception:
            pass

    def _set_status(self, text: str):
        """Update the status bar message."""
        try:
            self.status_label.configure(text=text)
        except Exception:
            pass

    # ─────────────────────────────────────────────────────────────
    # Silent cart clear (no confirmation prompt)
    # ─────────────────────────────────────────────────────────────
    def _clear_cart_silent(self):
        """Clear cart without prompting — used after save or hold."""
        self.cart = []
        self._draft_bill_id        = None
        self._clear_selected_customer()
        self.discount_var.set("0")
        self.cash_var.set("0")
        self.customer_entry.delete(0, "end")
        self.payment_mode_var.set("Cash")
        self._on_payment_mode_change("Cash")
        self._refresh_cart_tree()
        self._recalculate()

    # ─────────────────────────────────────────────────────────────
    # Receipt popup (shown after every successful bill save)
    # ─────────────────────────────────────────────────────────────
    def _show_receipt(self, bill_id: int):
        """Formatted bill receipt with Thermal Print / PDF (A4) options."""
        bill, items = self.db.get_bill_by_id(bill_id)
        if not bill:
            return

        settings = {
            "shop_name"   : self.db.get_setting("shop_name",     "Priya Store"),
            "shop_address": self.db.get_setting("shop_address",  ""),
            "shop_city"   : self.db.get_setting("shop_city",     ""),
            "shop_phone"  : self.db.get_setting("shop_phone",    ""),
            "shop_gst"    : self.db.get_setting("shop_gst",      ""),
            "cashier"     : self.current_user.get("username",    ""),
        }

        raw_dt = str(bill.get("bill_date", "") or "")
        date_str, time_str = raw_dt[:10], raw_dt
        try:
            _dt = datetime.strptime(raw_dt[:19], "%Y-%m-%d %H:%M:%S")
            date_str = _dt.strftime("%Y-%m-%d")
            time_str = _dt.strftime("%d %b %Y  \u2022  %I:%M %p")
        except Exception:
            pass

        BLUE, GREEN, MUTED, DARK = "#1D4ED8", "#16A34A", "#64748B", "#1A1A2E"

        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title("Bill Receipt")
        place_popup(dlg, 500, 640)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        scroll = ctk.CTkScrollableFrame(dlg, fg_color="#FFFFFF")
        scroll.pack(fill="both", expand=True, padx=2, pady=2)

        def hline(color=BLUE, h=2, pady=(8, 8)):
            ctk.CTkFrame(scroll, fg_color=color, height=h).pack(fill="x", padx=24, pady=pady)

        # Shop header
        ctk.CTkLabel(scroll, text=settings["shop_name"] or "Priya Store",
                     font=("Segoe UI Semibold", 22, "bold"), text_color=BLUE).pack(pady=(16, 0))
        addr = ", ".join([p for p in (settings["shop_address"], settings["shop_city"]) if p])
        if addr:
            ctk.CTkLabel(scroll, text=addr, font=("Segoe UI", 12), text_color=MUTED).pack()
        if settings["shop_phone"]:
            ctk.CTkLabel(scroll, text=f"\U0001F4DE  {settings['shop_phone']}",
                         font=("Segoe UI", 12), text_color=MUTED).pack(pady=(2, 0))
        if settings["shop_gst"]:
            ctk.CTkLabel(scroll, text=f"GSTIN: {settings['shop_gst']}",
                         font=("Segoe UI", 11), text_color=MUTED).pack()

        hline()

        def meta_row(left, right, rcolor=DARK):
            f = ctk.CTkFrame(scroll, fg_color="transparent")
            f.pack(fill="x", padx=24, pady=1)
            ctk.CTkLabel(f, text=left, font=("Segoe UI", 13, "bold"),
                         text_color=DARK, anchor="w").pack(side="left")
            ctk.CTkLabel(f, text=right, font=("Segoe UI", 13, "bold"),
                         text_color=rcolor, anchor="e").pack(side="right")

        meta_row(f"Bill: {bill['bill_number']}", date_str)
        meta_row(f"Customer: {bill.get('customer_name', 'Walk-in Customer')}",
                 bill.get("payment_mode", "Cash"), rcolor=BLUE)

        hline(color="#E2E8F0", h=1, pady=(10, 4))

        # Items table
        tbl = ctk.CTkFrame(scroll, fg_color="transparent")
        tbl.pack(fill="x", padx=24, pady=(2, 2))
        tbl.grid_columnconfigure(0, weight=1)
        for c in (1, 2, 3, 4):
            tbl.grid_columnconfigure(c, weight=0, minsize=56)

        for c, h in enumerate(["Item", "Qty", "Rate", "Disc", "Amt"]):
            ctk.CTkLabel(tbl, text=h, font=("Segoe UI", 12, "bold"), text_color=MUTED,
                         anchor="w" if c == 0 else "e").grid(
                row=0, column=c, sticky="w" if c == 0 else "e",
                pady=(0, 4), padx=(0, 0) if c == 0 else (6, 0))

        for r, it in enumerate(items, start=1):
            ctk.CTkLabel(tbl, text=it["product_name"], font=("Segoe UI", 12),
                         text_color=DARK, anchor="w").grid(row=r, column=0, sticky="w", pady=2)
            ctk.CTkLabel(tbl, text=f"{it['quantity']:g}", font=("Segoe UI", 12),
                         text_color=DARK, anchor="e").grid(row=r, column=1, sticky="e", padx=(6, 0))
            ctk.CTkLabel(tbl, text=f"{it['unit_price']:.0f}", font=("Segoe UI", 12),
                         text_color=DARK, anchor="e").grid(row=r, column=2, sticky="e", padx=(6, 0))
            ctk.CTkLabel(tbl, text=f"{it.get('discount', 0):.0f}", font=("Segoe UI", 12),
                         text_color=DARK, anchor="e").grid(row=r, column=3, sticky="e", padx=(6, 0))
            ctk.CTkLabel(tbl, text=f"{it['line_total']:.2f}", font=("Segoe UI", 12, "bold"),
                         text_color=DARK, anchor="e").grid(row=r, column=4, sticky="e", padx=(6, 0))

        hline(color="#E2E8F0", h=1, pady=(8, 6))

        def tot_row(lbl, val, color=DARK, bold=False):
            f = ctk.CTkFrame(scroll, fg_color="transparent")
            f.pack(fill="x", padx=24, pady=1)
            ctk.CTkLabel(f, text=lbl, font=("Segoe UI", 13, "bold" if bold else "normal"),
                         text_color=color, anchor="w").pack(side="left")
            ctk.CTkLabel(f, text=val, font=("Segoe UI", 13, "bold"),
                         text_color=color, anchor="e").pack(side="right")

        tot_row("Subtotal:", f"\u20b9 {bill['subtotal']:,.2f}")
        if bill.get("discount"):
            tot_row("Discount:", f"\u2212 \u20b9 {bill['discount']:,.2f}", color="#EF4444")
        udhaar_adj = float(bill.get("udhaar_adjustment") or 0)
        if udhaar_adj > 0:
            tot_row("Bill Total:", f"\u20b9 {bill['grand_total']:,.2f}")
            tot_row(f"\u26a0\ufe0f  Prev. Udhaar Cleared:", f"+ \u20b9 {udhaar_adj:,.2f}", color="#C2410C")

        total_display = round(bill['grand_total'] + udhaar_adj, 2)
        gt = ctk.CTkFrame(scroll, fg_color="#DBEAFE", corner_radius=10)
        gt.pack(fill="x", padx=24, pady=(6, 6))
        ctk.CTkLabel(gt, text="TOTAL TO COLLECT:" if udhaar_adj > 0 else "GRAND TOTAL:",
                     font=("Segoe UI", 14, "bold"),
                     text_color=BLUE, anchor="w").pack(side="left", padx=14, pady=10)
        ctk.CTkLabel(gt, text=f"\u20b9 {total_display:,.2f}",
                     font=("Segoe UI Semibold", 16, "bold"), text_color=BLUE,
                     anchor="e").pack(side="right", padx=14, pady=10)

        tot_row("Amount Paid:", f"\u20b9 {bill.get('amount_paid', 0):,.2f}", color=GREEN)
        tot_row("Change Due:",  f"\u20b9 {bill.get('change_due', 0):,.2f}", color=GREEN)

        hline(pady=(10, 8))

        ctk.CTkLabel(scroll, text="Thank you for shopping with us!  \U0001F64F",
                     font=("Segoe UI", 13, "bold"), text_color=GREEN).pack(pady=(0, 2))
        if time_str:
            ctk.CTkLabel(scroll, text=time_str, font=("Segoe UI", 11),
                         text_color=MUTED).pack(pady=(0, 12))

        def _thermal():
            try:
                from bill_printer import print_thermal
                paper = self.db.get_setting("paper_width", "80mm") or "80mm"
                ok, msg = print_thermal(bill, items, settings, paper)
                if ok:
                    messagebox.showinfo("Printed", f"Receipt sent to: {msg}", parent=dlg)
                else:
                    messagebox.showerror("Thermal Print Failed", str(msg), parent=dlg)
            except Exception as e:
                messagebox.showerror("Thermal Print Error", str(e), parent=dlg)

        def _pdf():
            try:
                from bill_printer import generate_pdf_bill, open_file
                import tkinter.filedialog as fd
                path = fd.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF file", "*.pdf")],
                    initialfile=f"Bill_{bill['bill_number']}.pdf",
                    title="Save PDF Bill",
                    parent=dlg,
                )
                if path:
                    generate_pdf_bill(bill, items, settings, path)
                    open_file(path)
            except Exception as e:
                messagebox.showerror("PDF Error", str(e), parent=dlg)

        btn_row = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(4, 12))
        ctk.CTkButton(btn_row, text="\U0001F5A8  Thermal Print", font=("Segoe UI", 13, "bold"),
                      fg_color="#3B82F6", hover_color="#2563EB", height=46, corner_radius=12,
                      command=_thermal).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(btn_row, text="\U0001F4C4  PDF / A4", font=("Segoe UI", 13, "bold"),
                      fg_color="#A855F7", hover_color="#9333EA", height=46, corner_radius=12,
                      command=_pdf).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(btn_row, text="\u2705  Done", font=("Segoe UI", 13, "bold"),
                      fg_color="#22C55E", hover_color="#16A34A", height=46, corner_radius=12,
                      command=dlg.destroy).pack(side="left", fill="x", expand=True)

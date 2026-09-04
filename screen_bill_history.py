"""
screen_bill_history.py — Bill History screen
View, reprint, and void past bills with date filter.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import date, timedelta
from config import COLORS, FONTS, RADII, METRICS, GUTTERS
from responsive import (ResponsiveMixin, fit_columns, widget_scaling,
                        autohide_scrollbar)
from ui_utils import place_popup
from lang import t


class BillHistoryScreen(ResponsiveMixin, ctk.CTkFrame):
    def __init__(self, parent, db, current_user, app):
        super().__init__(parent, fg_color=COLORS["bg_main"], corner_radius=0)
        self.db           = db
        self.current_user = current_user
        self.app          = app
        self._build()

    # -- Direction B primitives ------------------------------
    def _card(self, parent, **kw):
        return ctk.CTkFrame(parent, fg_color=COLORS["bg_card"],
                            corner_radius=RADII["card"], border_width=1,
                            border_color=COLORS["hairline"], **kw)

    def _pill(self, parent, text, kind="plain", command=None, width=None,
              height=None):
        """44px pill. Only `primary` is a solid fill; everything else is a
        tint with dark ink, which is how Direction B ranks actions."""
        tints = {
            "primary": (COLORS["accent_action"], COLORS["btn_primary_h"], COLORS["on_accent"]),
            "action":  (COLORS["accent_action_tint"], COLORS["glass_glow"], COLORS["accent_action_fg"]),
            "money":   (COLORS["accent_money_tint"], COLORS["accent_money_tint"], COLORS["accent_money_fg"]),
            "expiry":  (COLORS["accent_expiry_tint"], COLORS["accent_expiry_tint"], COLORS["accent_expiry_fg"]),
            "stock":   (COLORS["accent_stock_tint"], COLORS["accent_stock_tint"], COLORS["accent_stock_fg"]),
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

    def _stat_chip(self, parent, kind):
        """A 34px status count chip in its own hue tint."""
        tints = {
            "paid":  (COLORS["accent_money_tint"], COLORS["accent_money_fg"]),
            "due":   (COLORS["accent_expiry_tint"], COLORS["accent_expiry_fg"]),
            "void":  (COLORS["accent_danger_tint"], COLORS["accent_danger_fg"]),
            "draft": (COLORS["accent_counts_tint"], COLORS["accent_counts_fg"]),
        }
        bg, ink = tints[kind]
        chip = ctk.CTkLabel(parent, text="", font=FONTS["small_bold"],
                            fg_color=bg, text_color=ink,
                            corner_radius=RADII["pill_sm"],
                            height=METRICS["control_sm"])
        return chip

    def _build(self):
        L = self.app.current_lang

        # -- Header band -------------------------------------
        header = ctk.CTkFrame(self, fg_color="transparent",
                              height=METRICS["header"])
        self._header = header
        header.pack(fill="x", padx=28)
        header.pack_propagate(False)

        titles = ctk.CTkFrame(header, fg_color="transparent")
        titles.pack(side="left", fill="y")
        ctk.CTkLabel(titles, text=t("Bill History", L),
                     font=("Segoe UI Semibold", 26, "bold"),
                     text_color=COLORS["text_dark"], anchor="w"
                     ).pack(anchor="w", pady=(16, 0))
        # The old "N bill(s) found" counter becomes the artboard's summary
        # line: count, money collected, and the range being shown.
        self.count_label = ctk.CTkLabel(
            titles, text="", font=FONTS["small"],
            text_color=COLORS["text_muted"], anchor="w")
        self.count_label.pack(anchor="w")

        search_wrap = ctk.CTkFrame(header, fg_color="transparent")
        search_wrap.pack(side="right", fill="y")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._load_bills())
        self.search_entry = ctk.CTkEntry(
            search_wrap, textvariable=self.search_var,
            font=FONTS["label_form"], width=300,
            height=METRICS["control"],
            corner_radius=RADII["input"], border_width=1,
            border_color=COLORS["hairline"],
            fg_color=COLORS["bg_white"],
            text_color=COLORS["text_dark"])
        self.search_entry.pack(side="right", pady=16)
        # A textvariable suppresses CTkEntry's own placeholder, and this field
        # needs one to drive the filter trace. So draw the hint as a label over
        # the empty field; it never touches the variable.
        self._search_hint = ctk.CTkLabel(
            self.search_entry,
            text="\U0001F50D  " + t("Bill no. or customer name", L),
            font=FONTS["label_form"], text_color=COLORS["text_muted"],
            fg_color="transparent")
        self._search_hint.place(x=18, rely=0.5, anchor="w")
        self._search_hint.bind("<Button-1>",
                               lambda _e: self.search_entry.focus_set())

        # -- Filter row --------------------------------------
        fbar = ctk.CTkFrame(self, fg_color="transparent")
        self._fbar = fbar
        fbar.pack(fill="x", padx=28, pady=(0, 12))

        seg = ctk.CTkFrame(fbar, fg_color=COLORS["bg_white"],
                           corner_radius=RADII["input"], border_width=1,
                           border_color=COLORS["hairline"])
        seg.pack(side="left")
        self._range_chips = {}
        for label, days in (("Today", 0), ("7 days", 6), ("30 days", 29), ("All", None)):
            chip = ctk.CTkButton(
                seg, text=t(label, L), font=FONTS["small"],
                fg_color="transparent", hover_color=COLORS["glass_glow"],
                text_color=COLORS["text_muted"],
                height=36, width=84, corner_radius=18, border_width=0,
                command=lambda d=days, k=label: self._set_range(k, d),
            )
            chip.pack(side="left", padx=3, pady=4)
            self._range_chips[label] = chip

        # Explicit From/To still available for an arbitrary range.
        self.from_var = tk.StringVar(value=str(date.today() - timedelta(days=30)))
        self.to_var   = tk.StringVar(value=str(date.today()))
        for var in (self.from_var, self.to_var):
            ctk.CTkEntry(fbar, textvariable=var, width=124,
                         height=METRICS["control"], font=FONTS["label_form"],
                         corner_radius=RADII["input"], border_width=1,
                         border_color=COLORS["hairline"],
                         fg_color=COLORS["bg_white"],
                         text_color=COLORS["text_dark"], justify="center"
                         ).pack(side="left", padx=(10, 0))
        self._pill(fbar, t("Filter", L), kind="action", width=100,
                   command=self._apply_manual_range).pack(side="left", padx=(10, 0))

        # Packed straight into fbar: an empty wrapper frame would hold
        # CTkFrame's default 200x200 even with every chip hidden.
        self._status_chips = {}
        for kind in ("draft", "void", "due", "paid"):
            self._status_chips[kind] = self._stat_chip(fbar, kind)

        # -- Footer action bar -------------------------------
        # Packed before the table: an expanding widget packed first would
        # consume every remaining pixel and starve a later side="bottom".
        act_bar = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0,
                               height=METRICS["header"])
        act_bar.pack(fill="x", side="bottom")
        act_bar.pack_propagate(False)
        ctk.CTkFrame(act_bar, fg_color=COLORS["hairline"], height=1,
                     corner_radius=0).pack(fill="x", side="top")

        self.sel_label = ctk.CTkLabel(act_bar, text=t("No bill selected", L),
                                      font=FONTS["label_form"],
                                      text_color=COLORS["text_muted"])
        self.sel_label.pack(side="left", padx=(28, 14))

        if self.current_user["role"] == "admin":
            # Packed before the left-hand group: a side="right" widget only
            # gets what earlier widgets leave, so Void was being squeezed off
            # the edge entirely.
            self._pill(act_bar, t("Void Bill", L), kind="danger",
                       width=112, height=46, command=self._void_bill
                       ).pack(side="right", padx=(0, 28), pady=15)

        self._first_action = self._pill(act_bar, t("View Bill", L),
                                        kind="primary", width=112,
                                        height=46, command=self._view_bill)
        self._first_action.pack(side="left", padx=(0, 8), pady=15)
        self._pill(act_bar, t("Reprint", L), kind="plain", width=100,
                   height=46, command=self._reprint_bill
                   ).pack(side="left", padx=(0, 8), pady=15)
        self._pill(act_bar, t("Resume Draft", L), kind="expiry", width=130,
                   height=46, command=self._resume_draft
                   ).pack(side="left", padx=(0, 8), pady=15)

        if self.current_user["role"] == "admin":
            self._pill(act_bar, t("Return / Refund", L), kind="stock",
                       width=140, height=46, command=self._return_bill
                       ).pack(side="left", padx=(0, 8), pady=15)

        # -- Bills table -------------------------------------
        tbl_frame = self._card(self)
        self._tbl = tbl_frame
        tbl_frame.pack(fill="both", expand=True, padx=28, pady=(0, 12))

        cols = ("bill_number", "date", "customer", "items", "subtotal",
                "discount", "grand_total", "mode", "status")
        self.tree = ttk.Treeview(
            tbl_frame, columns=cols, show="headings",
            style="Bill.Treeview", selectmode="browse"
        )
        # No currency glyph in the headers: it clipped to a stub at narrow
        # widths, and repeating it three times says nothing the summary line
        # above the table does not already say.
        heads  = (t("Bill No.", L), t("Date & Time", L), t("Customer", L),
                  t("Items", L), t("Subtotal", L),
                  t("Discount", L), t("Total", L),
                  t("Mode", L), t("Status", L))
        # Customer takes the surplus; money columns keep a floor wide
        # enough for their widest real value so a figure never clips.
        self.HIST_COLSPEC = [
            ("bill_number", 0, 104), ("date", 0, 140), ("customer", 1, 150),
            ("items", 0, 58), ("subtotal", 0, 96), ("discount", 0, 90),
            ("grand_total", 0, 100), ("mode", 0, 108), ("status", 0, 80),
        ]
        for (col, _w, m), head in zip(self.HIST_COLSPEC, heads):
            anch = "e" if col in ("subtotal", "discount", "grand_total", "items") else "w"
            self.tree.heading(col, text=head, anchor=anch,
                              command=lambda c=col: self._sort_by(c))
            self.tree.column(col, width=m, anchor=anch, minwidth=m,
                             stretch=(col == "customer"))

        vsb = ttk.Scrollbar(tbl_frame, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(tbl_frame, orient="horizontal", command=self.tree.xview)
        _hgrid = dict(row=1, column=0, sticky="ew", padx=(10, 0), pady=(0, 8))
        self.tree.configure(
            yscrollcommand=vsb.set,
            xscrollcommand=autohide_scrollbar(self.tree, hsb, _hgrid))
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=(10, 0))
        vsb.grid(row=0, column=1, sticky="ns",  pady=(10, 0), padx=(0, 8))
        hsb.grid(row=1, column=0, sticky="ew",  padx=(10, 0), pady=(0, 8))
        tbl_frame.grid_rowconfigure(0, weight=1)
        tbl_frame.grid_columnconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", lambda _e: self._update_selection_label())
        tbl_frame.bind("<Configure>", lambda _e: self._fit_hist_columns(), add="+")

        # -- Store sort state --------------------------------
        self._sel_pad = (28, 14)
        self.bind_responsive()
        self._sort_col  = "date"
        self._sort_asc  = False
        self._all_bills = []
        self._range_key = "30 days"
        self._paint_range_chips()

    # -- Filter helpers --------------------------------------
    def _fit_hist_columns(self):
        tree = getattr(self, "tree", None)
        if tree is None or tree.winfo_width() <= 1:
            return
        fit_columns(tree, self.HIST_COLSPEC, tree.winfo_width(),
                    widget_scaling(self))

    def on_breakpoint(self, bp, logical_w):
        g = GUTTERS[bp]
        for w in (self._header, self._fbar, self._tbl):
            w.pack_configure(padx=g)
        self._sel_pad = (g, 14)
        self.sel_label.pack_configure(padx=self._sel_pad)
        # Five footer actions do not fit a compact window. The label goes
        # first: the selected bill is already named in the confirm dialog.
        if bp == "compact":
            self.sel_label.pack_forget()
        else:
            self.sel_label.pack(side="left", padx=self._sel_pad, before=self._first_action)
        self._fit_hist_columns()

    def _paint_range_chips(self):
        for label, chip in self._range_chips.items():
            on = label == getattr(self, "_range_key", None)
            chip.configure(
                fg_color=COLORS["accent_action"] if on else "transparent",
                text_color=COLORS["on_accent"] if on else COLORS["text_muted"],
                hover_color=COLORS["accent_action"] if on else COLORS["glass_glow"],
                font=FONTS["small_bold"] if on else FONTS["small"],
            )

    def _set_range(self, key, days):
        """Segmented control: days=None means the whole history."""
        self._range_key = key
        if days is None:
            self.from_var.set("")
        else:
            self.from_var.set(str(date.today() - timedelta(days=days)))
        self.to_var.set(str(date.today()))
        self._paint_range_chips()
        self._load_bills()

    def _apply_manual_range(self):
        """A hand-typed From/To no longer matches any chip."""
        self._range_key = None
        self._paint_range_chips()
        self._load_bills()

    def _update_selection_label(self):
        L = self.app.current_lang
        sel = self.tree.selection()
        if not sel:
            self.sel_label.configure(text=t("No bill selected", L),
                                     text_color=COLORS["text_muted"])
            return
        vals = self.tree.item(sel[0], "values")
        self.sel_label.configure(text=f"{vals[0]} {t('selected', L)}",
                                 text_color=COLORS["text_dark"])

    def _sync_search_hint(self):
        hint = getattr(self, "_search_hint", None)
        if hint is None:
            return
        if self.search_var.get():
            hint.place_forget()
        else:
            hint.place(x=18, rely=0.5, anchor="w")

    def _update_summary(self, bills, capped):
        """Header subtitle + the status count chips."""
        L = self.app.current_lang
        counts = {"paid": 0, "due": 0, "void": 0, "draft": 0}
        collected = 0.0
        for b in bills:
            status = b["status"]
            if status == "Void":
                counts["void"] += 1
            elif status == "Draft":
                counts["draft"] += 1
            elif "Credit" in (b.get("payment_mode") or ""):
                # Udhaar: billed, but not money in the drawer yet.
                counts["due"] += 1
            else:
                counts["paid"] += 1
                collected += float(b.get("grand_total") or 0)

        # "bill(s) found" is a {n} template in every language \u2014 format it
        # rather than concatenating a count in front, which rendered a
        # literal "6 {n} bill(s) found".
        n = len(bills)
        found = t("bill(s) found", L).format(n=self._LIMIT if capped else n)
        if capped:
            found = f"{t('Showing latest', L)} {found}"
        parts = [found, f"\u20b9 {collected:,.0f} " + t("collected", L)]
        ellipsis = "\u2026"
        rng_from = self.from_var.get().strip() or ellipsis
        rng_to = self.to_var.get().strip() or ellipsis
        if (rng_from, rng_to) != (ellipsis, ellipsis):
            parts.append(f"{rng_from} \u2013 {rng_to}")
        self.count_label.configure(text="  \u00b7  ".join(parts))

        labels = {"paid": t("Paid", L), "due": t("Due", L),
                  "void": t("Void", L), "draft": t("Draft", L)}
        for kind, chip in self._status_chips.items():
            c = counts[kind]
            if c:
                chip.configure(text=f"  {c} {labels[kind]}  ")
                chip.pack(side="right", padx=(8, 0))
            else:
                chip.pack_forget()

    def _sort_by(self, col):
        """Sort the loaded bills by the clicked column and re-render."""
        if not self._all_bills:
            return
        if self._sort_col == col:
            self._sort_asc = not self._sort_asc
        else:
            self._sort_col = col
            self._sort_asc = True

        numeric = {"subtotal", "discount", "grand_total"}
        key_map = {
            "bill_number": "bill_number",
            "date":        "bill_date",
            "customer":    "customer_name",
            "subtotal":    "subtotal",
            "discount":    "discount",
            "grand_total": "grand_total",
            "mode":        "payment_mode",
            "status":      "status",
        }
        key = key_map.get(col)
        if not key:
            return  # non-sortable column (e.g. items)

        if col in numeric:
            def sort_key(b): return float(b.get(key) or 0)
        else:
            def sort_key(b): return str(b.get(key) or "").lower()

        self._all_bills = sorted(self._all_bills, key=sort_key, reverse=not self._sort_asc)
        self._render_table(self._all_bills)

    def on_show(self):
        self._load_bills()

    def _filter_today(self):
        self._set_range("Today", 0)

    def _filter_all(self):
        self._set_range("All", None)

    _LIMIT = 500

    def _load_bills(self):
        L = self.app.current_lang
        search    = self.search_var.get().strip()
        date_from = self.from_var.get().strip() or None
        date_to   = self.to_var.get().strip()   or None
        # Validate any supplied date so a typo doesn't silently return 0 rows.
        for label, val in (("From", date_from), ("To", date_to)):
            if val:
                try:
                    date.fromisoformat(val)
                except ValueError:
                    messagebox.showwarning(
                        t("Invalid Date", L),
                        t("Enter dates in YYYY-MM-DD format.", L) + f"  ({label}: {val})",
                        parent=self.winfo_toplevel())
                    return
        bills = self.db.get_bills(search=search, date_from=date_from,
                                  date_to=date_to, limit=self._LIMIT)
        self._all_bills = bills
        self._render_table(bills)
        self._update_summary(bills, capped=len(bills) >= self._LIMIT)
        self._update_selection_label()
        self._sync_search_hint()

    def _render_table(self, bills):
        self.tree.delete(*self.tree.get_children())
        _row_colors = COLORS["ROW_COLORS"]
        normal_idx = 0
        for b in bills:
            if b["status"] == "Void":
                tag = "void"
            elif b["status"] == "Draft":
                tag = "draft"
            else:
                tag = f"row{normal_idx % len(_row_colors)}"
                normal_idx += 1
            self.tree.insert("", "end", iid=str(b["bill_id"]), values=(
                b["bill_number"],
                b["bill_date"][:16] if b["bill_date"] else "",
                b.get("customer_name", "Walk-in"),
                b.get("item_count", ""),
                f"{b['subtotal']:,.2f}",
                f"{b['discount']:,.2f}",
                f"{b['grand_total']:,.2f}",
                b["payment_mode"],
                b["status"],
            ), tags=(tag,))
        self.tree.tag_configure("void",  background=COLORS["row_void"], foreground=COLORS["fg_void"])
        self.tree.tag_configure("draft", background=COLORS["row_draft"], foreground=COLORS["text_dark"])
        for idx, color in enumerate(_row_colors):
            self.tree.tag_configure(f"row{idx}", background=color, foreground=COLORS["text_dark"])

    def _get_selected_bill_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select Bill", "Please select a bill first.",
                                parent=self.winfo_toplevel())
            return None
        return int(sel[0])

    def _view_bill(self):
        bill_id = self._get_selected_bill_id()
        if not bill_id:
            return
        bill, items = self.db.get_bill_by_id(bill_id)
        if not bill:
            return

        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title(f"Bill — {bill['bill_number']}")
        place_popup(dlg, 520, 600, self.winfo_toplevel())
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        scroll = ctk.CTkScrollableFrame(dlg, fg_color=COLORS["bg_card"])
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        def row(lbl, val, bold=False):
            f = ctk.CTkFrame(scroll, fg_color="transparent")
            f.pack(fill="x", padx=20, pady=3)
            fnt = FONTS["body_bold"] if bold else FONTS["body"]
            ctk.CTkLabel(f, text=lbl, font=fnt, text_color=COLORS["text_muted"],
                         width=160, anchor="w").pack(side="left")
            ctk.CTkLabel(f, text=str(val), font=fnt, text_color=COLORS["text_dark"],
                         anchor="w").pack(side="left")

        ctk.CTkLabel(scroll, text=f"Bill: {bill['bill_number']}",
                     font=FONTS["subheading"], text_color=COLORS["btn_primary"]
                    ).pack(pady=(16, 4), padx=20, anchor="w")

        row("Date:",     bill["bill_date"][:16])
        row("Customer:", bill.get("customer_name", "Walk-in"))
        row("Status:",   bill["status"])
        row("Mode:",     bill["payment_mode"])
        if bill.get("void_reason"):
            row("Void Reason:", bill["void_reason"])

        ctk.CTkFrame(scroll, fg_color=COLORS["tbl_select"], height=2).pack(fill="x", padx=20, pady=8)
        ctk.CTkLabel(scroll, text="Items", font=FONTS["body_bold"],
                     text_color=COLORS["btn_primary"]).pack(anchor="w", padx=20)

        for it in items:
            f = ctk.CTkFrame(scroll, fg_color=COLORS["bg_popup_item"], corner_radius=6)
            f.pack(fill="x", padx=20, pady=2)
            ctk.CTkLabel(f, text=f"{it['product_name']}  ×  {it['quantity']} {it['unit']}",
                         font=FONTS["body"], text_color=COLORS["text_dark"],
                         anchor="w").pack(side="left", padx=10, pady=8)
            ctk.CTkLabel(f, text=f"₹ {it['line_total']:.2f}",
                         font=FONTS["body_bold"], text_color=COLORS["btn_primary"],
                         anchor="e").pack(side="right", padx=10)

        ctk.CTkFrame(scroll, fg_color=COLORS["tbl_select"], height=2).pack(fill="x", padx=20, pady=8)
        row("Subtotal:",   f"₹ {bill['subtotal']:,.2f}")
        row("Discount:",   f"₹ {bill['discount']:,.2f}")
        row("TOTAL:",      f"₹ {bill['grand_total']:,.2f}", bold=True)
        row("Paid:",       f"₹ {bill['amount_paid']:,.2f}")
        row("Change Due:", f"₹ {bill['change_due']:,.2f}")

        btn_f = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_f.pack(pady=10, fill="x", padx=20)
        ctk.CTkButton(btn_f, text="📄  PDF / A4",
                      font=FONTS["button"], fg_color=COLORS["btn_purple"],
                      hover_color=COLORS["btn_purple_h"],
                      height=44, width=150,
                      command=lambda b=bill, i=items: self._pdf_bill(b, i)
                     ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btn_f, text="✅  Close", font=FONTS["button"],
                      fg_color=COLORS["btn_secondary"],
                      height=44, width=110,
                      command=dlg.destroy).pack(side="left")

    def _pdf_bill(self, bill: dict, items: list):
        """Generate PDF for a bill and auto-open it."""
        try:
            from bill_printer import generate_pdf_bill, open_file
            settings = {
                "shop_name"   : self.db.get_setting("shop_name",    ""),
                "shop_address": self.db.get_setting("shop_address",  ""),
                "shop_city"   : self.db.get_setting("shop_city",     ""),
                "shop_phone"  : self.db.get_setting("shop_phone",    ""),
                "shop_gst"    : self.db.get_setting("shop_gst",      ""),
            }
            path = generate_pdf_bill(bill, items, settings)
            open_file(path)
        except Exception as e:
            messagebox.showerror("PDF Error", str(e),
                                 parent=self.winfo_toplevel())

    def _reprint_bill(self):
        """Reprint selected bill on the thermal printer."""
        bill_id = self._get_selected_bill_id()
        if not bill_id:
            return
        bill, items = self.db.get_bill_by_id(bill_id)
        if not bill:
            return
        if bill["status"] != "Active":
            # Never reprint a Void or Draft bill as a real customer receipt —
            # a Draft was never completed (no stock/payment recorded).
            messagebox.showwarning(
                "Cannot Reprint",
                f"Only Active bills can be reprinted.\nThis bill is '{bill['status']}'.",
                parent=self.winfo_toplevel())
            return
        try:
            from bill_printer import print_thermal
            settings = {
                "shop_name"   : self.db.get_setting("shop_name",    "Priya Store"),
                "shop_address": self.db.get_setting("shop_address",  ""),
                "shop_city"   : self.db.get_setting("shop_city",     ""),
                "shop_phone"  : self.db.get_setting("shop_phone",    ""),
                "shop_gst"    : self.db.get_setting("shop_gst",      ""),
                "cashier"     : self.current_user.get("username",    ""),
            }
            paper = self.db.get_setting("paper_width", "80mm") or "80mm"
            ok, msg = print_thermal(bill, items, settings, paper)
            if ok:
                messagebox.showinfo("Printed", f"Receipt sent to: {msg}",
                                    parent=self.winfo_toplevel())
            else:
                messagebox.showerror("Thermal Print Failed", str(msg),
                                     parent=self.winfo_toplevel())
        except Exception as e:
            messagebox.showerror("Thermal Print Error", str(e),
                                 parent=self.winfo_toplevel())

    def _void_bill(self):
        bill_id = self._get_selected_bill_id()
        if not bill_id:
            return
        bill, _ = self.db.get_bill_by_id(bill_id)
        if not bill:
            return
        if bill["status"] != "Active":
            messagebox.showwarning("Cannot Void",
                                   f"Only Active bills can be voided.\n"
                                   f"This bill is '{bill['status']}'.",
                                   parent=self.winfo_toplevel())
            return

        if self.db.bill_has_returns(bill_id):
            messagebox.showwarning(
                "Cannot Void",
                "This bill already has one or more returns recorded against it.\n"
                "Voiding it would double-restore stock and double-refund the customer.\n\n"
                "Reverse or reconcile the returns instead of voiding.",
                parent=self.winfo_toplevel())
            return

        reason = simpledialog.askstring(
            "Void Reason",
            f"Enter reason for voiding bill {bill['bill_number']}:",
            parent=self.winfo_toplevel()
        )
        if not reason:
            return
        if messagebox.askyesno(
            "Confirm Void",
            f"Void bill {bill['bill_number']}?\n"
            f"Stock will be reversed automatically.",
            parent=self.winfo_toplevel()
        ):
            if self.db.void_bill(bill_id, reason, self.current_user["user_id"]):
                messagebox.showinfo("Voided",
                                    f"Bill {bill['bill_number']} has been voided.",
                                    parent=self.winfo_toplevel())
                self._load_bills()
            else:
                messagebox.showerror("Error", "Could not void bill.",
                                     parent=self.winfo_toplevel())

    # ─────────────────────────────────────────────────────────────
    # Sales Return / Refund (admin only)
    # ─────────────────────────────────────────────────────────────
    def _return_bill(self):
        bill_id = self._get_selected_bill_id()
        if not bill_id:
            return
        bill, _ = self.db.get_bill_by_id(bill_id)
        if not bill:
            return
        L = self.app.current_lang
        if bill["status"] != "Active":
            messagebox.showwarning(
                t("Return / Refund", L),
                t("Only active bills returnable", L).format(status=bill["status"]),
                parent=self.winfo_toplevel())
            return

        rows = [r for r in self.db.get_returnable_items(bill_id) if r["returnable"] > 0]
        if not rows:
            messagebox.showinfo(
                t("Return / Refund", L),
                "All items on this bill have already been fully returned.",
                parent=self.winfo_toplevel())
            return

        has_customer = bool(bill.get("customer_id"))

        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title(f"{t('Return / Refund', L)} — {bill['bill_number']}")
        place_popup(dlg, 780, 660, self.winfo_toplevel())
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        # Header
        head = ctk.CTkFrame(dlg, fg_color=COLORS["bg_card"], corner_radius=0, height=56)
        head.pack(fill="x")
        head.pack_propagate(False)
        ctk.CTkLabel(head, text=f"↩  {t('Sales Return', L)} — {bill['bill_number']}",
                     font=FONTS["subheading"], text_color=COLORS["accent_stock_fg"]
                     ).pack(side="left", padx=18, pady=10)
        ctk.CTkLabel(head, text=f"{bill.get('customer_name','Walk-in')}  •  {bill['bill_date'][:16]}",
                     font=FONTS["small"], text_color=COLORS["text_muted"]
                     ).pack(side="right", padx=18)

        # Column header
        colhdr = ctk.CTkFrame(dlg, fg_color="transparent")
        colhdr.pack(fill="x", padx=18, pady=(10, 0))
        for txt, w, anchor in [
            (t("Product", L), 220, "w"),
            (t("Sold Qty", L), 100, "e"),
            (t("Already Returned", L), 130, "e"),
            (t("Return Qty", L), 110, "center"),
            (f"{t('Total Refund', L)} ₹", 100, "e"),
            (t("Restock", L), 90, "center"),
        ]:
            ctk.CTkLabel(colhdr, text=txt, font=FONTS["small_bold"],
                         text_color=COLORS["text_muted"], width=w, anchor=anchor
                         ).pack(side="left", padx=2)

        # Scrollable item rows
        body = ctk.CTkScrollableFrame(dlg, fg_color=COLORS["bg_main"], height=300)
        body.pack(fill="both", expand=True, padx=16, pady=4)

        ret_rows = []
        total_var = tk.StringVar(value="₹ 0.00")
        self._ret_total = 0.0

        def _recalc(*_):
            total = 0.0
            for rr in ret_rows:
                try:
                    q = float(rr["qty_var"].get() or 0)
                except ValueError:
                    q = 0.0
                q = max(0.0, min(q, rr["returnable"]))
                line = round(q * rr["unit_price"], 2)
                rr["refund_lbl"].configure(text=f"{line:,.2f}")
                total += line
            self._ret_total = round(total, 2)
            total_var.set(f"₹ {total:,.2f}")

        for r in rows:
            rowf = ctk.CTkFrame(body, fg_color=COLORS["bg_card"], corner_radius=8)
            rowf.pack(fill="x", pady=3, padx=2)
            ctk.CTkLabel(rowf, text=r["product_name"], font=FONTS["body"],
                         text_color=COLORS["text_dark"], width=220, anchor="w"
                         ).pack(side="left", padx=4, pady=6)
            ctk.CTkLabel(rowf, text=f"{r['quantity']:.2f} {r['unit']}", font=FONTS["small"],
                         text_color=COLORS["text_muted"], width=100, anchor="e"
                         ).pack(side="left", padx=2)
            ctk.CTkLabel(rowf, text=f"{r['already_returned']:.2f}", font=FONTS["small"],
                         text_color=COLORS["text_muted"], width=130, anchor="e"
                         ).pack(side="left", padx=2)
            qv = tk.StringVar(value="0")
            qv.trace_add("write", _recalc)
            ctk.CTkEntry(rowf, textvariable=qv, width=100, height=34, justify="center",
                         font=FONTS["input"]).pack(side="left", padx=2)
            refund_lbl = ctk.CTkLabel(rowf, text="0.00", font=FONTS["body_bold"],
                                      text_color=COLORS["accent_stock_fg"], width=100, anchor="e")
            refund_lbl.pack(side="left", padx=2)
            rsv = tk.BooleanVar(value=True)
            ctk.CTkCheckBox(rowf, text=f"max {r['returnable']:.2f}", variable=rsv,
                            font=("Segoe UI", 13), width=90
                            ).pack(side="left", padx=(14, 2))
            ret_rows.append({
                "bill_item_id": r["item_id"],
                "product_id":   r["product_id"],
                "product_name": r["product_name"],
                "unit":         r["unit"],
                "unit_price":   float(r["unit_price"]),
                "returnable":   float(r["returnable"]),
                "qty_var":      qv,
                "restock_var":  rsv,
                "refund_lbl":   refund_lbl,
            })

        # Footer
        footer = ctk.CTkFrame(dlg, fg_color=COLORS["bg_card"], corner_radius=0)
        footer.pack(fill="x", side="bottom")

        row1 = ctk.CTkFrame(footer, fg_color="transparent")
        row1.pack(fill="x", padx=16, pady=(10, 4))
        ctk.CTkLabel(row1, text=f"{t('Refund Method', L)}:", font=FONTS["body"],
                     text_color=COLORS["text_dark"]).pack(side="left", padx=(0, 8))
        method_map = {
            t("Cash Refund", L):   "Cash",
            t("Adjust Credit", L): "Credit Adjust",
            t("Store Credit", L):  "Store Credit",
        }
        method_labels = [t("Cash Refund", L)]
        if has_customer:
            method_labels += [t("Adjust Credit", L), t("Store Credit", L)]
        method_var = tk.StringVar(value=method_labels[0])
        ctk.CTkOptionMenu(row1, variable=method_var, values=method_labels,
                          width=200, height=36, font=FONTS["input"]).pack(side="left")
        if not has_customer:
            ctk.CTkLabel(row1, text="(Walk-in: cash only)", font=FONTS["small"],
                         text_color=COLORS["text_muted"]).pack(side="left", padx=10)
        ctk.CTkLabel(row1, textvariable=total_var, font=FONTS["subheading"],
                     text_color=COLORS["accent_stock_fg"]).pack(side="right", padx=4)
        ctk.CTkLabel(row1, text=f"{t('Total Refund', L)}:", font=FONTS["body"],
                     text_color=COLORS["text_muted"]).pack(side="right")

        row2 = ctk.CTkFrame(footer, fg_color="transparent")
        row2.pack(fill="x", padx=16, pady=(0, 8))
        ctk.CTkLabel(row2, text=f"{t('Return Reason', L)}:", font=FONTS["body"],
                     text_color=COLORS["text_dark"]).pack(side="left", padx=(0, 8))
        reason_var = tk.StringVar()
        ctk.CTkEntry(row2, textvariable=reason_var, width=440, height=34,
                     font=FONTS["input"], placeholder_text=t("Return Reason", L)
                     ).pack(side="left")

        btns = ctk.CTkFrame(footer, fg_color="transparent")
        btns.pack(fill="x", padx=16, pady=(0, 12))

        def _confirm():
            items = []
            for rr in ret_rows:
                try:
                    q = float(rr["qty_var"].get() or 0)
                except ValueError:
                    q = 0.0
                if q <= 0:
                    continue
                if q > rr["returnable"] + 1e-9:
                    messagebox.showwarning(
                        t("Return / Refund", L),
                        f"{rr['product_name']}: max {rr['returnable']:.2f}.", parent=dlg)
                    return
                items.append({
                    "bill_item_id": rr["bill_item_id"],
                    "product_id":   rr["product_id"],
                    "product_name": rr["product_name"],
                    "unit":         rr["unit"],
                    "quantity":     round(q, 3),
                    "unit_price":   rr["unit_price"],
                    "line_total":   round(q * rr["unit_price"], 2),
                    "restocked":    1 if rr["restock_var"].get() else 0,
                })
            if not items:
                messagebox.showinfo(t("Return / Refund", L),
                                    t("No items to return", L), parent=dlg)
                return
            refund_mode = method_map.get(method_var.get(), "Cash")
            return_data = {
                "bill_id":       bill["bill_id"],
                "bill_number":   bill["bill_number"],
                "customer_id":   bill.get("customer_id"),
                "customer_name": bill.get("customer_name"),
                "refund_mode":   refund_mode,
                "reason":        reason_var.get().strip(),
            }
            try:
                ret_id, ret_no = self.db.save_return(
                    return_data, items, self.current_user["user_id"])
            except Exception as e:
                messagebox.showerror(t("Return / Refund", L), str(e), parent=dlg)
                return
            self.db.log_activity(
                self.current_user["user_id"], "RETURN_SAVED",
                f"{ret_no} vs {bill['bill_number']} — ₹{self._ret_total:.2f} ({refund_mode})")
            dlg.destroy()
            messagebox.showinfo(
                t("Return / Refund", L),
                t("Returned successfully", L).format(return_number=ret_no),
                parent=self.winfo_toplevel())
            if messagebox.askyesno(t("Return Note", L),
                                   f"{t('Return Note', L)} — {ret_no}?",
                                   parent=self.winfo_toplevel()):
                self._print_return_receipt(ret_id)
            self._load_bills()

        ctk.CTkButton(btns, text=t("Process Return", L), font=FONTS["button"],
                      fg_color=COLORS["accent_stock"], hover_color=COLORS["accent_stock_fg"], height=44, width=180,
                      command=_confirm).pack(side="left")
        ctk.CTkButton(btns, text=t("Cancel", L), font=FONTS["button"],
                      fg_color=COLORS["btn_secondary"], height=44, width=120,
                      command=dlg.destroy).pack(side="left", padx=8)

        _recalc()

    def _print_return_receipt(self, return_id):
        """Print the thermal return receipt; fall back to the A4 PDF note on failure."""
        ret, items = self.db.get_return_by_id(return_id)
        if not ret:
            return
        settings = {
            "shop_name":    self.db.get_setting("shop_name",    "Priya Store"),
            "shop_address": self.db.get_setting("shop_address", ""),
            "shop_city":    self.db.get_setting("shop_city",    ""),
            "shop_phone":   self.db.get_setting("shop_phone",   ""),
            "shop_gst":     self.db.get_setting("shop_gst",     ""),
            "cashier":      self.current_user.get("username",   ""),
        }
        paper = self.db.get_setting("paper_width", "80mm") or "80mm"
        try:
            from bill_printer import print_thermal_return
            ok, msg = print_thermal_return(ret, items, settings, paper)
            if ok:
                messagebox.showinfo("Printed", f"Receipt sent to: {msg}",
                                    parent=self.winfo_toplevel())
                return
            if messagebox.askyesno(
                "Thermal Print Failed",
                f"{msg}\n\nGenerate A4 PDF return note instead?",
                parent=self.winfo_toplevel()):
                self._print_return_note(return_id)
        except Exception as e:
            messagebox.showerror("Print Error", str(e),
                                 parent=self.winfo_toplevel())

    def _print_return_note(self, return_id):
        """Generate the PDF return note and auto-open it."""
        ret, items = self.db.get_return_by_id(return_id)
        if not ret:
            return
        try:
            from bill_printer import generate_return_pdf, open_file
            settings = {
                "shop_name":    self.db.get_setting("shop_name",    "Priya Store"),
                "shop_address": self.db.get_setting("shop_address", ""),
                "shop_city":    self.db.get_setting("shop_city",    ""),
                "shop_phone":   self.db.get_setting("shop_phone",   ""),
                "shop_gst":     self.db.get_setting("shop_gst",     ""),
            }
            path = generate_return_pdf(ret, items, settings)
            open_file(path)
        except Exception as e:
            messagebox.showerror("PDF Error", str(e),
                                 parent=self.winfo_toplevel())

    def _resume_draft(self):
        """Load a Draft bill back into the billing cart for completion."""
        bill_id = self._get_selected_bill_id()
        if not bill_id:
            return
        bill, items = self.db.get_bill_by_id(bill_id)
        if not bill:
            return
        if bill["status"] != "Draft":
            messagebox.showwarning(
                "Not a Draft",
                f"Only Draft bills can be resumed.\n\n"
                f"Bill '{bill['bill_number']}' is currently '{bill['status']}'.",
                parent=self.winfo_toplevel()
            )
            return
        self.app.navigate_to("billing")
        billing = self.app.screens.get("billing")
        if billing:
            billing.load_draft(bill_id, bill, items)

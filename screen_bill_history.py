"""
screen_bill_history.py — Bill History screen
View, reprint, and void past bills with date filter.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import date, timedelta
from config import COLORS, FONTS
from ui_utils import place_popup
from lang import t


class BillHistoryScreen(ctk.CTkFrame):
    def __init__(self, parent, db, current_user, app):
        super().__init__(parent, fg_color=COLORS["bg_main"], corner_radius=0)
        self.db           = db
        self.current_user = current_user
        self.app          = app
        self._build()

    def _build(self):
        # ── Header ───────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        L = self.app.current_lang
        ctk.CTkLabel(header, text=f"📋   {t('Bill History', L)}",
                     font=FONTS["heading"], text_color=COLORS["text_dark"]
                    ).pack(side="left", padx=25, pady=15)

        # ── Filter bar ───────────────────────────────────────
        fbar = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0, height=65)
        fbar.pack(fill="x", pady=(2, 0))
        fbar.pack_propagate(False)

        ctk.CTkLabel(fbar, text=t("Search", L) + ":", font=FONTS["body"],
                     text_color=COLORS["text_dark"]).pack(side="left", padx=(20, 5), pady=12)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._load_bills())
        ctk.CTkEntry(fbar, textvariable=self.search_var,
                     placeholder_text=t("Bill no. or customer name", L),
                     font=FONTS["input"], width=220, height=40,
                     border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"]
                    ).pack(side="left", padx=(0, 15), pady=12)

        ctk.CTkLabel(fbar, text=t("From:", L), font=FONTS["body"],
                     text_color=COLORS["text_dark"]).pack(side="left", padx=(0, 4))
        self.from_var = tk.StringVar(value=str(date.today() - timedelta(days=30)))
        ctk.CTkEntry(fbar, textvariable=self.from_var,
                     width=115, height=40, font=FONTS["input"],
                     border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"]
                    ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(fbar, text=t("To:", L), font=FONTS["body"],
                     text_color=COLORS["text_dark"]).pack(side="left", padx=(0, 4))
        self.to_var = tk.StringVar(value=str(date.today()))
        ctk.CTkEntry(fbar, textvariable=self.to_var,
                     width=115, height=40, font=FONTS["input"],
                     border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"]
                    ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(fbar, text=f"🔍 {t('Filter', L)}",
                      font=FONTS["button"], fg_color=COLORS["btn_primary"],
                      height=40, width=100, corner_radius=10,
                      command=self._load_bills
                     ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(fbar, text=t("Today", L),
                      font=FONTS["small_bold"], fg_color=COLORS["btn_secondary"],
                      height=40, width=70, corner_radius=10,
                      command=self._filter_today
                     ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(fbar, text=t("All", L),
                      font=FONTS["small_bold"], fg_color=COLORS["btn_secondary"],
                      height=40, width=60, corner_radius=10,
                      command=self._filter_all
                     ).pack(side="left", padx=(0, 6))

        # Status count label
        self.count_label = ctk.CTkLabel(fbar, text="",
                                         font=FONTS["small"], text_color=COLORS["text_muted"])
        self.count_label.pack(side="right", padx=20)

        # ── Bills table ──────────────────────────────────────
        tbl_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=16)
        tbl_frame.pack(fill="both", expand=True, padx=12, pady=10)

        # ttk styles applied globally via styles.py

        cols = ("bill_number", "date", "customer", "items", "subtotal",
                "discount", "grand_total", "mode", "status")
        self.tree = ttk.Treeview(
            tbl_frame, columns=cols, show="headings",
            style="Hist.Treeview", selectmode="browse"
        )
        heads  = (t("Bill No.", L), t("Date & Time", L), t("Customer", L),
                  t("Items", L), f"{t('Subtotal', L)} ₹",
                  f"{t('Discount', L)} ₹", f"{t('Total', L)} ₹",
                  t("Mode", L), t("Status", L))
        widths = (110, 155, 180, 55, 100, 80, 100, 120, 80)
        for col, head, w in zip(cols, heads, widths):
            self.tree.heading(col, text=head,
                              command=lambda c=col: self._sort_by(c))
            anch = "e" if col in ("subtotal","discount","grand_total","items") else "w"
            self.tree.column(col, width=w, anchor=anch, minwidth=50)

        vsb = ttk.Scrollbar(tbl_frame, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(tbl_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(6,0), pady=(6,0))
        vsb.grid(row=0, column=1, sticky="ns",  pady=(6,0))
        hsb.grid(row=1, column=0, sticky="ew",  padx=(6,0))
        tbl_frame.grid_rowconfigure(0, weight=1)
        tbl_frame.grid_columnconfigure(0, weight=1)

        # ── Action buttons bar ───────────────────────────────
        act_bar = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0, height=60)
        act_bar.pack(fill="x")
        act_bar.pack_propagate(False)

        ctk.CTkButton(act_bar, text=t("View Bill", L),
                      font=FONTS["button"], fg_color=COLORS["btn_primary"],
                      height=44, width=140, corner_radius=10,
                      command=self._view_bill
                     ).pack(side="left", padx=(20,8), pady=8)
        ctk.CTkButton(act_bar, text=t("Reprint", L),
                      font=FONTS["button"], fg_color="#0277BD",
                      height=44, width=120, corner_radius=10,
                      command=self._reprint_bill
                     ).pack(side="left", padx=(0,8), pady=8)
        ctk.CTkButton(act_bar, text=t("Resume Draft", L),
                      font=FONTS["button"], fg_color=COLORS["btn_warning"],
                      hover_color="#CC7700",
                      height=44, width=160, corner_radius=10,
                      command=self._resume_draft
                     ).pack(side="left", padx=(0,8), pady=8)

        if self.current_user["role"] == "admin":
            ctk.CTkButton(act_bar, text=f"↩ {t('Return / Refund', L)}",
                          font=FONTS["button"], fg_color="#C2410C",
                          hover_color="#9A3412",
                          height=44, width=170, corner_radius=10,
                          command=self._return_bill
                         ).pack(side="left", padx=(0,8), pady=8)
            ctk.CTkButton(act_bar, text=t("Void Bill", L),
                          font=FONTS["button"], fg_color=COLORS["btn_danger"],
                          height=44, width=120, corner_radius=10,
                          command=self._void_bill
                         ).pack(side="left", padx=(0,8), pady=8)

        # ── Store sort state ─────────────────────────────────
        self._sort_col  = "date"
        self._sort_asc  = False
        self._all_bills = []

    def on_show(self):
        self._load_bills()

    def _filter_today(self):
        today = str(date.today())
        self.from_var.set(today)
        self.to_var.set(today)
        self._load_bills()

    def _filter_all(self):
        self.from_var.set("2020-01-01")
        self.to_var.set(str(date.today()))
        self._load_bills()

    def _load_bills(self):
        search    = self.search_var.get().strip()
        date_from = self.from_var.get().strip() or None
        date_to   = self.to_var.get().strip()   or None
        bills = self.db.get_bills(search=search, date_from=date_from, date_to=date_to, limit=500)
        self._all_bills = bills
        self._render_table(bills)
        self.count_label.configure(text=f"{len(bills)} bill(s) found")

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
                "",                                 # items count filled below
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
        place_popup(dlg, 520, 600)
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
                      hover_color="#9B45C7",
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
        if bill["status"] == "Void":
            messagebox.showwarning("Voided Bill",
                                   "This bill has been voided and cannot be reprinted.",
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
                     font=FONTS["subheading"], text_color="#9A3412"
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
                                      text_color="#9A3412", width=100, anchor="e")
            refund_lbl.pack(side="left", padx=2)
            rsv = tk.BooleanVar(value=True)
            ctk.CTkCheckBox(rowf, text=f"max {r['returnable']:.2f}", variable=rsv,
                            font=("Segoe UI", 11), width=90
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
                     text_color="#9A3412").pack(side="right", padx=4)
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
                      fg_color="#C2410C", hover_color="#9A3412", height=44, width=180,
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

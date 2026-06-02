"""
screen_customers.py — Customer Master + Udhaar Ledger (Phase 3)
Add/edit customers, view & manage credit balances, full transaction history.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from config import COLORS, FONTS


class CustomerScreen(ctk.CTkFrame):
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
        hdr = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0, height=70)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)
        ctk.CTkLabel(hdr, text="👥   Customers & Udhaar",
                     font=FONTS["heading"], text_color=COLORS["text_dark"]
                    ).pack(side="left", padx=25, pady=15)
        ctk.CTkButton(hdr, text="➕  Add New Customer",
                      font=FONTS["button"], fg_color=COLORS["btn_success"],
                      height=44, corner_radius=10,
                      command=lambda: self._open_form(None)
                     ).pack(side="right", padx=20, pady=13)

        # ── KPI Cards ────────────────────────────────────────
        kpi_row = ctk.CTkFrame(self, fg_color="transparent")
        kpi_row.grid(row=1, column=0, sticky="ew", padx=14, pady=(10, 4))
        for i in range(3):
            kpi_row.grid_columnconfigure(i, weight=1)

        self._kpi_total    = self._make_kpi(kpi_row, "👥  Total Customers", "—", COLORS["btn_primary"], 0)
        self._kpi_udhaar   = self._make_kpi(kpi_row, "💳  Total Udhaar",    "₹0", COLORS["btn_danger"], 1)
        self._kpi_credit_n = self._make_kpi(kpi_row, "📋  Credit Accounts", "—", COLORS["btn_warning"], 2)

        # ── Body ─────────────────────────────────────────────
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 8))
        body.grid_rowconfigure(1, weight=1)
        body.grid_columnconfigure(0, weight=1)

        # Search bar
        sbar = ctk.CTkFrame(body, fg_color=COLORS["bg_card"], corner_radius=16, height=58)
        sbar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        sbar.grid_propagate(False)
        sbar.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(sbar, text="🔍", font=FONTS["body"],
                     text_color=COLORS["btn_primary"]).grid(row=0, column=0, padx=(16, 4))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._load_customers())
        ctk.CTkEntry(sbar, textvariable=self.search_var,
                     placeholder_text="Search by name or phone…",
                     font=FONTS["input"], height=40,
                     border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"]
                    ).grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=9)
        self.count_lbl = ctk.CTkLabel(sbar, text="", font=FONTS["small"],
                                       text_color=COLORS["text_muted"])
        self.count_lbl.grid(row=0, column=2, padx=(0, 16))

        # Table
        tbl = ctk.CTkFrame(body, fg_color=COLORS["bg_card"], corner_radius=16)
        tbl.grid(row=1, column=0, sticky="nsew")
        tbl.grid_rowconfigure(0, weight=1)
        tbl.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Cust.Treeview",
            font=FONTS["table"], rowheight=48,
            background="white", foreground=COLORS["text_dark"],
            fieldbackground="white", borderwidth=0)
        style.configure("Cust.Treeview.Heading",
            font=FONTS["table_hdr"],
            background=COLORS["tbl_header_bg"], foreground="white", relief="flat")
        style.map("Cust.Treeview",
            background=[("selected", "#BBDEFB")],
            foreground=[("selected", COLORS["text_dark"])])

        cols   = ("name", "phone", "address", "balance", "status")
        heads  = ("Customer Name", "Phone", "Address", "Udhaar Balance", "Status")
        widths = (240, 160, 260, 160, 100)
        self.tree = ttk.Treeview(tbl, columns=cols, show="headings",
                                  style="Cust.Treeview", selectmode="browse")
        for col, head, w in zip(cols, heads, widths):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=w, minwidth=50, stretch=False)  # CUST-2 fix
        vsb = ttk.Scrollbar(tbl, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(tbl, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=(6, 0))
        vsb.grid(row=0, column=1, sticky="ns",  pady=(6, 0))
        hsb.grid(row=1, column=0, sticky="ew",  padx=(6, 0), pady=(0, 4))
        self.tree.bind("<Double-1>", lambda e: self._open_edit_form())
        self.tree.tag_configure("alt",    background=COLORS["tbl_row_alt"])
        self.tree.tag_configure("credit", background="#FFF3E0")  # orange tint if has balance

        # ── Action bar ───────────────────────────────────────
        act = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0, height=62)
        act.grid(row=3, column=0, sticky="ew")
        act.grid_propagate(False)
        for txt, color, cmd in [
            ("✏️  Edit",          COLORS["btn_primary"],   self._open_edit_form),
            ("📖  View Ledger",   COLORS["btn_purple"],    self._open_ledger),
            ("🖨️  Print Ledger",  "#0277BD",               self._print_ledger),
            ("💳  Add Payment",   COLORS["btn_success"],   self._add_payment),
            ("📝  Add Udhaar",    COLORS["btn_warning"],   self._add_udhaar),
            ("🗑️  Delete",        COLORS["btn_danger"],    self._delete_customer),
        ]:
            ctk.CTkButton(act, text=txt, font=FONTS["button"],
                          fg_color=color, height=44, corner_radius=10,
                          command=cmd).pack(side="left", padx=(8, 0), pady=9)

    # ── KPI helper ───────────────────────────────────────────
    def _make_kpi(self, parent, label, value, color, col):
        card = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=14)
        card.grid(row=0, column=col, sticky="ew", padx=6, pady=4)
        ctk.CTkLabel(card, text=label, font=FONTS["small_bold"],
                     text_color=COLORS["text_muted"]).pack(pady=(14, 2), padx=20, anchor="w")
        lbl = ctk.CTkLabel(card, text=value, font=FONTS["num_md"], text_color=color)
        lbl.pack(pady=(0, 14), padx=20, anchor="w")
        return lbl

    def on_show(self):
        self._load_kpis()
        self._load_customers()

    def _load_kpis(self):
        s = self.db.get_customers_summary()
        self._kpi_total.configure(text=str(s["total"]))
        self._kpi_udhaar.configure(text=f"₹{s['total_udhaar']:,.2f}")
        self._kpi_credit_n.configure(text=str(s["credit_accounts"]))

    def _load_customers(self):
        search = self.search_var.get().strip()
        rows   = self.db.get_customers(search=search)
        self.tree.delete(*self.tree.get_children())
        _row_colors = COLORS["ROW_COLORS"]
        for i, c in enumerate(rows):
            bal = c.get("credit_balance") or 0
            tag = "credit" if bal > 0 else f"row{i % len(_row_colors)}"
            self.tree.insert("", "end", iid=str(c["customer_id"]), values=(
                c["name"],
                c.get("phone", "") or "",
                c.get("address", "") or "",
                f"₹{bal:,.2f}" if bal > 0 else "—",
                "✅ Active" if (c.get("is_active") in (None, 1)) else "❌ Inactive",
            ), tags=(tag,))
        for idx, color in enumerate(_row_colors):
            self.tree.tag_configure(f"row{idx}", background=color)
        self.count_lbl.configure(text=f"{len(rows)} customer(s)")

    def _get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select Customer",
                                "Please select a customer first.",
                                parent=self.winfo_toplevel())
            return None
        return int(sel[0])

    # ── Add / Edit form ──────────────────────────────────────
    def _open_edit_form(self):
        cid = self._get_selected_id()
        if not cid:
            return
        cust = self.db.get_customer_by_id(cid)
        if cust:
            self._open_form(cust)

    def _open_form(self, customer):
        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title("Edit Customer" if customer else "Add New Customer")
        dlg.geometry("480x400")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        ctk.CTkLabel(dlg, text=f"{'✏️  Edit' if customer else '➕  Add'} Customer",
                     font=FONTS["heading"], text_color=COLORS["btn_primary"]
                    ).pack(pady=(20, 6), padx=24, anchor="w")
        ctk.CTkFrame(dlg, fg_color=COLORS["tbl_select"], height=2).pack(fill="x", padx=24, pady=(0, 14))

        p = customer or {}
        entries = {}

        def field(label, key, default="", placeholder="", required=False):
            f = ctk.CTkFrame(dlg, fg_color="transparent")
            f.pack(fill="x", padx=24, pady=6)
            ctk.CTkLabel(f, text=label + (" *" if required else ""),
                         font=FONTS["label_form"], text_color=COLORS["text_dark"],
                         width=140, anchor="w").pack(side="left")
            var = tk.StringVar(value=str(default) if default else "")
            ctk.CTkEntry(f, textvariable=var, placeholder_text=placeholder,
                         font=FONTS["input"], height=44,
                         border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"],
                         width=280).pack(side="left")
            entries[key] = var

        field("Full Name",   "name",    p.get("name",""),    "e.g. Raju Sharma",   required=True)
        field("Phone",       "phone",   p.get("phone",""),   "e.g. 98765 43210")
        field("Address",     "address", p.get("address",""), "e.g. Lane 4, Market")

        err_lbl = ctk.CTkLabel(dlg, text="", font=FONTS["small"], text_color=COLORS["btn_danger"])
        err_lbl.pack(pady=(4, 0), padx=24, anchor="w")

        def save():
            name = entries["name"].get().strip()
            if not name:
                err_lbl.configure(text="⚠  Customer name is required.")
                return
            data = {
                "name":    name,
                "phone":   entries["phone"].get().strip() or None,
                "address": entries["address"].get().strip() or None,
            }
            if customer:
                self.db.update_customer(customer["customer_id"], data)
                messagebox.showinfo("Saved", f"'{name}' updated.", parent=dlg)
            else:
                self.db.add_customer(data)
                messagebox.showinfo("Added", f"'{name}' added.", parent=dlg)
            dlg.destroy()
            self._load_customers()
            self._load_kpis()

        btn_row = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=16)
        ctk.CTkButton(btn_row, text="💾  Save", font=FONTS["button"],
                      fg_color=COLORS["btn_success"], height=50, corner_radius=16,
                      command=save).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(btn_row, text="Cancel", font=FONTS["button"],
                      fg_color=COLORS["btn_secondary"], height=50, corner_radius=16,
                      command=dlg.destroy).pack(side="left", width=110)

    # ── Ledger popup ─────────────────────────────────────────
    def _open_ledger(self):
        cid = self._get_selected_id()
        if not cid:
            return
        cust = self.db.get_customer_by_id(cid)
        if not cust:
            return
        txns = self.db.get_customer_transactions(cid, limit=200)

        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title(f"Ledger — {cust['name']}")
        dlg.geometry("700x540")
        dlg.resizable(True, True)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        # Header
        hdr = ctk.CTkFrame(dlg, fg_color=COLORS["btn_primary"], corner_radius=0, height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        bal = cust.get("credit_balance") or 0
        ctk.CTkLabel(hdr, text=f"📖  {cust['name']}  |  Phone: {cust.get('phone','—')}",
                     font=FONTS["body_bold"], text_color="white"
                    ).pack(side="left", padx=20, pady=10)
        bal_color = "#FFCDD2" if bal > 0 else "#C8E6C9"
        ctk.CTkLabel(hdr, text=f"Balance: ₹{bal:,.2f}",
                     font=FONTS["body_bold"], text_color=bal_color
                    ).pack(side="right", padx=20)

        # Table
        tbl = ctk.CTkFrame(dlg, fg_color=COLORS["bg_card"], corner_radius=0)
        tbl.pack(fill="both", expand=True, padx=10, pady=10)
        tbl.grid_rowconfigure(0, weight=1)
        tbl.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure("Led.Treeview",
            font=FONTS["table"], rowheight=38,
            background="white", foreground=COLORS["text_dark"],
            fieldbackground="white", borderwidth=0)
        style.configure("Led.Treeview.Heading",
            font=FONTS["table_hdr"],
            background=COLORS["btn_primary"], foreground="white", relief="flat")
        style.map("Led.Treeview",
            background=[("selected", "#BBDEFB")],
            foreground=[("selected", COLORS["text_dark"])])

        cols   = ("date", "type", "amount", "reference", "notes")
        heads  = ("Date & Time", "Type", "Amount (₹)", "Reference", "Notes")
        widths = (180, 110, 130, 160, 160)
        tree = ttk.Treeview(tbl, columns=cols, show="headings",
                             style="Led.Treeview", selectmode="browse")
        for col, head, w in zip(cols, heads, widths):
            tree.heading(col, text=head)
            tree.column(col, width=w, minwidth=60)
        vsb = ttk.Scrollbar(tbl, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.grid(row=0, column=0, sticky="nsew", padx=(4, 0), pady=4)
        vsb.grid(row=0, column=1, sticky="ns", pady=4)
        tree.tag_configure("credit",  background="#FFEBEE")
        tree.tag_configure("payment", background="#E8F5E9")

        for i, t in enumerate(txns):
            tag = "credit" if t["txn_type"] == "Credit" else "payment"
            tree.insert("", "end", values=(
                str(t["created_at"])[:16],
                "🔴 Udhaar" if t["txn_type"] == "Credit" else "🟢 Payment",
                f"₹{t['amount']:,.2f}",
                t.get("reference", "") or "",
                t.get("notes", "") or "",
            ), tags=(tag,))

        if not txns:
            tree.insert("", "end", values=("No transactions yet", "", "", "", ""))

        ctk.CTkButton(dlg, text="Close", font=FONTS["button"],
                      fg_color=COLORS["btn_secondary"], height=44, corner_radius=10,
                      command=dlg.destroy).pack(pady=8)

    # ── Add Payment (reduce balance) ─────────────────────────
    def _add_payment(self):
        self._transaction_dialog("Payment")

    # ── Add Udhaar (increase balance) ───────────────────────
    def _add_udhaar(self):
        self._transaction_dialog("Credit")

    def _transaction_dialog(self, txn_type: str):
        cid = self._get_selected_id()
        if not cid:
            return
        cust = self.db.get_customer_by_id(cid)
        if not cust:
            return

        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        title = "💳  Record Payment" if txn_type == "Payment" else "📝  Add Udhaar (Credit)"
        dlg.title(title)
        dlg.geometry("440x380")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        ctk.CTkLabel(dlg, text=title, font=FONTS["heading"],
                     text_color=COLORS["btn_primary"] if txn_type == "Payment" else COLORS["btn_warning"]
                    ).pack(pady=(20, 4), padx=24, anchor="w")
        ctk.CTkLabel(dlg, text=f"Customer: {cust['name']}  |  Current Balance: ₹{(cust.get('credit_balance') or 0):,.2f}",
                     font=FONTS["small"], text_color=COLORS["text_muted"]
                    ).pack(padx=24, anchor="w")
        ctk.CTkFrame(dlg, fg_color=COLORS["tbl_select"], height=2).pack(fill="x", padx=24, pady=(8, 14))

        def row(label, widget_fn):
            f = ctk.CTkFrame(dlg, fg_color="transparent")
            f.pack(fill="x", padx=24, pady=6)
            ctk.CTkLabel(f, text=label, font=FONTS["label_form"],
                         text_color=COLORS["text_dark"], width=130, anchor="w").pack(side="left")
            return widget_fn(f)

        amt_var = tk.StringVar()
        row("Amount (₹) *", lambda f: ctk.CTkEntry(
            f, textvariable=amt_var, placeholder_text="e.g. 500",
            font=FONTS["input"], height=44,
            border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"], width=260
        ).pack(side="left"))

        ref_var = tk.StringVar()
        row("Reference", lambda f: ctk.CTkEntry(
            f, textvariable=ref_var, placeholder_text="Bill no / note",
            font=FONTS["input"], height=44,
            border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"], width=260
        ).pack(side="left"))

        note_var = tk.StringVar()
        row("Notes", lambda f: ctk.CTkEntry(
            f, textvariable=note_var, placeholder_text="Optional note",
            font=FONTS["input"], height=44,
            border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"], width=260
        ).pack(side="left"))

        err_lbl = ctk.CTkLabel(dlg, text="", font=FONTS["small"], text_color=COLORS["btn_danger"])
        err_lbl.pack(pady=(4, 0), padx=24, anchor="w")

        def save():
            try:
                amount = float(amt_var.get().strip())
                if amount <= 0:
                    raise ValueError
            except ValueError:
                err_lbl.configure(text="⚠  Enter a valid amount.")
                return
            self.db.add_customer_transaction(
                cid, txn_type, amount,
                ref_var.get().strip() or None,
                note_var.get().strip() or None,
                self.current_user["user_id"]
            )
            verb = "Payment of" if txn_type == "Payment" else "Udhaar of"
            messagebox.showinfo("Saved", f"{verb} ₹{amount:,.2f} recorded.", parent=dlg)
            dlg.destroy()
            self._load_customers()
            self._load_kpis()

        btn_row = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=14)
        btn_color = COLORS["btn_success"] if txn_type == "Payment" else COLORS["btn_warning"]
        ctk.CTkButton(btn_row, text="💾  Save", font=FONTS["button"],
                      fg_color=btn_color, height=50, corner_radius=16,
                      command=save).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(btn_row, text="Cancel", font=FONTS["button"],
                      fg_color=COLORS["btn_secondary"], height=50, corner_radius=16,
                      command=dlg.destroy).pack(side="left", width=110)

    def _delete_customer(self):
        """Permanently delete customer (CUST-1). Deactivates if has bills."""
        cid = self._get_selected_id()
        if not cid:
            return
        cust = self.db.get_customer_by_id(cid)
        if not cust:
            return
        if not messagebox.askyesno(
            "Delete Customer",
            f"Permanently DELETE '{cust['name']}'?\n\n"
            "⚠️  Cannot be undone.\n"
            "If this customer has billing history they will be deactivated instead.",
            parent=self.winfo_toplevel()
        ):
            return
        ok, msg = self.db.delete_customer(cid)
        if ok:
            messagebox.showinfo("Deleted", msg, parent=self.winfo_toplevel())
        else:
            messagebox.showwarning("Cannot Delete", msg, parent=self.winfo_toplevel())
            self.db.deactivate_customer(cid)
        self._load_customers()
        self._load_kpis()

    def _print_ledger(self):
        """Print customer ledger as PDF (CUST-3)."""
        cid = self._get_selected_id()
        if not cid:
            return
        cust = self.db.get_customer_by_id(cid)
        if not cust:
            return
        txns = self.db.get_customer_transactions(cid, limit=500)
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import mm
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import ParagraphStyle
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            import tkinter.filedialog as fd, os

            path = fd.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF file", "*.pdf")],
                initialfile=f"Ledger_{cust['name'].replace(' ','_')}.pdf",
                title="Save Customer Ledger",
                parent=self.winfo_toplevel(),
            )
            if not path:
                return

            BLUE = colors.HexColor("#1565C0")
            doc  = SimpleDocTemplate(path, pagesize=A4,
                                     leftMargin=15*mm, rightMargin=15*mm,
                                     topMargin=10*mm, bottomMargin=10*mm)
            h_s = ParagraphStyle("h", fontSize=14, fontName="Helvetica-Bold",
                                  textColor=BLUE, alignment=TA_CENTER)
            s_s = ParagraphStyle("s", fontSize=10, fontName="Helvetica",
                                  textColor=colors.grey, alignment=TA_CENTER)
            c_s = ParagraphStyle("c", fontSize=9,  fontName="Helvetica")
            t_s = ParagraphStyle("t", fontSize=9,  fontName="Helvetica-Bold",
                                  textColor=colors.white)

            shop = self.db.get_setting("shop_name", "FMCG Shop")
            bal  = float(cust.get("credit_balance") or 0)
            story = [
                Paragraph(shop, h_s),
                Paragraph("Customer Ledger Statement", s_s),
                Spacer(1, 4*mm),
                Paragraph(f"Customer: {cust['name']}   |   Phone: {cust.get('phone','—')}   |   Outstanding: ₹{bal:,.2f}", s_s),
                Spacer(1, 4*mm),
            ]
            hdr_row = [Paragraph(x, t_s) for x in ["Date & Time","Type","Amount ₹","Reference","Notes"]]
            rows = [hdr_row]
            for t in txns:
                rows.append([
                    Paragraph(str(t.get("created_at",""))[:16], c_s),
                    Paragraph(str(t.get("txn_type","")),         c_s),
                    Paragraph(f"₹{float(t.get('amount',0)):,.2f}", c_s),
                    Paragraph(str(t.get("reference","") or ""), c_s),
                    Paragraph(str(t.get("notes","") or ""),     c_s),
                ])
            tbl = Table(rows, colWidths=[38*mm,28*mm,28*mm,40*mm,48*mm], repeatRows=1)
            tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0,0),(-1,0),  BLUE),
                ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, colors.HexColor("#F5F7FF")]),
                ("GRID",          (0,0),(-1,-1), 0.3, colors.HexColor("#CCCCCC")),
                ("TOPPADDING",    (0,0),(-1,-1), 4),
                ("BOTTOMPADDING", (0,0),(-1,-1), 4),
                ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
            ]))
            story += [tbl, Spacer(1,6*mm),
                      Paragraph(f"<b>Total Outstanding: ₹{bal:,.2f}</b>",
                                ParagraphStyle("sum",fontSize=11,fontName="Helvetica-Bold",
                                               textColor=BLUE,alignment=TA_LEFT))]
            doc.build(story)
            messagebox.showinfo("Saved", f"Ledger saved:\n{path}", parent=self.winfo_toplevel())
            try:
                os.startfile(path)
            except Exception:
                import webbrowser; webbrowser.open(path)
        except ImportError:
            messagebox.showerror("Missing Library","reportlab is required.\nRun: pip install reportlab",
                                 parent=self.winfo_toplevel())
        except Exception as e:
            messagebox.showerror("PDF Error", str(e), parent=self.winfo_toplevel())

    def _deactivate(self):
        cid = self._get_selected_id()
        if not cid:
            return
        cust = self.db.get_customer_by_id(cid)
        if not cust:
            return
        if messagebox.askyesno("Deactivate",
                               f"Deactivate '{cust['name']}'?",
                               parent=self.winfo_toplevel()):
            self.db.deactivate_customer(cid)
            self._load_customers()
            self._load_kpis()

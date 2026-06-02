"""
screen_suppliers.py — Supplier Master (Phase 2)
Add, edit, view all suppliers.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from config import COLORS, FONTS


class SupplierScreen(ctk.CTkFrame):
    def __init__(self, parent, db, current_user, app):
        super().__init__(parent, fg_color=COLORS["bg_main"], corner_radius=0)
        self.db           = db
        self.current_user = current_user
        self.app          = app
        self._editing_id  = None
        self._build()

    def _build(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Header ───────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0, height=70)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        ctk.CTkLabel(header, text="🏭   Supplier Master",
                     font=FONTS["heading"], text_color=COLORS["text_dark"]
                    ).pack(side="left", padx=25, pady=15)
        ctk.CTkButton(header, text="➕  Add New Supplier",
                      font=FONTS["button"], fg_color=COLORS["btn_success"],
                      height=44, corner_radius=10,
                      command=lambda: self._open_form(None)
                     ).pack(side="right", padx=20, pady=13)

        # ── Body ─────────────────────────────────────────────
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=12, pady=8)
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
        self.search_var.trace_add("write", lambda *_: self._load_suppliers())
        ctk.CTkEntry(sbar, textvariable=self.search_var,
                     placeholder_text="Search by name, contact person or phone…",
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

        # ttk styles applied globally via styles.py

        cols   = ("name", "contact", "phone", "city", "gst", "status")
        heads  = ("Supplier Name", "Contact Person", "Phone", "City", "GST Number", "Status")
        widths = (240, 180, 140, 130, 160, 90)
        self.tree = ttk.Treeview(tbl, columns=cols, show="headings",
                                  style="Sup.Treeview", selectmode="browse")
        for col, head, w in zip(cols, heads, widths):
            self.tree.heading(col, text=head)
            self.tree.column(col, width=w, minwidth=50)
        vsb = ttk.Scrollbar(tbl, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(6, 0), pady=6)
        vsb.grid(row=0, column=1, sticky="ns", pady=6)
        self.tree.bind("<Double-1>", lambda e: self._open_edit_form())
        self.tree.tag_configure("alt", background=COLORS["tbl_row_alt"])

        # Action bar
        act = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0, height=58)
        act.grid(row=2, column=0, sticky="ew")
        act.grid_propagate(False)
        ctk.CTkButton(act, text="✏️  Edit",
                      font=FONTS["button"], fg_color=COLORS["btn_primary"],
                      height=42, width=110, corner_radius=10,
                      command=self._open_edit_form
                     ).pack(side="left", padx=(20, 6), pady=8)
        ctk.CTkButton(act, text="💰  Record Payment",
                      font=FONTS["button"], fg_color=COLORS["btn_warning"],
                      height=42, width=170, corner_radius=10,
                      command=self._record_payment
                     ).pack(side="left", padx=(0, 6), pady=8)
        ctk.CTkButton(act, text="🚫  Deactivate",
                      font=FONTS["button"], fg_color="#FF8C00",
                      height=42, width=140, corner_radius=10,
                      command=self._deactivate
                     ).pack(side="left", padx=(0, 6), pady=8)
        ctk.CTkButton(act, text="🗑️  Delete",
                      font=FONTS["button"], fg_color=COLORS["btn_danger"],
                      height=42, width=110, corner_radius=10,
                      command=self._delete_supplier
                     ).pack(side="left", padx=(0, 6), pady=8)

    def on_show(self):
        self._load_suppliers()

    def _load_suppliers(self):
        search = self.search_var.get().strip()
        rows   = self.db.get_suppliers(active_only=False, search=search)
        self.tree.delete(*self.tree.get_children())
        for i, s in enumerate(rows):
            tag = "alt" if i % 2 == 0 else ""
            self.tree.insert("", "end", iid=str(s["supplier_id"]), values=(
                s["name"],
                s.get("contact_person", "") or "",
                s.get("phone", "") or "",
                s.get("city", "") or "",
                s.get("gst_number", "") or "",
                "✅ Active" if s["is_active"] else "❌ Inactive",
            ), tags=(tag,))
        self.count_lbl.configure(text=f"{len(rows)} supplier(s)")

    def _get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select Supplier",
                                "Please select a supplier first.",
                                parent=self.winfo_toplevel())
            return None
        return int(sel[0])

    def _open_edit_form(self):
        sid = self._get_selected_id()
        if not sid:
            return
        sup = self.db.get_supplier_by_id(sid)
        if sup:
            self._editing_id = sid
            self._open_form(sup)

    def _open_form(self, supplier):
        self._editing_id = supplier["supplier_id"] if supplier else None
        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        title = "Edit Supplier" if supplier else "Add New Supplier"
        dlg.title(title)
        dlg.geometry("520x580")
        dlg.resizable(False, True)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        scroll = ctk.CTkScrollableFrame(dlg, fg_color=COLORS["bg_main"])
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll,
                     text=f"{'✏️  Edit' if supplier else '➕  Add'} Supplier",
                     font=FONTS["heading"], text_color=COLORS["btn_primary"]
                    ).pack(pady=(18, 10), padx=24, anchor="w")
        ctk.CTkFrame(scroll, fg_color=COLORS["tbl_select"], height=2).pack(fill="x", padx=24, pady=(0, 16))

        p = supplier or {}
        entries = {}

        def field(label, key, default="", placeholder="", required=False):
            f = ctk.CTkFrame(scroll, fg_color="transparent")
            f.pack(fill="x", padx=24, pady=6)
            lbl_text = label + (" *" if required else "")
            ctk.CTkLabel(f, text=lbl_text, font=FONTS["label_form"],
                         text_color=COLORS["text_dark"], width=180, anchor="w"
                        ).pack(side="left")
            var = tk.StringVar(value=str(default) if default else "")
            ctk.CTkEntry(f, textvariable=var, placeholder_text=placeholder,
                         font=FONTS["input"], height=44,
                         border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"],
                         width=260
                        ).pack(side="left")
            entries[key] = var

        field("Supplier Name",    "name",           p.get("name", ""),
              "e.g. Reliance Mart", required=True)
        field("Contact Person",   "contact_person", p.get("contact_person", ""),
              "e.g. Ramesh Gupta")
        field("Phone Number",     "phone",          p.get("phone", ""),
              "e.g. 98765 43210")
        field("Email",            "email",          p.get("email", ""),
              "e.g. supplier@email.com")
        field("City",             "city",           p.get("city", ""),
              "e.g. Mumbai")
        field("GST Number",       "gst_number",     p.get("gst_number", ""),
              "e.g. 27AAPFU0939F1ZV")

        # Notes
        ctk.CTkLabel(scroll, text="Notes", font=FONTS["label_form"],
                     text_color=COLORS["text_dark"]
                    ).pack(anchor="w", padx=24, pady=(6, 2))
        notes_box = ctk.CTkTextbox(scroll, font=FONTS["input"], height=80,
                                    border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"],
                                    border_width=2)
        notes_box.pack(fill="x", padx=24)
        if p.get("notes"):
            notes_box.insert("1.0", p["notes"])

        err_lbl = ctk.CTkLabel(scroll, text="", font=FONTS["small"],
                                text_color=COLORS["btn_danger"])
        err_lbl.pack(pady=(6, 0), padx=24, anchor="w")

        def save():
            name = entries["name"].get().strip()
            if not name:
                err_lbl.configure(text="⚠  Supplier name is required.")
                return
            data = {
                "name":           name,
                "contact_person": entries["contact_person"].get().strip() or None,
                "phone":          entries["phone"].get().strip() or None,
                "email":          entries["email"].get().strip() or None,
                "city":           entries["city"].get().strip() or None,
                "gst_number":     entries["gst_number"].get().strip() or None,
                "notes":          notes_box.get("1.0", "end-1c").strip() or None,
            }
            if self._editing_id:
                self.db.update_supplier(self._editing_id, data)
                messagebox.showinfo("Saved", f"Supplier '{name}' updated.", parent=dlg)
            else:
                self.db.add_supplier(data)
                messagebox.showinfo("Added", f"Supplier '{name}' added.", parent=dlg)
            dlg.destroy()
            self._load_suppliers()

        # Enter key submits the form
        dlg.bind("<Return>", lambda e: save())

        dlg.bind("<Return>", lambda e: save())  # SUP-2: Enter key submits form

        btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=14)
        ctk.CTkButton(btn_row, text="💾  Save Supplier",
                      font=FONTS["button"], fg_color=COLORS["btn_success"],
                      height=50, corner_radius=16,
                      command=save).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(btn_row, text="Cancel",
                      font=FONTS["button"], fg_color=COLORS["btn_secondary"],
                      height=50, corner_radius=16,
                      command=dlg.destroy).pack(side="left", width=110)

    def _record_payment(self):
        sid = self._get_selected_id()
        if not sid:
            return
        sup = self.db.get_supplier_by_id(sid)
        if not sup:
            return

        invoices = self.db.get_outstanding_purchases(sid)
        if not invoices:
            messagebox.showinfo("No Outstanding Bills",
                                f"No unpaid invoices found for '{sup['name']}'.",
                                parent=self.winfo_toplevel())
            return

        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title(f"Record Payment — {sup['name']}")
        dlg.geometry("540x480")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        scroll = ctk.CTkScrollableFrame(dlg, fg_color=COLORS["bg_main"])
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll, text=f"💰  Record Payment — {sup['name']}",
                     font=FONTS["heading"], text_color=COLORS["btn_primary"]
                    ).pack(pady=(16, 6), padx=20, anchor="w")
        ctk.CTkFrame(scroll, fg_color=COLORS["tbl_select"], height=2).pack(fill="x", padx=20, pady=(0, 12))

        ctk.CTkLabel(scroll, text="Select Invoice:",
                     font=FONTS["label_form"], text_color=COLORS["text_dark"]
                    ).pack(anchor="w", padx=20)

        inv_var = tk.StringVar()
        inv_map = {}
        for inv in invoices:
            label = f"  {inv['grn_number']}  |  Date: {inv['purchase_date']}  |  Balance: ₹{inv['balance']:.2f}"
            inv_map[label] = (inv["purchase_id"], inv["balance"])

        first = list(inv_map.keys())[0]
        inv_var.set(first)

        inv_menu = ctk.CTkOptionMenu(
            scroll, variable=inv_var,
            values=list(inv_map.keys()),
            font=FONTS["body"], height=44, width=490,
            fg_color=COLORS["btn_primary"], button_color="#005BBE",
            dynamic_resizing=False
        )
        inv_menu.pack(padx=20, pady=(4, 12))

        def _update_max(*_):
            _, bal = inv_map.get(inv_var.get(), (None, 0))
            max_lbl.configure(text=f"Balance due: ₹ {bal:.2f}")
        inv_var.trace_add("write", _update_max)

        amt_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        amt_frame.pack(fill="x", padx=20, pady=4)
        ctk.CTkLabel(amt_frame, text="Amount Paid (₹):",
                     font=FONTS["label_form"], text_color=COLORS["text_dark"],
                     width=180, anchor="w").pack(side="left")
        amt_var = tk.StringVar()
        ctk.CTkEntry(amt_frame, textvariable=amt_var,
                     placeholder_text="e.g. 5000",
                     font=FONTS["input"], height=44,
                     border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"],
                     width=260).pack(side="left")

        _, init_bal = inv_map[first]
        max_lbl = ctk.CTkLabel(scroll, text=f"Balance due: ₹ {init_bal:.2f}",
                                font=FONTS["small"], text_color=COLORS["btn_success"])
        max_lbl.pack(anchor="w", padx=20, pady=(0, 8))

        notes_ent = ctk.CTkEntry(scroll, placeholder_text="Notes (optional)",
                                  font=FONTS["input"], height=44,
                                  border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"])
        notes_ent.pack(fill="x", padx=20, pady=(0, 8))

        err_lbl = ctk.CTkLabel(scroll, text="", font=FONTS["small"], text_color=COLORS["btn_danger"])
        err_lbl.pack(anchor="w", padx=20)

        def save():
            purchase_id, balance = inv_map.get(inv_var.get(), (None, 0))
            if not purchase_id:
                err_lbl.configure(text="⚠  Please select an invoice.")
                return
            try:
                amount = float(amt_var.get().strip())
                if amount <= 0: raise ValueError
            except ValueError:
                err_lbl.configure(text="⚠  Enter a valid amount greater than 0.")
                return
            if amount > balance + 0.01:
                err_lbl.configure(text=f"⚠  Amount exceeds balance of ₹{balance:.2f}.")
                return
            uid = self.current_user.get("user_id") if self.current_user else None
            self.db.record_supplier_payment(purchase_id, amount, notes_ent.get().strip() or None, uid)
            messagebox.showinfo("Payment Recorded",
                                f"✅  ₹{amount:,.2f} recorded successfully.",
                                parent=dlg)
            dlg.destroy()

        btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=14)
        ctk.CTkButton(btn_row, text="💾  Save Payment",
                      font=FONTS["button"], fg_color=COLORS["btn_success"],
                      height=50, corner_radius=10,
                      command=save).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(btn_row, text="Cancel",
                      font=FONTS["button"], fg_color=COLORS["btn_secondary"],
                      height=50, corner_radius=10,
                      command=dlg.destroy).pack(side="left", width=110)

    def _deactivate(self):
        sid = self._get_selected_id()
       
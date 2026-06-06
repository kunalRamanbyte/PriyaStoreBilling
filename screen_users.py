"""
screen_users.py — User Management
Phase 4 | Admin-only

Features:
  • List all users (active + inactive toggle)
  • Add new user (name, username, password, role)
  • Edit name / role
  • Change password
  • Deactivate / Reactivate
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from config import COLORS, FONTS
from ui_utils import place_popup
from lang import t

ROLE_LABELS = {
    "admin"        : "Admin",
    "cashier"      : "Cashier",
    "stock_manager": "Stock Manager",
}
ROLES = list(ROLE_LABELS.values())
ROLE_BY_LABEL = {v: k for k, v in ROLE_LABELS.items()}

ROLE_COLORS = {
    "admin"        : COLORS["btn_purple"],
    "cashier"      : COLORS["btn_primary"],
    "stock_manager": COLORS["btn_success"],
}


class UserScreen(ctk.CTkFrame):

    COLS = [
        ("Name",     200),
        ("Username", 150),
        ("Role",     130),
        ("Status",    90),
        ("Created",  160),
    ]

    def __init__(self, parent, db, current_user, app):
        super().__init__(parent, fg_color=COLORS["bg_main"], corner_radius=0)
        self.db           = db
        self.current_user = current_user
        self.app          = app
        self._selected_id = None
        self._show_all    = tk.BooleanVar(value=False)
        self._build()

    # ─────────────────────────────────────────────────────────
    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        L = self.app.current_lang

        # ── Header ──
        hdr = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                           corner_radius=16, height=70)
        hdr.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 0))
        hdr.grid_propagate(False)
        ctk.CTkLabel(hdr, text=t("User Management", L),
                     font=FONTS["subheading"],
                     text_color=COLORS["text_dark"]).pack(side="left", padx=24, pady=18)
        ctk.CTkButton(
            hdr, text=t("Add User", L),
            font=FONTS["button"],
            fg_color=COLORS["btn_success"],
            hover_color="#28A745",
            height=42, width=140,
            command=self._open_add,
        ).pack(side="right", padx=18)
        ctk.CTkCheckBox(
            hdr, text=t("Show Inactive", L),
            font=FONTS["body"],
            text_color=COLORS["text_dark"],
            variable=self._show_all,
            command=self._load,
        ).pack(side="right", padx=8)

        # ── Table ──
        tbl_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                                  corner_radius=16)
        tbl_frame.grid(row=2, column=0, sticky="nsew",
                       padx=20, pady=(10, 0))
        tbl_frame.grid_rowconfigure(0, weight=1)
        tbl_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            tbl_frame,
            columns=[c for c, w in self.COLS],
            show="headings",
            style="User.Treeview",
            selectmode="browse",
        )
        # ttk styles applied globally via styles.py
        for col, w in self.COLS:
            self.tree.heading(col, text=t(col, L))
            self.tree.column(col, width=w, minwidth=60, anchor="center")
        self.tree.column("Name", anchor="w")

        # Row tags
        self.tree.tag_configure("inactive", background=COLORS["row_inactive"],
                                foreground=COLORS["fg_inactive"])
        self.tree.tag_configure("admin_row",  background=COLORS["row_admin"])
        self.tree.tag_configure("even",       background=COLORS["tbl_row_alt"])

        vsb = ttk.Scrollbar(tbl_frame, orient="vertical",
                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # ── Action bar ──
        action = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                               corner_radius=16, height=72)
        action.grid(row=3, column=0, sticky="ew", padx=20, pady=(8, 16))
        action.pack_propagate(False)

        self._btn_edit   = self._action_btn(action, t("✏️  Edit", L),        COLORS["btn_primary"], self._open_edit)
        self._btn_pwd    = self._action_btn(action, t("🔑  Change Pwd", L),  COLORS["btn_warning"],  self._change_pwd)
        self._btn_toggle = self._action_btn(action, t("🚫  Deactivate", L),  COLORS["btn_danger"],   self._toggle_status)

        for btn in (self._btn_edit, self._btn_pwd, self._btn_toggle):
            btn.pack(side="left", padx=8, pady=14)
            btn.configure(state="disabled")

        self._load()

    def _action_btn(self, parent, text, color, cmd):
        return ctk.CTkButton(parent, text=text, font=FONTS["button"],
                             fg_color=color, height=44, width=170,
                             command=cmd, state="disabled")

    # ─────────────────────────────────────────────────────────
    def _load(self):
        L = self.app.current_lang
        self.tree.delete(*self.tree.get_children())
        users = self.db.get_users(include_inactive=self._show_all.get())
        for i, u in enumerate(users):
            role_lbl = ROLE_LABELS.get(u["role"], u["role"])
            status   = "✅ Active" if u["is_active"] else "❌ Inactive"
            created  = str(u.get("created_at", ""))[:10]
            tags = []
            if not u["is_active"]:
                tags.append("inactive")
            elif u["role"] == "admin":
                tags.append("admin_row")
            elif i % 2 == 0:
                tags.append("even")
            self.tree.insert("", "end",
                             iid=str(u["user_id"]),
                             values=(u["name"], u["username"],
                                     role_lbl, status, created),
                             tags=tags)
        self._selected_id = None
        self._set_buttons_state(False)

    def _on_select(self, _=None):
        L = self.app.current_lang
        sel = self.tree.selection()
        if not sel:
            self._selected_id = None
            self._set_buttons_state(False)
            return
        self._selected_id = int(sel[0])
        u = self.db.get_user_by_id(self._selected_id)
        if not u:
            return
        self._set_buttons_state(True)
        # Can't deactivate yourself
        is_self = (self._selected_id == self.current_user["user_id"])
        active = bool(u["is_active"])
        self._btn_toggle.configure(
            text=t("Reactivate", L) if not active else t("Deactivate", L),
            fg_color=COLORS["btn_success"] if not active else COLORS["btn_danger"],
            state="disabled" if is_self else "normal",
        )

    def _set_buttons_state(self, on: bool):
        state = "normal" if on else "disabled"
        for b in (self._btn_edit, self._btn_pwd, self._btn_toggle):
            b.configure(state=state)

    # ─────────────────────────────────────────────────────────
    def _open_add(self):
        self._user_form(None)

    def _open_edit(self):
        if not self._selected_id:
            return
        u = self.db.get_user_by_id(self._selected_id)
        if u:
            self._user_form(u)

    def _user_form(self, user):
        """Add or Edit user dialog."""
        L = self.app.current_lang
        is_edit = user is not None
        dlg = ctk.CTkToplevel(self)
        dlg.title(t("Edit User", L) if is_edit else t("Add New User", L))
        place_popup(dlg, 480, 480)
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.configure(fg_color=COLORS["bg_main"])

        # Header
        hdr = ctk.CTkFrame(dlg, fg_color=COLORS["btn_primary"],
                           corner_radius=0, height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr,
                     text=t("Edit User", L) if is_edit else t("Add New User", L),
                     font=FONTS["subheading"], text_color="white").pack(
                          side="left", padx=20, pady=14)

        body = ctk.CTkFrame(dlg, fg_color=COLORS["bg_main"])
        body.pack(fill="both", expand=True, padx=24, pady=16)

        def _lbl(text):
            ctk.CTkLabel(body, text=text, font=FONTS["label_form"],
                          text_color=COLORS["text_dark"],
                          anchor="w").pack(fill="x", pady=(10, 2))

        def _ent(ph="", show=""):
            e = ctk.CTkEntry(body, font=FONTS["input"],
                             fg_color=COLORS["bg_input"],
                             border_color=COLORS["border"],
                             text_color=COLORS["text_dark"],
                             placeholder_text=ph,
                             show=show,
                             height=44)
            e.pack(fill="x")
            return e

        _lbl(t("Full Name *", L))
        e_name = _ent("e.g. Priya Sharma")
        _lbl(t("Username *", L))
        e_user = _ent("e.g. priya")
        _lbl(t("Role *", L))
        role_var = ctk.StringVar(value=ROLE_LABELS.get(user["role"] if is_edit else "cashier", "Cashier"))
        ctk.CTkOptionMenu(body, values=ROLES, variable=role_var,
                          font=FONTS["body"],
                          fg_color=COLORS["btn_primary"],
                          button_color=COLORS["btn_primary"],
                          height=44).pack(fill="x", pady=(4, 0))

        if not is_edit:
            _lbl(t("Password *", L))
            e_pwd = _ent(t("Enter at least 4 characters.", L), show="*")
        else:
            e_pwd = None

        if is_edit:
            e_name.insert(0, user["name"])
            e_user.insert(0, user["username"])
            e_user.configure(state="disabled")  # username can't change

        def _save():
            name = e_name.get().strip()
            uname = e_user.get().strip().lower() if not is_edit else user["username"]
            role  = ROLE_BY_LABEL.get(role_var.get(), "cashier")

            if not name:
                messagebox.showwarning(t("Required", L), t("Name is required.", L), parent=dlg)
                return
            if not is_edit and not uname:
                messagebox.showwarning(t("Required", L), t("Username is required.", L), parent=dlg)
                return

            if is_edit:
                self.db.update_user(user["user_id"], name, role)
                self.db.log_activity(self.current_user["user_id"],
                                     "USER_UPDATED", f"User '{uname}' updated")
                messagebox.showinfo(t("Saved", L), f"User '{name}' " + t("User updated.", L), parent=dlg)
            else:
                pwd = e_pwd.get().strip()
                if len(pwd) < 4:
                    messagebox.showwarning(t("Weak Password", L),
                                           t("Enter at least 4 characters.", L),
                                           parent=dlg)
                    return
                ok, result = self.db.add_user(name, uname, pwd, role)
                if not ok:
                    messagebox.showerror(t("Error", L), result, parent=dlg)
                    return
                self.db.log_activity(self.current_user["user_id"],
                                     "USER_ADDED", f"New user '{uname}' ({role}) added")
                messagebox.showinfo(t("Created", L), f"User '{name}' " + t("User added.", L), parent=dlg)

            dlg.destroy()
            self._load()

        ctk.CTkButton(body, text=t("Save", L),
                      font=FONTS["button"],
                      fg_color=COLORS["btn_success"],
                      hover_color="#28A745",
                      height=48,
                      command=_save).pack(fill="x", pady=(18, 0))

    # ─────────────────────────────────────────────────────────
    def _change_pwd(self):
        L = self.app.current_lang
        if not self._selected_id:
            return
        u = self.db.get_user_by_id(self._selected_id)
        if not u:
            return

        dlg = ctk.CTkToplevel(self)
        dlg.title(t("Change Password", L))
        place_popup(dlg, 420, 300)
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.configure(fg_color=COLORS["bg_main"])

        hdr = ctk.CTkFrame(dlg, fg_color=COLORS["btn_warning"],
                           corner_radius=0, height=56)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text=t("Change Password", L) + f" — {u['name']}",
                     font=FONTS["body_bold"], text_color="white").pack(
                          side="left", padx=20, pady=14)

        body = ctk.CTkFrame(dlg, fg_color=COLORS["bg_main"])
        body.pack(fill="both", expand=True, padx=24, pady=16)

        ctk.CTkLabel(body, text=t("New Password *", L),
                     font=FONTS["label_form"],
                     text_color=COLORS["text_dark"],
                     anchor="w").pack(fill="x", pady=(8, 2))
        e_new = ctk.CTkEntry(body, font=FONTS["input"],
                             fg_color=COLORS["bg_input"],
                             border_color=COLORS["border"],
                             text_color=COLORS["text_dark"],
                             show="*", height=44)
        e_new.pack(fill="x")

        ctk.CTkLabel(body, text=t("Confirm Password *", L),
                     font=FONTS["label_form"],
                     text_color=COLORS["text_dark"],
                     anchor="w").pack(fill="x", pady=(12, 2))
        e_confirm = ctk.CTkEntry(body, font=FONTS["input"],
                                 fg_color=COLORS["bg_input"],
                                 border_color=COLORS["border"],
                                 text_color=COLORS["text_dark"],
                                 show="*", height=44)
        e_confirm.pack(fill="x")

        def _save():
            p1 = e_new.get().strip()
            p2 = e_confirm.get().strip()
            if len(p1) < 4:
                messagebox.showwarning(t("Weak", L), t("Enter at least 4 characters.", L), parent=dlg)
                return
            if p1 != p2:
                messagebox.showwarning(t("Mismatch", L), t("Passwords do not match.", L), parent=dlg)
                return
            self.db.change_password(u["user_id"], p1)
            self.db.log_activity(self.current_user["user_id"],
                                 "PWD_CHANGED",
                                 f"Password changed for '{u['username']}'")
            messagebox.showinfo(t("Done", L), t("Password changed.", L), parent=dlg)
            dlg.destroy()

        ctk.CTkButton(body, text=t("Update Password", L),
                      font=FONTS["button"],
                      fg_color=COLORS["btn_warning"],
                      hover_color="#CC7700",
                      height=48,
                      command=_save).pack(fill="x", pady=(18, 0))

    # ─────────────────────────────────────────────────────────
    def _toggle_status(self):
        L = self.app.current_lang
        if not self._selected_id:
            return
        if self._selected_id == self.current_user["user_id"]:
            messagebox.showwarning(t("Warning", L), t("Admin cannot be deactivated.", L))
            return
        u = self.db.get_user_by_id(self._selected_id)
        if not u:
            return
        if u["is_active"]:
            msg_tpl = "Deactivate user '{name}'?\nThey will not be able to log in."
            if not messagebox.askyesno(
                    t("Deactivate", L),
                    t(msg_tpl, L).format(name=u['name'])):
                return
            self.db.deactivate_user(u["user_id"])
            self.db.log_activity(self.current_user["user_id"],
                                 "USER_DEACTIVATED",
                                 f"User '{u['username']}' deactivated")
        else:
            self.db.reactivate_user(u["user_id"])
            self.db.log_activity(self.current_user["user_id"],
                                 "USER_REACTIVATED",
                                 f"User '{u['username']}' reactivated")
        self._load()

    def on_show(self):
        self._load()

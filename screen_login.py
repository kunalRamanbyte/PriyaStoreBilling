"""
screen_login.py — Login screen

Direction B: a single split card centred on the app canvas. The left panel
is the deep blue brand block; the right panel is the form. Solid fills,
hairline borders and generous radii only — no photographic background, no
gradient, no glass. Default: admin / admin123
"""

import os
import glob
from datetime import datetime
import customtkinter as ctk
from config import (COLORS, FONTS, RADII, METRICS, APP_VERSION, SHOP_NAME,
                    DB_PATH)
from lang import t


class LoginScreen(ctk.CTkFrame):
    def __init__(self, parent, on_success_callback):
        super().__init__(parent, fg_color=COLORS["bg_main"], corner_radius=0)
        self.on_success = on_success_callback
        self._lang = getattr(self.winfo_toplevel(), "current_lang", "English") or "English"
        self._pwd_shown = False
        self._build()

    # ── Helpers ─────────────────────────────────────────────
    def _backup_chip_text(self):
        """Direction B shows a backup chip on the brand panel. Report what
        is actually on disk rather than a decorative 'Backed up today'."""
        L = self._lang
        try:
            db = getattr(self.winfo_toplevel(), "db", None)
            folder = None
            if db is not None:
                folder = db.get_setting("backup_folder", "") or None
            if not folder:
                folder = os.path.join(os.path.dirname(DB_PATH), "backups")
            files = glob.glob(os.path.join(folder, "billing_backup*.db"))
            if not files:
                return t("No backup yet", L)
            newest = max(files, key=os.path.getmtime)
            when = datetime.fromtimestamp(os.path.getmtime(newest))
            if when.date() == datetime.now().date():
                return t("Backed up today", L)
            return f"{t('Last backup', L)} {when.strftime('%d %b')}"
        except Exception:
            return t("No backup yet", L)

    def _chip(self, parent, text):
        """A 32px white pill on the blue brand panel."""
        chip = ctk.CTkFrame(parent, fg_color=COLORS["on_accent"],
                            corner_radius=16, height=32)
        chip.pack(side="left", padx=(0, 10))
        chip.pack_propagate(False)
        ctk.CTkLabel(chip, text=text, font=FONTS["caption"],
                     text_color=COLORS["accent_action_deep"]
                     ).pack(padx=14, pady=6)
        return chip

    def _field(self, parent, show=None):
        """A 52px pill field that takes a blue focus ring, matching the
        password field's focused state in the artboard."""
        e = ctk.CTkEntry(
            parent,
            show=show,
            font=("Segoe UI", 17),
            height=52,
            border_width=2,
            border_color=COLORS["bg_input"],   # invisible until focused
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_dark"],
            corner_radius=26,
        )
        e.bind("<FocusIn>", lambda _e: e.configure(
            border_color=COLORS["accent_action"], fg_color=COLORS["bg_white"]))
        e.bind("<FocusOut>", lambda _e: e.configure(
            border_color=COLORS["bg_input"], fg_color=COLORS["bg_input"]))
        return e

    # ── Build ───────────────────────────────────────────────
    def _build(self):
        L = self._lang

        # ── The split card ───────────────────────────────────
        card = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                            corner_radius=RADII["hero"],
                            width=940, height=560,
                            border_width=1, border_color=COLORS["hairline"])
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        # ── Left: brand panel ────────────────────────────────
        # CustomTkinter cannot clip a child to its parent's rounded corners,
        # so the blue block is inset and carries its own radius instead of
        # sitting flush to the card edge.
        brand = ctk.CTkFrame(card, fg_color=COLORS["accent_action_deep"],
                             corner_radius=RADII["pill_lg"], width=376)
        brand.pack(side="left", fill="y", padx=12, pady=12)
        brand.pack_propagate(False)

        # Top: mark + name
        top = ctk.CTkFrame(brand, fg_color="transparent")
        top.pack(fill="x", padx=32, pady=(32, 0))

        mark = ctk.CTkFrame(top, fg_color=COLORS["on_accent"],
                            corner_radius=15, width=42, height=42)
        mark.pack(side="left", padx=(0, 11))
        mark.pack_propagate(False)
        ctk.CTkLabel(mark, text=SHOP_NAME[0].upper(),
                     font=("Segoe UI Semibold", 18, "bold"),
                     text_color=COLORS["accent_action_deep"]
                     ).place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(top, text=SHOP_NAME,
                     font=("Segoe UI Semibold", 17, "bold"),
                     text_color=COLORS["on_accent"]).pack(side="left")

        # Middle: the promise
        mid = ctk.CTkFrame(brand, fg_color="transparent")
        mid.pack(fill="both", expand=True, padx=32)
        ctk.CTkLabel(mid, text=t("Ring it up in seconds.", L),
                     font=("Segoe UI Semibold", 32, "bold"),
                     text_color=COLORS["on_accent"],
                     wraplength=300, justify="left", anchor="w"
                     ).pack(anchor="w", pady=(0, 12))
        ctk.CTkLabel(
            mid,
            text=t("Bills, stock, udhaar and reports — one window, keyboard first.", L),
            font=FONTS["body"], text_color=COLORS["on_accent_soft"],
            wraplength=300, justify="left", anchor="w"
        ).pack(anchor="w")

        # Bottom: status chips
        chips = ctk.CTkFrame(brand, fg_color="transparent")
        chips.pack(fill="x", padx=32, pady=(0, 32))
        self._chip(chips, f"v{APP_VERSION}")
        self._chip(chips, self._backup_chip_text())

        # ── Right: form ──────────────────────────────────────
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(side="left", fill="both", expand=True, padx=(44, 56), pady=52)

        inner = ctk.CTkFrame(form, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center", relwidth=1.0)

        ctk.CTkLabel(inner, text=t("Welcome back", L),
                     font=("Segoe UI Semibold", 30, "bold"),
                     text_color=COLORS["text_dark"], anchor="w"
                     ).pack(fill="x")
        ctk.CTkLabel(inner, text=t("Sign in to open the counter.", L),
                     font=FONTS["body"], text_color=COLORS["text_muted"],
                     anchor="w").pack(fill="x", pady=(6, 28))

        # Username
        ctk.CTkLabel(inner, text=t("Username", L), font=FONTS["small"],
                     text_color=COLORS["text_secondary"], anchor="w"
                     ).pack(fill="x", pady=(0, 7))
        self.username_entry = self._field(inner)
        self.username_entry.pack(fill="x", pady=(0, 16))

        # Password + show/hide
        ctk.CTkLabel(inner, text=t("Password", L), font=FONTS["small"],
                     text_color=COLORS["text_secondary"], anchor="w"
                     ).pack(fill="x", pady=(0, 7))

        pwd_row = ctk.CTkFrame(inner, fg_color="transparent")
        pwd_row.pack(fill="x")
        self.password_entry = self._field(pwd_row, show="●")
        self.password_entry.pack(side="left", fill="x", expand=True)

        self.show_btn = ctk.CTkButton(
            pwd_row, text=t("Show", L), width=62, height=52,
            font=FONTS["button"], fg_color="transparent",
            hover_color=COLORS["accent_action_tint"],
            text_color=COLORS["accent_action"],
            corner_radius=26, border_width=0,
            command=self._toggle_password,
        )
        self.show_btn.pack(side="left", padx=(6, 0))

        # Error label
        self.error_label = ctk.CTkLabel(
            inner, text="", font=FONTS["small"],
            text_color=COLORS["accent_danger"], anchor="w",
        )
        self.error_label.pack(fill="x", pady=(8, 0))

        # Sign in — the one solid blue CTA on the screen
        self.login_btn = ctk.CTkButton(
            inner,
            text="🔒   " + t("Sign In", L),
            font=("Segoe UI Semibold", 17, "bold"),
            fg_color=COLORS["accent_action"],
            hover_color=COLORS["btn_primary_h"],
            text_color=COLORS["on_accent"],
            height=METRICS["control_lg"],
            corner_radius=RADII["pill_lg"],
            border_width=0,
            command=self._do_login,
        )
        self.login_btn.pack(fill="x", pady=(16, 0))

        # Hint — only while the seeded default admin password is still in
        # place, so we don't advertise credentials that no longer work (or
        # that a security-conscious owner has already changed).
        try:
            show_hint = self.winfo_toplevel().db.is_default_admin_active()
        except Exception:
            show_hint = False
        if show_hint:
            ctk.CTkLabel(
                inner,
                text=t("First run? Use admin / admin123, then change it in Settings.", L),
                font=FONTS["small"], text_color=COLORS["text_muted"],
                anchor="w", justify="left", wraplength=420,
            ).pack(fill="x", pady=(16, 0))

        # Keyboard bindings
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self._do_login())
        self.after(100, self.username_entry.focus)

    # ── Behaviour ───────────────────────────────────────────
    def _toggle_password(self):
        self._pwd_shown = not self._pwd_shown
        self.password_entry.configure(show="" if self._pwd_shown else "●")
        self.show_btn.configure(
            text=t("Hide" if self._pwd_shown else "Show", self._lang))

    def _do_login(self):
        L = self._lang
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.error_label.configure(text="⚠  " + t("Please enter username and password.", L))
            return

        app = self.winfo_toplevel()
        user = app.db.authenticate(username, password)

        if user:
            self.error_label.configure(text="")
            self.on_success(user)
        else:
            self.error_label.configure(text="❌  " + t("Wrong username or password. Try again.", L))
            self.password_entry.delete(0, "end")
            self.password_entry.focus()

"""
screen_settings.py — Shop Settings & Configuration
Phase 4 | Admin-only

Sections:
  • Shop Info  — name, address, phone, GST, city
  • Bill Config — prefix, starting number, thermal width
  • Backup      — manual backup, custom folder, scheduled daily, restore
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import os
import shutil
import sqlite3
import applog
from datetime import datetime
from config import COLORS, FONTS, RADII, METRICS, GUTTERS
from responsive import ResponsiveMixin
from lang import LANGUAGES, LANG_DB_VALUES, t


def _is_valid_sqlite(path: str) -> bool:
    """True if `path` is a readable SQLite database file."""
    try:
        if not os.path.isfile(path) or os.path.getsize(path) < 100:
            return False
        with open(path, "rb") as fh:
            if fh.read(16) != b"SQLite format 3\x00":
                return False
        con = sqlite3.connect(path)
        try:
            con.execute("PRAGMA schema_version;").fetchone()
        finally:
            con.close()
        return True
    except Exception:
        return False


class SettingsScreen(ResponsiveMixin, ctk.CTkFrame):

    FIELDS = [
        # (key, label, placeholder, section)
        # shop_name is intentionally omitted: main.py enforces it to "Priya Store"
        # on every startup, so an editable field here would silently revert.
        ("shop_address", "Address",            "Street / Area",                     "shop"),
        ("shop_city",    "City",               "e.g. Mumbai",                       "shop"),
        ("shop_phone",   "Phone",              "+91 XXXXX XXXXX",                   "shop"),
        ("shop_gst",     "GST Number",         "e.g. 27AABCU9603R1ZX",             "shop"),
        ("bill_prefix",  "Bill Prefix *",      "e.g. BILL or INV",                  "bill"),
        ("next_bill_no", "Next Bill Number *", "e.g. 1",                            "bill"),
        ("paper_width",  "Thermal Paper Width","58mm  or  80mm",                   "bill"),
    ]

    def __init__(self, parent, db, current_user, app):
        super().__init__(parent, fg_color=COLORS["bg_main"], corner_radius=0)
        self.db           = db
        self.current_user = current_user
        self.app          = app
        self._entries     = {}
        # _ensure_section() reloads values into freshly built widgets, but not
        # while _build() is still running — _build() does its own _load().
        self._ready       = False
        self._build()
        self._ready       = True

    # ─────────────────────────────────────────────────────────
    # -- Direction B primitives ------------------------------
    def _card(self, parent, title=None, subtitle=None):
        """White surface, 24px corners, hairline border, optional heading."""
        card = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"],
                            corner_radius=RADII["card"], border_width=1,
                            border_color=COLORS["hairline"])
        card.pack(fill="x", pady=(0, 14))
        if title:
            head = ctk.CTkFrame(card, fg_color="transparent")
            head.pack(fill="x", padx=24, pady=(20, 0))
            ctk.CTkLabel(head, text=title, font=FONTS["subheading"],
                         text_color=COLORS["text_dark"], anchor="w"
                         ).pack(anchor="w")
            if subtitle:
                ctk.CTkLabel(head, text=subtitle, font=FONTS["small"],
                             text_color=COLORS["text_muted"], anchor="w"
                             ).pack(anchor="w", pady=(2, 0))
        return card

    def _pill(self, parent, text, kind="plain", command=None, width=None,
              height=None):
        tints = {
            "primary": (COLORS["accent_action"], COLORS["btn_primary_h"], COLORS["on_accent"]),
            "action":  (COLORS["accent_action_tint"], COLORS["glass_glow"], COLORS["accent_action_fg"]),
            "money":   (COLORS["accent_money_tint"], COLORS["accent_money_tint"], COLORS["accent_money_fg"]),
            "expiry":  (COLORS["accent_expiry_tint"], COLORS["accent_expiry_tint"], COLORS["accent_expiry_fg"]),
            "danger":  (COLORS["accent_danger_tint"], COLORS["accent_danger_tint"], COLORS["accent_danger_fg"]),
            "danger_solid": (COLORS["accent_danger"], COLORS["btn_danger_h"], COLORS["on_accent"]),
            "plain":   (COLORS["bg_main"], COLORS["glass_glow"], COLORS["text_dark"]),
        }
        fg, hov, ink = tints.get(kind, tints["plain"])
        h = height or METRICS["control"]
        kw = {"width": width} if width else {}
        return ctk.CTkButton(parent, text=text, font=FONTS["button"],
                             fg_color=fg, hover_color=hov, text_color=ink,
                             height=h, corner_radius=h // 2, border_width=0,
                             command=command, **kw)

    def _row(self, parent, label, hint=None):
        """A label column plus a control column, the artboard's field row.

        The label is a fixed-width CTkLabel rather than a frame: a frame with
        pack_propagate(False) and no height keeps CTkFrame's default 200px and
        turns every field row into a 200px block."""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=24, pady=8)
        text = f"{label}\n{hint}" if hint else label
        ctk.CTkLabel(row, text=text, font=FONTS["label_form"],
                     text_color=COLORS["text_muted"], anchor="w",
                     justify="left", width=170).pack(side="left")
        return row

    def _entry(self, parent, placeholder="", width=None):
        kw = {"width": width} if width else {}
        return ctk.CTkEntry(parent, font=FONTS["input"],
                            fg_color=COLORS["bg_input"],
                            border_width=1, border_color=COLORS["hairline"],
                            text_color=COLORS["text_dark"],
                            placeholder_text=placeholder,
                            corner_radius=RADII["input"],
                            height=46, **kw)

    # -- Build ------------------------------------------------
    def _build(self):
        L = self.app.current_lang
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # -- Header band -------------------------------------
        hdr = ctk.CTkFrame(self, fg_color="transparent", height=METRICS["header"])
        self._hdr = hdr
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew", padx=28)
        hdr.grid_propagate(False)

        titles = ctk.CTkFrame(hdr, fg_color="transparent")
        titles.pack(side="left", fill="y")
        ctk.CTkLabel(titles, text=t("Settings", L),
                     font=("Segoe UI Semibold", 26, "bold"),
                     text_color=COLORS["text_dark"], anchor="w"
                     ).pack(anchor="w", pady=(16, 0))
        ctk.CTkLabel(titles, text=t("Shop details, bill numbering, backups", L),
                     font=FONTS["small"], text_color=COLORS["text_muted"],
                     anchor="w").pack(anchor="w")

        self._pill(hdr, "\U0001F4BE  " + t("Save changes", L), kind="primary",
                   width=170, height=46, command=self._save
                   ).pack(side="right", pady=15)

        # -- Section nav -------------------------------------
        nav = ctk.CTkFrame(self, fg_color="transparent", width=200)
        self._nav = nav
        nav.grid(row=1, column=0, sticky="nsew", padx=(28, 0), pady=(0, 20))
        nav.pack_propagate(False)

        self._sections = {}
        self._section_btns = {}

        # -- Content stack -----------------------------------
        stack = ctk.CTkFrame(self, fg_color="transparent")
        stack.grid(row=1, column=1, sticky="nsew", padx=(20, 28), pady=(0, 20))
        self._stack_holder = stack
        self._stack = stack

        def make_section(key, label, icon):
            panel = ctk.CTkScrollableFrame(stack, fg_color="transparent",
                                           corner_radius=0)
            self._sections[key] = panel
            btn = ctk.CTkButton(
                nav, text=f"  {icon}  {t(label, L)}", font=FONTS["sidebar"],
                fg_color="transparent", hover_color=COLORS["sidebar_hover"],
                text_color=COLORS["sidebar_text"], anchor="w",
                height=METRICS["nav_item"], corner_radius=RADII["sidebar"],
                border_width=0, command=lambda k=key: self._show_section(k),
            )
            btn.pack(fill="x", pady=2)
            self._section_btns[key] = btn
            return panel

        shop_p   = make_section("shop",     "Shop",             "\U0001F3EA")
        bill_p   = make_section("billing",  "Billing",          "\U0001F9FE")
        backup_p = make_section("backup",   "Backup",           "\U0001F4BE")
        lang_p   = make_section("language", "Language & Theme", "\U0001F310")
        danger_p = None
        if self.current_user.get("role") == "admin":
            danger_p = make_section("danger", "Danger Zone", "\u26A0\uFE0F")

        # Each section's BODY is built the first time that section is
        # opened. Building all five up front made this the most expensive
        # screen in the app — 269 widgets, ~534ms of Tcl round-trips inside
        # navigate_to() — to show a shopkeeper a single card. The five panels
        # created above are cheap; only their contents are not.
        self._builders = {
            "shop":     self._build_shop,
            "billing":  self._build_billing,
            "language": self._build_language,
            "backup":   self._build_backup,
            "danger":   self._build_danger,
        }
        self._built = set()


        self._show_section("shop")
        self._load()
        self.bind_responsive()

    def _build_shop(self, panel):
        """Built on first open — see _ensure_section()."""
        L = self.app.current_lang
        # -- Shop ---------------------------------------------
        card = self._card(panel, t("Shop Information", L),
                          t("Printed at the top of every receipt.", L))
        pad = ctk.CTkFrame(card, fg_color="transparent", height=6)
        pad.pack()
        for key, label, ph, sec in self.FIELDS:
            if sec != "shop":
                continue
            row = self._row(card, t(label, L))
            ent = self._entry(row, t(ph, L))
            ent.pack(side="left", fill="x", expand=True)
            self._entries[key] = ent
        ctk.CTkFrame(card, fg_color="transparent", height=10).pack()


    def _build_billing(self, panel):
        """Built on first open — see _ensure_section()."""
        L = self.app.current_lang
        # -- Billing ------------------------------------------
        card = self._card(panel, t("Bill Configuration", L))
        ctk.CTkFrame(card, fg_color="transparent", height=6).pack()
        for key, label, ph, sec in self.FIELDS:
            if sec != "bill":
                continue
            row = self._row(card, t(label, L))
            ent = self._entry(row, t(ph, L), width=240)
            ent.pack(side="left")
            self._entries[key] = ent
            if key == "next_bill_no":
                self._next_bill_hint = ctk.CTkLabel(
                    row, text="", font=FONTS["small"],
                    text_color=COLORS["accent_action_deep"], anchor="w")
                self._next_bill_hint.pack(side="left", padx=(14, 0))
        ctk.CTkFrame(card, fg_color="transparent", height=10).pack()


    def _build_language(self, panel):
        """Built on first open — see _ensure_section()."""
        L = self.app.current_lang
        # -- Language & Theme ---------------------------------
        card = self._card(panel, t("Language & Theme", L))
        ctk.CTkFrame(card, fg_color="transparent", height=6).pack()

        row = self._row(card, t("Select Language", L))
        self._lang_var = tk.StringVar()
        self._lang_menu = ctk.CTkOptionMenu(
            card, variable=self._lang_var, values=LANGUAGES,
            font=FONTS["input"], height=46, width=280,
            corner_radius=RADII["input"],
            fg_color=COLORS["bg_input"], button_color=COLORS["accent_action"],
            button_hover_color=COLORS["btn_primary_h"],
            text_color=COLORS["text_dark"],
            dropdown_fg_color=COLORS["bg_card"],
            dropdown_text_color=COLORS["text_dark"],
            command=self._change_language,
        )
        self._lang_menu.pack(in_=row, side="left")

        # Appearance is the artboard's segmented control, not a dropdown.
        row = self._row(card, t("Appearance", L))
        seg = ctk.CTkFrame(row, fg_color=COLORS["bg_input"],
                           corner_radius=RADII["input"])
        seg.pack(side="left")
        self._theme_var = tk.StringVar(value="System")
        self._theme_chips = {}
        for mode in ("Light", "Dark", "System"):
            chip = ctk.CTkButton(
                seg, text=t(mode, L), font=FONTS["small"],
                fg_color="transparent", hover_color=COLORS["glass_glow"],
                text_color=COLORS["text_muted"], height=38, width=88,
                corner_radius=19, border_width=0,
                command=lambda m=mode: self._pick_theme(m),
            )
            chip.pack(side="left", padx=2, pady=4)
            self._theme_chips[mode] = chip
        # _load() sets _theme_var directly, so repaint from the variable.
        self._theme_var.trace_add("write", lambda *_: self._paint_theme_chips())

        row = self._row(card, t("Smooth Animations", L))
        ctk.CTkLabel(row,
                     text=t("Slide and fade between screens and dialogs", L),
                     font=FONTS["small"], text_color=COLORS["text_muted"],
                     anchor="w", justify="left", wraplength=380
                     ).pack(side="left", fill="x", expand=True)
        self._anim_var = tk.BooleanVar(value=True)
        ctk.CTkSwitch(row, text="", variable=self._anim_var,
                      fg_color=COLORS["hairline"],
                      progress_color=COLORS["accent_money"],
                      button_color=COLORS["bg_white"],
                      command=self._toggle_animations).pack(side="right")
        ctk.CTkFrame(card, fg_color="transparent", height=10).pack()


    def _build_backup(self, panel):
        """Built on first open — see _ensure_section()."""
        L = self.app.current_lang
        # -- Backup -------------------------------------------
        card = self._card(panel, t("Backup & Restore", L))
        ctk.CTkFrame(card, fg_color="transparent", height=6).pack()

        row = self._row(card, t("Last Backup", L))
        self._last_backup_label = ctk.CTkLabel(
            row, text="\u2014", font=FONTS["body"],
            text_color=COLORS["text_muted"], anchor="w")
        self._last_backup_label.pack(side="left", fill="x", expand=True)
        self._pill(row, "\U0001F504  " + t("Backup Now", L), kind="action",
                   width=160, command=self._do_backup).pack(side="right")

        row = self._row(card, t("Backup Folder", L))
        self._folder_label = ctk.CTkLabel(
            row, text=t("Default (app folder)", L), font=FONTS["small"],
            text_color=COLORS["text_muted"], anchor="w", wraplength=320,
            justify="left")
        self._folder_label.pack(side="left", fill="x", expand=True)
        self._pill(row, t("Reset to Default", L), kind="plain", width=150,
                   command=self._reset_backup_folder).pack(side="right", padx=(8, 0))
        self._pill(row, "\U0001F4C2  " + t("Choose Folder", L), kind="expiry",
                   width=160, command=self._choose_backup_folder).pack(side="right")

        row = self._row(card, t("Daily Auto-Backup", L))
        ctk.CTkLabel(row,
                     text=t("Automatically backup once every 24 hours while the app is open", L),
                     font=FONTS["small"], text_color=COLORS["text_muted"],
                     anchor="w", justify="left", wraplength=380
                     ).pack(side="left", fill="x", expand=True)
        self._auto_backup_var = tk.BooleanVar(value=True)
        ctk.CTkSwitch(row, text="", variable=self._auto_backup_var,
                      fg_color=COLORS["hairline"],
                      progress_color=COLORS["accent_money"],
                      button_color=COLORS["bg_white"],
                      command=self._toggle_auto_backup).pack(side="right")

        row = self._row(card, t("Restore from Backup", L))
        ctk.CTkLabel(row,
                     text=t("Replace current data with a previous backup file (.db)", L),
                     font=FONTS["small"], text_color=COLORS["text_muted"],
                     anchor="w", justify="left", wraplength=340
                     ).pack(side="left", fill="x", expand=True)
        self._pill(row, "\u267B\uFE0F  " + t("Restore Backup", L), kind="danger",
                   width=170, command=self._do_restore).pack(side="right")
        ctk.CTkFrame(card, fg_color="transparent", height=10).pack()

        # -- Problem Reports ----------------------------------
        # The app keeps a log; this is the only place a shopkeeper can reach
        # it. Everything here is read-only and carries no bill or customer
        # data, so it is safe to send to support as-is.
        card = self._card(panel, t("Problem Reports", L),
                          t("If something goes wrong, send these details for support.", L))
        ctk.CTkFrame(card, fg_color="transparent", height=6).pack()

        row = self._row(card, t("Recent Problems", L))
        self._problem_label = ctk.CTkLabel(
            row, text="—", font=FONTS["body"],
            text_color=COLORS["text_muted"], anchor="w")
        self._problem_label.pack(side="left", fill="x", expand=True)
        self._pill(row, "📋  " + t("Copy Details", L), kind="action",
                   width=170, command=self._copy_diagnostics).pack(side="right")

        row = self._row(card, t("Log File", L))
        self._log_label = ctk.CTkLabel(
            row, text=applog.log_file() or "—", font=FONTS["small"],
            text_color=COLORS["text_muted"], anchor="w", wraplength=320,
            justify="left")
        self._log_label.pack(side="left", fill="x", expand=True)
        self._pill(row, "📂  " + t("Open Log Folder", L), kind="plain",
                   width=180, command=self._open_log_folder).pack(side="right")
        ctk.CTkFrame(card, fg_color="transparent", height=10).pack()


    def _build_danger(self, panel):
        """Built on first open — see _ensure_section()."""
        L = self.app.current_lang
        # -- Danger Zone (admin only) -------------------------
        card = ctk.CTkFrame(panel, fg_color=COLORS["accent_danger_tint"],
                            corner_radius=RADII["card"], border_width=1,
                            border_color=COLORS["accent_danger"])
        card.pack(fill="x", pady=(0, 14))
        head = ctk.CTkFrame(card, fg_color="transparent")
        head.pack(fill="x", padx=24, pady=(20, 0))
        ctk.CTkLabel(head, text=t("Factory Reset / Format Data", L),
                     font=FONTS["subheading"],
                     text_color=COLORS["accent_danger"], anchor="w"
                     ).pack(anchor="w")
        ctk.CTkLabel(
            head,
            text=t("Permanently delete ALL bills, products, categories, "
                   "customers, suppliers, stock data and non-admin users. "
                   "Only admin accounts and settings are kept.", L),
            font=FONTS["small"], text_color=COLORS["accent_danger"],
            anchor="w", justify="left", wraplength=560
        ).pack(anchor="w", pady=(4, 0))
        self._pill(card, "\U0001F5D1\uFE0F  " + t("Format Data", L),
                   kind="danger_solid", width=190, height=46,
                   command=self._do_format_data).pack(anchor="w", padx=24,
                                                      pady=(16, 22))

    def on_breakpoint(self, bp, logical_w):
        g = GUTTERS[bp]
        self._hdr.grid_configure(padx=g)
        self._nav.grid_configure(padx=(g, 0))
        self._stack_holder.grid_configure(padx=(16 if bp == "compact" else 20, g))
        self._nav.configure(width=160 if bp == "compact" else 200)

    # -- Section switching ------------------------------------
    def _ensure_section(self, key):
        """Build a section's body the first time anything needs it.

        Called by _show_section() and by _save(), which reads fields out of
        the Billing section a shopkeeper may never have opened.

        `_built` is recorded only AFTER the builder returns — the same rule
        the Categories card grid follows — so a builder that raises partway
        cannot cache a half-built panel and lock it in for the life of the
        screen.
        """
        if key in self._built or key not in self._sections:
            return
        builder = self._builders.get(key)
        if builder is None:
            return
        builder(self._sections[key])
        self._built.add(key)
        if self._ready:
            self._load()        # new widgets arrive empty; _load() fills them

    def _show_section(self, key):
        self._ensure_section(key)
        for name, panel in self._sections.items():
            if name == key:
                panel.pack(fill="both", expand=True)
            else:
                panel.pack_forget()
        for name, btn in self._section_btns.items():
            on = name == key
            danger = name == "danger"
            btn.configure(
                fg_color=((COLORS["accent_danger"] if danger
                           else COLORS["sidebar_active"]) if on else "transparent"),
                text_color=(COLORS["on_accent"] if on else
                            (COLORS["accent_danger"] if danger
                             else COLORS["sidebar_text"])),
                hover_color=((COLORS["accent_danger"] if danger
                              else COLORS["sidebar_active"]) if on
                             else COLORS["sidebar_hover"]),
            )
        self._active_section = key

    # -- Appearance segmented control -------------------------
    def _pick_theme(self, mode):
        self._theme_var.set(mode)     # trace repaints the chips
        self._change_theme(mode)

    def _paint_theme_chips(self):
        current = self._theme_var.get()
        for mode, chip in self._theme_chips.items():
            on = mode == current
            chip.configure(
                fg_color=COLORS["accent_action"] if on else "transparent",
                text_color=COLORS["on_accent"] if on else COLORS["text_muted"],
                hover_color=(COLORS["accent_action"] if on
                             else COLORS["glass_glow"]),
                font=FONTS["small_bold"] if on else FONTS["small"],
            )


    # ─────────────────────────────────────────────────────────
    def _load(self):
        s = self.db.get_all_settings()
        for key, ent in self._entries.items():
            val = s.get(key, "")
            ent.delete(0, "end")
            ent.insert(0, val)
        # Every widget below belongs to a section that may not be built
        # yet, so each is fetched defensively. _ensure_section() calls _load()
        # again once a section appears, which is what fills it in.
        if getattr(self, "_last_backup_label", None) is not None:
            last = s.get("last_backup", "")
            self._last_backup_label.configure(
                text=last if last else "No backup yet")

        # -- Language & Theme section, if it has been built --------
        if getattr(self, "_lang_var", None) is not None:
            saved_lang = s.get("app_language", "English")
            # Map DB value to display name
            lang_display = "English"
            for display, db_val in zip(LANGUAGES, LANG_DB_VALUES):
                if db_val == saved_lang:
                    lang_display = display
                    break
            self._lang_var.set(lang_display)
            self._theme_var.set(s.get("app_theme", "System"))
            self._anim_var.set(s.get("animations_enabled", "1") == "1")

        # -- Backup section, if it has been built ------------------
        if getattr(self, "_folder_label", None) is not None:
            custom = s.get("backup_folder", "")
            self._folder_label.configure(
                text=custom if custom else "Default (app folder)")
            self._auto_backup_var.set(
                s.get("auto_backup_enabled", "1") == "1")

        # Artboard shows the number the next bill will actually get, beside
        # the field, so a prefix/counter edit can be sanity-checked in place.
        self._refresh_next_bill_hint()

    def _refresh_next_bill_hint(self):
        """Preview of the next bill number, from the two fields as typed."""
        hint = getattr(self, "_next_bill_hint", None)
        if hint is None:
            return
        L = self.app.current_lang
        prefix = (self._entries["bill_prefix"].get().strip() or "BILL")
        seq = self._entries["next_bill_no"].get().strip()
        if seq.isdigit():
            hint.configure(text=f"{t('Next bill:', L)}  {prefix}-{int(seq):05d}")
        else:
            hint.configure(text="")

    def _save(self):
        L = self.app.current_lang
        # Bill numbering lives in the Billing section, but Save sits in the
        # header and Settings opens on Shop — so this reads fields the user
        # need never have looked at. Build them before reading them.
        self._ensure_section("billing")
        self._ensure_section("shop")
        bill_prefix = self._entries["bill_prefix"].get().strip() or "BILL"
        next_no = self._entries["next_bill_no"].get().strip()
        if not next_no.isdigit() or int(next_no) < 1:
            messagebox.showwarning(t("Invalid", L),
                                   t("Next Bill Number must be a positive number.", L))
            return
        # Must be strictly greater than the highest bill number already issued,
        # otherwise the next checkout would generate a duplicate bill_number and
        # every subsequent save would fail on the UNIQUE constraint.
        max_seq = self.db.max_bill_sequence()
        if int(next_no) <= max_seq:
            messagebox.showwarning(
                t("Invalid", L),
                t("Next Bill Number must be greater than the highest used", L)
                + f" ({max_seq}).")
            return

        # Normalise/validate paper width — only 58mm or 80mm are meaningful.
        paper_ent = self._entries.get("paper_width")
        if paper_ent is not None:
            pw = paper_ent.get().strip().lower().replace(" ", "")
            if pw not in ("58mm", "80mm"):
                messagebox.showwarning(t("Invalid", L),
                                       t("Thermal paper width must be 58mm or 80mm.", L))
                return
            paper_ent.delete(0, "end")
            paper_ent.insert(0, pw)

        data = {k: ent.get().strip() for k, ent in self._entries.items()}
        data["bill_prefix"] = bill_prefix
        self.db.save_settings_bulk(data)
        self.db.log_activity(
            self.current_user["user_id"], "SETTINGS_SAVED",
            f"Settings updated by {self.current_user['name']}"
        )
        messagebox.showinfo("Saved", "Settings saved successfully!")

    # ── Backup folder picker ─────────────────────────────────
    def _choose_backup_folder(self):
        folder = filedialog.askdirectory(
            title="Choose Backup Destination (USB, Google Drive, etc.)",
            parent=self.winfo_toplevel()
        )
        if folder:
            self.db.set_setting("backup_folder", folder)
            self._folder_label.configure(text=folder)
            messagebox.showinfo("Folder Set",
                                f"Backups will now be saved to:\n{folder}",
                                parent=self.winfo_toplevel())

    def _reset_backup_folder(self):
        self.db.set_setting("backup_folder", "")
        self._folder_label.configure(text="Default (app folder)")

    # ── Auto-backup toggle ───────────────────────────────────
    def _toggle_auto_backup(self):
        val = "1" if self._auto_backup_var.get() else "0"
        self.db.set_setting("auto_backup_enabled", val)
        if hasattr(self.app, "update_auto_backup_schedule"):
            self.app.update_auto_backup_schedule()

    # ── Animation toggle ─────────────────────────────────────
    def _toggle_animations(self):
        import motion
        motion.set_enabled(self._anim_var.get(), self.db)

    # ── Manual backup ────────────────────────────────────────
    def _do_backup(self):
        try:
            dst = _run_backup(self.db)
            ts_display = datetime.now().strftime("%d %b %Y  %I:%M %p")
            self.db.set_setting("last_backup", ts_display)
            self._last_backup_label.configure(text=ts_display)
            messagebox.showinfo("Backup", f"Backup saved!\n{dst}",
                                parent=self.winfo_toplevel())
        except Exception as e:
            messagebox.showerror("Backup Failed", str(e),
                                 parent=self.winfo_toplevel())

    # ── Restore ──────────────────────────────────────────────
    def _do_restore(self):
        # Warn user first
        confirmed = messagebox.askyesno(
            "Restore Backup",
            "WARNING: This will REPLACE all current data with the backup.\n\n"
            "Your current data will be saved as a safety backup first.\n\n"
            "Continue?",
            icon="warning",
            parent=self.winfo_toplevel()
        )
        if not confirmed:
            return

        src_file = filedialog.askopenfilename(
            title="Select a Backup File to Restore",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")],
            parent=self.winfo_toplevel()
        )
        if not src_file:
            return

        # Validate that the chosen file is actually a readable SQLite database
        # BEFORE we overwrite the live DB — otherwise a wrong pick bricks the app.
        if not _is_valid_sqlite(src_file):
            messagebox.showerror(
                "Invalid Backup",
                "The selected file is not a valid SQLite database.\n"
                "No changes were made.",
                parent=self.winfo_toplevel())
            return

        try:
            # 1. Safety-backup the current DB before overwriting
            _run_backup(self.db, label="pre_restore")

            # 2. Overwrite the live DB with the chosen backup, then clear any stale
            #    WAL/SHM sidecars so the OLD db's uncheckpointed frames are not
            #    replayed into the freshly restored file on next open.
            shutil.copy2(src_file, self.db.db_path)
            for sidecar in (self.db.db_path + "-wal", self.db.db_path + "-shm"):
                try:
                    if os.path.exists(sidecar):
                        os.remove(sidecar)
                except Exception:
                    # A -wal left behind here replays the OLD database's
                    # uncheckpointed frames into the file just restored. This
                    # is the one silent failure in the app that can lose bills.
                    applog.swallow(f"remove sidecar {sidecar!r} after restore",
                                   applog.ERROR)

            # 3. Re-run init_db so new tables / migrations apply
            self.db.init_db()

            ts_display = datetime.now().strftime("%d %b %Y  %I:%M %p")
            self.db.set_setting("last_backup", ts_display)
            self._last_backup_label.configure(text=ts_display)

            messagebox.showinfo(
                "Restore Complete",
                f"Data restored from:\n{src_file}\n\n"
                "Please restart the app for all screens to refresh.",
                parent=self.winfo_toplevel()
            )
        except Exception as e:
            messagebox.showerror("Restore Failed", str(e),
                                 parent=self.winfo_toplevel())

    # ── Language change ──────────────────────────────────────
    def _change_language(self, display_name: str):
        """Save selected language to DB and rebuild the UI."""
        # Map display name → DB value
        db_val = "English"
        for disp, val in zip(LANGUAGES, LANG_DB_VALUES):
            if disp == display_name:
                db_val = val
                break
        self.db.set_setting("app_language", db_val)
        if hasattr(self.app, "apply_language"):
            self.app.apply_language(db_val)

    def _change_theme(self, theme_name: str):
        """Save selected theme to DB and rebuild the UI."""
        self.db.set_setting("app_theme", theme_name)
        if hasattr(self.app, "apply_theme"):
            self.app.apply_theme(theme_name)

    # ── Format / Factory Reset ───────────────────────────────
    def _do_format_data(self):
        """Two-step confirmation before wiping all data."""
        # Step 1: warning dialog
        step1 = messagebox.askyesno(
            "⚠️ Format All Data?",
            "This will PERMANENTLY DELETE:\n"
            "  • All bills and bill items\n"
            "  • All products and categories\n"
            "  • All customers and their balances\n"
            "  • All suppliers and purchases\n"
            "  • All stock adjustments\n"
            "  • All non-admin users (cashiers, stock managers)\n"
            "  • Activity log\n\n"
            "Only admin accounts and settings will be KEPT.\n"
            "Bill number will be reset to 1.\n\n"
            "A safety backup will be created automatically first.\n\n"
            "Are you absolutely sure you want to continue?",
            icon="warning",
            parent=self.winfo_toplevel(),
        )
        if not step1:
            return

        # Step 2: type-to-confirm dialog
        dialog = ctk.CTkInputDialog(
            text='Type  CONFIRM  (all caps) to proceed with the factory reset:',
            title="Confirm Format Data",
        )
        typed = dialog.get_input()
        if not typed or typed.strip().upper() != "CONFIRM":
            messagebox.showinfo(
                "Cancelled",
                "Format cancelled. No data was changed.",
                parent=self.winfo_toplevel(),
            )
            return

        # ── Execute reset ──────────────────────────────────────
        try:
            # 1. Safety backup before wiping
            dst = _run_backup(self.db, label="pre_format")

            # 2. Wipe all data
            self.db.factory_reset(keep_settings=True)

            # 3. Log (fresh log table, so this will be entry #1)
            self.db.log_activity(
                self.current_user["user_id"],
                "FORMAT_DATA",
                f"Factory reset performed by {self.current_user['name']}. "
                f"Pre-format backup: {dst}",
            )

            messagebox.showinfo(
                "Format Complete",
                f"All data has been reset successfully.\n\n"
                f"Safety backup saved to:\n{dst}\n\n"
                "Please restart the app for all screens to refresh fully.",
                parent=self.winfo_toplevel(),
            )

            # Rebuild settings screen to reflect fresh state
            if hasattr(self.app, "rebuild_screen"):
                self.app.rebuild_screen("settings")

        except Exception as exc:
            messagebox.showerror(
                "Format Failed",
                f"An error occurred during the reset:\n{exc}\n\n"
                "No data has been changed.",
                parent=self.winfo_toplevel(),
            )

    # -- Problem reporting ------------------------------------
    def _refresh_problem_status(self):
        # Lives on the Backup panel, which on_show() reaches whether or not
        # the shopkeeper has ever opened that section.
        if getattr(self, "_problem_label", None) is None:
            return
        L = self.app.current_lang
        count, last = applog.problem_summary()
        if count:
            # The translation carries a {n} placeholder; substitute rather than
            # concatenate, so Bengali and Hindi keep their own word order.
            txt = t("{n} problem(s) this session", L).replace("{n}", str(count))
            if last is not None:
                txt += f"   •   {last:%d %b  %I:%M %p}"
            self._problem_label.configure(
                text=txt, text_color=COLORS["accent_danger_fg"])
        else:
            self._problem_label.configure(
                text=t("No problems recorded", L),
                text_color=COLORS["text_muted"])
        self._log_label.configure(text=applog.log_file() or "—")

    def _copy_diagnostics(self):
        L = self.app.current_lang
        try:
            text = applog.diagnostics_text(
                db_path=self.db.db_path,
                extra={"language": L, "theme": self.app.current_theme})
            self.clipboard_clear()
            self.clipboard_append(text)
            # Windows serves the clipboard from the owning process; without a
            # pass through the event loop the text is gone the moment focus
            # moves to WhatsApp.
            self.update()
            messagebox.showinfo(
                t("Copied", L),
                t("Problem details copied. Paste them into WhatsApp or email.", L),
                parent=self.winfo_toplevel())
        except Exception:
            applog.swallow("copy diagnostics")

    def _open_log_folder(self):
        L = self.app.current_lang
        if not applog.open_log_folder():
            messagebox.showwarning(t("Problem Reports", L),
                                   t("Could not open the log folder.", L),
                                   parent=self.winfo_toplevel())

    def on_show(self):
        self._load()
        self._refresh_problem_status()


# ─── Shared backup helper (used by settings screen + main.py scheduler) ──────

def _run_backup(db, label: str = None) -> str:
    """
    Copy the live DB to the configured backup folder (or default backups/).
    Returns the destination path.
    Keeps only the 10 most recent backups per folder.
    """
    custom_folder = db.get_setting("backup_folder", "")
    if custom_folder and os.path.isdir(custom_folder):
        backup_dir = custom_folder
    else:
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(db.db_path)),
                                  "backups")

    os.makedirs(backup_dir, exist_ok=True)
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"billing_backup_{label}_{ts}.db" if label else f"billing_backup_{ts}.db"
    dst = os.path.join(backup_dir, fname)
    shutil.copy2(db.db_path, dst)

    # Prune: keep only the 10 most recent of OUR OWN backups in this folder.
    # Only touch files matching our naming pattern (never unrelated .db files
    # that may live in a user-chosen USB/Drive folder), and rank by real
    # modification time rather than by filename.
    try:
        ours = [
            os.path.join(backup_dir, f)
            for f in os.listdir(backup_dir)
            if f.startswith("billing_backup_") and f.endswith(".db")
        ]
        ours.sort(key=os.path.getmtime, reverse=True)
        for old in ours[10:]:
            try:
                os.remove(old)
            except Exception:
                applog.swallow(f"prune old backup {old!r}", applog.DEBUG)
    except Exception:
        applog.swallow("prune backup folder", applog.DEBUG)

    return dst

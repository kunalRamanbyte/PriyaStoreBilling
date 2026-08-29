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
from datetime import datetime
from config import COLORS, FONTS
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


class SettingsScreen(ctk.CTkFrame):

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
        self._build()

    # ─────────────────────────────────────────────────────────
    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── Header ──
        hdr = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                           corner_radius=16, height=70)
        hdr.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 0))
        hdr.grid_propagate(False)
        ctk.CTkLabel(hdr, text="⚙️   Settings & Configuration",
                     font=FONTS["subheading"],
                     text_color=COLORS["text_dark"]).pack(side="left", padx=24, pady=18)

        # ── Scrollable body ──
        body = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_main"],
                                      corner_radius=0)
        body.grid(row=1, column=0, sticky="nsew", padx=20, pady=12)
        body.grid_columnconfigure(0, weight=1)

        # ── Language & Theme section ─────────────────────────
        self._section(body, 0, "🌐  Language & Theme")
        lang_card = ctk.CTkFrame(body, fg_color=COLORS["bg_card"], corner_radius=16)
        lang_card.grid(row=1, column=0, sticky="ew", pady=4, padx=4)
        lang_card.grid_columnconfigure(1, weight=1)
        
        # Row 0: Language Selection
        ctk.CTkLabel(lang_card, text="Select Language",
                     font=FONTS["label_form"],
                     text_color=COLORS["text_dark"],
                     width=200, anchor="w").grid(row=0, column=0, padx=18, pady=14)
        self._lang_var = tk.StringVar()
        self._lang_menu = ctk.CTkOptionMenu(
            lang_card, variable=self._lang_var,
            values=LANGUAGES,
            font=FONTS["input"], height=42, width=260, corner_radius=10,
            fg_color=COLORS["bg_input"], button_color=COLORS["btn_primary"],
            button_hover_color="#005BBE",
            text_color=COLORS["text_dark"],
            dropdown_fg_color=COLORS["bg_card"], dropdown_text_color=COLORS["text_dark"],
            command=self._change_language,
        )
        self._lang_menu.grid(row=0, column=1, padx=(0, 18), pady=10, sticky="w")

        # Row 1: Theme Mode Selection
        ctk.CTkLabel(lang_card, text="Theme Mode",
                     font=FONTS["label_form"],
                     text_color=COLORS["text_dark"],
                     width=200, anchor="w").grid(row=1, column=0, padx=18, pady=14)
        self._theme_var = tk.StringVar()
        self._theme_menu = ctk.CTkOptionMenu(
            lang_card, variable=self._theme_var,
            values=["System", "Light", "Dark"],
            font=FONTS["input"], height=42, width=260, corner_radius=10,
            fg_color=COLORS["bg_input"], button_color=COLORS["btn_primary"],
            button_hover_color="#005BBE",
            text_color=COLORS["text_dark"],
            dropdown_fg_color=COLORS["bg_card"], dropdown_text_color=COLORS["text_dark"],
            command=self._change_theme,
        )
        self._theme_menu.grid(row=1, column=1, padx=(0, 18), pady=10, sticky="w")

        # Shop Info section
        self._section(body, 2, "🏪  Shop Information")
        row = 3
        for key, label, ph, sec in self.FIELDS:
            if sec != "shop":
                continue
            self._field_row(body, row, key, label, ph)
            row += 1

        # Bill Config section
        self._section(body, row, "🧾  Bill Configuration")
        row += 1
        # Offset rows by 2 because language section took rows 0-1
        for key, label, ph, sec in self.FIELDS:
            if sec != "bill":
                continue
            self._field_row(body, row, key, label, ph)
            row += 1

        # ── Backup section ──────────────────────────────────────
        self._section(body, row, "💾  Backup & Restore")
        row += 1

        # --- Row 1: Last backup info + Backup Now ---
        brow = ctk.CTkFrame(body, fg_color=COLORS["bg_card"], corner_radius=16)
        brow.grid(row=row, column=0, sticky="ew", pady=4, padx=4)
        brow.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(brow, text="Last Backup",
                     font=FONTS["label_form"],
                     text_color=COLORS["text_dark"],
                     width=200, anchor="w").grid(row=0, column=0, padx=18, pady=14)
        self._last_backup_label = ctk.CTkLabel(
            brow, text="—", font=FONTS["body"],
            text_color=COLORS["text_muted"], anchor="w")
        self._last_backup_label.grid(row=0, column=1, padx=12, sticky="w")
        ctk.CTkButton(
            brow, text="🔄  Backup Now",
            font=FONTS["button"], fg_color=COLORS["btn_primary"],
            hover_color="#005BBE", height=40, width=160,
            command=self._do_backup,
        ).grid(row=0, column=2, padx=18, pady=10)
        row += 1

        # --- Row 2: Custom backup folder ---
        frow = ctk.CTkFrame(body, fg_color=COLORS["bg_card"], corner_radius=16)
        frow.grid(row=row, column=0, sticky="ew", pady=4, padx=4)
        frow.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frow, text="Backup Folder",
                     font=FONTS["label_form"],
                     text_color=COLORS["text_dark"],
                     width=200, anchor="w").grid(row=0, column=0, padx=18, pady=14)
        self._folder_label = ctk.CTkLabel(
            frow, text="Default (app folder)", font=FONTS["small"],
            text_color=COLORS["text_muted"], anchor="w", wraplength=340)
        self._folder_label.grid(row=0, column=1, padx=12, sticky="w")

        btn_col = ctk.CTkFrame(frow, fg_color="transparent")
        btn_col.grid(row=0, column=2, padx=18, pady=10)
        ctk.CTkButton(
            btn_col, text="📂  Choose Folder",
            font=FONTS["button"], fg_color=COLORS["btn_warning"],
            hover_color="#CC7700", height=40, width=160,
            command=self._choose_backup_folder,
        ).pack(side="top", pady=(0, 4))
        ctk.CTkButton(
            btn_col, text="🗑  Reset to Default",
            font=FONTS["small"], fg_color=COLORS["btn_secondary"],
            hover_color=COLORS["btn_secondary"], height=32, width=160,
            command=self._reset_backup_folder,
        ).pack(side="top")
        row += 1

        # --- Row 3: Scheduled daily backup toggle ---
        srow = ctk.CTkFrame(body, fg_color=COLORS["bg_card"], corner_radius=16)
        srow.grid(row=row, column=0, sticky="ew", pady=4, padx=4)
        srow.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(srow, text="Daily Auto-Backup",
                     font=FONTS["label_form"],
                     text_color=COLORS["text_dark"],
                     width=200, anchor="w").grid(row=0, column=0, padx=18, pady=14)
        ctk.CTkLabel(srow, text="Automatically backup once every 24 hours while the app is open",
                     font=FONTS["small"], text_color=COLORS["text_muted"],
                     anchor="w").grid(row=0, column=1, padx=12, sticky="w")
        self._auto_backup_var = tk.BooleanVar(value=True)
        ctk.CTkSwitch(
            srow, text="", variable=self._auto_backup_var,
            fg_color=COLORS["btn_primary"], progress_color="#43A047",
            command=self._toggle_auto_backup,
        ).grid(row=0, column=2, padx=18, pady=10)
        row += 1

        # --- Row 4: Restore ---
        rrow = ctk.CTkFrame(body, fg_color=COLORS["bg_card"], corner_radius=16)
        rrow.grid(row=row, column=0, sticky="ew", pady=4, padx=4)
        rrow.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(rrow, text="Restore from Backup",
                     font=FONTS["label_form"],
                     text_color=COLORS["text_dark"],
                     width=200, anchor="w").grid(row=0, column=0, padx=18, pady=14)
        ctk.CTkLabel(rrow, text="Replace current data with a previous backup file (.db)",
                     font=FONTS["small"], text_color=COLORS["text_muted"],
                     anchor="w").grid(row=0, column=1, padx=12, sticky="w")
        ctk.CTkButton(
            rrow, text="♻️  Restore Backup",
            font=FONTS["button"], fg_color=COLORS["btn_danger"],
            hover_color="#CC2200", height=40, width=160,
            command=self._do_restore,
        ).grid(row=0, column=2, padx=18, pady=10)
        row += 1

        # ── Save button ──
        btn_frame = ctk.CTkFrame(body, fg_color="transparent")
        btn_frame.grid(row=row, column=0, sticky="ew", pady=(18, 8))
        ctk.CTkButton(
            btn_frame,
            text="💾   Save Settings",
            font=FONTS["button"],
            fg_color=COLORS["btn_success"],
            hover_color="#28A745",
            height=52, width=240,
            command=self._save,
        ).pack(side="left", padx=4)
        row += 1

        # ── Danger Zone (admin only) ─────────────────────────────
        if self.current_user.get("role") == "admin":
            self._section(body, row, "⚠️  Danger Zone")
            row += 1

            danger_card = ctk.CTkFrame(
                body,
                fg_color="#FFF5F5",
                corner_radius=16,
                border_width=2,
                border_color="#FF4444",
            )
            danger_card.grid(row=row, column=0, sticky="ew", pady=4, padx=4)
            danger_card.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                danger_card,
                text="Factory Reset / Format Data",
                font=FONTS["label_form"],
                text_color="#CC0000",
                width=220,
                anchor="w",
            ).grid(row=0, column=0, padx=18, pady=(14, 2), sticky="w")
            ctk.CTkLabel(
                danger_card,
                text="Permanently delete ALL bills, products, categories, customers, suppliers,\n"
                     "stock data and non-admin users. Only admin accounts and settings are kept.",
                font=FONTS["small"],
                text_color="#AA2200",
                anchor="w",
                justify="left",
            ).grid(row=1, column=0, columnspan=2, padx=18, pady=(0, 14), sticky="w")
            ctk.CTkButton(
                danger_card,
                text="🗑️  Format Data",
                font=FONTS["button"],
                fg_color=COLORS["btn_danger"],
                hover_color="#AA0000",
                height=42,
                width=180,
                command=self._do_format_data,
            ).grid(row=0, column=2, padx=18, pady=12)

        self._load()

    def _section(self, parent, row, title):
        ctk.CTkFrame(parent, fg_color="transparent", height=8).grid(
            row=row, column=0)
        ctk.CTkLabel(parent, text=title,
                     font=FONTS["body_bold"],
                     text_color=COLORS["btn_primary"],
                     anchor="w").grid(row=row, column=0, sticky="w",
                                      padx=6, pady=(14, 2))

    def _field_row(self, parent, row, key, label, placeholder):
        card = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=16)
        card.grid(row=row, column=0, sticky="ew", pady=4, padx=4)
        card.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(card, text=label,
                     font=FONTS["label_form"],
                     text_color=COLORS["text_dark"],
                     width=200, anchor="w").grid(row=0, column=0, padx=18, pady=14)
        ent = ctk.CTkEntry(card, font=FONTS["input"],
                           fg_color=COLORS["bg_input"],
                           border_color=COLORS["border"],
                           text_color=COLORS["text_dark"],
                           placeholder_text=placeholder,
                           height=42)
        ent.grid(row=0, column=1, padx=(0, 18), pady=10, sticky="ew")
        self._entries[key] = ent

    # ─────────────────────────────────────────────────────────
    def _load(self):
        s = self.db.get_all_settings()
        for key, ent in self._entries.items():
            val = s.get(key, "")
            ent.delete(0, "end")
            ent.insert(0, val)
        last = s.get("last_backup", "")
        self._last_backup_label.configure(text=last if last else "No backup yet")

        # Restore language selection
        saved_lang = s.get("app_language", "English")
        # Map DB value to display name
        lang_display = "English"
        for display, db_val in zip(LANGUAGES, LANG_DB_VALUES):
            if db_val == saved_lang:
                lang_display = display
                break
        self._lang_var.set(lang_display)

        # Restore theme selection
        saved_theme = s.get("app_theme", "System")
        self._theme_var.set(saved_theme)

        # Restore custom backup folder label
        custom = s.get("backup_folder", "")
        self._folder_label.configure(
            text=custom if custom else "Default (app folder)")

        # Restore auto-backup toggle
        auto = s.get("auto_backup_enabled", "1")
        self._auto_backup_var.set(auto == "1")

    def _save(self):
        L = self.app.current_lang
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
                    pass

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

    def on_show(self):
        self._load()


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
                pass
    except Exception:
        pass

    return dst

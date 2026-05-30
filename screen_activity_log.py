"""
screen_activity_log.py — Activity Log Viewer
Phase 4 | Admin-only

Shows every logged system event:
  • Login / Logout
  • Bills created / voided
  • GRNs saved
  • Products / categories / suppliers added or edited
  • User changes
  • Settings saved
  • Backup events

Live search, row count, and CSV export.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from config import COLORS, FONTS

ACTION_COLORS = {
    "LOGIN"           : "#E8F5E9",
    "LOGOUT"          : "#EEEEEE",
    "BILL_SAVED"      : COLORS["tbl_select"],
    "BILL_VOIDED"     : "#FFEBEE",
    "GRN_SAVED"       : "#E8EAF6",
    "PRODUCT_"        : "#FFF8E1",
    "USER_"           : "#F3E5F5",
    "SETTINGS_SAVED"  : "#E0F7FA",
    "BACKUP"          : "#E0F7FA",
    "PWD_CHANGED"     : "#FFF3E0",
}


def _row_color(action: str) -> str:
    for prefix, color in ACTION_COLORS.items():
        if action.startswith(prefix):
            return color
    return "white"


class ActivityLogScreen(ctk.CTkFrame):

    COLS = [
        ("Date & Time",  160),
        ("User",         150),
        ("Role",         120),
        ("Action",       160),
        ("Details",      480),
    ]

    PAGE_SIZE = 100

    def __init__(self, parent, db, current_user, app):
        super().__init__(parent, fg_color=COLORS["bg_main"], corner_radius=0)
        self.db           = db
        self.current_user = current_user
        self.app          = app
        self._search_var  = tk.StringVar()
        self._offset      = 0
        self._total       = 0
        self._build()

    # ─────────────────────────────────────────────────────────
    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ── Header ──
        hdr = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                           corner_radius=16, height=70)
        hdr.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 0))
        hdr.grid_propagate(False)
        ctk.CTkLabel(hdr, text="📋   Activity Log",
                     font=FONTS["subheading"],
                     text_color=COLORS["text_dark"]).pack(side="left", padx=24, pady=18)
        ctk.CTkButton(
            hdr, text="📥  Export CSV",
            font=FONTS["button"],
            fg_color=COLORS["btn_purple"],
            hover_color="#9B45C7",
            height=42, width=150,
            command=self._export_csv,
        ).pack(side="right", padx=18)

        # ── Search bar ──
        search_bar = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                                   corner_radius=16, height=60)
        search_bar.grid(row=1, column=0, sticky="ew", padx=20, pady=(10, 0))
        search_bar.grid_propagate(False)
        search_bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(search_bar, text="🔍",
                     font=("Segoe UI", 20)).grid(
                         row=0, column=0, padx=(16, 4), pady=10)
        ctk.CTkEntry(
            search_bar,
            textvariable=self._search_var,
            font=FONTS["input"],
            fg_color=COLORS["bg_input"],
            border_color=COLORS["border"],
            text_color=COLORS["text_dark"],
            placeholder_text="Search by user, action, or details...",
            height=40,
        ).grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=10)

        self._count_label = ctk.CTkLabel(
            search_bar, text="0 records",
            font=FONTS["small_bold"],
            text_color=COLORS["text_muted"])
        self._count_label.grid(row=0, column=2, padx=12)

        self._search_var.trace_add("write", lambda *_: self._search_changed())

        # ── Table ──
        tbl_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                                  corner_radius=16)
        tbl_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(10, 0))
        tbl_frame.grid_rowconfigure(0, weight=1)
        tbl_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            tbl_frame,
            columns=[c for c, w in self.COLS],
            show="headings",
            style="Log.Treeview",
            selectmode="browse",
        )
        # ttk styles applied globally via styles.py
        for col, w in self.COLS:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, minwidth=60,
                             anchor="w" if col == "Details" else "center")

        vsb = ttk.Scrollbar(tbl_frame, orient="vertical",
                            command=self.tree.yview)
        hsb = ttk.Scrollbar(tbl_frame, orient="horizontal",
                            command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set,
                            xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # ── Pagination bar ──
        pg = ctk.CTkFrame(self, fg_color=COLORS["bg_card"],
                           corner_radius=16, height=58)
        pg.grid(row=3, column=0, sticky="ew", padx=20, pady=(8, 16))
        pg.pack_propagate(False)

        self._btn_prev = ctk.CTkButton(
            pg, text="◀  Previous", font=FONTS["button"],
            fg_color=COLORS["btn_secondary"],
            hover_color="#263238",
            height=40, width=140,
            command=self._prev_page, state="disabled")
        self._btn_prev.pack(side="left", padx=12, pady=8)

        self._page_label = ctk.CTkLabel(
            pg, text="Page 1", font=FONTS["body_bold"],
            text_color=COLORS["text_dark"])
        self._page_label.pack(side="left", padx=16)

        self._btn_next = ctk.CTkButton(
            pg, text="Next  ▶", font=FONTS["button"],
            fg_color=COLORS["btn_primary"],
            hover_color="#005BBE",
            height=40, width=140,
            command=self._next_page, state="disabled")
        self._btn_next.pack(side="left", padx=4)

        self._load()

    # ─────────────────────────────────────────────────────────
    def _search_changed(self):
        self._offset = 0
        self._load()

    def _load(self):
        search = self._search_var.get().strip()
        self._total = self.db.get_activity_log_count(search)
        rows = self.db.get_activity_log(
            search=search,
            limit=self.PAGE_SIZE,
            offset=self._offset,
        )

        self.tree.delete(*self.tree.get_children())

        # Register unique color tags
        seen_tags = set()
        for r in rows:
            action = str(r.get("action", ""))
            color  = _row_color(action)
            tag    = f"clr_{color.replace('#','')}"
            if tag not in seen_tags:
                self.tree.tag_configure(tag, background=color)
                seen_tags.add(tag)

            ts = str(r.get("timestamp", ""))[:19].replace("T", "  ")
            self.tree.insert("", "end",
                             values=(
                                 ts,
                                 r.get("user_name", "—"),
                                 r.get("role", "—").title(),
                                 action,
                                 r.get("details", ""),
                             ),
                             tags=(tag,))

        # Update counters
        self._count_label.configure(
            text=f"{self._total} record{'s' if self._total != 1 else ''}")

        page     = self._offset // self.PAGE_SIZE + 1
        total_pg = max(1, (self._total + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        self._page_label.configure(text=f"Page {page} / {total_pg}")
        self._btn_prev.configure(
            state="normal" if self._offset > 0 else "disabled")
        self._btn_next.configure(
            state="normal" if (self._offset + self.PAGE_SIZE) < self._total
            else "disabled")

    def _prev_page(self):
        self._offset = max(0, self._offset - self.PAGE_SIZE)
        self._load()

    def _next_page(self):
        self._offset += self.PAGE_SIZE
        self._load()

    # ─────────────────────────────────────────────────────────
    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV file", "*.csv")],
            initialfile="activity_log",
            title="Export Activity Log",
        )
        if not path:
            return
        try:
            search = self._search_var.get().strip()
            all_rows = self.db.get_activity_log(
                search=search, limit=99999, offset=0)
            headers = ["Date & Time", "User", "Role", "Action", "Details"]
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow(headers)
                for r in all_rows:
                    ts = str(r.get("timestamp", ""))[:19].replace("T", " ")
                    w.writerow([
                        ts,
                        r.get("user_name", ""),
                        r.get("role", "").title(),
                        r.get("action", ""),
                        r.get("details", ""),
                    ])
            messagebox.showinfo("Exported",
                                f"✅  Activity log exported!\n{path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

    def on_show(self):
        self._offset = 0
        self._load()

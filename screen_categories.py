"""
screen_categories.py — Category Manager screen
Add, edit, colour-code product categories.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, colorchooser
from config import COLORS, FONTS, CAT_COLORS
from lang import t


class CategoryScreen(ctk.CTkFrame):
    def __init__(self, parent, db, current_user, app):
        super().__init__(parent, fg_color=COLORS["bg_main"], corner_radius=0)
        self.db           = db
        self.current_user = current_user
        self.app          = app
        self._editing_id  = None
        self._build()

    def _build(self):
        # ── Header ───────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=0, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        L = self.app.current_lang
        ctk.CTkLabel(header, text=t("Category Manager", L),
                     font=FONTS["heading"], text_color=COLORS["text_dark"]
                    ).pack(side="left", padx=25, pady=15)

        # ── Body: list + form side by side ───────────────────
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=12, pady=10)
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=0)
        body.grid_rowconfigure(0, weight=1)

        # ── Left: category cards list ─────────────────────────
        list_frame = ctk.CTkScrollableFrame(body, fg_color=COLORS["bg_card"], corner_radius=16)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.list_frame = list_frame

        ctk.CTkLabel(list_frame, text=t("All Categories_list", L),
                     font=FONTS["subheading"], text_color=COLORS["btn_primary"]
                    ).pack(pady=(14, 6), padx=16, anchor="w")
        ctk.CTkFrame(list_frame, fg_color=COLORS["tbl_select"], height=2
                    ).pack(fill="x", padx=16, pady=(0, 10))

        self.cat_cards_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        self.cat_cards_frame.pack(fill="both", expand=True, padx=10)

        # ── Right: add/edit form ──────────────────────────────
        form_outer = ctk.CTkFrame(body, fg_color=COLORS["bg_card"], corner_radius=14, width=340)
        form_outer.grid(row=0, column=1, sticky="ns")
        form_outer.grid_propagate(False)

        ctk.CTkLabel(form_outer, text=t("Add / Edit Category", L),
                     font=FONTS["subheading"], text_color=COLORS["btn_primary"]
                    ).pack(pady=(20, 8), padx=20, anchor="w")
        ctk.CTkFrame(form_outer, fg_color=COLORS["tbl_select"], height=2
                    ).pack(fill="x", padx=20, pady=(0, 16))

        ctk.CTkLabel(form_outer, text=t("Category Name *", L),
                     font=FONTS["label_form"], text_color=COLORS["text_dark"]
                    ).pack(anchor="w", padx=20)
        self.name_var = tk.StringVar()
        self.name_entry = ctk.CTkEntry(
            form_outer, textvariable=self.name_var,
            placeholder_text="e.g. Atta & Flour",
            font=FONTS["input"], height=46,
            border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"]
        )
        self.name_entry.pack(fill="x", padx=20, pady=(4, 16))

        ctk.CTkLabel(form_outer, text=t("Colour Code", L),
                     font=FONTS["label_form"], text_color=COLORS["text_dark"]
                    ).pack(anchor="w", padx=20)

        # Colour swatches
        swatch_frame = ctk.CTkFrame(form_outer, fg_color="transparent")
        swatch_frame.pack(fill="x", padx=20, pady=(4, 6))
        self.selected_color = tk.StringVar(value=CAT_COLORS[0])

        self.swatch_buttons = []
        for i, c in enumerate(CAT_COLORS):
            btn = ctk.CTkButton(
                swatch_frame, text="", fg_color=c,
                hover_color=c, width=28, height=28,
                corner_radius=6,
                command=lambda col=c: self._select_color(col)
            )
            btn.grid(row=i // 5, column=i % 5, padx=3, pady=3)
            self.swatch_buttons.append(btn)

        # Custom colour picker
        pick_row = ctk.CTkFrame(form_outer, fg_color="transparent")
        pick_row.pack(fill="x", padx=20, pady=(4, 16))
        ctk.CTkLabel(pick_row, text="Custom:", font=FONTS["small"],
                     text_color=COLORS["text_muted"]).pack(side="left")
        ctk.CTkButton(pick_row, text=t("Pick Colour", L),
                      font=FONTS["small_bold"], fg_color="#607D8B",
                      height=32, width=130, corner_radius=10,
                      command=self._pick_custom_color
                     ).pack(side="left", padx=8)
        self.color_preview = ctk.CTkFrame(pick_row, fg_color=CAT_COLORS[0],
                                           corner_radius=6, width=32, height=32)
        self.color_preview.pack(side="left")

        # Error label
        self.err_lbl = ctk.CTkLabel(form_outer, text="", font=FONTS["small"],
                                     text_color=COLORS["btn_danger"])
        self.err_lbl.pack(pady=(0, 6), padx=20, anchor="w")

        # Save button
        ctk.CTkButton(form_outer, text=t("Save Category", L),
                      font=FONTS["button"], fg_color=COLORS["btn_success"],
                      height=50, corner_radius=16,
                      command=self._save_category
                     ).pack(fill="x", padx=20, pady=(0, 8))

        ctk.CTkButton(form_outer, text=t("Reset / New", L),
                      font=FONTS["button"], fg_color=COLORS["btn_secondary"],
                      height=44, corner_radius=16,
                      command=self._reset_form
                     ).pack(fill="x", padx=20, pady=(0, 16))

    def on_show(self):
        self._load_categories()

    def _load_categories(self):
        for w in self.cat_cards_frame.winfo_children():
            w.destroy()

        cats = self.db.get_categories(active_only=False)
        if not cats:
            ctk.CTkLabel(self.cat_cards_frame, text="No categories yet.\nAdd one using the form →",
                         font=FONTS["body"], text_color=COLORS["text_muted"],
                         justify="center").pack(pady=40)
        else:
            for cat in cats:
                self._make_cat_card(cat)

        self.cat_cards_frame.update_idletasks()
        self.list_frame._parent_canvas.yview_moveto(0)

    @staticmethod
    def _safe_color(value):
        """Return a usable colour. Falls back to the default slate when the
        stored colour_code is missing or not a valid hex code (e.g. legacy/bad
        rows where a note got saved in the colour field) — otherwise passing it
        to a widget's fg_color raises TclError and aborts the whole list build."""
        default = COLORS["cat_default"]
        if not value or not isinstance(value, str):
            return default
        v = value.strip()
        if (len(v) in (4, 7) and v.startswith("#")
                and all(ch in "0123456789abcdefABCDEF" for ch in v[1:])):
            return v
        return default

    def _make_cat_card(self, cat):
        color = self._safe_color(cat.get("colour_code"))
        card = ctk.CTkFrame(self.cat_cards_frame, fg_color=COLORS["bg_card"],
                             corner_radius=16, height=60)
        card.pack(fill="x", pady=4)
        card.pack_propagate(False)

        # Colour strip
        ctk.CTkFrame(card, fg_color=color, corner_radius=0,
                     width=8, height=60).pack(side="left")

        # Dot
        ctk.CTkLabel(card, text="⬤", font=("Segoe UI", 22),
                     text_color=color).pack(side="left", padx=(10, 6))

        ctk.CTkLabel(card, text=cat["name"],
                     font=FONTS["body_bold"], text_color=COLORS["text_dark"]
                    ).pack(side="left", pady=14)

        if not cat.get("is_active", 1):
            ctk.CTkLabel(card, text="(Inactive)",
                         font=FONTS["small"], text_color=COLORS["text_muted"]
                        ).pack(side="left", padx=6)

        # Edit button
        ctk.CTkButton(card, text="✏️ Edit",
                      font=FONTS["small_bold"], fg_color=COLORS["btn_primary"],
                      hover_color="#005BBE", width=72, height=34, corner_radius=6,
                      command=lambda c=cat: self._edit_category(c)
                     ).pack(side="right", padx=(0, 8))

        ctk.CTkButton(card, text="🗑️",
                      font=FONTS["small_bold"], fg_color=COLORS["btn_danger"],
                      hover_color="#CC2200", width=42, height=34, corner_radius=6,
                      command=lambda c=cat: self._delete_category(c)
                     ).pack(side="right", padx=(0, 4))

    def _select_color(self, color):
        self.selected_color.set(color)
        self.color_preview.configure(fg_color=color)
        for btn, c in zip(self.swatch_buttons, CAT_COLORS):
            btn.configure(border_width=3 if c == color else 0,
                          border_color="black" if c == color else color)

    def _pick_custom_color(self):
        color = colorchooser.askcolor(
            title="Choose Category Colour",
            color=self.selected_color.get()
        )
        if color and color[1]:
            self._select_color(color[1])

    def _save_category(self):
        name  = self.name_var.get().strip()
        color = self.selected_color.get()

        if not name:
            self.err_lbl.configure(text="⚠  Category name is required.")
            return

        if self._editing_id:
            self.db.update_category(self._editing_id, name, color)
            self._reset_form()
            self._load_categories()
            messagebox.showinfo("Saved", f"Category '{name}' updated.",
                                parent=self.winfo_toplevel())
        else:
            ok = self.db.add_category(name, color)
            if not ok:
                self.err_lbl.configure(text="⚠  Category name already exists.")
                return
            self._reset_form()
            self._load_categories()
            messagebox.showinfo("Added", f"Category '{name}' added.",
                                parent=self.winfo_toplevel())

    def _edit_category(self, cat):
        self._editing_id = cat["category_id"]
        self.name_var.set(cat["name"])
        self._select_color(cat.get("colour_code", CAT_COLORS[0]))
        self.err_lbl.configure(text="")
        self.name_entry.focus()

    def _delete_category(self, cat):
        if messagebox.askyesno(
            "Delete Category",
            f"Delete category  '{cat['name']}'?\n\n"
            f"Products in this category won't be affected,\nbut they'll have no category assigned.",
            parent=self.winfo_toplevel()
        ):
            self.db.delete_category(cat["category_id"])
            self._load_categories()

    def _reset_form(self):
        self._editing_id = None
        self.name_var.set("")
        self._select_color(CAT_COLORS[0])
        self.err_lbl.configure(text="")

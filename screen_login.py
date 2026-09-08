"""
screen_login.py — Login screen

Direction B: a single split card centred on the app canvas. The left panel
is the deep blue brand block; the right panel is the form.

The brand panel carries a shop photograph under a deep-blue wash. That wash
is *baked into the bitmap*, never drawn: `assets/login_panel.png` is the
photo already composited under the artboard's three-stop gradient, so
CustomTkinter only ever renders a flat image. The rest of the screen keeps
the house rule — solid fills, hairline borders, radii, nothing translucent.

    Recipe for assets/login_panel.png, if the source photo is ever swapped:
      crop assets/login_bg.png to (253, 300, 770, 1024)   # below the signage
      resize to 800x1116                                  # 2x of 400x558
      composite under linear-gradient(180deg,
          rgba(11,29,72,.72) 0%, rgba(20,50,116,.82) 55%, rgba(15,38,92,.92))
      quantize to 256 colours (the wash is near-monochrome; 492KB -> 171KB,
      max channel delta 4)

The panel is a raw `tk.Canvas`, not stacked CustomTkinter widgets. A CTk
widget with `fg_color="transparent"` resolves to its master's colour and
paints an *opaque* rectangle, so a label placed over the image punches a
flat blue box through it — verified, not assumed. `Canvas.create_text`
composites for real. It also makes the failure path free: the canvas
background is the flat brand blue, so a missing or unreadable image degrades
to precisely the panel that shipped before.

Default: admin / admin123
"""

import os
import glob
import tkinter as tk
from tkinter import font as tkfont
from datetime import datetime
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk
import applog
from config import (COLORS, FONTS, RADII, METRICS, APP_VERSION, SHOP_NAME,
                    DB_PATH, resource_path)
from lang import t


class LoginScreen(ctk.CTkFrame):
    _SHOW_BTN_W = 72
    # Brand panel in artboard units. 558 rather than 560: the panel sits
    # flush inside the card's 1px hairline, top and bottom.
    _PANEL_W = 400
    _PANEL_H = 558

    def __init__(self, parent, on_success_callback):
        super().__init__(parent, fg_color=COLORS["bg_main"], corner_radius=0)
        self.on_success = on_success_callback
        self._lang = getattr(self.winfo_toplevel(), "current_lang", "English") or "English"
        self._pwd_shown = False
        self._panel_size = (0, 0)
        self._panel_ref = None
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

    # ── Brand panel (canvas) ────────────────────────────────
    @staticmethod
    def _round_rect(cv, x0, y0, x1, y1, r, fill):
        """A filled rounded rectangle on a Canvas — two rectangles plus four
        pieslices. `create_polygon(smooth=True)` only approximates a radius,
        and the white chips sit right next to 26px pill fields, where an
        approximate corner reads as a wobble."""
        cv.create_rectangle(x0 + r, y0, x1 - r, y1, fill=fill, outline=fill)
        cv.create_rectangle(x0, y0 + r, x1, y1 - r, fill=fill, outline=fill)
        for cx, cy, start in ((x0 + r, y0 + r,  90), (x1 - r, y0 + r,   0),
                              (x1 - r, y1 - r, 270), (x0 + r, y1 - r, 180)):
            cv.create_arc(cx - r, cy - r, cx + r, cy + r, start=start,
                          extent=90, fill=fill, outline=fill, style="pieslice")

    def _compose_panel(self, w, h, r):
        """The baked photo, resized to the panel and with its two left corners
        cut back to the card's radius and filled with the card surface — the
        panel sits flush to the card edge, and CustomTkinter cannot clip a
        child to a parent's rounded corner, so the corner is painted into the
        bitmap instead.

        Pure image work, and it raises rather than swallowing: keeping it free
        of Tk is what lets the suite assert the corner really picks up the
        *current theme's* card colour, which a screenshot cannot prove
        headlessly."""
        src = Image.open(resource_path("assets", "login_panel.png"))
        im = src.convert("RGB").resize((w, h), Image.LANCZOS)
        card = Image.new("RGB", (w, h), COLORS["bg_card"])

        # Build the corner mask at 4x and downsample, so the curve is
        # anti-aliased instead of a staircase against the card.
        ss = 4
        mask = Image.new("L", (w * ss, h * ss), 0)
        box = [0, 0, w * ss - 1, h * ss - 1]
        try:
            ImageDraw.Draw(mask).rounded_rectangle(
                box, radius=r * ss, fill=255,
                corners=(True, False, False, True))
        except TypeError:
            # Pillow < 9.4 has no per-corner control; rounding all four is a
            # hair off the artboard but never renders broken.
            ImageDraw.Draw(mask).rounded_rectangle(box, radius=r * ss, fill=255)
        mask = mask.resize((w, h), Image.LANCZOS)

        return Image.composite(im, card, mask)

    def _panel_photo(self, w, h, r):
        """Compose and hand back a Tk image, or None on any failure — the
        caller then leaves the canvas on its flat brand-blue background, which
        is exactly the panel that shipped before the photo."""
        try:
            photo = ImageTk.PhotoImage(self._compose_panel(w, h, r))
            self._panel_ref = photo          # Tk keeps no reference of its own
            return photo
        except Exception:
            applog.swallow("login: brand panel image", applog.WARNING)
            return None

    def _draw_panel(self, event=None):
        """Redraw the brand panel at its real pixel size.

        Everything is laid out in the artboard's logical units and scaled by
        one factor measured off the canvas. A raw tk.Canvas is invisible to
        `ctk.set_widget_scaling()`, so deriving the factor from the widget's
        actual height is what keeps the panel in step with the CTk card
        around it on a high-DPI display."""
        cv = self._canvas
        w, h = cv.winfo_width(), cv.winfo_height()
        if w < 2 or h < 2 or (w, h) == self._panel_size:
            return
        self._panel_size = (w, h)
        cv.delete("all")

        k = h / float(self._PANEL_H)

        def s(v):
            return int(round(v * k))

        def font(spec, size):
            return (spec[0], max(1, s(size))) + tuple(spec[2:])

        photo = self._panel_photo(w, h, s(RADII["hero"]))
        if photo is not None:
            cv.create_image(0, 0, anchor="nw", image=photo)

        L = self._lang
        pad = s(36)
        ink = COLORS["on_accent"]

        # Top: rounded mark + shop name
        m = s(42)
        top = s(40)
        self._round_rect(cv, pad, top, pad + m, top + m, s(15), ink)
        cv.create_text(pad + m // 2, top + m // 2, text=SHOP_NAME[0].upper(),
                       fill=COLORS["accent_action_deep"],
                       font=font(("Segoe UI Semibold", 0, "bold"), 18))
        cv.create_text(pad + m + s(11), top + m // 2, anchor="w",
                       text=SHOP_NAME, fill=ink,
                       font=font(("Segoe UI Semibold", 0, "bold"), 17))

        # Middle: the promise, vertically centred as a pair
        wrap = w - 2 * pad
        head = cv.create_text(
            pad, 0, anchor="nw", width=wrap, justify="left",
            text=t("Ring it up in seconds.", L), fill=ink,
            font=font(("Segoe UI Semibold", 0, "bold"), 32))
        sub = cv.create_text(
            pad, cv.bbox(head)[3] + s(14), anchor="nw", width=wrap,
            justify="left",
            text=t("Bills, stock, udhaar and reports — one window, keyboard first.", L),
            fill=COLORS["on_accent_soft"], font=font(FONTS["body"], 16))
        top_y, bot_y = cv.bbox(head)[1], cv.bbox(sub)[3]
        dy = (h - (bot_y - top_y)) // 2 - top_y
        cv.move(head, 0, dy)
        cv.move(sub, 0, dy)

        # Bottom: status chips
        ch, cr = s(32), s(16)
        cy0 = h - s(40) - ch
        x = pad
        cfont = font(FONTS["caption"], 13)
        measure = tkfont.Font(family=cfont[0], size=cfont[1]).measure
        for text in (f"v{APP_VERSION}", self._backup_chip_text()):
            cw = measure(text) + 2 * s(14)
            self._round_rect(cv, x, cy0, x + cw, cy0 + ch, cr, ink)
            cv.create_text(x + cw // 2, cy0 + ch // 2, text=text,
                           fill=COLORS["accent_action_deep"], font=cfont)
            x += cw + s(10)

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
        # A raw tk.Canvas, so the headline can sit *on* the photo instead of
        # in an opaque box punched through it — see the module docstring. The
        # canvas background is the flat brand blue, which doubles as the
        # panel's fallback when the image will not load.
        brand = ctk.CTkFrame(card, fg_color=COLORS["accent_action_deep"],
                             corner_radius=0, width=self._PANEL_W)
        brand.pack(side="left", fill="y", padx=(1, 0), pady=1)
        brand.pack_propagate(False)

        self._canvas = tk.Canvas(brand, highlightthickness=0, bd=0,
                                 bg=COLORS["accent_action_deep"])
        self._canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self._canvas.bind("<Configure>", self._draw_panel)

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
        user_row = ctk.CTkFrame(inner, fg_color="transparent")
        user_row.pack(fill="x", pady=(0, 16))
        self.username_entry = self._field(user_row)
        self.username_entry.pack(side="left", fill="x", expand=True)
        # Reserve the Show button's width so both fields end on the same edge.
        # Matches the Show button's real footprint (its width plus the 6px
        # gap), so both fields end on the same edge.
        ctk.CTkFrame(user_row, fg_color="transparent",
                     width=self._SHOW_BTN_W + 6, height=1).pack(side="left")

        # Password + show/hide
        ctk.CTkLabel(inner, text=t("Password", L), font=FONTS["small"],
                     text_color=COLORS["text_secondary"], anchor="w"
                     ).pack(fill="x", pady=(0, 7))

        pwd_row = ctk.CTkFrame(inner, fg_color="transparent")
        pwd_row.pack(fill="x")
        self.password_entry = self._field(pwd_row, show="●")
        self.password_entry.pack(side="left", fill="x", expand=True)

        self.show_btn = ctk.CTkButton(
            pwd_row, text=t("Show", L), width=self._SHOW_BTN_W, height=52,
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

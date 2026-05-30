"""
screen_login.py — Login screen
Large, colorful, simple — designed for 60+ age users.
Default: admin / admin123
"""

import os
from PIL import Image
import customtkinter as ctk
import tkinter as tk
from config import COLORS, FONTS, APP_TITLE, SHOP_NAME, resource_path


class LoginScreen(ctk.CTkFrame):
    def __init__(self, parent, on_success_callback):
        super().__init__(parent, fg_color="#1A237E", corner_radius=0)
        self.on_success = on_success_callback
        self._build()

    def _build(self):
        # ── Background image ───────────────────────────────
        # Track sizes to prevent unnecessary resize loops
        self._current_width = 1366
        self._current_height = 768
        
        try:
            bg_path = resource_path("assets", "login_bg.png")
            if os.path.exists(bg_path):
                pil_img = Image.open(bg_path)
                self.bg_image = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(1366, 768))
                self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                self.bind("<Configure>", self._on_resize)
            else:
                self.configure(fg_color="#1A237E")
        except Exception as e:
            print("Error loading background image:", e)
            self.configure(fg_color="#1A237E")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Centre card (glassmorphic) ────────────────────────
        card = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=24,
                             width=480, height=580,
                             border_width=2, border_color=COLORS["glass_border"])
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        # Gradient-inspired top banner
        banner = ctk.CTkFrame(card, fg_color="#1E3A5F", corner_radius=0,
                               height=130)
        banner.pack(fill="x")
        banner.pack_propagate(False)

        ctk.CTkLabel(banner, text="🛒", font=("Segoe UI", 52),
                     text_color="white").pack(pady=(18, 0))
        ctk.CTkLabel(banner, text=SHOP_NAME,
                     font=("Segoe UI", 18, "bold"),
                     text_color="#93C5FD").pack()

        # ── Form ─────────────────────────────────────────────
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=40, pady=20)

        ctk.CTkLabel(form, text="Welcome Back! 👋",
                     font=("Segoe UI", 22, "bold"),
                     text_color=COLORS["text_dark"]).pack(pady=(10, 4))
        ctk.CTkLabel(form, text="Please sign in to continue",
                     font=("Segoe UI", 15),
                     text_color=COLORS["text_muted"]).pack(pady=(0, 20))

        # Username
        ctk.CTkLabel(form, text="Username",
                     font=FONTS["label_form"],
                     text_color=COLORS["text_dark"],
                     anchor="w").pack(fill="x")
        self.username_entry = ctk.CTkEntry(
            form,
            placeholder_text="Enter your username",
            font=FONTS["input"],
            height=50,
            border_width=2,
            border_color=COLORS["glass_border"],
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_dark"],
            corner_radius=14,
        )
        self.username_entry.pack(fill="x", pady=(4, 14))

        # Password
        ctk.CTkLabel(form, text="Password",
                     font=FONTS["label_form"],
                     text_color=COLORS["text_dark"],
                     anchor="w").pack(fill="x")
        self.password_entry = ctk.CTkEntry(
            form,
            placeholder_text="Enter your password",
            show="●",
            font=FONTS["input"],
            height=50,
            border_width=2,
            border_color=COLORS["glass_border"],
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_dark"],
            corner_radius=14,
        )
        self.password_entry.pack(fill="x", pady=(4, 5))

        # Error label
        self.error_label = ctk.CTkLabel(
            form, text="", font=("Segoe UI", 14),
            text_color=COLORS["btn_danger"]
        )
        self.error_label.pack(pady=(0, 8))

        # Login button (gradient-inspired)
        self.login_btn = ctk.CTkButton(
            form,
            text="🔓   Sign In",
            font=("Segoe UI", 18, "bold"),
            fg_color=COLORS["btn_primary"],
            hover_color=COLORS["btn_primary_h"],
            text_color="white",
            height=55,
            corner_radius=18,
            border_width=2,
            border_color=COLORS["glass_glow"],
            command=self._do_login,
        )
        self.login_btn.pack(fill="x", pady=(5, 10))

        # Hint
        ctk.CTkLabel(form, text="Default: admin / admin123",
                     font=("Segoe UI", 13),
                     text_color="#94A3B8").pack()

        # Keyboard bindings
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self._do_login())
        self.after(100, self.username_entry.focus)

    def _on_resize(self, event):
        # Update background image size dynamically on resize (bulletproof check)
        w = self.winfo_width()
        h = self.winfo_height()
        if w > 10 and h > 10 and (w != self._current_width or h != self._current_height):
            self._current_width = w
            self._current_height = h
            if hasattr(self, 'bg_image') and hasattr(self, 'bg_label'):
                self.bg_image.configure(size=(w, h))
                self.bg_label.configure(image=self.bg_image)

    def _do_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.error_label.configure(text="⚠  Please enter username and password.")
            return

        # Import db from parent
        app = self.winfo_toplevel()
        user = app.db.authenticate(username, password)

        if user:
            self.error_label.configure(text="")
            self.on_success(user)
        else:
            self.error_label.configure(text="❌  Wrong username or password. Try again.")
            self.password_entry.delete(0, "end")
            self.password_entry.focus()

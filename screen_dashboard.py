"""
screen_dashboard.py — Dashboard/Home screen

Direction B: a 76px title header with the one blue CTA, a row of five KPI
cards where each figure carries the hue its meaning owns, a coral attention
banner when stock needs looking at, and the recent-bills card with a
Today/Week/All segmented control.
"""

import customtkinter as ctk
from tkinter import ttk
from datetime import datetime, timedelta
from config import COLORS, FONTS, RADII, METRICS, GUTTERS
from responsive import ResponsiveMixin
from lang import t
from ui_utils import EmptyState


# Each KPI owns one hue: blue action, violet counts, coral stock risk,
# amber expiry, teal money-in. The tint is the bubble, the vivid colour is
# the icon, and the sub-label takes the dark ink of the same family.
KPI_HUES = {
    "action": ("accent_action_tint", "accent_action",    "accent_action_fg"),
    "counts": ("accent_counts_tint", "accent_counts",    "accent_counts_fg"),
    "stock" : ("accent_stock_tint",  "accent_stock",     "accent_stock_fg"),
    "expiry": ("accent_expiry_tint", "accent_expiry",    "accent_expiry_fg"),
    "money" : ("accent_money_tint",  "accent_money",     "accent_money_fg"),
}

PERIODS = ("Today", "Week", "All")


class DashboardScreen(ResponsiveMixin, ctk.CTkFrame):
    def __init__(self, parent, db, current_user, app):
        super().__init__(parent, fg_color=COLORS["bg_main"], corner_radius=0)
        self.db = db
        self.current_user = current_user
        self.app = app
        self._period = "Today"
        self._period_chips = {}
        self._clock_job = None
        self._build()
        self.bind_responsive()

    # ── Small Direction B primitives ────────────────────────
    def _pill_button(self, parent, text, kind="primary", command=None,
                     height=None):
        """A 44px pill. `primary` is the solid blue CTA; every other kind is
        a tinted button with dark ink, which is how Direction B keeps
        secondary actions quiet and still at 4.5:1."""
        tints = {
            "primary": (COLORS["accent_action"], COLORS["btn_primary_h"], COLORS["on_accent"]),
            "action" : (COLORS["accent_action_tint"], COLORS["glass_glow"], COLORS["accent_action_fg"]),
            "counts" : (COLORS["accent_counts_tint"], COLORS["accent_counts_tint"], COLORS["accent_counts_fg"]),
            "money"  : (COLORS["accent_money_tint"], COLORS["accent_money_tint"], COLORS["accent_money_fg"]),
            "expiry" : (COLORS["accent_expiry_tint"], COLORS["accent_expiry_tint"], COLORS["accent_expiry_fg"]),
            "stock"  : (COLORS["accent_stock_tint"], COLORS["accent_stock_tint"], COLORS["accent_stock_fg"]),
            "plain"  : (COLORS["bg_white"], COLORS["bg_main"], COLORS["text_dark"]),
        }
        fg, hov, ink = tints.get(kind, tints["plain"])
        h = height or METRICS["control"]
        return ctk.CTkButton(
            parent, text=text, font=FONTS["button"],
            fg_color=fg, hover_color=hov, text_color=ink,
            height=h, corner_radius=h // 2, border_width=0,
            command=command,
        )

    def _card(self, parent, **kw):
        """White surface, 24px corners, one hairline border. No shadow."""
        return ctk.CTkFrame(parent, fg_color=COLORS["bg_card"],
                            corner_radius=RADII["card"],
                            border_width=1, border_color=COLORS["hairline"], **kw)

    # ── Build ───────────────────────────────────────────────
    def _build(self):
        L = self.app.current_lang

        # ── Header band ──────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent",
                              height=METRICS["header"])
        self._header = header
        header.pack(fill="x", padx=28, pady=(0, 4))
        header.pack_propagate(False)

        titles = ctk.CTkFrame(header, fg_color="transparent")
        titles.pack(side="left", fill="y")
        self.greet_label = ctk.CTkLabel(
            titles, text="", font=("Segoe UI Semibold", 26, "bold"),
            text_color=COLORS["text_dark"], anchor="w")
        self.greet_label.pack(anchor="w", pady=(16, 0))
        self.dt_label = ctk.CTkLabel(
            titles, text="", font=FONTS["small"],
            text_color=COLORS["text_muted"], anchor="w")
        self.dt_label.pack(anchor="w")

        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.pack(side="right", fill="y")
        if self.app.current_role in ("admin", "cashier"):
            self._pill_button(
                actions, "＋  " + t("New Bill", L), kind="primary",
                command=lambda: self.app.navigate_to("billing"),
            ).pack(side="left", pady=16)

        self._update_clock()

        # ── Scrollable body ──────────────────────────────────
        body = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_main"],
                                      corner_radius=0)
        self._body = body
        body.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        # ── KPI cards ────────────────────────────────────────
        kpi_row = ctk.CTkFrame(body, fg_color="transparent")
        self._kpi_row = kpi_row
        kpi_row.pack(fill="x", pady=(4, 16))

        self.kpi_sales  = self._kpi_card(kpi_row, "💰", t("Today's Sales", L),      "action")
        self.kpi_bills  = self._kpi_card(kpi_row, "🧾", t("Bills Today", L),        "counts")
        self.kpi_low    = self._kpi_card(kpi_row, "⚠️",  t("Low Stock Items", L),    "stock")
        self.kpi_expiry = self._kpi_card(kpi_row, "📅", t("Expiring (30 days)", L), "expiry")
        self.kpi_disc   = self._kpi_card(kpi_row, "🏷️", t("Discount Given", L),     "money")

        self._kpi_cards = (self.kpi_sales, self.kpi_bills, self.kpi_low,
                           self.kpi_expiry, self.kpi_disc)
        self._layout_kpis("standard")

        # ── Attention banner (coral) ─────────────────────────
        # Direction B leads with one sentence, not a table.
        self.alert_frame = ctk.CTkFrame(body, fg_color=COLORS["accent_stock_tint"],
                                        corner_radius=22)
        alert_inner = ctk.CTkFrame(self.alert_frame, fg_color="transparent")
        alert_inner.pack(fill="x", padx=20, pady=16)

        bubble = ctk.CTkFrame(alert_inner, fg_color=COLORS["accent_stock"],
                              corner_radius=16, width=44, height=44)
        bubble.pack(side="left", padx=(0, 16))
        bubble.pack_propagate(False)
        ctk.CTkLabel(bubble, text="!", font=("Segoe UI Semibold", 22, "bold"),
                     text_color=COLORS["on_accent"]
                     ).place(relx=0.5, rely=0.5, anchor="center")

        alert_text = ctk.CTkFrame(alert_inner, fg_color="transparent")
        alert_text.pack(side="left", fill="x", expand=True)
        self.alert_title = ctk.CTkLabel(
            alert_text, text="", font=("Segoe UI Semibold", 17, "bold"),
            text_color=COLORS["text_dark"], anchor="w")
        self.alert_title.pack(anchor="w")
        self.alert_detail = ctk.CTkLabel(
            alert_text, text="", font=FONTS["label_form"],
            text_color=COLORS["accent_stock_fg"], anchor="w")
        self.alert_detail.pack(anchor="w")

        if self.app.current_role in ("admin", "stock_manager"):
            self._pill_button(
                alert_inner, t("Review stock", L), kind="plain", height=40,
                command=lambda: self.app.navigate_to("inventory"),
            ).pack(side="right")

        # ── Quick actions ────────────────────────────────────
        # Not in the artboard, which puts navigation in the sidebar — kept
        # because they are real shortcuts, but restyled from 84px vivid
        # blocks down to quiet tinted pills so they stop competing with the
        # KPI row and the one blue CTA in the header.
        role = self.app.current_role
        role_access = {
            "billing":      ["admin", "cashier"],
            "products":     ["admin", "stock_manager"],
            "bill_history": ["admin", "cashier", "stock_manager"],
            "categories":   ["admin", "stock_manager"],
        }
        actions_spec = [
            (t("New Bill_qa", L),     "action", "billing"),
            (t("Add Product_qa", L),  "money",  "products"),
            (t("Bill History_qa", L), "counts", "bill_history"),
            (t("Categories_qa", L),   "expiry", "categories"),
        ]
        actions_spec = [a for a in actions_spec if role in role_access.get(a[2], [])]
        if actions_spec:
            qa_row = ctk.CTkFrame(body, fg_color="transparent")
            qa_row.pack(fill="x", pady=(0, 16))
            for i, (text, kind, screen) in enumerate(actions_spec):
                self._pill_button(
                    qa_row, text, kind=kind,
                    command=lambda s=screen: self.app.navigate_to(s),
                ).pack(side="left", fill="x", expand=True,
                       padx=(0 if i == 0 else 8, 0))

        # ── Expiry detail table ──────────────────────────────
        # The banner above says how many and names the most urgent one, so
        # this list only earns its place when there is more than one.
        self.expiry_frame = self._card(body)
        exp_hdr = ctk.CTkFrame(self.expiry_frame, fg_color="transparent")
        exp_hdr.pack(fill="x", padx=18, pady=(14, 8))
        ctk.CTkLabel(exp_hdr, text=t("Products Expiring Within 30 Days", L),
                     font=FONTS["subheading"], text_color=COLORS["text_dark"]
                     ).pack(side="left")

        exp_cols = ("name", "category", "stock", "expiry_date", "days_left")
        self.exp_tree = ttk.Treeview(
            self.expiry_frame, columns=exp_cols, show="headings",
            height=5, style="Exp.Treeview", selectmode="none"
        )
        for col, head, w in zip(
            exp_cols,
            (t("Product Name", L), t("Category", L), t("Stock", L),
             t("Expiry Date", L), t("Days Left", L)),
            (240, 130, 70, 110, 90)
        ):
            self.exp_tree.heading(col, text=head)
            self.exp_tree.column(col, width=w,
                                 anchor="w" if col in ("name", "category") else "center")
        self.exp_tree.tag_configure("expired", background=COLORS["row_expired"])
        self.exp_tree.tag_configure("expiring", background=COLORS["row_expiring"])
        self.exp_tree.pack(fill="x", padx=10, pady=(0, 10))

        # ── Recent bills card ────────────────────────────────
        self.bills_card = self._card(body)
        self.bills_card.pack(fill="both", expand=True)

        bills_hdr = ctk.CTkFrame(self.bills_card, fg_color="transparent")
        bills_hdr.pack(fill="x", padx=18, pady=(14, 8))
        ctk.CTkLabel(bills_hdr, text=t("Recent Bills", L),
                     font=FONTS["subheading"], text_color=COLORS["text_dark"]
                     ).pack(side="left")

        # Segmented control — a tinted track holding the chips
        seg = ctk.CTkFrame(bills_hdr, fg_color=COLORS["bg_main"],
                           corner_radius=20)
        seg.pack(side="right")
        for period in PERIODS:
            chip = ctk.CTkButton(
                seg, text=t(period, L), font=FONTS["small"],
                fg_color="transparent", hover_color=COLORS["glass_glow"],
                text_color=COLORS["text_muted"],
                height=METRICS["control_sm"], width=76,
                corner_radius=RADII["pill_sm"], border_width=0,
                command=lambda p=period: self._set_period(p),
            )
            chip.pack(side="left", padx=3, pady=3)
            self._period_chips[period] = chip

        cols = ("bill_number", "date_time", "customer", "amount", "mode", "status")
        self.recent_tree = ttk.Treeview(
            self.bills_card, columns=cols, show="headings",
            height=9, style="Dash.Treeview", selectmode="browse"
        )
        heads = (t("Bill No.", L), t("Date & Time", L), t("Customer", L),
                 t("Amount (₹)", L), t("Mode", L), t("Status", L))
        widths = (110, 160, 180, 110, 90, 80)
        for col, head, w in zip(cols, heads, widths):
            self.recent_tree.heading(col, text=head)
            self.recent_tree.column(col, width=w,
                                    anchor="e" if col == "amount" else "w")

        scroll = ttk.Scrollbar(self.bills_card, orient="vertical",
                               command=self.recent_tree.yview)
        self.recent_tree.configure(yscrollcommand=scroll.set)
        self.recent_tree.pack(side="left", fill="both", expand=True,
                              padx=(10, 0), pady=(0, 10))
        scroll.pack(side="right", fill="y", padx=(0, 8), pady=(0, 10))

        self._empty = EmptyState(self.bills_card, t("No bills yet", L),
                                 t("Bills you save will appear here.", L))
        self._paint_period_chips()

    def _layout_kpis(self, bp):
        """Five cards across needs room. Below `standard` they wrap to a 3+2
        grid rather than shrinking until "Expiring (30 days)" clips."""
        for c in self._kpi_cards:
            c.pack_forget()
            c.grid_forget()
        for i in range(3):
            self._kpi_row.grid_columnconfigure(i, weight=0, uniform="")
        if bp == "compact":
            for i in range(3):
                self._kpi_row.grid_columnconfigure(i, weight=1, uniform="kpi")
            for i, c in enumerate(self._kpi_cards):
                c.grid(row=i // 3, column=i % 3, sticky="nsew",
                       padx=(0 if i % 3 == 0 else 8, 0),
                       pady=(0 if i < 3 else 8, 0))
        else:
            for i, c in enumerate(self._kpi_cards):
                c.pack(side="left", fill="both", expand=True,
                       padx=(0 if i == 0 else 7, 0))

    def on_breakpoint(self, bp, logical_w):
        g = GUTTERS[bp]
        self._header.pack_configure(padx=g)
        self._body.pack_configure(padx=g)
        self._layout_kpis(bp)

    # ── KPI card ────────────────────────────────────────────
    def _kpi_card(self, parent, icon, title, hue):
        tint_key, icon_key, sub_key = KPI_HUES[hue]
        # width=1 so five cards divide the row evenly instead of each
        # demanding CTkFrame's default 200px and overflowing 1366.
        card = self._card(parent, height=136, width=1)
        card.pack_propagate(False)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=18, pady=16)

        bubble = ctk.CTkFrame(inner, fg_color=COLORS[tint_key],
                              corner_radius=RADII["bubble"],
                              width=METRICS["bubble"], height=METRICS["bubble"])
        bubble.pack(anchor="w")
        bubble.pack_propagate(False)
        ctk.CTkLabel(bubble, text=icon, font=("Segoe UI", 19),
                     text_color=COLORS[icon_key]
                     ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(inner, text=title, font=FONTS["small"],
                     text_color=COLORS["text_muted"], anchor="w"
                     ).pack(anchor="w", pady=(10, 0))

        val_lbl = ctk.CTkLabel(inner, text="—", font=FONTS["num_md"],
                               text_color=COLORS["text_dark"], anchor="w")
        val_lbl.pack(anchor="w")

        sub_lbl = ctk.CTkLabel(inner, text="", font=FONTS["caption"],
                               text_color=COLORS[sub_key], anchor="w")
        sub_lbl.pack(anchor="w")

        card._val_lbl = val_lbl
        card._sub_lbl = sub_lbl
        return card

    # ── Period segmented control ────────────────────────────
    def _set_period(self, period):
        self._period = period
        self._paint_period_chips()
        self._load_bills()

    def _paint_period_chips(self):
        for period, chip in self._period_chips.items():
            on = period == self._period
            chip.configure(
                fg_color=COLORS["accent_action"] if on else "transparent",
                text_color=COLORS["on_accent"] if on else COLORS["text_muted"],
                hover_color=(COLORS["accent_action"] if on
                             else COLORS["glass_glow"]),
                font=FONTS["small_bold"] if on else FONTS["small"],
            )

    def _period_range(self):
        """(date_from, date_to) for the selected chip; None means unbounded."""
        today = datetime.now().date()
        if self._period == "Today":
            return today.isoformat(), today.isoformat()
        if self._period == "Week":
            return (today - timedelta(days=6)).isoformat(), today.isoformat()
        return None, None

    # ── Data refresh ────────────────────────────────────────
    def on_show(self):
        # Screens are cached, so on_hide() cancelled the clock chain when we
        # left. Restart it here rather than leaving a frozen timestamp.
        if self._clock_job is None:
            self._update_clock()
        self._load_data()

    def _load_data(self):
        L = self.app.current_lang
        stats    = self.db.get_today_stats()
        low      = self.db.get_low_stock_count()
        expiring = self.db.get_expiring_products(30)
        exp_cnt  = len(expiring)
        bills    = stats["bill_count"]

        self.kpi_sales._val_lbl.configure(text=f"₹ {stats['total_sales']:,.2f}")
        self.kpi_sales._sub_lbl.configure(
            text=f"{bills} {t('Bills Today', L).lower()}" if bills else "")

        self.kpi_bills._val_lbl.configure(text=str(bills))
        avg = (stats["total_sales"] / bills) if bills else 0
        self.kpi_bills._sub_lbl.configure(text=f"avg ₹ {avg:,.0f}" if bills else "")

        self.kpi_low._val_lbl.configure(text=str(low))
        self.kpi_low._sub_lbl.configure(text=t("reorder now", L) if low else "")

        self.kpi_expiry._val_lbl.configure(text=str(exp_cnt))
        expired_now = sum(1 for i in expiring if i.get("days_left", 0) < 0)
        self.kpi_expiry._sub_lbl.configure(
            text=f"{expired_now} {t('expired', L)}" if expired_now else "")

        self.kpi_disc._val_lbl.configure(text=f"₹ {stats['total_discount']:,.2f}")
        self.kpi_disc._sub_lbl.configure(text=t("this shift", L))

        self._load_alert(expiring)
        self._load_bills()

    def _load_alert(self, expiring):
        """Coral banner headlines the count and names the most urgent item;
        the table below only appears when there is more than one."""
        L = self.app.current_lang
        exp_cnt = len(expiring)

        if exp_cnt == 0:
            self.alert_frame.pack_forget()
            self.expiry_frame.pack_forget()
            return

        noun = t("item", L) if exp_cnt == 1 else t("items", L)
        verb = t("needs attention today", L) if exp_cnt == 1 else t("need attention today", L)
        self.alert_title.configure(text=f"{exp_cnt} {noun} {verb}")

        worst = min(expiring, key=lambda i: i.get("days_left", 0))
        dl = worst.get("days_left", 0)
        when = (t("expired", L) if dl < 0 else f"{dl} days") + \
               (f" {worst.get('expiry_date', '')}" if worst.get("expiry_date") else "")
        self.alert_detail.configure(
            text=f"{worst['name']} · {worst.get('category_name', '')} · "
                 f"{worst.get('current_stock', 0):.0f} · {when}")
        self.alert_frame.pack(fill="x", pady=(0, 16), before=self.bills_card)

        self.exp_tree.delete(*self.exp_tree.get_children())
        for item in expiring:
            dl = item.get("days_left", 0)
            self.exp_tree.insert("", "end", values=(
                item["name"],
                item.get("category_name", ""),
                f"{item.get('current_stock', 0):.1f}",
                item.get("expiry_date", ""),
                t("EXPIRED", L) if dl < 0 else f"{dl} days",
            ), tags=("expired" if dl < 0 else "expiring",))

        if exp_cnt > 1:
            self.expiry_frame.pack(fill="x", pady=(0, 16), before=self.bills_card)
        else:
            self.expiry_frame.pack_forget()

    def _load_bills(self):
        L = self.app.current_lang
        date_from, date_to = self._period_range()
        rows = self.db.get_bills(date_from=date_from, date_to=date_to, limit=60)

        self.recent_tree.delete(*self.recent_tree.get_children())
        for i, b in enumerate(rows):
            dt = b["bill_date"][:16] if b["bill_date"] else ""
            status = b["status"]
            tag = {"Void": "void", "Draft": "draft"}.get(status, f"row{i % 6}")
            self.recent_tree.insert("", "end", values=(
                b["bill_number"], dt,
                b.get("customer_name") or t("Walk-in", L),
                f"₹ {b['grand_total']:,.2f}",
                b["payment_mode"],
                status,
            ), tags=(tag,))

        self._empty.sync(len(rows))
        for i, color in enumerate(COLORS["ROW_COLORS"]):
            self.recent_tree.tag_configure(f"row{i}", background=color)
        self.recent_tree.tag_configure("void", background=COLORS["row_void"],
                                       foreground=COLORS["fg_void"])
        self.recent_tree.tag_configure("draft", background=COLORS["row_draft"])

    def _update_clock(self):
        L = self.app.current_lang
        now = datetime.now()
        hour = now.hour
        greet = ("Good morning" if hour < 12
                 else "Good afternoon" if hour < 17
                 else "Good evening")
        name = self.current_user.get("name", "")
        self.greet_label.configure(text=f"{t(greet, L)}, {name}")
        self.dt_label.configure(text=now.strftime("%A, %d %B %Y · %I:%M %p"))
        self._clock_job = self.after(30000, self._update_clock)

    def on_hide(self):
        """Stop the clock while the screen is parked — screens are cached
        and never destroyed, so the after() chain would otherwise keep
        firing for the life of the app."""
        if self._clock_job is not None:
            try:
                self.after_cancel(self._clock_job)
            except Exception:
                pass
            self._clock_job = None

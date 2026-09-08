"""
ui_utils.py — shared UI helpers.

The app drives responsiveness through CustomTkinter *widget* scaling
(set once in main.py via ctk.set_widget_scaling), while leaving *window*
scaling at 1.0 so the main window geometry stays in raw pixels.

That split is fine for the main window, but it breaks fixed-size popups:
a CTkToplevel created with geometry("500x640") keeps a raw 500x640 window
(window scaling = 1.0) while all of its child widgets are enlarged by the
widget-scaling factor (1.31x at 1080p, 1.5x at 4K) — so the content
overflows or is clipped. place_popup() fixes this by sizing the window in
the SAME scale as its contents, clamping it to the screen, and centring it
over the parent window.
"""

import calendar

import customtkinter as ctk

import applog
import motion

try:
    from customtkinter.windows.widgets.scaling.scaling_tracker import ScalingTracker
except Exception:  # pragma: no cover - defensive fallback
    ScalingTracker = None


def place_popup(dlg, logical_w: int, logical_h: int, parent=None):
    """Size `dlg` to logical_w x logical_h *design* pixels (the size you would
    pick at 1.0 scale), corrected for the active widget-scaling factor, clamped
    to the usable screen, and centred over its parent window.

    Call right after creating the CTkToplevel (before/after grab_set is fine).
    """
    # Hide the window before any geometry work: a Toplevel paints at its
    # default position first, so without this the dialog visibly flashes at
    # the wrong spot and then jumps.
    try:
        dlg.attributes("-alpha", 0.0)
    except Exception:
        pass

    widget_scale, window_scale = 1.0, 1.0
    if ScalingTracker is not None:
        try:
            widget_scale = ScalingTracker.get_widget_scaling(dlg) or 1.0
            window_scale = ScalingTracker.get_window_scaling(dlg) or 1.0
        except Exception:
            pass

    dlg.update_idletasks()
    sw = dlg.winfo_screenwidth()
    sh = dlg.winfo_screenheight()

    # Physical size = design size scaled to match the (widget-scaled) content,
    # never larger than the usable screen (leave room for taskbar / title bar).
    phys_w = min(int(logical_w * widget_scale), sw - 40)
    phys_h = min(int(logical_h * widget_scale), sh - 80)

    # Centre over the parent window when it is realised, else over the screen.
    par = parent or dlg.master
    px = py = pw = ph = 0
    try:
        pw, ph = par.winfo_width(), par.winfo_height()
        px, py = par.winfo_rootx(), par.winfo_rooty()
    except Exception:
        pw = ph = 0
    if pw > 1 and ph > 1:
        x = px + (pw - phys_w) // 2
        y = py + (ph - phys_h) // 2
    else:
        x = (sw - phys_w) // 2
        y = (sh - phys_h) // 2

    # Keep the whole window on-screen.
    x = max(0, min(x, sw - phys_w))
    y = max(0, min(y, sh - phys_h))

    # CTkToplevel.geometry() multiplies the string by window scaling, so divide
    # it back out to land on the physical pixels we computed above.
    gw = round(phys_w / window_scale)
    gh = round(phys_h / window_scale)
    gx = round(x / window_scale)
    gy = round(y / window_scale)
    dlg.geometry(f"{gw}x{gh}+{gx}+{gy}")
    from config import MOTION
    motion.fade_in(dlg, MOTION["fade_ms"])


# ─────────────────────────────────────────────────────────────────────────────
# Calendar date picker
#
# Hand-built on the stdlib `calendar` module rather than tkcalendar, which is
# GPLv3 -- linking it into a closed-source binary would have forced the whole
# app to be published under the GPL. It also dragged in babel purely to name
# weekdays; tkcalendar is 108 KB, babel is 31 MB, and dropping the pair took
# the built app from 237 MB to 202 MB.
#
# The replacement is also the first version of this dialog that speaks the
# shop's language: tkcalendar was constructed without a `locale=` argument, so
# it always drew English month names regardless of the app's setting, and the
# three buttons underneath it were hardcoded English too.
# ─────────────────────────────────────────────────────────────────────────────

# Sunday-first, the ordering a shop counter in India expects. `calendar`'s own
# default is Monday-first, so this is set explicitly rather than inherited.
_CAL = calendar.Calendar(firstweekday=6)

_MONTHS = ["January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"]
_WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

_GRID_ROWS = 6          # the most weeks any month can span


def open_date_picker(parent, var, title="Select Date", lang="English"):
    """Open a calendar popup and write the selected date (YYYY-MM-DD) into *var*.

    *parent* — any tkinter widget (used for positioning).
    *var*    — a tk.StringVar whose value will be set; "" when cleared.
    *lang*   — app.current_lang, so month and weekday names follow the shop.

    The contract is the one the old tkcalendar version had: parse *var* as an
    ISO date (falling back to today), write back an ISO date on Select, write
    an empty string on Clear, and stay modal until dismissed.
    """
    from datetime import date, timedelta
    from config import COLORS, FONTS, RADII, METRICS
    from lang import t

    try:
        selected = date.fromisoformat(var.get().strip())
    except (ValueError, AttributeError):
        selected = date.today()

    today = date.today()
    shown = [selected.year, selected.month]      # list so the closures can write

    # The footer holds four equal buttons, and Bengali and Hindi labels are far
    # wider than the English ones -- at a fixed 420 the Bengali "Select" needed
    # 127px in an 86px cell and lost its last syllable. Three of the four keys
    # (Today / Clear / Cancel) are shared with other screens and must not be
    # reworded to fit, so the dialog measures the text and sizes itself.
    # Measured with the unscaled font, because place_popup applies widget
    # scaling to the logical size it is given.
    import tkinter.font as tkfont
    try:
        _f = tkfont.Font(font=FONTS["button"])
        _btn = max(_f.measure(t(k, lang))
                   for k in ("Today", "Clear", "Cancel", "Select")) + 30
    except Exception:
        _btn = 96
    _width = max(420, _btn * 4 + 5 * 3 + 56)     # 3 gaps + card and dialog padding

    dlg = ctk.CTkToplevel(parent.winfo_toplevel())
    dlg.title(title)
    dlg.resizable(False, False)
    dlg.configure(fg_color=COLORS["bg_main"])
    place_popup(dlg, _width, 428, parent.winfo_toplevel())
    dlg.transient(parent.winfo_toplevel())

    card = ctk.CTkFrame(dlg, fg_color=COLORS["bg_card"],
                        corner_radius=RADII["card"], border_width=1,
                        border_color=COLORS["hairline"])
    card.pack(fill="both", expand=True, padx=14, pady=14)

    # ── Month / year navigation ──────────────────────────────────
    nav = ctk.CTkFrame(card, fg_color="transparent")
    nav.pack(fill="x", padx=14, pady=(14, 4))

    def _nav_btn(text, command, tip):
        b = ctk.CTkButton(nav, text=text, width=32, height=32, corner_radius=16,
                          font=FONTS["button"], fg_color="transparent",
                          hover_color=COLORS["accent_action_tint"],
                          text_color=COLORS["text_muted"], border_width=0,
                          command=command)
        attach_tooltip(b, tip)
        return b

    def _shift_month(delta):
        m = shown[1] + delta
        y = shown[0] + (m - 1) // 12
        shown[0], shown[1] = y, (m - 1) % 12 + 1
        _render()

    def _shift_year(delta):
        shown[0] += delta
        _render()

    _nav_btn("«", lambda: _shift_year(-1),
             t("Previous year", lang)).pack(side="left")
    _nav_btn("‹", lambda: _shift_month(-1),
             t("Previous month", lang)).pack(side="left", padx=(2, 0))
    _nav_btn("»", lambda: _shift_year(1),
             t("Next year", lang)).pack(side="right")
    _nav_btn("›", lambda: _shift_month(1),
             t("Next month", lang)).pack(side="right", padx=(0, 2))

    title_lbl = ctk.CTkLabel(nav, text="", font=FONTS["subheading"],
                             text_color=COLORS["text_dark"])
    title_lbl.pack(side="left", fill="x", expand=True)

    # ── Weekday header ───────────────────────────────────────────
    head = ctk.CTkFrame(card, fg_color="transparent")
    head.pack(fill="x", padx=14, pady=(6, 0))
    for col, wd in enumerate(_WEEKDAYS):
        head.grid_columnconfigure(col, weight=1, uniform="day")
        ctk.CTkLabel(head, text=t(wd, lang).upper(), font=FONTS["small"],
                     text_color=COLORS["text_muted"], height=22
                     ).grid(row=0, column=col, sticky="nsew")

    # ── Day grid ─────────────────────────────────────────────────
    # Built once and reconfigured on every month change. Destroying and
    # rebuilding 42 buttons per arrow press is the same mistake the sidebar
    # and the Categories card grid were both fixed for.
    grid = ctk.CTkFrame(card, fg_color="transparent")
    grid.pack(fill="both", expand=True, padx=14, pady=(2, 6))
    cells = []
    for r in range(_GRID_ROWS):
        grid.grid_rowconfigure(r, weight=1)
        for c in range(7):
            if r == 0:
                grid.grid_columnconfigure(c, weight=1, uniform="day")
            b = ctk.CTkButton(grid, text="", width=46, height=40,
                              corner_radius=RADII["badge"], font=FONTS["body"],
                              fg_color="transparent", border_width=0)
            b.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
            cells.append(b)

    def _pick(d):
        nonlocal selected
        selected = d
        shown[0], shown[1] = d.year, d.month
        _render()

    def _render():
        title_lbl.configure(
            text=f"{t(_MONTHS[shown[1] - 1], lang)}  {shown[0]}")
        weeks = _CAL.monthdayscalendar(shown[0], shown[1])
        flat = [d for wk in weeks for d in wk]
        flat += [0] * (_GRID_ROWS * 7 - len(flat))
        for i, day in enumerate(flat):
            b = cells[i]
            if day == 0:
                b.configure(text="", state="disabled", fg_color="transparent",
                            hover=False, command=None)
                continue
            d = date(shown[0], shown[1], day)
            if d == selected:
                fg, ink, hov = (COLORS["accent_action"], COLORS["on_accent"],
                                COLORS["btn_primary_h"])
            elif d == today:
                fg, ink, hov = (COLORS["accent_action_tint"],
                                COLORS["accent_action_fg"],
                                COLORS["accent_action_tint"])
            else:
                fg, ink, hov = ("transparent", COLORS["text_dark"],
                                COLORS["accent_action_tint"])
            b.configure(text=str(day), state="normal", fg_color=fg,
                        text_color=ink, hover=True, hover_color=hov,
                        command=lambda dd=d: _pick(dd))

    # ── Footer ───────────────────────────────────────────────────
    foot = ctk.CTkFrame(card, fg_color="transparent")
    foot.pack(fill="x", padx=14, pady=(0, 14))

    def _pill(text, kind, command):
        tints = {
            "primary": (COLORS["accent_action"], COLORS["btn_primary_h"],
                        COLORS["on_accent"]),
            "action":  (COLORS["accent_action_tint"], COLORS["glass_glow"],
                        COLORS["accent_action_fg"]),
            "danger":  (COLORS["accent_danger_tint"], COLORS["accent_danger_tint"],
                        COLORS["accent_danger_fg"]),
            "plain":   (COLORS["bg_main"], COLORS["glass_glow"],
                        COLORS["text_dark"]),
        }
        fg, hov, ink = tints[kind]
        h = METRICS["control_sm"]
        return ctk.CTkButton(foot, text=text, font=FONTS["button"], fg_color=fg,
                             hover_color=hov, text_color=ink, height=h,
                             width=1, corner_radius=h // 2, border_width=0,
                             command=command)

    def confirm():
        var.set(selected.isoformat())
        _close()

    def clear():
        var.set("")
        _close()

    def _close():
        try:
            dlg.grab_release()
        except Exception:
            applog.swallow("release date picker grab", applog.DEBUG)
        dlg.destroy()

    # Four equal columns rather than pack. Packing these starved the last two:
    # Select and Cancel each took CTkButton's default 140px width and left
    # Clear 30px and Today 1px. width=1 stops each button demanding that
    # default, and the uniform grid gives them an equal share -- which also
    # survives Bengali and Hindi, whose labels are longer than the English.
    for c in range(4):
        foot.grid_columnconfigure(c, weight=1, uniform="foot")
    for col, (label, kind, cmd) in enumerate((
            (t("Today", lang), "action", lambda: _pick(date.today())),
            (t("Clear", lang), "danger", clear),
            (t("Cancel", lang), "plain", _close),
            (t("Select", lang), "primary", confirm))):
        _pill(label, kind, cmd).grid(row=0, column=col, sticky="ew",
                                     padx=(0 if col == 0 else 5, 0))

    # ── Keyboard ─────────────────────────────────────────────────
    def _move(days):
        _pick(selected + timedelta(days=days))

    dlg.bind("<Escape>",    lambda e: _close())
    dlg.bind("<Return>",    lambda e: confirm())
    dlg.bind("<KP_Enter>",  lambda e: confirm())
    dlg.bind("<Left>",      lambda e: _move(-1))
    dlg.bind("<Right>",     lambda e: _move(1))
    dlg.bind("<Up>",        lambda e: _move(-7))
    dlg.bind("<Down>",      lambda e: _move(7))
    dlg.bind("<Prior>",     lambda e: _shift_month(-1))
    dlg.bind("<Next>",      lambda e: _shift_month(1))

    _render()

    def _make_modal(attempt=0):
        # Wait for the window to actually be MAPPED before taking focus and
        # the grab. A fixed delay is not enough: focus_force() on an unmapped
        # window does not stick, focus falls back to the main window, and then
        # every binding below -- Escape, Return, the arrow keys -- is dead,
        # because Tk routes key events to the focus widget. grab_set() on an
        # unmapped window fails outright. Poll the condition instead, bounded
        # so a window that never maps cannot leave a timer running forever.
        try:
            if not dlg.winfo_exists():
                return
            if not dlg.winfo_viewable():
                if attempt < 50:                       # ~1s at 20ms
                    dlg.after(20, lambda: _make_modal(attempt + 1))
                return
            dlg.focus_force()
            dlg.grab_set()
        except Exception:
            applog.swallow("focus/grab date picker", applog.DEBUG)

    dlg.after(10, _make_modal)
    return dlg


class EmptyState:
    """A message shown over an empty table.

    Every table in this app except the POS cart used to render bare column
    headers over blank white, which tells a shopkeeper nothing about whether
    the filter is wrong, the day is quiet, or the app is broken.

    Placed over the table's container rather than packed, so it never
    disturbs the layout it sits on.
    """

    def __init__(self, parent, title, hint=None):
        import customtkinter as ctk
        from config import COLORS, FONTS
        self._frame = ctk.CTkFrame(parent, fg_color="transparent")
        ctk.CTkLabel(self._frame, text=title, font=FONTS["subheading"],
                     text_color=COLORS["text_muted"]).pack()
        if hint:
            ctk.CTkLabel(self._frame, text=hint, font=FONTS["body"],
                         text_color=COLORS["text_muted"],
                         justify="center").pack(pady=(6, 0))
        self._shown = False

    def sync(self, row_count):
        if row_count:
            if self._shown:
                self._frame.place_forget()
                self._shown = False
        elif not self._shown:
            self._frame.place(relx=0.5, rely=0.5, anchor="center")
            self._shown = True

    def set_text(self, title, hint=None):
        kids = self._frame.winfo_children()
        if kids:
            kids[0].configure(text=title)
        if hint is not None and len(kids) > 1:
            kids[1].configure(text=hint)


# ─────────────────────────────────────────────────────────────────────────────
# Hover tooltip
# ─────────────────────────────────────────────────────────────────────────────

class Tooltip:
    """A hover label for a control that carries no text of its own.

    Built for the icon-only sidebar, where the nav pills are bare emoji and
    the label they lost has to live somewhere. Uses a bare tk.Toplevel with
    overrideredirect(True) rather than a CTkToplevel: it must not steal focus,
    must not appear in the taskbar, and must never outlive the widget it
    describes — the billing/GRN suggestion popups are the standing reminder of
    what a stray Toplevel does to the screen you switch to next.

    Bindings are attached with add="+" so CustomTkinter's own hover effects on
    the button canvas keep working, and to the whole widget subtree because Tk
    sends <Leave> to a parent the moment the pointer crosses onto its child.
    """

    def __init__(self, widget, text, delay=400, side="right", active=True):
        self.widget = widget
        self.text   = text
        self.delay  = delay
        self.side   = side
        self.active = active
        self._after = None
        self._tip   = None
        self._bind_tree(widget)

    def set_active(self, flag):
        """Turn the tooltip on or off without rebinding anything.

        The sidebar toggles between a labelled rail and an icon-only one. Only
        the icon-only mode needs tooltips — a hover label over a pill whose
        text is already visible is noise — and rebinding on every toggle would
        stack duplicate handlers on a widget that now survives the switch.
        """
        self.active = bool(flag)
        if not self.active:
            self._hide()

    def _bind_tree(self, w):
        w.bind("<Enter>",    self._schedule, add="+")
        w.bind("<Leave>",    self._hide,     add="+")
        w.bind("<Button-1>", self._hide,     add="+")
        w.bind("<Destroy>",  self._hide,     add="+")
        for child in w.winfo_children():
            self._bind_tree(child)

    def _schedule(self, _event=None):
        self._cancel()
        if not self.active:
            return
        try:
            self._after = self.widget.after(self.delay, self._show)
        except Exception:
            self._after = None

    def _cancel(self):
        if self._after is not None:
            try:
                self.widget.after_cancel(self._after)
            except Exception:
                pass
            self._after = None

    def _show(self):
        self._after = None
        if self._tip is not None or not self.text:
            return
        import tkinter as tk
        from config import COLORS, FONTS
        try:
            if not self.widget.winfo_exists() or not self.widget.winfo_ismapped():
                return
            tip = tk.Toplevel(self.widget.winfo_toplevel())
            tip.overrideredirect(True)
            tip.attributes("-topmost", True)
            # A neutral dark chip, not one of the four meaning-locked hues —
            # a tooltip carries no meaning of its own.
            bg = COLORS["text_dark"]
            tip.configure(bg=bg)
            tk.Label(tip, text=self.text, bg=bg, fg="#FFFFFF",
                     font=FONTS["caption"], padx=10, pady=5,
                     justify="left").pack()
            tip.update_idletasks()

            if self.side == "right":
                x = self.widget.winfo_rootx() + self.widget.winfo_width() + 8
                y = (self.widget.winfo_rooty()
                     + (self.widget.winfo_height() - tip.winfo_height()) // 2)
            else:
                x = self.widget.winfo_rootx()
                y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6

            # Keep the chip on-screen even for the last pill on a short display.
            x = max(0, min(x, tip.winfo_screenwidth()  - tip.winfo_width()))
            y = max(0, min(y, tip.winfo_screenheight() - tip.winfo_height()))
            tip.geometry(f"+{x}+{y}")
            self._tip = tip
        except Exception:
            self._tip = None

    def _hide(self, _event=None):
        self._cancel()
        if self._tip is not None:
            try:
                self._tip.destroy()
            except Exception:
                pass
            self._tip = None


def attach_tooltip(widget, text, side="right", active=True):
    """Attach a hover tooltip to *widget*. Returns the Tooltip, which callers
    keep when they need to switch it on and off later."""
    return Tooltip(widget, text, side=side, active=active)


class SearchHint:
    """Placeholder text for a search box that is driven by a textvariable.

    CTkEntry suppresses its own `placeholder_text` the moment a `textvariable`
    is set, and every search box in this app needs that variable to drive its
    filter trace — so the hint has to be a CTkLabel placed on top of the field.

    That label is a *sibling* of the entry's inner tk.Entry (CTkEntry is a
    composite: CTkCanvas + Entry) and is created after it, so Tk stacks it on
    top, and `fg_color="transparent"` paints the parent's fill rather than
    letting anything through. It therefore hides two things, not one: the typed
    text, and the blinking insertion caret sitting at the text origin.

    So the hint is unmapped while the field has **focus** as well as while it
    has content. Hiding it on content alone leaves a field that looks dead when
    you click into it — the caret is there, blinking underneath an opaque
    label. Ask for the state with sync() after anything that changes the text.
    """

    def __init__(self, entry, text, font=None, x=18):
        import customtkinter as ctk
        from config import COLORS, FONTS
        self.entry    = entry
        self._x       = x
        self._focused = False
        self.label = ctk.CTkLabel(entry, text=text,
                                  font=font or FONTS["label_form"],
                                  text_color=COLORS["text_muted"],
                                  fg_color="transparent")
        # The label covers most of the field, so its own click has to reach the
        # entry underneath it.
        self.label.bind("<Button-1>", lambda _e: entry.focus_set())
        # CTkEntry.bind() forwards to the inner tk.Entry — which is the widget
        # that actually takes focus, so these fire for real clicks and for Tab.
        entry.bind("<FocusIn>",  self._on_focus_in)
        entry.bind("<FocusOut>", self._on_focus_out)
        self.sync()

    def _on_focus_in(self, _e=None):
        self._focused = True
        self.sync()

    def _on_focus_out(self, _e=None):
        self._focused = False
        self.sync()

    def sync(self, *_):
        """Show the hint only while the field is empty AND unfocused."""
        if self._focused or self.entry.get():
            self.label.place_forget()
        else:
            self.label.place(x=self._x, rely=0.5, anchor="w")

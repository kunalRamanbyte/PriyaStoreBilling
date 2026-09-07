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

import customtkinter as ctk
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
# Calendar date picker helper
# ─────────────────────────────────────────────────────────────────────────────

def open_date_picker(parent, var, title="Select Date"):
    """Open a calendar popup and write the selected date (YYYY-MM-DD) into *var*.

    *parent* — any tkinter widget (used for positioning).
    *var*    — a tk.StringVar whose value will be set.
    """
    import tkinter as tk
    from datetime import date

    try:
        from tkcalendar import Calendar
    except ImportError:
        from tkinter import messagebox
        messagebox.showerror(
            "Missing Library",
            "tkcalendar is required.\nRun:  pip install tkcalendar",
            parent=parent.winfo_toplevel(),
        )
        return

    popup = tk.Toplevel(parent.winfo_toplevel())
    popup.title(title)
    popup.resizable(False, False)
    popup.grab_set()
    popup.attributes("-topmost", True)

    # Start date: parse from var, or use today
    try:
        start = date.fromisoformat(var.get().strip())
    except (ValueError, AttributeError):
        start = date.today()

    from config import COLORS
    bg_pop = COLORS.get("bg_white", "#FFFFFF")
    fg_pop = COLORS.get("text_dark", "#000000")
    bg_input = COLORS.get("bg_input", "#F1F5F9")
    btn_prim = COLORS.get("btn_primary", "#1D4ED8")
    btn_succ = COLORS.get("btn_success", "#16A34A")
    btn_dang = COLORS.get("btn_danger", "#EF4444")
    btn_sec = COLORS.get("btn_secondary", "#94A3B8")
    border_col = COLORS.get("border", "#CBD5E1")

    cal = Calendar(
        popup,
        selectmode="day",
        year=start.year,
        month=start.month,
        day=start.day,
        date_pattern="yyyy-mm-dd",
        font=("Segoe UI", 14),
        background=btn_prim,
        foreground="white",
        # The weekday header used to borrow bg_sidebar, which was deep
        # navy. Direction B's sidebar is white, so it needs its own tint
        # with dark ink rather than white-on-white.
        headersbackground=COLORS["accent_action_tint"],
        headersforeground=COLORS["accent_action_deep"],
        selectbackground=btn_succ,
        selectforeground="white",
        normalbackground=bg_pop,
        normalforeground=fg_pop,
        weekendbackground=bg_input,
        weekendforeground=fg_pop,
        bordercolor=border_col,
    )
    cal.pack(padx=10, pady=10)

    popup.configure(bg=bg_pop)
    btn_frame = tk.Frame(popup, bg=bg_pop)
    btn_frame.pack(fill="x", padx=10, pady=(0, 10))

    def confirm():
        var.set(cal.get_date())
        popup.destroy()

    def clear():
        var.set("")
        popup.destroy()

    tk.Button(btn_frame, text="✅  Select", font=("Segoe UI", 13, "bold"),
              bg=btn_succ, fg="white", relief="flat", padx=16, pady=6,
              cursor="hand2", command=confirm
             ).pack(side="left", padx=(0, 6))
    tk.Button(btn_frame, text="🗑  Clear", font=("Segoe UI", 13),
              bg=btn_dang, fg="white", relief="flat", padx=16, pady=6,
              cursor="hand2", command=clear
             ).pack(side="left", padx=(0, 6))
    tk.Button(btn_frame, text="Cancel", font=("Segoe UI", 13),
              bg=btn_sec, fg="white", relief="flat", padx=16, pady=6,
              cursor="hand2", command=popup.destroy
             ).pack(side="left")

    # Centre over parent
    popup.update_idletasks()
    pw = popup.winfo_width()
    ph = popup.winfo_height()
    px = parent.winfo_rootx() + parent.winfo_width() // 2 - pw // 2
    py = parent.winfo_rooty() + parent.winfo_height() // 2 - ph // 2
    popup.geometry(f"+{max(0, px)}+{max(0, py)}")



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

    def __init__(self, widget, text, delay=400, side="right"):
        self.widget = widget
        self.text   = text
        self.delay  = delay
        self.side   = side
        self._after = None
        self._tip   = None
        self._bind_tree(widget)

    def _bind_tree(self, w):
        w.bind("<Enter>",    self._schedule, add="+")
        w.bind("<Leave>",    self._hide,     add="+")
        w.bind("<Button-1>", self._hide,     add="+")
        w.bind("<Destroy>",  self._hide,     add="+")
        for child in w.winfo_children():
            self._bind_tree(child)

    def _schedule(self, _event=None):
        self._cancel()
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


def attach_tooltip(widget, text, side="right"):
    """Attach a hover tooltip to *widget*. Returns the Tooltip (usually ignored)."""
    return Tooltip(widget, text, side=side)

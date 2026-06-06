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

    cal = Calendar(
        popup,
        selectmode="day",
        year=start.year,
        month=start.month,
        day=start.day,
        date_pattern="yyyy-mm-dd",
        font=("Segoe UI", 12),
        background="#1D4ED8",
        foreground="white",
        headersbackground="#1E3A8A",
        headersforeground="white",
        selectbackground="#16A34A",
        selectforeground="white",
        normalbackground="white",
        normalforeground="#1A1A2E",
        weekendbackground="#F1F5F9",
        weekendforeground="#1A1A2E",
        bordercolor="#CBD5E1",
    )
    cal.pack(padx=10, pady=10)

    btn_frame = tk.Frame(popup, bg="#F8FAFC")
    btn_frame.pack(fill="x", padx=10, pady=(0, 10))

    def confirm():
        var.set(cal.get_date())
        popup.destroy()

    def clear():
        var.set("")
        popup.destroy()

    tk.Button(btn_frame, text="✅  Select", font=("Segoe UI", 11, "bold"),
              bg="#16A34A", fg="white", relief="flat", padx=16, pady=6,
              cursor="hand2", command=confirm
             ).pack(side="left", padx=(0, 6))
    tk.Button(btn_frame, text="🗑  Clear", font=("Segoe UI", 11),
              bg="#EF4444", fg="white", relief="flat", padx=16, pady=6,
              cursor="hand2", command=clear
             ).pack(side="left", padx=(0, 6))
    tk.Button(btn_frame, text="Cancel", font=("Segoe UI", 11),
              bg="#94A3B8", fg="white", relief="flat", padx=16, pady=6,
              cursor="hand2", command=popup.destroy
             ).pack(side="left")

    # Centre over parent
    popup.update_idletasks()
    pw = popup.winfo_width()
    ph = popup.winfo_height()
    px = parent.winfo_rootx() + parent.winfo_width() // 2 - pw // 2
    py = parent.winfo_rooty() + parent.winfo_height() // 2 - ph // 2
    popup.geometry(f"+{max(0, px)}+{max(0, py)}")


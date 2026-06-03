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

"""
responsive.py — one resize contract for every screen.

The app sets `ctk.set_widget_scaling()` once at startup, derived from screen
*height*. Nothing recomputes it, so the logical width a screen actually gets
can be far smaller than the window suggests: a 1366px window on a machine that
scaled up for a tall panel renders ~1038 logical px. That is what used to clip
the cart quantities, squeeze the Excel button to a sliver and overflow the KPI
row — the same defect as "not responsive", seen from a different angle.

So screens stop hardcoding widths and instead react to the logical width they
are really given.

Usage:

    class MyScreen(ResponsiveMixin, ctk.CTkFrame):
        def __init__(...):
            super().__init__(...)
            self._build()
            self.bind_responsive()          # after the widgets exist

        def on_breakpoint(self, bp, logical_w):
            self.header.configure(...)      # called only when bp changes
"""

import customtkinter as ctk
from config import breakpoint_for, GUTTERS


def widget_scaling(widget) -> float:
    """The scaling factor CustomTkinter is rendering this widget at."""
    try:
        return ctk.ScalingTracker.get_widget_scaling(widget)
    except Exception:
        return 1.0


def logical_width(widget) -> float:
    """Width in the same units widget sizes are expressed in."""
    px = widget.winfo_width()
    if px <= 1:
        px = widget.winfo_reqwidth()
    return px / max(0.1, widget_scaling(widget))


class ResponsiveMixin:
    """Debounced <Configure> -> on_breakpoint(name, logical_width).

    Only fires when the breakpoint actually changes, so a resize drag does not
    rebuild the layout on every pixel. Call bind_responsive() once the widgets
    the callback touches exist.
    """

    _RESIZE_DEBOUNCE_MS = 90

    def bind_responsive(self):
        self._bp = None
        self._bp_job = None
        self.bind("<Configure>", self._on_configure, add="+")
        # Settle once after the first real geometry pass.
        self.after(60, self._apply_breakpoint)

    def _on_configure(self, _event=None):
        if getattr(self, "_bp_job", None) is not None:
            try:
                self.after_cancel(self._bp_job)
            except Exception:
                pass
        self._bp_job = self.after(self._RESIZE_DEBOUNCE_MS, self._apply_breakpoint)

    def _apply_breakpoint(self):
        self._bp_job = None
        lw = logical_width(self)
        if lw <= 1:
            return
        bp = breakpoint_for(lw)
        if bp == getattr(self, "_bp", None):
            return
        self._bp = bp
        try:
            self.on_breakpoint(bp, lw)
        except Exception:
            # A layout callback must never take the till down mid-sale, but
            # swallowing it silently would hide a real layout bug, so it goes
            # to stderr rather than nowhere.
            import traceback, sys as _sys
            print(f"[responsive] {type(self).__name__}.on_breakpoint({bp}) failed:",
                  file=_sys.stderr)
            traceback.print_exc()

    # Subclasses override.
    def on_breakpoint(self, bp, logical_w):
        pass

    # -- helpers -------------------------------------------------
    @property
    def bp(self):
        return getattr(self, "_bp", None) or "standard"

    def gutter(self):
        return GUTTERS[self.bp]


def fit_columns(tree, spec, avail_px, scaling=1.0, min_scale=0.62):
    """Size treeview columns to the width actually available.

    `spec` is [(col, weight, min_px), ...]. Weights divide the surplus; every
    column keeps at least min_px so a number never clips to "1.00(". When the
    table genuinely cannot fit, columns bottom out at min_px and the treeview's
    own horizontal scrollbar takes over — which is honest, unlike silently
    truncating a quantity.
    """
    if avail_px <= 1:
        return
    # Leave a couple of px for the treeview's own border, otherwise the
    # columns exactly equal the width and ttk shows a scrollbar for nothing.
    logical = (avail_px - 4) / max(0.1, scaling)
    total_min = sum(m for _, _, m in spec)
    total_weight = sum(w for _, w, _ in spec) or 1

    surplus = logical - total_min
    if surplus < 0:
        # Not enough room even for the minimums: shrink proportionally but
        # never below min_scale, then let the scrollbar do its job.
        factor = max(min_scale, logical / total_min)
        for col, _, m in spec:
            tree.column(col, width=int(m * factor), minwidth=int(m * min_scale))
        return

    for col, weight, m in spec:
        tree.column(col, width=int(m + surplus * weight / total_weight),
                    minwidth=m)


def autohide_scrollbar(widget, bar, layout_kw):
    """Show a scrollbar only when it can actually scroll.

    ttk scrollbars stay visible once placed, so a table whose columns already
    fit carried a dead bar across its edge, and an empty table carried two.

    Works with either geometry manager: pass the same kwargs you would give
    grid() or pack(), and the manager is inferred from them.
    """
    use_pack = "row" not in layout_kw and "column" not in layout_kw

    def _show():
        if use_pack:
            bar.pack(**layout_kw)
        else:
            bar.grid(**layout_kw)

    def _hide():
        if use_pack:
            bar.pack_forget()
        else:
            bar.grid_remove()

    def _set(first, last):
        bar.set(first, last)
        if float(first) <= 0.0 and float(last) >= 1.0:
            _hide()
        else:
            _show()
    return _set

"""
motion.py — the app's motion layer.

Two measurements shape every line of this module.

1. In Tk, translating is cheap and resizing is not. Moving a widget with
   place_configure(x=..) costs 5-9ms a frame; changing any width that
   participates in layout costs 32-126ms, because the geometry manager
   re-solves the whole containing window. So this module animates position
   and window alpha, and nothing else. There is deliberately no size tween.

2. Tweens must be driven by the wall clock, not by a frame counter. A
   frame-driven loop (`for i in range(20)`) stretches a 160ms animation into
   a 600ms crawl on a slow till, which reads far worse than no animation at
   all. Driving by elapsed time means slow hardware drops frames instead:
   the animation still ends on schedule, just less smoothly.
"""

import time

# ~60fps. Tk's after() resolution makes anything finer pointless.
_FRAME_MS = 16

# Keyed by the Tk widget path name (str(widget)), which is unique and stable
# for the life of the widget. id() would be wrong: CPython reuses ids after
# garbage collection, so a new widget could inherit a dead one's animation.
_running = {}

_enabled = True


# ─────────────────────────────────────────────────────────────
# Kill switch
# ─────────────────────────────────────────────────────────────

def init(db):
    """Load the persisted preference once at startup."""
    global _enabled
    try:
        _enabled = db.get_setting("animations_enabled", "1") == "1"
    except Exception:
        _enabled = True


def enabled():
    return _enabled


def set_enabled(flag, db=None):
    """Flip the switch, and persist it when a db is supplied."""
    global _enabled
    _enabled = bool(flag)
    if db is not None:
        db.set_setting("animations_enabled", "1" if _enabled else "0")


# ─────────────────────────────────────────────────────────────
# Easing and colour
# ─────────────────────────────────────────────────────────────

def ease_out_cubic(t):
    """Fast out of the gate, settling at the end. One easing curve is enough."""
    return 1.0 - (1.0 - t) ** 3


def _rgb(c):
    c = c.lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def blend(c1, c2, t):
    """Linear interpolation between two hex colours."""
    a, b = _rgb(c1), _rgb(c2)
    return "#%02x%02x%02x" % tuple(
        max(0, min(255, round(x + (y - x) * t))) for x, y in zip(a, b))


# ─────────────────────────────────────────────────────────────
# The tween
# ─────────────────────────────────────────────────────────────

class _Anim:
    __slots__ = ("widget", "job", "apply", "on_done")

    def __init__(self, widget, apply, on_done):
        self.widget = widget
        self.job = None
        self.apply = apply
        self.on_done = on_done


def _alive(widget):
    try:
        return bool(widget.winfo_exists())
    except Exception:
        return False


def _sweep():
    """Drop registry entries whose widget is gone.

    Destroying a widget deletes the Tcl command behind its pending after()
    callback, so that tick never fires and never notices the widget died.
    Without a sweep the registry keeps a dead entry for every widget
    destroyed mid-animation — and apply_language()/apply_theme() destroy
    every cached screen at once.
    """
    for key, anim in list(_running.items()):
        if not _alive(anim.widget):
            _running.pop(key, None)


def _finish(anim):
    """Land an animation on its end state and fire its callback, once."""
    if _alive(anim.widget):
        try:
            anim.apply(1.0)
        except Exception:
            pass
    if anim.on_done is not None:
        try:
            anim.on_done()
        except Exception:
            pass


def cancel(widget):
    """Supersede any animation on this widget, landing it on its end state.

    Landing rather than abandoning is the point: a cashier clicking through
    the sidebar faster than 160ms would otherwise leave a screen stranded
    partway through its slide.
    """
    anim = _running.pop(str(widget), None)
    if anim is None:
        return
    if anim.job is not None:
        try:
            anim.widget.after_cancel(anim.job)
        except Exception:
            pass
    _finish(anim)


def pending():
    """How many animations are in flight. For tests."""
    _sweep()
    return len(_running)


def tween(widget, ms, apply, on_done=None):
    """Call apply(eased_progress) every ~16ms for ms milliseconds.

    apply() always receives exactly 1.0 as its final call, whether the tween
    ran to completion, was superseded, was disabled, or raised.
    """
    _sweep()
    cancel(widget)

    if not _enabled or ms <= 0 or not _alive(widget):
        anim = _Anim(widget, apply, on_done)
        _finish(anim)
        return

    key = str(widget)
    anim = _Anim(widget, apply, on_done)
    _running[key] = anim
    start = time.perf_counter()

    def tick():
        anim.job = None
        if _running.get(key) is not anim:
            return                      # superseded while the tick was queued
        if not _alive(widget):
            _running.pop(key, None)
            return
        t = min(1.0, (time.perf_counter() - start) * 1000.0 / ms)
        try:
            apply(ease_out_cubic(t))
        except Exception:
            # A bug in apply() must never strand a screen off-position.
            _running.pop(key, None)
            _finish(anim)
            return
        if t >= 1.0:
            _running.pop(key, None)
            if on_done is not None:
                try:
                    on_done()
                except Exception:
                    pass
            return
        anim.job = widget.after(_FRAME_MS, tick)

    tick()


# ─────────────────────────────────────────────────────────────
# Window fade
# ─────────────────────────────────────────────────────────────

def fade_in(win, ms=120):
    """Fade a Toplevel from transparent to opaque.

    Window alpha is the ONE kind of opacity available here: CustomTkinter
    cannot draw translucency on a widget, but a Toplevel has a real -alpha
    attribute. If the platform refuses it, the window is simply left opaque.
    """
    def alpha(v):
        win.attributes("-alpha", v)

    try:
        alpha(0.0)
    except Exception:
        return                      # no alpha support: leave it fully opaque

    if not _enabled:
        try:
            alpha(1.0)
        except Exception:
            pass
        return

    def apply(p):
        try:
            alpha(p)
        except Exception:
            pass

    tween(win, ms, apply)

# Smooth Motion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the ~125ms freeze on every screen navigation, then add restrained motion (a 28px slide, popup fades, nav-pill colour blends) so the app reads as deliberate rather than cheap.

**Architecture:** A new `motion.py` supplies time-driven tweens, a hex colour blend, and a window-alpha fade. `navigate_to()` stops using `pack`/`pack_forget` — which forced Tk to relayout the incoming widget tree on every visit — and instead `place()`s each screen once and swaps with `lift()`. Motion is applied only to widget *position* and *window alpha*, never to width or height, because resizing costs 32–126ms per frame in Tk while translating costs 5–9ms.

**Tech Stack:** Python 3.13, CustomTkinter 5.x, Tkinter, sqlite3. No new third-party dependencies. No pytest — this project's tests are standalone scripts run with `python <script>.py` that print a report and exit 0/1.

**Spec:** `docs/superpowers/specs/2026-09-05-smooth-motion-design.md`

## Global Constraints

- **Animate position and window alpha only. Never animate width or height** of anything that participates in layout. Measured: `place_configure(x=…)` is 5–9ms/frame; changing a laid-out width is 32–126ms/frame.
- **Every tween is time-driven, never frame-driven.** Each tick computes `t = min(1.0, elapsed_ms / duration_ms)`. A frame-driven loop stretches a 160ms animation into a 600ms crawl on a slow till.
- Slide: **28px, 160ms, ease-out-cubic**. Popup fade-in: **120ms**. Nav pill blend: **120ms**.
- Every visible UI string goes through `t(key, lang)` from `lang.py`; new strings need all three translations in the `T` dict (index 0 English, 1 Bengali, 2 Hindi).
- Colours come from `config.COLORS` only. Never a raw hex in a screen file, never `LIGHT_COLORS`/`DARK_COLORS` directly.
- No gradient, blur, shadow or translucency on any *widget* — CustomTkinter cannot draw them. Window-level `-alpha` on a `Toplevel` is the one exception and is what the fade uses.
- `python verify_screens.py` must stay at **16 passed | 0 failed** after every task.
- Any test script that writes to the `settings` table must restore the previous values in a `finally:` block. A script that crashes before restoring leaves the shop's live database altered.
- **Never assert on geometry without waiting for the widget to be mapped.** An unmapped Tk window reports `winfo_width() == 1`, which fails geometry checks intermittently and unreproducibly while every other check passes. Use the `wait_mapped()` helper in Task 3.

---

### Task 1: `motion.py` — the tween engine

**Files:**
- Create: `motion.py`
- Create: `verify_motion.py`

**Interfaces:**
- Consumes: nothing (leaf module; imports only `time`)
- Produces:
  - `ease_out_cubic(t: float) -> float`
  - `blend(c1: str, c2: str, t: float) -> str` — returns `"#rrggbb"`
  - `tween(widget, ms: int, apply, on_done=None) -> None`
  - `cancel(widget) -> None`
  - `enabled() -> bool`
  - `set_enabled(flag: bool, db=None) -> None`
  - `init(db) -> None`
  - `pending() -> int` — count of in-flight animations, for tests

- [ ] **Step 1: Write the failing test**

Create `verify_motion.py`:

```python
"""
verify_motion.py — Headless verification of the motion layer.

Unlike verify_screens.py (which stubs FakeApp), these checks need the real
BillingApp: navigation, the sidebar and the popup helper are what is under
test. Run: python verify_motion.py
"""
import sys, os, time, traceback
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import customtkinter as ctk
import motion

PASS_MARK, FAIL_MARK = "PASS", "FAIL"
results = []


def check(name, fn):
    try:
        fn()
        results.append((PASS_MARK, name, ""))
    except Exception:
        results.append((FAIL_MARK, name, traceback.format_exc(limit=4)))


root = ctk.CTk()
root.withdraw()


def pump(ms):
    """Run the Tk event loop for ms milliseconds so after() callbacks fire."""
    end = time.perf_counter() + ms / 1000.0
    while time.perf_counter() < end:
        root.update()
        time.sleep(0.005)


def test_easing_endpoints():
    assert motion.ease_out_cubic(0.0) == 0.0
    assert motion.ease_out_cubic(1.0) == 1.0
    mid = motion.ease_out_cubic(0.5)
    assert 0.5 < mid < 1.0, f"ease-out must overshoot linear at t=0.5, got {mid}"


def test_blend_endpoints_and_midpoint():
    assert motion.blend("#000000", "#ffffff", 0.0).lower() == "#000000"
    assert motion.blend("#000000", "#ffffff", 1.0).lower() == "#ffffff"
    assert motion.blend("#000000", "#ffffff", 0.5).lower() == "#808080"


def test_blend_accepts_short_hex():
    assert motion.blend("#000", "#fff", 1.0).lower() == "#ffffff"


def test_tween_reaches_exactly_one():
    seen = []
    motion.tween(root, 80, lambda p: seen.append(p))
    pump(400)
    assert seen, "tween never applied anything"
    assert seen[-1] == 1.0, f"tween must land on exactly 1.0, got {seen[-1]}"
    assert motion.pending() == 0, "tween left a handle outstanding"


def test_tween_is_time_driven_not_frame_driven():
    t0 = time.perf_counter()
    done = []
    # Timestamp inside on_done. Measuring after pump() would measure pump(),
    # which blocks for its full duration no matter how fast the tween was.
    motion.tween(root, 120, lambda p: None,
                 on_done=lambda: done.append(time.perf_counter()))
    pump(500)
    assert done, "on_done never fired"
    elapsed = (done[0] - t0) * 1000
    assert elapsed < 400, f"a 120ms tween took {elapsed:.0f}ms — frame-driven?"


def test_cancel_lands_superseded_animation_on_its_end_state():
    seen = []
    motion.tween(root, 5000, lambda p: seen.append(p))
    pump(50)
    motion.cancel(root)
    assert seen[-1] == 1.0, "cancel must apply the final state, not abandon it"
    assert motion.pending() == 0


def test_second_tween_supersedes_the_first():
    a, b = [], []
    motion.tween(root, 5000, lambda p: a.append(p))
    pump(50)
    motion.tween(root, 60, lambda p: b.append(p))
    pump(300)
    assert a[-1] == 1.0, "the superseded tween must land on 1.0"
    assert b[-1] == 1.0, "the new tween must complete"
    assert motion.pending() == 0


def test_disabled_applies_final_state_immediately():
    motion.set_enabled(False)
    try:
        seen = []
        motion.tween(root, 5000, lambda p: seen.append(p))
        assert seen == [1.0], f"disabled tween must apply 1.0 once, got {seen}"
        assert motion.pending() == 0, "disabled tween must schedule nothing"
    finally:
        motion.set_enabled(True)


def test_tween_survives_a_destroyed_widget():
    victim = ctk.CTkFrame(root)
    motion.tween(victim, 400, lambda p: victim.configure(width=100))
    pump(30)
    victim.destroy()
    pump(300)          # must not raise
    assert motion.pending() == 0, "a destroyed widget left an animation running"


def test_apply_raising_does_not_strand_the_animation():
    def boom(p):
        raise ValueError("apply blew up")
    motion.tween(root, 100, boom)
    pump(300)
    assert motion.pending() == 0, "a raising apply() left the animation running"


for name, fn in [
    ("motion — easing endpoints", test_easing_endpoints),
    ("motion — blend endpoints and midpoint", test_blend_endpoints_and_midpoint),
    ("motion — blend accepts short hex", test_blend_accepts_short_hex),
    ("motion — tween lands on exactly 1.0", test_tween_reaches_exactly_one),
    ("motion — tween is time-driven", test_tween_is_time_driven_not_frame_driven),
    ("motion — cancel lands on the end state", test_cancel_lands_superseded_animation_on_its_end_state),
    ("motion — a second tween supersedes the first", test_second_tween_supersedes_the_first),
    ("motion — disabled is instant", test_disabled_applies_final_state_immediately),
    ("motion — survives a destroyed widget", test_tween_survives_a_destroyed_widget),
    ("motion — a raising apply() does not strand", test_apply_raising_does_not_strand_the_animation),
]:
    check(name, fn)

root.destroy()

print()
print("=" * 64)
print("  Priya Store — Motion Verification Report")
print("=" * 64)
passed = failed = 0
for mark, name, tb in results:
    print(f" {mark}  {name}")
    if tb:
        for line in tb.strip().splitlines()[-6:]:
            print(f"       {line}")
    if mark == PASS_MARK:
        passed += 1
    else:
        failed += 1
print("-" * 64)
print(f"  {passed} passed  |  {failed} failed  |  {passed+failed} total")
print("=" * 64)
sys.exit(0 if failed == 0 else 1)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python verify_motion.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'motion'`

- [ ] **Step 3: Write the implementation**

Create `motion.py`:

```python
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
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `python verify_motion.py`
Expected: `10 passed  |  0 failed  |  10 total`, exit 0

- [ ] **Step 5: Confirm nothing regressed**

Run: `python verify_screens.py`
Expected: `16 passed  |  0 failed  |  16 total`

- [ ] **Step 6: Commit**

```bash
git add motion.py verify_motion.py
git commit -m "feat: add motion.py, a time-driven tween layer

Tweens are driven by the wall clock rather than a frame counter: a
frame-driven loop stretches a 160ms animation into a 600ms crawl on slow
hardware, which reads worse than no animation. Time-driven means slow
machines drop frames and still finish on schedule.

cancel() lands a superseded animation on its end state rather than
abandoning it, so rapid navigation cannot strand a screen mid-slide.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 2: Popup fade-in

**Files:**
- Modify: `ui_utils.py` — `place_popup()`
- Modify: `verify_motion.py` — add two checks

**Interfaces:**
- Consumes: `motion.tween`, `motion.enabled` (Task 1)
- Produces: `motion.fade_in(win, ms=120) -> None`; `place_popup()` gains fade behaviour with an unchanged signature

This hooks the single chokepoint used by 21 call sites — 20 dialogs across nine screen modules plus `webcam_scanner.py`. The billing and GRN search-suggestion dropdowns are hand-built `tk.Toplevel`s (`screen_billing.py:844` and `:964`) that never call `place_popup()`, so they stay instant by construction. That is intended: a fade on a dropdown that appears while the user is still typing reads as lag.

- [ ] **Step 1: Write the failing test**

Add to `verify_motion.py`, immediately before the `for name, fn in [` list:

```python
def test_fade_in_reaches_full_opacity():
    from ui_utils import place_popup
    dlg = ctk.CTkToplevel(root)
    try:
        place_popup(dlg, 300, 200, root)
        alpha_at_start = float(dlg.attributes("-alpha"))
        assert alpha_at_start < 0.9, (
            f"popup must start transparent, got {alpha_at_start}")
        pump(400)
        assert float(dlg.attributes("-alpha")) == 1.0, "popup never reached full opacity"
    finally:
        dlg.destroy()


def test_fade_in_is_instant_when_disabled():
    from ui_utils import place_popup
    motion.set_enabled(False)
    dlg = ctk.CTkToplevel(root)
    try:
        place_popup(dlg, 300, 200, root)
        assert float(dlg.attributes("-alpha")) == 1.0, (
            "with animation off the popup must be opaque immediately")
        assert motion.pending() == 0
    finally:
        dlg.destroy()
        motion.set_enabled(True)
```

And add these two entries to the `for name, fn in [...]` list:

```python
    ("popup — fade reaches full opacity", test_fade_in_reaches_full_opacity),
    ("popup — instant when animation is off", test_fade_in_is_instant_when_disabled),
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python verify_motion.py`
Expected: FAIL on "popup — fade reaches full opacity" with an assertion that the popup did not start transparent (it starts at 1.0 today).

- [ ] **Step 3: Add `fade_in` to `motion.py`**

Append to `motion.py`:

```python
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
```

- [ ] **Step 4: Hook it into `place_popup`**

In `ui_utils.py`, add the import at the top of the file, beside `import customtkinter as ctk`:

```python
import motion
```

In `place_popup()`, insert this immediately after the docstring and before the `widget_scale, window_scale = 1.0, 1.0` line:

```python
    # Hide the window before any geometry work: a Toplevel paints at its
    # default position first, so without this the dialog visibly flashes at
    # the wrong spot and then jumps.
    try:
        dlg.attributes("-alpha", 0.0)
    except Exception:
        pass
```

Then replace the final line of `place_popup()`:

```python
    dlg.geometry(f"{gw}x{gh}+{gx}+{gy}")
```

with:

```python
    dlg.geometry(f"{gw}x{gh}+{gx}+{gy}")
    motion.fade_in(dlg)
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python verify_motion.py`
Expected: `12 passed  |  0 failed  |  12 total`

Run: `python verify_screens.py`
Expected: `16 passed  |  0 failed  |  16 total`

- [ ] **Step 6: Commit**

```bash
git add motion.py ui_utils.py verify_motion.py
git commit -m "feat: fade dialogs in through the place_popup chokepoint

place_popup() is called by 21 sites, so hooking it covers every modal
dialog in the app at one point. Setting -alpha 0 before the geometry work
also fixes a pre-existing flash: a Toplevel paints at its default position
before geometry() lands, so dialogs visibly jumped.

The billing/GRN suggestion dropdowns are hand-built tk.Toplevels that
never call place_popup(), so they stay instant - which is what a dropdown
appearing mid-keystroke needs.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 3: Navigation on place + lift (the freeze fix, no motion yet)

**Files:**
- Modify: `main.py` — `navigate_to()`
- Modify: `verify_motion.py` — add three checks

**Interfaces:**
- Consumes: nothing from earlier tasks (this is the pure performance change)
- Produces: screens are managed by `place`, not `pack`. Later tasks rely on `screen.place_configure(x=…)` being valid on every screen.

This is the change that actually removes the cheap feeling. `pack_forget()` + `pack()` forces Tk to relayout the incoming screen's entire widget tree — measured at 60–125ms of frozen UI per navigation, of which `on_show()`'s database reload is only ~9ms.

Safe because no screen manipulates its own geometry manager: every `grid_rowconfigure` / `grid_columnconfigure` call in the 13 screen modules configures a screen's *internal* children.

- [ ] **Step 1: Write the failing test**

Add to `verify_motion.py`. These checks need the real `BillingApp`, and a
process must have exactly one Tk root — so this **replaces** the two lines

```python
root = ctk.CTk()
root.withdraw()
```

with the fixture below. `root = app` at the end keeps every Task 1 and Task 2
check working unchanged.

```python
# ── Real app fixture ──────────────────────────────────────────────────────
# The BillingApp IS the Tk root here. Creating a second ctk.CTk() alongside it
# would give the process two Tk interpreters, which do not share widgets.
#
# Deliberately NOT withdrawn: winfo_ismapped() is false for every child of a
# withdrawn window, and mapping is exactly what these checks assert. A window
# flashes up during the run; that is the cost of testing real geometry.
import main as M

app = M.BillingApp()
root = app
_db = app.db
_saved = {k: _db.get_setting(k, d) for k, d in
          (("sidebar_collapsed", "0"), ("app_theme", "System"),
           ("app_language", "English"), ("animations_enabled", "1"))}
_user = _db.authenticate("admin", "admin123")
assert _user, "admin/admin123 login failed — cannot verify navigation"
app.sidebar_collapsed = False
app._on_login_success(_user)
app.update()

ALL_SCREENS = ["dashboard", "billing", "bill_history", "products", "categories",
               "inventory", "suppliers", "purchase", "customers", "reports",
               "settings", "users", "activity_log"]


def app_pump(ms):
    end = time.perf_counter() + ms / 1000.0
    while time.perf_counter() < end:
        app.update()
        time.sleep(0.005)


def wait_mapped(widget, timeout=5.0):
    """Block until a widget actually has a size.

    An unmapped Tk window reports winfo_width() == 1, which silently fails
    every geometry assertion while the non-geometry checks still pass. The
    sidebar harness produced exactly that once — an 18/6 split where the six
    failures were precisely the six geometry checks — and it was not
    reproducible, because it depended on when the window manager got around
    to realising the window. Never measure geometry without this.
    """
    end = time.perf_counter() + timeout
    while time.perf_counter() < end:
        app.update(); app.update_idletasks()
        if widget.winfo_width() > 1 and widget.winfo_ismapped():
            return
        time.sleep(0.02)
    raise AssertionError(
        f"{widget} never mapped within {timeout}s "
        f"(width={widget.winfo_width()}) — cannot measure geometry")


wait_mapped(app.content_area)
```

Then add these checks before the `for name, fn in [` list:

```python
def test_every_screen_builds_and_shows_under_place():
    for name in ALL_SCREENS:
        app.navigate_to(name)
        app_pump(250)
        scr = app.screens[name]
        assert scr.winfo_manager() == "place", (
            f"{name} is managed by {scr.winfo_manager()!r}, expected 'place'")
        wait_mapped(scr)


def test_navigation_leaves_the_screen_at_x_zero():
    for name in ALL_SCREENS:
        app.navigate_to(name)
        app_pump(400)
        wait_mapped(app.screens[name])
        x = app.screens[name].winfo_x()
        assert x == 0, f"{name} settled at x={x}, expected 0"


def test_rapid_navigation_strands_nothing():
    order = ["dashboard", "billing", "products", "reports", "customers",
             "inventory", "billing", "dashboard", "settings", "products"]
    for name in order:
        app.navigate_to(name)
        app.update()            # deliberately no settling time
    app_pump(600)
    assert app.current_screen == "products"
    stranded = [n for n in ALL_SCREENS
                if n in app.screens and app.screens[n].winfo_x() != 0]
    assert not stranded, f"screens stranded off-position: {stranded}"

    # The assertions above are bookkeeping and position; neither can see
    # stacking order, so both would still pass with lift() deleted outright -
    # the exact failure this task exists to prevent. `winfo children` returns
    # siblings in stacking order, lowest first, so the last entry is the one
    # actually on top.
    top = app.content_area.winfo_children()[-1]
    assert top is app.screens["products"], (
        f"topmost screen is {top}, expected the products screen - "
        f"lift() is not putting the target on top")
```

And add to the `for name, fn in [...]` list:

```python
    ("nav — every screen builds and shows under place", test_every_screen_builds_and_shows_under_place),
    ("nav — navigation settles at x=0", test_navigation_leaves_the_screen_at_x_zero),
    ("nav — rapid navigation strands nothing", test_rapid_navigation_strands_nothing),
```

Finally, replace the bare `root.destroy()` near the bottom of the file with a restore block:

```python
# A script that writes to the settings table MUST restore it, even on a crash:
# an earlier version of this harness died mid-run and left the shop's live
# database on a different language and theme.
try:
    for k, v in _saved.items():
        _db.set_setting(k, v)
finally:
    # One destroy, not two: `root is app` here. Calling both raises
    # TclError("application has been destroyed") and kills the script
    # before it ever prints its pass/fail report.
    root.destroy()
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python verify_motion.py`
Expected: FAIL on "nav — every screen builds and shows under place" with `is managed by 'pack', expected 'place'`

- [ ] **Step 3: Rewrite the geometry half of `navigate_to`**

In `main.py`, delete this block from `navigate_to()` (it sits just after the `self._paint_nav(screen_name)` call):

```python
        for w in self.content_area.winfo_children():
            w.pack_forget()
            w.place_forget()
```

Then replace everything from `screen = self.screens[screen_name]` down to `self.current_screen = screen_name` with:

```python
        screen = self.screens[screen_name]

        # Screens are placed once and then swapped with lift(). The old
        # pack_forget()/pack() pair forced Tk to relayout the incoming
        # screen's entire widget tree on every visit — 60-125ms of frozen UI
        # per navigation, measured, against ~9ms for on_show()'s DB reload.
        # lift() is a stacking-order change and does no geometry work.
        if screen.winfo_manager() != "place":
            screen.place(x=0, y=0, relwidth=1, relheight=1)

        if hasattr(screen, "on_show"):
            screen.on_show()

        screen.lift()

        self.current_screen = screen_name
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python verify_motion.py`
Expected: `15 passed  |  0 failed  |  15 total`

Run: `python verify_screens.py`
Expected: `16 passed  |  0 failed  |  16 total`

- [ ] **Step 5: Confirm the freeze actually shrank**

Run this and record both numbers in the commit message:

```bash
python -c "
import sys, time, statistics; sys.path.insert(0, '.')
import main as M
app = M.BillingApp(); db = app.db
app.sidebar_collapsed = False
app._on_login_success(db.authenticate('admin','admin123')); app.update()
for s in ['dashboard','billing','bill_history','products']:
    app.navigate_to(s); app.update()
t = []
for _ in range(6):
    for s in ['bill_history','billing']:
        t0 = time.perf_counter(); app.navigate_to(s); app.update()
        t.append((time.perf_counter()-t0)*1000)
print('median navigation: %.1fms' % statistics.median(t))
app.destroy()"
```

Expected: meaningfully below the ~125ms baseline. If it did not improve, stop and investigate before continuing — the rest of the plan assumes the budget is there.

- [ ] **Step 6: Commit**

```bash
git add main.py verify_motion.py
git commit -m "perf: swap screens with lift() instead of repacking them

pack_forget()/pack() made Tk relayout the incoming screen's whole widget
tree on every visit. Measured at 60-125ms of frozen UI per navigation, of
which on_show()'s DB reload was only ~9ms - the freeze was the relayout,
not the query.

Screens are now place()d once and swapped with lift(), a stacking-order
change that does no geometry work. Safe because no screen manages its own
placement; their grid_*configure calls are all for internal children.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 4: The 28px slide

**Files:**
- Modify: `motion.py` — add `slide_start` / `slide_home`
- Modify: `main.py` — `navigate_to()`, and a `SLIDE_PX` constant
- Modify: `config.py` — add `MOTION` timings
- Modify: `verify_motion.py` — add two checks

**Interfaces:**
- Consumes: `motion.tween`, `motion.enabled` (Task 1); screens placed by `place` (Task 3)
- Produces:
  - `motion.slide_start(widget, px: int) -> int` — parks the widget and returns the offset actually applied (0 when animation is off)
  - `motion.slide_home(widget, px: int, ms: int = 160) -> None`
  - `config.MOTION` dict with keys `slide_px`, `slide_ms`, `fade_ms`, `blend_ms`

The two-call shape is deliberate. The widget must already sit at its start offset *before* the repaint, otherwise Tk paints it at x=0 and the first tween tick snaps it to x=28 — a visible flash in the wrong direction.

- [ ] **Step 1: Write the failing test**

Add to `verify_motion.py` before the `for name, fn in [` list:

```python
def test_slide_moves_the_screen_and_settles_home():
    app.navigate_to("dashboard")
    app_pump(400)
    app.navigate_to("products")
    app.update()
    scr = app.screens["products"]
    from config import MOTION
    assert scr.winfo_x() > 0, (
        f"the incoming screen must start offset by {MOTION['slide_px']}px, "
        f"found x={scr.winfo_x()}")
    app_pump(500)
    assert scr.winfo_x() == 0, f"the slide did not settle, x={scr.winfo_x()}"


def test_slide_frame_budget_stays_under_33ms():
    from config import MOTION
    app.navigate_to("bill_history")
    app_pump(400)
    scr = app.screens["bill_history"]
    wait_mapped(scr)
    px = MOTION["slide_px"]
    frames = []
    for i in range(21):
        t0 = time.perf_counter()
        scr.place_configure(x=int(px * (1 - i / 20)))
        app.update()
        frames.append((time.perf_counter() - t0) * 1000)
    scr.place_configure(x=0)
    med = statistics.median(frames)
    assert med < 33, f"slide frames cost {med:.1f}ms — below 30fps"
```

Add `import statistics` to the imports at the top of `verify_motion.py`, and add to the list:

```python
    ("slide — moves the screen and settles home", test_slide_moves_the_screen_and_settles_home),
    ("slide — frame budget under 33ms", test_slide_frame_budget_stays_under_33ms),
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python verify_motion.py`
Expected: FAIL — `ImportError: cannot import name 'MOTION' from 'config'`

- [ ] **Step 3: Add the timings to `config.py`**

In `config.py`, immediately after the `METRICS = { ... }` block, add:

```python
# --- Motion ---
# Position and window alpha only: in Tk, translating costs 5-9ms a frame and
# resizing costs 32-126ms, so nothing here ever animates a width or a height.
# 28px rather than a full-width push — a till operator navigates all day, and
# Tk has no cross-fade to soften a bigger move.
MOTION = {
    "slide_px" : 28,
    "slide_ms" : 160,
    "fade_ms"  : 120,
    "blend_ms" : 120,
}
```

- [ ] **Step 4: Add the slide helpers to `motion.py`**

Append to `motion.py`:

```python
# ─────────────────────────────────────────────────────────────
# Screen slide
# ─────────────────────────────────────────────────────────────
#
# Split into two calls on purpose. The widget has to be sitting at its start
# offset BEFORE it is painted; parking and animating in one call would let Tk
# paint it at x=0 first, and the opening frame would snap it sideways.

def slide_start(widget, px):
    """Park a placed widget px to the right. Returns the offset applied."""
    if not _enabled or px <= 0:
        return 0
    try:
        widget.place_configure(x=px)
    except Exception:
        return 0
    return px


def slide_home(widget, px, ms=160):
    """Tween a parked widget back to x=0."""
    if px <= 0 or not _enabled:
        try:
            widget.place_configure(x=0)
        except Exception:
            pass
        return

    def apply(p):
        try:
            widget.place_configure(x=int(round(px * (1.0 - p))))
        except Exception:
            pass

    tween(widget, ms, apply)
```

- [ ] **Step 5: Wire it into `navigate_to`**

In `main.py`, add `MOTION` to the `from config import (...)` list, and add `import motion` beside `from lang import t`.

Then, in `navigate_to()`, replace:

```python
        if hasattr(screen, "on_show"):
            screen.on_show()

        screen.lift()

        self.current_screen = screen_name
```

with:

```python
        if hasattr(screen, "on_show"):
            screen.on_show()

        # Park the screen before it is painted, so its first frame is already
        # offset — otherwise Tk paints it home and the slide snaps sideways.
        px = motion.slide_start(screen, MOTION["slide_px"])
        screen.lift()

        # Pay on_show()'s reload and the first repaint here, before a single
        # frame is scheduled, so the slide runs on a clean budget.
        self.update_idletasks()

        motion.slide_home(screen, px, MOTION["slide_ms"])

        self.current_screen = screen_name
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `python verify_motion.py`
Expected: `17 passed  |  0 failed  |  17 total`

Run: `python verify_screens.py`
Expected: `16 passed  |  0 failed  |  16 total`

- [ ] **Step 7: Look at it**

Run `python main.py`, log in as `admin` / `admin123`, and click through Dashboard → New Bill → Products → Reports. The slide should read as a settle, not a swipe. If it feels sluggish, `MOTION["slide_ms"]` is the one number to turn down.

- [ ] **Step 8: Commit**

```bash
git add motion.py main.py config.py verify_motion.py
git commit -m "feat: slide the incoming screen 28px home over 160ms

Parking and animating are two calls because the screen must already sit at
its offset before Tk paints it; doing both at once paints it home first and
the opening frame snaps sideways.

on_show() and the first repaint are both paid before any frame is
scheduled, so the slide runs on a clean budget instead of stuttering on
frame one.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 5: Nav pill colour blend

**Files:**
- Modify: `main.py` — `_paint_nav()`, plus two new helpers
- Modify: `verify_motion.py` — add one check

**Interfaces:**
- Consumes: `motion.tween`, `motion.blend` (Task 1); `config.MOTION` (Task 4)
- Produces: `BillingApp._set_pill(btn, icon, is_active)` and `BillingApp._blend_pill(btn, icon, is_active)`

Only the two pills that actually change are blended — the outgoing active one and the incoming one. The other eleven are configured instantly, as today.

- [ ] **Step 1: Write the failing test**

Add to `verify_motion.py` before the `for name, fn in [` list:

```python
def test_active_pill_blends_and_lands_on_the_exact_token():
    from config import COLORS
    app.navigate_to("dashboard")
    app_pump(400)
    app.navigate_to("customers")
    app.update()
    btn = app.nav_buttons["customers"]
    mid = btn.cget("fg_color")
    assert mid != "transparent", "the incoming pill should be blending, not transparent"
    app_pump(500)
    assert btn.cget("fg_color") == COLORS["sidebar_active"], (
        f"the active pill must land on the exact token, got {btn.cget('fg_color')}")
    assert app.nav_buttons["dashboard"].cget("fg_color") == "transparent", (
        "the outgoing pill must land on literal 'transparent'")
    assert app.nav_icons["customers"].cget("fg_color") == COLORS["sidebar_active"]
```

Add to the list:

```python
    ("nav pill — blends and lands on the exact token", test_active_pill_blends_and_lands_on_the_exact_token),
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python verify_motion.py`
Expected: FAIL with "the incoming pill should be blending, not transparent" — today `_paint_nav` sets the final colour in one step.

- [ ] **Step 3: Split `_paint_nav` into instant and blended paths**

In `main.py`, replace the whole `_paint_nav` method with:

```python
    def _set_pill(self, btn, icon, is_active):
        """Put a nav pill in its final state, no animation."""
        btn.configure(
            fg_color=COLORS["sidebar_active"] if is_active else "transparent",
            border_width=0,
            hover_color=(COLORS["sidebar_active"] if is_active
                         else COLORS["sidebar_hover"]),
            text_color=(COLORS["on_accent"] if is_active
                        else COLORS["sidebar_text"]),
            font=self._nav_font(is_active),
        )
        if icon is not None:
            # The icon's fg_color must move with the pill. CTkLabel resolves
            # "transparent" against its parent's fill at CREATION time, and
            # these buttons are created transparent on the white sidebar — so
            # an active icon kept a stale white background that covered the
            # glyph entirely.
            icon.configure(
                text_color=COLORS["on_accent"] if is_active
                else COLORS["sidebar_text"],
                fg_color=COLORS["sidebar_active"] if is_active
                else "transparent")

    def _blend_pill(self, btn, icon, is_active):
        """Fade a pill between its resting and active colours.

        "transparent" cannot be interpolated, so the tween runs against the
        sidebar's actual fill and _set_pill() restores the literal token on
        the final frame. Font weight is a discrete change — no curve helps —
        so it is applied up front.
        """
        base, fill = COLORS["bg_sidebar"], COLORS["sidebar_active"]
        ink, on_fill = COLORS["sidebar_text"], COLORS["on_accent"]
        c_from, c_to = (base, fill) if is_active else (fill, base)
        k_from, k_to = (ink, on_fill) if is_active else (on_fill, ink)

        btn.configure(font=self._nav_font(is_active), border_width=0,
                      hover_color=(fill if is_active
                                   else COLORS["sidebar_hover"]))

        def apply(p):
            c = motion.blend(c_from, c_to, p)
            k = motion.blend(k_from, k_to, p)
            btn.configure(fg_color=c, text_color=k)
            if icon is not None:
                icon.configure(fg_color=c, text_color=k)

        motion.tween(btn, MOTION["blend_ms"], apply,
                     on_done=lambda: self._set_pill(btn, icon, is_active))

    def _paint_nav(self, screen_name: str):
        """Mark *screen_name* as the active pill and reset every other one.

        Only the two pills that change are blended; the other eleven are set
        instantly, because animating widgets whose appearance is identical
        before and after is pure cost.
        """
        prev = getattr(self, "current_screen", None)
        for name, btn in self.nav_buttons.items():
            is_active = name == screen_name
            icon = self.nav_icons.get(name)
            if prev != screen_name and name in (prev, screen_name):
                self._blend_pill(btn, icon, is_active)
            else:
                self._set_pill(btn, icon, is_active)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python verify_motion.py`
Expected: `18 passed  |  0 failed  |  18 total`

Run: `python verify_screens.py`
Expected: `16 passed  |  0 failed  |  16 total`

- [ ] **Step 5: Check the collapsed rail too**

Run `python main.py`, collapse the sidebar with the `«` button, and navigate. The icon squares must blend the same way — `_blend_pill` drives `nav_icons`, which exists in both states.

- [ ] **Step 6: Commit**

```bash
git add main.py verify_motion.py
git commit -m "feat: blend the nav pill between resting and active colours

Only the two pills that change are animated; animating the other eleven,
whose appearance is identical before and after, is pure cost.

'transparent' cannot be interpolated, so the tween runs against the
sidebar's real fill and the final frame restores the literal token.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 6: The `animations_enabled` setting

**Files:**
- Modify: `main.py` — call `motion.init(db)` at startup
- Modify: `lang.py` — two new strings
- Modify: `screen_settings.py` — a row in the "Language & Theme" card, `_load()`, and a handler
- Modify: `verify_motion.py` — add one check

**Interfaces:**
- Consumes: `motion.init`, `motion.set_enabled`, `motion.enabled` (Task 1)
- Produces: settings key `animations_enabled` (`"1"` / `"0"`, default `"1"`); `SettingsScreen._toggle_animations()`

- [ ] **Step 1: Write the failing test**

Add to `verify_motion.py` before the `for name, fn in [` list:

```python
def test_settings_toggle_persists_and_drives_motion():
    app.navigate_to("settings")
    app_pump(400)
    scr = app.screens["settings"]
    assert hasattr(scr, "_anim_var"), "Settings has no animations toggle"

    scr._anim_var.set(False)
    scr._toggle_animations()
    assert _db.get_setting("animations_enabled") == "0"
    assert motion.enabled() is False, "the toggle did not reach the motion layer"

    # With motion off, navigation must be instant — no offset, ever.
    app.navigate_to("products")
    app.update()
    assert app.screens["products"].winfo_x() == 0, (
        "with animation off the screen must never be offset")

    scr._anim_var.set(True)
    scr._toggle_animations()
    assert _db.get_setting("animations_enabled") == "1"
    assert motion.enabled() is True
```

Add to the list:

```python
    ("settings — animation toggle persists and takes effect", test_settings_toggle_persists_and_drives_motion),
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python verify_motion.py`
Expected: FAIL with "Settings has no animations toggle"

- [ ] **Step 3: Add the strings to `lang.py`**

In `lang.py`, in the `T` dict, add these immediately after the `"Expand menu"` entry:

```python
    "Smooth Animations": ["Smooth Animations", "স্মুথ অ্যানিমেশন",   "स्मूथ एनिमेशन"],
    "Slide and fade between screens and dialogs":
        ["Slide and fade between screens and dialogs",
         "স্ক্রিন আর ডায়ালগ স্লাইড আর ফেড হয়ে আসবে",
         "स्क्रीन और डायलॉग स्लाइड और फेड होकर आएंगे"],
```

- [ ] **Step 4: Load the preference at startup**

In `main.py`, add `import motion` if Task 4 did not already, then in `BillingApp.__init__`, immediately after the `self.sidebar_collapsed = ...` line, add:

```python
        # Motion reads its own preference once; the tween loop must never
        # touch the database.
        motion.init(self.db)
```

- [ ] **Step 5: Add the Settings row**

In `screen_settings.py`, find the "Language & Theme" card. Immediately after the theme segmented-control block — that is, after the line `self._theme_var.trace_add("write", lambda *_: self._paint_theme_chips())` and before `ctk.CTkFrame(card, fg_color="transparent", height=10).pack()` — insert:

```python
        row = self._row(card, t("Smooth Animations", L))
        ctk.CTkLabel(row,
                     text=t("Slide and fade between screens and dialogs", L),
                     font=FONTS["small"], text_color=COLORS["text_muted"],
                     anchor="w", justify="left", wraplength=380
                     ).pack(side="left", fill="x", expand=True)
        self._anim_var = tk.BooleanVar(value=True)
        ctk.CTkSwitch(row, text="", variable=self._anim_var,
                      fg_color=COLORS["hairline"],
                      progress_color=COLORS["accent_money"],
                      button_color=COLORS["bg_white"],
                      command=self._toggle_animations).pack(side="right")
```

In `_load()`, immediately after the `self._theme_var.set(saved_theme)` line, add:

```python
        # Restore the animation toggle
        self._anim_var.set(s.get("animations_enabled", "1") == "1")
```

And add the handler beside `_toggle_auto_backup` (immediately after it):

```python
    # ── Animation toggle ─────────────────────────────────────
    def _toggle_animations(self):
        import motion
        motion.set_enabled(self._anim_var.get(), self.db)
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `python verify_motion.py`
Expected: `19 passed  |  0 failed  |  19 total`

Run: `python verify_screens.py`
Expected: `16 passed  |  0 failed  |  16 total`

- [ ] **Step 7: Commit**

```bash
git add main.py lang.py screen_settings.py verify_motion.py
git commit -m "feat: add a Smooth Animations toggle in Settings

Reads once at startup into motion's module-level cache, so the tween loop
never touches the database. Off restores the app's previous instant
behaviour exactly, which is what a slow till or a user who dislikes motion
needs.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 7: Stop Categories rebuilding its cards on every visit

**Files:**
- Modify: `screen_categories.py` — `_load_categories()`
- Modify: `verify_motion.py` — add one check

**Interfaces:**
- Consumes: nothing
- Produces: `CategoryScreen._cards_sig` — the list of row tuples the visible cards were built from

`CategoryScreen.on_show()` costs **449ms**, ~50× every other screen. Profiling shows it is not a query: `_load_categories()` destroys and re-creates all 10 cards — roughly 6 CustomTkinter widgets each — on every visit. `destroy` accounts for ~287ms and `_make_cat_card` ~331ms across three runs; `get_categories()` itself barely registers.

The rows almost never change between visits, so redraw only when they actually did. No `force` flag is needed: any edit changes the signature and triggers the rebuild by itself. A theme change destroys the whole screen anyway (`apply_theme` clears `self.screens`), so stale colours are not a risk.

- [ ] **Step 1: Write the failing test**

Add to `verify_motion.py` before the `for name, fn in [` list:

```python
def test_categories_does_not_rebuild_unchanged_cards():
    app.navigate_to("categories")
    app_pump(600)
    scr = app.screens["categories"]
    before = [str(w) for w in scr.cat_cards_frame.winfo_children()]
    assert before, "no category cards were built at all"

    t0 = time.perf_counter()
    scr.on_show()
    app.update()
    reload_ms = (time.perf_counter() - t0) * 1000

    after = [str(w) for w in scr.cat_cards_frame.winfo_children()]
    assert after == before, (
        "unchanged categories were destroyed and rebuilt — the widget paths "
        "changed, so on_show() is still tearing the grid down")
    assert reload_ms < 60, (
        f"an unchanged Categories reload still costs {reload_ms:.0f}ms")
```

Add to the list:

```python
    ("categories — unchanged cards are not rebuilt", test_categories_does_not_rebuild_unchanged_cards),
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python verify_motion.py`
Expected: FAIL with "unchanged categories were destroyed and rebuilt"

- [ ] **Step 3: Guard the rebuild with a signature**

In `screen_categories.py`, replace the whole `_load_categories` method with:

```python
    def _load_categories(self):
        cats = self.db.get_categories(active_only=False)

        # Rebuilding this grid destroys and re-creates about six
        # CustomTkinter widgets per category. Profiled at ~449ms per
        # on_show(), roughly 50x every other screen's reload, and almost none
        # of it is the query — it is the teardown and redraw. The rows rarely
        # change between visits, so redraw only when they actually did.
        # No force flag is needed: an edit changes the signature by itself.
        sig = [(c["category_id"], c["name"], c.get("colour_code"),
                c.get("is_active", 1)) for c in cats]
        if sig == getattr(self, "_cards_sig", None):
            return
        self._cards_sig = sig

        for w in self.cat_cards_frame.winfo_children():
            w.destroy()

        if not cats:
            ctk.CTkLabel(self.cat_cards_frame,
                         text="No categories yet.\nAdd one using the form →",
                         font=FONTS["body"], text_color=COLORS["text_muted"],
                         justify="center").pack(pady=40)
        else:
            for cat in cats:
                self._make_cat_card(cat)

        self.cat_cards_frame.update_idletasks()
        self.list_frame._parent_canvas.yview_moveto(0)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python verify_motion.py`
Expected: `20 passed  |  0 failed  |  20 total`

Run: `python verify_screens.py`
Expected: `16 passed  |  0 failed  |  16 total`

- [ ] **Step 5: Verify the mutation paths still redraw**

Run `python main.py`, open Categories, and exercise all three call sites that reload the list (`screen_categories.py:225`, `:234`, `:253`): add a category, edit one's name or colour, and delete one. Each must appear in the list immediately — the signature changes, so the guard lets the rebuild through.

- [ ] **Step 6: Commit**

```bash
git add screen_categories.py verify_motion.py
git commit -m "perf: stop Categories rebuilding its cards on every visit

on_show() cost 449ms, ~50x every other screen. Profiling put it on widget
teardown and redraw, not the query: _load_categories() destroyed and
re-created about six CustomTkinter widgets per category on every visit.

Guarded by a signature of the rows the cards were built from. An edit
changes the signature and rebuilds by itself, so no force flag is needed.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 8: Documentation

**Files:**
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: everything above
- Produces: nothing code-facing

- [ ] **Step 1: Update the screen contract**

In `CLAUDE.md`, under "Screen Construction Contract", replace the paragraph beginning "3. Lazily instantiates the target screen…" and the sentence about `pack_forget()`s with an accurate description. In the numbered `navigate_to` list, replace item 4:

```markdown
4. `place()`s the target at `x=0, relwidth=1, relheight=1` on its first visit,
   then swaps screens with `lift()` and calls `on_show()`.
```

And immediately after that list, add:

```markdown
> Screens are managed by **`place`, not `pack`**. `pack_forget()`/`pack()` made
> Tk relayout the incoming screen's entire widget tree on every visit —
> measured at 60–125ms of frozen UI per navigation, against ~9ms for
> `on_show()`'s database reload. `lift()` is a stacking-order change and does
> no geometry work. Never reintroduce `pack()` for a screen: it silently
> restores the freeze.
```

- [ ] **Step 2: Document the motion layer**

In `CLAUDE.md`, add a new section immediately after "Shared UI Helpers (`ui_utils.py`)":

```markdown
### Motion (`motion.py`)

`config.MOTION` holds every timing: `slide_px` 28, `slide_ms` 160, `fade_ms`
120, `blend_ms` 120. Never hardcode a duration in a screen.

Two measurements govern this module:

- **Translating is cheap, resizing is not.** `place_configure(x=…)` costs
  5–9ms a frame; changing any width that participates in layout costs
  32–126ms, because the geometry manager re-solves the containing window.
  Animate position and window `-alpha` only. This is why the sidebar collapse
  is *not* animated — a width tween on the rail measured 126ms per frame.
- **Tweens are time-driven, never frame-driven.** Each tick computes
  `t = elapsed / duration`. A `for i in range(20)` loop stretches a 160ms
  animation into a 600ms crawl on slow hardware.

`motion.cancel(widget)` lands a superseded animation on its end state rather
than abandoning it, so rapid navigation cannot strand a screen off-position.
Starting a second tween on the same widget cancels the first automatically.

Popups fade through `place_popup()`, the single chokepoint for 21 dialog
sites. The billing/GRN search-suggestion dropdowns are hand-built
`tk.Toplevel`s that never call it, so they stay instant — which is what a
dropdown appearing mid-keystroke needs. Don't route them through
`place_popup()`.

The `animations_enabled` setting (Settings → Language & Theme) turns all of it
off; every helper then applies its final state immediately.
```

- [ ] **Step 3: Document the second test script**

In `CLAUDE.md`, under "Running Tests", replace "This is the only test suite." with:

```markdown
There are two suites:

```bash
python verify_screens.py    # 16 checks — screens build, ROW_COLORS, styles
python verify_motion.py     # 20 checks — the motion layer and navigation
```

`verify_screens.py` stubs a `FakeApp`, so it never exercises the real sidebar
or `navigate_to()`. `verify_motion.py` builds the real `BillingApp` and covers
what the stub cannot. Both exit 0 on success, 1 on any failure.

> `verify_motion.py` writes to the `settings` table and restores it in a
> `finally:` block. Keep that block — an earlier version crashed mid-run and
> left the shop's live database on a different language and theme.
```

- [ ] **Step 4: Verify the documentation matches reality**

Run both suites and confirm the counts quoted in `CLAUDE.md` are correct:

```bash
python verify_screens.py; python verify_motion.py
```

Expected: 16 and 20. If either differs, fix the number in `CLAUDE.md`.

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: record the place/lift screen contract and the motion layer

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Self-review notes

Checked against `docs/superpowers/specs/2026-09-05-smooth-motion-design.md`:

| Spec requirement | Task |
|---|---|
| `motion.py` tween/fade/blend layer | 1, 2, 4 |
| Time-driven, not frame-driven | 1 (tested) |
| `cancel()` supersedes and lands | 1 (tested) |
| Navigation → place + lift | 3 |
| 28px / 160ms ease-out slide | 4 |
| `on_show` + repaint before the slide starts | 4 |
| Popup fade via `place_popup` | 2 |
| Suggestion dropdowns stay instant | 2 (by construction; noted in 8) |
| Nav pill blend, two pills only | 5 |
| `animations_enabled` + Settings toggle | 6 |
| Categories 449ms | 7 |
| `CLAUDE.md` updated | 8 |
| Error handling: destroyed widget, raising `apply` | 1 (both tested) |
| Tests 1–8 from the spec | 3, 4, 6 (nav/instant/budget), 1 (destroy), 2 (alpha) |

Deviation from the spec worth noting: the spec listed the Categories work as
"investigation, fixed only if the cause is contained". It was profiled during
planning, the cause is contained, and Task 7 carries the actual fix — so it is
now a commitment rather than an open question.

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
    ("popup — fade reaches full opacity", test_fade_in_reaches_full_opacity),
    ("popup — instant when animation is off", test_fade_in_is_instant_when_disabled),
    ("nav — every screen builds and shows under place", test_every_screen_builds_and_shows_under_place),
    ("nav — navigation settles at x=0", test_navigation_leaves_the_screen_at_x_zero),
    ("nav — rapid navigation strands nothing", test_rapid_navigation_strands_nothing),
]:
    check(name, fn)

# A script that writes to the settings table MUST restore it, even on a crash:
# an earlier version of this harness died mid-run and left the shop's live
# database on a different language and theme.
try:
    for k, v in _saved.items():
        _db.set_setting(k, v)
finally:
    # root IS app (see the fixture above) - destroying it twice raises
    # TclError: "application has been destroyed" on the second call.
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

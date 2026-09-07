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

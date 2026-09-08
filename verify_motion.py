"""
verify_motion.py — Headless verification of the motion layer.

Unlike verify_screens.py (which stubs FakeApp), these checks need the real
BillingApp: navigation, the sidebar and the popup helper are what is under
test. Run: python verify_motion.py
"""
import sys, os, time, traceback, statistics
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


def wait_mapped(widget, timeout=15.0):
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
        sized = widget.winfo_width() > 1
        # When the toplevel itself is not viewable — the OS locked the screen,
        # or the window was minimised — every child reports unmapped, and that
        # says nothing about the code under test. Geometry is still computed,
        # so require the size and let mapping go. Without this the suite fails
        # roughly one run in seven on a machine with a lock timeout.
        if sized and (widget.winfo_ismapped() or not app.winfo_viewable()):
            return
        time.sleep(0.02)
    raise AssertionError(
        f"{widget} never mapped within {timeout}s "
        f"(width={widget.winfo_width()}, "
        f"toplevel viewable={bool(app.winfo_viewable())}) — "
        f"cannot measure geometry")


def require_viewable(timeout=2.0):
    """Bring the app window back on screen and wait until Tk agrees it is.

    `winfo_ismapped()` on a child is AND-ed with every ancestor's map state,
    so while the toplevel is minimised — a stray taskbar click, a screen lock,
    a session switch — EVERY screen reports unmapped, no matter what
    navigate_to() actually did. Measured directly: driving the toplevel to
    winfo_viewable()==0 turns a placed child's winfo_ismapped() to 0 while its
    geometry stays correct. That is what turned "expected only the target
    screen mapped" into "found: []" and "the visible screen must be mapped"
    into a failure, on a clean tree, with nothing wrong with the code.

    Note this is NOT the same condition as losing OS focus: a window that is
    merely behind another one still reports viewable=1 and ismapped=1. Only
    genuine non-viewability does this, which is why the guard is deiconify()
    and not focus.

    Unlike focus, viewability is ours to reclaim — deiconify() acts on our own
    window and is not subject to Windows' foreground lock — so poll and
    restore rather than sleeping a fixed amount, and the wait costs nothing on
    a run where the window was never disturbed.
    """
    end = time.perf_counter() + timeout
    while time.perf_counter() < end:
        if not app.winfo_viewable():
            try:
                if app.state() != "normal":
                    app.deiconify()
                app.lift()
            except Exception:
                pass
        app.update_idletasks(); app.update()
        if app.winfo_viewable():
            return True
        time.sleep(0.02)
    return bool(app.winfo_viewable())


def mapped_screens(timeout=5.0):
    """Every cached screen Tk reports as mapped, read while really on screen.

    The read is taken only when the toplevel is viewable BOTH before and
    after it: a minimise landing mid-measurement would otherwise report every
    screen unmapped, which is indistinguishable from the real defect these
    callers exist to catch. Re-read instead of trusting the first sample.
    """
    end = time.perf_counter() + timeout
    while time.perf_counter() < end:
        if require_viewable():
            names = [n for n, scr in app.screens.items() if scr.winfo_ismapped()]
            if app.winfo_viewable():        # still true after the read -> trustworthy
                return names
        time.sleep(0.02)
    raise AssertionError(
        f"the app window never stayed viewable for {timeout}s "
        f"(state={app.state()!r}, viewable={bool(app.winfo_viewable())}) — "
        f"cannot measure which screens are mapped")


def settle(timeout=5.0):
    """Run the event loop until no animation is in flight.

    _on_login_success() navigates to the dashboard, and from Task 4 onward a
    navigation starts a 160ms slide. Seven checks in this file assert
    motion.pending() == 0, and pending() is global — so without settling here,
    the dashboard's own slide is still running when the early checks execute
    and they fail intermittently. Call this after anything that navigates.
    """
    end = time.perf_counter() + timeout
    while time.perf_counter() < end:
        app.update()
        if motion.pending() == 0:
            return
        time.sleep(0.01)
    raise AssertionError(
        f"animations still in flight after {timeout}s "
        f"(pending={motion.pending()})")


wait_mapped(app.content_area)
settle()


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

    # Only the visible (mapped) screen's position is meaningful. A screen
    # navigated away from mid-slide is now place_forget()'d (the Critical
    # fix, item 1) before its tween settles, and Tk never commits that
    # tween's landing x=0 for a widget that is about to be unmanaged - so a
    # forgotten screen's winfo_x() is just a stale snapshot of wherever its
    # slide happened to be at the last moment it was still real geometry.
    # That's harmless: navigate_to() always re-place()s at x=0 before a
    # forgotten screen is ever shown again. Checking every cached screen's
    # winfo_x() here (as this test used to) flags that harmless staleness as
    # "stranded"; only the currently-visible screen's settled position says
    # anything real.
    target = app.screens["products"]
    assert target.winfo_x() == 0, (
        f"the visible screen settled at x={target.winfo_x()}, expected 0")

    # The assertions above are bookkeeping and position; neither can see
    # stacking order, so both would still pass with lift() deleted outright -
    # the exact failure this task exists to prevent.
    #
    # navigate_to() now place_forget()s every screen but the target (the
    # Critical fix for Tab-reachable hidden screens), so winfo_ismapped()
    # alone proves exclusivity but NOT that lift() ran - place_forget()/
    # place() guarantees "only one screen mapped" all by itself, with or
    # without a lift() call. Keep it anyway, because it is the assertion
    # that actually proves the Critical fix (item 1) held under rapid,
    # unsettled navigation.
    mapped = mapped_screens()
    assert mapped == ["products"], (
        f"expected only the target screen mapped after rapid navigation, "
        f"found: {mapped}")

    # Stacking order is untouched by place_forget()/place() - it is set
    # purely by lift() - so this is the assertion that still exercises
    # lift() itself. `winfo children` returns siblings in stacking order,
    # lowest first, so the last entry is the one actually on top.
    top = app.content_area.winfo_children()[-1]
    assert top is app.screens["products"], (
        f"topmost screen is {top}, expected the products screen - "
        f"lift() is not putting the target on top")


def test_focus_cannot_tab_into_a_hidden_screen():
    app.navigate_to("products")
    app_pump(500)
    # Tk's focus ring skips unmapped widgets only. If a hidden screen is
    # left mapped, Tab walks the cashier out of the visible screen into an
    # invisible one — and billing's cart_tree binds <Delete> to removing a
    # line, so an invisible focus there can silently edit a held cart.
    #
    # Both facts are read from ONE guarded sample. Re-reading
    # app.screens["products"].winfo_ismapped() separately afterwards asserts
    # nothing new and reopens the exact race this guard closes: the window
    # can be minimised between the two reads.
    on_screen = mapped_screens()
    mapped = [n for n in on_screen if n != "products"]
    assert not mapped, (
        f"hidden screens are still mapped and reachable by Tab: {mapped}")
    assert "products" in on_screen, (
        f"the visible screen must be mapped; mapped screens: {on_screen}")


def test_slide_moves_the_screen_and_settles_home():
    app.navigate_to("dashboard")
    app_pump(400)
    app.navigate_to("products")
    # update_idletasks(), NOT update(): this asserts on a *transient* state --
    # the screen parked at slide_px before the tween starts walking it home.
    # update() runs pending after() callbacks, so on a loaded machine enough
    # wall-clock passed for the time-driven tween to finish and the assertion
    # saw x=0. update_idletasks() runs the geometry pass without letting any
    # timer fire, so the parked position is observed deterministically.
    app.update_idletasks()
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


def test_a_screen_built_on_this_visit_does_not_slide():
    """The build is the lag; sliding on top of it is what drops frames.

    A first visit pays the screen's whole widget tree inside navigate_to() --
    measured at 124-150ms median and 534ms for Settings, and it is Tcl
    round-trips, not queries (7 DB round-trips across all 13 constructors).
    Whatever repaint work spills past update_idletasks() then lands on the
    slide's opening frames: measured gaps of 25-146ms against a 16ms budget,
    on first visits only. So a screen constructed on this very visit is
    placed home and not animated. A cached one still slides -- the test
    below is what keeps this fix from quietly deleting the motion layer.
    """
    app.navigate_to("dashboard")
    app_pump(400)
    stale = app.screens.pop("users", None)
    if stale is not None:
        stale.destroy()          # force a genuine first visit
    app.navigate_to("users")
    # update_idletasks(), NOT update(): asserts on the transient parked state,
    # for the same reason spelled out in the slide test above.
    app.update_idletasks()
    scr = app.screens["users"]
    assert scr.winfo_x() == 0, (
        "a screen constructed on this visit must not slide, "
        f"found x={scr.winfo_x()}")


def test_a_cached_screen_still_slides():
    """Guard on the fix above: only the FIRST visit skips the animation."""
    app.navigate_to("users")
    app_pump(400)
    app.navigate_to("dashboard")
    app_pump(400)
    app.navigate_to("users")                 # cached now -- must animate
    app.update_idletasks()
    scr = app.screens["users"]
    from config import MOTION
    assert scr.winfo_x() > 0, (
        f"a cached screen must still start offset by {MOTION['slide_px']}px, "
        f"found x={scr.winfo_x()}")
    app_pump(500)
    assert scr.winfo_x() == 0, f"the slide did not settle, x={scr.winfo_x()}"


def test_active_pill_blends_and_lands_on_the_exact_token():
    from config import COLORS
    app.navigate_to("dashboard")
    app_pump(400)
    app.navigate_to("customers")
    # Sample with NO pump in between. motion.tween() runs its first tick
    # synchronously, so the blend's opening frame is already applied when
    # navigate_to returns. Calling app.update() first makes this a race: it
    # drains pending after() callbacks, and on a loaded machine the whole
    # 120ms blend can finish before the sample — measured failing 2 runs in 7.
    btn = app.nav_buttons["customers"]
    mid = btn.cget("fg_color")
    # Mid-blend the pill must be at NEITHER endpoint. Asserting only
    # "!= transparent" cannot fail: before this task the incoming pill was
    # already set straight to sidebar_active, which is also != "transparent".
    assert mid not in ("transparent", COLORS["sidebar_active"]), (
        f"the incoming pill is at an endpoint ({mid}), not blending — "
        f"_paint_nav is still setting the final colour in one step")
    app_pump(500)
    assert btn.cget("fg_color") == COLORS["sidebar_active"], (
        f"the active pill must land on the exact token, got {btn.cget('fg_color')}")
    assert app.nav_buttons["dashboard"].cget("fg_color") == "transparent", (
        "the outgoing pill must land on literal 'transparent'")
    assert app.nav_icons["customers"].cget("fg_color") == COLORS["sidebar_active"]


def test_unchanged_pills_are_not_repainted_on_navigation():
    app.navigate_to("dashboard")
    app_pump(400)
    untouched = "settings" if "settings" in app.nav_buttons else None
    assert untouched, "expected a settings pill to observe"
    before = app.nav_buttons[untouched].cget("fg_color")
    calls = []
    orig = app._set_pill
    app._set_pill = lambda b, i, a: (calls.append(b), orig(b, i, a))[1]
    try:
        app.navigate_to("customers")
        app_pump(400)
    finally:
        app._set_pill = orig
    # Only the outgoing and incoming pills may be touched. Repainting the
    # other eleven costs ~22ms of a navigation for no visible change.
    assert len(calls) <= 2, (
        f"_set_pill ran {len(calls)} times on one navigation; only the "
        f"outgoing and incoming pills should be painted")
    assert app.nav_buttons[untouched].cget("fg_color") == before


def test_settings_toggle_persists_and_drives_motion():
    app.navigate_to("settings")
    app_pump(400)
    scr = app.screens["settings"]
    # The switch lives on the Language & Theme card, and Settings section
    # bodies are built on first open — so reach it the way a shopkeeper does
    # rather than expecting it to exist before its section has been shown.
    scr._show_section("language")
    app_pump(100)
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


def test_init_reads_the_persisted_preference():
    _db.set_setting("animations_enabled", "0")
    motion.init(_db)
    assert motion.enabled() is False, "init() did not read a persisted 0"
    _db.set_setting("animations_enabled", "1")
    motion.init(_db)
    assert motion.enabled() is True, "init() did not read a persisted 1"


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


def test_categories_rebuilds_when_the_signature_changes():
    app.navigate_to("categories")
    app_pump(600)
    scr = app.screens["categories"]
    before = [str(w) for w in scr.cat_cards_frame.winfo_children()]
    assert before, "no category cards were built at all"
    # Force a signature mismatch without touching the database. Tk never
    # reuses a destroyed widget's path name, so a genuine rebuild is
    # visible as changed paths.
    scr._cards_sig = None
    scr.on_show()
    app.update()
    after = [str(w) for w in scr.cat_cards_frame.winfo_children()]
    assert len(after) == len(before), (
        f"rebuild produced {len(after)} cards, expected {len(before)}")
    assert after != before, (
        "a changed signature did not force a rebuild — the guard is "
        "skipping redraws it must permit")


def test_category_signature_covers_every_column():
    # The guard compares a tuple of columns. If a later refactor narrows
    # that tuple, edits to the dropped column would silently fail to
    # redraw on a shop till. Pin it to the table's real schema.
    import ast
    import inspect
    import textwrap
    from screen_categories import CategoryScreen
    with _db.get_conn() as conn:
        columns = {r[1] for r in conn.execute(
            "PRAGMA table_info(categories)").fetchall()}
    src = textwrap.dedent(inspect.getsource(CategoryScreen._load_categories))
    tree = ast.parse(src)

    sig_assign = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "sig" for t in node.targets):
            sig_assign = node
            break
    assert sig_assign is not None, (
        "could not find the 'sig = ...' assignment in _load_categories — "
        "has the guard been renamed or restructured?")

    referenced = {
        n.value for n in ast.walk(sig_assign.value)
        if isinstance(n, ast.Constant) and isinstance(n.value, str)
    }
    missing = [c for c in columns if c not in referenced]
    assert not missing, (
        f"_load_categories' signature ignores {missing} — an edit to "
        f"those columns would not redraw the cards")


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
    ("nav — focus cannot tab into a hidden screen", test_focus_cannot_tab_into_a_hidden_screen),
    ("slide — moves the screen and settles home", test_slide_moves_the_screen_and_settles_home),
    ("slide — frame budget under 33ms", test_slide_frame_budget_stays_under_33ms),
    ("slide — a screen built on this visit does not slide", test_a_screen_built_on_this_visit_does_not_slide),
    ("slide — a cached screen still slides", test_a_cached_screen_still_slides),
    ("nav pill — blends and lands on the exact token", test_active_pill_blends_and_lands_on_the_exact_token),
    ("nav — unchanged pills are not repainted", test_unchanged_pills_are_not_repainted_on_navigation),
    ("settings — animation toggle persists and takes effect", test_settings_toggle_persists_and_drives_motion),
    ("settings — init reads the persisted preference", test_init_reads_the_persisted_preference),
    ("categories — unchanged cards are not rebuilt", test_categories_does_not_rebuild_unchanged_cards),
    ("categories — a changed signature forces a rebuild", test_categories_rebuilds_when_the_signature_changes),
    ("categories — signature covers every column", test_category_signature_covers_every_column),
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

# Smooth motion for Priya Store

**Date:** 2026-09-05
**Branch:** `design-direction-b`
**Status:** approved, not yet implemented

## The problem, restated from measurements

The reported symptom was "navigation and popups are not smooth — it feels like a
cheap app". The obvious reading is that the app lacks animation. Measurement on
the target machine says otherwise.

Every figure below is a median over repeated runs against the real app, real
`billing_data.db`, with heavy screens built:

| Action | Cost | Verdict |
|---|---|---|
| Popup fade via window `-alpha` | 0.15 ms/frame | 60fps, effectively free |
| Nav pill colour blend (`configure(fg_color=…)`) | 1.6 ms/frame | 60fps |
| Slide a pre-`place()`d screen (`place_configure(x=…)`) | 9.4 ms/frame | 60fps |
| Screen swap as written today (`pack_forget` + `pack`) | 60–125 ms | UI frozen |
| Animate the sidebar rail's width (a grid column) | 126 ms/frame | impossible |
| Same, with no screen packed at all | 54 ms/frame | still impossible |
| Rail as a `place()`d overlay, width animated | 32 ms/frame | 30fps at best |
| Rail as a `place()`d overlay, translated by x | 5 ms/frame | 60fps |

Two conclusions follow, and they drive the whole design.

**1. The app feels cheap because it freezes, not because it lacks motion.**
A cached navigation costs ~125 ms end to end. `on_show()` — the DB reload — is
only ~9 ms of that, 8%. The remaining ~115 ms is Tk relayouting the incoming
screen's entire widget tree when it is packed. Animation layered on top of a
125 ms freeze produces a stutter, which reads *worse* than an instant swap.
The freeze has to go first; the motion is what makes its absence legible.

**2. In Tk, translating is cheap and resizing is not.**
Moving a widget with `place(x=…)` costs 5–9 ms. Changing any width that
participates in layout costs 32–126 ms, because the geometry manager
re-solves the containing window. Therefore: **this design animates position
and window alpha only. It never animates the width or height of anything.**

A corollary the user has already accepted: the sidebar cannot smoothly shrink.
Collapsing the rail stays instant. It is out of scope here.

### Separately identified

`ScreenCategories.on_show()` costs **449 ms** — roughly 50× the ~9 ms median of
every other screen. That is the single largest smoothness defect in the app and
no animation can hide it. In scope for investigation (see Scope, below).

## Scope

In scope:

1. A new `motion.py` module — the shared tween/fade/blend layer.
2. Navigation reworked from `pack`/`pack_forget` to `place` + `lift`, with a
   28px ease-out slide on the incoming screen.
3. Popup fade-in, hooked into the single `place_popup()` chokepoint.
4. Nav pill active-state colour blend.
5. An `animations_enabled` setting with a Settings checkbox.
6. Investigation of the 449 ms Categories reload — fixed if the cause is
   contained; reported rather than pursued if it turns out to be a deep query
   problem, so this work does not balloon.
7. `CLAUDE.md` updated for the changed screen contract.

Explicitly out of scope, with reasons:

- **Animating the sidebar collapse.** 126 ms/frame as a grid column; 32 ms/frame
  even as an overlay resize. Physically cannot be made smooth, and collapse is a
  once-a-day action.
- **Popup fade-out.** Would mean touching every dialog's close path (33
  `CTkToplevel` sites) and guarding `destroy()` mid-fade, for a moment the user
  has already looked away from.
- **Button hover transitions.** CustomTkinter owns hover internally; overriding
  it app-wide is invasive for little perceived gain.
- **Fading the search-suggestion dropdowns or the sidebar tooltip.** These must
  feel instantaneous while the user is typing or hovering; a fade there reads as
  lag. They are hand-built `tk.Toplevel`s that never call `place_popup()`, so
  excluding them requires no work.

## Architecture

### `motion.py`

A single new module with no dependency on any screen. It knows about
CustomTkinter widgets and the settings-backed kill switch, nothing else.

```
ease_out_cubic(t)                       -> float        # 1 - (1-t)**3
blend(hex_a, hex_b, t)                  -> "#rrggbb"
tween(widget, ms, apply, on_done=None)  -> handle
cancel(widget)                                          # supersede in-flight
fade_in(toplevel, ms=120)
enabled()                               -> bool
set_enabled(flag)                                       # cache + settings write
```

**`tween` is time-driven, not frame-driven.** Each tick reads the wall clock and
computes `t = min(1.0, elapsed / ms)`, then calls `apply(ease_out_cubic(t))`.
It reschedules with `after(16)` until `t == 1.0`, and always makes a final
`apply(1.0)` call.

This is the load-bearing decision in the module. A frame-driven tween (`for i in
range(20)`) on a slow till stretches a 160 ms animation into a 600 ms crawl. A
time-driven tween drops frames instead: the animation still finishes in 160 ms,
just less smoothly. Slow hardware degrades to something close to today's instant
snap rather than to something visibly worse than it.

**`cancel(widget)` is required, not optional.** Animations are registered in a
dict keyed by the widget. Starting a new animation on a widget cancels the
in-flight one *and applies its final state* before beginning. Without this, a
cashier clicking through the sidebar quickly leaves screens stranded partway
through a slide.

**`enabled()`** reads a module-level cache of the `animations_enabled` setting,
so it costs nothing per frame. When false, `tween` and `fade_in` apply the final
state immediately and return without scheduling anything.

### Navigation

`BillingApp.navigate_to()` changes its geometry strategy:

- **Today:** every screen is `pack(fill="both", expand=True)`ed on show and
  `pack_forget()`ed on hide. Each swap forces a full relayout of the incoming
  tree — the ~115 ms.
- **Proposed:** each screen is `place(x=0, y=0, relwidth=1, relheight=1)`d once,
  on first visit, and stays placed for the life of the session. A swap is
  `screen.lift()` — a stacking-order change, no geometry work.

This is safe because no screen manipulates its own geometry manager. Verified by
grep across all 13 screen modules: every `grid_rowconfigure` / `grid_columnconfigure`
call configures a screen's *internal* children, never the screen's own placement
in `content_area`.

Ordering within a navigation:

1. Role check (unchanged).
2. `on_hide()` on the outgoing screen (unchanged).
3. `_paint_nav()` — now blending, see below.
4. Construct the target screen if this is its first visit, and `place` it.
5. `on_show()` on the target.
6. `lift()` the target, and force the repaint.
7. *Then* start the slide.

Steps 5 and 6 carry the ~9 ms reload and the ~29 ms first repaint. Both complete
before any frame of the animation is scheduled, so the slide runs on a clean
budget rather than stuttering on its first frame.

The slide: incoming screen starts at `x = +28` and tweens to `x = 0` over
**160 ms**, ease-out.

28px rather than a full-width push. Full-width is more dramatic, but a till
operator navigating all day finds it tiring, and Tk offers no cross-fade to
soften it — there is no per-widget alpha, only per-window. For those 160 ms a
28px sliver of the previous screen is visible at the left edge; that is what a
push transition looks like, and both screens share the `bg_main` ground there.

### Popups

`ui_utils.place_popup()` is called by 21 sites — 20 dialogs across nine screen
modules plus the webcam scanner — and is the only place that needs to change:

1. On entry, set `-alpha 0` before any geometry work, so the window never paints
   at full opacity in the wrong position.
2. Compute and apply geometry exactly as today.
3. `motion.fade_in(dlg, 120)`.

The webcam scanner goes through `place_popup()` too, so it fades with the rest;
that is fine for a window the user has deliberately opened.

What stays instant is what must: the billing and GRN search-suggestion dropdowns
and the sidebar tooltip. These are plain `tk.Toplevel`s built by hand
(`screen_billing.py:844` and `:964`), not `CTkToplevel`s routed through
`place_popup()`, so they are excluded by construction rather than by a special
case. A fade on a dropdown that appears while the user is still typing reads as
lag.

### Nav pill colour

`_paint_nav()` currently `configure()`s all pills instantly. It will instead
blend `fg_color` and `text_color` over 120 ms for **only the two pills that
change** — the outgoing active one and the incoming one — leaving the other
eleven configured instantly as today.

`"transparent"` cannot be interpolated, so the blend resolves it to
`COLORS["bg_sidebar"]` for the purpose of the tween and sets the literal
`"transparent"` on the final frame.

### Setting

`animations_enabled`, stored in the `settings` table, default `"1"`. Read once
at startup into `motion`'s cache. A checkbox in Settings writes it through
`motion.set_enabled()`, which updates both the cache and the row.

## Error handling

- Every `after` callback is wrapped: a raised exception cancels the animation and
  applies the final state, so a bug in a tween can never leave a screen stranded
  off-position or a popup stuck at `alpha 0`.
- `tween` checks `widget.winfo_exists()` on each tick and self-cancels if the
  widget was destroyed underneath it — the language/theme switch destroys every
  cached screen, and a rebuild during a slide must not raise.
- `fade_in` is guarded for platforms where `-alpha` is unsupported: if setting it
  raises, the window is left fully opaque. (Measured as supported here; the guard
  is for the frozen build on other Windows configurations.)

## Testing

Headless assertions against the real `BillingApp`, extending the pattern already
used for the sidebar work:

1. All 13 screens build, show, and hide under place/lift.
2. Every navigation ends with the target at exactly `x == 0`.
3. Ten rapid successive navigations leave exactly one screen on top, none
   stranded mid-slide.
4. `animations_enabled = 0` makes navigation and popups instant — no `after`
   handles left outstanding.
5. A popup's alpha reaches 1.0 after its fade.
6. Measured per-frame budget during a slide stays under 33 ms.
7. A screen destroyed mid-slide (language switch) does not raise.
8. `verify_screens.py` stays at 16/16.

## Risks

- **`navigate_to()` is the spine of the app.** Mitigated by the geometry-coupling
  grep above and by exercising all 13 screens in the test pass.
- **`place(relwidth=1, relheight=1)` vs `pack(fill="both", expand=True)`** are
  equivalent in the space they grant a child, but screens laying out with
  internal `grid` depend on getting their full allocation. Covered by test 1.
- **All screens stay placed simultaneously.** No change in memory behaviour —
  screens are already never destroyed between visits today.

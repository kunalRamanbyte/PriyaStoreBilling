# Handoff — sidebar collapse & the motion layer

Written 2026-09-05, updated 2026-09-07 for the finished state. Read this
before touching `main.py`, `motion.py`, or any `verify_*.py` script.

## Where the work sits

```
main
└── design-direction-b     ← Direction B design work; sidebar collapse landed here
    └── feat/smooth-motion ← DONE. Motion plan (8 tasks) + a final-review fix wave.
```

## Status: complete

- `python verify_motion.py`  → **25 passed**
- `python verify_screens.py` → **16 passed**
- `python verify_sidebar.py` → **24 passed**

### What the branch delivers

- **`motion.py`** — a time-driven (not frame-driven) tween engine. Animates
  position and window `-alpha` only, never width/height — see measurements
  below for why.
- **Popup fade-in** through the `place_popup()` chokepoint, honouring
  `config.MOTION["fade_ms"]`.
- **Navigation on `place()` + `lift()`** instead of `pack_forget()`/`pack()` —
  the freeze fix. `navigate_to()` also now `place_forget()`s every screen but
  the target on each call: Tk's focus ring skips *unmapped* widgets only, so
  leaving twelve cached-but-covered screens `place()`d kept them fully
  Tab-reachable (worst case, Billing's `cart_tree` binds `<Delete>` to
  removing a cart line).
- **28px / 160ms slide-in** on every navigation.
- **Nav pill colour blend** between resting and active state on the sidebar.
  Only the outgoing and incoming pills are ever touched — a full 13-pill
  repaint measured 23.4ms against 1.4ms for the 2 that actually change.
- **`animations_enabled`** setting (Settings → Language & Theme); every
  motion helper applies its final state immediately when it's off.
- **Categories' ~449ms reload** collapsed to near-zero on an unchanged
  revisit via a row-signature cache in `screen_categories.py` (one side
  effect: an unchanged revisit no longer resets scroll position to the top).
- **76px collapsible sidebar rail**, off by default, remembered in `settings`
  as `sidebar_collapsed`.

Decisions worth not re-litigating:

- **76px, not 64.** The nav pills sit in a `CTkScrollableFrame`, which
  reserves a fixed 16px scrollbar column, so the icons centred on axis 24
  while the brand mark and avatar centred on 32 — a visible 8px stagger.
  Every non-scrolling block now carries the same allowance on its right.
  `config.SIDEBAR_SCROLLBAR_W` exists for this and nothing else.
- **Activity Log is 🕘, not 📋.** It shared 📋 with Bill History, and with the
  labels gone a duplicated glyph is the whole label.

## Not verified — read this before claiming it works

**The 76px rail has never been looked at with human eyes.** The machine
locked partway through the original session and every screenshot after the
alignment fix captured the Windows lock screen. What was seen with human eyes
was the *64px* version, pre-fix. The 76px build is verified by measurement
only — confirm the icon column lines up with the brand mark and the avatar,
in both light and dark themes, before calling this fully closed.

## The measurements that drive the motion design

Do not redesign the motion layer without re-reading these. They were taken on
this machine against the real app with heavy screens built.

| Action | Cost | Verdict |
|---|---|---|
| Popup fade via window `-alpha` | 0.15 ms/frame | free |
| Nav pill colour blend | 1.6 ms/frame | 60fps |
| Slide a pre-`place()`d screen | 9.4 ms/frame | 60fps |
| Screen swap via `pack_forget`+`pack` | 60–125 ms | **frozen** |
| Animate the sidebar rail's width | 126 ms/frame | impossible |
| Rail as an overlay, width animated | 32 ms/frame | 30fps at best |
| Rail as an overlay, translated by x | 5 ms/frame | 60fps |

**The app does not feel cheap because it lacks animation. It feels cheap because
it freezes.** A cached navigation used to cost ~125ms; `on_show()`'s database
reload is only ~9ms of that. The rest was Tk relayouting the incoming widget
tree on `pack()`. Animation on top of a freeze is a stutter, which reads worse
than a snap. Moving to `place()`+`lift()` cut this substantially (a later,
imperfectly-controlled remeasurement put it around 90ms), but the improvement
should be read as directional, not as a precise benchmark — treat any single
before/after number in this codebase's history with the same caution.

**In Tk, translating is cheap and resizing is not.** Hence: animate position and
window alpha, never width or height. Hence also: the sidebar collapse is *not*
animated, and should not be attempted.

## Traps this session already fell into

**Geometry assertions need a mapped window.** An unmapped Tk window reports
`winfo_width() == 1`. This produced an 18/6 split in `verify_sidebar.py` once and
would not reproduce — the six failures were precisely the six geometry checks.
Both `verify_sidebar.py` and `verify_motion.py` now block on `wait_mapped()`
before measuring. **Never assert on geometry without it.**

**A widget's own in-flight tween can silently undo `place_forget()`.**
`motion.slide_home()`'s `apply()` calls `place_configure()` on every tick,
including its last — and `place_configure()` re-invokes the place geometry
manager even on a widget that was just unmapped. Navigating away from a
screen before its 160ms slide-in settles, then `place_forget()`-ing it (as
`navigate_to()` now does on every call), leaves that stray tween free to
re-map the screen minutes later when it finally ticks to completion.
`navigate_to()` calls `motion.cancel(scr)` before forgetting a screen for
exactly this reason — cancel forces the tween to land *now*, so nothing is
left pending to resurrect the mapping.

**The verification scripts write to the shop's live `billing_data.db`.** They
touch `settings` (`app_theme`, `app_language`, `sidebar_collapsed`). An earlier
run crashed on a console encoding error *before* its restore step and left the
real database on Bengali + Light theme. Restore in a `finally:` block, always.
`sys.stdout.reconfigure(encoding="utf-8", errors="replace")` at the top of any
script that might print Bengali or Hindi.

**`cashier` / `cash123` does not exist in this live database.** Only
`admin` / `admin123` works. Tests that need a non-admin role should fake the role
on the admin user dict rather than authenticate.

**`rtk` is not installed on this machine** despite `~/.claude/CLAUDE.md`
prescribing it. Both `rtk` in bash and PowerShell return "not recognized". Use
plain `git`.

**CustomTkinter forwards `bind()` to its inner canvas.** `btn.event_generate(...)`
on a `CTkButton` does not fire a binding attached through `btn.bind(...)` — the
binding lives on `btn.winfo_children()[0]`. This cost an hour of chasing a
tooltip that worked fine. Fire synthetic events at the canvas.

## Non-obvious things about this codebase

Everything else lives in `CLAUDE.md` and it is accurate. The parts that bite:

- Screens are cached and never destroyed. Anything bound on the toplevel must be
  armed in `on_show()` and disarmed in `on_hide()`.
- `CTkFrame` defaults to 200×200. An empty frame, or one with
  `pack_propagate(False)` and no height, silently holds that size.
- `side="bottom"` does not reserve space — pack footers before any sibling with
  `expand=True`.
- Never read `LIGHT_COLORS` / `DARK_COLORS` in a screen. Always `COLORS`.

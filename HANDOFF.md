# Handoff — sidebar collapse & the motion layer

Written 2026-09-05. Read this before touching `main.py`, `motion.py`, or either
`verify_*.py` script.

## Where the work sits

```
main                       ← untouched
└── design-direction-b     ← the Direction B design work; sidebar collapse landed here
    └── feat/smooth-motion ← YOU ARE HERE. Empty so far; the motion plan executes on it.
```

| Commit | What |
|---|---|
| `e2c37a3` | Motion spec |
| `6fc9519` | Motion plan (8 tasks) |
| `ad06ebf` | Sidebar collapse feature + `verify_sidebar.py` |
| `f90dc0b` | Plan hardening — the mapping guard |

## Done and verified

**Collapsible sidebar.** The rail collapses to an icon-only 76px, remembered in
`settings` as `sidebar_collapsed`, **off by default**. Toggle is `«` in the brand
row when expanded, `»` under the brand mark when collapsed.

- `python verify_screens.py` → **16 passed**
- `python verify_sidebar.py` → **24 passed**

Two decisions worth not re-litigating:

- **76px, not 64.** The nav pills sit in a `CTkScrollableFrame`, which reserves a
  fixed 16px scrollbar column, so the icons centred on axis 24 while the brand
  mark and avatar centred on 32 — a visible 8px stagger. Every non-scrolling
  block now carries the same allowance on its right. Measured spread: 0.4px.
  `config.SIDEBAR_SCROLLBAR_W` exists for this and nothing else.
- **Activity Log is 🕘, not 📋.** It shared 📋 with Bill History, and with the
  labels gone a duplicated glyph is the whole label.

## Not verified — read this before claiming it works

**The 76px rail has never been looked at.** The machine locked partway through
the session and every screenshot after the alignment fix captured the Windows
lock screen. What was seen with human eyes was the *64px* version, pre-fix. The
76px build is verified by measurement only.

**First thing to do on an unlocked machine:** run `python main.py`, log in as
`admin` / `admin123`, collapse the rail, and confirm the icon column lines up
with the brand mark and the avatar in both light and dark themes.

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
it freezes.** A cached navigation costs ~125 ms; `on_show()`'s database reload is
only ~9 ms of that. The rest is Tk relayouting the incoming widget tree on
`pack()`. Animation on top of a freeze is a stutter, which reads worse than a
snap.

**In Tk, translating is cheap and resizing is not.** Hence: animate position and
window alpha, never width or height. Hence also: the sidebar collapse is *not*
animated, and should not be attempted.

## What executes next

`docs/superpowers/plans/2026-09-05-smooth-motion.md` — 8 tasks, 50 steps, each
carrying real test code and its own commit.

1. `motion.py` — time-driven tween engine + `verify_motion.py`
2. Popup fade-in via the `place_popup()` chokepoint
3. **Navigation on `place` + `lift`** — the freeze fix; the task that matters most
4. The 28px / 160ms slide
5. Nav pill colour blend
6. `animations_enabled` setting + Settings toggle
7. Categories' 449 ms reload
8. `CLAUDE.md`

Task 3 is the one to get right. Tasks 1–2 are safe; 4–6 are polish on top.

## Traps this session already fell into

**Geometry assertions need a mapped window.** An unmapped Tk window reports
`winfo_width() == 1`. This produced an 18/6 split in `verify_sidebar.py` once and
would not reproduce — the six failures were precisely the six geometry checks.
Both `verify_sidebar.py` and the plan's `verify_motion.py` now block on
`wait_mapped()` before measuring. **Never assert on geometry without it.**

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

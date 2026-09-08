"""
verify_login.py — the login screen, and its photographic brand panel.

Run:  python verify_login.py     (exit 0 on all pass, 1 on any failure)

Login had no coverage at all before this file: `verify_screens.py` walks the
screens reachable from `NAV`, and login is not one of them — it is built by
`main._show_login()` before a user exists. That gap matters more than most,
because this is the one screen every session has to get through.

What is actually at risk here:

  * **The panel is a raw `tk.Canvas`, not CustomTkinter widgets.** A CTk widget
    with `fg_color="transparent"` resolves to its master's colour and paints an
    *opaque* rectangle, so a label placed over the photo punches a flat blue box
    through it. `Canvas.create_text` composites for real. Nothing in CTk stops
    someone "tidying" the canvas back into CTkLabels, so the suite asserts the
    canvas is there and has drawn.

  * **The corner is painted into the bitmap**, filled with `COLORS["bg_card"]`,
    because CTk cannot clip a child to a parent's rounded corner. That colour
    differs between themes, so a composite that hardcoded white would look
    correct in Light and show a white notch against the dark card in Dark. A
    screenshot cannot prove that headlessly; reading the pixel can, and does —
    both themes, below.

  * **The image must never be able to block sign-in.** A missing, truncated or
    unreadable asset has to degrade to the flat brand-blue panel that shipped
    before, log a warning, and leave every control usable. That path is tested
    by actually moving the asset out of the way.

Read-only with respect to the shop: the live database is opened only to be
copied, and the log is redirected to a throwaway directory.
"""

import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

import config

_TMP = tempfile.mkdtemp(prefix="priya_login_")
_db_copy = os.path.join(_TMP, "billing_data.db")
if os.path.exists(config.DB_PATH):
    shutil.copy2(config.DB_PATH, _db_copy)

import database
database.DB_PATH = _db_copy          # read at Database() construction time

import applog
_LOGTMP = tempfile.mkdtemp(prefix="priya_login_log_")
applog._resolve_log_dir = lambda: _LOGTMP
applog._show_dialog = lambda *a, **k: None      # never block the run on a dialog
applog.install(version="test")
sys.excepthook = sys.__excepthook__             # keep real crashes visible

import tkinter as tk
import customtkinter as ctk
from config import COLORS, resource_path
from database import Database
from screen_login import LoginScreen

PASS, FAIL = [], []

ASSET = os.path.join(ROOT, "assets", "login_panel.png")


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f" {'PASS' if cond else 'FAIL'}  {name}" + (f"  -- {detail}" if detail and not cond else ""))


def read_log():
    p = applog.log_file()
    if not p or not os.path.isfile(p):
        return ""
    with io.open(p, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def pump(w, cycles=8):
    for _ in range(cycles):
        w.update_idletasks()
        w.update()


def rgb(value):
    """'#RRGGBB' -> (r, g, b)."""
    v = value.lstrip("#")
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))


def build(mode):
    """A real LoginScreen on a real root, parked offscreen but viewable —
    the canvas only draws once Tk gives it a size, so a withdrawn root would
    leave every canvas assertion vacuously true."""
    ctk.set_appearance_mode(mode)
    config.apply_theme_mode(mode.lower())
    root = ctk.CTk()
    root.geometry("1366x768+4000+4000")
    root.current_lang = "English"
    root.db = Database()
    screen = LoginScreen(root, lambda u: None)
    screen.pack(fill="both", expand=True)
    pump(root)
    return root, screen


print("=" * 68)
print("  login screen verification")
print("=" * 68)

# ── The asset ───────────────────────────────────────────────
check("panel asset exists in assets/", os.path.isfile(ASSET))
check("panel asset resolves through resource_path",
      os.path.isfile(resource_path("assets", "login_panel.png")))

# ── Light: structure ────────────────────────────────────────
before = len(read_log())
root, screen = build("Light")

canvas = getattr(screen, "_canvas", None)
check("brand panel is a raw tk.Canvas", isinstance(canvas, tk.Canvas),
      type(canvas).__name__)

items = canvas.find_all() if canvas is not None else []
kinds = [canvas.type(i) for i in items] if canvas is not None else []
check("canvas actually drew", len(items) > 0, f"{len(items)} items")
check("panel photo is on the canvas", "image" in kinds, str(sorted(set(kinds))))

texts = [canvas.itemcget(i, "text") for i in items
         if canvas.type(i) == "text"]
check("shop name drawn on the panel", config.SHOP_NAME in texts, str(texts))
check("headline drawn on the panel",
      any("Ring it up" in x for x in texts), str(texts))
check("version chip drawn on the panel",
      any(x == f"v{config.APP_VERSION}" for x in texts), str(texts))
check("both status chips drawn", len(texts) >= 5, f"{len(texts)} text items")

# The panel must fill its side of the card, not CTkFrame's default 200px.
pump(root)
check("panel canvas took a real size",
      canvas.winfo_width() > 300 and canvas.winfo_height() > 400,
      f"{canvas.winfo_width()}x{canvas.winfo_height()}")

# ── Light: the baked corner ─────────────────────────────────
img = screen._compose_panel(400, 558, 36)
check("composed panel is the requested size", img.size == (400, 558), str(img.size))
check("Light: top-left corner is the card surface",
      img.getpixel((1, 1)) == rgb(COLORS["bg_card"]),
      f"{img.getpixel((1, 1))} vs {rgb(COLORS['bg_card'])}")
check("Light: bottom-left corner is the card surface",
      img.getpixel((1, 556)) == rgb(COLORS["bg_card"]),
      f"{img.getpixel((1, 556))} vs {rgb(COLORS['bg_card'])}")
check("right edge is NOT cut back (it meets the form, not the card edge)",
      img.getpixel((399, 1)) != rgb(COLORS["bg_card"]),
      str(img.getpixel((399, 1))))
check("panel centre is photo, not flat fill",
      img.getpixel((200, 279)) != rgb(COLORS["bg_card"]),
      str(img.getpixel((200, 279))))

check("clean build logs no problem", "Unhandled exception" not in read_log()[before:],
      read_log()[before:][-300:])

light_card = rgb(COLORS["bg_card"])
root.destroy()

# ── Dark: the corner must follow the theme ──────────────────
root, screen = build("Dark")
dark_card = rgb(COLORS["bg_card"])
check("Dark theme really swapped bg_card", dark_card != light_card,
      f"{dark_card} == {light_card}")

img = screen._compose_panel(400, 558, 36)
check("Dark: top-left corner is the DARK card surface",
      img.getpixel((1, 1)) == dark_card,
      f"{img.getpixel((1, 1))} vs {dark_card}")
check("Dark: bottom-left corner is the DARK card surface",
      img.getpixel((1, 556)) == dark_card,
      f"{img.getpixel((1, 556))} vs {dark_card}")
root.destroy()

ctk.set_appearance_mode("Light")
config.apply_theme_mode("light")

# ── The failure path ────────────────────────────────────────
# Move the asset aside and rebuild: the panel must degrade to flat blue,
# say so in the log, and leave the screen fully usable.
stashed = os.path.join(_TMP, "login_panel.png")
shutil.move(ASSET, stashed)
try:
    before = len(read_log())
    root, screen = build("Light")
    fresh = read_log()[before:]

    canvas = screen._canvas
    kinds = [canvas.type(i) for i in canvas.find_all()]
    check("missing asset: no image item on the canvas", "image" not in kinds,
          str(sorted(set(kinds))))
    check("missing asset: canvas still shows the brand blue",
          canvas.cget("bg") == COLORS["accent_action_deep"],
          canvas.cget("bg"))

    texts = [canvas.itemcget(i, "text") for i in canvas.find_all()
             if canvas.type(i) == "text"]
    check("missing asset: panel text still drawn",
          config.SHOP_NAME in texts and any("Ring it up" in x for x in texts),
          str(texts))

    check("missing asset: sign-in controls still usable",
          screen.username_entry.winfo_exists()
          and screen.password_entry.winfo_exists()
          and str(screen.login_btn.cget("state")) == "normal")
    check("missing asset: it was logged, not silently swallowed",
          "brand panel image" in fresh, fresh[-300:])
    check("missing asset: it did NOT log as an unhandled crash",
          "Unhandled exception" not in fresh, fresh[-300:])
    root.destroy()
finally:
    shutil.move(stashed, ASSET)

check("asset restored after the failure-path test", os.path.isfile(ASSET))

# ── The credentials hint ────────────────────────────────────
root, screen = build("Light")


def all_text(widget, out):
    """Walk for labels rather than indexing the tree: the nesting is layout,
    not a contract, and an indexed path would break on the next re-layout."""
    for w in widget.winfo_children():
        try:
            if isinstance(w, ctk.CTkLabel):
                out.append(str(w.cget("text")))
        except Exception:
            pass
        all_text(w, out)
    return out


labels = all_text(screen, [])
default_active = root.db.is_default_admin_active()
check("credentials hint matches is_default_admin_active()",
      any("admin123" in x for x in labels) == bool(default_active),
      f"active={default_active} labels={[x for x in labels if 'admin' in x]}")
root.destroy()

# ── Report ──────────────────────────────────────────────────
shutil.rmtree(_TMP, ignore_errors=True)
for h in list(applog.log.handlers):
    try:
        h.close()
    except Exception:
        pass
    applog.log.removeHandler(h)
shutil.rmtree(_LOGTMP, ignore_errors=True)

print("-" * 68)
print(f"  {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    for name in FAIL:
        print(f"    FAILED: {name}")
print("=" * 68)
sys.exit(1 if FAIL else 0)

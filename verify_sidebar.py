"""
verify_sidebar.py — Headless verification of the collapsible sidebar.

verify_screens.py stubs a FakeApp, so it never exercises the real sidebar
or navigate_to(). These checks build the real BillingApp instead.
Run: python verify_sidebar.py
"""
import os, sys, time
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import customtkinter as ctk
import tkinter as tk
import main as M
from config import SIDEBAR_WIDTH, SIDEBAR_WIDTH_COLLAPSED, COLORS

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"   [{detail}]" if detail else ""))


app = M.BillingApp()
# NOT withdrawn: winfo_rootx on an unmapped window is meaningless, and the
# whole point of these checks is real geometry.
db = app.db
prev_collapsed = db.get_setting("sidebar_collapsed", "0")
prev_theme = db.get_setting("app_theme", "System")
prev_lang = db.get_setting("app_language", "English")

user = db.authenticate("admin", "admin123")
app.sidebar_collapsed = False
app._on_login_success(user)
app.update(); app.update_idletasks()


def wait_mapped(timeout=5.0):
    """Block until the rail actually has a width.

    An unmapped Tk window reports winfo_width() == 1, which silently fails
    every geometry assertion below while the non-geometry checks still pass.
    That is exactly the 18/6 split this harness produced once: the window had
    not been realised yet when the measurements were taken.
    """
    end = time.perf_counter() + timeout
    while time.perf_counter() < end:
        app.update(); app.update_idletasks()
        if app._sidebar.winfo_width() > 1 and app._sidebar.winfo_ismapped():
            return
        time.sleep(0.02)
    raise AssertionError(
        f"sidebar never mapped within {timeout}s "
        f"(width={app._sidebar.winfo_width()}) - cannot measure geometry")


wait_mapped()
scale = ctk.ScalingTracker.get_widget_scaling(app)


def centre(w):
    return (w.winfo_rootx() - app._sidebar.winfo_rootx() + w.winfo_width() / 2) / scale


print("\n-- expanded --")
check("rail is SIDEBAR_WIDTH",
      abs(app._sidebar.winfo_width() / scale - SIDEBAR_WIDTH) < 2,
      f"{app._sidebar.winfo_width() / scale:.0f}")
check("nav pills carry their labels",
      all(b.cget("text").strip() for b in app.nav_buttons.values()),
      f"{len(app.nav_buttons)} pills")

print("\n-- toggle -> collapsed --")
app._toggle_sidebar(); wait_mapped()
check("setting persisted as 1", db.get_setting("sidebar_collapsed") == "1")
check("rail is SIDEBAR_WIDTH_COLLAPSED",
      abs(app._sidebar.winfo_width() / scale - SIDEBAR_WIDTH_COLLAPSED) < 2,
      f"{app._sidebar.winfo_width() / scale:.0f}")
check("nav pills carry no label",
      all(b.cget("text") == "" for b in app.nav_buttons.values()))
check("every screen still has an icon",
      set(app.nav_icons) == set(app.nav_buttons),
      f"{len(app.nav_icons)} icons")

# One optical centre down the rail.
rail = app._sidebar
brand = rail.winfo_children()[0]
mark = brand.winfo_children()[0]
axes = {"brand mark": centre(mark)}
for k, b in app.nav_buttons.items():
    axes[f"pill:{k}"] = centre(b)
spread = max(axes.values()) - min(axes.values())
check("every block shares one optical centre", spread <= 1.5,
      f"spread {spread:.1f}px, axis {min(axes.values()):.1f}")

print("\n-- active pill survives the rebuild --")
active = [n for n, b in app.nav_buttons.items()
          if b.cget("fg_color") == COLORS["sidebar_active"]]
check("active pill preserved across toggle", active == [app.current_screen],
      f"active={active} screen={app.current_screen}")

app.navigate_to("reports"); app.update()
active = [n for n, b in app.nav_buttons.items()
          if b.cget("fg_color") == COLORS["sidebar_active"]]
check("active pill follows navigation while collapsed", active == ["reports"], str(active))
icon = app.nav_icons["reports"]
check("active icon repaints onto the pill fill",
      icon.cget("fg_color") == COLORS["sidebar_active"], str(icon.cget("fg_color")))

print("\n-- hover tooltip --")


def toplevels():
    return [w for w in app.winfo_children() if w.winfo_class() == "Toplevel"]


before = len(toplevels())
btn = app.nav_buttons["purchase"]
btn.winfo_children()[0].event_generate("<Enter>", x=10, y=10)
for _ in range(20):
    app.update(); time.sleep(0.05)
tips = [w for w in toplevels()]
check("tooltip appears on hover", len(tips) == before + 1, f"{before} -> {len(tips)}")
if len(tips) > before:
    tip = tips[-1]
    lbl = tip.winfo_children()[0]
    expected = M.t("Purchase/GRN", app.current_lang)
    check("tooltip shows the label the pill lost", lbl.cget("text") == expected,
          repr(lbl.cget("text")))
    check("tooltip sits clear of the rail (right of the pill)",
          tip.winfo_rootx() >= btn.winfo_rootx() + btn.winfo_width(),
          f"tip x={tip.winfo_rootx()} pill right={btn.winfo_rootx() + btn.winfo_width()}")
    check("tooltip is a borderless topmost window",
          tip.overrideredirect() and tip.attributes("-topmost"))
    check("tooltip ink clears its ground",
          lbl.cget("bg") == COLORS["text_dark"] and lbl.cget("fg") == "#FFFFFF",
          f"{lbl.cget('bg')} / {lbl.cget('fg')}")

btn.winfo_children()[0].event_generate("<Leave>")
app.update()
check("tooltip is destroyed on leave", len(toplevels()) == before,
      f"{len(toplevels())} left")

print("\n-- tooltip cannot outlive its rail --")
btn.winfo_children()[0].event_generate("<Enter>", x=10, y=10)
for _ in range(20):
    app.update(); time.sleep(0.05)
had = len(toplevels()) > before
app._toggle_sidebar()          # destroys the sidebar out from under the tooltip
app.update(); time.sleep(0.3); app.update()
check("stray tooltip torn down with the sidebar", had and len(toplevels()) == before,
      f"raised={had} left={len(toplevels()) - before}")
check("setting persisted back to 0", db.get_setting("sidebar_collapsed") == "0")

print("\n-- collapsed state survives theme and language switches --")
app._toggle_sidebar(); app.update()
app.apply_theme("Dark"); wait_mapped()
check("still collapsed after theme switch",
      app.sidebar_collapsed
      and abs(app._sidebar.winfo_width() / scale - SIDEBAR_WIDTH_COLLAPSED) < 2)
check("dark theme repaints the rail",
      app._sidebar.cget("fg_color") == COLORS["bg_sidebar"])
app.apply_theme("Light"); app.update()

app.apply_language("Bengali"); app.update()
check("still collapsed after language switch", app.sidebar_collapsed)
btn = app.nav_buttons["products"]
btn.winfo_children()[0].event_generate("<Enter>", x=10, y=10)
for _ in range(20):
    app.update(); time.sleep(0.05)
tips = toplevels()
if len(tips) > before:
    got = tips[-1].winfo_children()[0].cget("text")
    check("tooltip is translated, not English",
          got == M.t("Products", "Bengali") and got != "Products", repr(got))
    tips[-1].destroy()
else:
    check("tooltip is translated, not English", False, "no tooltip raised")
app.apply_language("English"); app.update()

print("\n-- role filtering still applies collapsed --")
cash = dict(app.current_user); cash["role"] = "cashier"
app.current_user, app.current_role = cash, "cashier"
app.screens = {}
app._build_main_window(); wait_mapped()
check("cashier sees only their screens",
      set(app.nav_buttons) == {"dashboard", "billing", "bill_history", "customers"},
      str(sorted(app.nav_buttons)))
check("collapsed rail intact for a short nav list",
      abs(app._sidebar.winfo_width() / scale - SIDEBAR_WIDTH_COLLAPSED) < 2)

db.set_setting("sidebar_collapsed", prev_collapsed)
db.set_setting("app_theme", prev_theme)
db.set_setting("app_language", prev_lang)
app.destroy()

passed = sum(1 for _, ok, _ in results if ok)
print(f"\n{'=' * 60}\n  {passed} passed | {len(results) - passed} failed "
      f"| {len(results)} total\n{'=' * 60}")
print("restored settings:", prev_collapsed, prev_theme, prev_lang)
sys.exit(0 if passed == len(results) else 1)

"""
verify_theme.py — the theme/language rebuild must not leave dead widgets behind.

Run:  python verify_theme.py     (exit 0 on all pass, 1 on any failure)

Regression test for a crash the log recorder caught in real use:

    _tkinter.TclError: bad window path name
    ".!ctkframe.!ctkframe3.!billingscreen. ... .!ctkentry.!entry"

On Windows, CustomTkinter recolours the title bar by withdrawing and re-showing
the root window. Before withdrawing it captures `focus_get()`, and afterwards
schedules `after(1, that_widget.focus)` to put focus back
(`ctk_tk.py::_windows_set_titlebar_color`). `apply_theme()` then destroys every
cached screen — so if the cashier's focus was in a POS field, that widget is
gone by the time the 1 ms timer fires.

`apply_language()` is the control: it runs the same destroy loop but never
touches the appearance mode, so nothing is scheduled and nothing breaks.

The oracle is `applog` itself — a real Tk callback failure is exactly what it
records, so the assertion is simply "the recorder logged nothing".

Runs against a COPY of the database: the live shop file is opened only to be
copied, and `apply_theme` writes `app_theme` to the settings table.
"""

import io
import os
import shutil
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

import config

_TMP = tempfile.mkdtemp(prefix="priya_theme_")
_db_copy = os.path.join(_TMP, "billing_data.db")
if os.path.exists(config.DB_PATH):
    shutil.copy2(config.DB_PATH, _db_copy)

import database
database.DB_PATH = _db_copy          # read at Database() construction time

import applog
_LOGTMP = tempfile.mkdtemp(prefix="priya_theme_log_")
applog._resolve_log_dir = lambda: _LOGTMP
applog._show_dialog = lambda *a, **k: None      # never block the run on a dialog
applog.install(version="test")
sys.excepthook = sys.__excepthook__             # keep real crashes in this script visible

import customtkinter as ctk
import main as M

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f" {'PASS' if cond else 'FAIL'}  {name}" + (f"  -- {detail}" if detail and not cond else ""))


def read_log():
    p = applog.log_file()
    if not p or not os.path.isfile(p):
        return ""
    with io.open(p, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def pump(app, cycles=25):
    """Run the event loop long enough for a 1 ms after() to fire and land."""
    for _ in range(cycles):
        app.update_idletasks()
        app.update()
        time.sleep(0.02)


def take_focus(widget, timeout=1.0):
    """Put OS focus inside `widget` and wait until Tk agrees that it is there.

    `focus_set()` only queues a focus change *within* the application; it says
    nothing about whether the application holds focus at the OS level. While
    any other window is in front, `focus_get()` returns None even though this
    window is still viewable and its widgets still mapped — measured directly:
    viewable=1, ismapped=1, focus_get()=None, while Tk's own focus_lastfor()
    still names the entry. A developer machine hands focus to a notification
    or a build window at any moment, so a fixed `pump()` followed by a single
    `focus_get()` reads whatever happened to be true at that instant. That is
    the whole of this check's flakiness: it failed with detail `None`.

    Waiting for the real thing matters beyond this check. CustomTkinter
    captures `self.focus_get()` before withdrawing the root
    (`ctk_tk.py::_windows_set_titlebar_color`) — so with the window merely
    unfocused it captures None, schedules no `after(1, widget.focus)`, and the
    three theme checks below would pass without ever exercising the crash they
    exist to catch. Never paper over this by asserting on `focus_lastfor()`
    instead: it survives a focus loss precisely because it is *not* what
    CustomTkinter reads.

    So poll for the condition rather than assume it arrived, the same way
    `ui_utils.open_date_picker` does before `focus_force()`/`grab_set()`:
    wait for the window to be viewable (forcing focus onto an unmapped window
    does not stick), re-assert the claim on every pass so a transient steal is
    recovered from rather than being fatal, and stop the moment `focus_get()`
    names a widget. Bounded, so a window that never gets focus cannot hang the
    run — the caller still asserts on what is returned.
    """
    top = widget.winfo_toplevel()
    end = time.perf_counter() + timeout
    while time.perf_counter() < end:
        if not top.winfo_viewable():
            # Minimised or withdrawn — by a screen lock, a session switch, a
            # stray taskbar click. Unlike OS focus, this is ours to reclaim:
            # deiconify() acts on our own window and no foreground lock
            # applies. Without it the loop below would spin out its whole
            # budget waiting for a window nothing was going to restore.
            try:
                if top.state() != "normal":
                    top.deiconify()
                top.lift()
            except Exception:
                pass
        top.update_idletasks()
        top.update()
        if top.winfo_viewable():
            try:
                widget.focus_force()      # CTkEntry delegates to its inner tk.Entry
            except Exception:
                pass
            top.update_idletasks()
            top.update()
            got = top.focus_get()
            if got is not None:
                return got
        time.sleep(0.02)
    return top.focus_get()


print("=" * 68)
print("  theme / language rebuild verification")
print("=" * 68)

app = M.BillingApp()
app.geometry("1400x860+4000+4000")       # offscreen but viewable: focus is real
app.current_user = {"user_id": 1, "username": "admin", "name": "Admin", "role": "admin"}
app.current_role = "admin"
app._build_main_window()
pump(app, 6)

app.navigate_to("billing")
pump(app, 6)
pos = app.screens["billing"]

# Focus must genuinely sit inside a POS field, because that is the widget
# CustomTkinter captures and then tries to restore after the rebuild.
focused = take_focus(pos.search_entry)
check("focus really is inside a POS entry",
      focused is not None and "billingscreen" in str(focused),
      str(focused))

for theme in ("Dark", "Light"):
    before = len(read_log())
    app.apply_theme(theme)
    pump(app)
    fresh = read_log()[before:]
    check(f"theme switch to {theme} leaves no dead widget",
          "bad window path name" not in fresh,
          fresh[-300:])
    check(f"theme switch to {theme} logs no unhandled exception",
          "Unhandled exception" not in fresh,
          fresh[-300:])
    check(f"app still alive after switching to {theme}", bool(app.winfo_exists()))

    # Put focus back into the rebuilt POS for the next iteration, through the
    # same helper: the second pass has to be as genuinely focused as the
    # first, or the Light switch below captures None and verifies nothing
    # while still reporting PASS.
    app.navigate_to("billing")
    pump(app, 6)
    take_focus(app.screens["billing"].search_entry)

# Control: same destroy loop, no appearance change.
before = len(read_log())
app.apply_language("English")
pump(app)
check("language switch leaves no dead widget",
      "bad window path name" not in read_log()[before:])

app.destroy()
shutil.rmtree(_TMP, ignore_errors=True)
for h in list(applog.log.handlers):
    try:
        h.close()
    except Exception:
        pass
    applog.log.removeHandler(h)
shutil.rmtree(_LOGTMP, ignore_errors=True)

print("-" * 68)
print(f"  {len(PASS)} passed  |  {len(FAIL)} failed  |  {len(PASS) + len(FAIL)} total")
print("=" * 68)
sys.exit(1 if FAIL else 0)

"""
verify_applog.py — proves the black box actually records.

Run:  python verify_applog.py     (exit 0 on all pass, 1 on any failure)

Every test runs against a throwaway log directory, never the shop's own.
The important cases are the ones that used to leave nothing behind:

  * an exception inside a Tk callback (where nearly every real crash lands)
  * an exception inside an after() tick
  * a windowed build, where sys.stderr is None
  * a repeating fault, which must be logged every time but interrupt once
"""

import io
import os
import shutil
import sys
import tempfile

import applog

PASS, FAIL = [], []

# applog installs sys.excepthook, so a bug in THIS script would be quietly
# logged to a temp file that the cleanup then deletes. Keep the real one.
_ORIGINAL_EXCEPTHOOK = sys.excepthook


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f" {'PASS' if cond else 'FAIL'}  {name}" + (f"  -- {detail}" if detail and not cond else ""))


def wait_for(predicate, timeout=3.0, tick=None):
    """Pump the event loop until `predicate()` holds, or the timeout expires.

    A fixed number of update() calls is not a wait: `after(1, ...)` needs
    real elapsed time, and on a fast machine twenty update() calls can span
    under a millisecond. That made this suite pass or fail depending on how
    busy the box was.
    """
    import time
    end = time.time() + timeout
    while time.time() < end:
        if tick is not None:
            tick()
        if predicate():
            return True
        time.sleep(0.01)
    return predicate()


def read_log():
    path = applog.log_file()
    if not path or not os.path.isfile(path):
        return ""
    with io.open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


# ── Redirect the log somewhere disposable, and never show a real dialog ──
TMP = tempfile.mkdtemp(prefix="priya_applog_")
applog._resolve_log_dir = lambda: TMP

_dialogs = []
applog._show_dialog = lambda exc_type, exc, fatal: _dialogs.append(
    (getattr(exc_type, "__name__", "?"), fatal))

# The windowed build has no stderr. install() must cope, and every later
# log call must still work -- a StreamHandler(None) would raise on every
# single record instead.
_real_stderr, sys.stderr = sys.stderr, None
try:
    applog.install(version="test")
finally:
    sys.stderr = _real_stderr
sys.excepthook = _ORIGINAL_EXCEPTHOOK

print("=" * 64)
print("  applog verification")
print("=" * 64)

check("install() creates a log file", os.path.isfile(applog.log_file()),
      applog.log_file())
check("no console handler when sys.stderr is None",
      not any(h.__class__.__name__ == "StreamHandler" for h in applog.log.handlers))
check("startup banner recorded", "starting" in read_log())

# ── swallow() ───────────────────────────────────────────────────────
try:
    raise ValueError("simulated backup failure")
except Exception:
    applog.swallow("unit test: nightly backup", applog.ERROR)

body = read_log()
check("swallow() records the context", "unit test: nightly backup" in body)
check("swallow() records the traceback",
      "ValueError: simulated backup failure" in body and "Traceback" in body)

# ── sys.excepthook ──────────────────────────────────────────────────
try:
    raise RuntimeError("simulated fatal")
except Exception:
    applog._sys_excepthook(*sys.exc_info())
check("sys.excepthook logs + dialogs once",
      "simulated fatal" in read_log() and ("RuntimeError", True) in _dialogs)

# ── The one that matters: exceptions inside Tk callbacks ────────────
import tkinter as tk
import customtkinter as ctk

root = ctk.CTk()
root.geometry("300x200+4000+4000")      # parked offscreen, still viewable
root.update()

check("tk.Tk.report_callback_exception is ours",
      tk.Tk.report_callback_exception.__name__ == "report_callback_exception")


def boom(_event=None):
    raise KeyError("button callback exploded")


# Two traps to avoid here:
#   * CTkButton.invoke() calls the command directly, so it never reaches Tk's
#     CallWrapper and would not exercise the hook at all.
#   * CTkButton is a composite (canvas + label), so bind() on the wrapper and
#     event_generate() on the wrapper do not necessarily meet.
# The thing under test is Tk's callback dispatcher, so bind a plain Tk widget
# and dispatch a real event at it. The window is parked offscreen rather than
# withdrawn because event_generate(when="now") only delivers to a viewable
# widget.
btn = tk.Frame(root, width=40, height=20)
btn.pack()
btn.bind("<Button-1>", boom)
root.update()


def click():
    before = len(read_log())
    btn.event_generate("<Button-1>", when="now")
    root.update()
    return read_log()[before:]


fresh = click()
check("button callback exception is logged",
      "button callback exploded" in fresh)
check("app survives a failing button callback", bool(root.winfo_exists()))
check("callback exception raised a dialog",
      any(n == "KeyError" for n, _ in _dialogs))
check("callback exception is reported as non-fatal",
      ("KeyError", False) in _dialogs)


# after() ticks are how the clock, the debounce and the daily backup run.
def tick_boom():
    raise ZeroDivisionError("after tick exploded")


before = len(read_log())
root.after(1, tick_boom)
logged = wait_for(lambda: "after tick exploded" in read_log()[before:],
                  tick=root.update)
check("after() tick exception is logged", logged)

# ── A repeating fault must log every time, interrupt once ───────────
# Drain any timer still in flight, so a late tick cannot be counted as one of
# the five clicks below.
wait_for(lambda: False, timeout=0.2, tick=root.update)

dialogs_before = len(_dialogs)
# Count log RECORDS, not string matches: a traceback echoes the offending
# source line, so the message itself appears twice per occurrence.
occurrences = sum(click().count("Unhandled exception (ui callback)")
                  for _ in range(5))
check("a repeating fault is logged every time", occurrences == 5, f"got {occurrences}")
check("a repeating fault interrupts the user only once",
      len(_dialogs) == dialogs_before)

# Hard ceiling, independent of how many distinct faults appear.
for i in range(10):
    try:
        raise IndexError(f"distinct fault {i}")
    except Exception:
        applog._report(*sys.exc_info(), origin="test", fatal=False)
check("dialogs are capped per session",
      len(_dialogs) <= applog._MAX_DIALOGS + 2, f"{len(_dialogs)} dialogs")

# ── Re-entrancy: a crash inside the crash reporter must not recurse ─
applog._in_handler = True
try:
    raise RuntimeError("should be ignored while handling")
except Exception:
    applog._report(*sys.exc_info(), origin="test", fatal=False)
applog._in_handler = False
check("re-entrant report is dropped, not recursed",
      "should be ignored while handling" not in read_log())

# ── What the shopkeeper sends ───────────────────────────────────────
count, last = applog.problem_summary()
check("problem_summary() counts this session", count > 0 and last is not None)

diag = applog.diagnostics_text(db_path="", extra={"language": "Bengali"})
check("diagnostics names the log file", applog.log_file() in diag)
check("diagnostics lists recent problems", "problem(s) this session" in diag)
check("diagnostics carries the extra fields", "Bengali" in diag)
check("diagnostics is pasteable in one message", len(diag) < 20000,
      f"{len(diag)} chars")

root.destroy()

# ── Cleanup ─────────────────────────────────────────────────────────
for h in list(applog.log.handlers):
    try:
        h.close()
    except Exception:
        pass
    applog.log.removeHandler(h)
shutil.rmtree(TMP, ignore_errors=True)

print("-" * 64)
print(f"  {len(PASS)} passed  |  {len(FAIL)} failed  |  {len(PASS) + len(FAIL)} total")
print("=" * 64)
sys.exit(1 if FAIL else 0)

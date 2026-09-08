"""
applog.py — the app's black box recorder.

Three kinds of failure used to leave a shop with nothing to send back:

  1. **The window never appears.** An exception before `mainloop()` — a missing
     PyInstaller `hiddenimport` is the classic — kills the process with no
     message at all.
  2. **A button quietly stops working.** Tk catches every exception raised
     inside a widget callback and prints it to `sys.stderr`. This app is built
     with `console=False`, so in the installed `.exe` `sys.stderr` is `None`,
     and `print(file=None)` is a silent no-op. Those tracebacks went to
     literally nowhere. This is where most real crashes land, because almost
     everything in a Tk app runs inside a callback or an `after()` tick.
  3. **Something just doesn't happen.** `except: pass` blocks — including the
     one around the nightly backup — discarded the exception without a trace.

This module makes all three leave evidence in a file the shopkeeper can send.

It is deliberately **stdlib-only and imports no project module at import
time**, so it can be the first import in `main.py` and still record an
ImportError raised by the ones after it.

Usage:

    import applog
    applog.install()                    # first thing in main.py

    try:
        ...
    except Exception:
        applog.swallow("daily auto-backup")   # inside the except block
"""

import logging
import logging.handlers
import os
import sys
import traceback
from collections import deque
from datetime import datetime

# Re-exported so callers can pick a level without importing logging themselves.
DEBUG, INFO, WARNING, ERROR = (logging.DEBUG, logging.INFO,
                               logging.WARNING, logging.ERROR)

LOGGER_NAME = "priya"
_MAX_BYTES = 512 * 1024      # ~0.5 MB per file, 4 files => ~2 MB ceiling
_BACKUP_COUNT = 3
_MAX_DIALOGS = 3             # per session; see _should_dialog()

log = logging.getLogger(LOGGER_NAME)

_installed = False
_in_handler = False          # re-entrancy guard: a crash while reporting a crash
_dialog_count = 0
_seen_signatures = set()
_recent = deque(maxlen=25)   # this session's warnings and errors, for Settings

_log_dir = None
_log_file = None
_language = "English"


# ── Where the log lives ────────────────────────────────────────────
def _base_dir() -> str:
    """The directory the app writes to — same rule config.DB_PATH uses.

    Duplicated rather than imported: this module has to be importable before
    `config` so that a failure inside `config` itself is still recorded.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _resolve_log_dir() -> str:
    """`logs/` next to the database, falling back to LOCALAPPDATA.

    The install directory is writable in the normal case (Setup runs with
    PrivilegesRequired=lowest, so the installing user owns C:\\PriyaStore).
    If it somehow is not — a locked-down machine, a copy run from a read-only
    share — losing the log is the one failure this module cannot report, so it
    retreats to the user profile instead of giving up.
    """
    for candidate in (os.path.join(_base_dir(), "logs"),
                      os.path.join(os.environ.get("LOCALAPPDATA")
                                   or os.path.expanduser("~"),
                                   "PriyaStore", "logs")):
        try:
            os.makedirs(candidate, exist_ok=True)
            probe = os.path.join(candidate, ".writable")
            with open(probe, "w") as fh:
                fh.write("")
            os.remove(probe)
            return candidate
        except Exception:
            continue
    return ""


def log_file() -> str:
    """Absolute path of the current log file ("" if none could be opened)."""
    return _log_file or ""


def log_dir() -> str:
    return _log_dir or ""


def set_language(lang: str):
    """Crash dialogs follow the shop's language. Called on startup and on change."""
    global _language
    _language = lang or "English"


def _t(key: str) -> str:
    """Translate, but never let a broken translation table hide a crash."""
    try:
        from lang import t
        return t(key, _language)
    except Exception:
        return key


# ── Install ────────────────────────────────────────────────────────
def install(version: str = None):
    """Wire up the log file and every exception hook. Safe to call twice."""
    global _installed, _log_dir, _log_file
    if _installed:
        return
    _installed = True

    _log_dir = _resolve_log_dir()
    log.setLevel(logging.DEBUG)
    log.propagate = False

    fmt = logging.Formatter(
        "%(asctime)s  %(levelname)-7s  %(name)s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S")

    if _log_dir:
        _log_file = os.path.join(_log_dir, "priya_store.log")
        try:
            fh = logging.handlers.RotatingFileHandler(
                _log_file, maxBytes=_MAX_BYTES, backupCount=_BACKUP_COUNT,
                encoding="utf-8")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(fmt)
            log.addHandler(fh)
        except Exception:
            _log_file = None

    # Only attach a console handler when there is a console. In the windowed
    # build sys.stderr is None, and StreamHandler(None) writes to sys.stderr
    # at emit time -- which would raise inside logging on every single record.
    if sys.stderr is not None:
        sh = logging.StreamHandler(sys.stderr)
        sh.setLevel(logging.INFO)
        sh.setFormatter(fmt)
        log.addHandler(sh)

    log.addHandler(_RingHandler())

    sys.excepthook = _sys_excepthook
    _install_thread_hook()
    _install_unraisable_hook()
    _install_tk_hook()

    if version is None:
        # Resolved here rather than taken as a required argument so main.py can
        # install the hooks before it imports config -- if config is what
        # breaks, that traceback still lands in the file.
        try:
            from config import APP_VERSION as version
        except Exception:
            version = "?"

    log.info("=" * 68)
    log.info("Priya Store v%s starting  |  python %s  |  frozen=%s",
             version, sys.version.split()[0], bool(getattr(sys, "frozen", False)))
    log.info("log file: %s", _log_file or "(none - could not open)")


class _RingHandler(logging.Handler):
    """Keeps this session's problems in memory so Settings can show them
    without re-reading (and re-parsing) the rotating file."""

    def __init__(self):
        super().__init__(level=logging.WARNING)

    def emit(self, record):
        try:
            _recent.append((datetime.fromtimestamp(record.created),
                            record.levelname,
                            record.getMessage()))
        except Exception:
            pass


# ── Hooks ──────────────────────────────────────────────────────────
def _sys_excepthook(exc_type, exc, tb):
    """Uncaught exception on the main thread — usually fatal."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc, tb)
        return
    _report(exc_type, exc, tb, origin="startup/shutdown", fatal=True)


def _install_thread_hook():
    import threading
    if not hasattr(threading, "excepthook"):
        return

    def hook(args):
        if issubclass(args.exc_type, SystemExit):
            return
        _report(args.exc_type, args.exc_value, args.exc_traceback,
                origin=f"thread {getattr(args.thread, 'name', '?')}",
                fatal=False)

    threading.excepthook = hook


def _install_unraisable_hook():
    """Exceptions inside __del__ / GC — never surfaced, occasionally the only
    sign that a database connection or file handle is being torn down wrong."""
    if not hasattr(sys, "unraisablehook"):
        return

    def hook(args):
        try:
            log.warning("unraisable in %r: %s",
                        args.object,
                        "".join(traceback.format_exception(
                            args.exc_type, args.exc_value, args.exc_traceback)))
        except Exception:
            pass

    sys.unraisablehook = hook


def _install_tk_hook():
    """The important one.

    Tk routes every widget callback and every `after()` tick through
    `CallWrapper.__call__`, which hands exceptions to the root window's
    `report_callback_exception`. The default implementation prints to
    `sys.stderr` -- None in this build. Setting it on the class covers the CTk
    root and every CTkToplevel, since they all resolve to `_root()`.
    """
    try:
        import tkinter as tk
    except Exception:
        return

    def report_callback_exception(self, exc_type, exc, tb):
        _report(exc_type, exc, tb, origin="ui callback", fatal=False)

    tk.Tk.report_callback_exception = report_callback_exception


# ── Reporting ──────────────────────────────────────────────────────
def _signature(exc_type, tb) -> tuple:
    """Identify a fault by where it was raised, so a callback that fails on
    every tick is logged every time but only interrupts the user once."""
    last = ("?", 0)
    try:
        frames = traceback.extract_tb(tb)
        if frames:
            last = (os.path.basename(frames[-1].filename), frames[-1].lineno)
    except Exception:
        pass
    return (getattr(exc_type, "__name__", "?"),) + last


def _report(exc_type, exc, tb, origin: str, fatal: bool):
    global _in_handler
    if _in_handler:
        return                      # a crash inside the crash reporter
    _in_handler = True
    try:
        text = "".join(traceback.format_exception(exc_type, exc, tb))
        log.error("Unhandled exception (%s)\n%s", origin, text)
        for h in log.handlers:
            try:
                h.flush()
            except Exception:
                pass
        if _should_dialog(_signature(exc_type, tb)):
            _show_dialog(exc_type, exc, fatal)
    except Exception:
        pass
    finally:
        _in_handler = False


def _should_dialog(sig) -> bool:
    """A failing `after()` loop would otherwise raise a dialog every tick and
    lock the shopkeeper out of their own till. Log all of them, interrupt once."""
    global _dialog_count
    if sig in _seen_signatures or _dialog_count >= _MAX_DIALOGS:
        return False
    _seen_signatures.add(sig)
    _dialog_count += 1
    return True


def _show_dialog(exc_type, exc, fatal: bool):
    name = getattr(exc_type, "__name__", "Error")
    detail = str(exc).strip()
    body = _t("Something went wrong. Your saved data is safe.")
    if fatal:
        body = _t("The app hit a problem it could not recover from.")
    where = _t("Details were written to the log file:")
    body = (f"{body}\n\n{name}: {detail}\n\n"
            f"{where}\n{_log_file or '(log file unavailable)'}\n\n"
            f"{_t('Settings > Backup > Problem Reports has a Copy Details button.')}")
    title = _t("Priya Store — Problem")

    try:
        from tkinter import messagebox
        messagebox.showerror(title, body)
        return
    except Exception:
        pass
    try:                                    # Tk itself is gone or never started
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, body, title, 0x10)
    except Exception:
        pass


# ── For `except:` blocks that used to be `pass` ────────────────────
def swallow(context: str, level: int = logging.WARNING, exc_info: bool = True):
    """Record the exception currently being handled, then carry on.

    Call from inside an `except` block. Use this wherever continuing really is
    the right behaviour but the failure still matters — a backup that did not
    run, an export that produced nothing, a receipt that never printed.

        except Exception:
            applog.swallow("nightly backup")

    Pass `exc_info=False` for a failure that is *expected* and frequent -- the
    ALTER TABLE migrations raise once per column on every launch after the
    first. It logs a single line with the exception's type and message instead
    of a full traceback, so routine noise cannot push real entries out of the
    rotation.
    """
    try:
        if exc_info:
            log.log(level, "handled failure: %s", context, exc_info=True)
        else:
            exc = sys.exc_info()[1]
            log.log(level, "handled failure: %s -- %s: %s", context,
                    type(exc).__name__ if exc else "?", exc)
    except Exception:
        pass


# ── What the shopkeeper sends you ──────────────────────────────────
def problem_summary():
    """(count, last_datetime_or_None) for warnings+ seen this session."""
    if not _recent:
        return 0, None
    return len(_recent), _recent[-1][0]


def diagnostics_text(db_path: str = "", extra: dict = None) -> str:
    """A single block of text to paste into WhatsApp.

    It reads nothing from the database beyond its file size, so it carries no
    bills, customers or prices of its own accord. The one caveat worth knowing
    before telling a shopkeeper this is safe to send: a traceback quotes the
    exception's own message, so a failure raised *about* a specific record
    ("no such customer: Ramesh") will carry that fragment with it.
    """
    import platform
    lines = ["Priya Store — problem report",
             f"generated : {datetime.now():%Y-%m-%d %H:%M:%S}"]
    try:
        from config import APP_VERSION
        lines.append(f"version   : {APP_VERSION}")
    except Exception:
        pass
    lines += [
        f"python    : {sys.version.split()[0]}",
        f"windows   : {platform.platform()}",
        f"installed : {'exe' if getattr(sys, 'frozen', False) else 'source'}",
        f"log file  : {_log_file or '(none)'}",
    ]
    if db_path:
        try:
            size = os.path.getsize(db_path)
            lines.append(f"database  : {size / 1048576:.1f} MB")
        except Exception:
            lines.append("database  : (not readable)")
    for k, v in (extra or {}).items():
        lines.append(f"{k:<10}: {v}")

    lines.append("")
    if _recent:
        lines.append(f"--- {len(_recent)} problem(s) this session ---")
        for when, level, msg in _recent:
            lines.append(f"{when:%H:%M:%S} {level:<7} {msg.splitlines()[0][:160]}")
    else:
        lines.append("--- no problems recorded this session ---")

    tail = _log_tail(80)
    if tail:
        lines += ["", "--- end of log file ---", tail]
    return "\n".join(lines)


def _log_tail(n: int) -> str:
    if not _log_file or not os.path.isfile(_log_file):
        return ""
    try:
        with open(_log_file, "r", encoding="utf-8", errors="replace") as fh:
            return "".join(fh.readlines()[-n:]).rstrip()
    except Exception:
        return ""


def open_log_folder() -> bool:
    """Open the log folder in Explorer. False if there is nothing to open."""
    if not _log_dir or not os.path.isdir(_log_dir):
        return False
    try:
        os.startfile(_log_dir)               # noqa: S606 - Windows only, no shell
        return True
    except Exception:
        swallow("open log folder")
        return False

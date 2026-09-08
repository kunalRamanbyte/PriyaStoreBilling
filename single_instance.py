"""
single_instance.py — one till per database.

Nothing stopped a second copy of the app opening on the same
`billing_data.db`. Ordinary billing survives that: WAL lets several processes
share the file, and `save_bill()` claims its document number inside
`BEGIN IMMEDIATE`, so two copies still cannot mint the same bill number.

What does not survive it:

  * **Restore and Factory Reset.** Both overwrite `billing_data.db` and delete
    the `-wal`/`-shm` sidecars while the other process still holds the file
    open with cached pages.
  * **Backups that look complete and are not.** `_run_backup()` copies only the
    `.db`, never the `-wal`. Within one process that is safe, because the copy
    runs on the UI thread and nothing else there can be writing. With two, the
    other copy can commit into the WAL mid-copy and those bills are simply
    absent from the backup file.
  * **Two daily backup schedulers**, each pruning to the 10 most recent, so the
    retained history covers half the intended span.

The guard is keyed to the **database path**, not to the application, because
the shared resource is the file. That deliberately lets a developer run from
source while the installed build is open — they point at different databases
and cannot interfere.

A Windows named mutex is used rather than a lock file: the OS drops it when
the process dies, so a crash cannot strand a stale lock that blocks the till
from ever starting again. That failure would be worse than the one being
fixed, which is why this must never be reimplemented with a file.
"""

import ctypes
import hashlib
import os
import sys

_ERROR_ALREADY_EXISTS = 183

# Held for the lifetime of the process. Windows releases the mutex when the
# handle closes, which happens automatically on exit -- including a crash.
_handle = None


def mutex_name(db_path: str) -> str:
    """A stable, per-database name.

    Windows mutex names may not contain a backslash, and paths are
    case-insensitive, so the path is normalised and hashed rather than used
    directly.
    """
    key = os.path.abspath(db_path).lower().encode("utf-8")
    return "PriyaStore.SingleInstance." + hashlib.sha256(key).hexdigest()[:16]


def acquire(db_path: str) -> bool:
    """True if this process may open `db_path`; False if another already has it.

    Never returns False when the answer is unknown. Refusing to start a till
    because the guard itself misbehaved would be a far worse outcome than the
    duplicate it exists to prevent.
    """
    global _handle
    if not sys.platform.startswith("win"):
        return True
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateMutexW.restype = ctypes.c_void_p
        kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_int,
                                          ctypes.c_wchar_p]
        handle = kernel32.CreateMutexW(None, 0, mutex_name(db_path))
        err = ctypes.get_last_error()
        if not handle:
            return True
        if err == _ERROR_ALREADY_EXISTS:
            kernel32.CloseHandle(ctypes.c_void_p(handle))
            return False
        _handle = handle
        return True
    except Exception:
        return True


def release():
    """Drop the claim. Only needed by tests -- exit does this on its own."""
    global _handle
    if _handle is None:
        return
    try:
        ctypes.WinDLL("kernel32").CloseHandle(ctypes.c_void_p(_handle))
    except Exception:
        pass
    _handle = None


def focus_existing(title: str) -> bool:
    """Raise the already-running window, so the second click does what the
    person meant: show me the till.

    Matched on the exact window title, which `main.py` builds from constants
    and never changes at runtime. Returns False if no such window was found,
    so the caller can say something instead of exiting silently.
    """
    if not sys.platform.startswith("win"):
        return False
    try:
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        user32.FindWindowW.restype = ctypes.c_void_p
        user32.FindWindowW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p]
        hwnd = user32.FindWindowW(None, title)
        if not hwnd:
            return False
        SW_RESTORE = 9
        user32.ShowWindow(ctypes.c_void_p(hwnd), SW_RESTORE)
        user32.SetForegroundWindow(ctypes.c_void_p(hwnd))
        return True
    except Exception:
        return False

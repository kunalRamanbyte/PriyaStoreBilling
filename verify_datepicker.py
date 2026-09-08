"""
verify_datepicker.py — the stdlib date picker, and the licence audit behind it.

Run:  python verify_datepicker.py     (exit 0 on all pass, 1 on any failure)

`ui_utils.open_date_picker` used to be a thin wrapper around **tkcalendar**,
which is **GPLv3** — linking it into a closed-source binary would have forced
the whole app under the GPL. It also pulled in **babel** purely to name
weekdays, costing 31 MB in the built app against tkcalendar's own 108 KB.

Two things are checked here:

1. **Behaviour** — the replacement honours the exact contract the two call
   sites (Products, Purchase/GRN) rely on: parse the StringVar as an ISO date,
   write an ISO date on Select, write "" on Clear, leave it untouched on
   Cancel. Nothing tested the picker at all before; `verify_screens.py` builds
   the screens but never opens the popup.
2. **Licensing** — no copyleft package is reachable from the app's imports,
   and tkcalendar/babel are not pulled in even after the picker has run.

Headless: the root window is parked offscreen but left viewable, because
`invoke()` and focus both need a mapped widget.
"""

import os
import sys
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

import tkinter as tk
import customtkinter as ctk

import applog
applog.install(version="test")
sys.excepthook = sys.__excepthook__      # keep real bugs in this script visible

from ui_utils import open_date_picker
from lang import t

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f" {'PASS' if cond else 'FAIL'}  {name}" + (f"  -- {detail}" if detail and not cond else ""))


def walk(w, out=None):
    out = [] if out is None else out
    for c in w.winfo_children():
        out.append(c)
        walk(c, out)
    return out


def buttons(dlg):
    return [b for b in walk(dlg) if isinstance(b, ctk.CTkButton)]


def by_text(dlg, text):
    for b in buttons(dlg):
        try:
            if b.cget("text") == text:
                return b
        except Exception:
            pass
    return None


def labels(dlg):
    out = []
    for w in walk(dlg):
        if isinstance(w, ctk.CTkLabel):
            try:
                out.append(w.cget("text"))
            except Exception:
                pass
    return out


print("=" * 68)
print("  date picker + licence verification")
print("=" * 68)

root = ctk.CTk()
root.geometry("900x600+4000+4000")       # offscreen, still viewable
root.update()


def pump(n=6):
    for _ in range(n):
        root.update_idletasks()
        root.update()


def open_at(value, lang="English"):
    var = tk.StringVar(value=value)
    dlg = open_date_picker(root, var, "Test", lang)
    pump()
    return var, dlg


def focused(dlg, timeout=3.0):
    """Wait until the dialog is mapped, then put Tk's focus on it.

    Key events go to the focus widget, so generating one before that silently
    tests nothing. Two deliberate choices here:

    * The wait is on `winfo_viewable()`, which is the condition the picker's
      own `_make_modal()` polls for, and is purely about this application.
    * The assertion is NOT `focus_get() is dlg`. `focus_get()` returns None
      whenever the *process* is not the foreground OS window, so gating on it
      made this suite pass or fail according to what else was on the desktop.
      `focus_set()` is Tk-internal and needs no foreground status.
    """
    import time
    end = time.time() + timeout
    while time.time() < end and not dlg.winfo_viewable():
        root.update_idletasks()
        root.update()
        time.sleep(0.02)
    if dlg.winfo_viewable():
        dlg.focus_set()
        pump(3)
    return bool(dlg.winfo_viewable())


def close(dlg):
    try:
        dlg.grab_release()
    except Exception:
        pass
    try:
        dlg.destroy()
    except Exception:
        pass
    pump(2)


# ── Contract: the two call sites depend on exactly this ─────────────
var, dlg = open_at("2024-02-29")
check("opens on the month held in the variable",
      any("2024" in s and t("February") in s for s in labels(dlg)),
      str([s for s in labels(dlg) if "2024" in s]))
check("a leap day is rendered", by_text(dlg, "29") is not None)

by_text(dlg, "15").invoke()
pump()
by_text(dlg, t("Select")).invoke()
pump()
check("Select writes an ISO date", var.get() == "2024-02-15", var.get())
check("Select closes the dialog", not dlg.winfo_exists())

var, dlg = open_at("2024-02-29")
by_text(dlg, t("Clear")).invoke()
pump()
check("Clear empties the variable", var.get() == "", repr(var.get()))

var, dlg = open_at("2024-02-29")
by_text(dlg, t("Cancel")).invoke()
pump()
check("Cancel leaves the variable untouched", var.get() == "2024-02-29", var.get())

# ── Falling back to today ───────────────────────────────────────────
today = date.today()
for label, value in (("empty", ""), ("unparseable", "not-a-date")):
    var, dlg = open_at(value)
    check(f"{label} value falls back to today",
          any(t(today.strftime("%B")) in s and str(today.year) in s
              for s in labels(dlg)),
          str(labels(dlg)[:3]))
    by_text(dlg, t("Select")).invoke()
    pump()
    check(f"{label} value then selects today",
          var.get() == today.isoformat(), var.get())

# ── Navigation ──────────────────────────────────────────────────────
var, dlg = open_at("2024-02-29")
by_text(dlg, "›").invoke()          # next month
pump()
check("next month advances to March",
      any(t("March") in s and "2024" in s for s in labels(dlg)))
by_text(dlg, "‹").invoke()
by_text(dlg, "‹").invoke()          # back two -> January
pump()
check("previous month steps back",
      any(t("January") in s and "2024" in s for s in labels(dlg)))
by_text(dlg, "»").invoke()          # next year
pump()
check("year jump moves a whole year",
      any(t("January") in s and "2025" in s for s in labels(dlg)))
by_text(dlg, "«").invoke()
by_text(dlg, "«").invoke()
pump()
check("year jump works backwards",
      any(t("January") in s and "2023" in s for s in labels(dlg)))

# December -> January must roll the year, not produce month 13.
close(dlg)
var, dlg = open_at("2024-12-10")
by_text(dlg, "›").invoke()
pump()
check("December rolls forward into next January",
      any(t("January") in s and "2025" in s for s in labels(dlg)),
      str([s for s in labels(dlg) if "20" in s]))
by_text(dlg, "‹").invoke()
pump()
check("January rolls back into December",
      any(t("December") in s and "2024" in s for s in labels(dlg)))
close(dlg)

# ── Expiry dates are years out: the year control must reach them ────
var, dlg = open_at(date(today.year, 1, 15).isoformat())
for _ in range(3):
    by_text(dlg, "»").invoke()
pump()
by_text(dlg, "15").invoke()
by_text(dlg, t("Select")).invoke()
pump()
check("three year-jumps reach a far-future expiry",
      var.get() == date(today.year + 3, 1, 15).isoformat(), var.get())

# ── Weekday header, Sunday-first as a counter in India expects ──────
var, dlg = open_at("2024-02-29")
heads = [s for s in labels(dlg) if s in
         [t(d).upper() for d in ("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat")]]
check("seven weekday headers are drawn", len(heads) == 7, str(heads))
check("the week starts on Sunday", heads[:1] == [t("Sun").upper()], str(heads[:2]))
close(dlg)

# ── The i18n fix: tkcalendar always drew English ────────────────────
var, dlg = open_at("2024-02-29", lang="Bengali")
bn_month = t("February", "Bengali")
check("month name is translated", any(bn_month in s for s in labels(dlg)),
      str([s for s in labels(dlg) if "2024" in s]))
check("buttons are translated",
      by_text(dlg, t("Select", "Bengali")) is not None)
check("Bengali strings are really Bengali",
      any(ord(c) > 127 for c in bn_month), bn_month)
close(dlg)

var, dlg = open_at("2024-02-29", lang="Hindi")
check("Hindi month name is translated",
      any(t("February", "Hindi") in s for s in labels(dlg)))
close(dlg)

# ── Keyboard ────────────────────────────────────────────────────────
# These were entirely dead until the dialog was made to wait for the window
# to map before taking focus: Tk routes key events to the focus widget, and
# focus_force() on an unmapped window does not stick.
var, dlg = open_at("2024-02-29")
check("the dialog maps and can take focus", focused(dlg))
dlg.event_generate("<Escape>", when="now")
pump()
check("Escape closes without writing",
      not dlg.winfo_exists() and var.get() == "2024-02-29", var.get())

var, dlg = open_at("2024-02-15")
focused(dlg)
dlg.event_generate("<Return>", when="now")
pump()
check("Return selects the highlighted day",
      not dlg.winfo_exists() and var.get() == "2024-02-15", var.get())

var, dlg = open_at("2024-02-15")
focused(dlg)
dlg.event_generate("<Right>", when="now")
dlg.event_generate("<Down>", when="now")      # +1 day, then +7
pump()
dlg.event_generate("<Return>", when="now")
pump()
check("arrow keys move the selection by day and week",
      var.get() == "2024-02-23", var.get())

# Arrowing past the end of the month must carry into the next one.
var, dlg = open_at("2024-02-29")
focused(dlg)
dlg.event_generate("<Right>", when="now")
pump()
check("arrowing off the end of February lands in March",
      any(t("March") in s and "2024" in s for s in labels(dlg)),
      str([s for s in labels(dlg) if "2024" in s]))
dlg.event_generate("<Return>", when="now")
pump()
check("the carried-over date is written correctly",
      var.get() == "2024-03-01", var.get())

root.destroy()

# ── Licensing ───────────────────────────────────────────────────────
print("-" * 68)
check("tkcalendar was never imported", "tkcalendar" not in sys.modules)
check("babel was never imported", "babel" not in sys.modules)

for f in ("requirements.txt", "PriyaStore.spec"):
    with open(f, encoding="utf-8") as fh:
        body = fh.read()
    check(f"{f} no longer requires tkcalendar", "tkcalendar" not in body)

# ── Every dependency, transitively, must be non-copyleft ────────────
# The first version of this audit had two holes that are exactly how a GPL
# package slips in unnoticed:
#   * it skipped any distribution it could not resolve (which silently
#     excluded opencv, the single largest thing in the bundle), and
#   * it only read the legacy "License" field, so packages declaring
#     PEP 639 "License-Expression" (Pillow, numpy) passed as unverified.
# Both are now failures rather than omissions.
import importlib.metadata as md
import re

# Same import name, different distribution name depending on which build is
# installed; either satisfies the requirement.
ALIASES = {"opencv-contrib-python": ("opencv-contrib-python", "opencv-python")}
COPYLEFT = ("gpl", "agpl", "lgpl", "copyleft", "eupl", "mozilla public", "mpl-",
            "cddl", "epl-", "osl-", "sleepycat")
PERMISSIVE_HINTS = ("mit", "bsd", "apache", "psf", "python software",
                    "zlib", "isc", "cc0", "unlicense", "0bsd", "postgresql",
                    "historical permission", "public domain")


def base_name(spec):
    return re.split(r"[<>=!~;\[\s]", spec.strip(), 1)[0].strip()


def resolve(name):
    for cand in ALIASES.get(name, (name,)):
        try:
            return md.distribution(cand)
        except Exception:
            continue
    return None


def licence_of(dist):
    m = dist.metadata
    parts = [m.get("License-Expression") or "", m.get("License") or ""]
    parts += [c for c in (m.get_all("Classifier") or []) if "License" in c]
    return " ".join(p for p in parts if p).strip()


declared = [base_name(l) for l in open("requirements.txt", encoding="utf-8")
            if l.strip() and not l.strip().startswith("#")]

# Walk the transitive closure, ignoring optional "extra ==" requirements.
seen, queue, unresolved = {}, list(declared), []
while queue:
    name = queue.pop()
    key = name.lower().replace("_", "-")
    if key in seen:
        continue
    dist = resolve(name)
    if dist is None:
        unresolved.append(name)
        seen[key] = None
        continue
    seen[key] = dist
    for req in (dist.requires or []):
        if "extra ==" in req:
            continue
        queue.append(base_name(req))

check(f"every declared dependency resolves ({len(declared)} declared)",
      not unresolved, str(unresolved))

unknown, copyleft = [], []
for key, dist in sorted(seen.items()):
    if dist is None:
        continue
    lic = licence_of(dist)
    low = lic.lower()
    if any(k in low for k in COPYLEFT):
        copyleft.append((key, lic[:70]))
    elif not any(k in low for k in PERMISSIVE_HINTS):
        unknown.append((key, lic[:70] or "(no licence metadata)"))

check(f"no copyleft licence in the dependency closure ({len(seen)} packages)",
      not copyleft, str(copyleft))
check("every package's licence is identifiable", not unknown, str(unknown))

for key, dist in sorted(seen.items()):
    if dist is not None:
        print(f"        {key:26} {licence_of(dist)[:56]}")

print("-" * 68)
print(f"  {len(PASS)} passed  |  {len(FAIL)} failed  |  {len(PASS) + len(FAIL)} total")
print("=" * 68)
sys.exit(1 if FAIL else 0)

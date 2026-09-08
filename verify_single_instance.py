"""
verify_single_instance.py — one till per database.

Run:  python verify_single_instance.py   (exit 0 on all pass, 1 on any failure)

The claim under test can only be proved across *processes*: a second
`acquire()` inside this interpreter would reuse the handle we already hold and
prove nothing. Every rejection test therefore spawns a real second Python.

Nothing here touches the shop's database — the paths are invented, and only
their names are hashed.
"""

import ast
import io
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

import single_instance

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f" {'PASS' if cond else 'FAIL'}  {name}" + (f"  -- {detail}" if detail and not cond else ""))


def other_process(db_path):
    """Ask a separate interpreter whether it can claim `db_path`."""
    code = (
        "import sys; sys.path.insert(0, r'%s');"
        "import single_instance;"
        "print('YES' if single_instance.acquire(r'%s') else 'NO')"
        % (ROOT, db_path)
    )
    out = subprocess.run([sys.executable, "-c", code], capture_output=True,
                         text=True, timeout=60)
    return out.stdout.strip()


print("=" * 66)
print("  single-instance guard")
print("=" * 66)

DB_A = os.path.join(tempfile.gettempdir(), "priya_a", "billing_data.db")
DB_B = os.path.join(tempfile.gettempdir(), "priya_b", "billing_data.db")

# ── The name ────────────────────────────────────────────────────────
check("the name is stable for one path",
      single_instance.mutex_name(DB_A) == single_instance.mutex_name(DB_A))
check("the name differs per database",
      single_instance.mutex_name(DB_A) != single_instance.mutex_name(DB_B))
check("the name ignores case and path form",
      single_instance.mutex_name(DB_A.upper())
      == single_instance.mutex_name(DB_A.lower()))
check("the name carries no backslash (Windows forbids it in mutex names)",
      "\\" not in single_instance.mutex_name(DB_A),
      single_instance.mutex_name(DB_A))

# ── The guard ───────────────────────────────────────────────────────
check("the first copy may start", single_instance.acquire(DB_A) is True)

check("a second copy on the SAME database is refused",
      other_process(DB_A) == "NO", other_process(DB_A))

check("a copy on a DIFFERENT database still starts",
      other_process(DB_B) == "YES",
      "dev-from-source must not be blocked by the installed build")

# ── Release ─────────────────────────────────────────────────────────
single_instance.release()
check("the claim is dropped when the owner goes away",
      other_process(DB_A) == "YES",
      "a crashed till must not lock the shop out of its own software")

# A second acquire in this process must not corrupt the handle bookkeeping.
check("re-acquiring after release works", single_instance.acquire(DB_A) is True)
single_instance.release()

# ── Wiring: the guard must not fire during tests or imports ─────────
src = io.open(os.path.join(ROOT, "main.py"), encoding="utf-8").read()
tree = ast.parse(src)

main_block = None
for node in tree.body:
    if (isinstance(node, ast.If)
            and isinstance(node.test, ast.Compare)
            and getattr(node.test.left, "id", "") == "__name__"):
        main_block = node

check("main.py has a __main__ block", main_block is not None)

calls_in_main, calls_anywhere = [], []
for node in ast.walk(tree):
    if isinstance(node, ast.Attribute) and node.attr == "acquire":
        calls_anywhere.append(node.lineno)
if main_block is not None:
    for node in ast.walk(main_block):
        if isinstance(node, ast.Attribute) and node.attr == "acquire":
            calls_in_main.append(node.lineno)

check("main.py claims the database", bool(calls_anywhere))
check("the claim happens ONLY inside __main__",
      calls_anywhere and calls_in_main == calls_anywhere,
      f"found at {calls_anywhere}, inside __main__ {calls_in_main}")

# Importing main must therefore be free of side effects -- every other verify
# script builds BillingApp directly and would break otherwise.
probe = subprocess.run(
    [sys.executable, "-c",
     f"import sys; sys.path.insert(0, r'{ROOT}');"
     "import single_instance, main;"
     "print('CLEAN' if single_instance._handle is None else 'CLAIMED')"],
    capture_output=True, text=True, timeout=180)
check("importing main.py claims nothing",
      probe.stdout.strip() == "CLEAN",
      probe.stdout.strip() + probe.stderr.strip()[-200:])

print("-" * 66)
print(f"  {len(PASS)} passed  |  {len(FAIL)} failed  |  {len(PASS) + len(FAIL)} total")
print("=" * 66)
sys.exit(1 if FAIL else 0)

"""
verify_auth.py — logging in, and the password format behind it.

Run:  python verify_auth.py   (exit 0 on all pass, 1 on any failure)

Passwords are salted PBKDF2-HMAC-SHA256, stored as
`pbkdf2_sha256$iters$salt$hash`. `authenticate()` also accepts a legacy bare
SHA-256 hash and transparently re-hashes it to PBKDF2 on a successful login.
None of that had a test.

The case that prompted this file: `hmac.compare_digest` raises `TypeError` on a
`str` containing non-ASCII, and the legacy comparison sat **outside** the
`try/except` that guards the PBKDF2 branch. A corrupted or hand-edited
`password_hash` therefore propagated out of `authenticate()` into the login
handler, and nobody could log in — with no route back from inside the app. A
malformed hash must fail that one login, not the whole till.

The legacy checks here are not decoration: they pin the behaviour that the
fix's `try/except` sits on top of, so a future tightening of that branch cannot
silently stop upgrading old hashes.

Nothing here touches the shop's database — it builds a throwaway one in the
temp directory.
"""

import hashlib
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

from database import Database, hash_password, verify_password, is_legacy_hash

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f" {'PASS' if cond else 'FAIL'}  {name}" + (f"  -- {detail}" if detail and not cond else ""))


def stored_hash(db, username):
    with db.get_conn() as conn:
        r = conn.execute("SELECT password_hash FROM users WHERE username=?",
                         (username,)).fetchone()
    return r["password_hash"] if r else None


def set_hash(db, username, value):
    with db.get_conn() as conn:
        conn.execute("UPDATE users SET password_hash=? WHERE username=?",
                     (value, username))


print("=" * 66)
print("  authentication")
print("=" * 66)

tmpdir = tempfile.mkdtemp(prefix="priya_auth_")
db = Database()
db.db_path = os.path.join(tmpdir, "billing_data.db")

try:
    db.init_db()

    # ── The stored format ────────────────────────────────────────────
    h = stored_hash(db, "admin")
    parts = (h or "").split("$")
    check("the seeded password is stored as PBKDF2, not plaintext or SHA-256",
          len(parts) == 4 and parts[0] == "pbkdf2_sha256", f"stored {h!r}")
    check("the iteration count is 200k",
          len(parts) == 4 and parts[1] == "200000",
          f"iterations = {parts[1] if len(parts) == 4 else '?'}")
    check("each hash is salted differently",
          hash_password("same") != hash_password("same"))

    # ── Ordinary login ───────────────────────────────────────────────
    user = db.authenticate("admin", "admin123")
    check("the right password logs in", user is not None)
    check("the wrong password does not", db.authenticate("admin", "wrong") is None)
    check("an unknown user does not", db.authenticate("nobody", "admin123") is None)
    check("the returned user carries no password hash",
          user is not None and "password_hash" not in user,
          f"keys: {sorted(user) if user else None}")

    # ── A malformed hash must fail the login, not the app ─────────────
    # This is the regression. Before the fix, hmac.compare_digest raised
    # TypeError out of authenticate() and the login screen was unusable.
    for label, bad in (("non-ASCII", "কখগ" + "a" * 60),
                       ("empty", ""),
                       ("truncated", "pbkdf2_sha256$200000$deadbeef"),
                       ("plaintext left in the column", "admin123")):
        set_hash(db, "admin", bad)
        try:
            got = db.authenticate("admin", "admin123")
            raised = None
        except Exception as exc:
            got, raised = "RAISED", exc
        check(f"{label}: the login is refused, not raised",
              raised is None and got is None,
              f"raised {type(raised).__name__}: {raised}" if raised else f"returned {got!r}")

        try:
            vp, vp_raised = verify_password("admin123", bad), None
        except Exception as exc:
            vp, vp_raised = None, exc
        check(f"{label}: verify_password returns False, not an exception",
              vp_raised is None and vp is False,
              f"raised {type(vp_raised).__name__}: {vp_raised}" if vp_raised else f"returned {vp!r}")

    # ── Legacy bare SHA-256 still works, and is upgraded on login ─────
    legacy = hashlib.sha256("legacypass".encode()).hexdigest()
    set_hash(db, "admin", legacy)
    check("a legacy bare SHA-256 hash is recognised as legacy",
          is_legacy_hash(legacy) and not is_legacy_hash(hash_password("x")))
    check("a legacy hash still verifies",
          verify_password("legacypass", legacy) is True)
    check("a legacy hash rejects the wrong password",
          verify_password("wrong", legacy) is False)

    upgraded_user = db.authenticate("admin", "legacypass")
    check("a legacy password logs in", upgraded_user is not None)
    now = stored_hash(db, "admin")
    check("logging in upgrades the legacy hash to PBKDF2",
          now is not None and now.startswith("pbkdf2_sha256$"), f"stored {now!r}")
    check("and the upgraded hash still verifies the same password",
          verify_password("legacypass", now) is True)
    check("logging in again works after the upgrade",
          db.authenticate("admin", "legacypass") is not None)

    # ── The default-admin hint ───────────────────────────────────────
    set_hash(db, "admin", hash_password("admin123"))
    check("the default-password hint is on while admin/admin123 works",
          db.is_default_admin_active() is True)
    set_hash(db, "admin", hash_password("something else"))
    check("and off once the password is changed",
          db.is_default_admin_active() is False)

finally:
    shutil.rmtree(tmpdir, ignore_errors=True)

print("-" * 66)
print(f"  {len(PASS)} passed  |  {len(FAIL)} failed  |  {len(PASS) + len(FAIL)} total")
print("=" * 66)
sys.exit(1 if FAIL else 0)

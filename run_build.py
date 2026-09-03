import subprocess
import sys
import os

# Project directory = wherever this script lives (never a hardcoded path)
project_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_dir)

print("Starting PyInstaller build using PriyaStore.spec...")

# Run PyInstaller using the spec file (retains our customtkinter, reportlab and assets hooks)
result = subprocess.run(
    [sys.executable, '-m', 'PyInstaller', 'PriyaStore.spec', '--noconfirm'],
    cwd=project_dir,
    capture_output=True,
    text=True
)


def seed_fresh_db(dst_db):
    """Create a brand-new, empty database at `dst_db`.

    NEVER copy the live billing_data.db here: the installer packages whatever
    sits in dist/PriyaStore/, so copying it would ship this shop's real bills,
    customer names and phone numbers, udhaar balances and the users table
    (password hashes included) inside every Setup .exe we hand out.
    init_db() creates the schema and seeds the default admin/cashier accounts.
    """
    for suffix in ("", "-wal", "-shm"):
        stale = dst_db + suffix
        if os.path.exists(stale):
            os.remove(stale)

    from database import Database
    db = Database()
    db.db_path = dst_db          # Database() defaults to the live config.DB_PATH
    db.init_db()


# Post-build database seeding
if result.returncode == 0:
    print("PyInstaller build successful! Seeding database and setting up directory...")
    try:
        dst_db = os.path.join(project_dir, "dist", "PriyaStore", "billing_data.db")
        seed_fresh_db(dst_db)
        print(f"Seeded a fresh empty database at {dst_db}")

        # Create backups directory inside build folder
        backups_dir = os.path.join(project_dir, "dist", "PriyaStore", "backups")
        os.makedirs(backups_dir, exist_ok=True)
        print("Created backups folder in dist.")
    except Exception as e:
        print("Error during post-build setup:", e)
else:
    print("Error: PyInstaller build failed!")

# Write logs and done flag
with open(os.path.join(project_dir, 'build_log.txt'), 'w', encoding='utf-8') as f:
    f.write(result.stdout[-10000:] + '\n\n--- STDERR ---\n\n' + result.stderr[-5000:])

with open(os.path.join(project_dir, 'build_done.txt'), 'w', encoding='utf-8') as f:
    f.write(str(result.returncode))

print("Build process complete. Return code written to build_done.txt.")

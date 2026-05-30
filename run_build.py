import subprocess
import sys
import os
import shutil

# Change to the project directory
project_dir = r'C:\Users\Admin\Desktop\billing'
os.chdir(project_dir)

print("Starting PyInstaller build using PriyaStore.spec...")

# Run PyInstaller using the spec file (retains our customtkinter, reportlab and assets hooks)
result = subprocess.run(
    [sys.executable, '-m', 'PyInstaller', 'PriyaStore.spec', '--noconfirm'],
    cwd=project_dir,
    capture_output=True,
    text=True
)

# Post-build copying of database
if result.returncode == 0:
    print("PyInstaller build successful! Copying database and setting up directory...")
    try:
        # Copy the pre-populated database file next to PriyaStore.exe
        src_db = os.path.join(project_dir, "billing_data.db")
        dst_db = os.path.join(project_dir, "dist", "PriyaStore", "billing_data.db")
        if os.path.exists(src_db):
            shutil.copy2(src_db, dst_db)
            print(f"Copied {src_db} to {dst_db}")
        else:
            print("Warning: billing_data.db not found in root folder to copy.")
            
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

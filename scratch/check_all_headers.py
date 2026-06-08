import re
import os

workspace = r"c:\Users\Admin\Desktop\billing"
for f_name in os.listdir(workspace):
    if not f_name.endswith(".py") or not f_name.startswith("screen_"):
        continue
    f_path = os.path.join(workspace, f_name)
    with open(f_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    
    # Search for headings/columns definitions
    lines = content.splitlines()
    for idx, line in enumerate(lines, 1):
        if "heads =" in line or "heads  =" in line or "tree.heading" in line:
            print(f"{f_name}:{idx}: {ascii(line)}")

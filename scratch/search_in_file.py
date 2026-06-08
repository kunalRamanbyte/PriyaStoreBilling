with open(r"c:\Users\Admin\Desktop\billing\screen_users.py", "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

lines = content.splitlines()
for idx, line in enumerate(lines, 1):
    if "cols" in line or "heading" in line or "tree" in line.lower():
        print(f"{idx}: {ascii(line)}")

with open(r"c:\Users\Admin\Desktop\billing\screen_inventory.py", "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

# We want to replace the duplicate lines:
target_old = """        ctk.CTkButton(btn_row, text=t("Cancel", L),
                      font=FONTS["button"], fg_color=COLORS["btn_secondary"],
                      height=52, corner_radius=16,
                      command=dlg.destroy).pack(side="left", width=110)
                      font=FONTS["button"], fg_color=COLORS["btn_secondary"],
                      height=52, corner_radius=16,
                      command=dlg.destroy).pack(side="left", width=110)"""

target_new = """        ctk.CTkButton(btn_row, text=t("Cancel", L),
                      font=FONTS["button"], fg_color=COLORS["btn_secondary"],
                      height=52, corner_radius=16,
                      command=dlg.destroy).pack(side="left", width=110)"""

if target_old in content:
    content = content.replace(target_old, target_new)
    print("Replacement succeeded.")
else:
    print("Error: Target not found.")

with open(r"c:\Users\Admin\Desktop\billing\screen_inventory.py", "w", encoding="utf-8") as f:
    f.write(content)

with open(r"c:\Users\Admin\Desktop\billing\screen_purchase.py", "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

# Let's find def _open_new_product_form
start_idx = content.find("    def _open_new_product_form")
# find where err_lbl.pack(pady=(4, 0), padx=24, anchor="w") ends
end_idx = content.find('err_lbl.pack(pady=(4, 0), padx=24, anchor="w")')

if start_idx != -1 and end_idx != -1:
    actual_segment = content[start_idx:end_idx + len('err_lbl.pack(pady=(4, 0), padx=24, anchor="w")')]
    print("ACTUAL SEGMENT:")
    print(ascii(actual_segment))
else:
    print("Could not find segment.")

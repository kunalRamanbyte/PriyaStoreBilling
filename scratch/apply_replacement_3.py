with open(r"c:\Users\Admin\Desktop\billing\screen_purchase.py", "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

start_marker = "    def _open_new_product_form(self):"
end_marker = '        err_lbl.pack(pady=(4, 0), padx=24, anchor="w")'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("Error: Could not find markers.")
    import sys
    sys.exit(1)

# Segment to replace
target_segment = content[start_idx:end_idx + len(end_marker)]

new_segment = """    def _open_new_product_form(self):
        \"\"\"Open a form to create a brand-new product, save it to the
        Product Master, and immediately add it to the current GRN cart.\"\"\"
        L = self.app.current_lang
        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title(t("Add New Product", L))
        place_popup(dlg, 540, 640)
        dlg.resizable(False, True)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        scroll = ctk.CTkScrollableFrame(dlg, fg_color=COLORS["bg_main"])
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll, text="➕  " + t("Add New Product", L),
                     font=FONTS["heading"], text_color=COLORS["btn_primary"]
                    ).pack(pady=(16, 10), padx=24, anchor="w")

        cats  = self.db.get_categories()
        c_map = {c["name"]: c["category_id"] for c in cats}
        c_names = list(c_map.keys())

        entries = {}

        def field(label, key, default="", placeholder="", wide=False):
            f = ctk.CTkFrame(scroll, fg_color="transparent")
            f.pack(fill="x", padx=24, pady=5)
            ctk.CTkLabel(f, text=label, font=FONTS["label_form"],
                          text_color=COLORS["text_dark"],
                          width=165, anchor="w").pack(side="left")
            var = tk.StringVar(value=str(default) if default not in (None, "") else "")
            ctk.CTkEntry(f, textvariable=var,
                          placeholder_text=placeholder,
                          font=FONTS["input"], height=40,
                          border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"],
                          width=290 if wide else 220
                         ).pack(side="left")
            entries[key] = var
            return var

        def dropdown(label, key, values, default=""):
            f = ctk.CTkFrame(scroll, fg_color="transparent")
            f.pack(fill="x", padx=24, pady=5)
            ctk.CTkLabel(f, text=label, font=FONTS["label_form"],
                          text_color=COLORS["text_dark"],
                          width=165, anchor="w").pack(side="left")
            var = tk.StringVar(value=default if default else (values[0] if values else ""))
            ctk.CTkOptionMenu(f, variable=var, values=values,
                               font=FONTS["input"], height=40, width=220,
                               fg_color=COLORS["btn_primary"], button_color="#005BBE"
                              ).pack(side="left")
            entries[key] = var

        field(t("Product Name *", L),       "name",           "",  t("e.g. Aashirvaad Atta 5kg", L), wide=True)
        field(t("Product Code", L),         "product_code",   "",  t("Auto-generated if blank", L))
        dropdown(t("Category *", L),        "category",       c_names,
                 c_names[0] if c_names else "")
        field(t("Brand", L),                "brand",          "",  t("Optional", L))
        dropdown(t("Unit *", L),            "unit",           UNITS, "piece")
        field(t("Selling Price (₹) *", L),  "selling_price",  "",  t("e.g. 45.50", L))
        field(t("Purchase Price (₹)", L),   "purchase_price", "",  t("For margin calc", L))
        field(t("Current Stock", L),        "current_stock",  "0", t("Quantity in hand", L))
        field(t("Reorder Level", L),        "reorder_level",  "5", t("Alert threshold", L))
        # Expiry date \u2014 entry + calendar button
        exp_f = ctk.CTkFrame(scroll, fg_color="transparent")
        exp_f.pack(fill="x", padx=24, pady=5)
        ctk.CTkLabel(exp_f, text=t("Expiry Date", L), font=FONTS["label_form"],
                     text_color=COLORS["text_dark"],
                     width=165, anchor="w").pack(side="left")
        exp_var = tk.StringVar(value="")
        entries["expiry_date"] = exp_var
        ctk.CTkEntry(exp_f, textvariable=exp_var,
                     placeholder_text=t("Click calendar →", L),
                     font=FONTS["input"], height=40, width=170,
                     border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"]
                    ).pack(side="left", padx=(0, 6))
        ctk.CTkButton(exp_f, text="📅", width=44, height=40,
                      font=("Segoe UI", 18), corner_radius=10,
                      fg_color=COLORS["btn_primary"],
                      command=lambda: open_date_picker(exp_f, exp_var, t("Select Expiry Date", L))
                     ).pack(side="left")

        err_lbl = ctk.CTkLabel(scroll, text="", font=FONTS["small"],
                                text_color=COLORS["btn_danger"])
        err_lbl.pack(pady=(4, 0), padx=24, anchor="w")"""

content = content.replace(target_segment, new_segment)
with open(r"c:\Users\Admin\Desktop\billing\screen_purchase.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Replacement 3 succeeded successfully.")

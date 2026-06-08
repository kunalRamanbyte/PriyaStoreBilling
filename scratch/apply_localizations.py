import os

# Paths to the target files
lang_file = r"c:\Users\Admin\Desktop\billing\lang.py"
purchase_file = r"c:\Users\Admin\Desktop\billing\screen_purchase.py"
inventory_file = r"c:\Users\Admin\Desktop\billing\screen_inventory.py"

# ── 1. Modify lang.py ─────────────────────────────────────────
with open(lang_file, "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

# To match safely, let's find: "e.g. 10":                  ["e.g. 10", "যেমন: ১০", "जैसे: 10"],
target = '"e.g. 10":                  ["e.g. 10", "যেমন: ১০", "जैसे: 10"],'

new_keys = """
    # Reports
    "Daily Sales":              ["Daily Sales", "ডেইলি সেলস", "डेली सेल्स"],
    "Item-wise Sales":          ["Item-wise Sales", "আইটেম-ওয়াইজ সেলস", "आइटम-वाइज़ सेल्स"],
    "Low Stock Alert":          ["Low Stock Alert", "কম স্টক অ্যালার্ট", "कम स्टॉक अलर्ट"],
    "Purchase / GRN":           ["Purchase / GRN", "পারচেজ / জিআরএন", "परचेज / जीआरएन"],
    "Profit & Margin":          ["Profit & Margin", "প্রফিট ও মার্জিন", "प्रॉफ़िट और मार्जिन"],
    "Stock Valuation":          ["Stock Valuation", "স্টক ভ্যালুয়েশন", "स्टॉक वैल्यूएशन"],
    "Customer Ledger":          ["Customer Ledger", "কাস্টমার লেজার", "ग्राहक लेजर"],
    "Slow-Moving Items":        ["Slow-Moving Items", "স্লো-মুভিং আইটেমস", "स्लो-मूविंग आइटम्स"],
    "#":                        ["#", "#", "#"],
    "Amount \\u20b9":            ["Amount \\u20b9", "টাকা \\u20b9", "रकम \\u20b9"],
    "GRN":                      ["GRN", "জিআরএন", "जीआरএন"],
    "SELECT REPORT":            ["SELECT REPORT", "রিপোর্ট সিলেক্ট করো", "रिपोर्ट सिलेक्ट करें"],
    "openpyxl is required for Excel export.\\n\\n": [
        "openpyxl is required for Excel export.\\n\\n",
        "এক্সেল এক্সপোর্টের জন্য openpyxl লাইব্রেরি প্রয়োজন।\\n\\n",
        "एक्सेल एक्सपोर्ट के लिए openpyxl लाइब्रेरी आवश्यक है।\\n\\n"
    ],
    # Purchase Dialog Elements
    "Add Item":                 ["Add Item", "আইটেম যোগ করো", "आइटम जोड़ें"],
    "Edit Item":                ["Edit Item", "আইটেম এডিট", "आइटम एडिट"],
    "Enter valid quantity and price.": [
        "Enter valid quantity and price.",
        "সঠিক পরিমাণ এবং দাম লিখুন।",
        "सही मात्रा और दाम लिखें।"
    ],
    "Add New Product":          ["Add New Product", "নতুন প্রোডাক্ট", "नया प्रोडक्ट"],
    "e.g. Aashirvaad Atta 5kg": ["e.g. Aashirvaad Atta 5kg", "যেমন: আশির্বাদ আটা ৫ কেজি", "जैसे: आशीर्वाद आटा 5 किलो"],
    "e.g. 45.50":               ["e.g. 45.50", "যেমন: ৪৫.৫০", "जैसे: 45.50"],
    "Product Name is required.": [
        "Product Name is required.",
        "প্রোডাক্টের নাম দিতে হবে।",
        "प्रोडक्ट का नाम देना होगा।"
    ],
    "Prices and stock must be numbers.": [
        "Prices and stock must be numbers.",
        "দাম এবং স্টক অবশ্যই সংখ্যা হতে হবে।",
        "दाम और स्टॉक संख्या होने चाहिए।"
    ],
    "Expiry Date must be YYYY-MM-DD (e.g. 2026-12-31).": [
        "Expiry Date must be YYYY-MM-DD (e.g. 2026-12-31).",
        "মেয়াদ শেষের তারিখ YYYY-MM-DD হতে হবে (যেমন: 2026-12-31)।",
        "एक्सपायरी तारीख YYYY-MM-DD होनी चाहिए (जैसे: 2026-12-31)।"
    ],
    "Product Added":            ["Product Added", "প্রোডাক্ট যোগ করা হয়েছে", "प्रोडक्ट जोड़ा गया"],
    "Product Added Msg": [
        "'{name}' has been added to the Product Master.\\n\\nIt will now be opened for quantity & price entry.",
        "'{name}' প্রোডাক্ট মাস্টারে যোগ করা হয়েছে।\\n\\nএখন এটার পরিমাণ ও দাম এন্ট্রি করা যাবে।",
        "'{name}' प्रोडक्ट मास्टर में जोड़ दिया गया है।\\n\\nअब इसका मात्रा और दाम डाला जा सकता है।"
    ],
    "GRN History":              ["GRN History", "জিআরএন হিস্ট্রি", "जीআরএন  হিস্ট্রি"],
    "GRN Saved \\u2705":         ["GRN Saved \\u2705", "জিআরএন সেভ হয়েছে \\u2705", "जीआरएन सेव हुआ \\u2705"],
    # Inventory Adjustment Reasons
    "New Stock Received":       ["New Stock Received", "নতুন স্টক এসেছে", "नया स्टॉक मिला"],
    "Damaged / Expired":        ["Damaged / Expired", "নষ্ট / মেয়াদ শেষ", "खराब / एक्सपायर"],
    "Theft / Loss":             ["Theft / Loss", "চুরি / ক্ষতি", "चोरी / नुकसान"],
    "Physical Count Correction": ["Physical Count Correction", "স্টক গণনা ঠিক করা", "स्टॉक गिनती सुधार"],
    "Return to Supplier":       ["Return to Supplier", "সাপ্লায়ারকে ফেরত", "सप्लायर को वापसी"],
    "Other":                    ["Other", "অন্যান্য", "अन्य"],
    "Enter a valid positive quantity.": [
        "Enter a valid positive quantity.",
        "সঠিক পজিটিভ পরিমাণ লিখুন।",
        "सही पॉजिटिव मात्रा लिखें।"
    ],
    "Cannot remove more than current stock ({stock}).": [
        "Cannot remove more than current stock ({stock}).",
        "বর্তমান স্টক ({stock}) এর বেশি সরানো যাবে না।",
        "वर्तमान स्टॉक ({stock}) से अधिक नहीं हटा सकते।"
    ],"""

if target in content:
    content = content.replace(target, target + new_keys)
    print("lang.py updated successfully.")
else:
    print("Error: Could not find target in lang.py")

with open(lang_file, "w", encoding="utf-8") as f:
    f.write(content)


# ── 2. Modify screen_purchase.py ─────────────────────────────
with open(purchase_file, "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

# Make the specific replacements
# replacement 1: _edit_item_dialog
old_edit_item = """    def _edit_item_dialog(self, prod=None, new=False):
        if prod is None:
            sel = self.cart_tree.selection()
            if not sel:
                return
            idx = int(sel[0])
            prod_data = self._cart[idx]
            prod = {"product_id": prod_data["product_id"],
                    "name": prod_data["product_name"],
                    "unit": prod_data["unit"],
                    "purchase_price": prod_data["unit_price"]}
        else:
            prod_data = None

        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title("Add Item" if new else "Edit Item")
        place_popup(dlg, 420, 360)
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        ctk.CTkLabel(dlg, text=prod["name"],
                     font=FONTS["subheading"], text_color=COLORS["text_dark"]
                    ).pack(pady=(20, 4), padx=24, anchor="w")
        ctk.CTkLabel(dlg, text=f"Unit: {prod.get('unit','piece')}",
                     font=FONTS["small"], text_color=COLORS["text_muted"]
                    ).pack(anchor="w", padx=24, pady=(0, 16))

        # Qty
        ctk.CTkLabel(dlg, text="Quantity *", font=FONTS["label_form"],
                     text_color=COLORS["text_dark"]).pack(anchor="w", padx=24)
        qty_var = tk.StringVar(value="1" if new else str(prod_data["quantity"]))
        ctk.CTkEntry(dlg, textvariable=qty_var, font=FONTS["input"],
                     height=50, border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"]
                    ).pack(fill="x", padx=24, pady=(4, 14))

        # Buy price
        ctk.CTkLabel(dlg, text="Purchase Price (₹) *", font=FONTS["label_form"],
                     text_color=COLORS["text_dark"]).pack(anchor="w", padx=24)
        buy_default = prod_data["unit_price"] if not new else prod.get("purchase_price", 0)
        price_var = tk.StringVar(value=str(buy_default))
        ctk.CTkEntry(dlg, textvariable=price_var, font=FONTS["input"],
                     height=50, border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"]
                    ).pack(fill="x", padx=24, pady=(4, 6))

        err_lbl = ctk.CTkLabel(dlg, text="", font=FONTS["small"],
                                text_color=COLORS["btn_danger"])
        err_lbl.pack(pady=(0, 6), padx=24, anchor="w")"""

new_edit_item = """    def _edit_item_dialog(self, prod=None, new=False):
        L = self.app.current_lang
        if prod is None:
            sel = self.cart_tree.selection()
            if not sel:
                return
            idx = int(sel[0])
            prod_data = self._cart[idx]
            prod = {"product_id": prod_data["product_id"],
                    "name": prod_data["product_name"],
                    "unit": prod_data["unit"],
                    "purchase_price": prod_data["unit_price"]}
        else:
            prod_data = None

        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title(t("Add Item", L) if new else t("Edit Item", L))
        place_popup(dlg, 420, 360)
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        ctk.CTkLabel(dlg, text=prod["name"],
                     font=FONTS["subheading"], text_color=COLORS["text_dark"]
                    ).pack(pady=(20, 4), padx=24, anchor="w")
        ctk.CTkLabel(dlg, text=f"{t('Unit', L)}: {prod.get('unit','piece')}",
                     font=FONTS["small"], text_color=COLORS["text_muted"]
                    ).pack(anchor="w", padx=24, pady=(0, 16))

        # Qty
        ctk.CTkLabel(dlg, text=t("Quantity *", L), font=FONTS["label_form"],
                     text_color=COLORS["text_dark"]).pack(anchor="w", padx=24)
        qty_var = tk.StringVar(value="1" if new else str(prod_data["quantity"]))
        ctk.CTkEntry(dlg, textvariable=qty_var, font=FONTS["input"],
                     height=50, border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"]
                    ).pack(fill="x", padx=24, pady=(4, 14))

        # Buy price
        ctk.CTkLabel(dlg, text=t("Purchase Price (₹) *", L), font=FONTS["label_form"],
                     text_color=COLORS["text_dark"]).pack(anchor="w", padx=24)
        buy_default = prod_data["unit_price"] if not new else prod.get("purchase_price", 0)
        price_var = tk.StringVar(value=str(buy_default))
        ctk.CTkEntry(dlg, textvariable=price_var, font=FONTS["input"],
                     height=50, border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"]
                    ).pack(fill="x", padx=24, pady=(4, 6))

        err_lbl = ctk.CTkLabel(dlg, text="", font=FONTS["small"],
                                text_color=COLORS["btn_danger"])
        err_lbl.pack(pady=(0, 6), padx=24, anchor="w")"""

# replacement 2: err_lbl inside confirm()
old_err_confirm = '                err_lbl.configure(text="⚠  Enter valid quantity and price.")'
new_err_confirm = '                err_lbl.configure(text="⚠  " + t("Enter valid quantity and price.", L))'

# replacement 3: _open_new_product_form dialog and fields setup
old_new_prod_form = """    def _open_new_product_form(self):
        \"\"\"Open a form to create a brand-new product, save it to the
        Product Master, and immediately add it to the current GRN cart.\"\"\"
        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title("Add New Product")
        place_popup(dlg, 540, 640)
        dlg.resizable(False, True)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        scroll = ctk.CTkScrollableFrame(dlg, fg_color=COLORS["bg_main"])
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll, text="➕  Add New Product",
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

        field("Product Name *",       "name",           "",  "e.g. Aashirvaad Atta 5kg", wide=True)
        field("Product Code",         "product_code",   "",  "Auto-generated if blank")
        dropdown("Category *",        "category",       c_names,
                 c_names[0] if c_names else "")
        field("Brand",                "brand",          "",  "Optional")
        dropdown("Unit *",            "unit",           UNITS, "piece")
        field("Selling Price (₹) *",  "selling_price",  "",  "e.g. 45.50")
        field("Purchase Price (₹)",   "purchase_price", "",  "For margin calc")
        field("Current Stock",        "current_stock",  "0", "Quantity in hand")
        field("Reorder Level",        "reorder_level",  "5", "Alert threshold")
        # Expiry date — entry + calendar button
        exp_f = ctk.CTkFrame(scroll, fg_color="transparent")
        exp_f.pack(fill="x", padx=24, pady=5)
        ctk.CTkLabel(exp_f, text="Expiry Date", font=FONTS["label_form"],
                     text_color=COLORS["text_dark"],
                     width=165, anchor="w").pack(side="left")
        exp_var = tk.StringVar(value="")
        entries["expiry_date"] = exp_var
        ctk.CTkEntry(exp_f, textvariable=exp_var,
                     placeholder_text="Click calendar →",
                     font=FONTS["input"], height=40, width=170,
                     border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"]
                    ).pack(side="left", padx=(0, 6))
        ctk.CTkButton(exp_f, text="📅", width=44, height=40,
                      font=("Segoe UI", 18), corner_radius=10,
                      fg_color=COLORS["btn_primary"],
                      command=lambda: open_date_picker(exp_f, exp_var, "Select Expiry Date")
                     ).pack(side="left")

        err_lbl = ctk.CTkLabel(scroll, text="", font=FONTS["small"],
                                text_color=COLORS["btn_danger"])
        err_lbl.pack(pady=(4, 0), padx=24, anchor="w")"""

new_new_prod_form = """    def _open_new_product_form(self):
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
        # Expiry date — entry + calendar button
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

# replacement 4: validation checks inside _open_new_product_form -> save()
old_valid_new_prod = """            name = entries["name"].get().strip()
            if not name:
                err_lbl.configure(text="⚠  Product Name is required.")
                return
            try:
                sell = float(entries["selling_price"].get() or 0)
                buy  = float(entries["purchase_price"].get() or 0)
                stk  = float(entries["current_stock"].get() or 0)
                ror  = float(entries["reorder_level"].get() or 5)
            except ValueError:
                err_lbl.configure(text="⚠  Prices and stock must be numbers.")
                return

            exp_raw = entries["expiry_date"].get().strip()
            expiry  = None
            if exp_raw:
                try:
                    from datetime import date as _date
                    _date.fromisoformat(exp_raw)
                    expiry = exp_raw
                except ValueError:
                    err_lbl.configure(text="⚠  Expiry Date must be YYYY-MM-DD (e.g. 2026-12-31).")
                    return"""

new_valid_new_prod = """            name = entries["name"].get().strip()
            if not name:
                err_lbl.configure(text="⚠  " + t("Product Name is required.", L))
                return
            try:
                sell = float(entries["selling_price"].get() or 0)
                buy  = float(entries["purchase_price"].get() or 0)
                stk  = float(entries["current_stock"].get() or 0)
                ror  = float(entries["reorder_level"].get() or 5)
            except ValueError:
                err_lbl.configure(text="⚠  " + t("Prices and stock must be numbers.", L))
                return

            exp_raw = entries["expiry_date"].get().strip()
            expiry  = None
            if exp_raw:
                try:
                    from datetime import date as _date
                    _date.fromisoformat(exp_raw)
                    expiry = exp_raw
                except ValueError:
                    err_lbl.configure(text="⚠  " + t("Expiry Date must be YYYY-MM-DD (e.g. 2026-12-31).", L))
                    return"""

# replacement 5: success messagebox inside save()
old_success_new_prod = """            dlg.destroy()
            messagebox.showinfo(
                "Product Added",
                f"'{name}' has been added to the Product Master.\\n\\n"
                "It will now be opened for quantity & price entry.",
                parent=self.winfo_toplevel()
            )"""

new_success_new_prod = """            dlg.destroy()
            messagebox.showinfo(
                t("Product Added", L),
                t("Product Added Msg", L).format(name=name),
                parent=self.winfo_toplevel()
            )"""

# replacement 6: _show_grn_receipt popup
old_grn_receipt = """    def _show_grn_receipt(self, purchase_id):
        p, items = self.db.get_purchase_by_id(purchase_id)
        if not p:
            return

        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title("GRN Saved ✅")
        place_popup(dlg, 520, 520)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        ctk.CTkFrame(dlg, fg_color=COLORS["btn_success"], height=6, corner_radius=0).pack(fill="x")

        scroll = ctk.CTkScrollableFrame(dlg, fg_color=COLORS["bg_card"])
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        ctk.CTkLabel(scroll, text="✅  GRN Saved Successfully!",
                     font=FONTS["subheading"], text_color=COLORS["btn_success"]
                    ).pack(pady=(18, 4), padx=24, anchor="w")
        ctk.CTkLabel(scroll, text=f"GRN Number:  {p['grn_number']}",
                     font=FONTS["body_bold"], text_color=COLORS["text_dark"]
                    ).pack(anchor="w", padx=24)
        ctk.CTkLabel(scroll, text=f"Supplier:  {p['supplier_name']}",
                     font=FONTS["body"], text_color=COLORS["text_muted"]
                    ).pack(anchor="w", padx=24, pady=(2, 16))"""

new_grn_receipt = """    def _show_grn_receipt(self, purchase_id):
        L = self.app.current_lang
        p, items = self.db.get_purchase_by_id(purchase_id)
        if not p:
            return

        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title(t("GRN Saved ✅", L))
        place_popup(dlg, 520, 520)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        ctk.CTkFrame(dlg, fg_color=COLORS["btn_success"], height=6, corner_radius=0).pack(fill="x")

        scroll = ctk.CTkScrollableFrame(dlg, fg_color=COLORS["bg_card"])
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        ctk.CTkLabel(scroll, text="✅  " + t("GRN Saved Successfully!", L),
                     font=FONTS["subheading"], text_color=COLORS["btn_success"]
                    ).pack(pady=(18, 4), padx=24, anchor="w")
        ctk.CTkLabel(scroll, text=f"{t('GRN Number', L)}:  {p['grn_number']}",
                     font=FONTS["body_bold"], text_color=COLORS["text_dark"]
                    ).pack(anchor="w", padx=24)
        ctk.CTkLabel(scroll, text=f"{t('Supplier:', L)}  {p['supplier_name']}",
                     font=FONTS["body"], text_color=COLORS["text_muted"]
                    ).pack(anchor="w", padx=24, pady=(2, 16))"""

# replacement 7: close button in _show_grn_receipt
old_grn_receipt_close = """        ctk.CTkButton(btn_row, text="Close",
                      font=FONTS["button"], fg_color=COLORS["btn_primary"],
                      height=48, corner_radius=16,
                      command=dlg.destroy
                     ).pack(side="left", fill="x", expand=True)"""

new_grn_receipt_close = """        ctk.CTkButton(btn_row, text=t("Close", L),
                      font=FONTS["button"], fg_color=COLORS["btn_primary"],
                      height=48, corner_radius=16,
                      command=dlg.destroy
                     ).pack(side="left", fill="x", expand=True)"""

# replacement 8: _show_grn_history
old_grn_history = """    def _show_grn_history(self):
        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title("GRN History")
        place_popup(dlg, 900, 560)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        # Header + search
        top = ctk.CTkFrame(dlg, fg_color=COLORS["bg_main"], corner_radius=0)
        top.pack(fill="x", padx=12, pady=(12, 4))
        ctk.CTkLabel(top, text="📋   GRN History",
                     font=FONTS["subheading"], text_color=COLORS["text_dark"]
                    ).pack(side="left")

        search_var = tk.StringVar()
        ctk.CTkEntry(top, textvariable=search_var,
                     placeholder_text="Search GRN no. or supplier…",
                     font=FONTS["input"], height=40, width=260,
                     border_color=COLORS["border_focus"], fg_color=COLORS["bg_card"]
                    ).pack(side="right")

        frame = ctk.CTkFrame(dlg, fg_color=COLORS["bg_card"], corner_radius=16)
        frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # ttk styles applied globally via styles.py

        cols   = ("grn", "date", "supplier", "items", "total")
        heads  = ("GRN Number", "Date", "Supplier", "Items", "Total ₹")"""

new_grn_history = """    def _show_grn_history(self):
        L = self.app.current_lang
        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title(t("GRN History", L))
        place_popup(dlg, 900, 560)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        # Header + search
        top = ctk.CTkFrame(dlg, fg_color=COLORS["bg_main"], corner_radius=0)
        top.pack(fill="x", padx=12, pady=(12, 4))
        ctk.CTkLabel(top, text="📋   " + t("GRN History", L),
                     font=FONTS["subheading"], text_color=COLORS["text_dark"]
                    ).pack(side="left")

        search_var = tk.StringVar()
        ctk.CTkEntry(top, textvariable=search_var,
                     placeholder_text=t("Search GRN no. or supplier…", L),
                     font=FONTS["input"], height=40, width=260,
                     border_color=COLORS["border_focus"], fg_color=COLORS["bg_card"]
                    ).pack(side="right")

        frame = ctk.CTkFrame(dlg, fg_color=COLORS["bg_card"], corner_radius=16)
        frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # ttk styles applied globally via styles.py

        cols   = ("grn", "date", "supplier", "items", "total")
        heads  = (t("GRN Number", L), t("Date", L), t("Supplier", L), t("Items", L), t("Total ₹", L))"""


# Apply all screen_purchase.py replacements
replacements_purchase = [
    (old_edit_item, new_edit_item),
    (old_err_confirm, new_err_confirm),
    (old_new_prod_form, new_new_prod_form),
    (old_valid_new_prod, new_valid_new_prod),
    (old_success_new_prod, new_success_new_prod),
    (old_grn_receipt, new_grn_receipt),
    (old_grn_receipt_close, new_grn_receipt_close),
    (old_grn_history, new_grn_history),
]

for idx, (old, new) in enumerate(replacements_purchase, 1):
    if old in content:
        content = content.replace(old, new)
        print(f"screen_purchase.py: Replacement {idx} succeeded.")
    else:
        print(f"screen_purchase.py: Error - Replacement {idx} target not found.")

with open(purchase_file, "w", encoding="utf-8") as f:
    f.write(content)


# ── 3. Modify screen_inventory.py ─────────────────────────────
with open(inventory_file, "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

# Replacement 1: _open_adjustment_dialog
old_adj_dlg = """    def _open_adjustment_dialog(self, product_id=None):
        if not product_id:
            product_id = self._get_selected_pid()
        if not product_id:
            return

        prod = self.db.get_product_by_id(product_id)
        if not prod:
            return

        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title("Adjust Stock")
        place_popup(dlg, 500, 480)
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        # Header
        ctk.CTkFrame(dlg, fg_color=COLORS["btn_warning"], height=6, corner_radius=0).pack(fill="x")
        ctk.CTkLabel(dlg, text="🔧   Adjust Stock",
                     font=FONTS["heading"], text_color=COLORS["text_dark"]
                    ).pack(pady=(18, 4), padx=24, anchor="w")

        # Product info card
        info = ctk.CTkFrame(dlg, fg_color=COLORS["bg_main"], corner_radius=16)
        info.pack(fill="x", padx=24, pady=(0, 16))
        ctk.CTkLabel(info, text=prod["name"],
                     font=FONTS["body_bold"], text_color=COLORS["text_dark"]
                    ).pack(anchor="w", padx=16, pady=(10, 2))
        ctk.CTkLabel(info,
                     text=f"Current Stock:  {prod['current_stock']:.1f}  {prod.get('unit','piece')}   |   "
                          f"Reorder Level: {prod['reorder_level']:.0f}",
                     font=FONTS["small"], text_color=COLORS["text_muted"]
                    ).pack(anchor="w", padx=16, pady=(0, 10))

        # Adjustment type
        ctk.CTkLabel(dlg, text="Adjustment Type",
                     font=FONTS["label_form"], text_color=COLORS["text_dark"]
                    ).pack(anchor="w", padx=24, pady=(0, 4))
        adj_type = tk.StringVar(value="Add")
        type_frame = ctk.CTkFrame(dlg, fg_color="transparent")
        type_frame.pack(fill="x", padx=24, pady=(0, 14))
        for t, col in [("Add", COLORS["btn_success"]),
                       ("Remove", COLORS["btn_danger"]),
                       ("Set", COLORS["btn_primary"])]:
            ctk.CTkRadioButton(
                type_frame, text=t, variable=adj_type, value=t,
                font=FONTS["body_bold"], text_color=COLORS["text_dark"],
                fg_color=col, hover_color=col
            ).pack(side="left", padx=(0, 20))

        # Quantity
        ctk.CTkLabel(dlg, text=t("Quantity *", L),
                     font=FONTS["label_form"], text_color=COLORS["text_dark"]
                    ).pack(anchor="w", padx=24)
        qty_var = tk.StringVar()
        ctk.CTkEntry(dlg, textvariable=qty_var,
                     placeholder_text=t("e.g. 10", L),
                     font=FONTS["input"], height=50,
                     border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"]
                    ).pack(fill="x", padx=24, pady=(4, 14))

        # Reason
        ctk.CTkLabel(dlg, text=t("Reason *", L),
                     font=FONTS["label_form"], text_color=COLORS["text_dark"]
                    ).pack(anchor="w", padx=24)
        reasons = ["New Stock Received", "Damaged / Expired", "Theft / Loss",
                   "Physical Count Correction", "Return to Supplier", "Other"]
        reason_var = tk.StringVar(value=reasons[0])
        ctk.CTkOptionMenu(dlg, variable=reason_var, values=reasons,
                          font=FONTS["input"], height=46, fg_color=COLORS["btn_primary"],
                          button_color="#005BBE"
                         ).pack(fill="x", padx=24, pady=(4, 0))

        err_lbl = ctk.CTkLabel(dlg, text="", font=FONTS["small"],
                                text_color=COLORS["btn_danger"])
        err_lbl.pack(pady=(6, 0), padx=24, anchor="w")

        def save():
            try:
                qty = float(qty_var.get())
                if qty <= 0:
                    raise ValueError
            except ValueError:
                err_lbl.configure(text="⚠  Enter a valid positive quantity.")
                return
            t = adj_type.get()
            if t == "Remove" and qty > prod["current_stock"]:
                err_lbl.configure(
                    text=f"⚠  Cannot remove more than current stock ({prod['current_stock']:.1f})."
                )
                return
            self.db.do_stock_adjustment(
                product_id, t, qty, reason_var.get(),
                self.current_user["user_id"]
            )
            messagebox.showinfo("Done", f"Stock adjusted successfully!", parent=dlg)
            dlg.destroy()
            self._load_stats()
            self._load_products()

        btn_row = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=14)
        ctk.CTkButton(btn_row, text=t("Save Adjustment", L),
                      font=FONTS["button"], fg_color=COLORS["btn_success"],
                      height=52, corner_radius=16,
                      command=save).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(btn_row, text="Cancel","""

new_adj_dlg = """    def _open_adjustment_dialog(self, product_id=None):
        L = self.app.current_lang
        if not product_id:
            product_id = self._get_selected_pid()
        if not product_id:
            return

        prod = self.db.get_product_by_id(product_id)
        if not prod:
            return

        dlg = ctk.CTkToplevel(self.winfo_toplevel())
        dlg.title(t("Adjust Stock", L))
        place_popup(dlg, 500, 480)
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        # Header
        ctk.CTkFrame(dlg, fg_color=COLORS["btn_warning"], height=6, corner_radius=0).pack(fill="x")
        ctk.CTkLabel(dlg, text="🔧   " + t("Adjust Stock", L),
                     font=FONTS["heading"], text_color=COLORS["text_dark"]
                    ).pack(pady=(18, 4), padx=24, anchor="w")

        # Product info card
        info = ctk.CTkFrame(dlg, fg_color=COLORS["bg_main"], corner_radius=16)
        info.pack(fill="x", padx=24, pady=(0, 16))
        ctk.CTkLabel(info, text=prod["name"],
                     font=FONTS["body_bold"], text_color=COLORS["text_dark"]
                    ).pack(anchor="w", padx=16, pady=(10, 2))
        ctk.CTkLabel(info,
                     text=f"{t('Current Stock', L)}:  {prod['current_stock']:.1f}  {prod.get('unit','piece')}   |   "
                          f"{t('Reorder Level', L)}: {prod['reorder_level']:.0f}",
                     font=FONTS["small"], text_color=COLORS["text_muted"]
                    ).pack(anchor="w", padx=16, pady=(0, 10))

        # Adjustment type
        ctk.CTkLabel(dlg, text=t("Adjustment Type", L),
                     font=FONTS["label_form"], text_color=COLORS["text_dark"]
                    ).pack(anchor="w", padx=24, pady=(0, 4))
        adj_type = tk.StringVar(value="Add")
        type_frame = ctk.CTkFrame(dlg, fg_color="transparent")
        type_frame.pack(fill="x", padx=24, pady=(0, 14))
        for mode_key, col in [("Add", COLORS["btn_success"]),
                              ("Remove", COLORS["btn_danger"]),
                              ("Set", COLORS["btn_primary"])]:
            ctk.CTkRadioButton(
                type_frame, text=t(mode_key, L), variable=adj_type, value=mode_key,
                font=FONTS["body_bold"], text_color=COLORS["text_dark"],
                fg_color=col, hover_color=col
            ).pack(side="left", padx=(0, 20))

        # Quantity
        ctk.CTkLabel(dlg, text=t("Quantity *", L),
                     font=FONTS["label_form"], text_color=COLORS["text_dark"]
                    ).pack(anchor="w", padx=24)
        qty_var = tk.StringVar()
        ctk.CTkEntry(dlg, textvariable=qty_var,
                     placeholder_text=t("e.g. 10", L),
                     font=FONTS["input"], height=50,
                     border_color=COLORS["border_focus"], fg_color=COLORS["bg_input"]
                    ).pack(fill="x", padx=24, pady=(4, 14))

        # Reason
        ctk.CTkLabel(dlg, text=t("Reason *", L),
                     font=FONTS["label_form"], text_color=COLORS["text_dark"]
                    ).pack(anchor="w", padx=24)
        reasons_list = ["New Stock Received", "Damaged / Expired", "Theft / Loss",
                        "Physical Count Correction", "Return to Supplier", "Other"]
        reasons_display = [t(r, L) for r in reasons_list]
        reason_var = tk.StringVar(value=reasons_display[0])
        ctk.CTkOptionMenu(dlg, variable=reason_var, values=reasons_display,
                          font=FONTS["input"], height=46, fg_color=COLORS["btn_primary"],
                          button_color="#005BBE"
                         ).pack(fill="x", padx=24, pady=(4, 0))

        err_lbl = ctk.CTkLabel(dlg, text="", font=FONTS["small"],
                                text_color=COLORS["btn_danger"])
        err_lbl.pack(pady=(6, 0), padx=24, anchor="w")

        def save():
            try:
                qty = float(qty_var.get())
                if qty <= 0:
                    raise ValueError
            except ValueError:
                err_lbl.configure(text="⚠  " + t("Enter a valid positive quantity.", L))
                return
            adj_t = adj_type.get()
            if adj_t == "Remove" and qty > prod["current_stock"]:
                err_lbl.configure(
                    text="⚠  " + t("Cannot remove more than current stock ({stock}).", L).format(stock=f"{prod['current_stock']:.1f}")
                )
                return
            
            # Map reason back to English for DB
            db_reason = reason_var.get()
            try:
                r_idx = reasons_display.index(db_reason)
                db_reason = reasons_list[r_idx]
            except ValueError:
                pass

            self.db.do_stock_adjustment(
                product_id, adj_t, qty, db_reason,
                self.current_user["user_id"]
            )
            messagebox.showinfo(t("Done", L), t("Stock adjusted successfully!", L), parent=dlg)
            dlg.destroy()
            self._load_stats()
            self._load_products()

        btn_row = ctk.CTkFrame(dlg, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=14)
        ctk.CTkButton(btn_row, text=t("Save Adjustment", L),
                      font=FONTS["button"], fg_color=COLORS["btn_success"],
                      height=52, corner_radius=16,
                      command=save).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(btn_row, text=t("Cancel", L),
                      font=FONTS["button"], fg_color=COLORS["btn_secondary"],
                      height=52, corner_radius=16,
                      command=dlg.destroy).pack(side="left", width=110)"""

# Replacement 2: _show_adj_history rendering
old_history_render = """        records = self.db.get_stock_adjustments(limit=200)
        for r in records:
            tree.insert("", "end", values=(
                r["created_at"][:16],
                r["product_name"],
                r["adj_type"],
                f"{r['qty_before']:.1f}",
                f"+{r['qty_change']:.1f}" if r["adj_type"] == "Add"
                    else (f"-{r['qty_change']:.1f}" if r["adj_type"] == "Remove"
                          else f"→{r['qty_change']:.1f}"),
                f"{r['qty_after']:.1f}",
                r.get("reason", ""),
            ))"""

new_history_render = """        records = self.db.get_stock_adjustments(limit=200)
        for r in records:
            tree.insert("", "end", values=(
                r["created_at"][:16],
                r["product_name"],
                t(r["adj_type"], L),
                f"{r['qty_before']:.1f}",
                f"+{r['qty_change']:.1f}" if r["adj_type"] == "Add"
                    else (f"-{r['qty_change']:.1f}" if r["adj_type"] == "Remove"
                          else f"→{r['qty_change']:.1f}"),
                f"{r['qty_after']:.1f}",
                t(r.get("reason", ""), L),
            ))"""

replacements_inventory = [
    (old_adj_dlg, new_adj_dlg),
    (old_history_render, new_history_render),
]

for idx, (old, new) in enumerate(replacements_inventory, 1):
    if old in content:
        content = content.replace(old, new)
        print(f"screen_inventory.py: Replacement {idx} succeeded.")
    else:
        print(f"screen_inventory.py: Error - Replacement {idx} target not found.")

with open(inventory_file, "w", encoding="utf-8") as f:
    f.write(content)

print("All file edits completed successfully.")

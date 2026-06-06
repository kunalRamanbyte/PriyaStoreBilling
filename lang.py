"""
lang.py — UI string translations for Priya Store billing system
Supports: English, Bengali (colloquial), Hindi (colloquial)

Style: Daily-use words. Product names, brand names, units, and technical
terms that people already say in English stay in English.
"""

LANGUAGES = ["English", "বাংলা (Bengali)", "हिन्दी (Hindi)"]
LANG_DB_VALUES = ["English", "Bengali", "Hindi"]   # stored in settings table
DEFAULT_LANG = "English"

# Master translation table
# Keys match what the code uses; values are [English, Bengali, Hindi]
T = {
    # ══════════════════════════════════════════════════════════════
    # Sidebar / Navigation
    # ══════════════════════════════════════════════════════════════
    "Dashboard":        ["Dashboard",        "Dashboard",         "Dashboard"],
    "New Bill":         ["New Bill",          "নতুন বিল",          "नया बिल"],
    "Bill History":     ["Bill History",      "বিল History",       "बिल History"],
    "Products":         ["Products",          "Products",          "Products"],
    "Categories":       ["Categories",        "Categories",        "Categories"],
    "Inventory":        ["Inventory",         "Inventory",         "Inventory"],
    "Suppliers":        ["Suppliers",         "Suppliers",         "Suppliers"],
    "Purchase/GRN":     ["Purchase/GRN",      "Purchase/GRN",      "Purchase/GRN"],
    "Customers":        ["Customers",         "Customers",         "Customers"],
    "Reports":          ["Reports",           "Reports",           "Reports"],
    "Settings":         ["Settings",          "Settings",          "Settings"],
    "Users":            ["Users",             "Users",             "Users"],
    "Activity Log":     ["Activity Log",      "Activity Log",      "Activity Log"],
    "Sign Out":         ["Sign Out",          "বের হও",            "बाहर जाओ"],

    # ══════════════════════════════════════════════════════════════
    # Common buttons / labels
    # ══════════════════════════════════════════════════════════════
    "Save":             ["Save",              "Save করো",          "Save करो"],
    "Cancel":           ["Cancel",            "Cancel",            "Cancel"],
    "Close":            ["Close",             "বন্ধ করো",          "बंद करो"],
    "Search":           ["Search",            "Search",            "Search"],
    "Add":              ["Add",               "Add করো",           "Add करो"],
    "Edit":             ["Edit",              "Edit করো",          "Edit करो"],
    "Delete":           ["Delete",            "Delete করো",        "Delete करो"],
    "Total":            ["Total",             "Total",             "Total"],
    "Grand Total":      ["Grand Total",       "মোট Total",         "कुल Total"],
    "Subtotal":         ["Subtotal",          "Subtotal",          "Subtotal"],
    "Discount":         ["Discount",          "Discount",          "Discount"],
    "Quantity":         ["Quantity",           "পরিমাণ",            "मात्रा"],
    "Price":            ["Price",             "দাম",               "दाम"],
    "Amount Paid":      ["Amount Paid",       "টাকা দিয়েছে",       "पैसा दिया"],
    "Change Due":       ["Change Due",        "ফেরত",              "वापसी"],
    "Ready":            ["Ready",             "তৈয়ার",             "तैयार"],
    "Today":            ["Today",             "আজকে",              "आज"],
    "All":              ["All",               "সব",                "सब"],
    "Filter":           ["Filter",            "Filter",            "Filter"],
    "From:":            ["From:",             "থেকে:",             "से:"],
    "To:":              ["To:",               "পর্যন্ত:",           "तक:"],
    "Status":           ["Status",            "Status",            "Status"],
    "Date":             ["Date",              "তারিখ",             "तारीख"],
    "Name":             ["Name",              "নাম",               "नाम"],
    "Phone":            ["Phone",             "Phone",             "Phone"],
    "Address":          ["Address",           "Address",           "Address"],
    "Yes":              ["Yes",               "হ্যাঁ",              "हाँ"],
    "No":               ["No",                "না",                "नहीं"],
    "OK":               ["OK",                "OK",                "OK"],
    "Error":            ["Error",             "Error",             "Error"],
    "Warning":          ["Warning",           "Warning",           "Warning"],
    "Required":         ["Required",          "Required",          "Required"],

    # ══════════════════════════════════════════════════════════════
    # Header / App
    # ══════════════════════════════════════════════════════════════
    "Exit the billing system?":
        ["Exit the billing system?",
         "Billing system বন্ধ করবে?",
         "Billing system बंद करोगे?"],
    "Exit":              ["Exit",              "Exit",              "Exit"],
    "Logout":            ["Logout",            "Logout",            "Logout"],
    "Are you sure you want to logout?":
        ["Are you sure you want to logout?",
         "সত্যিই Logout করবে?",
         "सच में Logout करोगे?"],

    # ══════════════════════════════════════════════════════════════
    # Dashboard
    # ══════════════════════════════════════════════════════════════
    "Today's Sales":        ["Today's Sales",        "আজকের বিক্রি",       "आज की बिक्री"],
    "Bills Today":          ["Bills Today",          "আজকের বিল",          "आज के बिल"],
    "Low Stock Items":      ["Low Stock Items",      "কম Stock",            "कम Stock"],
    "Expiring (30 days)":   ["Expiring (30 days)",   "Expire হচ্ছে (30 দিন)", "Expire हो रहा (30 दिन)"],
    "Discount Given":       ["Discount Given",       "Discount দিয়েছ",      "Discount दिया"],
    "Quick Actions":        ["Quick Actions",        "Quick Actions",       "Quick Actions"],
    "New Bill_qa":          ["🧾\nNew Bill",          "🧾\nনতুন বিল",        "🧾\nनया बिल"],
    "Add Product_qa":       ["📦\nAdd Product",       "📦\nProduct Add",     "📦\nProduct Add"],
    "Bill History_qa":      ["📋\nBill History",      "📋\nবিল History",     "📋\nबिल History"],
    "Categories_qa":        ["🏷️\nCategories",       "🏷️\nCategories",     "🏷️\nCategories"],
    "Products Expiring Within 30 Days":
        ["Products Expiring Within 30 Days",
         "30 দিনে Expire হচ্ছে",
         "30 दिन में Expire हो रहा"],
    "Product Name":         ["Product Name",         "Product এর নাম",      "Product का नाम"],
    "Category":             ["Category",             "Category",            "Category"],
    "Stock":                ["Stock",                "Stock",               "Stock"],
    "Expiry Date":          ["Expiry Date",          "Expiry Date",         "Expiry Date"],
    "Days Left":            ["Days Left",            "বাকি দিন",            "बाकी दिन"],
    "Recent Bills":         ["Recent Bills",         "Recent বিল",          "Recent बिल"],
    "Bill No.":             ["Bill No.",             "Bill No.",            "Bill No."],
    "Date & Time":          ["Date & Time",          "Date & Time",         "Date & Time"],
    "Customer":             ["Customer",             "Customer",            "Customer"],
    "Amount (₹)":           ["Amount (₹)",           "Amount (₹)",          "Amount (₹)"],
    "Mode":                 ["Mode",                 "Mode",                "Mode"],

    # ══════════════════════════════════════════════════════════════
    # Billing Screen
    # ══════════════════════════════════════════════════════════════
    "Bright Billing Dashboard":
        ["Bright Billing Dashboard",
         "Billing Dashboard",
         "Billing Dashboard"],
    "Cart is empty.\nSearch and add products above.":
        ["🛒\n\nCart is empty.\nSearch and add products above.",
         "🛒\n\nCart খালি আছে।\nউপরে Search করে Product add করো।",
         "🛒\n\nCart खाली है।\nऊपर Search करके Product add करो।"],
    "Product Name_col":     ["Product Name",         "Product",             "Product"],
    "Unit":                 ["Unit",                 "Unit",                "Unit"],
    "Qty":                  ["Qty",                  "Qty",                 "Qty"],
    "Price ₹":              ["Price ₹",              "দাম ₹",               "दाम ₹"],
    "Disc ₹":               ["Disc ₹",               "Disc ₹",              "Disc ₹"],
    "Total ₹":              ["Total ₹",              "Total ₹",             "Total ₹"],
    "Summary":              ["Summary",              "Summary",             "Summary"],
    "Subtotal :":           ["Subtotal :",           "Subtotal :",          "Subtotal :"],
    "Discount (₹) :":      ["Discount (₹) :",       "Discount (₹) :",      "Discount (₹) :"],
    "TOTAL":                ["TOTAL",                "TOTAL",               "TOTAL"],
    "Bill Discount (₹):":  ["Bill Discount (₹):",   "Bill Discount (₹):",  "Bill Discount (₹):"],
    "Payment Mode":         ["Payment Mode",         "Payment Mode",        "Payment Mode"],
    "Cash Received (₹)":   ["Cash Received (₹)",    "Cash পেয়েছ (₹)",     "Cash मिला (₹)"],
    "Change Due :":         ["Change Due :",         "ফেরত :",              "वापसी :"],
    "F10 Print & Save":     ["F10 Print & Save",     "F10 Print & Save",    "F10 Print & Save"],
    "F8 Hold Bill":         ["F8 Hold Bill",         "F8 বিল Hold",         "F8 बिल Hold"],
    "ESC Clear Cart":       ["ESC Clear Cart",       "ESC Cart খালি",       "ESC Cart खाली"],
    "Walk-in":              ["Walk-in",              "Walk-in",             "Walk-in"],
    "Customer: Search or type customer name...":
        ["Customer: Search or type customer name...",
         "Customer: নাম search করো...",
         "Customer: नाम search करो..."],
    "Scan barcode or search product…   (F2)":
        ["🔍  Scan barcode or search product…   (F2)",
         "🔍  Barcode scan বা Product search করো…   (F2)",
         "🔍  Barcode scan या Product search करो…   (F2)"],
    "Add New Customer":     ["Add New Customer",     "নতুন Customer",       "नया Customer"],
    "Name *":               ["Name *",               "নাম *",               "नाम *"],
    "Full name":            ["Full name",            "পুরো নাম",            "पूरा नाम"],
    "Mobile number":        ["Mobile number",        "Mobile number",       "Mobile number"],
    "Shop / area":          ["Shop / area",          "Shop / area",         "Shop / area"],
    "Save Customer":        ["✅  Save Customer",     "✅  Save করো",        "✅  Save करो"],
    "Prev. Udhaar":         ["⚠️  Prev. Udhaar :",    "⚠️  আগের বাকি :",     "⚠️  पिछला उधार :"],
    "Empty Cart":           ["Empty Cart",           "Cart খালি",           "Cart खाली"],
    "Please add at least one product to the bill.":
        ["Please add at least one product to the bill.",
         "Bill এ কমপক্ষে একটা Product add করো।",
         "Bill में कम से कम एक Product add करो।"],
    "Clear Cart":           ["Clear Cart",           "Cart খালি করো",       "Cart खाली करो"],
    "Clear all items from cart?":
        ["Clear all items from cart?",
         "Cart এর সব item মুছবে?",
         "Cart के सब item हटाओगे?"],
    "Bill saved successfully!":
        ["✅  Bill saved successfully!",
         "✅  বিল Save হয়ে গেছে!",
         "✅  बिल Save हो गया!"],
    "Cart cleared.":        ["🗑️  Cart cleared.",     "🗑️  Cart খালি।",      "🗑️  Cart खाली।"],
    "Bill Held":            ["Bill Held",            "বিল Hold",            "बिल Hold"],
    "Bill saved as draft.\nYou can resume it from Bill History.":
        ["Bill saved as draft.\nYou can resume it from Bill History.",
         "বিল Draft হিসেবে Save।\nBill History থেকে Resume করতে পারো।",
         "बिल Draft Save हुआ।\nBill History से Resume कर सकते हो।"],
    "Bill held. Cart cleared for next bill.":
        ["✋  Bill held. Cart cleared for next bill.",
         "✋  বিল Hold। Cart খালি।",
         "✋  बिल Hold। Cart खाली।"],
    "New Bill_confirm":     ["New Bill",              "নতুন বিল",            "नया बिल"],
    "Start a new bill? Current cart items will be cleared.":
        ["Start a new bill? Current cart items will be cleared.",
         "নতুন বিল শুরু করবে? Cart এর সব item মুছে যাবে।",
         "नया बिल शुरू करोगे? Cart के सब item हट जाएंगे।"],
    "Insufficient Stock":   ["Insufficient Stock",   "Stock কম",            "Stock कम"],
    "Remove Item":          ["Remove Item",          "Item সরাও",           "Item हटाओ"],
    "Bill Receipt":         ["Bill Receipt",         "Bill Receipt",        "Bill Receipt"],
    "Thank you for shopping with us!":
        ["Thank you for shopping with us!  🙏",
         "আমাদের থেকে কেনার জন্য ধন্যবাদ!  🙏",
         "हमसे खरीदारी करने के लिए धन्यवाद!  🙏"],
    "Thermal Print":        ["🖨  Thermal Print",     "🖨  Thermal Print",   "🖨  Thermal Print"],
    "PDF / A4":             ["📄  PDF / A4",          "📄  PDF / A4",        "📄  PDF / A4"],
    "Done":                 ["✅  Done",              "✅  Done",            "✅  Done"],
    "Update":               ["✅  Update",            "✅  Update",          "✅  Update"],
    "Remove":               ["🗑️  Remove",            "🗑️  সরাও",           "🗑️  हटाओ"],
    "GRAND TOTAL:":         ["GRAND TOTAL:",          "মোট TOTAL:",          "कुल TOTAL:"],
    "TOTAL TO COLLECT:":    ["TOTAL TO COLLECT:",     "মোট নিতে হবে:",       "कुल लेना है:"],
    "Amount Paid:":         ["Amount Paid:",          "টাকা দিয়েছে:",        "पैसा दिया:"],
    "Change Due:":          ["Change Due:",           "ফেরত:",              "वापसी:"],
    "Subtotal:":            ["Subtotal:",             "Subtotal:",           "Subtotal:"],
    "Discount:":            ["Discount:",             "Discount:",           "Discount:"],
    "Item":                 ["Item",                  "Item",                "Item"],
    "Rate":                 ["Rate",                  "Rate",                "Rate"],
    "Disc":                 ["Disc",                  "Disc",                "Disc"],
    "Amt":                  ["Amt",                   "Amt",                 "Amt"],
    "Select Customer":      ["Select Customer",       "Customer বাছো",       "Customer चुनो"],

    # ══════════════════════════════════════════════════════════════
    # Bill History
    # ══════════════════════════════════════════════════════════════
    "Bill no. or customer name":
        ["Bill no. or customer name",
         "Bill no. বা Customer নাম",
         "Bill no. या Customer नाम"],
    "bill(s) found":        ["{n} bill(s) found",    "{n} বিল পাওয়া গেছে",  "{n} बिल मिले"],
    "View Bill":            ["👁️  View Bill",         "👁️  বিল দেখো",        "👁️  बिल देखो"],
    "Reprint":              ["🖨️  Reprint",           "🖨️  Reprint",         "🖨️  Reprint"],
    "Resume Draft":         ["▶️  Resume Draft",      "▶️  Draft Resume",    "▶️  Draft Resume"],
    "Void Bill":            ["❌  Void Bill",          "❌  বিল Void",         "❌  बिल Void"],
    "Select Bill":          ["Select Bill",           "বিল Select করো",     "बिल Select करो"],
    "Please select a bill first.":
        ["Please select a bill first.",
         "আগে একটা বিল select করো।",
         "पहले एक बिल select करो।"],
    "Voided Bill":          ["Voided Bill",           "Voided বিল",          "Voided बिल"],
    "This bill has been voided and cannot be reprinted.":
        ["This bill has been voided and cannot be reprinted.",
         "এই বিল void হয়ে গেছে, reprint হবে না।",
         "यह बिल void हो चुका है, reprint नहीं होगा।"],
    "Items":                ["Items",                 "Items",               "Items"],
    "Paid:":                ["Paid:",                 "দিয়েছে:",             "दिया:"],
    "TOTAL:":               ["TOTAL:",                "TOTAL:",              "TOTAL:"],
    "Void Reason":          ["Void Reason",           "Void Reason",         "Void Reason"],
    "Cannot Void":          ["Cannot Void",           "Void করা যাবে না",    "Void नहीं हो सकता"],
    "Confirm Void":         ["Confirm Void",          "Void Confirm",        "Void Confirm"],
    "Voided":               ["Voided",                "Voided",              "Voided"],
    "Not a Draft":          ["Not a Draft",           "Draft না",            "Draft नहीं"],

    # ══════════════════════════════════════════════════════════════
    # Product Master
    # ══════════════════════════════════════════════════════════════
    "Product Master":       ["📦   Product Master",    "📦   Product Master", "📦   Product Master"],
    "Add New Product":      ["➕  Add New Product",    "➕  নতুন Product",    "➕  नया Product"],
    "Search products...":   ["Search products...",    "Product search করো...", "Product search करो..."],
    "All Categories":       ["All Categories",        "সব Categories",       "सब Categories"],
    "Sell ₹":               ["Sell ₹",                "বিক্রি ₹",            "बिक्री ₹"],
    "Purchase ₹":           ["Purchase ₹",            "কেনা ₹",              "खरीद ₹"],
    "Active":               ["Active",                "Active",              "Active"],
    "product(s)":           ["{n} product(s)",        "{n} product",         "{n} product"],
    "Add Product":          ["Add Product",           "Product Add",         "Product Add"],
    "Edit Product":         ["Edit Product",          "Product Edit",        "Product Edit"],
    "Category *":           ["Category *",            "Category *",          "Category *"],
    "Product Name *":       ["Product Name *",        "Product নাম *",       "Product नाम *"],
    "HSN Code":             ["HSN Code",              "HSN Code",            "HSN Code"],
    "Barcode":              ["Barcode",               "Barcode",             "Barcode"],
    "Unit *":               ["Unit *",                "Unit *",              "Unit *"],
    "Selling Price *":      ["Selling Price *",       "বিক্রি দাম *",        "बिक्री दाम *"],
    "Purchase Price":       ["Purchase Price",        "কেনা দাম",            "खरीद दाम"],
    "Opening Stock":        ["Opening Stock",         "শুরুর Stock",          "शुरू का Stock"],
    "Min Stock Alert":      ["Min Stock Alert",       "Min Stock Alert",     "Min Stock Alert"],
    "Save Product":         ["💾  Save Product",       "💾  Save করো",        "💾  Save करो"],
    "Deactivate":           ["Deactivate",            "Deactivate",          "Deactivate"],
    "Activate":             ["Activate",              "Activate",            "Activate"],

    # ══════════════════════════════════════════════════════════════
    # Category Manager
    # ══════════════════════════════════════════════════════════════
    "Category Manager":     ["🏷️   Category Manager",  "🏷️   Category Manager", "🏷️   Category Manager"],
    "All Categories_list":  ["All Categories",         "সব Categories",        "सब Categories"],
    "Add / Edit Category":  ["Add / Edit Category",    "Category Add / Edit",  "Category Add / Edit"],
    "Category Name *":      ["Category Name *",        "Category নাম *",       "Category नाम *"],
    "Colour Code":          ["Colour Code",            "Colour Code",          "Colour Code"],
    "Custom:":              ["Custom:",                "Custom:",              "Custom:"],
    "Pick Colour":          ["🎨 Pick Colour",          "🎨 Colour বাছো",       "🎨 Colour चुनो"],
    "Save Category":        ["💾  Save Category",       "💾  Save করো",         "💾  Save करो"],
    "Reset / New":          ["🔄  Reset / New",         "🔄  Reset / নতুন",     "🔄  Reset / नया"],
    "No categories yet.\nAdd one using the form →":
        ["No categories yet.\nAdd one using the form →",
         "এখনো কোনো Category নেই।\nForm থেকে Add করো →",
         "अभी कोई Category नहीं।\nForm से Add करो →"],
    "(Inactive)":           ["(Inactive)",             "(Inactive)",           "(Inactive)"],
    "Category name is required.":
        ["⚠  Category name is required.",
         "⚠  Category নাম দাও।",
         "⚠  Category नाम दो।"],

    # ══════════════════════════════════════════════════════════════
    # Inventory
    # ══════════════════════════════════════════════════════════════
    "Inventory Overview":   ["📊   Inventory Overview", "📊   Inventory",       "📊   Inventory"],
    "Current Stock":        ["Current Stock",           "এখনকার Stock",         "अभी का Stock"],
    "Low Stock":            ["⚠️  Low Stock",            "⚠️  কম Stock",         "⚠️  कम Stock"],
    "Out of Stock":         ["🚫  Out of Stock",         "🚫  Stock নেই",        "🚫  Stock नहीं"],
    "All Stock":            ["All Stock",               "সব Stock",             "सब Stock"],
    "Export Excel":         ["📥  Export Excel",         "📥  Excel Export",     "📥  Excel Export"],
    "Adjust Stock":         ["🔧  Adjust Stock",        "🔧  Stock ঠিক করো",   "🔧  Stock ठीक करो"],
    "Stock Adjustment":     ["Stock Adjustment",        "Stock Adjustment",    "Stock Adjustment"],
    "New Qty *":            ["New Qty *",               "নতুন Qty *",          "नया Qty *"],
    "Reason *":             ["Reason *",                "কারণ *",              "कारण *"],
    "Apply Adjustment":     ["Apply Adjustment",        "Apply করো",           "Apply करो"],

    # ══════════════════════════════════════════════════════════════
    # Suppliers
    # ══════════════════════════════════════════════════════════════
    "Supplier Master":      ["🏭   Supplier Master",    "🏭   Supplier Master", "🏭   Supplier Master"],
    "Add Supplier":         ["➕  Add Supplier",        "➕  নতুন Supplier",    "➕  नया Supplier"],
    "Supplier Name":        ["Supplier Name",           "Supplier নাম",         "Supplier नाम"],
    "Contact Person":       ["Contact Person",          "Contact Person",       "Contact Person"],
    "GST Number":           ["GST Number",              "GST Number",           "GST Number"],
    "Save Supplier":        ["💾  Save Supplier",       "💾  Save করো",         "💾  Save करो"],

    # ══════════════════════════════════════════════════════════════
    # Purchase / GRN
    # ══════════════════════════════════════════════════════════════
    "New Purchase / GRN":   ["🛒   New Purchase / GRN", "🛒   নতুন Purchase / GRN", "🛒   नया Purchase / GRN"],
    "Select Supplier *":    ["Select Supplier *",       "Supplier বাছো *",      "Supplier चुनो *"],
    "Invoice / Ref No.":    ["Invoice / Ref No.",       "Invoice / Ref No.",    "Invoice / Ref No."],
    "Select product from existing or search":
        ["Select product from existing or search",
         "Product search করো বা বাছো",
         "Product search करो या चुनो"],
    "Add New Item":         ["➕ Add New Item",          "➕ নতুন Item",         "➕ नया Item"],
    "Add to Purchase":      ["➕  Add to Purchase",     "➕  Purchase এ Add",   "➕  Purchase में Add"],
    "Save GRN":             ["💾  Save GRN",            "💾  GRN Save",         "💾  GRN Save"],
    "Clear All":            ["🗑  Clear All",            "🗑  সব মুছো",           "🗑  सब हटाओ"],
    "Purchase Items":       ["Purchase Items",          "Purchase Items",       "Purchase Items"],
    "Unit Price ₹":         ["Unit Price ₹",            "দাম ₹",                "दाम ₹"],
    "Line Total":           ["Line Total",              "Line Total",           "Line Total"],

    # ══════════════════════════════════════════════════════════════
    # Customers
    # ══════════════════════════════════════════════════════════════
    "Customer Master":      ["👥   Customer Master",    "👥   Customer Master", "👥   Customer Master"],
    "Add Customer":         ["➕  Add Customer",        "➕  নতুন Customer",    "➕  नया Customer"],
    "Search customers...":  ["Search customers...",     "Customer search করো...", "Customer search करो..."],
    "Customer Name":        ["Customer Name",           "Customer নাম",         "Customer नाम"],
    "Credit Balance":       ["Credit Balance",          "বাকি টাকা",            "बाकी पैसा"],
    "Save Customer_btn":    ["💾  Save Customer",       "💾  Save করো",         "💾  Save करो"],

    # ══════════════════════════════════════════════════════════════
    # Reports
    # ══════════════════════════════════════════════════════════════
    "Reports & Analytics":  ["📈   Reports & Analytics", "📈   Reports",        "📈   Reports"],
    "Sales Summary":        ["Sales Summary",           "বিক্রি Summary",       "बिक्री Summary"],
    "Total Sales":          ["Total Sales",             "মোট বিক্রি",           "कुल बिक्री"],
    "Total Bills":          ["Total Bills",             "মোট বিল",              "कुल बिल"],
    "Total Discount":       ["Total Discount",          "মোট Discount",        "कुल Discount"],
    "Avg Bill Value":       ["Avg Bill Value",          "Average বিল",          "Average बिल"],
    "Top Products":         ["Top Products",            "Top Products",         "Top Products"],
    "Generate Report":      ["Generate Report",         "Report বানাও",         "Report बनाओ"],
    "Daily":                ["Daily",                   "দিনের",                "दिन का"],
    "Weekly":               ["Weekly",                  "সাপ্তাহিক",             "साप्ताहिक"],
    "Monthly":              ["Monthly",                 "মাসের",                "महीने का"],
    "Yearly":               ["Yearly",                  "বছরের",                "साल का"],

    # ══════════════════════════════════════════════════════════════
    # Settings
    # ══════════════════════════════════════════════════════════════
    "Settings & Configuration":
        ["⚙️   Settings & Configuration",
         "⚙️   Settings",
         "⚙️   Settings"],
    "Shop Information":     ["🏪  Shop Information",     "🏪  Shop তথ্য",        "🏪  Shop जानकारी"],
    "Bill Configuration":   ["🧾  Bill Configuration",   "🧾  Bill Config",      "🧾  Bill Config"],
    "Backup & Restore":     ["💾  Backup & Restore",     "💾  Backup & Restore", "💾  Backup & Restore"],
    "Last Backup":          ["Last Backup",              "শেষ Backup",           "आखिरी Backup"],
    "Backup Now":           ["🔄  Backup Now",           "🔄  এখন Backup",       "🔄  अभी Backup"],
    "Backup Folder":        ["Backup Folder",            "Backup Folder",        "Backup Folder"],
    "Default (app folder)": ["Default (app folder)",     "Default (app folder)", "Default (app folder)"],
    "Choose Folder":        ["📂  Choose Folder",        "📂  Folder বাছো",      "📂  Folder चुनो"],
    "Reset to Default":     ["🗑  Reset to Default",     "🗑  Default করো",       "🗑  Default करो"],
    "Daily Auto-Backup":    ["Daily Auto-Backup",        "Daily Auto-Backup",    "Daily Auto-Backup"],
    "Auto backup description":
        ["Automatically backup once every 24 hours while the app is open",
         "App চালু থাকলে 24 ঘণ্টায় automatically backup হবে",
         "App चालू रहने पर 24 घंटे में automatically backup होगा"],
    "Restore from Backup":  ["Restore from Backup",      "Backup থেকে Restore", "Backup से Restore"],
    "Restore description":
        ["Replace current data with a previous backup file (.db)",
         "আগের backup file (.db) দিয়ে data replace হবে",
         "पिछली backup file (.db) से data replace होगा"],
    "Restore Backup":       ["♻️  Restore Backup",       "♻️  Restore করো",      "♻️  Restore करो"],
    "Save Settings":        ["💾   Save Settings",       "💾   Settings Save",   "💾   Settings Save"],
    "No backup yet":        ["No backup yet",            "এখনো backup হয়নি",    "अभी तक backup नहीं"],
    "Saved":                ["Saved",                    "Save হয়েছে",          "Save हो गया"],
    "Settings saved successfully!":
        ["Settings saved successfully!",
         "Settings save হয়ে গেছে!",
         "Settings save हो गया!"],
    "Language":             ["🌐  Language",              "🌐  ভাষা",              "🌐  भाषा"],
    "Select Language":      ["Select Language",          "ভাষা বাছো",            "भाषा चुनो"],

    # ══════════════════════════════════════════════════════════════
    # Users
    # ══════════════════════════════════════════════════════════════
    "User Management":      ["👤   User Management",     "👤   User Management", "👤   User Management"],
    "Add User":             ["➕  Add User",              "➕  নতুন User",        "➕  नया User"],
    "Username":             ["Username",                  "Username",             "Username"],
    "Password":             ["Password",                  "Password",             "Password"],
    "Role":                 ["Role",                      "Role",                 "Role"],
    "Save User":            ["💾  Save User",             "💾  Save করো",         "💾  Save करो"],

    # ══════════════════════════════════════════════════════════════
    # Activity Log
    # ══════════════════════════════════════════════════════════════
    "Activity Log_heading":  ["📋   Activity Log",        "📋   Activity Log",    "📋   Activity Log"],
    "Action":                ["Action",                   "Action",               "Action"],
    "Details":               ["Details",                  "Details",              "Details"],
    "User":                  ["User",                     "User",                 "User"],
    "Timestamp":             ["Timestamp",                "Timestamp",            "Timestamp"],

    # ══════════════════════════════════════════════════════════════
    # Login
    # ══════════════════════════════════════════════════════════════
    "Login":                ["Login",                    "Login",                "Login"],
    "Sign In":              ["Sign In",                  "Sign In করো",          "Sign In करो"],

    # ══════════════════════════════════════════════════════════════
    # Field labels from Settings
    # ══════════════════════════════════════════════════════════════
    "Shop Name *":          ["Shop Name *",              "Shop নাম *",           "Shop नाम *"],
    "Shop Address":         ["Address",                  "Address",              "Address"],
    "City":                 ["City",                     "City",                 "City"],
    "GST Number_setting":   ["GST Number",               "GST Number",           "GST Number"],
    "Bill Prefix *":        ["Bill Prefix *",            "Bill Prefix *",        "Bill Prefix *"],
    "Next Bill Number *":   ["Next Bill Number *",       "Next Bill Number *",   "Next Bill Number *"],
      "Thermal Paper Width":  ["Thermal Paper Width",      "Thermal Paper Width",  "Thermal Paper Width"],

    # ── Additional Keys for Remaining Screens ──
    "Customers & Udhaar":   ["👥   Customers & Udhaar", "👥   Customers & Udhaar", "👥   Customers & Udhaar"],
    "Add New Customer":     ["➕  Add New Customer",    "➕  নতুন Customer",    "➕  नया Customer"],
    "Total Customers":      ["👥  Total Customers",      "👥  Total Customers",      "👥  Total Customers"],
    "Total Udhaar":         ["💳  Total Udhaar",         "💳  মোট Udhaar",         "💳  कुल Udhaar"],
    "Credit Accounts":      ["📋  Credit Accounts",      "📋  বাকি Account",      "📋  उधार Account"],
    "Search by name or phone…": ["Search by name or phone…", "নাম বা ফোন দিয়ে Search করো...", "नाम या फोन से Search करो..."],
    "Udhaar Balance":       ["Udhaar Balance",           "বাকি টাকা",            "उधार पैसा"],
    "✏️  Edit":              ["✏️  Edit",                 "✏️  Edit",                 "✏️  Edit"],
    "📖  View Ledger":       ["📖  View Ledger",          "📖  Ledger দেখো",          "📖  Ledger देखो"],
    "🖨️  Print Ledger":      ["🖨️  Print Ledger",         "🖨️  Ledger Print",         "🖨️  Ledger Print"],
    "💳  Add Payment":       ["💳  Add Payment",          "💳  টাকা জমা",          "💳  पैसा जमा"],
    "📝  Add Udhaar":        ["📝  Add Udhaar",           "📝  বাকি Add",           "📝  उधार Add"],
    "🗑️  Delete":            ["🗑️  Delete",               "🗑️  Delete",               "🗑️  Delete"],
    "{n} customer(s) found": ["{n} customer(s) found",    "{n} customer পাওয়া গেছে",  "{n} customer मिले"],
    "Edit Customer":        ["Edit Customer",            "Customer Edit",            "Customer Edit"],
    "Full Name":            ["Full Name",                "পুরো নাম",                "पूरा नाम"],
    "Full Name *":          ["Full Name *",              "পুরো নাম *",              "पूरा नाम *"],
    "Phone *":              ["Phone *",                  "Phone *",                  "Phone *"],
    "Address *":            ["Address *",                "Address *",                "Address *"],
    "Customer name is required.": ["Customer name is required.", "Customer নাম দিতে হবে", "Customer नाम देना होगा"],
    "Record Payment":       ["Record Payment",           "টাকা জমা করো",           "पैसा जमा করো"],
    "Add Udhaar (Credit)":  ["Add Udhaar (Credit)",      "বাকি লেখো",               "उधार लिखो"],
    "Current Balance":      ["Current Balance",          "বাকি টাকা",               "बाकी पैसा"],
    "Amount (₹) *":          ["Amount (₹) *",             "টাকা (₹) *",             "पैसा (₹) *"],
    "Reference":            ["Reference",                "Reference",                "Reference"],
    "Enter a valid amount.": ["Enter a valid amount.",    "সঠিক টাকা লেখো",          "सही पैसा लिखो"],
    "Delete Customer":      ["Delete Customer",          "Customer Delete",          "Customer Delete"],
    "Ledger":               ["Ledger",                   "Ledger",                   "Ledger"],
    "No transactions yet":  ["No transactions yet",      "কোনো transaction নেই",     "कोई transaction नहीं"],
    "SELECT REPORT":        ["SELECT REPORT",            "REPORT বাছো",             "REPORT चुनो"],
    "Daily Sales":          ["Daily Sales",              "দিনের বিক্রি",            "दिन की बिक्री"],
    "Item-wise Sales":      ["Item-wise Sales",          "জিনিসপত্র বিক্রি",        "सामान की बिक्री"],
    "Low Stock Alert":      ["Low Stock Alert",          "কম Stock Alert",         "कम Stock Alert"],
    "Profit & Margin":      ["Profit & Margin",          "Profit & Margin",          "Profit & Margin"],
    "Stock Valuation":      ["Stock Valuation",          "Stock Valuation",          "Stock Valuation"],
    "Customer Ledger":      ["Customer Ledger",          "Customer Ledger",          "Customer Ledger"],
    "Slow-Moving Items":    ["Slow-Moving Items",        "কম চলা Product",          "कम चलने वाले Product"],
    "Supplier Payables":    ["Supplier Payables",        "Supplier দেনা",            "Supplier देनदारी"],
    "Customer Ageing":      ["Customer Ageing",          "Customer Ageing",          "Customer Ageing"],
    "Customer:":            ["Customer:",                "Customer:",                "Customer:"],
    "All Customers":        ["All Customers",            "সব Customer",              "सब Customer"],
    "▶  Generate":          ["▶  Generate",              "▶  Generate",              "▶  Generate"],
    "📊 Excel":             ["📊 Excel",                 "📊 Excel",                 "📊 Excel"],
    "📋 CSV":               ["📋 CSV",                   "📋 CSV",                   "📋 CSV"],
    "📄 PDF":               ["📄 PDF",                   "📄 PDF",                   "📄 PDF"],
    "← Select a report from the left panel": ["← Select a report from the left panel", "← বাঁদিকের panel থেকে report বাছো", "← बाएँ panel से report चुनो"],
    "Total rows:":          ["Total rows:",              "মোট row:",                "कुल row:"],
    "Grand Total":          ["Grand Total",              "মোট Total",               "कुल Total"],
    "Bills":                ["Bills",                    "বিল",                     "बिल"],
    "Subtotal ₹":           ["Subtotal ₹",               "Subtotal ₹",               "Subtotal ₹"],
    "Discount ₹":           ["Discount ₹",               "Discount ₹",               "Discount ₹"],
    "Total ₹":              ["Total ₹",                  "Total ₹",                  "Total ₹"],
    "Product":              ["Product",                  "Product",                  "Product"],
    "Avg Price ₹":          ["Avg Price ₹",              "Avg Price ₹",              "Avg Price ₹"],
    "Total Sales ₹":        ["Total Sales ₹",            "Total Sales ₹",            "Total Sales ₹"],
    "Rank":                 ["Rank",                     "Rank",                     "Rank"],
    "Qty Sold":             ["Qty Sold",                 "বিক্রি Qty",               "बिक्री Qty"],
    "Revenue ₹":            ["Revenue ₹",                "Revenue ₹",                "Revenue ₹"],
    "Code":                 ["Code",                     "Code",                     "Code"],
    "Reorder":              ["Reorder",                  "Reorder",                  "Reorder"],
    "Shortage":             ["Shortage",                 "কমতি",                     "कमी"],
    "GRN No":               ["GRN No",                   "GRN No",                   "GRN No"],
    "Supplier":             ["Supplier",                 "Supplier",                 "Supplier"],
    "Cost ₹":               ["Cost ₹",                   "কেনা ₹",                   "खरीद ₹"],
    "Margin ₹":             ["Margin ₹",                 "Margin ₹",                 "Margin ₹"],
    "Margin %":             ["Margin %",                 "Margin %",                 "Margin %"],
    "Total Profit ₹":       ["Total Profit ₹",           "Total Profit ₹",           "Total Profit ₹"],
    "Cost Value ₹":         ["Cost Value ₹",             "Cost Value ₹",             "Cost Value ₹"],
    "Retail Value ₹":       ["Retail Value ₹",           "Retail Value ₹",           "Retail Value ₹"],
    "Last Sold":            ["Last Sold",                "শেষ বিক্রি",               "आखिरी बिक्री"],
    "Qty(30d)":             ["Qty(30d)",                 "Qty(30d)",                 "Qty(30d)"],
    "Invoice ₹":            ["Invoice ₹",                "Invoice ₹",                "Invoice ₹"],
    "Paid ₹":               ["Paid ₹",                   "Paid ₹",                   "Paid ₹"],
    "Balance ₹":            ["Balance ₹",                "Balance ₹",                "Balance ₹"],
    "Age (days)":           ["Age (days)",               "দিন (Age)",                "दिन (Age)"],
    "Bucket":               ["Bucket",                   "Bucket",                   "Bucket"],
    "Total Due ₹":          ["Total Due ₹",              "Total Due ₹",              "Total Due ₹"],
    "0-30 days ₹":          ["0-30 days ₹",              "0-30 days ₹",              "0-30 days ₹"],
    "31-60 days ₹":          ["31-60 days ₹",             "31-60 days ₹",             "31-60 days ₹"],
    "60+ days ₹":           ["60+ days ₹",               "60+ days ₹",               "60+ days ₹"],
    "Last Txn":             ["Last Txn",                 "Last Txn",                 "Last Txn"],
    "Date Error":           ["Date Error",               "তারিখের ভুল",              "तारीख की भूल"],
    "Enter valid dates in YYYY-MM-DD format.": ["Enter valid dates in YYYY-MM-DD format.", "YYYY-MM-DD format এ সঠিক তারিখ লেখো।", "YYYY-MM-DD format में सही तारीख लिखो।"],
    "No Data":              ["No Data",                  "কোনো Data নেই",            "कोई Data नहीं"],
    "Generate a report first.": ["Generate a report first.", "আগে report তৈরি করো।",      "पहले report बनाओ।"],
    "Missing Library":      ["Missing Library",          "Library নেই",              "Library नहीं है"],
    "Exported":             ["Exported",                 "Export হয়ে গেছে",         "Export हो गया"],
    "Saved to:":            ["Saved to:",                "Saved to:",                "Saved to:"],
    "PDF Exported":         ["PDF Exported",             "PDF Exported",             "PDF Exported"],
    "PDF Error":            ["PDF Error",                "PDF Error",                "PDF Error"],
    "Bills for":            ["Bills for",                "বিল তালিকা -",             "बिल सूची -"],
    "bill(s)   |   Total ₹": ["bill(s)   |   Total ₹",    "বিল   |   মোট ₹",            "बिल   |   कुल ₹"],
    "Bill #":               ["Bill #",                   "Bill #",                   "Bill #"],
    "Time":                 ["Time",                     "সময়",                     "समय"],
    "Show Inactive":        ["Show Inactive",            "Inactive দেখাও",           "Inactive दिखाओ"],
    "Reactivate":           ["Reactivate",               "Reactivate",               "Reactivate"],
    "Deactivate":           ["Deactivate",               "Deactivate",               "Deactivate"],
    "Edit User":            ["Edit User",                "User Edit",                "User Edit"],
    "Add New User":         ["Add New User",             "নতুন User",                "नया User"],
    "Change Password":      ["Change Password",          "Password বদলাও",           "Password बदलो"],
    "New Password *":       ["New Password *",           "নতুন Password *",          "नया Password *"],
    "Confirm Password *":   ["Confirm Password *",       "Password Confirm *",       "Password Confirm *"],
    "Update Password":      ["Update Password",          "Password Update",          "Password Update"],
    "Password changed.":    ["Password changed.",        "Password change হয়েছে।",  "Password change हो गया।"],
    "Passwords do not match.": ["Passwords do not match.",  "Password মেলেনি।",          "Password नहीं मिला।"],
    "Enter at least 4 characters.": ["Enter at least 4 characters.", "কমপক্ষে ৪ অক্ষরের হতে হবে।", "कम से कम 4 अक्षर होने चाहिए।"],
    "User updated.":        ["User updated.",            "User update হয়েছে।",      "User update हो गया।"],
    "User added.":          ["User added.",              "User add হয়েছে।",         "User add हो गया।"],
    "Username already exists.": ["Username already exists.", "এই Username আছে।",         "यह Username पहले से है।"],
    "Name is required.":    ["Name is required.",        "নাম দিতে হবে।",            "नाम देना होगा।"],
    "Username is required.": ["Username is required.",    "Username দিতে হবে।",       "Username देना होगा।"],
    "Password is required.": ["Password is required.",    "Password দিতে হবে।",       "Password देना होगा।"],
    "Admin cannot be deactivated.": ["Admin cannot be deactivated.", "Admin deactive করা যাবে না।", "Admin deactive नहीं कर सकते।"],
    "Deactivated successfully.": ["Deactivated successfully.", "Deactive করা হয়েছে।",       "Deactive कर दिया गया है।"],
    "Reactivated successfully.": ["Reactivated successfully.", "Active করা হয়েছে।",         "Active कर दिया गया है।"],
    "Export CSV":           ["📥  Export CSV",           "📥  CSV Export",           "📥  CSV Export"],
    "Search by user, action, or details...": ["Search by user, action, or details...", "User, action বা details দিয়ে search করো...", "User, action या details से search करो..."],
    "records":              ["records",                  "রেকর্ড",                   "रिकॉर्ड"],
    "Page":                 ["Page",                     "পৃষ্ঠা",                    "पेज"],
    "Previous":             ["◀  Previous",              "◀  আগের",                  "◀  पिछলা"],
    "Next":                 ["Next  ▶",                  "পরের  ▶",                  "अगला  ▶"],
    "Created":              ["Created",                  "তৈরি",                     "बनाया गया"],
    "Deactivate user '{name}'?\nThey will not be able to log in.": [
        "Deactivate user '{name}'?\nThey will not be able to log in.",
        "User '{name}' কে inactive করবে?\nওনারা আর login করতে পারবেন না।",
        "User '{name}' को inactive करोगे?\nवे अब login नहीं कर पाएंगे।"
    ],
}

# ── Internal index map ─────────────────────────────────────────────
_LANG_INDEX = {"English": 0, "Bengali": 1, "Hindi": 2}


def t(key: str, lang: str = "English") -> str:
    """Return the translated string for `key` in the given language.

    Falls back to English if the language or key is not found.
    """
    idx = _LANG_INDEX.get(lang, 0)
    entry = T.get(key)
    if entry and idx < len(entry):
        return entry[idx]
    return key   # fallback: return the key itself (English)

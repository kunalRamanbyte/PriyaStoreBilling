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
    "Dashboard":        ["Dashboard",        "ড্যাশবোর্ড",         "डैशबोर्ड"],
    "New Bill":         ["New Bill",          "নতুন বিল",          "नया बिल"],
    "Bill History":     ["Bill History",      "বিল হিস্ট্রি",       "बिल हिस्ट्री"],
    "Products":         ["Products",          "প্রোডাক্টস",          "प्रोडक्ट्स"],
    "Categories":       ["Categories",        "ক্যাটাগরি",        "कैटेगरी"],
    "Inventory":        ["Inventory",         "ইনভেন্টরি",         "इन्वेंट्री"],
    "Suppliers":        ["Suppliers",         "সাপ্লায়ার্স",         "सप्लायर्स"],
    "Purchase/GRN":     ["Purchase/GRN",      "পারচেজ / জিআরএন",      "परचेज / जीआरएन"],
    "Customers":        ["Customers",         "কাস্টমার্স",         "कस्टमर्स"],
    "Reports":          ["Reports",           "রিপোর্টস",           "रिपोर्ट्स"],
    "Settings":         ["Settings",          "সেটিংস",          "सेटिंग्स"],
    "Users":            ["Users",             "ইউজার্স",             "यूज़र्स"],
    "Activity Log":     ["Activity Log",      "অ্যাক্টিভিটি লগ",      "एक्टिविटी लॉग"],
    "Sign Out":         ["Sign Out",          "বের হও",            "बाहर जाओ"],

    # ══════════════════════════════════════════════════════════════
    # Common buttons / labels
    # ══════════════════════════════════════════════════════════════
    "Save":             ["Save",              "সেভ করো",          "सेव करो"],
    "Cancel":           ["Cancel",            "ক্যান্সেল",            "कैंसिल"],
    "Close":            ["Close",             "বন্ধ করো",          "बंद करो"],
    "Search":           ["Search",            "সার্চ",            "सर्च"],
    "Add":              ["Add",               "অ্যাড করো",           "ऐड करो"],
    "Edit":             ["Edit",              "এডিট করো",          "एडिट करो"],
    "Delete":           ["Delete",            "ডিলিট করো",        "डिलीट करो"],
    "Total":            ["Total",             "মোট",               "कुल"],
    "Grand Total":      ["Grand Total",       "মোট",               "कुल"],
    "Subtotal":         ["Subtotal",          "সাবটোটাল",          "सबटोटल"],
    "Discount":         ["Discount",          "ছাড়",              "छूट"],
    "Quantity":         ["Quantity",           "পরিমাণ",            "मात्रा"],
    "Price":            ["Price",             "দাম",               "दाम"],
    "Amount Paid":      ["Amount Paid",       "টাকা দিয়েছে",       "पैसा दिया"],
    "Change Due":       ["Change Due",        "ফেরত",              "वापसी"],
    "Ready":            ["Ready",             "তৈয়ার",             "तैयार"],
    "Today":            ["Today",             "আজকে",              "आज"],
    "All":              ["All",               "সব",                "सब"],
    "Filter":           ["Filter",            "ফিল্টার",           "फ़िल्टर"],
    "From:":            ["From:",             "থেকে:",             "से:"],
    "To:":              ["To:",               "পর্যন্ত:",           "तक:"],
    "Status":           ["Status",            "অবস্থা",            "स्थिति"],
    "Date":             ["Date",              "তারিখ",             "तैयार तारीख"],
    "Name":             ["Name",              "নাম",               "नाम"],
    "Phone":            ["Phone",             "ফোন",               "फ़ोन"],
    "Address":          ["Address",           "ঠিকানা",            "पता"],
    "Yes":              ["Yes",               "হ্যাঁ",              "हाँ"],
    "No":               ["No",                "না",                "नहीं"],
    "OK":               ["OK",                "ওকে",                "ओके"],
    "Error":            ["Error",             "এরর",             "एरर"],
    "Warning":          ["Warning",           "ওয়ার্নিং",           "वार्निंग"],
    "Required":         ["Required",          "প্রয়োজনীয়",          "ज़रूरी"],

    # ══════════════════════════════════════════════════════════════
    # Header / App
    # ══════════════════════════════════════════════════════════════
    "Exit the billing system?":
        ["Exit the billing system?",
         "বিলিং সিস্টেম বন্ধ করবে?",
         "बिलिंग सिस्टम बंद करोगे?"],
    "Exit":              ["Exit",              "বন্ধ করো",              "बंद करो"],
    "Logout":            ["Logout",            "লগআউট",            "लॉगआउट"],
    "Are you sure you want to logout?":
        ["Are you sure you want to logout?",
         "সত্যিই লগআউট করবে?",
         "सच में लॉगआउट करोगे?"],

    # ══════════════════════════════════════════════════════════════
    # Dashboard
    # ══════════════════════════════════════════════════════════════
    "Today's Sales":        ["Today's Sales",        "আজকের বিক্রি",       "आज की बिक्री"],
    "Bills Today":          ["Bills Today",          "আজকের বিল",          "आज के बिल"],
    "Low Stock Items":      ["Low Stock Items",      "কম স্টক",            "कम स्टॉक"],
    "Expiring (30 days)":   ["Expiring (30 days)",   "মেয়াদ শেষ হচ্ছে (৩০ দিন)", "एक्सपायर हो रहा (30 दिन)"],
    "Discount Given":       ["Discount Given",       "ডিসকাউন্ট দিয়েছ",      "डिस्काउंट दिया"],
    "Quick Actions":        ["Quick Actions",        "তাড়াতাড়ি কাজ",       "क्विक एक्शन"],
    "New Bill_qa":          ["🧾\nNew Bill",          "🧾\nনতুন বিল",        "🧾\nनया बिल"],
    "Add Product_qa":       ["📦\nAdd Product",       "📦\nপ্রোডাক্ট অ্যাড",     "📦\nप्रोडक्ट ऐड"],
    "Bill History_qa":      ["📋\nBill History",      "📋\nবিল হিস্ট্রি",     "📋\nबिल हिस्ट्री"],
    "Categories_qa":        ["🏷️\nCategories",       "🏷️\nক্যাটাগরি",     "🏷️\nकैटेगरी"],
    "Products Expiring Within 30 Days":
        ["Products Expiring Within 30 Days",
         "৩০ দিনে মেয়াদ শেষ হচ্ছে",
         "30 दिन में एक्सपायर हो रहा"],
    "Product Name":         ["Product Name",         "প্রোডাক্টের নাম",      "प्रोडक्ट का नाम"],
    "Category":             ["Category",             "ক্যাটাগরি",            "कैटेगरी"],
    "Stock":                ["Stock",                "স্টক",                "स्टॉक"],
    "Expiry Date":          ["Expiry Date",          "মেয়াদ শেষের তারিখ",         "एक्सपायरी तारीख"],
    "Days Left":            ["Days Left",            "বাকি দিন",            "बाकी दिन"],
    "Recent Bills":         ["Recent Bills",         "সাম্প্রতিক বিল",          "हाल के बिल"],
    "Bill No.":             ["Bill No.",             "বিল নম্বর",            "बिल नंबर"],
    "Date & Time":          ["Date & Time",          "তারিখ ও সময়",        "तैयार और समय"],
    "Customer":             ["Customer",             "কাস্টমার",            "ग्राहक"],
    "Amount (₹)":           ["Amount (₹)",           "টাকা (₹)",            "रकम (₹)"],
    "Mode":                 ["Mode",                 "মোড",                 "मोड"],

    # ══════════════════════════════════════════════════════════════
    # Billing Screen
    # ══════════════════════════════════════════════════════════════
    "Bright Billing Dashboard":
        ["Bright Billing Dashboard",
         "বিলিং ড্যাশবোর্ড",
         "बिलिंग डैशबोर्ड"],
    "Cart is empty.\nSearch and add products above.":
        ["🛒\n\nCart is empty.\nSearch and add products above.",
         "🛒\n\nকার্ট খালি আছে।\nউপরে সার্চ করে প্রোডাক্ট অ্যাড করো।",
         "🛒\n\nकार्ट खाली है।\nऊपर सर्च करके प्रोडक्ट ऐड करो।"],
    "Product Name_col":     ["Product Name",         "প্রোডাক্ট",             "प्रोडक्ट"],
    "Unit":                 ["Unit",                 "ইউনিট",               "यूनिट"],
    "Qty":                  ["Qty",                  "পরিমাণ",              "मात्रा"],
    "Price ₹":              ["Price ₹",              "দাম ₹",               "दाम ₹"],
    "Disc ₹":               ["Disc ₹",               "ছাড় ₹",              "छूट ₹"],
    "Total ₹":              ["Total ₹",              "মোট ₹",               "कुल ₹"],
    "Summary":              ["Summary",              "হিসাব",               "हिसाब"],
    "Subtotal :":           ["Subtotal :",           "সাবটোটাল :",          "सबटोटल :"],
    "Discount (₹) :":      ["Discount (₹) :",       "ছাড় (₹) :",          "छूट (₹) :"],
    "TOTAL":                ["TOTAL",                "মোট",                 "कुल"],
    "Bill Discount (₹):":  ["Bill Discount (₹):",   "বিল ছাড় (₹):",       "बिल छूट (₹):"],
    "Payment Mode":         ["Payment Mode",         "পেমেন্ট",             "पेमेंट"],
    "Cash Received (₹)":   ["Cash Received (₹)",    "Cash পেয়েছ (₹)",     "Cash मिला (₹)"],
    "Change Due :":         ["Change Due :",         "ফেরত :",              "वापसी :"],
    "F10 Print & Save":     ["F10 Print & Save",     "F10 ছাপাও ও সেভ",   "F10 छापो और सेव"],
    "F8 Hold Bill":         ["F8 Hold Bill",         "F8 বিল হোল্ড",         "F8 बिल होल्ड"],
    "ESC Clear Cart":       ["ESC Clear Cart",       "ESC কার্ট খালি",       "ESC कार्ट खाली"],
    "Walk-in":              ["Walk-in",              "ওয়াক-ইন (Walk-in)",             "वॉक-इन (Walk-in)"],
    "Customer: Search or type customer name...":
        ["Customer: Search or type customer name...",
         "কাস্টমার: নাম সার্চ করো...",
         "ग्राहक: नाम सर्च करो..."],
    "Scan barcode or search product…   (F2)":
        ["🔍  Scan barcode or search product…   (F2)",
         "🔍  বারকোড স্ক্যান বা প্রোডাক্ট সার্চ করো…   (F2)",
         "🔍  बारकोड स्कैन या प्रोडक्ट सर्च करो…   (F2)"],
    "Add New Customer":     ["Add New Customer",     "নতুন কাস্টমার",       "नया ग्राहक"],
    "Name *":               ["Name *",               "নাম *",               "नाम *"],
    "Full name":            ["Full name",            "পুরো নাম",            "पूरा नाम"],
    "Mobile number":        ["Mobile number",        "মোবাইল নম্বর",       "मोबाइल नंबर"],
    "Shop / area":          ["Shop / area",          "দোকান / এলাকা",         "दुकान / इलाका"],
    "Save Customer":        ["✅  Save Customer",     "✅  সেভ করো",        "✅  सेव करो"],
    "Prev. Udhaar":         ["⚠️  Prev. Udhaar :",    "⚠️  আগের বাকি :",     "⚠️  पिछला उधार :"],
    "Empty Cart":           ["Empty Cart",           "কার্ট খালি",           "कार्ट खाली"],
    "Please add at least one product to the bill.":
        ["Please add at least one product to the bill.",
         "বিলে কমপক্ষে একটা প্রোডাক্ট অ্যাড করো।",
         "बिल में कम से कम एक प्रोडक्ट ऐड करो।"],
    "Clear Cart":           ["Clear Cart",           "কার্ট খালি করো",       "कार्ट खाली करो"],
    "Clear all items from cart?":
        ["Clear all items from cart?",
         "কার্টের সব আইটেম মুছবে?",
         "कार्ट के सब आइटम हटाओगे?"],
    "Bill saved successfully!":
        ["✅  Bill saved successfully!",
         "✅  বিল সেভ হয়ে গেছে!",
         "✅  बिल सेव हो गया!"],
    "Cart cleared.":        ["🗑️  Cart cleared.",     "🗑️  কার্ট খালি।",      "🗑️  कार्ट खाली।"],
    "Bill Held":            ["Bill Held",            "বিল হোল্ড",            "बिल होल्ड"],
    "Bill saved as draft.\nYou can resume it from Bill History.":
        ["Bill saved as draft.\nYou can resume it from Bill History.",
         "বিল ড্রাফট হিসেবে সেভ।\nবিল হিস্ট্রি থেকে রিজুম করতে পারো।",
         "बिल ड्राफ्ट सेव हुआ।\nबिल हिस्ट्री से रिज्यूम कर सकते हो।"],
    "Bill held. Cart cleared for next bill.":
        ["✋  Bill held. Cart cleared for next bill.",
         "✋  বিল হোল্ড। কার্ট খালি।",
         "✋  बिल होल्ड। कार्ट खाली।"],
    "New Bill_confirm":     ["New Bill",              "নতুন বিল",            "नया बिल"],
    "Start a new bill? Current cart items will be cleared.":
        ["Start a new bill? Current cart items will be cleared.",
         "নতুন বিল শুরু করবে? কার্টের সব আইটেম মুছে যাবে।",
         "नया बिल शुरू करोगे? कार्ट के सब आइटम हट जाएंगे।"],
    "Insufficient Stock":   ["Insufficient Stock",   "স্টক কম",            "स्टॉक कम"],
    "Remove Item":          ["Remove Item",          "Item সরাও",           "Item हटाओ"],
    "Bill Receipt":         ["Bill Receipt",         "বিল রিসিট",        "बिल रसीद"],
    "Thank you for shopping with us!":
        ["Thank you for shopping with us!  🙏",
         "আমাদের থেকে কেনার জন্য ধন্যবাদ!  🙏",
         "हमसे खरीदारी करने के लिए धन्यवाद!  🙏"],
    "Thermal Print":        ["🖨  Thermal Print",     "🖨  থার্মাল প্রিন্ট",   "🖨  थर्मल प्रिंट"],
    "PDF / A4":             ["📄  PDF / A4",          "📄  পিডিএফ / A4",        "📄  पीडीएफ / A4"],
    "Done":                 ["✅  Done",              "✅  হয়ে গেছে",            "✅  हो गया"],
    "Update":               ["✅  Update",            "✅  আপডেট",          "✅  अपडेट"],
    "Remove":               ["🗑️  Remove",            "🗑️  সরাও",           "🗑️  हटाओ"],
    "GRAND TOTAL:":         ["GRAND TOTAL:",          "মোট:",                "कुल:"],
    "TOTAL TO COLLECT:":    ["TOTAL TO COLLECT:",     "মোট নিতে হবে:",       "कुल लेना है:"],
    "Amount Paid:":         ["Amount Paid:",          "টাকা দিয়েছে:",        "पैसा दिया:"],
    "Change Due:":          ["Change Due:",           "ফেরত:",              "वापसी:"],
    "Subtotal:":            ["Subtotal:",             "সাবটোটাল:",           "सबटोटल:"],
    "Discount:":            ["Discount:",             "ছাড়:",               "छूट:"],
    "Item":                 ["Item",                  "আইটেম",               "आइटम"],
    "Rate":                 ["Rate",                  "দাম",                 "दाम"],
    "Disc":                 ["Disc",                  "ছাড়",                "छूट"],
    "Amt":                  ["Amt",                   "টাকা",                "रकम"],
    "Select Customer":      ["Select Customer",       "কাস্টমার বাছো",       "ग्राहक चुनो"],

    # ══════════════════════════════════════════════════════════════
    # Bill History
    # ══════════════════════════════════════════════════════════════
    "Bill no. or customer name":
        ["Bill no. or customer name",
         "বিল নম্বর বা কাস্টমার নাম",
         "बिल नंबर या ग्राहक नाम"],
    "bill(s) found":        ["{n} bill(s) found",    "{n} বিল পাওয়া গেছে",  "{n} बिल मिले"],
    "View Bill":            ["👁️  View Bill",         "👁️  বিল দেখো",        "👁️  बिल देखो"],
    "Reprint":              ["🖨️  Reprint",           "🖨️  রিপ্রিন্ট",         "🖨️  रीप्रिंट"],
    "Resume Draft":         ["▶️  Resume Draft",      "▶️  ড্রাফট রিজুম",    "▶️  ड्राफ्ट रिज्यूम"],
    "Void Bill":            ["❌  Void Bill",          "❌  বিল বাতিল",         "❌  बिल निरस्त (Void)"],
    "Select Bill":          ["Select Bill",           "বিল সিলেক্ট করো",     "बिल सिलेक्ट करो"],
    "Please select a bill first.":
        ["Please select a bill first.",
         "আগে একটা বিল সিলেক্ট করো।",
         "पहले एक बिल सिलेक्ट करो।"],
    "Voided Bill":          ["Voided Bill",           "বাতিল বিল",          "निरस्त बिल"],
    "This bill has been voided and cannot be reprinted.":
        ["This bill has been voided and cannot be reprinted.",
         "এই বিল বাতিল হয়ে গেছে, রিপ্রিন্ট হবে না।",
         "यह बिल निरस्त हो चुका है, रीप्रिंट नहीं होगा।"],
    "Items":                ["Items",                 "আইটেমসমূহ",               "आइटम्स"],
    "Paid:":                ["Paid:",                 "দিয়েছে:",             "दिया:"],
    "TOTAL:":               ["TOTAL:",                "মোট:",              "कुल:"],
    "Void Reason":          ["Void Reason",           "বাতিল করার কারণ",         "निरस्त करने का कारण"],
    "Cannot Void":          ["Cannot Void",           "বাতিল করা যাবে না",    "निरस्त नहीं हो सकता"],
    "Confirm Void":         ["Confirm Void",          "বাতিল নিশ্চিত করো",        "निरस्त सुनिश्चित करें"],
    "Voided":               ["Voided",                "বাতিল হয়েছে",              "निरस्त हुआ"],
    "Not a Draft":          ["Not a Draft",           "ড্রাফট নয়",            "ड्राफ्ट नहीं"],

    # ══════════════════════════════════════════════════════════════
    # Product Master
    # ══════════════════════════════════════════════════════════════
    "Product Master":       ["📦   Product Master",    "📦   প্রোডাক্ট মাস্টার", "📦   प्रोडक्ट मास्टर"],
    "Add New Product":      ["➕  Add New Product",    "➕  নতুন প্রোডাক্ট",    "➕  नया प्रोडक्ट"],
    "Search products...":   ["Search products...",    "প্রোডাক্ট সার্চ করো...", "प्रोडक्ट सर्च करो..."],
    "All Categories":       ["All Categories",        "সব ক্যাটাগরি",       "सब कैटेगरी"],
    "Sell ₹":               ["Sell ₹",                "বিক্রি ₹",            "बिक्री ₹"],
    "Purchase ₹":           ["Purchase ₹",            "কেনা ₹",              "खरीद ₹"],
    "Active":               ["Active",                "সক্রিয়",              "सक्रिय"],
    "product(s)":           ["{n} product(s)",        "{n} টি প্রোডাক্ট",         "{n} प्रोडक्ट"],
    "Add Product":          ["Add Product",           "প্রোডাক্ট অ্যাড",         "प्रोडक्ट ऐड"],
    "Edit Product":         ["Edit Product",          "প্রোডাক্ট এডিট",        "प्रोडक्ट एडिट"],
    "Category *":           ["Category *",            "ক্যাটাগরি *",          "कैटेगरी *"],
    "Product Name *":       ["Product Name *",        "প্রোডাক্টের নাম *",       "प्रोडक्ट का नाम *"],
    "HSN Code":             ["HSN Code",              "এইচএসএন কোড",            "एचएसएन कोड"],
    "Barcode":              ["Barcode",               "বারকোড",             "बारकोड"],
    "Unit *":               ["Unit *",                "ইউনিট *",              "यूनिट *"],
    "Selling Price *":      ["Selling Price *",       "বিক্রি মূল্য *",        "बिक्री मूल्य *"],
    "Purchase Price":       ["Purchase Price",        "ক্রয় মূল্য",            "क्रय मूल्य"],
    "Opening Stock":        ["Opening Stock",         "শুরুর স্টক",          "शुरुआती स्टॉक"],
    "Min Stock Alert":      ["Min Stock Alert",       "কম স্টকের অ্যালার্ট",     "न्यूनतम स्टॉक अलर्ट"],
    "Save Product":         ["💾  Save Product",       "💾  প্রোডাক্ট সেভ করো",        "💾  प्रोडक्ट सेव करो"],
    "Deactivate":              ['Deactivate', 'নিষ্ক্রিয় করো', 'निष्क्रिय करें'],
    "Activate":             ["Activate",              "সক্রিয় করো",            "सक्रिय करें"],

    # ══════════════════════════════════════════════════════════════
    # Category Manager
    # ══════════════════════════════════════════════════════════════
    "Category Manager":     ["🏷️   Category Manager",  "🏷️   ক্যাটাগরি ম্যানেজার", "🏷️   कैटेगरी मैनेजर"],
    "All Categories_list":  ["All Categories",         "সব ক্যাটাগরি",        "सब कैटेगरी"],
    "Add / Edit Category":  ["Add / Edit Category",    "ক্যাটাগরি অ্যাড / এডিট",  "कैटेगरी ऐड / एडिट"],
    "Category Name *":      ["Category Name *",        "ক্যাটাগরির নাম *",       "कैटेगरी का नाम *"],
    "Colour Code":          ["Colour Code",            "কালার কোড",          "कलर कोड"],
    "Custom:":              ["Custom:",                "কাস্টম:",              "कस्टम:"],
    "Pick Colour":          ["🎨 Pick Colour",          "🎨 রঙ বাছো",       "🎨 रंग चुनो"],
    "Save Category":        ["💾  Save Category",       "💾  ক্যাটাগরি সেভ করো",         "💾  कैटेगरी सेव करो"],
    "Reset / New":          ["🔄  Reset / New",         "🔄  রিসেট / নতুন",     "🔄  रीसेट / नया"],
    "No categories yet.\nAdd one using the form →":
        ["No categories yet.\nAdd one using the form →",
         "এখনো কোনো ক্যাটাগরি নেই।\nফর্ম থেকে অ্যাড করো →",
         "अभी कोई कैटेगरी नहीं।\nफॉर्म से ऐड करो →"],
    "(Inactive)":           ["(Inactive)",             "(নিষ্ক্রিয়)",           "(निष्क्रिय)"],
    "Category name is required.":
        ["⚠  Category name is required.",
         "⚠  ক্যাটাগরির নাম দিতে হবে।",
         "⚠  कैटेगरी का नाम देना होगा।"],

    # ══════════════════════════════════════════════════════════════
    # Inventory
    # ══════════════════════════════════════════════════════════════
    "Inventory Overview":   ["📊   Inventory Overview", "📊   স্টক ওভারভিউ",       "📊   स्टॉक ओवरव्यू"],
    "Current Stock":        ["Current Stock",           "এখনকার স্টক",         "अभी का स्टॉक"],
    "Low Stock":            ["⚠️  Low Stock",            "⚠️  কম স্টক",         "⚠️  कम स्टॉक"],
    "Out of Stock":         ["🚫  Out of Stock",         "🚫  স্টক নেই",        "🚫  स्टॉक नहीं"],
    "All Stock":            ["All Stock",               "সব স্টক",             "सब स्टॉक"],
    "Export Excel":         ["📥  Export Excel",         "📥  এক্সেল এক্সপোর্ট",     "📥  एक्सेल एक्सपोर्ट"],
    "Adjust Stock":         ["🔧  Adjust Stock",        "🔧  স্টক ঠিক করো",   "🔧  स्टॉक ठीक करो"],
    "Stock Adjustment":     ["Stock Adjustment",        "স্টক অ্যাডजাস্টমেন্ট",    "स्टॉक एडजस्टमेंट"],
    "New Qty *":            ["New Qty *",               "নতুন পরিমাণ *",          "नई मात्रा *"],
    "Reason *":             ["Reason *",                "কারণ *",              "कारण *"],
    "Apply Adjustment":     ["Apply Adjustment",        "অ্যাডজাস্ট করো",           "एडजस्ट करो"],

    # ══════════════════════════════════════════════════════════════
    # Suppliers
    # ══════════════════════════════════════════════════════════════
    "Supplier Master":      ["🏭   Supplier Master",    "🏭   সাপ্লায়ার মাস্টার", "🏭   सप्लायर मास्टर"],
    "Add Supplier":         ["➕  Add Supplier",        "➕  নতুন সাপ্লায়ার",    "➕  नया सप्लायर"],
    "Supplier Name":           ['Supplier Name', 'সাপ্লায়ারের নাম', 'सप्लायर का नाम'],
    "Contact Person":          ['Contact Person', 'যোগাযোগের ব্যক্তি', 'संपर्क व्यक्ति'],
    "GST Number":              ['GST Number', 'জিএসটি নম্বর', 'जीएसटी नंबर'],
    "Save Supplier":        ["💾  Save Supplier",       "💾  সাপ্লায়ার সেভ করো",         "💾  सप्लायर सेव करो"],

    # ══════════════════════════════════════════════════════════════
    # Purchase / GRN
    # ══════════════════════════════════════════════════════════════
    "New Purchase / GRN":   ["🛒   New Purchase / GRN", "🛒   নতুন কেনাকাটা / জিআরএন", "🛒   नया खरीद / जीआरएन"],
    "Select Supplier *":    ["Select Supplier *",       "সাপ্লায়ার বাছো *",      "सप्लायर चुनो *"],
    "Invoice / Ref No.":    ["Invoice / Ref No.",       "ইনভয়েস নম্বর",    "इनवॉइस नंबर"],
    "Select product from existing or search":
        ["Select product from existing or search",
         "প্রোডাক্ট সার্চ করো বা বাছো",
         "प्रोडक्ट सर्च करो या चुनो"],
    "Add New Item":         ["➕ Add New Item",          "➕ নতুন আইটেम",         "➕ नया आइटम"],
    "Add to Purchase":      ["➕  Add to Purchase",     "➕  পারচেজে অ্যাড করো",   "➕  परचेज में ऐड करो"],
    "Save GRN":             ["💾  Save GRN",            "💾  জিআরএন সেভ করো",         "💾  जीआरएन सेव करो"],
    "Clear All":            ["🗑  Clear All",            "🗑  সব মুছে ফেলো",           "🗑  सब हटाएँ"],
    "Purchase Items":       ["Purchase Items",          "কেনা আইটেমসমূহ",       "खरीदे गए आइटम"],
    "Unit Price ₹":         ["Unit Price ₹",            "প্রতি ইউনিটের দাম ₹",                "प्रति यूनिट दाम ₹"],
    "Line Total":           ["Line Total",              "লাইন টোটাল",           "लाइन कुल"],

    # ══════════════════════════════════════════════════════════════
    # Customers
    # ══════════════════════════════════════════════════════════════
    "Customer Master":      ["👥   Customer Master",    "👥   কাস্টমার মাস্টার", "👥   ग्राहक मास्टर"],
    "Add Customer":         ["➕  Add Customer",        "➕  নতুন কাস্টমার",    "➕  नया ग्राहक"],
    "Search customers...":  ["Search customers...",     "কাস্টমার সার্চ করো...", "ग्राहक सर्च करो..."],
    "Customer Name":        ["Customer Name",           "কাস্টমার নাম",         "ग्राहक नाम"],
    "Credit Balance":       ["Credit Balance",          "বাকি টাকা",            "बाकी पैसा"],
    "Save Customer_btn":    ["💾  Save Customer",       "💾  সেভ কাস্টমার",         "💾  सेव ग्राहक"],
    "Change Balance":       ["Change Balance",          "চেঞ্জ ব্যালেন্স",        "चेंज बैलेंस"],
    "Change Used":          ["Change Used",             "চেঞ্জ ব্যবহার",         "चेंज उपयोग"],
    "Change Available":     ["Change Available",        "চেঞ্জ আছে",           "चेंज उपलब्ध"],
    "Change Balance Detected": ["Change Balance Detected",  "চেঞ্জ ব্যালেন্স পাওয়া গেছে", "चेंज बैलेंस मिला"],
    "Change Deposit":       ["Change Deposit",          "চেঞ্জ জমা",           "चेंज जमा"],
    "Change Cleared":       ["Change Cleared",          "চেঞ্জ পরিশোধ",         "चेंज क्लियर"],
    "Clear Change":         ["Clear Change",            "চেঞ্জ ক্লিয়ার",         "चेंज क्लियर"],
    "Only admins can clear the change balance.": ["Only admins can clear the change balance.", "শুধুমাত্র অ্যাডমিনরাই চেঞ্জ ব্যালেন্স ক্লিয়ার করতে পারবেন।", "केवल एडमिन ही चेंज बैलेंस क्लियर कर सकते हैं।"],
    "Are you sure you want to clear change balance of ₹{bal:,.2f} for '{name}'?": ["Are you sure you want to clear change balance of ₹{bal:,.2f} for '{name}'?", "আপনি কি নিশ্চিত যে আপনি '{name}'-এর জন্য ₹{bal:,.2f} চেঞ্জ ব্যালেন্স ক্লিয়ার করতে চান?", "क्या आप वाकई '{name}' के लिए ₹{bal:,.2f} का चेंज बैलेंस clear करना चाहते हैं?"],
    "Customer has no change balance to clear.": ["Customer has no change balance to clear.", "কাস্টমারের ক্লিয়ার করার মতো কোনো চেঞ্জ ব্যালেন্স নেই।", "ग्राहक के पास क्लियर करने के लिए कोई चेंज बैलेंस नहीं है।"],

    # ══════════════════════════════════════════════════════════════
    # Reports
    # ══════════════════════════════════════════════════════════════
    "Reports & Analytics":  ["📈   Reports & Analytics", "📈   রিপোর্ট ও অ্যানালিটিক্স",        "📈   रिपोर्ट और एनालिसिस"],
    "Sales Summary":        ["Sales Summary",           "বিক্রি সামারি",       "बिक्री समरी"],
    "Total Sales":          ["Total Sales",             "মোট বিক্রি",           "कुल बिक्री"],
    "Total Bills":          ["Total Bills",             "মোট বিল",              "कुल बिल"],
    "Total Discount":       ["Total Discount",          "মোট ডিসকাউন্ট",        "कुल डिस्काउंट"],
    "Avg Bill Value":       ["Avg Bill Value",          "গড় বিলের পরিমাণ",          "औसत बिल राशि"],
    "Top Products":         ["Top Products",            "সেরা প্রোডাক্টসমূহ",         "टॉप प्रोडक्ट्स"],
    "Generate Report":      ["Generate Report",         "রিপোর্ট তৈরি করো",         "रिपोर्ट तैयार करें"],
    "Daily":                ["Daily",                   "দিনের",                "दिन का"],
    "Weekly":               ["Weekly",                  "সাপ্তাহিক",             "साप्ताहिक"],
    "Monthly":              ["Monthly",                 "মাসের",                "महीने का"],
    "Yearly":               ["Yearly",                  "বছরের",                "साल का"],

    # ══════════════════════════════════════════════════════════════
    # Settings
    # ══════════════════════════════════════════════════════════════
    "Settings & Configuration":
        ["⚙️   Settings & Configuration",
         "⚙️   সেটিংস ও কনফিগারেশন",
         "⚙️   सेटिंग्स और कॉन्फ़िगरेशन"],
    "Shop Information":     ["🏪  Shop Information",     "🏪  দোকানের তথ্য",        "🏪  दुकान की जानकारी"],
    "Bill Configuration":   ["🧾  Bill Configuration",   "🧾  বিল কনফিগারেশন",      "🧾  बिल कॉन्फ़िगरेशन"],
    "Backup & Restore":     ["💾  Backup & Restore",     "💾  ব্যাকআপ ও রিস্টোর", "💾  बैकअप और रीस्टोर"],
    "Last Backup":          ["Last Backup",              "শেষ ব্যাকআপ",           "आखिरी बैकअप"],
    "Backup Now":           ["🔄  Backup Now",           "🔄  ব্যাকআপ নিন",       "🔄  बैकअप लें"],
    "Backup Folder":        ["Backup Folder",            "ব্যাকআপ ফোল্ডার",        "बैकअप फ़ोल्डर"],
    "Default (app folder)": ["Default (app folder)",     "ডিফল্ট (অ্যাপ ফোল্ডার)", "डिफ़ॉल्ट (ऐप फ़ोल्डर)"],
    "Choose Folder":        ["📂  Choose Folder",        "📂  ফোল্ডার বাছো",      "📂  फ़ोल्डर चुनें"],
    "Reset to Default":     ["🗑  Reset to Default",     "🗑  ডিফল্ট রিসেট করো",       "🗑  डिफ़ॉल्ट रीसेट करो"],
    "Daily Auto-Backup":    ["Daily Auto-Backup",        "প্রতিদিনের অটো-ব্যাকআপ",    "रोजाना ऑटो-ব্যাকअप"],
    "Auto backup description":
        ["Automatically backup once every 24 hours while the app is open",
         "অ্যাপ খোলা থাকলে প্রতি ২৪ ঘণ্টায় অটো-ব্যাকআপ হবে",
         "ऐप खुला रहने पर हर 24 घंटे में ऑटो-ব্যাকअप होगा"],
    "Restore from Backup":  ["Restore from Backup",      "ব্যাকআপ থেকে রিস্টোর", "बैकअप से रीस्टोर"],
    "Restore description":
        ["Replace current data with a previous backup file (.db)",
         "আগের ব্যাকআপ ফাইল (.db) দিয়ে ডেটা প্রতিস্থাপন হবে",
         "पिछली बैकअप फ़ाइल (.db) से डेटा रिप्लेस होगा"],
    "Restore Backup":       ["♻️  Restore Backup",       "♻️  ব্যাকআপ রিস্টোর করো",      "♻️  बैकअप रीस्टोर करें"],
    "Save Settings":        ["💾   Save Settings",       "💾   সেটিংস সেভ করো",   "💾   सेटिंग्स सेव करें"],
    "No backup yet":        ["No backup yet",            "কোনো ব্যাকআপ নেই",    "कोई बैकअप नहीं"],
    "Saved":                ["Saved",                    "সেভ হয়েছে",          "सेव हो गया"],
    "Settings saved successfully!":
        ["Settings saved successfully!",
         "সেটিংস সেভ হয়ে গেছে!",
         "सेटिंग्स सेव हो गई हैं!"],
    "Language":             ["🌐  Language",              "🌐  ভাষা",              "🌐  भाषा"],
    "Select Language":      ["Select Language",          "ভাষা বাছো",            "भाषा चुनें"],

    # ══════════════════════════════════════════════════════════════
    # Users
    # ══════════════════════════════════════════════════════════════
    "User Management":      ["👤   User Management",     "👤   ইউজার ম্যানেজমেন্ট", "👤   यूज़र मैनेजमेंट"],
    "Add User":             ["➕  Add User",              "➕  নতুন ইউজার",        "➕  नया यूज़र"],
    "Username":             ["Username",                  "ইউজারনেম",             "यूज़रनेम"],
    "Password":             ["Password",                  "পাসওয়ার্ড",             "पासवर्ड"],
    "Role":                 ["Role",                      "রোল / ভূমিকা",                 "रोल / भूमिका"],
    "Save User":            ["💾  Save User",             "💾  ইউজার সেভ করো",         "💾  यूज़र सेव करो"],

    # ══════════════════════════════════════════════════════════════
    # Activity Log
    # ══════════════════════════════════════════════════════════════
    "Activity Log_heading":  ["📋   Activity Log",        "📋   অ্যাক্টিভিটি লগ",    "📋   एक्टिविटी लॉग"],
    "Action":                ["Action",                   "অ্যাকশন / কাজ",               "एक्शन / कार्य"],
    "Details":               ["Details",                  "বিস্তারিত তথ্য",              "विवरण"],
    "User":                  ["User",                     "ইউজার",                 "यूज़र"],
    "Timestamp":             ["Timestamp",                "সময়কাল (টাইমস্ট্যাম্প)",            "समय (टाइमस्टैम्प)"],

    # ══════════════════════════════════════════════════════════════
    # Login
    # ══════════════════════════════════════════════════════════════
    "Login":                ["Login",                    "লগইন",                "लॉगिन"],
    "Sign In":              ["Sign In",                  "সাইন ইন করো",          "साइन इन करें"],

    # ══════════════════════════════════════════════════════════════
    # Field labels from Settings
    # ══════════════════════════════════════════════════════════════
    "Shop Name *":          ["Shop Name *",              "দোকানের নাম *",           "दुकान का नाम *"],
    "Shop Address":         ["Address",                  "ঠিকানা",              "पता"],
    "City":                 ["City",                     "শহর / সিটি",                 "शहर / सिटी"],
    "GST Number_setting":   ["GST Number",               "জিএসটি নম্বর",           "जीएसटी नंबर"],
    "Bill Prefix *":        ["Bill Prefix *",            "বিল প্রিফিক্স *",        "बिल प्रीफ़िक्स *"],
    "Next Bill Number *":   ["Next Bill Number *",       "পরবর্তী বিল নম্বর *",   "अगला बिल नंबर *"],
    "Thermal Paper Width":  ["Thermal Paper Width",      "থার্মাল পেপার চওড়া (উইডথ)",  "थर्मल पेपर चौड़ाई"],

    # ── Additional Keys for Remaining Screens ──
    "Customers & Udhaar":   ["👥   Customers & Udhaar", "👥   কাস্টমার ও বাকি (উধার)", "👥   ग्राहक और उधार"],
    "Add New Customer":     ["➕  Add New Customer",    "➕  নতুন কাস্টমার",    "➕  नया ग्राहक"],
    "Total Customers":      ["👥  Total Customers",      "👥  মোট কাস্টমার",      "👥  कुल ग्राहक"],
    "Total Udhaar":         ["💳  Total Udhaar",         "💳  মোট উধার / বাকি",         "💳  कुल उधार"],
    "Credit Accounts":      ["📋  Credit Accounts",      "📋  বাকি অ্যাকাউন্ট",      "📋  उधार अकाउंट"],
    "Search by name or phone…": ["Search by name or phone…", "নাম বা ফোন দিয়ে সার্চ করো...", "नाम या फोन से सर्च करो..."],
    "Udhaar Balance":       ["Udhaar Balance",           "বাকি ব্যালেন্স",            "उधार बैलेंस"],
    "✏️  Edit":              ["✏️  Edit",                 "✏️  এডিট",                 "✏️  एडिट"],
    "📖  View Ledger":       ["📖  View Ledger",          "📖  লেজার দেখো",          "📖  लेजर देखें"],
    "🖨️  Print Ledger":      ["🖨️  Print Ledger",         "🖨️  লেজার প্রিন্ট",         "🖨️  लेजर प्रिंट"],
    "💳  Add Payment":       ["💳  Add Payment",          "💳  পেমেন্ট অ্যাড করো",          "💳  पेमेंट ऐड करें"],
    "📝  Add Udhaar":        ["📝  Add Udhaar",           "📝  উধার অ্যাড করো",           "📝  उधार ऐड करें"],
    "🗑️  Delete":            ["🗑️  Delete",               "🗑️  ডিলিট",               "🗑️  डिलीट"],
    "{n} customer(s) found": ["{n} customer(s) found",    "{n} জন কাস্টমার পাওয়া গেছে",  "{n} ग्राहक मिले"],
    "Edit Customer":        ["Edit Customer",            "কাস্টমার এডিট",            "ग्राहक एडिट"],
    "Full Name":            ["Full Name",                "পুরো নাম",                "पूरा नाम"],
    "Full Name *":          ["Full Name *",              "পুরো নাম *",              "पूरा नाम *"],
    "Phone *":              ["Phone *",                  "ফোন নম্বর *",                  "फ़ोन नंबर *"],
    "Address *":            ["Address *",                "ঠিকানা *",                "पता *"],
    "Customer name is required.": ["Customer name is required.", "কাস্টমারের নাম দিতে হবে", "ग्राहक का नाम देना होगा"],
    "Record Payment":       ["Record Payment",           "পেমেন্ট রেকর্ড করো",           "पेमेंट रिकॉर्ड करें"],
    "Add Udhaar (Credit)":  ["Add Udhaar (Credit)",      "উধার / বাকি লিখুন",               "उधार लिखें"],
    "Current Balance":      ["Current Balance",          "বাকি টাকা",               "बाकी पैसा"],
    "Supplier Payables":    ["Supplier Payables",        "সাপ্লায়ার দেনা (Payables)",  "सप्लायर देनदारी (Payables)"],
    "Customer Ageing":      ["Customer Ageing",          "কাস্টমার বাকি হিসেব (Ageing)", "ग्राहक उधार अवधि (Ageing)"],
    "Customer:":            ["Customer:",                "কাস্টমার:",                 "ग्राहक:"],
    "All Customers":        ["All Customers",            "সব কাস্টমার",               "सभी ग्राहक"],
    "▶  Generate":          ["▶  Generate",              "▶  রিপোর্ট তৈরি",            "▶  रिपोर्ट तैयार करें"],
    "📊 Excel":             ["📊 Excel",                 "📊 এক্সেল",                  "📊 एक्सेल"],
    "📋 CSV":               ["📋 CSV",                   "📋 সিএসভি",                  "📋 सीएसवी"],
    "📄 PDF":               ["📄 PDF",                   "📄 পিডিএফ",                  "📄 पीडीएफ"],
    "← Select a report from the left panel": ["← Select a report from the left panel", "← বাঁদিকের প্যানেল থেকে রিপোর্ট বাছো", "← बाएँ पैनल से रिपोर्ट चुनें"],
    "Total rows:":          ["Total rows:",              "মোট রো (Rows):",            "कुल पंक्तियाँ (Rows):"],
    "Grand Total":          ["Grand Total",              "মোট",                     "कुल"],
    "Bills":                ["Bills",                    "বিল তালিকা",                 "बिल"],
    "Subtotal ₹":           ["Subtotal ₹",               "সাবটোটাল ₹",               "सबटोटल ₹"],
    "Discount ₹":           ["Discount ₹",               "ছাড় ₹",                   "छूट ₹"],
    "Total ₹":              ["Total ₹",                  "মোট ₹",                    "कुल ₹"],
    "Product":              ["Product",                  "প্রোডাক্ট",                 "प्रोडक्ट"],
    "Avg Price ₹":          ["Avg Price ₹",              "গড় দাম ₹",                "औसत दाम ₹"],
    "Total Sales ₹":        ["Total Sales ₹",            "মোট বিক্রি ₹",             "कुल बिक्री ₹"],
    "Rank":                 ["Rank",                     "র‍্যাংক",                    "रैंक"],
    "Qty Sold":             ["Qty Sold",                 "বিক্রি পরিমাণ",            "बेची गई मात्रा"],
    "Revenue ₹":            ["Revenue ₹",                "মোট আয় ₹",                  "कुल आय ₹"],
    "Code":                    ['Code', 'কোড', 'कोड'],
    "Reorder":                 ['Reorder', 'রিয়র্ডার', 'रीऑर्डर'],
    "Shortage":             ["Shortage",                 "কমতি",                     "कमी"],
    "GRN No":               ["GRN No",                   "জিআরএন নং",                "जीआरएन नं"],
    "Supplier":                ['Supplier', 'সাপ্লায়ার', 'सप्लायर'],
    "Cost ₹":               ["Cost ₹",                   "কেনা ₹",                   "खरीद ₹"],
    "Margin ₹":                ['Margin ₹', 'মার্জিন ₹', 'मार्जिन ₹'],
    "Margin %":                ['Margin %', 'মার্জিন %', 'मार्जिन %'],
    "Total Profit ₹":       ["Total Profit ₹",           "মোট লাভ ₹",                "कुल मुनाफ़ा ₹"],
    "Cost Value ₹":         ["Cost Value ₹",             "কেনা দাম ₹",               "खरीद दाम ₹"],
    "Retail Value ₹":          ['Retail Value ₹', 'বিক্রি দাম ₹', 'बिक्री दाम ₹'],
    "Last Sold":            ["Last Sold",                "শেষ বিক্রি",               "आखिरी बिक्री"],
    "Qty(30d)":                ['Qty(30d)', 'পরিমাণ (৩০ দিন)', 'मात्रा (30 दिन)'],
    "Invoice ₹":               ['Invoice ₹', 'ইনভয়েস ₹', 'इनवॉइस ₹'],
    "Paid ₹":                  ['Paid ₹', 'দিয়েছে ₹', 'दिया ₹'],
    "Balance ₹":               ['Balance ₹', 'বাকি ₹', 'बाकी ₹'],
    "Age (days)":           ["Age (days)",               "দিন (Age)",                "दिन (Age)"],
    "Bucket":                  ['Bucket', 'গ্রুপ (Bucket)', 'बकेट (Bucket)'],
    "Total Due ₹":             ['Total Due ₹', 'মোট বাকি ₹', 'कुल बाकी ₹'],
    "0-30 days ₹":          ["0-30 days ₹",              "0-30 days ₹",              "0-30 days ₹"],
    "31-60 days ₹":          ["31-60 days ₹",             "31-60 days ₹",             "31-60 days ₹"],
    "60+ days ₹":           ["60+ days ₹",               "60+ days ₹",               "60+ days ₹"],
    "Last Txn":             ["Last Txn",                 "শেষ লেনদেন",               "आखिरी लेनदेन"],
    "Date Error":           ["Date Error",               "তারিখের ভুল",              "तारीख की भूल"],
    "Enter valid dates in YYYY-MM-DD format.": ['Enter valid dates in YYYY-MM-DD format.', 'YYYY-MM-DD ফরম্যাটে সঠিক তারিখ লেখো।', 'YYYY-MM-DD फॉर्मेट में सही तारीख लिखें।'],
    "No Data":                 ['No Data', 'কোনো ডেটা নেই', 'कोई डेटा नहीं'],
    "Generate a report first.": ['Generate a report first.', 'আগে রিপোর্ট তৈরি করো।', 'पहले रिपोर्ट बनाओ।'],
    "Missing Library":         ['Missing Library', 'লাইব্রেরি নেই', 'लाइब्रेरी नहीं है'],
    "Exported":                ['Exported', 'এক্সপোর্ট হয়ে গেছে', 'एक्सपोर्ट हो गया'],
    "Saved to:":               ['Saved to:', 'সেভ হয়েছে:', 'सेव हुआ:'],
    "PDF Exported":            ['PDF Exported', 'পিডিএফ এক্সপোর্ট হয়েছে', 'पीडीएफ एक्सपोर्ट हुआ'],
    "PDF Error":               ['PDF Error', 'পিডিএফ এরর', 'पीडीएफ एरर'],
    "Bills for":               ['Bills for', 'বিল তালিকা -', 'बिल सूची -'],
    "bill(s)   |   Total ₹":   ['bill(s)   |   Total ₹', 'বিল   |   মোট ₹', 'बिल   |   कुल ₹'],
    "Bill #":                  ['Bill #', 'বিল নম্বর', 'बिल नंबर'],
    "Time":                    ['Time', 'সময়', 'समय'],
    "Show Inactive":           ['Show Inactive', 'নিষ্ক্রিয় দেখাও', 'निष्क्रिय दिखाओ'],
    "Reactivate":              ['Reactivate', 'পুনরায় সক্রিয় করো', 'सक्रिय करें'],
    "Deactivate":              ['Deactivate', 'নিষ্ক্রিয় করো', 'निष्क्रिय करें'],
    "Edit User":               ['Edit User', 'ইউজার এডিট', 'यूज़र एडिट'],
    "Add New User":            ['Add New User', 'নতুন ইউজার', 'नया यूज़र'],
    "Change Password":         ['Change Password', 'পাসওয়ার্ড বদলাও', 'पासवर्ड बदलें'],
    "New Password *":          ['New Password *', 'নতুন পাসওয়ার্ড *', 'नया पासवर्ड *'],
    "Confirm Password *":      ['Confirm Password *', 'পাসওয়ার্ড নিশ্চিত করো *', 'पासवर्ड कंफर्म करें *'],
    "Update Password":         ['Update Password', 'পাসওয়ার্ড আপডেট', 'पासवर्ड अपडेट'],
    "Password changed.":       ['Password changed.', 'পাসওয়ার্ড বদলানো হয়েছে।', 'पासवर्ड बदल गया है।'],
    "Passwords do not match.": ['Passwords do not match.', 'পাসওয়ার্ড মেলেনি।', 'पासवर्ड नहीं मिला।'],
    "Enter at least 4 characters.": ['Enter at least 4 characters.', 'কমপক্ষে ৪ অক্ষরের হতে হবে।', 'कम से कम 4 अक्षर होने चाहिए।'],
    "User updated.":           ['User updated.', 'ইউজার আপডেট হয়েছে।', 'यूज़र अपडेट हो गया।'],
    "User added.":             ['User added.', 'ইউজার অ্যাড করা হয়েছে।', 'यूज़र ऐड हो गया।'],
    "Username already exists.": ['Username already exists.', 'এই ইউজারনেমটি আগে থেকেই আছে।', 'यह यूज़रनेम पहले से है।'],
    "Name is required.":       ['Name is required.', 'নাম দিতে হবে।', 'नाम देना होगा।'],
    "Username is required.":   ['Username is required.', 'ইউজারনেম দিতে হবে।', 'यूज़रनेम देना होगा।'],
    "Password is required.":   ['Password is required.', 'পাসওয়ার্ড দিতে হবে।', 'पासवर्ड देना होगा।'],
    "Admin cannot be deactivated.": ['Admin cannot be deactivated.', 'অ্যাডমিন নিষ্ক্রিয় করা যাবে না।', 'एडमिन को निष्क्रिय नहीं कर सकते।'],
    "Deactivated successfully.": ['Deactivated successfully.', 'নিষ্ক্রিয় করা হয়েছে।', 'निष्क्रिय कर दिया गया है।'],
    "Reactivated successfully.": ['Reactivated successfully.', 'পুনরায় সক্রিয় করা হয়েছে।', 'सक्रिय कर दिया गया है।'],
    "Export CSV":              ['📥  Export CSV', '📥  সিএসভি এক্সপোর্ট', '📥  सीएसवी एक्सपोर्ट'],
    "Search by user, action, or details...": ['Search by user, action, or details...', 'ইউজার, কাজ বা ডিটেইলস দিয়ে সার্চ করো...', 'यूज़र, कार्य या डिटेल्स से सर्च करें...'],
    "records":                 ['records', 'রেকর্ড', 'रिकॉर्ड'],
    "Page":                    ['Page', 'পৃষ্ঠा', 'पेज'],
    "Previous":                ['◀  Previous', '◀  আগের', '◀  पिछला'],
    "Next":                    ['Next  ▶', 'পরের  ▶', 'अगला  ▶'],
    "Created":                 ['Created', 'তৈরি', 'बनाया गया'],
    "Deactivate user '{name}'?\nThey will not be able to log in.": [
        "Deactivate user '{name}'?\nThey will not be able to log in.",
        "ইউজার '{name}' কে নিষ্ক্রিয় করবে?\nওনারা আর লগইন করতে পারবেন না।",
        "यूज़र '{name}' को निष्क्रिय करोगे?\nवे अब लॉगिन नहीं कर पाएंगे।"
    ],
    "Brand":                   ['Brand', 'ব্র্যান্ড', 'ब्रांड'],
    "Stock Value ₹":           ['Stock Value ₹', 'স্টক ভ্যালু ₹', 'स्टॉक वैल्यू ₹'],
    "Stock Value":             ['Stock Value', 'স্টক ভ্যালু', 'स्टॉक वैल्यू'],
    "Buy Price ₹":             ['Buy Price ₹', 'কেনা দাম ₹', 'खरीद दाम ₹'],
    "Reorder Level":           ['Reorder Level', 'রিয়র্ডার লেভেল', 'रीऑर्डर लेवल'],
    "In Stock":                ['✅ In Stock', '✅ স্টকে আছে', '✅ स्टॉक में है'],
    "Before":                  ['Before', 'আগে', 'पहले'],
    "Change":                  ['Change', 'বদল', 'बदलाव'],
    "After":                   ['After', 'পরে', 'बाद'],
    "Reason":                  ['Reason', 'कारण', 'कारण'],
    "GRN Number":              ['GRN Number', 'জিআরএন নম্বর', 'जीआरएन नंबर'],
    "Search products by name, code, or brand…": ['Search products by name, code, or brand…', 'প্রোডাক্টের নাম, কোড বা ব্র্যান্ড দিয়ে সার্চ করো...', 'प्रोडक्ट का नाम, कोड या ब्रांड से सर्च करें...'],
    "Search inventory by name, code, or brand…": ['Search inventory by name, code, or brand…', 'ইনভেন্টরি নাম, কোড বা ব্র্যান্ড দিয়ে সার্চ করো...', 'इन्वेंट्री नाम, कोड या ब्रांड से सर्च करें...'],
    "Search suppliers by name, phone, or contact…": ['Search suppliers by name, phone, or contact…', 'সাপ্লায়ারের নাম, ফোন বা কন্ট্যাক্ট দিয়ে সার্চ করো...', 'सप्लायर का नाम, फ़ोन या संपर्क से सर्च करें...'],
    "Search products by name, barcode, code, or brand…": ['Search products by name, barcode, code, or brand…', 'প্রোডাক্টের নাম, বারকোড, কোড বা ব্র্যান্ড দিয়ে সার্চ করো...', 'प्रोडक्ट का नाम, बारकोड, कोड या ब्रांड से सर्च करें...'],
    "Search GRN no. or supplier…": ['Search GRN no. or supplier…', 'জিআরএন নং বা সাপ্লায়ার দিয়ে সার্চ করো...', 'जीआरएन नं या सप्लायर से सर्च करें...'],
    "Optional notes for this GRN": ['Optional notes for this GRN', 'জিআরএন-এর জন্য ঐচ্ছিক নোট', 'इस जीआरएन के लिए वैकल्पिक नोट'],
    "🔍  Search and select product from existing list…": ['🔍  Search and select product from existing list…', '🔍  খুঁজুন এবং লিস্ট থেকে প্রোডাক্ট সিলেক্ট করুন...', '🔍  खोजें और लिस्ट से प्रोडक्ट सिलेक्ट करें...'],
    "GRN Summary":             ['GRN Summary', 'জিআরএন হিসাব', 'जीआरएन विवरण'],
    "Total Items:":            ['Total Items:', 'মোট আইটেম:', 'कुल आइटम्स:'],
    "Grand Total:":            ['Grand Total:', 'মোট:', 'कुल:'],
    "✅  Save GRN\n(Update Stock)": ["✅  Save GRN\n(Update Stock)", "✅  জিআরএন সেভ করো\n(স্টক আপডেট)", "✅  जीआरएन सेव करें\n(स्टॉक अपडेट करें)"],
    "🧹  Clear Form":           ['🧹  Clear Form', '🧹  ফর্ম খালি করো', '🧹  फॉर्म खाली करें'],
    "📋  GRN History":          ['📋  GRN History', '📋  জিআরএন হিস্ট্রি', '📋  जीआरएन हिस्ट्री'],
    "View All GRNs":           ['View All GRNs', 'সব জিআরএন দেখাও', 'सभी जीआरएन देखें'],
    "✏️  Edit Item":           ['✏️  Edit Item', '✏️  আইটেম এডিট', '✏️  आइटम एडिट'],
    "🧹  Clear All":            ['🧹  Clear All', '🧹  সব পরিষ্কার করো', '🧹  सब खाली करें'],
    "Add Item":                ['Add Item', 'আইটেম যোগ করো', 'आइटम जोड़ें'],
    "Edit Item":               ['Edit Item', 'আইটেম এডিট', 'आइटम एडिट'],
    "Quantity *":              ['Quantity *', 'পরিমাণ *', 'मात्रा *'],
    "Purchase Price (₹) *":    ['Purchase Price (₹) *', 'ক্রয় মূল্য (₹) *', 'क्रय मूल्य (₹) *'],
    "✅  Confirm":              ['✅  Confirm', '✅  কনফার্ম করো', '✅  कंफर्म करें'],
    "Direct Purchase":         ['Direct Purchase', 'সরাসরি ক্রয়', 'सीधा खरीद'],
    "Category:":               ['Category:', 'ক্যাটাগরি:', 'कैटेगरी:'],
    "Low Stock Only":          ['Low Stock Only', 'শুধু কম স্টক', 'केवल कम स्टॉक'],
    "Phone Number":            ['Phone Number', 'ফোন নম্বর', 'फ़ोन नंबर'],
    "Email":                   ['Email', 'ইমেইল', 'ईमेल'],
    "Notes":                   ['Notes', 'নোট', 'नोट'],
    "Add New Supplier":        ['Add New Supplier', 'নতুন সাপ্লায়ার', 'नया सप्लायर'],
    "Edit Supplier":           ['Edit Supplier', 'সাপ্লায়ার এডিট', 'सप्लायर एडिट'],
    "📋  Adj. History":         ['📋  Adj. History', '📋  ইতিহাস (History)', '📋  इतिहास (History)'],
    "Total Products":          ['Total Products', 'মোট প্রোডাক্ট', 'कुल प्रोडक्ट्स'],
    "Type":                    ["Type", "টাইপ", "टाइप"],
    "Set":                     ["Set", "সেট করো", "सेट करें"],
    "Inactive":                ["Inactive", "নিষ্ক্রিয়", "निष्क्रिय"],
    "{n} supplier(s) found":   ["{n} supplier(s) found", "{n} জন সাপ্লায়ার পাওয়া গেছে", "{n} सप्लायर मिले"],
    "Supplier:":               ["Supplier:", "সাপ্লায়ার:", "सप्लायर:"],
    "Notes:":                  ["Notes:", "নোট:", "नोट:"],
    "Product Not Found":       ["Product Not Found", "প্রোডাক্ট পাওয়া যায়নি", "प्रोडक्ट नहीं मिला"],
    "Product Not Found Msg":   [
        "No product found for '{query}'\n\nClick YES to add it to the Product Master first.\nClick NO to add it as a one-time manual GRN entry.",
        "'{query}' এর জন্য কোনো প্রোডাক্ট পাওয়া যায়নি\n\nপ্রোডাক্ট মাস্টারে যোগ করতে 'হ্যাঁ' (YES) ক্লিক করুন।\nএকবারের ম্যানুয়াল এন্ট্রির জন্য 'না' (NO) ক্লিক করুন।",
        "'{query}' के लिए कोई प्रोडक्ट नहीं मिला\n\nप्रोडक्ट मास्टर में जोड़ने के लिए 'हाँ' (YES) क्लिक करें।\nएक बार की मैन्युअल एंट्री के लिए 'नहीं' (NO) क्लिक करें।"
    ],
    "Clear Items":             ["Clear Items", "আইটেম মুছুন", "आइटम हटाएं"],
    "Remove all items from this GRN?": [
        "Remove all items from this GRN?",
        "এই জিআরএন থেকে সব আইটেম মুছে ফেলবেন?",
        "इस जीआरएन से सभी आइटम हटा दें?"
    ],
    "Save GRN":                ["Save GRN", "জিআরএন সেভ করুন", "जीआरएन सेव करें"],
    "Save GRN Msg":            [
        "Save GRN from '{supplier}'?\n\nItems: {items}\nTotal: ₹{total:.2f}\n\nStock will be increased for all items.",
        "'{supplier}' থেকে পাওয়া জিআরএন সেভ করবেন?\n\nআইটেম: {items}\nমোট: ₹{total:.2f}\n\nসব আইটেমের স্টক বাড়িয়ে দেওয়া হবে।",
        "'{supplier}' से प्राप्त जीआरएन सेव करें?\n\nआइटम्स: {items}\nकुल: ₹{total:.2f}\n\nसभी आइटम्स का स्टॉक बढ़ा दिया जाएगा।"
    ],
    "Product Code":            ["Product Code", "প্রোডাক্ট কোড", "प्रोडक्ट कोड"],
    "Auto-generated if blank": ["Auto-generated if blank", "ফাঁকা থাকলে অটো তৈরি হবে", "खाली रहने पर ऑटो-जेनरेट होगा"],
    "Optional":                ["Optional", "ঐচ্ছিক", "वैकल्पिक"],
    "Selling Price (₹) *":     ["Selling Price (₹) *", "বিক্রি মূল্য (₹) *", "बिक्री मूल्य (₹) *"],
    "Purchase Price (₹)":      ["Purchase Price (₹)", "ক্রয় মূল্য (₹)", "क्रय मूल्य (₹)"],
    "For margin calc":         ["For margin calc", "মার্জিন হিসাবের জন্য", "मार्जिन हिसाब के लिए"],
    "Quantity in hand":        ["Quantity in hand", "হাতে থাকা পরিমাণ", "हाथ में मात्रा"],
    "Alert threshold":         ["Alert threshold", "অ্যালার্টের সীমা", "अलर्ट सीमा"],
    "Click calendar →":        ["Click calendar →", "ক্যালেন্ডারে ক্লিক করুন →", "कैलेंडर पर क्लिक करें →"],
    "Select Expiry Date":      ["Select Expiry Date", "মেয়াদ শেষের তারিখ বাছুন", "एक्सपायरी तारीख चुनें"],
    "Save & Add to GRN":       ["Save & Add to GRN", "সেভ করে জিআরএন-এ যোগ করুন", "सेव करके जीआरएन में जोड़ें"],
    "GRN Saved":               ["GRN Saved", "জিআরএন সেভ হয়েছে", "जीआरएन सेव हुआ"],
    "GRN Saved Successfully!": ["GRN Saved Successfully!", "জিআরএন সফলভাবে সেভ হয়েছে!", "जीआरएन सफलतापूर्वक सेव हो गया!"],
    "Total Amount:":           ["Total Amount:", "মোট টাকা:", "कुल रकम:"],
    "Stock has been updated for all items.": [
        "Stock has been updated for all items.",
        "সব আইটেমের স্টক আপডেট করা হয়েছে।",
        "सभी आइटम्स का स्टॉक अपडेट कर दिया गया है।"
    ],
    "Print PDF":               ["Print PDF", "পিডিএফ প্রিন্ট করো", "पीडीएफ प्रिंट करें"],
    "View GRN Details":        ["View GRN Details", "জিআরএন বিস্তারিত দেখো", "जीआरएन विवरण देखें"],
    "Reference":               ["Reference", "রেফারেন্স", "रेफरेंस"],
    "Select Invoice:":         ["Select Invoice:", "ইনভয়েস বাছুন:", "इनवॉइस चुनें:"],
    "Balance due:":            ["Balance due:", "বাকি টাকা:", "बकाया रकम:"],
    "Amount Paid (₹):":        ["Amount Paid (₹):", "পরিশোধিত টাকা (₹):", "भुगतान की गई राशि (₹):"],
    "Notes (optional)":        ["Notes (optional)", "নোট (ঐচ্ছিক)", "नोट (वैकल्पिक)"],
    "Save Payment":            ["Save Payment", "পেমেন্ট সেভ করো", "पेमेंट सेव करें"],
    "Deactivate Supplier Msg": [
        "Deactivate '{supplier}'?\nThey will be hidden from purchase forms.",
        "সাপ্লায়ার '{supplier}' কে নিষ্ক্রিয় করবেন?\nওনারা কেনাকাটার ফর্ম থেকে লুকানো থাকবেন।",
        "सप्लायर '{supplier}' को निष्क्रिय करें?\nवे खरीद फॉर्म से छिपे रहेंगे।"
    ],
    "Deactivate Supplier":      ["Deactivate Supplier", "সাপ্লায়ার নিষ্ক্রিয় করো", "सप्लायर निष्क्रिय करें"],
    "Save Adjustment":          ["Save Adjustment", "💾  অ্যাডজাস্টমেন্ট সেভ করো", "💾  एडजस्टमेंट सेव करें"],
    "Stock adjusted successfully!": ["Stock adjusted successfully!", "স্টক সফলভাবে অ্যাডজাস্ট করা হয়েছে!", "स्टॉक सफलतापूर्वक एडजस्ट कर दिया गया है!"],
    "Adjustment Type":          ["Adjustment Type", "অ্যাডজাস্টমেন্ট টাইপ", "एडजस्टमेंट प्रकार"],
    "Select Product":           ["Select Product", "প্রোডাক্ট সিলেক্ট করো", "प्रोडक्ट सिलेक्ट करें"],
    "Please select a product first.": ["Please select a product first.", "আগে একটা প্রোডাক্ট সিলেক্ট করো।", "पहले एक प्रोडक्ट सिलेक्ट करें।"],
    "e.g. 10":                  ["e.g. 10", "যেমন: ১০", "जैसे: 10"],
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
    "Amount \u20b9":            ["Amount \u20b9", "টাকা \u20b9", "रकम \u20b9"],
    "GRN":                      ["GRN", "জিআরএন", "जीआरএন"],
    "SELECT REPORT":            ["SELECT REPORT", "রিপোর্ট সিলেক্ট করো", "रिपोर्ट सिलेक्ट करें"],
    "openpyxl is required for Excel export.\n\n": [
        "openpyxl is required for Excel export.\n\n",
        "এক্সেল এক্সপোর্টের জন্য openpyxl লাইব্রেরি প্রয়োজন।\n\n",
        "एक्सेल एक्सपोर्ट के लिए openpyxl लाइब्रेरी आवश्यक है।\n\n"
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
        "'{name}' has been added to the Product Master.\n\nIt will now be opened for quantity & price entry.",
        "'{name}' প্রোডাক্ট মাস্টারে যোগ করা হয়েছে।\n\nএখন এটার পরিমাণ ও দাম এন্ট্রি করা যাবে।",
        "'{name}' प्रोडक्ट मास्टर में जोड़ दिया गया है।\n\nअब इसका मात्रा और दाम डाला जा सकता है।"
    ],
    "GRN History":              ["GRN History", "জিআরএন হিস্ট্রি", "जीআরএন  হিস্ট্রি"],
    "GRN Saved \u2705":         ["GRN Saved \u2705", "জিআরএন সেভ হয়েছে \u2705", "जीआरएन सेव हुआ \u2705"],
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
    ],
    "Scan": ["📷 Scan", "📷 স্ক্যান", "📷 स्कैन"],
    "Align QR/Barcode within camera frame": [
        "Align QR/Barcode within camera frame",
        "QR/বারকোড ক্যামেরার ফ্রেমে রাখুন",
        "QR/बारकोड को कैमरे के फ्रेम में रखें"
    ],
    "Initializing Camera...": [
        "Initializing Camera...",
        "ক্যামেরা চালু হচ্ছে...",
        "कैमरा शुरू हो रहा है..."
    ],
    "Camera Error": [
        "Camera Error",
        "ক্যামেরা এরর",
        "कैमरा एरर"
    ],
    "Webcam Scanner": [
        "Webcam Scanner",
        "ওয়েবক্যাম স্ক্যানার",
        "वेबकैम स्कैनर"
    ],
    "No product found for code": [
        "No product found for code '{code}'",
        "কোড '{code}' এর জন্য কোনো প্রোডাক্ট পাওয়া যায়নি",
        "कोड '{code}' के लिए कोई प्रोडक्ट नहीं मिला"
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

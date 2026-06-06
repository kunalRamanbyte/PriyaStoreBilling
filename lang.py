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
    "Deactivate":           ["Deactivate",            "নিষ্ক্রিয় করো",          "निष्क्रिय करें"],
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
    "Supplier Name":        ["Supplier Name",           "সাপ্লায়ারের নাম",         "सप्लायर का नाम"],
    "Contact Person":       ["Contact Person",          "যোগাযোগের ব্যক্তি",       "संपर्क व्यक्ति"],
    "GST Number":           ["GST Number",              "জিএসটি নম্বর",           "जीएसटी नंबर"],
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
    "Grand Total":          ["Grand Total",              "মোট",                     "कुल"],
    "Bills":                ["Bills",                    "বিল",                     "बिल"],
    "Subtotal ₹":           ["Subtotal ₹",               "সাবটোটাল ₹",               "सबटोटल ₹"],
    "Discount ₹":           ["Discount ₹",               "ছাড় ₹",                   "छूट ₹"],
    "Total ₹":              ["Total ₹",                  "মোট ₹",                    "कुल ₹"],
    "Product":              ["Product",                  "Product",                  "Product"],
    "Avg Price ₹":          ["Avg Price ₹",              "গড় দাম ₹",                "औसत दाम ₹"],
    "Total Sales ₹":        ["Total Sales ₹",            "মোট বিক্রি ₹",             "कुल बिक्री ₹"],
    "Rank":                 ["Rank",                     "ক্রম",                     "क्रम"],
    "Qty Sold":             ["Qty Sold",                 "বিক্রি পরিমাণ",            "बिक्री मात्रा"],
    "Revenue ₹":            ["Revenue ₹",                "আয় ₹",                    "आय ₹"],
    "Code":                 ["Code",                     "Code",                     "Code"],
    "Reorder":              ["Reorder",                  "Reorder",                  "Reorder"],
    "Shortage":             ["Shortage",                 "কমতি",                     "कमी"],
    "GRN No":               ["GRN No",                   "GRN No",                   "GRN No"],
    "Supplier":             ["Supplier",                 "Supplier",                 "Supplier"],
    "Cost ₹":               ["Cost ₹",                   "কেনা ₹",                   "खरीद ₹"],
    "Margin ₹":             ["Margin ₹",                 "Margin ₹",                 "Margin ₹"],
    "Margin %":             ["Margin %",                 "Margin %",                 "Margin %"],
    "Total Profit ₹":       ["Total Profit ₹",           "মোট লাভ ₹",                "कुल मुनाफ़ा ₹"],
    "Cost Value ₹":         ["Cost Value ₹",             "কেনা দাম ₹",               "खरीद दाम ₹"],
    "Retail Value ₹":       ["Retail Value ₹",           "বিক্রি দাম ₹",             "बिक्री दाम ₹"],
    "Last Sold":            ["Last Sold",                "শেষ বিক্রি",               "आखिरी बिक्री"],
    "Qty(30d)":             ["Qty(30d)",                 "Qty(30d)",                 "Qty(30d)"],
    "Invoice ₹":            ["Invoice ₹",                "Invoice ₹",                "Invoice ₹"],
    "Paid ₹":               ["Paid ₹",                   "দিয়েছে ₹",                "दिया ₹"],
    "Balance ₹":            ["Balance ₹",                "বাকি ₹",                  "बाकी ₹"],
    "Age (days)":           ["Age (days)",               "দিন (Age)",                "दिन (Age)"],
    "Bucket":               ["Bucket",                   "Bucket",                   "Bucket"],
    "Total Due ₹":          ["Total Due ₹",              "মোট বাকি ₹",              "कुल बाकी ₹"],
    "0-30 days ₹":          ["0-30 days ₹",              "0-30 days ₹",              "0-30 days ₹"],
    "31-60 days ₹":          ["31-60 days ₹",             "31-60 days ₹",             "31-60 days ₹"],
    "60+ days ₹":           ["60+ days ₹",               "60+ days ₹",               "60+ days ₹"],
    "Last Txn":             ["Last Txn",                 "শেষ লেনদেন",               "आखिरी लेनदेन"],
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

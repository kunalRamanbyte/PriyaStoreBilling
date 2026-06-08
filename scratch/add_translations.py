# -*- coding: utf-8 -*-
import os

lang_file = r"c:\Users\Admin\Desktop\billing\lang.py"

with open(lang_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
found = False

for line in lines:
    new_lines.append(line)
    if '"Save Customer_btn"' in line and not found:
        new_lines.append('    "Change Balance":       ["Change Balance",          "চেঞ্জ ব্যালেন্স",        "चेंज बैलेंस"],\n')
        new_lines.append('    "Change Deposit":       ["Change Deposit",          "চেঞ্জ জমা",           "चेंज जमा"],\n')
        new_lines.append('    "Change Cleared":       ["Change Cleared",          "চেঞ্জ পরিশোধ",         "चेंज क्लियर"],\n')
        new_lines.append('    "Clear Change":         ["Clear Change",            "চেঞ্জ ক্লিয়ার",         "चेंज क्लियर"],\n')
        new_lines.append('    "Only admins can clear the change balance.": ["Only admins can clear the change balance.", "শুধুমাত্র অ্যাডমিনরাই চেঞ্জ ব্যালেন্স ক্লিয়ার করতে পারবেন।", "केवल एडमिन ही चेंज बैलेंस क्लियर कर सकते हैं।"],\n')
        new_lines.append('    "Are you sure you want to clear change balance of \u20b9{bal:,.2f} for \'{name}\'?": ["Are you sure you want to clear change balance of \u20b9{bal:,.2f} for \'{name}\'?", "আপনি কি নিশ্চিত যে আপনি \'{name}\'-এর জন্য \u20b9{bal:,.2f} চেঞ্জ ব্যালেন্স ক্লিয়ার করতে চান?", "क्या आप वाकई \'{name}\' के लिए \u20b9{bal:,.2f} का चेंज बैलेंस क्लियर करना चाहते हैं?"],\n')
        new_lines.append('    "Customer has no change balance to clear.": ["Customer has no change balance to clear.", "কাস্টমারের ক্লিয়ার করার মতো কোনো চেঞ্জ ব্যালেন্স নেই।", "ग्राहक के पास क्लियर करने के लिए कोई चेंज बैलेंस नहीं है।"],\n')
        found = True

if found:
    with open(lang_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print("Success")
else:
    print("Error")

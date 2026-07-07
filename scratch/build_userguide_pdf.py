from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT    = Path(__file__).resolve().parents[1]
IMG_DIR = ROOT / "output" / "userguide" / "screenshots"
OUT_DIR = ROOT / "output" / "userguide"
OUT_PDF = OUT_DIR / "Priya_Store_User_Guide.pdf"

PW, PH = landscape(A4)

# ── Styles ────────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

COVER_TITLE = ParagraphStyle(
    "CoverTitle", parent=styles["Title"],
    fontName="Helvetica-Bold", fontSize=34, leading=40,
    alignment=TA_CENTER, textColor=colors.white,
)
COVER_SUB = ParagraphStyle(
    "CoverSub", parent=styles["BodyText"],
    fontName="Helvetica", fontSize=13, leading=18,
    alignment=TA_CENTER, textColor=colors.HexColor("#94A3B8"),
)
SECTION_TITLE = ParagraphStyle(
    "SectionTitle", parent=styles["Heading1"],
    fontName="Helvetica-Bold", fontSize=18, leading=22,
    alignment=TA_LEFT, textColor=colors.HexColor("#1E3A8A"), spaceAfter=4,
)
SECTION_SUB = ParagraphStyle(
    "SectionSub", parent=styles["BodyText"],
    fontName="Helvetica-Oblique", fontSize=11, leading=14,
    alignment=TA_LEFT, textColor=colors.HexColor("#64748B"), spaceAfter=6,
)
STEP_HEADING = ParagraphStyle(
    "StepHeading", parent=styles["Heading2"],
    fontName="Helvetica-Bold", fontSize=11, leading=14,
    alignment=TA_LEFT, textColor=colors.HexColor("#1E40AF"), spaceBefore=8, spaceAfter=2,
)
BODY = ParagraphStyle(
    "Body", parent=styles["BodyText"],
    fontName="Helvetica", fontSize=10, leading=14,
    alignment=TA_JUSTIFY, textColor=colors.HexColor("#111827"),
)
STEP = ParagraphStyle(
    "Step", parent=styles["BodyText"],
    fontName="Helvetica", fontSize=10, leading=14,
    leftIndent=14, firstLineIndent=-14,
    textColor=colors.HexColor("#111827"),
)
TIP = ParagraphStyle(
    "Tip", parent=styles["BodyText"],
    fontName="Helvetica-Oblique", fontSize=9.5, leading=13,
    leftIndent=10, textColor=colors.HexColor("#0369A1"),
)
WARN = ParagraphStyle(
    "Warn", parent=styles["BodyText"],
    fontName="Helvetica-Oblique", fontSize=9.5, leading=13,
    leftIndent=10, textColor=colors.HexColor("#B45309"),
)
KEY = ParagraphStyle(
    "Key", parent=styles["BodyText"],
    fontName="Helvetica-Bold", fontSize=9.5, leading=13,
    leftIndent=10, textColor=colors.HexColor("#7C3AED"),
)

# ── Section definitions ───────────────────────────────────────────────────────

SECTIONS = [
    # ── 1. Login ─────────────────────────────────────────────────────────────
    {
        "title": "Login",
        "subtitle": "Authenticate before using the application",
        "image": "login.png",
        "content": [
            ("heading", "How to Sign In"),
            ("steps", [
                "Launch the application by running <b>main.py</b> or the installed shortcut.",
                "The Login screen opens automatically.",
                "Type your <b>Username</b> in the first field.",
                "Type your <b>Password</b> in the second field.",
                "Click <b>Sign In</b> or press <b>Enter</b> to authenticate.",
                "If credentials are correct you are taken to the Dashboard.",
                "If incorrect, an error message appears — check Caps Lock and re-enter.",
            ]),
            ("heading", "Default Credentials"),
            ("steps", [
                "<b>Admin account:</b> Username: <b>admin</b> / Password: <b>admin123</b>",
                "<b>Cashier account:</b> Username: <b>cashier</b> / Password: <b>cash123</b>",
            ]),
            ("heading", "Role Access Summary"),
            ("steps", [
                "<b>Admin</b> — Full access to all screens including Users, Settings, and Activity Log.",
                "<b>Cashier</b> — Billing, Bill History, and Customer screens only.",
                "<b>Stock Manager</b> — Products, Categories, Inventory, Suppliers, and Purchase screens.",
            ]),
            ("tip", "Change default passwords immediately after first login from the Users screen."),
            ("warn", "The app does not have a password-reset email — if the admin password is lost, the database must be edited manually."),
        ],
    },

    # ── 2. Dashboard ─────────────────────────────────────────────────────────
    {
        "title": "Dashboard",
        "subtitle": "At-a-glance summary of today's business activity",
        "image": "dashboard.png",
        "content": [
            ("heading", "What You See"),
            ("steps", [
                "<b>Today's Sales</b> — total revenue collected today (all saved bills).",
                "<b>Bills Today</b> — count of bills saved today.",
                "<b>Low Stock Items</b> — number of products at or below the minimum stock threshold.",
                "<b>Expiring Soon</b> — products approaching their expiry date (if expiry is tracked).",
                "<b>Recent Bills</b> — last few bills with bill number, customer, and amount.",
            ]),
            ("heading", "Quick Actions"),
            ("steps", [
                "Click <b>New Bill</b> to open the Billing screen and start a sale immediately.",
                "Click <b>Products</b> to jump to the product list.",
                "Click <b>Reports</b> to open the reporting screen.",
                "Click <b>Customers</b> to view and manage customer accounts.",
            ]),
            ("heading", "Sidebar Navigation"),
            ("steps", [
                "The dark blue sidebar on the left is always visible after login.",
                "Click any menu item to navigate — the current screen is highlighted.",
                "The sidebar shows only the items your role is allowed to access.",
                "Your username and role are displayed at the bottom of the sidebar.",
            ]),
            ("tip", "The dashboard refreshes its numbers each time you navigate to it. Use the sidebar to go to another screen and come back to get updated totals."),
        ],
    },

    # ── 3. New Bill ──────────────────────────────────────────────────────────
    {
        "title": "New Bill",
        "subtitle": "Create and save a customer sale",
        "image": "new_bill.png",
        "content": [
            ("heading", "Step-by-Step Billing Workflow"),
            ("steps", [
                "Navigate to <b>New Bill</b> from the sidebar or press <b>F2</b> from anywhere to focus the product search.",
                "Type a product name or barcode in the search box — matching products appear instantly.",
                "Click a product from the suggestions or press <b>Enter</b> to add it to the cart.",
                "Adjust the <b>Quantity</b> directly in the cart row if more than 1 unit is needed.",
                "Apply an item-level <b>Discount</b> in the cart row if required.",
                "Select a <b>Customer</b> from the customer dropdown (optional — leave blank for Walk-in).",
                "Choose <b>Payment Mode</b>: Cash, UPI, Card, or Credit (Udhaar).",
                "Enter the <b>Amount Received</b> — change due is calculated automatically.",
                "Press <b>F10</b> or click <b>Print &amp; Save</b> to finalise and print the bill.",
            ]),
            ("heading", "Keyboard Shortcuts"),
            ("keys", [
                "F2 — Focus the product search box",
                "F8 — Hold (pause) the current bill to serve another customer",
                "F10 — Print and save the bill",
                "Del — Remove the selected item from the cart",
                "Esc — Clear the entire cart",
            ]),
            ("heading", "Payment Modes Explained"),
            ("steps", [
                "<b>Cash</b> — Physical money. Enter amount received; change is shown.",
                "<b>UPI</b> — Digital payment (Google Pay, PhonePe, etc.). No change calculated.",
                "<b>Card</b> — Debit or credit card payment.",
                "<b>Credit / Udhaar</b> — Customer takes goods on credit. The amount is added to the customer's outstanding balance.",
            ]),
            ("heading", "Holding a Bill"),
            ("steps", [
                "Press <b>F8</b> to save the current cart as a Draft without printing.",
                "The cart is cleared so you can serve the next customer.",
                "To resume a held bill, go to <b>Bill History</b>, find the Draft, and click <b>Resume</b>.",
            ]),
            ("tip", "A QR or barcode scanner can be used to add products automatically. Point the scanner at a product barcode and it adds the item to the cart."),
            ("warn", "Stock is deducted immediately when the bill is saved. Voiding the bill restores the stock."),
        ],
    },

    # ── 4. Bill History ──────────────────────────────────────────────────────
    {
        "title": "Bill History",
        "subtitle": "View, reprint, resume, and void past bills",
        "image": "bill_history.png",
        "content": [
            ("heading", "Finding a Bill"),
            ("steps", [
                "Open <b>Bill History</b> from the sidebar.",
                "By default, today's bills are shown.",
                "Use the <b>From Date</b> and <b>To Date</b> pickers to change the date range.",
                "Type in the <b>Search</b> box to filter by bill number or customer name.",
                "Click <b>Search / Refresh</b> to apply the filters.",
            ]),
            ("heading", "Bill Status Colours"),
            ("steps", [
                "<b>Normal rows</b> — saved and completed bills.",
                "<b>Draft (yellow/amber)</b> — bills that were held with F8 and not yet finalised.",
                "<b>Void (red/strikethrough)</b> — bills that were cancelled after saving.",
            ]),
            ("heading", "Actions on a Selected Bill"),
            ("steps", [
                "Click a bill row to select it, then use the action buttons on the right.",
                "<b>View / Print</b> — opens the bill detail popup with Thermal Print and PDF options.",
                "<b>Resume</b> — loads a Draft bill back into the New Bill screen to complete it.",
                "<b>Void</b> — cancels a saved bill and restores the deducted stock (admin only).",
            ]),
            ("heading", "Reprinting a Bill"),
            ("steps", [
                "Select the bill and click <b>View / Print</b>.",
                "In the popup, click <b>Thermal Print</b> to send to the receipt printer.",
                "Click <b>PDF / A4</b> to save and open a full-size A4 PDF of the bill.",
            ]),
            ("warn", "Voiding a bill is permanent and logged in the Activity Log. Only Admin role can void bills."),
            ("tip", "Use the date range filter with a wide range (e.g. full month) and export the result from the Reports screen for accounting purposes."),
        ],
    },

    # ── 5. Products ──────────────────────────────────────────────────────────
    {
        "title": "Products",
        "subtitle": "Manage the product master — the foundation of billing and stock",
        "image": "products.png",
        "content": [
            ("heading", "Adding a New Product"),
            ("steps", [
                "Click <b>Add Product</b> at the top of the screen.",
                "Enter the <b>Product Name</b> (required).",
                "Select a <b>Category</b> from the dropdown (add categories first if needed).",
                "Choose the <b>Unit</b> (e.g. kg, pcs, ltr, box).",
                "Enter the <b>Purchase Price</b> — cost from the supplier.",
                "Enter the <b>Selling Price</b> — price charged to the customer.",
                "Set the <b>Minimum Stock</b> level — alerts trigger when stock falls below this.",
                "Enter the current <b>Opening Stock</b> quantity.",
                "Click <b>Save</b> to create the product.",
            ]),
            ("heading", "Editing a Product"),
            ("steps", [
                "Find the product in the list (use the search box at the top).",
                "Click the product row to select it.",
                "Click <b>Edit</b> — the same form opens with existing values.",
                "Make changes and click <b>Save</b>.",
            ]),
            ("heading", "Deactivating vs Deleting"),
            ("steps", [
                "<b>Deactivate</b> — hides the product from billing and stock views but keeps all history. Use this for discontinued items.",
                "<b>Delete</b> — permanently removes the product. Only possible if the product has never been billed.",
            ]),
            ("tip", "Use the barcode field to store the product's EAN/QR code. The billing screen will then recognise it when a scanner is used."),
            ("warn", "Changing the selling price does not affect already-saved bills — only new bills use the updated price."),
        ],
    },

    # ── 6. Categories ────────────────────────────────────────────────────────
    {
        "title": "Categories",
        "subtitle": "Organise products into groups for easier billing and reporting",
        "image": "categories.png",
        "content": [
            ("heading", "Adding a Category"),
            ("steps", [
                "Click <b>Add Category</b>.",
                "Enter a <b>Category Name</b> (e.g. Beverages, Dairy, Staples).",
                "Click <b>Save</b>.",
            ]),
            ("heading", "Editing a Category"),
            ("steps", [
                "Select the category row.",
                "Click <b>Edit</b>, change the name, and click <b>Save</b>.",
                "All products assigned to this category will reflect the new name immediately.",
            ]),
            ("heading", "Deleting a Category"),
            ("steps", [
                "Select the category and click <b>Delete</b>.",
                "If any products are assigned to this category, deletion is blocked.",
                "Reassign or delete the products first, then retry deleting the category.",
            ]),
            ("tip", "Create categories before adding products — you will need to select one when creating each product."),
            ("tip", "Use category filters in the Reports screen to see sales broken down by category."),
        ],
    },

    # ── 7. Inventory ─────────────────────────────────────────────────────────
    {
        "title": "Inventory",
        "subtitle": "Monitor stock levels and record manual adjustments",
        "image": "inventory.png",
        "content": [
            ("heading", "Reading the Inventory List"),
            ("steps", [
                "Every active product is listed with its <b>Current Stock</b> and <b>Minimum Stock</b>.",
                "Rows highlighted in <b>red/amber</b> indicate stock at or below the minimum threshold.",
                "Use the search box to find a specific product quickly.",
            ]),
            ("heading", "Recording a Stock Adjustment"),
            ("steps", [
                "Select the product row you want to adjust.",
                "Click <b>Adjust Stock</b>.",
                "Choose the adjustment type: <b>Add</b> (stock received / found) or <b>Subtract</b> (damaged / missing).",
                "Enter the <b>Quantity</b> to adjust.",
                "Enter a <b>Reason</b> (e.g. 'Physical count correction', 'Damaged goods').",
                "Click <b>Save</b> — the stock updates immediately.",
            ]),
            ("heading", "Viewing Adjustment History"),
            ("steps", [
                "Click <b>History</b> to open the adjustment log.",
                "All past adjustments are listed with date, user, quantity change, and reason.",
                "Filter by date range to review a specific period.",
            ]),
            ("tip", "Run a physical stock count periodically and use adjustments to reconcile the system with actual counts."),
            ("warn", "Stock is also changed automatically when a bill is saved (deducted) or voided (restored), and when a Purchase GRN is saved (added). Manual adjustments are for corrections only."),
        ],
    },

    # ── 8. Suppliers ─────────────────────────────────────────────────────────
    {
        "title": "Suppliers",
        "subtitle": "Manage supplier contacts and outstanding payments",
        "image": "suppliers.png",
        "content": [
            ("heading", "Adding a Supplier"),
            ("steps", [
                "Click <b>Add Supplier</b>.",
                "Enter the <b>Supplier Name</b> (required).",
                "Enter <b>Contact Person</b>, <b>Phone</b>, <b>Email</b>, and <b>Address</b> as needed.",
                "Enter the <b>Opening Balance</b> if you owe money from before using this app.",
                "Click <b>Save</b>.",
            ]),
            ("heading", "Recording a Payment to a Supplier"),
            ("steps", [
                "Select the supplier row.",
                "Click <b>Record Payment</b>.",
                "Enter the <b>Amount Paid</b> and <b>Payment Mode</b> (Cash / UPI / Bank Transfer).",
                "Add a <b>Note</b> if needed.",
                "Click <b>Save</b> — the outstanding balance reduces immediately.",
            ]),
            ("heading", "Viewing Supplier Ledger"),
            ("steps", [
                "Select the supplier and click <b>View Ledger</b> (or double-click the row).",
                "All purchase entries and payments are listed with running balance.",
            ]),
            ("tip", "Always add the supplier before creating a Purchase GRN — the GRN form requires selecting a supplier."),
        ],
    },

    # ── 9. Purchase / GRN ────────────────────────────────────────────────────
    {
        "title": "Purchase / GRN",
        "subtitle": "Receive goods from a supplier and update stock",
        "image": "purchase_grn.png",
        "content": [
            ("heading", "Creating a Purchase Entry (GRN)"),
            ("steps", [
                "Navigate to <b>Purchase / GRN</b> from the sidebar.",
                "Click <b>New Purchase</b>.",
                "Select the <b>Supplier</b> from the dropdown.",
                "Enter the <b>Invoice Number</b> from the supplier's bill (optional but recommended).",
                "Set the <b>Purchase Date</b>.",
                "Add products: search by name in the item row, then enter <b>Quantity</b> and <b>Purchase Price</b>.",
                "Repeat for each product in the delivery.",
                "Review the <b>Total Amount</b> at the bottom.",
                "Click <b>Save GRN</b> — stock for each product is increased immediately and the supplier's outstanding balance increases.",
            ]),
            ("heading", "How Stock and Prices Update"),
            ("steps", [
                "Each product's <b>current stock</b> increases by the received quantity.",
                "Each product's <b>purchase price</b> is updated to the price entered in the GRN (used for profit calculations).",
                "The supplier's <b>outstanding balance</b> increases by the GRN total.",
                "Record a supplier payment separately to reduce the outstanding balance.",
            ]),
            ("heading", "Viewing Past GRN Entries"),
            ("steps", [
                "The main Purchase screen lists all GRN entries with date, supplier, and total.",
                "Click a row to view the full line-item breakdown.",
            ]),
            ("tip", "Match the invoice number on the GRN to the physical supplier bill so you can trace purchases easily."),
            ("warn", "Deleting a GRN is not supported after it has been saved, as it would require reversing stock and supplier balance. Use a stock adjustment if a correction is needed."),
        ],
    },

    # ── 10. Customers ────────────────────────────────────────────────────────
    {
        "title": "Customers",
        "subtitle": "Manage customer profiles, credit balances, and ledgers",
        "image": "customers.png",
        "content": [
            ("heading", "Adding a Customer"),
            ("steps", [
                "Click <b>Add Customer</b>.",
                "Enter <b>Name</b> (required), <b>Phone</b>, and <b>Address</b>.",
                "Enter an <b>Opening Balance</b> if the customer already owes money from before this app.",
                "Click <b>Save</b>.",
            ]),
            ("heading", "Credit / Udhaar Workflow"),
            ("steps", [
                "When billing, select the customer and choose <b>Credit (Udhaar)</b> as payment mode.",
                "The bill amount is added to the customer's outstanding balance automatically.",
                "When the customer pays later, open their record and click <b>Record Payment</b>.",
                "Enter the amount paid — the balance reduces immediately.",
            ]),
            ("heading", "Recording a Customer Payment"),
            ("steps", [
                "Find the customer in the list (use the search box).",
                "Click <b>Record Payment</b>.",
                "Enter the <b>Amount</b> and <b>Payment Mode</b>.",
                "Click <b>Save</b>.",
            ]),
            ("heading", "Viewing the Customer Ledger"),
            ("steps", [
                "Select the customer and click <b>View Ledger</b>.",
                "All transactions are shown: bills added on credit, payments received, and adjustments.",
                "The running balance column shows the outstanding amount at each step.",
            ]),
            ("heading", "Change Balance (Advance / Overpayment)"),
            ("steps", [
                "If a customer pays more than they owe, the surplus is stored as a <b>Change Balance</b>.",
                "At the next bill, the change balance can be applied automatically to reduce the amount to collect.",
            ]),
            ("tip", "Assign a customer at billing time even for cash sales — it helps track purchase history per customer in Reports."),
        ],
    },

    # ── 11. Reports ──────────────────────────────────────────────────────────
    {
        "title": "Reports",
        "subtitle": "Generate and export business reports for any date range",
        "image": "reports.png",
        "content": [
            ("heading", "Available Reports"),
            ("steps", [
                "<b>Sales Report</b> — total sales by day, filtered by date range and payment mode.",
                "<b>Item-wise Sales</b> — which products sold, in what quantity, and for how much.",
                "<b>Category-wise Sales</b> — sales grouped by product category.",
                "<b>Stock Report</b> — current stock levels for all products.",
                "<b>Purchase Report</b> — all GRN entries by supplier and date.",
                "<b>Customer Ledger Report</b> — outstanding balances and transaction history per customer.",
                "<b>Profit Report</b> — estimated profit based on purchase price vs selling price.",
            ]),
            ("heading", "Generating a Report"),
            ("steps", [
                "Select the <b>Report Type</b> from the dropdown.",
                "Set the <b>From Date</b> and <b>To Date</b> using the date pickers.",
                "Click <b>Generate</b> or <b>Search</b> — results appear in the table below.",
            ]),
            ("heading", "Exporting a Report"),
            ("steps", [
                "After generating, click <b>Export Excel</b> to save as a .xlsx file.",
                "Click <b>Export CSV</b> to save as a comma-separated values file.",
                "Click <b>Export PDF</b> to save as a formatted A4 PDF.",
                "A Save As dialog will appear — choose the destination folder and file name.",
            ]),
            ("tip", "Run the Sales Report for the full month at month-end to reconcile cash and UPI totals. The Payment Mode column breaks down each transaction type."),
            ("tip", "The Stock Report always shows current stock — it is not date-filtered. For stock movement over a period, use the Inventory adjustment history."),
        ],
    },

    # ── 12. Settings ─────────────────────────────────────────────────────────
    {
        "title": "Settings",
        "subtitle": "Configure the application, shop details, and backup options",
        "image": "settings.png",
        "content": [
            ("heading", "Shop Information"),
            ("steps", [
                "Go to <b>Settings</b> from the sidebar (Admin only).",
                "Enter <b>Shop Name</b> — this appears on every printed receipt and PDF bill.",
                "Enter <b>Address</b>, <b>City</b>, <b>Phone</b>, and <b>GST Number</b> — all printed on receipts.",
                "Click <b>Save Settings</b> to apply.",
            ]),
            ("heading", "Receipt / Thermal Printer Settings"),
            ("steps", [
                "Select <b>Paper Width</b>: <b>58mm</b> for narrow printers, <b>80mm</b> for wide printers.",
                "The receipt column layout adjusts automatically to the chosen width.",
                "Click <b>Save Settings</b> — takes effect on the next bill printed.",
            ]),
            ("heading", "Theme and Language"),
            ("steps", [
                "Select <b>Light</b> or <b>Dark</b> theme and click <b>Save Settings</b>.",
                "Select <b>Language</b>: English, Bengali, or Hindi.",
                "The app restarts its screens after a theme or language change.",
            ]),
            ("heading", "Backup"),
            ("steps", [
                "Click <b>Backup Now</b> to immediately copy the database to the <b>backups/</b> folder with a timestamp.",
                "Enable <b>Auto Backup</b> to automatically backup once every 24 hours.",
                "Backups are stored as <code>billing_data_YYYY-MM-DD_HH-MM.db</code> in the backups folder.",
                "To restore, copy a backup file over <code>billing_data.db</code> while the app is closed.",
            ]),
            ("tip", "Copy the backups folder to a USB drive or cloud storage (Google Drive, Dropbox) regularly as an offsite backup."),
            ("warn", "Theme and language changes take effect after navigating away and back — some screens require a full rebuild."),
        ],
    },

    # ── 13. Users ────────────────────────────────────────────────────────────
    {
        "title": "Users",
        "subtitle": "Manage operator accounts and role-based access",
        "image": "users.png",
        "content": [
            ("heading", "Adding a New User"),
            ("steps", [
                "Go to <b>Users</b> from the sidebar (Admin only).",
                "Click <b>Add User</b>.",
                "Enter a <b>Username</b> (unique, no spaces recommended).",
                "Enter a <b>Password</b>.",
                "Select a <b>Role</b>: Admin, Cashier, or Stock Manager.",
                "Click <b>Save</b>.",
            ]),
            ("heading", "Role Permissions at a Glance"),
            ("table", [
                ["Screen / Action", "Admin", "Cashier", "Stock Manager"],
                ["Dashboard",           "✓", "✓", "✓"],
                ["New Bill",            "✓", "✓", "✗"],
                ["Bill History",        "✓", "✓", "✗"],
                ["Void Bill",           "✓", "✗", "✗"],
                ["Products",            "✓", "✗", "✓"],
                ["Categories",          "✓", "✗", "✓"],
                ["Inventory",           "✓", "✗", "✓"],
                ["Suppliers",           "✓", "✗", "✓"],
                ["Purchase / GRN",      "✓", "✗", "✓"],
                ["Customers",           "✓", "✓", "✗"],
                ["Reports",             "✓", "✗", "✗"],
                ["Settings",            "✓", "✗", "✗"],
                ["Users",               "✓", "✗", "✗"],
                ["Activity Log",        "✓", "✗", "✗"],
            ]),
            ("heading", "Changing a Password"),
            ("steps", [
                "Select the user row and click <b>Edit</b>.",
                "Enter the new password and click <b>Save</b>.",
            ]),
            ("heading", "Deactivating a User"),
            ("steps", [
                "Select the user row and click <b>Deactivate</b>.",
                "The user can no longer log in but their history is preserved.",
                "Click <b>Activate</b> on the same row to re-enable them.",
            ]),
            ("warn", "There must always be at least one active Admin account. The system will not let you deactivate the last Admin."),
        ],
    },

    # ── 14. Activity Log ─────────────────────────────────────────────────────
    {
        "title": "Activity Log",
        "subtitle": "Audit trail of every significant action in the application",
        "image": "activity_log.png",
        "content": [
            ("heading", "What is Recorded"),
            ("steps", [
                "<b>LOGIN / LOGOUT</b> — every sign-in and sign-out with timestamp and username.",
                "<b>BILL_SAVED</b> — every completed bill with bill number and total.",
                "<b>BILL_VOIDED</b> — every voided bill with the reason.",
                "<b>GRN_SAVED</b> — every purchase entry with supplier and total.",
                "<b>PRODUCT_*</b> — product additions, edits, and deletions.",
                "<b>USER_*</b> — user account changes made by admin.",
                "<b>STOCK_ADJUSTED</b> — manual stock adjustment entries.",
            ]),
            ("heading", "Filtering the Log"),
            ("steps", [
                "Use <b>From Date</b> and <b>To Date</b> to narrow the date range.",
                "Type in the <b>Search</b> box to filter by username or action type.",
                "Click <b>Refresh</b> to reload the latest entries.",
            ]),
            ("heading", "Reading the Log Table"),
            ("steps", [
                "<b>Timestamp</b> — exact date and time of the action.",
                "<b>User</b> — which operator performed the action.",
                "<b>Action</b> — category of the action (e.g. BILL_SAVED).",
                "<b>Details</b> — specific information such as bill number, amounts, or product names.",
            ]),
            ("tip", "If you suspect an error or dispute a transaction, the Activity Log is the first place to check. It cannot be edited or deleted by any user."),
            ("tip", "Export the log to Excel from Reports > Activity Log Report for long-term record-keeping."),
        ],
    },
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _role_table(data: list) -> Table:
    col_w = [3.2 * inch, 1 * inch, 1 * inch, 1.5 * inch]
    t = Table(data, colWidths=col_w)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#1E3A8A")),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#F0F4FF"), colors.white]),
        ("ALIGN",         (1, 0), (-1, -1), "CENTER"),
        ("ALIGN",         (0, 0), (0, -1),  "LEFT"),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
    ]))
    return t


def _scaled_image(image_name: str, max_w: float, max_h: float):
    """Return a ReportLab Image scaled to fit max_w x max_h, or a warning para."""
    img_path = IMG_DIR / image_name
    if not img_path.exists():
        return Paragraph(f"[Screenshot missing: {image_name}]", WARN)
    # Open via PIL to get pixel dimensions, then tell ReportLab the exact size.
    from PIL import Image as PILImage
    with PILImage.open(img_path) as pil:
        px_w, px_h = pil.size
    # ReportLab renders images at 72 DPI; convert pixels → points.
    pt_w = px_w * 72.0 / 96.0
    pt_h = px_h * 72.0 / 96.0
    scale = min(max_w / pt_w, max_h / pt_h, 1.0)
    return Image(str(img_path), width=pt_w * scale, height=pt_h * scale)


def section_story(section: dict) -> list:
    story = []
    page_w = PW - 0.7 * inch   # usable width (margins 0.35 each side)

    # ── Section header banner ──
    banner = Table([[
        Paragraph(section["title"], ParagraphStyle(
            "BT", fontName="Helvetica-Bold", fontSize=16,
            textColor=colors.white, alignment=TA_LEFT)),
        Paragraph(section.get("subtitle", ""), ParagraphStyle(
            "BS", fontName="Helvetica-Oblique", fontSize=10,
            textColor=colors.HexColor("#93C5FD"), alignment=TA_LEFT)),
    ]], colWidths=[2.6 * inch, page_w - 2.6 * inch])
    banner.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#1E3A8A")),
        ("TOPPADDING",    (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(banner)
    story.append(Spacer(1, 0.1 * inch))

    # ── Screenshot — full width, max 3.4 inch tall ──
    story.append(_scaled_image(section["image"], max_w=page_w, max_h=3.4 * inch))
    story.append(Spacer(1, 0.08 * inch))

    # ── Notes flow linearly (no fixed-height Table), so they can span pages ──
    for item_type, item_val in section["content"]:
        if item_type == "heading":
            story.append(Paragraph(item_val, STEP_HEADING))
        elif item_type == "steps":
            for i, step in enumerate(item_val, 1):
                story.append(Paragraph(f"{i}.  {step}", STEP))
        elif item_type == "tip":
            story.append(Paragraph(f"💡  Tip: {item_val}", TIP))
            story.append(Spacer(1, 2))
        elif item_type == "warn":
            story.append(Paragraph(f"⚠  Note: {item_val}", WARN))
            story.append(Spacer(1, 2))
        elif item_type == "keys":
            story.append(Paragraph("⌨  Keyboard Shortcuts:", ParagraphStyle(
                "kh", fontName="Helvetica-Bold", fontSize=9.5,
                textColor=colors.HexColor("#7C3AED"), spaceBefore=6)))
            for k in item_val:
                story.append(Paragraph(f"     {k}", KEY))
        elif item_type == "table":
            story.append(Spacer(1, 4))
            story.append(_role_table(item_val))
            story.append(Spacer(1, 4))

    return story


def cover_story() -> list:
    box = Table([[
        Paragraph("Priya Store", ParagraphStyle(
            "CT1", fontName="Helvetica-Bold", fontSize=40, textColor=colors.HexColor("#93C5FD"),
            alignment=TA_CENTER)),
        Paragraph("User Guide", ParagraphStyle(
            "CT2", fontName="Helvetica-Bold", fontSize=40, textColor=colors.white,
            alignment=TA_CENTER)),
    ]], colWidths=[5.25 * inch, 5.25 * inch])
    box.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#0F172A")),
        ("TOPPADDING",    (0, 0), (-1, -1), 32),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 32),
        ("LEFTPADDING",   (0, 0), (-1, -1), 24),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 24),
        ("BOX",           (0, 0), (-1, -1), 2, colors.HexColor("#2563EB")),
        ("ROUNDEDCORNERS",[12, 12, 12, 12]),
    ]))

    toc_data = [["#", "Screen", "What it does"]]
    for i, s in enumerate(SECTIONS, 1):
        toc_data.append([str(i), s["title"], s.get("subtitle", "")])
    toc = Table(toc_data, colWidths=[0.35 * inch, 1.8 * inch, 8.35 * inch])
    toc.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#1E3A8A")),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9.5),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#F0F4FF"), colors.white]),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("ALIGN",         (0, 0), (0, -1),  "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 7),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 7),
    ]))

    return [
        Spacer(1, 0.5 * inch),
        box,
        Spacer(1, 0.22 * inch),
        Paragraph(
            "A complete screenshot-based walkthrough of every screen in the application,<br/>"
            "with step-by-step instructions, keyboard shortcuts, tips, and role permissions.",
            ParagraphStyle("intro", fontName="Helvetica", fontSize=11, leading=16,
                           alignment=TA_CENTER, textColor=colors.HexColor("#374151"))),
        Spacer(1, 0.22 * inch),
        Paragraph("Contents", ParagraphStyle("toch", fontName="Helvetica-Bold", fontSize=12,
                                              textColor=colors.HexColor("#1E3A8A"))),
        Spacer(1, 0.08 * inch),
        toc,
    ]


def decorate_page(canvas, doc):
    pw, ph = landscape(A4)
    canvas.saveState()
    # top bar
    canvas.setFillColor(colors.HexColor("#0F172A"))
    canvas.rect(0, ph - 24, pw, 24, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#2563EB"))
    canvas.rect(0, ph - 26, pw, 2, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawString(18, ph - 16, "Priya Store")
    canvas.setFont("Helvetica", 9)
    canvas.drawString(80, ph - 16, "User Guide")
    # bottom bar
    canvas.setFillColor(colors.HexColor("#F1F5F9"))
    canvas.rect(0, 0, pw, 18, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(pw - 16, 5, f"Page {doc.page}")
    canvas.restoreState()


def build_pdf():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=landscape(A4),
        leftMargin=0.35 * inch,
        rightMargin=0.35 * inch,
        topMargin=0.45 * inch,
        bottomMargin=0.3 * inch,
        title="Priya Store User Guide",
        author="Priya Store",
    )
    story = cover_story()
    story.append(PageBreak())
    for i, section in enumerate(SECTIONS):
        story.extend(section_story(section))
        if i != len(SECTIONS) - 1:
            story.append(PageBreak())
    doc.build(story, onFirstPage=decorate_page, onLaterPages=decorate_page)
    print(f"Built: {OUT_PDF}")


if __name__ == "__main__":
    build_pdf()

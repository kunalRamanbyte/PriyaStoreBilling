"""
database.py — All SQLite operations for FMCG Billing System Phase 1 + 2
Uses raw sqlite3 (no ORM) for simplicity and speed.
"""

import sqlite3
import hashlib
import os
from contextlib import contextmanager
from datetime import datetime, date
from config import DB_PATH


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class Database:
    def __init__(self):
        self.db_path = DB_PATH

    @contextmanager
    def get_conn(self):
        """Yield a connection, commit on success / rollback on error, and
        ALWAYS close it. Used as `with self.get_conn() as conn:` everywhere —
        the close() guarantees file handles are released and WAL checkpoints
        promptly instead of waiting on garbage collection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row          # rows as dicts
        conn.execute("PRAGMA journal_mode=WAL")  # power-cut safe
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ─── Schema Setup ─────────────────────────────────────────

    def init_db(self):
        """Create all tables and seed default data."""
        with self.get_conn() as conn:
            cur = conn.cursor()

            cur.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    name          TEXT    NOT NULL,
                    username      TEXT    UNIQUE NOT NULL,
                    password_hash TEXT    NOT NULL,
                    role          TEXT    NOT NULL DEFAULT 'cashier',
                    is_active     INTEGER DEFAULT 1,
                    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS categories (
                    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name        TEXT UNIQUE NOT NULL,
                    colour_code TEXT DEFAULT '#607D8B',
                    is_active   INTEGER DEFAULT 1
                );

                CREATE TABLE IF NOT EXISTS customers (
                    customer_id    INTEGER PRIMARY KEY AUTOINCREMENT,
                    name           TEXT NOT NULL,
                    phone          TEXT,
                    address        TEXT,
                    credit_balance REAL DEFAULT 0,
                    change_balance REAL DEFAULT 0,
                    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS products (
                    product_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_code   TEXT UNIQUE,
                    name           TEXT NOT NULL,
                    category_id    INTEGER REFERENCES categories(category_id),
                    brand          TEXT,
                    unit           TEXT DEFAULT 'piece',
                    selling_price  REAL NOT NULL DEFAULT 0,
                    purchase_price REAL DEFAULT 0,
                    current_stock  REAL DEFAULT 0,
                    reorder_level  REAL DEFAULT 5,
                    is_active      INTEGER DEFAULT 1,
                    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS bills (
                    bill_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_number  TEXT UNIQUE NOT NULL,
                    bill_date    DATETIME DEFAULT CURRENT_TIMESTAMP,
                    customer_id  INTEGER REFERENCES customers(customer_id),
                    customer_name TEXT DEFAULT 'Walk-in Customer',
                    subtotal     REAL DEFAULT 0,
                    discount     REAL DEFAULT 0,
                    grand_total  REAL DEFAULT 0,
                    payment_mode TEXT DEFAULT 'Cash',
                    amount_paid  REAL DEFAULT 0,
                    change_due   REAL DEFAULT 0,
                    status       TEXT DEFAULT 'Active',
                    void_reason  TEXT,
                    created_by   INTEGER REFERENCES users(user_id),
                    notes        TEXT,
                    udhaar_adjustment REAL DEFAULT 0,
                    change_adjustment REAL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS bill_items (
                    item_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_id      INTEGER NOT NULL REFERENCES bills(bill_id),
                    product_id   INTEGER NOT NULL REFERENCES products(product_id),
                    product_name TEXT NOT NULL,
                    unit         TEXT DEFAULT 'piece',
                    quantity     REAL NOT NULL,
                    unit_price   REAL NOT NULL,
                    discount     REAL DEFAULT 0,
                    line_total   REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS settings (
                    key   TEXT PRIMARY KEY,
                    value TEXT
                );

                CREATE TABLE IF NOT EXISTS activity_log (
                    log_id    INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id   INTEGER,
                    action    TEXT NOT NULL,
                    details   TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS suppliers (
                    supplier_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    name             TEXT NOT NULL,
                    contact_person   TEXT,
                    phone            TEXT,
                    email            TEXT,
                    city             TEXT,
                    gst_number       TEXT,
                    notes            TEXT,
                    is_active        INTEGER DEFAULT 1,
                    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS purchase_entries (
                    purchase_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                    grn_number      TEXT UNIQUE NOT NULL,
                    purchase_date   DATETIME DEFAULT CURRENT_TIMESTAMP,
                    supplier_id     INTEGER REFERENCES suppliers(supplier_id),
                    supplier_name   TEXT DEFAULT 'Direct Purchase',
                    total_amount    REAL DEFAULT 0,
                    notes           TEXT,
                    created_by      INTEGER REFERENCES users(user_id)
                );

                CREATE TABLE IF NOT EXISTS purchase_items (
                    item_id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    purchase_id     INTEGER NOT NULL REFERENCES purchase_entries(purchase_id),
                    product_id      INTEGER NOT NULL REFERENCES products(product_id),
                    product_name    TEXT NOT NULL,
                    unit            TEXT DEFAULT 'piece',
                    quantity        REAL NOT NULL,
                    unit_price      REAL NOT NULL,
                    line_total      REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS stock_adjustments (
                    adj_id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id      INTEGER NOT NULL REFERENCES products(product_id),
                    product_name    TEXT NOT NULL,
                    adj_type        TEXT NOT NULL,
                    qty_before      REAL NOT NULL,
                    qty_change      REAL NOT NULL,
                    qty_after       REAL NOT NULL,
                    reason          TEXT,
                    created_by      INTEGER REFERENCES users(user_id),
                    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS customer_transactions (
                    txn_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
                    txn_type    TEXT NOT NULL,
                    amount      REAL NOT NULL,
                    reference   TEXT,
                    notes       TEXT,
                    created_by  INTEGER REFERENCES users(user_id),
                    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS supplier_payments (
                    payment_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                    purchase_id INTEGER NOT NULL REFERENCES purchase_entries(purchase_id),
                    paid_amount REAL NOT NULL,
                    paid_date   DATETIME DEFAULT CURRENT_TIMESTAMP,
                    notes       TEXT,
                    created_by  INTEGER REFERENCES users(user_id)
                );
            """)

            # ── Migrations ────────────────────────────────────────
            for migration in [
                "ALTER TABLE customers ADD COLUMN is_active INTEGER DEFAULT 1",
                "ALTER TABLE products  ADD COLUMN expiry_date TEXT",
                "ALTER TABLE bills     ADD COLUMN udhaar_adjustment REAL DEFAULT 0",
                "ALTER TABLE customers ADD COLUMN change_balance REAL DEFAULT 0",
                "ALTER TABLE bills     ADD COLUMN change_adjustment REAL DEFAULT 0",
            ]:
                try:
                    conn.execute(migration)
                    conn.commit()
                except Exception:
                    pass

            # ── Performance indexes ───────────────────────────────
            for idx in [
                "CREATE INDEX IF NOT EXISTS idx_bills_date     ON bills(bill_date)",
                "CREATE INDEX IF NOT EXISTS idx_bills_status   ON bills(status)",
                "CREATE INDEX IF NOT EXISTS idx_bill_items_bid ON bill_items(bill_id)",
                "CREATE INDEX IF NOT EXISTS idx_bill_items_pid ON bill_items(product_id)",
                "CREATE INDEX IF NOT EXISTS idx_products_name  ON products(name)",
                "CREATE INDEX IF NOT EXISTS idx_products_code  ON products(product_code)",
                "CREATE INDEX IF NOT EXISTS idx_products_cat   ON products(category_id)",
                "CREATE INDEX IF NOT EXISTS idx_products_expiry ON products(expiry_date)",
                "CREATE INDEX IF NOT EXISTS idx_purchases_sup  ON purchase_entries(supplier_id)",
                "CREATE INDEX IF NOT EXISTS idx_cust_txn_cust  ON customer_transactions(customer_id)",
                "CREATE INDEX IF NOT EXISTS idx_sp_purchase    ON supplier_payments(purchase_id)",
            ]:
                try:
                    conn.execute(idx)
                    conn.commit()
                except Exception:
                    pass

            # ── Seed default admin user ──
            admin_exists = cur.execute(
                "SELECT 1 FROM users WHERE username='admin'"
            ).fetchone()
            if not admin_exists:
                cur.execute(
                    "INSERT INTO users (name, username, password_hash, role) VALUES (?,?,?,?)",
                    ("Shop Owner", "admin", hash_password("admin123"), "admin")
                )
                cur.execute(
                    "INSERT INTO users (name, username, password_hash, role) VALUES (?,?,?,?)",
                    ("Counter Staff", "cashier", hash_password("cash123"), "cashier")
                )

            # ── Seed default categories ──
            default_cats = [
                ("Atta & Flour",  "#FF6B35"),
                ("Oils",          "#FFB300"),
                ("Dairy",         "#1E88E5"),
                ("Rice & Pulses", "#43A047"),
                ("Snacks",        "#8E24AA"),
                ("Beverages",     "#00897B"),
                ("Spices",        "#E53935"),
                ("Personal Care", "#F06292"),
                ("Cleaning",      "#0288D1"),
                ("Other",         "#607D8B"),
            ]
            for name, color in default_cats:
                cur.execute(
                    "INSERT OR IGNORE INTO categories (name, colour_code) VALUES (?,?)",
                    (name, color)
                )

            # ── Seed default settings ──
            default_settings = [
                ("shop_name",    "Kunal's FMCG Grocery Shop"),
                ("shop_address", "Main Market, City"),
                ("shop_phone",   "+91 00000 00000"),
                ("bill_prefix",  "BILL"),
                ("next_bill_no", "1"),
                ("paper_width",  "80mm"),
            ]
            for key, val in default_settings:
                cur.execute(
                    "INSERT OR IGNORE INTO settings (key, value) VALUES (?,?)",
                    (key, val)
                )

            # ── Seed sample products ──
            prod_exists = cur.execute("SELECT COUNT(*) FROM products").fetchone()[0]
            if prod_exists == 0:
                sample_products = [
                    ("PROD-001", "Aashirvaad Atta 5kg",   1, "Aashirvaad", "piece", 280, 255, 50, 10),
                    ("PROD-002", "Fortune Sunflower Oil 1L", 2, "Fortune",  "litre", 155, 140, 30,  8),
                    ("PROD-003", "Amul Butter 100g",       3, "Amul",      "piece",  60,  52, 40, 10),
                    ("PROD-004", "Toor Dal 1kg",           4, "Local",     "kg",    160, 145, 25,  8),
                    ("PROD-005", "Lay's Classic Chips",    5, "Lay's",     "piece",  20,  16, 60, 20),
                    ("PROD-006", "Coca Cola 750ml",        6, "Coca Cola", "bottle", 45,  38, 24, 12),
                    ("PROD-007", "Red Chilli Powder 100g", 7, "MDH",      "piece",  55,  45, 20,  5),
                    ("PROD-008", "Colgate Toothpaste 150g",8, "Colgate",  "piece",  99,  85, 15,  5),
                    ("PROD-009", "Surf Excel 500g",        9, "Surf",     "pack",  120, 105, 18,  5),
                    ("PROD-010", "Sugar 1kg",              4, "Local",    "kg",     50,  45, 80, 20),
                    ("PROD-011", "Basmati Rice 5kg",       4, "India Gate","piece", 450, 400,  4,  5),
                    ("PROD-012", "Haldiram Namkeen 200g",  5, "Haldiram", "piece",  90,  78, 30, 10),
                ]
                cur.executemany(
                    """INSERT OR IGNORE INTO products
                       (product_code,name,category_id,brand,unit,selling_price,purchase_price,current_stock,reorder_level)
                       VALUES (?,?,?,?,?,?,?,?,?)""",
                    sample_products
                )

            conn.commit()

    # ─── Auth ──────────────────────────────────────────────────

    def authenticate(self, username: str, password: str):
        """Returns user dict or None."""
        with self.get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE username=? AND is_active=1",
                (username,)
            ).fetchone()
            if row and row["password_hash"] == hash_password(password):
                return dict(row)
        return None

    # ─── Settings ─────────────────────────────────────────────

    def get_setting(self, key: str, default="") -> str:
        with self.get_conn() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
            return row["value"] if row else default

    def set_setting(self, key: str, value: str):
        with self.get_conn() as conn:
            conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)", (key, value))
            conn.commit()

    # ─── Next Bill Number (atomic increment) ──────────────────

    def next_bill_number(self) -> str:
        """Return the current bill number string (does NOT increment)."""
        with self.get_conn() as conn:
            n      = int(self.get_setting("next_bill_no", "1"))
            prefix = self.get_setting("bill_prefix", "BILL")
            return f"{prefix}-{n:05d}"

    def increment_bill_number(self):
        """Atomically increment the bill counter in a single SQL statement."""
        with self.get_conn() as conn:
            conn.execute(
                """UPDATE settings
                   SET value = CAST(CAST(value AS INTEGER) + 1 AS TEXT)
                   WHERE key = 'next_bill_no'""",
            )
            conn.commit()

    def _claim_number(self, conn, setting_key: str, prefix: str, fallback_sql: str = None) -> str:
        """Claim the next document number inside an active write transaction."""
        row = conn.execute("SELECT value FROM settings WHERE key=?", (setting_key,)).fetchone()
        if row:
            n = int(row["value"])
        elif fallback_sql:
            n = int(conn.execute(fallback_sql).fetchone()[0])
            conn.execute("INSERT INTO settings (key, value) VALUES (?,?)", (setting_key, str(n)))
        else:
            n = 1
            conn.execute("INSERT INTO settings (key, value) VALUES (?,?)", (setting_key, "1"))

        conn.execute(
            "UPDATE settings SET value=CAST(? AS TEXT) WHERE key=?",
            (n + 1, setting_key)
        )
        return f"{prefix}-{n:05d}"

    # ─── Categories ───────────────────────────────────────────

    def get_categories(self, active_only=True):
        with self.get_conn() as conn:
            q = "SELECT * FROM categories"
            if active_only:
                q += " WHERE is_active=1"
            q += " ORDER BY name"
            return [dict(r) for r in conn.execute(q).fetchall()]

    def add_category(self, name: str, colour_code: str) -> bool:
        try:
            with self.get_conn() as conn:
                conn.execute(
                    "INSERT INTO categories (name, colour_code) VALUES (?,?)",
                    (name, colour_code)
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def update_category(self, category_id: int, name: str, colour_code: str):
        with self.get_conn() as conn:
            conn.execute(
                "UPDATE categories SET name=?, colour_code=? WHERE category_id=?",
                (name, colour_code, category_id)
            )
            conn.commit()

    def delete_category(self, category_id: int):
        with self.get_conn() as conn:
            conn.execute("UPDATE categories SET is_active=0 WHERE category_id=?", (category_id,))
            conn.commit()

    # ─── Products ─────────────────────────────────────────────

    def get_products(self, active_only=True, search="", category_id=None):
        with self.get_conn() as conn:
            q = """
                SELECT p.*, c.name AS category_name, c.colour_code
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                WHERE 1=1
            """
            params = []
            if active_only:
                q += " AND p.is_active=1"
            if search:
                q += " AND (p.name LIKE ? OR p.product_code LIKE ? OR p.brand LIKE ?)"
                like = f"%{search}%"
                params += [like, like, like]
            if category_id:
                q += " AND p.category_id=?"
                params.append(category_id)
            q += " ORDER BY p.name"
            return [dict(r) for r in conn.execute(q, params).fetchall()]

    def search_products_billing(self, query: str):
        """Fast search for billing screen — returns top 8 matches."""
        with self.get_conn() as conn:
            like = f"%{query}%"
            rows = conn.execute(
                """SELECT p.product_id, p.product_code, p.name, p.unit,
                          p.selling_price, p.purchase_price, p.current_stock,
                          c.name AS category_name, c.colour_code
                   FROM products p
                   LEFT JOIN categories c ON p.category_id=c.category_id
                   WHERE p.is_active=1
                     AND (p.name LIKE ? OR p.product_code LIKE ? OR p.brand LIKE ?)
                   ORDER BY p.name
                   LIMIT 8""",
                (like, like, like)
            ).fetchall()
            return [dict(r) for r in rows]

    def get_product_by_id(self, product_id: int):
        with self.get_conn() as conn:
            row = conn.execute(
                """SELECT p.*, c.name AS category_name
                   FROM products p
                   LEFT JOIN categories c ON p.category_id=c.category_id
                   WHERE p.product_id=?""",
                (product_id,)
            ).fetchone()
            return dict(row) if row else None

    def get_product_by_code(self, product_code: str):
        """Fetch an active product by exact product_code match."""
        with self.get_conn() as conn:
            row = conn.execute(
                """SELECT p.*, c.name AS category_name, c.colour_code
                   FROM products p
                   LEFT JOIN categories c ON p.category_id=c.category_id
                   WHERE p.product_code = ? AND p.is_active = 1""",
                (product_code,)
            ).fetchone()
            return dict(row) if row else None

    def add_product(self, data: dict) -> int:
        with self.get_conn() as conn:
            cur = conn.execute(
                """INSERT INTO products
                   (product_code, name, category_id, brand, unit,
                    selling_price, purchase_price, current_stock, reorder_level, expiry_date)
                   VALUES (:product_code,:name,:category_id,:brand,:unit,
                           :selling_price,:purchase_price,:current_stock,:reorder_level,
                           :expiry_date)""",
                {**data, "expiry_date": data.get("expiry_date")}
            )
            conn.commit()
            return cur.lastrowid

    def update_product(self, product_id: int, data: dict):
        with self.get_conn() as conn:
            conn.execute(
                """UPDATE products SET
                   product_code=:product_code, name=:name, category_id=:category_id,
                   brand=:brand, unit=:unit, selling_price=:selling_price,
                   purchase_price=:purchase_price, reorder_level=:reorder_level,
                   expiry_date=:expiry_date
                   WHERE product_id=:product_id""",
                {**data, "expiry_date": data.get("expiry_date"), "product_id": product_id}
            )
            conn.commit()

    def deactivate_product(self, product_id: int):
        with self.get_conn() as conn:
            conn.execute("UPDATE products SET is_active=0 WHERE product_id=?", (product_id,))
            conn.commit()

    def delete_product(self, product_id: int) -> tuple:
        """Hard delete. Returns (ok, message). Falls back to deactivate if used in bills."""
        with self.get_conn() as conn:
            used = conn.execute(
                "SELECT COUNT(*) FROM bill_items WHERE product_id=?", (product_id,)
            ).fetchone()[0]
            if used:
                return False, f"Product used in {used} bill(s). Deactivating instead."
            conn.execute("DELETE FROM purchase_items WHERE product_id=?", (product_id,))
            conn.execute("DELETE FROM products WHERE product_id=?", (product_id,))
            conn.commit()
            return True, "Product deleted."

    def adjust_stock(self, product_id: int, qty_change: float):
        """Positive = add stock, Negative = reduce stock."""
        with self.get_conn() as conn:
            conn.execute(
                "UPDATE products SET current_stock = current_stock + ? WHERE product_id=?",
                (qty_change, product_id)
            )
            conn.commit()

    def get_low_stock_count(self) -> int:
        with self.get_conn() as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM products WHERE is_active=1 AND current_stock <= reorder_level"
            ).fetchone()
            return row[0]

    # ─── Bills ────────────────────────────────────────────────

    def save_bill(self, bill_data: dict, items: list, user_id: int) -> int:
        """Save bill + items + deduct stock in one transaction."""
        with self.get_conn() as conn:
            conn.execute("BEGIN IMMEDIATE")
            pfx = conn.execute("SELECT value FROM settings WHERE key='bill_prefix'").fetchone()
            prefix = pfx["value"] if pfx else "BILL"
            bill_number = self._claim_number(conn, "next_bill_no", prefix)
            udhaar_adj = float(bill_data.get("udhaar_adjustment") or 0)
            change_adj = float(bill_data.get("change_adjustment") or 0)
            cur = conn.execute(
                """INSERT INTO bills
                   (bill_number, customer_id, customer_name, subtotal, discount,
                    grand_total, payment_mode, amount_paid, change_due, status,
                    udhaar_adjustment, change_adjustment, created_by)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    bill_number,
                    bill_data.get("customer_id"),
                    bill_data.get("customer_name", "Walk-in Customer"),
                    bill_data["subtotal"],
                    bill_data["discount"],
                    bill_data["grand_total"],
                    bill_data["payment_mode"],
                    bill_data["amount_paid"],
                    bill_data["change_due"],
                    "Active",
                    udhaar_adj,
                    change_adj,
                    user_id,
                )
            )
            bill_id = cur.lastrowid

            for item in items:
                conn.execute(
                    """INSERT INTO bill_items
                       (bill_id, product_id, product_name, unit, quantity, unit_price, discount, line_total)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (
                        bill_id,
                        item["product_id"],
                        item["product_name"],
                        item["unit"],
                        item["quantity"],
                        item["unit_price"],
                        item.get("discount", 0),
                        item["line_total"],
                    )
                )
                # Deduct stock
                conn.execute(
                    "UPDATE products SET current_stock = current_stock - ? WHERE product_id=?",
                    (item["quantity"], item["product_id"])
                )

            # Auto-log credit/payment transaction (Udhaar)
            if bill_data.get("customer_id"):
                cust_id = bill_data["customer_id"]
                p_val = float(bill_data.get("amount_paid") or 0)
                b_due = max(0.0, round(bill_data["grand_total"] - change_adj, 2))
                u_prev = udhaar_adj
                total_to_collect = round(b_due + u_prev, 2)

                credit_added = 0.0
                udhaar_collected = 0.0

                if p_val >= total_to_collect:
                    udhaar_collected = u_prev
                else:
                    if p_val >= u_prev:
                        udhaar_collected = u_prev
                        credit_added = round(total_to_collect - p_val, 2)
                    else:
                        udhaar_collected = p_val
                        credit_added = b_due

                if credit_added > 0:
                    conn.execute(
                        """INSERT INTO customer_transactions
                           (customer_id, txn_type, amount, reference, notes, created_by)
                           VALUES (?,?,?,?,?,?)""",
                        (cust_id, "Credit", credit_added,
                         bill_number, "Auto from bill", user_id)
                    )
                    conn.execute(
                        "UPDATE customers SET credit_balance = credit_balance + ? WHERE customer_id=?",
                        (credit_added, cust_id)
                    )

                if udhaar_collected > 0:
                    conn.execute(
                        """INSERT INTO customer_transactions
                           (customer_id, txn_type, amount, reference, notes, created_by)
                           VALUES (?,?,?,?,?,?)""",
                        (cust_id, "Payment", udhaar_collected,
                         bill_number, "Udhaar collected with bill", user_id)
                    )
                    conn.execute(
                        "UPDATE customers SET credit_balance = MAX(0, credit_balance - ?) WHERE customer_id=?",
                        (udhaar_collected, cust_id)
                    )

            # Deduct change_adjustment from customer's change_balance if customer is selected
            if change_adj > 0 and bill_data.get("customer_id"):
                conn.execute(
                    """INSERT INTO customer_transactions
                       (customer_id, txn_type, amount, reference, notes, created_by)
                       VALUES (?,?,?,?,?,?)""",
                    (bill_data["customer_id"], "Change Clear", change_adj,
                     bill_number, "Change adjusted in bill", user_id)
                )
                conn.execute(
                    "UPDATE customers SET change_balance = MAX(0, change_balance - ?) WHERE customer_id=?",
                    (change_adj, bill_data["customer_id"])
                )

            # Deposit change_due to customer's change_balance if customer is selected
            change_due = float(bill_data.get("change_due") or 0)
            if change_due > 0 and bill_data.get("customer_id"):
                conn.execute(
                    """INSERT INTO customer_transactions
                       (customer_id, txn_type, amount, reference, notes, created_by)
                       VALUES (?,?,?,?,?,?)""",
                    (bill_data["customer_id"], "Change Deposit", change_due,
                     bill_number, "Change from bill", user_id)
                )
                conn.execute(
                    "UPDATE customers SET change_balance = change_balance + ? WHERE customer_id=?",
                    (change_due, bill_data["customer_id"])
                )

            if bill_data.get("customer_id"):
                self._net_customer_balances(conn, bill_data["customer_id"], user_id, bill_number)

            conn.commit()

        self.log_activity(user_id, "BILL_SAVED", f"Bill {bill_number} saved. Total: ₹{bill_data['grand_total']:.2f}")
        return bill_id

    def save_draft_bill(self, bill_data: dict, items: list, user_id: int) -> int:
        """Save bill as Draft (stock NOT deducted)."""
        with self.get_conn() as conn:
            conn.execute("BEGIN IMMEDIATE")
            pfx = conn.execute("SELECT value FROM settings WHERE key='bill_prefix'").fetchone()
            prefix = pfx["value"] if pfx else "BILL"
            bill_number = self._claim_number(conn, "next_bill_no", prefix)
            change_adj = float(bill_data.get("change_adjustment") or 0)
            cur = conn.execute(
                """INSERT INTO bills
                   (bill_number, customer_id, customer_name, subtotal, discount,
                    grand_total, payment_mode, amount_paid, change_due, status,
                    change_adjustment, created_by)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    bill_number,
                    bill_data.get("customer_id"),
                    bill_data.get("customer_name", "Walk-in Customer"),
                    bill_data["subtotal"],
                    bill_data["discount"],
                    bill_data["grand_total"],
                    bill_data["payment_mode"],
                    bill_data.get("amount_paid", 0),
                    bill_data.get("change_due", 0),
                    "Draft",
                    change_adj,
                    user_id,
                )
            )
            bill_id = cur.lastrowid

            for item in items:
                conn.execute(
                    """INSERT INTO bill_items
                       (bill_id, product_id, product_name, unit, quantity, unit_price, discount, line_total)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (
                        bill_id,
                        item["product_id"],
                        item["product_name"],
                        item["unit"],
                        item["quantity"],
                        item["unit_price"],
                        item.get("discount", 0),
                        item["line_total"],
                    )
                )
            conn.commit()

        return bill_id

    def get_bills(self, search="", date_from=None, date_to=None, status=None, limit=200):
        with self.get_conn() as conn:
            q = "SELECT * FROM bills WHERE 1=1"
            params = []
            if search:
                q += " AND (bill_number LIKE ? OR customer_name LIKE ?)"
                like = f"%{search}%"
                params += [like, like]
            if date_from:
                q += " AND DATE(bill_date) >= ?"
                params.append(date_from)
            if date_to:
                q += " AND DATE(bill_date) <= ?"
                params.append(date_to)
            if status:
                q += " AND status=?"
                params.append(status)
            q += " ORDER BY bill_date DESC LIMIT ?"
            params.append(limit)
            return [dict(r) for r in conn.execute(q, params).fetchall()]

    def get_bill_by_id(self, bill_id: int):
        with self.get_conn() as conn:
            bill = conn.execute("SELECT * FROM bills WHERE bill_id=?", (bill_id,)).fetchone()
            if not bill:
                return None, []
            items = conn.execute(
                "SELECT * FROM bill_items WHERE bill_id=?", (bill_id,)
            ).fetchall()
            return dict(bill), [dict(i) for i in items]

    def void_bill(self, bill_id: int, reason: str, user_id: int):
        """Void a bill, reverse stock, and reverse credit balance for Udhaar bills."""
        bill, items = self.get_bill_by_id(bill_id)
        if not bill or bill["status"] != "Active":
            return False
        with self.get_conn() as conn:
            conn.execute(
                "UPDATE bills SET status='Void', void_reason=? WHERE bill_id=?",
                (reason, bill_id)
            )
            for item in items:
                conn.execute(
                    "UPDATE products SET current_stock = current_stock + ? WHERE product_id=?",
                    (item["quantity"], item["product_id"])
                )
            # Reverse the customer credit/payment balance that was affected when the bill was saved
            if bill.get("customer_id"):
                cust_id = bill["customer_id"]
                p_val = float(bill.get("amount_paid") or 0)
                change_adj_bill = float(bill.get("change_adjustment") or 0)
                udhaar_adj_bill = float(bill.get("udhaar_adjustment") or 0)
                b_due = max(0.0, round(bill["grand_total"] - change_adj_bill, 2))
                total_to_collect = round(b_due + udhaar_adj_bill, 2)

                credit_added = 0.0
                udhaar_collected = 0.0

                if p_val >= total_to_collect:
                    udhaar_collected = udhaar_adj_bill
                else:
                    if p_val >= udhaar_adj_bill:
                        udhaar_collected = udhaar_adj_bill
                        credit_added = round(total_to_collect - p_val, 2)
                    else:
                        udhaar_collected = p_val
                        credit_added = b_due

                if credit_added > 0:
                    conn.execute(
                        "UPDATE customers SET credit_balance = MAX(0, credit_balance - ?) WHERE customer_id=?",
                        (credit_added, cust_id)
                    )
                    conn.execute(
                        """INSERT INTO customer_transactions
                           (customer_id, txn_type, amount, reference, notes, created_by)
                           VALUES (?,?,?,?,?,?)""",
                        (cust_id, "Payment", credit_added,
                         bill["bill_number"], "Auto-reversed: bill voided", user_id)
                    )

                if udhaar_collected > 0:
                    conn.execute(
                        "UPDATE customers SET credit_balance = credit_balance + ? WHERE customer_id=?",
                        (udhaar_collected, cust_id)
                    )
                    conn.execute(
                        """INSERT INTO customer_transactions
                           (customer_id, txn_type, amount, reference, notes, created_by)
                           VALUES (?,?,?,?,?,?)""",
                        (cust_id, "Credit", udhaar_collected,
                         bill["bill_number"], "Auto-reversed: udhaar collection voided", user_id)
                    )
            # Reverse any change_due that was deposited into customer's change_balance
            change_due = float(bill.get("change_due") or 0)
            if change_due > 0 and bill.get("customer_id"):
                conn.execute(
                    "UPDATE customers SET change_balance = MAX(0, change_balance - ?) WHERE customer_id=?",
                    (change_due, bill["customer_id"])
                )
                conn.execute(
                    """INSERT INTO customer_transactions
                       (customer_id, txn_type, amount, reference, notes, created_by)
                       VALUES (?,?,?,?,?,?)""",
                    (bill["customer_id"], "Change Clear", change_due,
                     bill["bill_number"], "Auto-reversed: bill voided", user_id)
                )
            # Reverse any change_adjustment that was used/adjusted in this bill
            change_adj = float(bill.get("change_adjustment") or 0)
            if change_adj > 0 and bill.get("customer_id"):
                conn.execute(
                    "UPDATE customers SET change_balance = change_balance + ? WHERE customer_id=?",
                    (change_adj, bill["customer_id"])
                )
                conn.execute(
                    """INSERT INTO customer_transactions
                       (customer_id, txn_type, amount, reference, notes, created_by)
                       VALUES (?,?,?,?,?,?)""",
                    (bill["customer_id"], "Change Deposit", change_adj,
                     bill["bill_number"], "Auto-reversed: change adjustment voided", user_id)
                )
            if bill.get("customer_id"):
                self._net_customer_balances(conn, bill["customer_id"], user_id, bill["bill_number"])
            conn.commit()
        self.log_activity(user_id, "BILL_VOID", f"Bill {bill['bill_number']} voided. Reason: {reason}")
        return True

    def get_draft_bills(self):
        with self.get_conn() as conn:
            return [dict(r) for r in conn.execute(
                "SELECT * FROM bills WHERE status='Draft' ORDER BY bill_date DESC"
            ).fetchall()]

    def delete_draft(self, bill_id: int):
        with self.get_conn() as conn:
            conn.execute("DELETE FROM bill_items WHERE bill_id=?", (bill_id,))
            conn.execute("DELETE FROM bills WHERE bill_id=? AND status='Draft'", (bill_id,))
            conn.commit()

    # ─── Dashboard Stats ──────────────────────────────────────

    def get_today_stats(self):
        today = date.today().isoformat()
        with self.get_conn() as conn:
            row = conn.execute(
                """SELECT COUNT(*) AS bill_count,
                          COALESCE(SUM(grand_total),0) AS total_sales,
                          COALESCE(SUM(discount),0)    AS total_discount
                   FROM bills
                   WHERE DATE(bill_date)=? AND status='Active'""",
                (today,)
            ).fetchone()
            return dict(row) if row else {"bill_count": 0, "total_sales": 0, "total_discount": 0}

    def get_recent_bills(self, limit=10):
        with self.get_conn() as conn:
            return [dict(r) for r in conn.execute(
                "SELECT * FROM bills WHERE status='Active' ORDER BY bill_date DESC LIMIT ?",
                (limit,)
            ).fetchall()]

    # ─── Activity Log ─────────────────────────────────────────

    def log_activity(self, user_id, action: str, details: str = ""):
        with self.get_conn() as conn:
            conn.execute(
                "INSERT INTO activity_log (user_id, action, details) VALUES (?,?,?)",
                (user_id, action, details)
            )
            conn.commit()

    # ─── Phase 2: Inventory ───────────────────────────────────

    def get_inventory_stats(self):
        with self.get_conn() as conn:
            row = conn.execute("""
                SELECT
                    COUNT(*) AS total_products,
                    SUM(CASE WHEN current_stock <= reorder_level AND current_stock > 0 THEN 1 ELSE 0 END) AS low_stock,
                    SUM(CASE WHEN current_stock <= 0 THEN 1 ELSE 0 END) AS out_of_stock,
                    COALESCE(SUM(current_stock * purchase_price), 0) AS stock_value
                FROM products WHERE is_active=1
            """).fetchone()
            return dict(row) if row else {}

    def get_stock_adjustments(self, product_id=None, limit=100):
        with self.get_conn() as conn:
            q = "SELECT * FROM stock_adjustments WHERE 1=1"
            params = []
            if product_id:
                q += " AND product_id=?"
                params.append(product_id)
            q += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            return [dict(r) for r in conn.execute(q, params).fetchall()]

    def do_stock_adjustment(self, product_id: int, adj_type: str,
                             qty_change: float, reason: str, user_id: int):
        """
        adj_type: 'Add' | 'Remove' | 'Set'
        qty_change: amount to add/remove, or the new absolute value for 'Set'
        """
        with self.get_conn() as conn:
            row = conn.execute(
                "SELECT name, current_stock FROM products WHERE product_id=?",
                (product_id,)
            ).fetchone()
            if not row:
                return False
            qty_before = row["current_stock"]
            if adj_type == "Add":
                qty_after = qty_before + qty_change
            elif adj_type == "Remove":
                qty_after = max(0, qty_before - qty_change)
            else:  # Set
                qty_after = qty_change

            conn.execute(
                "UPDATE products SET current_stock=? WHERE product_id=?",
                (qty_after, product_id)
            )
            conn.execute(
                """INSERT INTO stock_adjustments
                   (product_id, product_name, adj_type, qty_before, qty_change, qty_after, reason, created_by)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (product_id, row["name"], adj_type, qty_before,
                 qty_change, qty_after, reason, user_id)
            )
            conn.commit()
        return True

    # ─── Phase 2: Suppliers ───────────────────────────────────

    def get_suppliers(self, active_only=True, search=""):
        with self.get_conn() as conn:
            q = "SELECT * FROM suppliers WHERE 1=1"
            params = []
            if active_only:
                q += " AND is_active=1"
            if search:
                q += " AND (name LIKE ? OR contact_person LIKE ? OR phone LIKE ?)"
                like = f"%{search}%"
                params += [like, like, like]
            q += " ORDER BY name"
            return [dict(r) for r in conn.execute(q, params).fetchall()]

    def get_supplier_by_id(self, supplier_id: int):
        with self.get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM suppliers WHERE supplier_id=?", (supplier_id,)
            ).fetchone()
            return dict(row) if row else None

    def add_supplier(self, data: dict) -> int:
        with self.get_conn() as conn:
            cur = conn.execute(
                """INSERT INTO suppliers
                   (name, contact_person, phone, email, city, gst_number, notes)
                   VALUES (:name,:contact_person,:phone,:email,:city,:gst_number,:notes)""",
                data
            )
            conn.commit()
            return cur.lastrowid

    def update_supplier(self, supplier_id: int, data: dict):
        with self.get_conn() as conn:
            conn.execute(
                """UPDATE suppliers SET
                   name=:name, contact_person=:contact_person, phone=:phone,
                   email=:email, city=:city, gst_number=:gst_number, notes=:notes
                   WHERE supplier_id=:supplier_id""",
                {**data, "supplier_id": supplier_id}
            )
            conn.commit()

    def deactivate_supplier(self, supplier_id: int):
        with self.get_conn() as conn:
            conn.execute(
                "UPDATE suppliers SET is_active=0 WHERE supplier_id=?", (supplier_id,)
            )
            conn.commit()

    def delete_supplier(self, supplier_id: int) -> tuple:
        """Hard delete. Returns (ok, message). Falls back to deactivate if has purchases."""
        with self.get_conn() as conn:
            used = conn.execute(
                "SELECT COUNT(*) FROM purchase_entries WHERE supplier_id=?", (supplier_id,)
            ).fetchone()[0]
            if used:
                return False, f"Supplier has {used} purchase record(s). Deactivating instead."
            conn.execute("DELETE FROM suppliers WHERE supplier_id=?", (supplier_id,))
            conn.commit()
            return True, "Supplier deleted."

    # ─── Phase 2: Purchase / GRN ──────────────────────────────

    def next_grn_number(self) -> str:
        with self.get_conn() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key='next_grn_no'").fetchone()
            if row:
                n = int(row["value"])
            else:
                n = conn.execute(
                    "SELECT COALESCE(MAX(purchase_id), 0) + 1 FROM purchase_entries"
                ).fetchone()[0]
            return f"GRN-{n:05d}"

    def save_purchase(self, purchase_data: dict, items: list, user_id: int) -> int:
        """Save GRN + items + increase stock in one transaction."""
        with self.get_conn() as conn:
            conn.execute("BEGIN IMMEDIATE")
            grn_number = self._claim_number(
                conn,
                "next_grn_no",
                "GRN",
                "SELECT COALESCE(MAX(purchase_id), 0) + 1 FROM purchase_entries"
            )
            cur = conn.execute(
                """INSERT INTO purchase_entries
                   (grn_number, supplier_id, supplier_name, total_amount, notes, created_by)
                   VALUES (?,?,?,?,?,?)""",
                (
                    grn_number,
                    purchase_data.get("supplier_id"),
                    purchase_data.get("supplier_name", "Direct Purchase"),
                    purchase_data["total_amount"],
                    purchase_data.get("notes", ""),
                    user_id,
                )
            )
            purchase_id = cur.lastrowid
            for item in items:
                prod_id = item.get("product_id")
                conn.execute(
                    """INSERT INTO purchase_items
                       (purchase_id, product_id, product_name, unit, quantity, unit_price, line_total)
                       VALUES (?,?,?,?,?,?,?)""",
                    (
                        purchase_id,
                        prod_id,
                        item["product_name"],
                        item["unit"],
                        item["quantity"],
                        item["unit_price"],
                        item["line_total"],
                    )
                )
                # Only update stock and price if product is in master (GRN-3)
                if prod_id is not None:
                    conn.execute(
                        "UPDATE products SET current_stock = current_stock + ? WHERE product_id=?",
                        (item["quantity"], prod_id)
                    )
                    conn.execute(
                        "UPDATE products SET purchase_price=? WHERE product_id=?",
                        (item["unit_price"], prod_id)
                    )
            conn.commit()
        self.log_activity(user_id, "PURCHASE_SAVED",
                          f"GRN {grn_number} saved. Total: ₹{purchase_data['total_amount']:.2f}")
        return purchase_id

    def get_purchases(self, search="", date_from=None, date_to=None, limit=200):
        with self.get_conn() as conn:
            q = """SELECT pe.*,
                          (SELECT COUNT(*) FROM purchase_items
                           WHERE purchase_id = pe.purchase_id) AS item_count
                   FROM purchase_entries pe WHERE 1=1"""
            params = []
            if search:
                q += " AND (grn_number LIKE ? OR supplier_name LIKE ?)"
                like = f"%{search}%"
                params += [like, like]
            if date_from:
                q += " AND DATE(purchase_date) >= ?"
                params.append(date_from)
            if date_to:
                q += " AND DATE(purchase_date) <= ?"
                params.append(date_to)
            q += " ORDER BY purchase_date DESC LIMIT ?"
            params.append(limit)
            return [dict(r) for r in conn.execute(q, params).fetchall()]

    def get_purchase_by_id(self, purchase_id: int):
        with self.get_conn() as conn:
            p = conn.execute(
                "SELECT * FROM purchase_entries WHERE purchase_id=?", (purchase_id,)
            ).fetchone()
            if not p:
                return None, []
            items = conn.execute(
                "SELECT * FROM purchase_items WHERE purchase_id=?", (purchase_id,)
            ).fetchall()
            return dict(p), [dict(i) for i in items]

    # --- Phase 3: Customers ---

    def get_customers(self, search="", active_only=False):
        with self.get_conn() as conn:
            q = "SELECT * FROM customers WHERE 1=1"
            params = []
            if active_only:
                q += " AND (is_active IS NULL OR is_active=1)"
            if search:
                q += " AND (name LIKE ? OR phone LIKE ?)"
                like = f"%{search}%"
                params += [like, like]
            q += " ORDER BY name"
            return [dict(r) for r in conn.execute(q, params).fetchall()]

    def get_customer_by_id(self, customer_id: int):
        with self.get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM customers WHERE customer_id=?", (customer_id,)
            ).fetchone()
            return dict(row) if row else None

    def add_customer(self, data: dict) -> int:
        with self.get_conn() as conn:
            cur = conn.execute(
                "INSERT INTO customers (name, phone, address) VALUES (:name,:phone,:address)",
                data
            )
            conn.commit()
            return cur.lastrowid

    def update_customer(self, customer_id: int, data: dict):
        with self.get_conn() as conn:
            conn.execute(
                "UPDATE customers SET name=:name, phone=:phone, address=:address WHERE customer_id=:cid",
                {**data, "cid": customer_id}
            )
            conn.commit()

    def search_customers_billing(self, query: str):
        with self.get_conn() as conn:
            like = f"%{query}%"
            rows = conn.execute(
                """SELECT customer_id, name, phone, credit_balance, change_balance
                   FROM customers
                   WHERE (is_active IS NULL OR is_active=1)
                     AND (name LIKE ? OR phone LIKE ?)
                   ORDER BY name LIMIT 8""",
                (like, like)
            ).fetchall()
            return [dict(r) for r in rows]

    def get_customer_transactions(self, customer_id: int, limit=100):
        with self.get_conn() as conn:
            rows = conn.execute(
                """SELECT * FROM customer_transactions
                   WHERE customer_id=?
                   ORDER BY txn_id DESC LIMIT ?""",
                (customer_id, limit)
            ).fetchall()
            return [dict(r) for r in rows]

    def _net_customer_balances(self, conn, customer_id: int, user_id: int, reference: str = None):
        """Net out the customer's credit_balance and change_balance.
        A customer cannot have both positive Udhaar and positive Change at the same time.
        """
        row = conn.execute(
            "SELECT credit_balance, change_balance FROM customers WHERE customer_id = ?",
            (customer_id,)
        ).fetchone()
        if not row:
            return
        credit = float(row["credit_balance"] or 0)
        change = float(row["change_balance"] or 0)
        if credit > 0 and change > 0:
            netted_amt = min(credit, change)
            new_credit = credit - netted_amt
            new_change = change - netted_amt
            conn.execute(
                "UPDATE customers SET credit_balance = ?, change_balance = ? WHERE customer_id = ?",
                (new_credit, new_change, customer_id)
            )
            # Log the automatic offsetting in the customer transaction history
            conn.execute(
                """INSERT INTO customer_transactions
                   (customer_id, txn_type, amount, reference, notes, created_by)
                   VALUES (?,?,?,?,?,?)""",
                (customer_id, "Payment", netted_amt, reference,
                 "Auto-adjusted with Change Balance", user_id)
            )
            conn.execute(
                """INSERT INTO customer_transactions
                   (customer_id, txn_type, amount, reference, notes, created_by)
                   VALUES (?,?,?,?,?,?)""",
                (customer_id, "Change Clear", netted_amt, reference,
                 "Auto-adjusted with Udhaar Balance", user_id)
            )

    def add_customer_transaction(self, customer_id: int, txn_type: str,
                                  amount: float, reference, notes, user_id: int):
        with self.get_conn() as conn:
            conn.execute(
                """INSERT INTO customer_transactions
                   (customer_id, txn_type, amount, reference, notes, created_by)
                   VALUES (?,?,?,?,?,?)""",
                (customer_id, txn_type, amount, reference, notes, user_id)
            )
            if txn_type == "Credit":
                conn.execute(
                    "UPDATE customers SET credit_balance = credit_balance + ? WHERE customer_id=?",
                    (amount, customer_id)
                )
            elif txn_type == "Payment":
                # Get current credit balance
                row = conn.execute(
                    "SELECT credit_balance FROM customers WHERE customer_id=?",
                    (customer_id,)
                ).fetchone()
                cur_bal = row["credit_balance"] if row else 0.0

                if amount > cur_bal:
                    surplus = amount - cur_bal
                    conn.execute(
                        "UPDATE customers SET credit_balance = 0, change_balance = change_balance + ? WHERE customer_id=?",
                        (surplus, customer_id)
                    )
                    # If they paid off some Udhaar and had extra change
                    if cur_bal > 0:
                        # Update the initial transaction to cover the credit payoff amount
                        conn.execute(
                            "UPDATE customer_transactions SET amount = ? WHERE txn_id = (SELECT MAX(txn_id) FROM customer_transactions)",
                            (cur_bal,)
                        )
                        # Log a second transaction for the change deposit
                        conn.execute(
                            """INSERT INTO customer_transactions
                               (customer_id, txn_type, amount, reference, notes, created_by)
                               VALUES (?,?,?,?,?,?)""",
                            (customer_id, "Change Deposit", surplus, reference,
                             "Change deposit from surplus payment", user_id)
                        )
                    else:
                        # The customer had 0 Udhaar, so convert this transaction to a Change Deposit
                        conn.execute(
                            "UPDATE customer_transactions SET txn_type = 'Change Deposit', notes = ? WHERE txn_id = (SELECT MAX(txn_id) FROM customer_transactions)",
                            ("Change deposit from payment",)
                        )
                else:
                    conn.execute(
                        "UPDATE customers SET credit_balance = credit_balance - ? WHERE customer_id=?",
                        (amount, customer_id)
                    )
            elif txn_type == "Change Deposit":
                conn.execute(
                    "UPDATE customers SET change_balance = change_balance + ? WHERE customer_id=?",
                    (amount, customer_id)
                )
            elif txn_type == "Change Clear":
                conn.execute(
                    "UPDATE customers SET change_balance = MAX(0, change_balance - ?) WHERE customer_id=?",
                    (amount, customer_id)
                )
            self._net_customer_balances(conn, customer_id, user_id, reference)
            conn.commit()

    def get_customers_summary(self):
        with self.get_conn() as conn:
            row = conn.execute("""
                SELECT COUNT(*) AS total,
                       SUM(CASE WHEN credit_balance > 0 THEN 1 ELSE 0 END) AS credit_accounts,
                       COALESCE(SUM(credit_balance), 0) AS total_udhaar
                FROM customers
                WHERE is_active IS NULL OR is_active=1
            """).fetchone()
            return dict(row) if row else {"total": 0, "credit_accounts": 0, "total_udhaar": 0}

    def deactivate_customer(self, customer_id: int):
        with self.get_conn() as conn:
            conn.execute(
                "UPDATE customers SET is_active=0 WHERE customer_id=?", (customer_id,)
            )
            conn.commit()

    def delete_customer(self, customer_id: int) -> tuple:
        """Hard delete. Returns (ok, message). Falls back to deactivate if has bills."""
        with self.get_conn() as conn:
            used = conn.execute(
                "SELECT COUNT(*) FROM bills WHERE customer_id=?", (customer_id,)
            ).fetchone()[0]
            if used:
                return False, f"Customer has {used} bill(s). Deactivating instead."
            conn.execute("DELETE FROM customer_transactions WHERE customer_id=?", (customer_id,))
            conn.execute("DELETE FROM customers WHERE customer_id=?", (customer_id,))
            conn.commit()
            return True, "Customer deleted."

    # --- Phase 3: Reports ---

    def report_daily_sales(self, date_from: str, date_to: str):
        with self.get_conn() as conn:
            rows = conn.execute("""
                SELECT DATE(bill_date) AS date,
                       COUNT(*) AS bills,
                       COALESCE(SUM(subtotal),0)    AS subtotal,
                       COALESCE(SUM(discount),0)    AS discount,
                       COALESCE(SUM(grand_total),0) AS total
                FROM bills
                WHERE status='Active'
                  AND DATE(bill_date) BETWEEN ? AND ?
                GROUP BY DATE(bill_date)
                ORDER BY date DESC
            """, (date_from, date_to)).fetchall()
            return [dict(r) for r in rows]

    def report_itemwise_sales(self, date_from: str, date_to: str):
        with self.get_conn() as conn:
            rows = conn.execute("""
                SELECT bi.product_name,
                       SUM(bi.quantity)            AS qty_sold,
                       ROUND(AVG(bi.unit_price),2) AS avg_price,
                       COALESCE(SUM(bi.discount),0) AS discount,
                       COALESCE(SUM(bi.line_total),0) AS total_sales
                FROM bill_items bi
                JOIN bills b ON bi.bill_id = b.bill_id
                WHERE b.status='Active'
                  AND DATE(b.bill_date) BETWEEN ? AND ?
                GROUP BY bi.product_name
                ORDER BY total_sales DESC
            """, (date_from, date_to)).fetchall()
            return [dict(r) for r in rows]

    def report_top_products(self, date_from: str, date_to: str, limit=15):
        with self.get_conn() as conn:
            rows = conn.execute("""
                SELECT ROW_NUMBER() OVER (ORDER BY SUM(bi.line_total) DESC) AS rank,
                       bi.product_name,
                       SUM(bi.quantity)               AS qty_sold,
                       COALESCE(SUM(bi.line_total),0) AS revenue
                FROM bill_items bi
                JOIN bills b ON bi.bill_id = b.bill_id
                WHERE b.status='Active'
                  AND DATE(b.bill_date) BETWEEN ? AND ?
                GROUP BY bi.product_id, bi.product_name
                ORDER BY revenue DESC
                LIMIT ?
            """, (date_from, date_to, limit)).fetchall()
            return [dict(r) for r in rows]

    def report_low_stock(self):
        with self.get_conn() as conn:
            rows = conn.execute("""
                SELECT p.product_code, p.name,
                       COALESCE(c.name,'---') AS category,
                       p.unit,
                       ROUND(p.current_stock,2) AS stock,
                       ROUND(p.reorder_level,2) AS reorder,
                       ROUND(p.reorder_level - p.current_stock, 2) AS shortage,
                       CASE WHEN p.current_stock <= 0 THEN 'Out of Stock'
                            ELSE 'Low Stock' END AS status
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                WHERE p.is_active=1 AND p.current_stock <= p.reorder_level
                ORDER BY shortage DESC
            """).fetchall()
            return [dict(r) for r in rows]

    def report_purchase(self, date_from: str, date_to: str):
        with self.get_conn() as conn:
            rows = conn.execute("""
                SELECT DATE(purchase_date) AS date,
                       grn_number, supplier_name,
                       (SELECT COUNT(*) FROM purchase_items
                        WHERE purchase_id=pe.purchase_id) AS items,
                       ROUND(total_amount,2) AS total
                FROM purchase_entries pe
                WHERE DATE(purchase_date) BETWEEN ? AND ?
                ORDER BY purchase_date DESC
            """, (date_from, date_to)).fetchall()
            return [dict(r) for r in rows]

    def report_profit_margin(self, date_from: str, date_to: str):
        with self.get_conn() as conn:
            rows = conn.execute("""
                SELECT bi.product_name,
                       SUM(bi.quantity)               AS qty_sold,
                       ROUND(AVG(bi.unit_price),2)    AS sell_price,
                       ROUND(p.purchase_price,2)      AS cost_price,
                       ROUND(AVG(bi.unit_price) - p.purchase_price, 2) AS margin_per_unit,
                       ROUND(
                         (AVG(bi.unit_price) - p.purchase_price) /
                         NULLIF(AVG(bi.unit_price),0) * 100, 1
                       )                              AS margin_pct,
                       ROUND(SUM(bi.quantity) *
                         (AVG(bi.unit_price) - p.purchase_price), 2) AS total_profit
                FROM bill_items bi
                JOIN bills b    ON bi.bill_id    = b.bill_id
                JOIN products p ON bi.product_id = p.product_id
                WHERE b.status='Active'
                  AND DATE(b.bill_date) BETWEEN ? AND ?
                GROUP BY bi.product_id, bi.product_name
                ORDER BY total_profit DESC
            """, (date_from, date_to)).fetchall()
            return [dict(r) for r in rows]

    def report_stock_valuation(self):
        with self.get_conn() as conn:
            rows = conn.execute("""
                SELECT p.product_code,
                       p.name,
                       COALESCE(c.name,'---') AS category,
                       p.unit,
                       ROUND(p.current_stock,2)  AS stock,
                       ROUND(p.purchase_price,2) AS cost_price,
                       ROUND(p.selling_price,2)  AS sell_price,
                       ROUND(p.current_stock * p.purchase_price, 2) AS cost_value,
                       ROUND(p.current_stock * p.selling_price,  2) AS retail_value
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                WHERE p.is_active=1
                ORDER BY cost_value DESC
            """).fetchall()
            return [dict(r) for r in rows]

    def report_customer_ledger(self, customer_id=None, date_from=None, date_to=None):
        with self.get_conn() as conn:
            q = """
                SELECT ct.created_at, c.name AS customer, c.phone,
                       ct.txn_type, ROUND(ct.amount,2) AS amount,
                       ct.reference, ct.notes
                FROM customer_transactions ct
                JOIN customers c ON ct.customer_id = c.customer_id
                WHERE 1=1
            """
            params = []
            if customer_id:
                q += " AND ct.customer_id=?"
                params.append(customer_id)
            if date_from:
                q += " AND DATE(ct.created_at) >= ?"
                params.append(date_from)
            if date_to:
                q += " AND DATE(ct.created_at) <= ?"
                params.append(date_to)
            q += " ORDER BY ct.created_at DESC"
            return [dict(r) for r in conn.execute(q, params).fetchall()]

    # ─── User Management (Phase 4) ────────────────────────────

    def get_users(self, include_inactive=False):
        with self.get_conn() as conn:
            q = "SELECT user_id, name, username, role, is_active, created_at FROM users"
            if not include_inactive:
                q += " WHERE is_active=1"
            q += " ORDER BY role, name"
            return [dict(r) for r in conn.execute(q).fetchall()]

    def add_user(self, name: str, username: str, password: str, role: str) -> tuple:
        """Returns (True, user_id) or (False, error_msg)."""
        try:
            with self.get_conn() as conn:
                cur = conn.execute(
                    "INSERT INTO users (name, username, password_hash, role) VALUES (?,?,?,?)",
                    (name.strip(), username.strip().lower(),
                     hash_password(password), role)
                )
                conn.commit()
                return True, cur.lastrowid
        except sqlite3.IntegrityError:
            return False, "Username already exists"
        except Exception as e:
            return False, str(e)

    def update_user(self, user_id: int, name: str, role: str):
        with self.get_conn() as conn:
            conn.execute(
                "UPDATE users SET name=?, role=? WHERE user_id=?",
                (name.strip(), role, user_id)
            )
            conn.commit()

    def change_password(self, user_id: int, new_password: str):
        with self.get_conn() as conn:
            conn.execute(
                "UPDATE users SET password_hash=? WHERE user_id=?",
                (hash_password(new_password), user_id)
            )
            conn.commit()

    def deactivate_user(self, user_id: int):
        with self.get_conn() as conn:
            conn.execute(
                "UPDATE users SET is_active=0 WHERE user_id=?",
                (user_id,)
            )
            conn.commit()

    def reactivate_user(self, user_id: int):
        with self.get_conn() as conn:
            conn.execute(
                "UPDATE users SET is_active=1 WHERE user_id=?",
                (user_id,)
            )
            conn.commit()

    def get_user_by_id(self, user_id: int):
        with self.get_conn() as conn:
            row = conn.execute(
                "SELECT user_id, name, username, role, is_active FROM users WHERE user_id=?",
                (user_id,)
            ).fetchone()
            return dict(row) if row else None

    # ─── Activity Log (Phase 4) ───────────────────────────────

    def get_activity_log(self, search="", limit=200, offset=0):
        with self.get_conn() as conn:
            base = """
                SELECT al.log_id,
                       COALESCE(u.name, 'System') AS user_name,
                       COALESCE(u.role, '---')     AS role,
                       al.action,
                       al.details,
                       al.timestamp
                FROM activity_log al
                LEFT JOIN users u ON al.user_id = u.user_id
            """
            if search:
                base += " WHERE al.action LIKE ? OR al.details LIKE ? OR u.name LIKE ?"
                params = (f"%{search}%", f"%{search}%", f"%{search}%")
            else:
                params = ()
            base += " ORDER BY al.timestamp DESC LIMIT ? OFFSET ?"
            params = params + (limit, offset)
            return [dict(r) for r in conn.execute(base, params).fetchall()]

    def get_activity_log_count(self, search="") -> int:
        with self.get_conn() as conn:
            if search:
                row = conn.execute(
                    """SELECT COUNT(*) FROM activity_log al
                       LEFT JOIN users u ON al.user_id=u.user_id
                       WHERE al.action LIKE ? OR al.details LIKE ? OR u.name LIKE ?""",
                    (f"%{search}%", f"%{search}%", f"%{search}%")
                ).fetchone()
            else:
                row = conn.execute("SELECT COUNT(*) FROM activity_log").fetchone()
            return row[0] if row else 0

    # ─── Settings bulk get/set (Phase 4) ─────────────────────

    def get_all_settings(self) -> dict:
        with self.get_conn() as conn:
            rows = conn.execute("SELECT key, value FROM settings").fetchall()
            return {r["key"]: r["value"] for r in rows}

    def save_settings_bulk(self, settings_dict: dict):
        with self.get_conn() as conn:
            for key, value in settings_dict.items():
                conn.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)"
                    , (key, str(value))
                )
            conn.commit()

    # ─── P1 Missing Reports ────────────────────────────────────

    def report_slow_moving(self, days: int = 30):
        """Products with zero sales in the last N days."""
        with self.get_conn() as conn:
            rows = conn.execute("""
                SELECT p.product_code,
                       p.name,
                       COALESCE(c.name,'---')      AS category,
                       p.unit,
                       ROUND(p.current_stock,2)    AS current_stock,
                       ROUND(p.selling_price,2)    AS selling_price,
                       COALESCE(last_sale.last_sold,'Never') AS last_sold,
                       COALESCE(last_sale.total_qty_sold,0)  AS total_qty_30d
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                LEFT JOIN (
                    SELECT bi.product_id,
                           MAX(DATE(b.bill_date))   AS last_sold,
                           SUM(bi.quantity)          AS total_qty_sold
                    FROM bill_items bi
                    JOIN bills b ON bi.bill_id = b.bill_id
                    WHERE b.status = 'Active'
                      AND DATE(b.bill_date) >= DATE('now',?)
                    GROUP BY bi.product_id
                ) last_sale ON p.product_id = last_sale.product_id
                WHERE p.is_active = 1
                  AND COALESCE(last_sale.total_qty_sold, 0) = 0
                ORDER BY p.current_stock DESC
            """, (f"-{days} days",)).fetchall()
            return [dict(r) for r in rows]

    def report_supplier_payables(self):
        """Outstanding payables per supplier with ageing buckets."""
        with self.get_conn() as conn:
            rows = conn.execute("""
                SELECT pe.supplier_name,
                       pe.grn_number,
                       DATE(pe.purchase_date)              AS purchase_date,
                       ROUND(pe.total_amount, 2)           AS invoice_amount,
                       COALESCE(ROUND(SUM(sp.paid_amount),2), 0)  AS paid_amount,
                       ROUND(pe.total_amount -
                             COALESCE(SUM(sp.paid_amount),0), 2)  AS balance,
                       CAST(JULIANDAY('now') -
                            JULIANDAY(pe.purchase_date) AS INTEGER) AS age_days,
                       CASE
                         WHEN CAST(JULIANDAY('now') - JULIANDAY(pe.purchase_date) AS INTEGER) <= 30
                              THEN '0-30 days'
                         WHEN CAST(JULIANDAY('now') - JULIANDAY(pe.purchase_date) AS INTEGER) <= 60
                              THEN '31-60 days'
                         ELSE '60+ days'
                       END AS ageing
                FROM purchase_entries pe
                LEFT JOIN supplier_payments sp
                       ON sp.purchase_id = pe.purchase_id
                GROUP BY pe.purchase_id
                HAVING balance > 0
                ORDER BY age_days DESC
            """).fetchall()
            return [dict(r) for r in rows]

    def report_customer_ageing(self):
        """Customer credit balances broken into 0-30/31-60/60+ day buckets."""
        with self.get_conn() as conn:
            rows = conn.execute("""
                SELECT c.name                                        AS customer,
                       c.phone,
                       ROUND(c.credit_balance, 2)                   AS total_due,
                       ROUND(COALESCE(b0_30.amt,  0), 2)            AS due_0_30,
                       ROUND(COALESCE(b31_60.amt, 0), 2)            AS due_31_60,
                       ROUND(COALESCE(b60p.amt,   0), 2)            AS due_60plus,
                       COALESCE(last_txn.last_date, '—')            AS last_txn_date
                FROM customers c
                LEFT JOIN (
                    SELECT customer_id, SUM(amount) AS amt
                    FROM customer_transactions
                    WHERE txn_type='Credit'
                      AND DATE(created_at) >= DATE('now','-30 days')
                    GROUP BY customer_id
                ) b0_30  ON b0_30.customer_id  = c.customer_id
                LEFT JOIN (
                    SELECT customer_id, SUM(amount) AS amt
                    FROM customer_transactions
                    WHERE txn_type='Credit'
                      AND DATE(created_at) BETWEEN DATE('now','-60 days')
                                               AND DATE('now','-31 days')
                    GROUP BY customer_id
                ) b31_60 ON b31_60.customer_id = c.customer_id
                LEFT JOIN (
                    SELECT customer_id, SUM(amount) AS amt
                    FROM customer_transactions
                    WHERE txn_type='Credit'
                      AND DATE(created_at) < DATE('now','-60 days')
                    GROUP BY customer_id
                ) b60p   ON b60p.customer_id   = c.customer_id
                LEFT JOIN (
                    SELECT customer_id, MAX(DATE(created_at)) AS last_date
                    FROM customer_transactions
                    GROUP BY customer_id
                ) last_txn ON last_txn.customer_id = c.customer_id
                WHERE c.credit_balance > 0
                  AND (c.is_active IS NULL OR c.is_active = 1)
                ORDER BY c.credit_balance DESC
            """).fetchall()
            return [dict(r) for r in rows]

    # --- Supplier Payments -------------------------------------------

    def get_outstanding_purchases(self, supplier_id: int):
        """Return unpaid / partially-paid purchase entries for a supplier."""
        with self.get_conn() as conn:
            rows = conn.execute("""
                SELECT pe.purchase_id,
                       pe.grn_number,
                       DATE(pe.purchase_date)                         AS purchase_date,
                       ROUND(pe.total_amount, 2)                      AS invoice_amount,
                       COALESCE(ROUND(SUM(sp.paid_amount),2), 0)      AS paid_amount,
                       ROUND(pe.total_amount -
                             COALESCE(SUM(sp.paid_amount),0), 2)      AS balance
                FROM purchase_entries pe
                LEFT JOIN supplier_payments sp ON sp.purchase_id = pe.purchase_id
                WHERE pe.supplier_id = ?
                GROUP BY pe.purchase_id
                HAVING balance > 0
                ORDER BY pe.purchase_date
            """, (supplier_id,)).fetchall()
            return [dict(r) for r in rows]

    def record_supplier_payment(self, purchase_id: int, paid_amount: float,
                                notes: str = None, created_by: int = None):
        """Record a partial or full payment against a purchase entry."""
        with self.get_conn() as conn:
            conn.execute(
                """INSERT INTO supplier_payments
                   (purchase_id, paid_amount, notes, created_by)
                   VALUES (?,?,?,?)""",
                (purchase_id, paid_amount, notes or None, created_by)
            )
            conn.commit()

    # --- Expiry Tracking ---------------------------------------------

    def get_expiring_products(self, days: int = 30):
        """Return active products whose expiry_date is within `days` days (or already expired)."""
        with self.get_conn() as conn:
            rows = conn.execute("""
                SELECT p.product_id,
                       p.name,
                       COALESCE(p.product_code, '') AS product_code,
                       COALESCE(cat.name, '')       AS category_name,
                       p.current_stock,
                       p.expiry_date,
                       CAST(JULIANDAY(p.expiry_date) - JULIANDAY('now') AS INTEGER) AS days_left
                FROM products p
                LEFT JOIN categories cat ON cat.category_id = p.category_id
                WHERE p.is_active = 1
                  AND p.expiry_date IS NOT NULL
                  AND p.expiry_date != ''
                  AND JULIANDAY(p.expiry_date) <= JULIANDAY('now', '+' || ? || ' days')
                ORDER BY p.expiry_date
            """, (days,)).fetchall()
            return [dict(r) for r in rows]

    def get_expiring_count(self, days: int = 30) -> int:
        """Quick count of products expiring within `days` days."""
        with self.get_conn() as conn:
            row = conn.execute("""
                SELECT COUNT(*) AS cnt FROM products
                WHERE is_active = 1
                  AND expiry_date IS NOT NULL
                  AND expiry_date != ''
                  AND JULIANDAY(expiry_date) <= JULIANDAY('now', '+' || ? || ' days')
            """, (days,)).fetchone()
            return row["cnt"] if row else 0

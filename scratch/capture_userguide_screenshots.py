from __future__ import annotations

import re
import sys
import time
from pathlib import Path

from PIL import ImageGrab

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from main import BillingApp


OUT_DIR = ROOT / "output" / "userguide" / "screenshots"


SCREENS = [
    ("login", "Login"),
    ("dashboard", "Dashboard"),
    ("billing", "New Bill"),
    ("bill_history", "Bill History"),
    ("products", "Products"),
    ("categories", "Categories"),
    ("inventory", "Inventory"),
    ("suppliers", "Suppliers"),
    ("purchase", "Purchase GRN"),
    ("customers", "Customers"),
    ("reports", "Reports"),
    ("settings", "Settings"),
    ("users", "Users"),
    ("activity_log", "Activity Log"),
]


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def settle(app: BillingApp, seconds: float = 0.8) -> None:
    end = time.time() + seconds
    while time.time() < end:
        app.update()
        time.sleep(0.05)


def capture(app: BillingApp, label: str) -> Path:
    app.update_idletasks()
    img = ImageGrab.grab(window=app.winfo_id())
    path = OUT_DIR / f"{slug(label)}.png"
    img.save(path)
    return path


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    app = BillingApp()
    app.lift()
    app.focus_force()
    settle(app, 1.0)
    capture(app, "Login")

    user = app.db.authenticate("admin", "admin123")
    if not user:
        raise RuntimeError("Default admin credentials did not authenticate")

    app.current_user = user
    app.current_role = user["role"]
    app._build_main_window()

    for key, label in SCREENS[1:]:
        app.navigate_to(key)
        settle(app, 1.0)
        capture(app, label)

    app.destroy()


if __name__ == "__main__":
    main()

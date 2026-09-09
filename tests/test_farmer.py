"""
Stage 2 independent test: Farmer helpers + registration API.

Uses a temporary SQLite file so agrilink.db is not changed.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app import create_app
from models import FarmerError, create_farmer, get_farmer, list_farmers


def run_tests() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "stage2_test.db"
        app = create_app(db_path)

        farmer = create_farmer(
            "Ravi Kumar",
            "9876543210",
            "Nashik",
            db_path=db_path,
        )
        assert farmer["farmer_id"] == 1
        assert farmer["name"] == "Ravi Kumar"
        assert farmer["phone"] == "9876543210"
        assert farmer["location"] == "Nashik"
        assert farmer["created_at"]

        listed = list_farmers(db_path=db_path)
        assert len(listed) == 1
        assert get_farmer(1, db_path=db_path)["name"] == "Ravi Kumar"
        assert get_farmer(99, db_path=db_path) is None

        try:
            create_farmer("Other", "9876543210", "Pune", db_path=db_path)
            raise AssertionError("Duplicate phone should have failed.")
        except FarmerError as exc:
            assert exc.code == "duplicate_phone"

        try:
            create_farmer("  ", "111", "Pune", db_path=db_path)
            raise AssertionError("Blank name should have failed.")
        except FarmerError:
            pass

        client = app.test_client()

        response = client.post(
            "/farmers",
            json={
                "name": "Meena Patil",
                "phone": "9123456780",
                "location": "Pune",
            },
        )
        assert response.status_code == 201, response.get_json()
        body = response.get_json()
        assert body["name"] == "Meena Patil"

        duplicate = client.post(
            "/farmers",
            json={
                "name": "Clone",
                "phone": "9123456780",
                "location": "Pune",
            },
        )
        assert duplicate.status_code == 409

        missing = client.post("/farmers", json={"name": "Only Name"})
        assert missing.status_code == 400

        listing = client.get("/farmers")
        assert listing.status_code == 200
        payload = listing.get_json()
        assert payload["count"] == 2

        detail = client.get("/farmers/1")
        assert detail.status_code == 200
        missing_id = client.get("/farmers/999")
        assert missing_id.status_code == 404

    print("Stage 2 farmer tests passed.")


if __name__ == "__main__":
    run_tests()

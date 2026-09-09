"""
AgriLink AI — Flask API.

Stage 2: Farmer Registration.
"""

from __future__ import annotations

import sys
from pathlib import Path

from flask import Flask, jsonify, request

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from database import initialize_database
from models import FarmerError, create_farmer, get_farmer, list_farmers


def create_app(db_path=None) -> Flask:
    initialize_database(db_path)
    app = Flask(__name__)
    app.config["DATABASE_PATH"] = db_path

    @app.route("/")
    def home():
        return {
            "message": "Welcome to AgriLink AI",
            "status": "Backend is running successfully",
            "stage": 2,
        }

    @app.post("/farmers")
    def register_farmer():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Send JSON with name, phone, and location."}), 400

        try:
            farmer = create_farmer(
                name=data.get("name"),
                phone=data.get("phone"),
                location=data.get("location"),
                db_path=app.config["DATABASE_PATH"],
            )
        except FarmerError as exc:
            status = 409 if exc.code == "duplicate_phone" else 400
            return jsonify({"error": str(exc)}), status

        return jsonify(farmer), 201

    @app.get("/farmers")
    def farmers_list():
        farmers = list_farmers(db_path=app.config["DATABASE_PATH"])
        return jsonify({"count": len(farmers), "farmers": farmers})

    @app.get("/farmers/<int:farmer_id>")
    def farmer_detail(farmer_id: int):
        farmer = get_farmer(farmer_id, db_path=app.config["DATABASE_PATH"])
        if farmer is None:
            return jsonify({"error": "Farmer not found."}), 404
        return jsonify(farmer)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)

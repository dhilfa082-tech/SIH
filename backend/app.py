"""
AgriLink AI — Complete Flask Backend + ML Price Prediction

SIH 2026
Problem Statement 26132

Complete workflow:

Farmer
→ Produce
→ Smart Pooling
→ Buyer
→ Smart Matching
→ Match Management
→ Journey Tracking
→ ML Market Price Prediction
"""

from __future__ import annotations

import sys
from pathlib import Path

import joblib
import pandas as pd

from flask import Flask, jsonify, request
from flask_cors import CORS


# =========================================================
# PATH SETUP
# =========================================================

BACKEND_DIR = Path(__file__).resolve().parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


# =========================================================
# ML MODEL SETUP
# =========================================================

MODEL_PATH = BACKEND_DIR / "agrilink_price_model.pkl"

try:
    price_model = joblib.load(MODEL_PATH)
    print("ML Price Prediction Model loaded successfully.")
except FileNotFoundError:
    price_model = None
    print("WARNING: agrilink_price_model.pkl was not found.")
except Exception as e:
    price_model = None
    print(f"WARNING: Could not load ML model: {e}")


# =========================================================
# IMPORTS
# =========================================================

from database import initialize_database

from models import (
    FarmerError,
    ProduceError,
    PoolError,
    BuyerError,
    MatchError,

    create_farmer,
    list_farmers,
    get_farmer,

    create_produce,
    list_produce,
    get_produce,

    create_pool,
    list_pools,
    get_pool,
    add_produce_to_pool,
    get_pool_details,

    create_buyer,
    list_buyers,
    get_buyer,

    get_match_suggestions,
    create_match,
    list_matches,
    get_match,
    update_match_status,

    get_journey,
)


# =========================================================
# CREATE APPLICATION
# =========================================================

def create_app(db_path=None):

    initialize_database(db_path)

    app = Flask(__name__)

    CORS(app)

    app.config["DATABASE_PATH"] = db_path


    # =====================================================
    # HOME
    # =====================================================

    @app.get("/")
    def home():

        return jsonify({

            "message": "Welcome to AgriLink AI",

            "status": "Complete backend is running successfully",

            "workflow": [

                "Farmer Registration",

                "Produce Registration",

                "Smart Farmer Pooling",

                "Buyer Registration",

                "Smart Buyer Matching",

                "Match Management",

                "Journey Tracking",

                "ML Market Price Prediction",

            ],
        })


    # =====================================================
    # ML MARKET PRICE PREDICTION
    # =====================================================

    @app.post("/predict-price")
    def predict_price():

        if price_model is None:

            return jsonify({
                "error": "ML model is not loaded.",
                "message": "Check agrilink_price_model.pkl in the backend folder."
            }), 500

        data = request.get_json(silent=True)

        if not isinstance(data, dict):

            return jsonify({
                "error": "Invalid JSON data."
            }), 400

        required_fields = [

            "year",
            "month",
            "day",
            "arrival_quantity",
            "min_price",
            "max_price",
            "previous_modal_price"

        ]

        missing_fields = [

            field for field in required_fields
            if data.get(field) is None

        ]

        if missing_fields:

            return jsonify({

                "error": "Missing required fields.",

                "missing_fields": missing_fields,

                "required_fields": required_fields

            }), 400

        try:

            # Create data exactly in the same order
            # used while training the ML model

            input_data = pd.DataFrame([{

                "Year": float(data["year"]),

                "Month": float(data["month"]),

                "Day": float(data["day"]),

                "Arrival Quantity":
                    float(data["arrival_quantity"]),

                "Min Price":
                    float(data["min_price"]),

                "Max Price":
                    float(data["max_price"]),

                "Previous_Modal_Price":
                    float(data["previous_modal_price"]),

            }])

            prediction = price_model.predict(input_data)[0]

            return jsonify({

                "message":
                    "Market price predicted successfully.",

                "predicted_modal_price":
                    round(float(prediction), 2),

                "currency":
                    "INR",

                "input_data": {

                    "year": data["year"],

                    "month": data["month"],

                    "day": data["day"],

                    "arrival_quantity":
                        data["arrival_quantity"],

                    "min_price":
                        data["min_price"],

                    "max_price":
                        data["max_price"],

                    "previous_modal_price":
                        data["previous_modal_price"]

                }

            }), 200

        except ValueError as e:

            return jsonify({

                "error":
                    "All prediction inputs must be valid numbers.",

                "details":
                    str(e)

            }), 400

        except Exception as e:

            return jsonify({

                "error":
                    "Prediction failed.",

                "details":
                    str(e)

            }), 500


    # =====================================================
    # FARMERS
    # =====================================================

    @app.post("/farmers")
    def register_farmer():

        data = request.get_json(silent=True)

        if not isinstance(data, dict):

            return jsonify({
                "error":
                    "Send JSON with name, phone and location."
            }), 400

        try:

            farmer = create_farmer(

                name=data.get("name"),

                phone=data.get("phone"),

                location=data.get("location"),

                db_path=app.config["DATABASE_PATH"],
            )

        except FarmerError as exc:

            status = (
                409
                if exc.code == "duplicate_phone"
                else 400
            )

            return jsonify({
                "error": str(exc)
            }), status

        return jsonify(farmer), 201


    @app.get("/farmers")
    def farmers():

        data = list_farmers(
            app.config["DATABASE_PATH"]
        )

        return jsonify({

            "count": len(data),

            "farmers": data,

        })


    @app.get("/farmers/<int:farmer_id>")
    def farmer(farmer_id):

        data = get_farmer(

            farmer_id,

            app.config["DATABASE_PATH"],
        )

        if data is None:

            return jsonify({
                "error":
                    "Farmer not found."
            }), 404

        return jsonify(data)


    # =====================================================
    # PRODUCE
    # =====================================================

    @app.post("/produce")
    def register_produce():

        data = request.get_json(silent=True)

        if not isinstance(data, dict):

            return jsonify({
                "error":
                    "Invalid JSON data."
            }), 400

        try:

            produce = create_produce(

                farmer_id=data.get("farmer_id"),

                crop_name=data.get("crop_name"),

                quantity_kg=data.get("quantity_kg"),

                location=data.get("location"),

                availability_date=data.get("availability_date"),

                db_path=app.config["DATABASE_PATH"],
            )

        except ProduceError as exc:

            status = (
                404
                if exc.code == "farmer_not_found"
                else 400
            )

            return jsonify({
                "error": str(exc)
            }), status

        return jsonify(produce), 201


    @app.get("/produce")
    def produce():

        data = list_produce(
            app.config["DATABASE_PATH"]
        )

        return jsonify({

            "count": len(data),

            "produce": data,

        })


    @app.get("/produce/<int:produce_id>")
    def produce_detail(produce_id):

        data = get_produce(

            produce_id,

            app.config["DATABASE_PATH"],
        )

        if data is None:

            return jsonify({
                "error":
                    "Produce not found."
            }), 404

        return jsonify(data)


    # =====================================================
    # SMART POOLING
    # =====================================================

    @app.post("/pools")
    def create_new_pool():

        data = request.get_json(silent=True)

        if not isinstance(data, dict):

            return jsonify({
                "error":
                    "Send crop_name and location."
            }), 400

        try:

            pool = create_pool(

                crop_name=data.get("crop_name"),

                location=data.get("location"),

                db_path=app.config["DATABASE_PATH"],
            )

        except PoolError as exc:

            return jsonify({
                "error": str(exc)
            }), 400

        return jsonify(pool), 201


    @app.get("/pools")
    def pools():

        data = list_pools(
            app.config["DATABASE_PATH"]
        )

        return jsonify({

            "count": len(data),

            "pools": data,

        })


    @app.get("/pools/<int:pool_id>")
    def pool(pool_id):

        data = get_pool(

            pool_id,

            app.config["DATABASE_PATH"],
        )

        if data is None:

            return jsonify({
                "error":
                    "Pool not found."
            }), 404

        return jsonify(data)


    @app.post("/pools/<int:pool_id>/produce/<int:produce_id>")
    def add_produce(pool_id, produce_id):

        try:

            pool = add_produce_to_pool(

                pool_id,

                produce_id,

                app.config["DATABASE_PATH"],
            )

        except PoolError as exc:

            status = (
                404
                if exc.code in (
                    "pool_not_found",
                    "produce_not_found",
                )
                else 400
            )

            return jsonify({
                "error": str(exc)
            }), status

        return jsonify({

            "message":
                "Produce successfully added to pool.",

            "pool": pool,

        })


    @app.get("/pools/<int:pool_id>/details")
    def pool_details(pool_id):

        data = get_pool_details(

            pool_id,

            app.config["DATABASE_PATH"],
        )

        if data is None:

            return jsonify({
                "error":
                    "Pool not found."
            }), 404

        return jsonify(data)


    # =====================================================
    # BUYERS
    # =====================================================

    @app.post("/buyers")
    def register_buyer():

        data = request.get_json(silent=True)

        if not isinstance(data, dict):

            return jsonify({
                "error":
                    "Invalid JSON data."
            }), 400

        try:

            buyer = create_buyer(

                buyer_name=data.get("buyer_name"),

                crop_name=data.get("crop_name"),

                required_quantity_kg=data.get(
                    "required_quantity_kg"
                ),

                location=data.get("location"),

                urgency=data.get(
                    "urgency",
                    "normal",
                ),

                db_path=app.config["DATABASE_PATH"],
            )

        except BuyerError as exc:

            return jsonify({
                "error": str(exc)
            }), 400

        return jsonify(buyer), 201


    @app.get("/buyers")
    def buyers():

        data = list_buyers(
            app.config["DATABASE_PATH"]
        )

        return jsonify({

            "count": len(data),

            "buyers": data,

        })


    @app.get("/buyers/<int:buyer_id>")
    def buyer(buyer_id):

        data = get_buyer(

            buyer_id,

            app.config["DATABASE_PATH"],
        )

        if data is None:

            return jsonify({
                "error":
                    "Buyer not found."
            }), 404

        return jsonify(data)


    # =====================================================
    # SMART MATCHING
    # =====================================================

    @app.get("/matches/suggestions")
    def match_suggestions():

        suggestions = get_match_suggestions(

            app.config["DATABASE_PATH"]
        )

        return jsonify({

            "count": len(suggestions),

            "suggestions": suggestions,

        })


    @app.post("/matches")
    def create_new_match():

        data = request.get_json(silent=True)

        if not isinstance(data, dict):

            return jsonify({
                "error":
                    "Send pool_id and buyer_id."
            }), 400

        try:

            match = create_match(

                pool_id=data.get("pool_id"),

                buyer_id=data.get("buyer_id"),

                price_per_kg=data.get("price_per_kg"),

                db_path=app.config["DATABASE_PATH"],
            )

        except MatchError as exc:

            status = (
                404
                if exc.code in (
                    "pool_not_found",
                    "buyer_not_found",
                )
                else 400
            )

            return jsonify({
                "error": str(exc)
            }), status

        return jsonify(match), 201


    @app.get("/matches")
    def matches():

        data = list_matches(
            app.config["DATABASE_PATH"]
        )

        return jsonify({

            "count": len(data),

            "matches": data,

        })


    @app.get("/matches/<int:match_id>")
    def match(match_id):

        data = get_match(

            match_id,

            app.config["DATABASE_PATH"],
        )

        if data is None:

            return jsonify({
                "error":
                    "Match not found."
            }), 404

        return jsonify(data)


    # =====================================================
    # MATCH CONFIRMATION
    # =====================================================

    @app.post("/matches/<int:match_id>/confirm")
    def confirm_match(match_id):

        try:

            data = update_match_status(

                match_id,

                "confirmed",

                app.config["DATABASE_PATH"],
            )

        except MatchError as exc:

            status = (
                404
                if exc.code == "match_not_found"
                else 400
            )

            return jsonify({
                "error": str(exc)
            }), status

        return jsonify(data)


    # =====================================================
    # MATCH REJECTION
    # =====================================================

    @app.post("/matches/<int:match_id>/reject")
    def reject_match(match_id):

        try:

            data = update_match_status(

                match_id,

                "rejected",

                app.config["DATABASE_PATH"],
            )

        except MatchError as exc:

            status = (
                404
                if exc.code == "match_not_found"
                else 400
            )

            return jsonify({
                "error": str(exc)
            }), status

        return jsonify(data)


    # =====================================================
    # MATCH COMPLETION
    # =====================================================

    @app.post("/matches/<int:match_id>/complete")
    def complete_match(match_id):

        try:

            data = update_match_status(

                match_id,

                "completed",

                app.config["DATABASE_PATH"],
            )

        except MatchError as exc:

            status = (
                404
                if exc.code == "match_not_found"
                else 400
            )

            return jsonify({
                "error": str(exc)
            }), status

        return jsonify(data)


    # =====================================================
    # JOURNEY TRACKING
    # =====================================================

    @app.get("/journey/<string:ref_type>/<int:ref_id>")
    def journey(ref_type, ref_id):

        allowed_types = (
            "produce",
            "pool",
            "match",
        )

        if ref_type not in allowed_types:

            return jsonify({

                "error":
                    "ref_type must be produce, pool, or match."

            }), 400

        data = get_journey(

            ref_type,

            ref_id,

            app.config["DATABASE_PATH"],
        )

        return jsonify({

            "ref_type": ref_type,

            "ref_id": ref_id,

            "journey": data,

        })


    # =====================================================
    # RETURN APPLICATION
    # =====================================================

    return app


# =========================================================
# APPLICATION ENTRY POINT
# =========================================================

app = create_app()


if __name__ == "__main__":

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True,

    )
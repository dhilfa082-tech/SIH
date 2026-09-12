"""
AgriLink AI - Core Business Logic

Complete workflow:

Farmer
→ Produce
→ Pool
→ Buyer
→ Match
→ Journey Tracking
"""

from __future__ import annotations

import sqlite3

from datetime import datetime

from typing import Any

from database import get_connection


# =========================================================
# ERRORS
# =========================================================


class FarmerError(Exception):

    def __init__(self, message, code="invalid"):
        super().__init__(message)
        self.code = code


class ProduceError(Exception):

    def __init__(self, message, code="invalid"):
        super().__init__(message)
        self.code = code


class PoolError(Exception):

    def __init__(self, message, code="invalid"):
        super().__init__(message)
        self.code = code


class BuyerError(Exception):

    def __init__(self, message, code="invalid"):
        super().__init__(message)
        self.code = code


class MatchError(Exception):

    def __init__(self, message, code="invalid"):
        super().__init__(message)
        self.code = code


# =========================================================
# COMMON VALIDATION
# =========================================================


def clean_text(value: Any, field_name: str):

    if value is None:
        raise ValueError(
            f"{field_name} is required."
        )

    value = str(value).strip()

    if not value:
        raise ValueError(
            f"{field_name} is required."
        )

    return value


def clean_quantity(value: Any, field_name="quantity_kg"):

    if value is None:
        raise ValueError(
            f"{field_name} is required."
        )

    try:
        value = float(value)

    except (TypeError, ValueError):

        raise ValueError(
            f"{field_name} must be a number."
        )

    if value <= 0:

        raise ValueError(
            f"{field_name} must be greater than 0."
        )

    return value


# =========================================================
# JOURNEY LOG
# =========================================================


def add_journey_log(
    ref_type,
    ref_id,
    current_status,
    db_path=None,
):

    connection = get_connection(db_path)

    try:

        connection.execute(
            """
            INSERT INTO JourneyLog
            (
                ref_type,
                ref_id,
                current_status
            )
            VALUES (?, ?, ?)
            """,
            (
                ref_type,
                ref_id,
                current_status,
            ),
        )

        connection.commit()

    finally:

        connection.close()


def get_journey(
    ref_type,
    ref_id,
    db_path=None,
):

    connection = get_connection(db_path)

    try:

        rows = connection.execute(
            """
            SELECT *
            FROM JourneyLog
            WHERE ref_type = ?
            AND ref_id = ?
            ORDER BY journey_id
            """,
            (
                ref_type,
                ref_id,
            ),
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        connection.close()


# =========================================================
# FARMER
# =========================================================


def row_to_farmer(row):

    return dict(row)


def create_farmer(
    name,
    phone,
    location,
    db_path=None,
):

    try:

        name = clean_text(name, "name")
        phone = clean_text(phone, "phone")
        location = clean_text(location, "location")

    except ValueError as exc:

        raise FarmerError(str(exc))

    connection = get_connection(db_path)

    try:

        cursor = connection.execute(
            """
            INSERT INTO Farmer
            (
                name,
                phone,
                location
            )
            VALUES (?, ?, ?)
            """,
            (
                name,
                phone,
                location,
            ),
        )

        connection.commit()

        farmer_id = cursor.lastrowid

        row = connection.execute(
            """
            SELECT *
            FROM Farmer
            WHERE farmer_id = ?
            """,
            (farmer_id,),
        ).fetchone()

        return row_to_farmer(row)

    except sqlite3.IntegrityError:

        raise FarmerError(
            "A farmer with this phone number is already registered.",
            "duplicate_phone",
        )

    finally:

        connection.close()


def list_farmers(db_path=None):

    connection = get_connection(db_path)

    try:

        rows = connection.execute(
            """
            SELECT *
            FROM Farmer
            ORDER BY farmer_id
            """
        ).fetchall()

        return [
            row_to_farmer(row)
            for row in rows
        ]

    finally:

        connection.close()


def get_farmer(
    farmer_id,
    db_path=None,
):

    connection = get_connection(db_path)

    try:

        row = connection.execute(
            """
            SELECT *
            FROM Farmer
            WHERE farmer_id = ?
            """,
            (farmer_id,),
        ).fetchone()

        return (
            row_to_farmer(row)
            if row
            else None
        )

    finally:

        connection.close()


# =========================================================
# PRODUCE
# =========================================================


def create_produce(
    farmer_id,
    crop_name,
    quantity_kg,
    location,
    availability_date,
    db_path=None,
):

    if farmer_id is None:

        raise ProduceError(
            "farmer_id is required."
        )

    farmer = get_farmer(
        farmer_id,
        db_path,
    )

    if farmer is None:

        raise ProduceError(
            "No farmer exists with that farmer_id.",
            "farmer_not_found",
        )

    try:

        crop_name = clean_text(
            crop_name,
            "crop_name",
        )

        quantity_kg = clean_quantity(
            quantity_kg,
        )

        location = clean_text(
            location,
            "location",
        )

        availability_date = clean_text(
            availability_date,
            "availability_date",
        )

        datetime.strptime(
            availability_date,
            "%Y-%m-%d",
        )

    except ValueError as exc:

        raise ProduceError(str(exc))

    connection = get_connection(db_path)

    try:

        cursor = connection.execute(
            """
            INSERT INTO Produce
            (
                farmer_id,
                crop_name,
                quantity_kg,
                location,
                availability_date
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                farmer_id,
                crop_name,
                quantity_kg,
                location,
                availability_date,
            ),
        )

        connection.commit()

        produce_id = cursor.lastrowid

        row = connection.execute(
            """
            SELECT *
            FROM Produce
            WHERE produce_id = ?
            """,
            (produce_id,),
        ).fetchone()

        produce = dict(row)

    finally:

        connection.close()

    add_journey_log(
        "produce",
        produce_id,
        "registered",
        db_path,
    )

    return produce


def list_produce(db_path=None):

    connection = get_connection(db_path)

    try:

        rows = connection.execute(
            """
            SELECT *
            FROM Produce
            ORDER BY produce_id
            """
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        connection.close()


def get_produce(
    produce_id,
    db_path=None,
):

    connection = get_connection(db_path)

    try:

        row = connection.execute(
            """
            SELECT *
            FROM Produce
            WHERE produce_id = ?
            """,
            (produce_id,),
        ).fetchone()

        return (
            dict(row)
            if row
            else None
        )

    finally:

        connection.close()


# =========================================================
# POOL
# =========================================================


def create_pool(
    crop_name,
    location,
    db_path=None,
):

    try:

        crop_name = clean_text(
            crop_name,
            "crop_name",
        )

        location = clean_text(
            location,
            "location",
        )

    except ValueError as exc:

        raise PoolError(str(exc))

    connection = get_connection(db_path)

    try:

        cursor = connection.execute(
            """
            INSERT INTO Pool
            (
                crop_name,
                location
            )
            VALUES (?, ?)
            """,
            (
                crop_name,
                location,
            ),
        )

        connection.commit()

        pool_id = cursor.lastrowid

        row = connection.execute(
            """
            SELECT *
            FROM Pool
            WHERE pool_id = ?
            """,
            (pool_id,),
        ).fetchone()

        pool = dict(row)

    finally:

        connection.close()

    add_journey_log(
        "pool",
        pool_id,
        "open",
        db_path,
    )

    return pool


def list_pools(db_path=None):

    connection = get_connection(db_path)

    try:

        rows = connection.execute(
            """
            SELECT *
            FROM Pool
            ORDER BY pool_id
            """
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        connection.close()


def get_pool(
    pool_id,
    db_path=None,
):

    connection = get_connection(db_path)

    try:

        row = connection.execute(
            """
            SELECT *
            FROM Pool
            WHERE pool_id = ?
            """,
            (pool_id,),
        ).fetchone()

        return (
            dict(row)
            if row
            else None
        )

    finally:

        connection.close()


def add_produce_to_pool(
    pool_id,
    produce_id,
    db_path=None,
):

    pool = get_pool(
        pool_id,
        db_path,
    )

    if pool is None:

        raise PoolError(
            "Pool not found.",
            "pool_not_found",
        )

    produce = get_produce(
        produce_id,
        db_path,
    )

    if produce is None:

        raise PoolError(
            "Produce not found.",
            "produce_not_found",
        )

    if produce["pool_id"] is not None:

        raise PoolError(
            "Produce is already assigned to a pool.",
            "already_pooled",
        )

    if (
        produce["crop_name"].lower()
        !=
        pool["crop_name"].lower()
    ):

        raise PoolError(
            "Crop does not match the pool crop.",
            "crop_mismatch",
        )

    if (
        produce["location"].lower()
        !=
        pool["location"].lower()
    ):

        raise PoolError(
            "Produce location does not match pool location.",
            "location_mismatch",
        )

    connection = get_connection(db_path)

    try:

        connection.execute(
            """
            UPDATE Produce
            SET
                pool_id = ?,
                status = 'pooled'
            WHERE produce_id = ?
            """,
            (
                pool_id,
                produce_id,
            ),
        )

        connection.execute(
            """
            UPDATE Pool
            SET total_quantity_kg =
                total_quantity_kg + ?
            WHERE pool_id = ?
            """,
            (
                produce["quantity_kg"],
                pool_id,
            ),
        )

        connection.commit()

        row = connection.execute(
            """
            SELECT *
            FROM Pool
            WHERE pool_id = ?
            """,
            (pool_id,),
        ).fetchone()

        updated_pool = dict(row)

    finally:

        connection.close()

    add_journey_log(
        "produce",
        produce_id,
        "pooled",
        db_path,
    )

    return updated_pool


def get_pool_details(
    pool_id,
    db_path=None,
):

    pool = get_pool(
        pool_id,
        db_path,
    )

    if pool is None:

        return None

    connection = get_connection(db_path)

    try:

        rows = connection.execute(
            """
            SELECT
                Produce.*,
                Farmer.name,
                Farmer.phone
            FROM Produce

            JOIN Farmer
            ON Produce.farmer_id = Farmer.farmer_id

            WHERE Produce.pool_id = ?

            ORDER BY Produce.produce_id
            """,
            (pool_id,),
        ).fetchall()

        produce_list = []

        for row in rows:

            item = {
                "produce_id": row["produce_id"],
                "crop_name": row["crop_name"],
                "quantity_kg": row["quantity_kg"],
                "location": row["location"],
                "status": row["status"],

                "farmer": {
                    "farmer_id": row["farmer_id"],
                    "name": row["name"],
                    "phone": row["phone"],
                },
            }

            produce_list.append(item)

        return {
            "pool": pool,
            "produce": produce_list,
        }

    finally:

        connection.close()


# =========================================================
# BUYER
# =========================================================


def create_buyer(
    buyer_name,
    crop_name,
    required_quantity_kg,
    location,
    urgency="normal",
    db_path=None,
):

    try:

        buyer_name = clean_text(
            buyer_name,
            "buyer_name",
        )

        crop_name = clean_text(
            crop_name,
            "crop_name",
        )

        required_quantity_kg = clean_quantity(
            required_quantity_kg,
            "required_quantity_kg",
        )

        location = clean_text(
            location,
            "location",
        )

        urgency = str(
            urgency
        ).lower().strip()

        if urgency not in (
            "low",
            "normal",
            "high",
        ):

            raise ValueError(
                "urgency must be low, normal, or high."
            )

    except ValueError as exc:

        raise BuyerError(str(exc))

    connection = get_connection(db_path)

    try:

        cursor = connection.execute(
            """
            INSERT INTO Buyer
            (
                buyer_name,
                crop_name,
                required_quantity_kg,
                location,
                urgency
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                buyer_name,
                crop_name,
                required_quantity_kg,
                location,
                urgency,
            ),
        )

        connection.commit()

        buyer_id = cursor.lastrowid

        row = connection.execute(
            """
            SELECT *
            FROM Buyer
            WHERE buyer_id = ?
            """,
            (buyer_id,),
        ).fetchone()

        return dict(row)

    finally:

        connection.close()


def list_buyers(db_path=None):

    connection = get_connection(db_path)

    try:

        rows = connection.execute(
            """
            SELECT *
            FROM Buyer
            ORDER BY buyer_id
            """
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        connection.close()


def get_buyer(
    buyer_id,
    db_path=None,
):

    connection = get_connection(db_path)

    try:

        row = connection.execute(
            """
            SELECT *
            FROM Buyer
            WHERE buyer_id = ?
            """,
            (buyer_id,),
        ).fetchone()

        return (
            dict(row)
            if row
            else None
        )

    finally:

        connection.close()


# =========================================================
# SMART BUYER MATCHING
# =========================================================


def get_match_suggestions(db_path=None):

    connection = get_connection(db_path)

    try:

        rows = connection.execute(
            """
            SELECT

                Pool.pool_id,
                Pool.crop_name AS pool_crop,
                Pool.total_quantity_kg,
                Pool.location AS pool_location,

                Buyer.buyer_id,
                Buyer.buyer_name,
                Buyer.crop_name AS buyer_crop,
                Buyer.required_quantity_kg,
                Buyer.location AS buyer_location,
                Buyer.urgency

            FROM Pool

            JOIN Buyer

            ON LOWER(Pool.crop_name)
            =
            LOWER(Buyer.crop_name)

            WHERE Pool.pool_status = 'open'

            AND Pool.total_quantity_kg
            >=
            Buyer.required_quantity_kg

            ORDER BY

                CASE Buyer.urgency
                    WHEN 'high' THEN 1
                    WHEN 'normal' THEN 2
                    WHEN 'low' THEN 3
                END

            """
        ).fetchall()

        suggestions = []

        for row in rows:

            quantity_difference = (
                row["total_quantity_kg"]
                -
                row["required_quantity_kg"]
            )

            score = 100

            # Same location gives higher score
            if (
                row["pool_location"].lower()
                ==
                row["buyer_location"].lower()
            ):
                score += 20

            # Less excess quantity means closer match
            if quantity_difference == 0:
                score += 20

            suggestions.append({

                "match_score": score,

                "pool": {
                    "pool_id": row["pool_id"],
                    "crop_name": row["pool_crop"],
                    "total_quantity_kg":
                        row["total_quantity_kg"],
                    "location":
                        row["pool_location"],
                },

                "buyer": {
                    "buyer_id": row["buyer_id"],
                    "buyer_name": row["buyer_name"],
                    "required_quantity_kg":
                        row["required_quantity_kg"],
                    "location":
                        row["buyer_location"],
                    "urgency":
                        row["urgency"],
                },

                "quantity_difference_kg":
                    quantity_difference,
            })

        suggestions.sort(
            key=lambda x: x["match_score"],
            reverse=True,
        )

        return suggestions

    finally:

        connection.close()


def create_match(
    pool_id,
    buyer_id,
    price_per_kg=None,
    db_path=None,
):

    pool = get_pool(
        pool_id,
        db_path,
    )

    if pool is None:

        raise MatchError(
            "Pool not found.",
            "pool_not_found",
        )

    buyer = get_buyer(
        buyer_id,
        db_path,
    )

    if buyer is None:

        raise MatchError(
            "Buyer not found.",
            "buyer_not_found",
        )

    if (
        pool["crop_name"].lower()
        !=
        buyer["crop_name"].lower()
    ):

        raise MatchError(
            "Pool crop and buyer crop do not match.",
            "crop_mismatch",
        )

    if (
        pool["total_quantity_kg"]
        <
        buyer["required_quantity_kg"]
    ):

        raise MatchError(
            "Pool quantity is insufficient for this buyer.",
            "insufficient_quantity",
        )

    matched_quantity = (
        buyer["required_quantity_kg"]
    )

    if price_per_kg is not None:

        try:

            price_per_kg = float(
                price_per_kg
            )

            if price_per_kg <= 0:
                raise ValueError

        except (TypeError, ValueError):

            raise MatchError(
                "price_per_kg must be a positive number."
            )

    connection = get_connection(db_path)

    try:

        cursor = connection.execute(
            """
            INSERT INTO Match
            (
                pool_id,
                buyer_id,
                matched_quantity_kg,
                price_per_kg,
                match_status
            )
            VALUES (?, ?, ?, ?, 'matched')
            """,
            (
                pool_id,
                buyer_id,
                matched_quantity,
                price_per_kg,
            ),
        )

        connection.execute(
            """
            UPDATE Pool
            SET pool_status = 'matched'
            WHERE pool_id = ?
            """,
            (pool_id,),
        )

        connection.commit()

        match_id = cursor.lastrowid

        row = connection.execute(
            """
            SELECT *
            FROM Match
            WHERE match_id = ?
            """,
            (match_id,),
        ).fetchone()

        match = dict(row)

    finally:

        connection.close()

    add_journey_log(
        "pool",
        pool_id,
        "matched",
        db_path,
    )

    add_journey_log(
        "match",
        match_id,
        "matched",
        db_path,
    )

    return match


def list_matches(db_path=None):

    connection = get_connection(db_path)

    try:

        rows = connection.execute(
            """
            SELECT *
            FROM Match
            ORDER BY match_id
            """
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        connection.close()


def get_match(
    match_id,
    db_path=None,
):

    connection = get_connection(db_path)

    try:

        row = connection.execute(
            """
            SELECT *
            FROM Match
            WHERE match_id = ?
            """,
            (match_id,),
        ).fetchone()

        return (
            dict(row)
            if row
            else None
        )

    finally:

        connection.close()


def update_match_status(
    match_id,
    new_status,
    db_path=None,
):

    allowed_statuses = (
        "confirmed",
        "rejected",
        "completed",
    )

    if new_status not in allowed_statuses:

        raise MatchError(
            "Invalid match status."
        )

    match = get_match(
        match_id,
        db_path,
    )

    if match is None:

        raise MatchError(
            "Match not found.",
            "match_not_found",
        )

    connection = get_connection(db_path)

    try:

        connection.execute(
            """
            UPDATE Match
            SET match_status = ?
            WHERE match_id = ?
            """,
            (
                new_status,
                match_id,
            ),
        )

        if new_status == "completed":

            connection.execute(
                """
                UPDATE Pool
                SET pool_status = 'completed'
                WHERE pool_id = ?
                """,
                (match["pool_id"],),
            )

            connection.execute(
                """
                UPDATE Produce
                SET status = 'sold'
                WHERE pool_id = ?
                """,
                (match["pool_id"],),
            )

        connection.commit()

        row = connection.execute(
            """
            SELECT *
            FROM Match
            WHERE match_id = ?
            """,
            (match_id,),
        ).fetchone()

        updated_match = dict(row)

    finally:

        connection.close()

    add_journey_log(
        "match",
        match_id,
        new_status,
        db_path,
    )

    if new_status == "completed":

        add_journey_log(
            "pool",
            match["pool_id"],
            "completed",
            db_path,
        )

    return updated_match
"""
AgriLink AI — database helpers.

Stage 2: Farmer only. Other tables will be added in later stages.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from database import get_connection


class FarmerError(Exception):
    """Invalid farmer data or a duplicate phone number."""

    def __init__(self, message: str, code: str = "invalid") -> None:
        super().__init__(message)
        self.code = code


def _row_to_farmer(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "farmer_id": row["farmer_id"],
        "name": row["name"],
        "phone": row["phone"],
        "location": row["location"],
        "created_at": row["created_at"],
    }


def _clean_text(value: Any, field_name: str) -> str:
    if value is None:
        raise FarmerError(f"{field_name} is required.")
    text = str(value).strip()
    if not text:
        raise FarmerError(f"{field_name} is required.")
    return text


def create_farmer(
    name: Any,
    phone: Any,
    location: Any,
    db_path=None,
) -> dict[str, Any]:
    """Insert one farmer. Phone must be unique (see schema.sql)."""
    clean_name = _clean_text(name, "name")
    clean_phone = _clean_text(phone, "phone")
    clean_location = _clean_text(location, "location")

    connection = get_connection(db_path)
    try:
        cursor = connection.execute(
            """
            INSERT INTO Farmer (name, phone, location)
            VALUES (?, ?, ?)
            """,
            (clean_name, clean_phone, clean_location),
        )
        connection.commit()
        farmer_id = cursor.lastrowid
        row = connection.execute(
            "SELECT * FROM Farmer WHERE farmer_id = ?",
            (farmer_id,),
        ).fetchone()
        return _row_to_farmer(row)
    except sqlite3.IntegrityError as exc:
        raise FarmerError(
            "A farmer with this phone number is already registered.",
            code="duplicate_phone",
        ) from exc
    finally:
        connection.close()


def list_farmers(db_path=None) -> list[dict[str, Any]]:
    connection = get_connection(db_path)
    try:
        rows = connection.execute(
            "SELECT * FROM Farmer ORDER BY farmer_id"
        ).fetchall()
        return [_row_to_farmer(row) for row in rows]
    finally:
        connection.close()


def get_farmer(farmer_id: int, db_path=None) -> dict[str, Any] | None:
    connection = get_connection(db_path)
    try:
        row = connection.execute(
            "SELECT * FROM Farmer WHERE farmer_id = ?",
            (farmer_id,),
        ).fetchone()
        if row is None:
            return None
        return _row_to_farmer(row)
    finally:
        connection.close()

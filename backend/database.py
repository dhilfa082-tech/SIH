"""
AgriLink AI - Database Configuration
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent

DEFAULT_DB_PATH = PROJECT_DIR / "agrilink.db"

SCHEMA_PATH = PROJECT_DIR / "docs" / "schema.sql"


def get_connection(db_path=None):

    path = Path(db_path) if db_path else DEFAULT_DB_PATH

    connection = sqlite3.connect(path)

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database(db_path=None):

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"Schema file not found: {SCHEMA_PATH}"
        )

    connection = get_connection(db_path)

    try:

        schema = SCHEMA_PATH.read_text(
            encoding="utf-8"
        )

        connection.executescript(schema)

        connection.commit()

    finally:

        connection.close()
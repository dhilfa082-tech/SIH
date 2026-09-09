"""
AgriLink AI — SQLite connection and schema initialization.

Windows-safe paths: files are located from this module, not from the current
working directory.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
SCHEMA_PATH = PROJECT_ROOT / "docs" / "schema.sql"
DATABASE_PATH = PROJECT_ROOT / "agrilink.db"

REQUIRED_TABLES = (
    "Farmer",
    "Produce",
    "Pool",
    "Buyer",
    "Match",
    "JourneyLog",
)


class DatabaseError(Exception):
    """Raised when the database cannot be opened or initialized."""


def get_schema_path() -> Path:
    """Return the path to docs/schema.sql and fail clearly if it is missing."""
    if not SCHEMA_PATH.is_file():
        raise DatabaseError(
            f"Schema file not found: {SCHEMA_PATH}\n"
            "Expected docs/schema.sql next to the backend folder."
        )
    return SCHEMA_PATH


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Open SQLite with row access by column name and foreign keys enabled."""
    path = Path(db_path) if db_path is not None else DATABASE_PATH
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(str(path))
    except sqlite3.Error as exc:
        raise DatabaseError(f"Could not connect to database {path}: {exc}") from exc

    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _read_schema_sql() -> str:
    schema_file = get_schema_path()
    try:
        return schema_file.read_text(encoding="utf-8")
    except OSError as exc:
        raise DatabaseError(f"Could not read schema file {schema_file}: {exc}") from exc


def list_tables(connection: sqlite3.Connection) -> list[str]:
    rows = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    ).fetchall()
    return [row["name"] for row in rows]


def verify_tables(connection: sqlite3.Connection) -> None:
    existing = set(list_tables(connection))
    missing = [name for name in REQUIRED_TABLES if name not in existing]
    if missing:
        raise DatabaseError(
            "Database is missing required tables: "
            + ", ".join(missing)
            + f"\nFound: {', '.join(sorted(existing)) or '(none)'}"
        )


def initialize_database(db_path: Path | None = None) -> Path:
    """
    Create all tables and indexes from docs/schema.sql.

    Safe to run more than once (schema uses IF NOT EXISTS).
    """
    target = Path(db_path) if db_path is not None else DATABASE_PATH
    sql = _read_schema_sql()
    connection = None
    try:
        connection = get_connection(target)
        connection.executescript(sql)
        connection.commit()
        verify_tables(connection)
    except sqlite3.Error as exc:
        raise DatabaseError(f"Failed to initialize database {target}: {exc}") from exc
    finally:
        if connection is not None:
            connection.close()

    return target


def _run_self_test() -> int:
    print("AgriLink AI - Stage 1 database test")
    print(f"Project root : {PROJECT_ROOT}")
    print(f"Schema file  : {SCHEMA_PATH}")
    print(f"Database file: {DATABASE_PATH}")
    print()

    try:
        db_file = initialize_database()
        connection = get_connection(db_file)
        try:
            tables = list_tables(connection)
            print("Initialization succeeded.")
            print(f"Database: {db_file}")
            print("Tables:")
            for name in tables:
                print(f"  - {name}")
        finally:
            connection.close()
    except DatabaseError as exc:
        print("ERROR:", exc, file=sys.stderr)
        return 1

    print()
    print("Stage 1 test passed.")
    return 0


if __name__ == "__main__":
    sys.exit(_run_self_test())

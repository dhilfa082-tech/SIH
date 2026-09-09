import sqlite3

DATABASE = "agrilink.db"


def get_connection():
    """Create and return a database connection."""
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create all required tables."""

    connection = get_connection()
    cursor = connection.cursor()

    # Farmers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS farmers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            location TEXT
        )
    """)

    # Produce table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produce (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farmer_id INTEGER,
            crop_name TEXT NOT NULL,
            quantity REAL NOT NULL,
            location TEXT,
            availability_date TEXT,
            status TEXT DEFAULT 'Registered',
            FOREIGN KEY (farmer_id) REFERENCES farmers(id)
        )
    """)

    # Buyers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS buyers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            crop_name TEXT NOT NULL,
            required_quantity REAL NOT NULL,
            location TEXT,
            urgency TEXT
        )
    """)

    connection.commit()
    connection.close()

    print("Database initialized successfully!")

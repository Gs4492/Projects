from db.database import get_connection


def _add_column_if_missing(cursor, table_name: str, column_name: str, sql_type: str):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = {row["name"] for row in cursor.fetchall()}
    if column_name not in columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {sql_type}")


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        opponent TEXT,
        match_date TEXT,
        format TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS deliveries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        player_id INTEGER,
        over INTEGER,
        ball INTEGER,
        bowler_type TEXT,
        line TEXT,
        length TEXT,
        shot TEXT,
        outcome TEXT,
        dismissal TEXT,
        pitch_x REAL,
        pitch_y REAL,
        release_x REAL,
        release_y REAL,
        speed_kph REAL,
        FOREIGN KEY(match_id) REFERENCES matches(id)
    )
    """)

    # Lightweight migrations for existing local DBs created with older schema.
    _add_column_if_missing(cursor, "deliveries", "dismissal", "TEXT")
    _add_column_if_missing(cursor, "deliveries", "pitch_x", "REAL")
    _add_column_if_missing(cursor, "deliveries", "pitch_y", "REAL")
    _add_column_if_missing(cursor, "deliveries", "release_x", "REAL")
    _add_column_if_missing(cursor, "deliveries", "release_y", "REAL")
    _add_column_if_missing(cursor, "deliveries", "speed_kph", "REAL")

    # Idempotency guard: one player can only have one record per ball in a match.
    cursor.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_delivery_ball
        ON deliveries (match_id, player_id, over, ball)
        """
    )

    conn.commit()
    conn.close()

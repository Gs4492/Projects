from db.database import get_connection


def _normalize_batting_hand(value: str) -> str:
    value = value.strip().lower()
    if value in {"right", "r"}:
        return "R"
    if value in {"left", "l"}:
        return "L"
    raise ValueError("batting_hand must be one of: right, left, R, L")


def create_player(player):
    conn = get_connection()
    cursor = conn.cursor()

    normalized_hand = _normalize_batting_hand(player.batting_hand)

    cursor.execute(
        """
        INSERT INTO players (name, batting_hand, level)
        VALUES (?, ?, ?)
        """,
        (player.name, normalized_hand, player.level)
    )

    conn.commit()
    player_id = cursor.lastrowid
    conn.close()

    return player_id


def get_player(player_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM players WHERE id = ?",
        (player_id,)
    )

    row = cursor.fetchone()
    conn.close()

    return row

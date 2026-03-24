from db.database import get_connection


def create_match(match):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO matches (opponent, match_date, format) VALUES (?, ?, ?)",
        (match.opponent, match.match_date, match.format)
    )

    conn.commit()
    match_id = cursor.lastrowid
    conn.close()

    return match_id


def _match_exists(cursor, match_id: int) -> bool:
    cursor.execute("SELECT 1 FROM matches WHERE id = ?", (match_id,))
    return cursor.fetchone() is not None


def add_deliveries(match_id, deliveries):
    conn = get_connection()
    cursor = conn.cursor()

    if not _match_exists(cursor, match_id):
        conn.close()
        raise ValueError(f"match_id {match_id} does not exist")

    inserted = 0
    ignored = 0

    for d in deliveries:
        cursor.execute(
            """
            INSERT OR IGNORE INTO deliveries (
                match_id, player_id, over, ball,
                bowler_type, line, length,
                shot, outcome, dismissal,
                pitch_x, pitch_y, release_x, release_y, speed_kph
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                match_id,
                d.player_id,
                d.over,
                d.ball,
                d.bowler_type,
                d.line,
                d.length,
                d.shot,
                d.outcome,
                d.dismissal,
                d.pitch_x,
                d.pitch_y,
                d.release_x,
                d.release_y,
                d.speed_kph,
            )
        )

        if cursor.rowcount == 1:
            inserted += 1
        else:
            ignored += 1

    conn.commit()
    conn.close()
    return {"inserted": inserted, "ignored": ignored}


def get_last_matches_deliveries(player_id: int, last_matches: int = 5):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT d.match_id
        FROM deliveries d
        JOIN matches m ON m.id = d.match_id
        WHERE d.player_id = ?
        GROUP BY d.match_id
        ORDER BY date(m.match_date) DESC, d.match_id DESC
        LIMIT ?
        """,
        (player_id, last_matches),
    )
    match_ids = [row["match_id"] for row in cursor.fetchall()]

    if not match_ids:
        conn.close()
        return []

    placeholders = ",".join(["?"] * len(match_ids))
    query = f"""
        SELECT id, match_id, player_id, over, ball, bowler_type, line, length, shot, outcome, dismissal,
               pitch_x, pitch_y, release_x, release_y, speed_kph
        FROM deliveries
        WHERE player_id = ?
          AND match_id IN ({placeholders})
        ORDER BY match_id DESC, over ASC, ball ASC
    """

    cursor.execute(query, (player_id, *match_ids))
    rows = cursor.fetchall()
    conn.close()
    return rows

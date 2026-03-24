import os
from typing import Any

import requests


MATCH_SERVICE_URL = os.getenv("MATCH_SERVICE_URL", "http://127.0.0.1:8002")


def fetch_deliveries(player_id: int, last_matches: int = 5) -> list[dict[str, Any]]:
    response = requests.get(
        f"{MATCH_SERVICE_URL}/players/{player_id}/deliveries",
        params={"last_matches": last_matches},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()

import os

import requests


ANALYTICS_URL = os.getenv("ANALYTICS_URL", "http://127.0.0.1:8003")


def fetch_batting_analytics(player_id: int, last_matches: int = 5):
    response = requests.get(
        f"{ANALYTICS_URL}/analytics/batting/{player_id}",
        params={"last_matches": last_matches},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def fetch_bowling_analytics(player_id: int, last_matches: int = 5):
    response = requests.get(
        f"{ANALYTICS_URL}/analytics/bowling/{player_id}",
        params={"last_matches": last_matches},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()

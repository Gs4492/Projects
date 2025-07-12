import random

def score_lead(lead_data):
    source_score = {
        "Website": 60,
        "Referral": 80,
        "Event": 50,
        "Other": 40
    }

    base_score = source_score.get(lead_data.get("source", "Other"), 50)
    randomness = random.randint(-10, 10)
    final_score = min(100, max(0, base_score + randomness))

    return {"score": final_score}

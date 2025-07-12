from repository.lead_repo import save_lead, fetch_leads
from ML.lead_scorer import score_lead

def create_lead(data):
    scored = score_lead(data)
    data["score"] = scored["score"]
    return save_lead(data)

def get_all_leads():
    return fetch_leads()

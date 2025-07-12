from flask import Blueprint, request, jsonify
from services.lead_service import create_lead, get_all_leads

lead_bp = Blueprint('lead_bp', __name__)

@lead_bp.route('/leads/submit', methods=['POST'])
def submit_lead():
    data = request.get_json()
    new_lead = create_lead(data)
    return jsonify({"message": "Lead submitted", "lead": new_lead}), 201

@lead_bp.route('/leads', methods=['GET'])
def list_leads():
    return jsonify(get_all_leads())

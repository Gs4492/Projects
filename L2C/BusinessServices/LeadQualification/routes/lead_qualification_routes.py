from flask import Blueprint, request, jsonify
from repository.lead_repository import save_qualified_lead, fetch_qualified_leads

lead_qualification_bp = Blueprint('lead_qualification', __name__)

@lead_qualification_bp.route('/qualified-leads', methods=['GET'])
def get_qualified_leads():
    leads = fetch_qualified_leads()
    return jsonify(leads)

@lead_qualification_bp.route('/qualified-leads', methods=['POST'])
def post_qualified_lead():
    data = request.json
    result = save_qualified_lead(data)
    return jsonify(result), 201

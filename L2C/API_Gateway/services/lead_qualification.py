import requests
from flask import Blueprint, request, jsonify

lead_qualification_api_bp = Blueprint('lead_qualification_api', __name__)

BASE_URL = 'http://localhost:5011/qualified-leads'

@lead_qualification_api_bp.route('/api/qualified-leads', methods=['GET'])
def proxy_get_leads():
    try:
        resp = requests.get(BASE_URL)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@lead_qualification_api_bp.route('/api/qualified-leads', methods=['POST'])
def proxy_post_lead():
    try:
        resp = requests.post(BASE_URL, json=request.json)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

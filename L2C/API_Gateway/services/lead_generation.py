from flask import Blueprint, request, jsonify
import requests

lead_generation_blueprint = Blueprint('lead_generation', __name__)

BASE_URL = 'http://localhost:5010'  # Points to the LeadGeneration microservice

@lead_generation_blueprint.route('/leadgeneration', methods=['GET'])
def get_leads():
    try:
        response = requests.get(f'{BASE_URL}/leads')
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Failed to fetch leads', 'details': str(e)}), 500

@lead_generation_blueprint.route('/leadgeneration', methods=['POST'])
def submit_lead():
    try:
        data = request.get_json()
        response = requests.post(f'{BASE_URL}/leads/submit', json=data)
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Failed to submit lead', 'details': str(e)}), 500

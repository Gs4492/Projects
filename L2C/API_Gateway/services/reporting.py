# API_Gateway/services/reporting.py

from flask import Blueprint, request, jsonify
import requests

report_blueprint = Blueprint('reporting', __name__)
BASE_URL = 'http://localhost:5007'  # Reporting microservice URL

@report_blueprint.route('/reports', methods=['GET'])
def get_reports():
    response = requests.get(f'{BASE_URL}/reports')
    return jsonify(response.json()), response.status_code

@report_blueprint.route('/reports', methods=['POST'])
def add_report():
    data = request.get_json()
    response = requests.post(f'{BASE_URL}/reports', json=data)
    return jsonify(response.json()), response.status_code

@report_blueprint.route('/reports/<int:report_id>', methods=['PUT'])
def update_report(report_id):
    data = request.get_json()
    response = requests.put(f'{BASE_URL}/reports/{report_id}', json=data)
    return jsonify(response.json()), response.status_code

@report_blueprint.route('/reports/<int:report_id>', methods=['DELETE'])
def delete_report(report_id):
    response = requests.delete(f'{BASE_URL}/reports/{report_id}')
    return jsonify(response.json()), response.status_code

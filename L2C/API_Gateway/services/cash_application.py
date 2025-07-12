from flask import Blueprint, jsonify, request
import requests

cash_app_blueprint = Blueprint('cash_application', __name__)

BASE_URL = 'http://localhost:5008'  # microservice URL

@cash_app_blueprint.route('/cash_applications', methods=['GET'])
def get_cash_applications():
    response = requests.get(f'{BASE_URL}/cash_applications')
    return jsonify(response.json()), response.status_code

@cash_app_blueprint.route('/cash_applications', methods=['POST'])
def add_cash_application():
    data = request.get_json()
    response = requests.post(f'{BASE_URL}/cash_applications', json=data)
    return jsonify(response.json()), response.status_code

@cash_app_blueprint.route('/cash_applications/<int:id>', methods=['DELETE'])
def delete_cash_application(id):
    response = requests.delete(f'{BASE_URL}/cash_applications/{id}')
    return jsonify(response.json()), response.status_code

@cash_app_blueprint.route('/cash_applications/<int:id>', methods=['PUT'])
def update_cash_application(id):
    data = request.get_json()
    response = requests.put(f'{BASE_URL}/cash_applications/{id}', json=data)
    return jsonify(response.json()), response.status_code

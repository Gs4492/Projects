# API_Gateway/services/credit_management.py

from flask import Blueprint, request, jsonify
import requests

credit_mgmt_blueprint = Blueprint('credit_management', __name__)

BASE_URL = 'http://localhost:5002'  # Points to the credit_management microservice

@credit_mgmt_blueprint.route('/credits', methods=['GET'])
def get_credits():
    response = requests.get(f'{BASE_URL}/credits')
    return jsonify(response.json()), response.status_code

@credit_mgmt_blueprint.route('/credits', methods=['POST'])
def add_credit():
    data = request.get_json()
    response = requests.post(f'{BASE_URL}/credits', json=data)
    return jsonify(response.json()), response.status_code

@credit_mgmt_blueprint.route('/credits/<int:credit_id>', methods=['PUT'])
def update_credit(credit_id):
    data = request.get_json()
    response = requests.put(f'{BASE_URL}/credits/{credit_id}', json=data)
    return jsonify(response.json()), response.status_code

@credit_mgmt_blueprint.route('/credits/<int:credit_id>', methods=['DELETE'])
def delete_credit(credit_id):
    response = requests.delete(f'{BASE_URL}/credits/{credit_id}')
    return jsonify(response.json()), response.status_code

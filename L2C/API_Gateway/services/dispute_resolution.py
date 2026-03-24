# API_Gateway/services/dispute_resolution.py

from flask import Blueprint, request, jsonify
import requests

dispute_blueprint = Blueprint('dispute_resolution', __name__)
BASE_URL = 'http://localhost:5006'  # Microservice for dispute_resolution

@dispute_blueprint.route('/disputes', methods=['GET'])
def get_disputes():
    response = requests.get(f'{BASE_URL}/disputes')
    return jsonify(response.json()), response.status_code

@dispute_blueprint.route('/disputes', methods=['POST'])
def add_dispute():
    data = request.get_json()
    response = requests.post(f'{BASE_URL}/disputes', json=data)
    return jsonify(response.json()), response.status_code

@dispute_blueprint.route('/disputes/<int:id>', methods=['PUT'])
def update_dispute(id):
    data = request.get_json()
    response = requests.put(f'{BASE_URL}/disputes/{id}', json=data)
    return jsonify(response.json()), response.status_code

@dispute_blueprint.route('/disputes/<int:id>', methods=['DELETE'])
def delete_dispute(id):
    response = requests.delete(f'{BASE_URL}/disputes/{id}')
    return jsonify(response.json()), response.status_code

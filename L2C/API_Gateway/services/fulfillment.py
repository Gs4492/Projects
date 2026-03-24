# API_Gateway/services/fulfillment.py

from flask import Blueprint, request, jsonify
import requests

fulfillment_blueprint = Blueprint('fulfillment', __name__)
BASE_URL = 'http://localhost:5004'  # Fulfillment microservice

@fulfillment_blueprint.route('/fulfillment', methods=['GET'])
def get_fulfillments():
    response = requests.get(f'{BASE_URL}/fulfillment')
    return jsonify(response.json()), response.status_code

@fulfillment_blueprint.route('/fulfillment', methods=['POST'])
def add_fulfillment():
    data = request.get_json()
    response = requests.post(f'{BASE_URL}/fulfillment', json=data)
    return jsonify(response.json()), response.status_code

@fulfillment_blueprint.route('/fulfillment/<int:id>', methods=['PUT'])
def update_fulfillment(id):
    data = request.get_json()
    response = requests.put(f'{BASE_URL}/fulfillment/{id}', json=data)
    return jsonify(response.json()), response.status_code

@fulfillment_blueprint.route('/fulfillment/<int:id>', methods=['DELETE'])
def delete_fulfillment(id):
    response = requests.delete(f'{BASE_URL}/fulfillment/{id}')
    return jsonify(response.json()), response.status_code

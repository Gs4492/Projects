# API_Gateway/services/payment_collection.py

from flask import Blueprint, request, jsonify
import requests

payment_blueprint = Blueprint('payment_collection', __name__)
BASE_URL = 'http://localhost:5003'  # Payment Collection microservice URL

@payment_blueprint.route('/payments', methods=['GET'])
def get_payments():
    response = requests.get(f'{BASE_URL}/payments')
    return jsonify(response.json()), response.status_code

@payment_blueprint.route('/payments', methods=['POST'])
def add_payment():
    data = request.get_json()
    response = requests.post(f'{BASE_URL}/payments', json=data)
    return jsonify(response.json()), response.status_code

@payment_blueprint.route('/payments/<int:payment_id>', methods=['PUT'])
def update_payment(payment_id):
    data = request.get_json()
    response = requests.put(f'{BASE_URL}/payments/{payment_id}', json=data)
    return jsonify(response.json()), response.status_code

@payment_blueprint.route('/payments/<int:payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    response = requests.delete(f'{BASE_URL}/payments/{payment_id}')
    return jsonify(response.json()), response.status_code

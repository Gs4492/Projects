# API_Gateway/services/order_management.py

from flask import Blueprint, request, jsonify
import requests

order_blueprint = Blueprint('order_management', __name__)
BASE_URL = 'http://localhost:5001'  # Order Management microservice

@order_blueprint.route('/orders', methods=['GET'])
def get_orders():
    response = requests.get(f'{BASE_URL}/orders')
    return jsonify(response.json()), response.status_code

@order_blueprint.route('/orders', methods=['POST'])
def add_order():
    data = request.get_json()
    response = requests.post(f'{BASE_URL}/orders', json=data)
    return jsonify(response.json()), response.status_code

@order_blueprint.route('/orders/<int:id>', methods=['PUT'])
def update_order(id):
    data = request.get_json()
    response = requests.put(f'{BASE_URL}/orders/{id}', json=data)
    return jsonify(response.json()), response.status_code

@order_blueprint.route('/orders/<int:id>', methods=['DELETE'])
def delete_order(id):
    response = requests.delete(f'{BASE_URL}/orders/{id}')
    return jsonify(response.json()), response.status_code

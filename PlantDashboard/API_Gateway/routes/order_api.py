import requests
from flask import Blueprint, request, jsonify

order_api = Blueprint('order_api', __name__)
ORDER_SERVICE_URL = 'http://localhost:5002'

@order_api.route('/orders', methods=['GET', 'POST'])
def handle_orders():
    if request.method == 'GET':
        res = requests.get(f'{ORDER_SERVICE_URL}/orders')
        return jsonify(res.json()), res.status_code
    if request.method == 'POST':
        res = requests.post(f'{ORDER_SERVICE_URL}/orders', json=request.json)
        return jsonify(res.json()), res.status_code

@order_api.route('/orders/<int:order_id>', methods=['PUT', 'DELETE'])
def modify_order(order_id):
    if request.method == 'PUT':
        res = requests.put(f'{ORDER_SERVICE_URL}/orders/{order_id}', json=request.json)
        return jsonify(res.json()), res.status_code
    if request.method == 'DELETE':
        res = requests.delete(f'{ORDER_SERVICE_URL}/orders/{order_id}')
        return jsonify(res.json()), res.status_code

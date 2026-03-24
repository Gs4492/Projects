import requests
from flask import Blueprint, request, jsonify

customer_api = Blueprint('customer_api', __name__)
CUSTOMER_SERVICE_URL = 'http://localhost:5003'

@customer_api.route('/customers', methods=['GET', 'POST'])
def handle_customers():
    if request.method == 'GET':
        res = requests.get(f'{CUSTOMER_SERVICE_URL}/customers')
        return jsonify(res.json()), res.status_code
    if request.method == 'POST':
        res = requests.post(f'{CUSTOMER_SERVICE_URL}/customers', json=request.json)
        return jsonify(res.json()), res.status_code

@customer_api.route('/customers/<int:customer_id>', methods=['PUT', 'DELETE'])
def modify_customer(customer_id):
    if request.method == 'PUT':
        res = requests.put(f'{CUSTOMER_SERVICE_URL}/customers/{customer_id}', json=request.json)
        return jsonify(res.json()), res.status_code
    if request.method == 'DELETE':
        res = requests.delete(f'{CUSTOMER_SERVICE_URL}/customers/{customer_id}')
        return jsonify(res.json()), res.status_code

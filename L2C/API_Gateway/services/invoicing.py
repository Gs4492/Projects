# API_Gateway/services/invoicing.py

from flask import Blueprint, request, jsonify
import requests

invoicing_blueprint = Blueprint('invoicing', __name__)
BASE_URL = 'http://localhost:5005'  # Invoice microservice base URL

@invoicing_blueprint.route('/invoices', methods=['GET'])
def get_invoices():
    response = requests.get(f'{BASE_URL}/invoices')
    return jsonify(response.json()), response.status_code

@invoicing_blueprint.route('/invoices/count', methods=['GET'])
def get_invoice_count():
    response = requests.get(f'{BASE_URL}/invoices/count')
    return jsonify(response.json()), response.status_code

@invoicing_blueprint.route('/invoices', methods=['POST'])
def add_invoice():
    data = request.get_json()
    response = requests.post(f'{BASE_URL}/invoices', json=data)
    return jsonify(response.json()), response.status_code

@invoicing_blueprint.route('/invoices/<int:id>', methods=['PUT'])
def update_invoice(id):
    data = request.get_json()
    response = requests.put(f'{BASE_URL}/invoices/{id}', json=data)
    return jsonify(response.json()), response.status_code

@invoicing_blueprint.route('/invoices/<int:id>', methods=['DELETE'])
def delete_invoice(id):
    response = requests.delete(f'{BASE_URL}/invoices/{id}')
    return jsonify(response.json()), response.status_code

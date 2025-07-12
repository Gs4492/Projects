# routes/billing_api.py

from flask import Blueprint, request, jsonify
import requests

BILLING_SERVICE_URL = 'http://localhost:5004'

billing_bp = Blueprint('billing_api', __name__)

@billing_bp.route('/invoices', methods=['GET'])
def get_invoices():
    res = requests.get(f'{BILLING_SERVICE_URL}/invoices')
    return jsonify(res.json()), res.status_code

@billing_bp.route('/invoices/<int:invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    res = requests.get(f'{BILLING_SERVICE_URL}/invoices/{invoice_id}')
    return jsonify(res.json()), res.status_code

@billing_bp.route('/invoices', methods=['POST'])
def create_invoice():
    data = request.get_json()
    res = requests.post(f'{BILLING_SERVICE_URL}/invoices', json=data)
    return jsonify(res.json()), res.status_code

@billing_bp.route('/invoices/<int:invoice_id>', methods=['PUT'])
def update_invoice(invoice_id):
    data = request.get_json()
    res = requests.put(f'{BILLING_SERVICE_URL}/invoices/{invoice_id}', json=data)
    return jsonify(res.json()), res.status_code

@billing_bp.route('/invoices/<int:invoice_id>', methods=['DELETE'])
def delete_invoice(invoice_id):
    res = requests.delete(f'{BILLING_SERVICE_URL}/invoices/{invoice_id}')
    return jsonify(res.json()), res.status_code

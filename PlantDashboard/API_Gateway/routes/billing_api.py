import requests
from flask import Blueprint, request, jsonify

billing_api = Blueprint('billing_api', __name__)
BILLING_SERVICE_URL = 'http://localhost:5004'

@billing_api.route('/invoices', methods=['GET', 'POST'])
def handle_invoices():
    if request.method == 'GET':
        res = requests.get(f'{BILLING_SERVICE_URL}/invoices')
        return jsonify(res.json()), res.status_code
    if request.method == 'POST':
        res = requests.post(f'{BILLING_SERVICE_URL}/invoices', json=request.json)
        return jsonify(res.json()), res.status_code

@billing_api.route('/invoices/<int:invoice_id>', methods=['PUT', 'DELETE'])
def modify_invoice(invoice_id):
    if request.method == 'PUT':
        res = requests.put(f'{BILLING_SERVICE_URL}/invoices/{invoice_id}', json=request.json)
        return jsonify(res.json()), res.status_code
    if request.method == 'DELETE':
        res = requests.delete(f'{BILLING_SERVICE_URL}/invoices/{invoice_id}')
        return jsonify(res.json()), res.status_code

@billing_api.route('/invoices/revenue', methods=['GET'])
def get_revenue():
    res = requests.get(f'{BILLING_SERVICE_URL}/invoices/revenue')
    return jsonify(res.json()), res.status_code

from flask import Blueprint, request, jsonify
from repository.billing_repository import (
    get_all_invoices, create_invoice, update_invoice_status, get_total_revenue
)

billing_bp = Blueprint('billing_bp', __name__)

@billing_bp.route('/invoices', methods=['GET'])
def fetch_invoices():
    invoices = get_all_invoices()
    return jsonify(invoices), 200

@billing_bp.route('/invoices', methods=['POST'])
def add_invoice():
    data = request.json
    create_invoice(data)
    return jsonify({'message': 'Invoice created'}), 201

@billing_bp.route('/invoices/<int:invoice_id>', methods=['PUT'])
def mark_paid(invoice_id):
    status = request.json.get('payment_status', 'Paid')
    success = update_invoice_status(invoice_id, status)
    if success:
        return jsonify({'message': 'Invoice updated'}), 200
    return jsonify({'error': 'Invoice not found'}), 404

@billing_bp.route('/invoices/revenue', methods=['GET'])
def total_revenue():
    revenue = get_total_revenue()
    return jsonify({'total_revenue': revenue}), 200

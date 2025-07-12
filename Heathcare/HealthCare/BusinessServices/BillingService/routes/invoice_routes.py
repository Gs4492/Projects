# routes/invoice_routes.py

from flask import Blueprint, request, jsonify
from repository import invoice_repository

invoice_bp = Blueprint('invoices', __name__)

@invoice_bp.route('/invoices', methods=['GET'])
def get_all():
    invoices = invoice_repository.get_all_invoices()
    return jsonify([inv.to_dict() for inv in invoices])

@invoice_bp.route('/invoices/<int:invoice_id>', methods=['GET'])
def get_one(invoice_id):
    inv = invoice_repository.get_invoice_by_id(invoice_id)
    if inv:
        return jsonify(inv.to_dict())
    return jsonify({'error': 'Invoice not found'}), 404

@invoice_bp.route('/invoices', methods=['POST'])
def create():
    data = request.get_json()
    required = ['patient_name', 'amount', 'status', 'date']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing fields'}), 400
    inv_id = invoice_repository.create_invoice(data)
    return jsonify({'message': 'Invoice created', 'id': inv_id}), 201

@invoice_bp.route('/invoices/<int:invoice_id>', methods=['PUT'])
def update(invoice_id):
    data = request.get_json()
    success = invoice_repository.update_invoice(invoice_id, data)
    if success:
        return jsonify({'message': 'Invoice updated'})
    return jsonify({'error': 'Invoice not found'}), 404

@invoice_bp.route('/invoices/<int:invoice_id>', methods=['DELETE'])
def delete(invoice_id):
    success = invoice_repository.delete_invoice(invoice_id)
    if success:
        return jsonify({'message': 'Invoice deleted'})
    return jsonify({'error': 'Invoice not found'}), 404

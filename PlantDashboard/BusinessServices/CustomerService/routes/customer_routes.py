from flask import Blueprint, request, jsonify
from repository.customer_repository import get_all_customers, add_customer, update_customer, delete_customer

customer_bp = Blueprint('customer_bp', __name__)

@customer_bp.route('/customers', methods=['GET'])
def fetch_customers():
    customers = get_all_customers()
    return jsonify(customers), 200

@customer_bp.route('/customers', methods=['POST'])
def create_customer():
    data = request.json
    add_customer(data)
    return jsonify({'message': 'Customer added successfully'}), 201

@customer_bp.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer_by_id(customer_id):
    data = request.json
    success = update_customer(customer_id, data)
    if success:
        return jsonify({'message': 'Customer updated'}), 200
    return jsonify({'error': 'Customer not found'}), 404

@customer_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer_by_id(customer_id):
    success = delete_customer(customer_id)
    if success:
        return jsonify({'message': 'Customer deleted'}), 200
    return jsonify({'error': 'Customer not found'}), 404

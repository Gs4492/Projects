from flask import Blueprint, request, jsonify
from repository.order_repository import get_all_orders, add_order, update_order_status, delete_order

order_bp = Blueprint('order_bp', __name__)

@order_bp.route('/orders', methods=['GET'])
def fetch_orders():
    orders = get_all_orders()
    return jsonify(orders), 200

@order_bp.route('/orders', methods=['POST'])
def create_order():
    data = request.json
    add_order(data)
    return jsonify({'message': 'Order placed successfully'}), 201

@order_bp.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    status = request.json.get('status')
    success = update_order_status(order_id, status)
    if success:
        return jsonify({'message': 'Order status updated'}), 200
    return jsonify({'error': 'Order not found'}), 404

@order_bp.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order_by_id(order_id):
    success = delete_order(order_id)
    if success:
        return jsonify({'message': 'Order deleted'}), 200
    return jsonify({'error': 'Order not found'}), 404

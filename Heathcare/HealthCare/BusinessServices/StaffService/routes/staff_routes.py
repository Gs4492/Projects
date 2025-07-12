# routes/staff_routes.py

from flask import Blueprint, request, jsonify
from repository import staff_repository

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/staff', methods=['GET'])
def get_all():
    staff = staff_repository.get_all_staff()
    return jsonify([s.to_dict() for s in staff])

@staff_bp.route('/staff/active', methods=['GET'])
def get_active():
    staff = staff_repository.get_active_staff()
    return jsonify([s.to_dict() for s in staff])

@staff_bp.route('/staff', methods=['POST'])
def create():
    data = request.get_json()
    required = ['name', 'role', 'contact']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing fields'}), 400
    staff_id = staff_repository.create_staff(data)
    return jsonify({'message': 'Staff added', 'id': staff_id}), 201

@staff_bp.route('/staff/<int:staff_id>', methods=['PUT'])
def update(staff_id):
    data = request.get_json()
    if 'active' not in data:
        data['active'] = 1
    success = staff_repository.update_staff(staff_id, data)
    if success:
        return jsonify({'message': 'Staff updated'})
    return jsonify({'error': 'Staff not found'}), 404

@staff_bp.route('/staff/<int:staff_id>', methods=['DELETE'])
def delete(staff_id):
    success = staff_repository.delete_staff(staff_id)
    if success:
        return jsonify({'message': 'Staff deleted'})
    return jsonify({'error': 'Staff not found'}), 404

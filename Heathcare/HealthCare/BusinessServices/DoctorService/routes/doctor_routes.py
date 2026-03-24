# routes/doctor_routes.py

from flask import Blueprint, request, jsonify
from repository import doctor_repository

doctor_bp = Blueprint('doctors', __name__)

@doctor_bp.route('/doctors', methods=['GET'])
def get_all():
    doctors = doctor_repository.get_all_doctors()
    return jsonify([d.to_dict() for d in doctors])

@doctor_bp.route('/doctors/<int:doctor_id>', methods=['GET'])
def get_one(doctor_id):
    doctor = doctor_repository.get_doctor_by_id(doctor_id)
    if doctor:
        return jsonify(doctor.to_dict())
    return jsonify({'error': 'Doctor not found'}), 404

@doctor_bp.route('/doctors', methods=['POST'])
def create():
    data = request.get_json()
    required = ['name', 'specialty', 'contact']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing fields'}), 400
    doctor_id = doctor_repository.create_doctor(data)
    return jsonify({'message': 'Doctor added', 'id': doctor_id}), 201

@doctor_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
def update(doctor_id):
    data = request.get_json()
    if 'available' not in data:
        data['available'] = 1
    success = doctor_repository.update_doctor(doctor_id, data)
    if success:
        return jsonify({'message': 'Doctor updated'})
    return jsonify({'error': 'Doctor not found'}), 404

@doctor_bp.route('/doctors/<int:doctor_id>', methods=['DELETE'])
def delete(doctor_id):
    success = doctor_repository.delete_doctor(doctor_id)
    if success:
        return jsonify({'message': 'Doctor deleted'})
    return jsonify({'error': 'Doctor not found'}), 404

@doctor_bp.route('/doctors/available', methods=['GET'])
def available():
    doctors = doctor_repository.get_available_doctors()
    return jsonify([d.to_dict() for d in doctors])

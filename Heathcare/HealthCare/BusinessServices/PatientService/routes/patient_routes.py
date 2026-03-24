# routes/patient_routes.py

from flask import Blueprint, request, jsonify
from repository import patient_repository

patient_bp = Blueprint('patients', __name__)

@patient_bp.route('/patients', methods=['GET'])
def get_patients():
    patients = patient_repository.get_all_patients()
    return jsonify([p.to_dict() for p in patients])

@patient_bp.route('/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    patient = patient_repository.get_patient_by_id(patient_id)
    if patient:
        return jsonify(patient.to_dict())
    return jsonify({'error': 'Patient not found'}), 404

@patient_bp.route('/patients', methods=['POST'])
def create_patient():
    data = request.get_json()
    required_fields = ['name', 'age', 'gender', 'contact']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing fields'}), 400

    new_id = patient_repository.create_patient(data)
    return jsonify({'message': 'Patient added', 'id': new_id}), 201

@patient_bp.route('/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    data = request.get_json()
    success = patient_repository.update_patient(patient_id, data)
    if success:
        return jsonify({'message': 'Patient updated'})
    return jsonify({'error': 'Patient not found'}), 404

@patient_bp.route('/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    success = patient_repository.delete_patient(patient_id)
    if success:
        return jsonify({'message': 'Patient deleted'})
    return jsonify({'error': 'Patient not found'}), 404

# routes/appointment_routes.py

from flask import Blueprint, request, jsonify
from repository import appointment_repository
from datetime import date

appointment_bp = Blueprint('appointments', __name__)

@appointment_bp.route('/appointments', methods=['GET'])
def get_all():
    appts = appointment_repository.get_all_appointments()
    return jsonify([a.to_dict() for a in appts])

@appointment_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
def get_one(appointment_id):
    appt = appointment_repository.get_appointment_by_id(appointment_id)
    if appt:
        return jsonify(appt.to_dict())
    return jsonify({'error': 'Appointment not found'}), 404

@appointment_bp.route('/appointments', methods=['POST'])
def create():
    data = request.get_json()
    required = ['patient_name', 'doctor_name', 'date', 'time', 'status']
    if not all(k in data for k in required):
        return jsonify({'error': 'Missing fields'}), 400
    appt_id = appointment_repository.create_appointment(data)
    return jsonify({'message': 'Appointment created', 'id': appt_id}), 201

@appointment_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
def update(appointment_id):
    data = request.get_json()
    success = appointment_repository.update_appointment(appointment_id, data)
    if success:
        return jsonify({'message': 'Appointment updated'})
    return jsonify({'error': 'Appointment not found'}), 404

@appointment_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
def delete(appointment_id):
    success = appointment_repository.delete_appointment(appointment_id)
    if success:
        return jsonify({'message': 'Appointment deleted'})
    return jsonify({'error': 'Appointment not found'}), 404

@appointment_bp.route('/appointments/today', methods=['GET'])
def get_today():
    today = date.today().isoformat()
    appts = appointment_repository.get_today_appointments(today)
    return jsonify([a.to_dict() for a in appts])

# routes/appointment_api.py

from flask import Blueprint, request, jsonify
import requests

APPOINTMENT_SERVICE_URL = 'http://localhost:5003'

appointment_bp = Blueprint('appointment_api', __name__)

@appointment_bp.route('/appointments', methods=['GET'])
def get_appointments():
    res = requests.get(f'{APPOINTMENT_SERVICE_URL}/appointments')
    return jsonify(res.json()), res.status_code

@appointment_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
def get_appointment(appointment_id):
    res = requests.get(f'{APPOINTMENT_SERVICE_URL}/appointments/{appointment_id}')
    return jsonify(res.json()), res.status_code

@appointment_bp.route('/appointments', methods=['POST'])
def create_appointment():
    data = request.get_json()
    res = requests.post(f'{APPOINTMENT_SERVICE_URL}/appointments', json=data)
    return jsonify(res.json()), res.status_code

@appointment_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
def update_appointment(appointment_id):
    data = request.get_json()
    res = requests.put(f'{APPOINTMENT_SERVICE_URL}/appointments/{appointment_id}', json=data)
    return jsonify(res.json()), res.status_code

@appointment_bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    res = requests.delete(f'{APPOINTMENT_SERVICE_URL}/appointments/{appointment_id}')
    return jsonify(res.json()), res.status_code

@appointment_bp.route('/appointments/today', methods=['GET'])
def get_today_appointments():
    res = requests.get(f'{APPOINTMENT_SERVICE_URL}/appointments/today')
    return jsonify(res.json()), res.status_code

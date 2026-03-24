# routes/doctor_api.py

from flask import Blueprint, request, jsonify
import requests

DOCTOR_SERVICE_URL = 'http://localhost:5002'

doctor_bp = Blueprint('doctor_api', __name__)

@doctor_bp.route('/doctors', methods=['GET'])
def get_doctors():
    res = requests.get(f'{DOCTOR_SERVICE_URL}/doctors')
    return jsonify(res.json()), res.status_code

@doctor_bp.route('/doctors/<int:doctor_id>', methods=['GET'])
def get_doctor(doctor_id):
    res = requests.get(f'{DOCTOR_SERVICE_URL}/doctors/{doctor_id}')
    return jsonify(res.json()), res.status_code

@doctor_bp.route('/doctors', methods=['POST'])
def create_doctor():
    data = request.get_json()
    res = requests.post(f'{DOCTOR_SERVICE_URL}/doctors', json=data)
    return jsonify(res.json()), res.status_code

@doctor_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
def update_doctor(doctor_id):
    data = request.get_json()
    res = requests.put(f'{DOCTOR_SERVICE_URL}/doctors/{doctor_id}', json=data)
    return jsonify(res.json()), res.status_code

@doctor_bp.route('/doctors/<int:doctor_id>', methods=['DELETE'])
def delete_doctor(doctor_id):
    res = requests.delete(f'{DOCTOR_SERVICE_URL}/doctors/{doctor_id}')
    return jsonify(res.json()), res.status_code

@doctor_bp.route('/doctors/available', methods=['GET'])
def get_available_doctors():
    res = requests.get(f'{DOCTOR_SERVICE_URL}/doctors/available')
    return jsonify(res.json()), res.status_code

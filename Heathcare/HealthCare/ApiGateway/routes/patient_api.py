# routes/patient_api.py

from flask import Blueprint, request, jsonify
import requests

PATIENT_SERVICE_URL = 'http://localhost:5001'

patient_bp = Blueprint('patient_api', __name__)

@patient_bp.route('/patients', methods=['GET'])
def get_patients():
    res = requests.get(f'{PATIENT_SERVICE_URL}/patients')
    return jsonify(res.json()), res.status_code

@patient_bp.route('/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    res = requests.get(f'{PATIENT_SERVICE_URL}/patients/{patient_id}')
    return jsonify(res.json()), res.status_code

@patient_bp.route('/patients', methods=['POST'])
def create_patient():
    data = request.get_json()
    res = requests.post(f'{PATIENT_SERVICE_URL}/patients', json=data)
    return jsonify(res.json()), res.status_code

@patient_bp.route('/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    data = request.get_json()
    res = requests.put(f'{PATIENT_SERVICE_URL}/patients/{patient_id}', json=data)
    return jsonify(res.json()), res.status_code

@patient_bp.route('/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    res = requests.delete(f'{PATIENT_SERVICE_URL}/patients/{patient_id}')
    return jsonify(res.json()), res.status_code

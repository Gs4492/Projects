# routes/staff_api.py

from flask import Blueprint, request, jsonify
import requests

STAFF_SERVICE_URL = 'http://localhost:5005'

staff_bp = Blueprint('staff_api', __name__)

@staff_bp.route('/staff', methods=['GET'])
def get_staff():
    res = requests.get(f'{STAFF_SERVICE_URL}/staff')
    return jsonify(res.json()), res.status_code

@staff_bp.route('/staff/active', methods=['GET'])
def get_active_staff():
    res = requests.get(f'{STAFF_SERVICE_URL}/staff/active')
    return jsonify(res.json()), res.status_code

@staff_bp.route('/staff', methods=['POST'])
def create_staff():
    data = request.get_json()
    res = requests.post(f'{STAFF_SERVICE_URL}/staff', json=data)
    return jsonify(res.json()), res.status_code

@staff_bp.route('/staff/<int:staff_id>', methods=['PUT'])
def update_staff(staff_id):
    data = request.get_json()
    res = requests.put(f'{STAFF_SERVICE_URL}/staff/{staff_id}', json=data)
    return jsonify(res.json()), res.status_code

@staff_bp.route('/staff/<int:staff_id>', methods=['DELETE'])
def delete_staff(staff_id):
    res = requests.delete(f'{STAFF_SERVICE_URL}/staff/{staff_id}')
    return jsonify(res.json()), res.status_code

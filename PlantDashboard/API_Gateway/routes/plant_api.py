import requests
from flask import Blueprint, request, jsonify

plant_api = Blueprint('plant_api', __name__)
PLANT_SERVICE_URL = 'http://localhost:5001'

@plant_api.route('/plants', methods=['GET', 'POST'])
def handle_plants():
    if request.method == 'GET':
        res = requests.get(f'{PLANT_SERVICE_URL}/plants')
        return jsonify(res.json()), res.status_code
    if request.method == 'POST':
        res = requests.post(f'{PLANT_SERVICE_URL}/plants', json=request.json)
        return jsonify(res.json()), res.status_code

@plant_api.route('/plants/<int:plant_id>', methods=['PUT', 'DELETE'])
def modify_plant(plant_id):
    if request.method == 'PUT':
        res = requests.put(f'{PLANT_SERVICE_URL}/plants/{plant_id}', json=request.json)
        return jsonify(res.json()), res.status_code
    if request.method == 'DELETE':
        res = requests.delete(f'{PLANT_SERVICE_URL}/plants/{plant_id}')
        return jsonify(res.json()), res.status_code

from flask import Blueprint, request, jsonify
from repository.plant_repository import (
    get_all_plants,
    add_plant,
    update_plant,
    delete_plant
)

plant_bp = Blueprint('plant_bp', __name__)

@plant_bp.route('/plants', methods=['GET'])
def fetch_plants():
    plants = get_all_plants()
    return jsonify(plants), 200

@plant_bp.route('/plants', methods=['POST'])
def create_plant():
    data = request.json
    add_plant(data)
    return jsonify({'message': 'Plant added successfully'}), 201

@plant_bp.route('/plants/<int:plant_id>', methods=['PUT'])
def update_plant_by_id(plant_id):
    data = request.json
    success = update_plant(plant_id, data)
    if success:
        return jsonify({'message': 'Plant updated successfully'}), 200
    return jsonify({'error': 'Plant not found'}), 404

@plant_bp.route('/plants/<int:plant_id>', methods=['DELETE'])
def delete_plant_by_id(plant_id):
    success = delete_plant(plant_id)
    if success:
        return jsonify({'message': 'Plant deleted successfully'}), 200
    return jsonify({'error': 'Plant not found'}), 404

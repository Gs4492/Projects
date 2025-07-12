from flask import Blueprint, render_template, request, redirect, url_for
import requests

plant_bp = Blueprint('plant_bp', __name__)
API_URL = 'http://localhost:8000/plants'

@plant_bp.route('/plants')
def plants():
    res = requests.get(API_URL)
    plants = res.json() if res.status_code == 200 else []
    return render_template('plants.html', plants=plants)

@plant_bp.route('/plants/add', methods=['POST'])
def add_plant():
    data = {
        'name': request.form['name'],
        'category': request.form['category'],
        'price': float(request.form['price']),
        'stock': int(request.form['stock']),
        'image_url': request.form.get('image_url', '')
    }
    requests.post(API_URL, json=data)
    return redirect(url_for('plant_bp.plants'))

@plant_bp.route('/plants/delete/<int:id>')
def delete_plant(id):
    requests.delete(f"{API_URL}/{id}")
    return redirect(url_for('plant_bp.plants'))

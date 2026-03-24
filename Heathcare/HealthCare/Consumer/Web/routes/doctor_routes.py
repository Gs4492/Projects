# routes/doctor_routes.py

from flask import Blueprint, render_template, request, redirect, url_for
import requests


doctor_bp = Blueprint('doctors', __name__)
API_URL = 'http://localhost:8000/api/doctors'

@doctor_bp.route('/doctors')
def list_doctors():
    res = requests.get(API_URL)
    return render_template('doctors.html', doctors=res.json())

@doctor_bp.route('/doctors/add', methods=['POST'])
def add_doctor():
    data = {
        "name": request.form['name'],
        "specialty": request.form['specialty'],  # fixed name
        "contact": request.form['contact'],      # added field
        "available": request.form['available'] == '1'
    }
    response = requests.post('http://localhost:8000/api/doctors', json=data)
    return redirect(url_for('doctors.list_doctors'))

@doctor_bp.route('/doctors/edit/<int:doctor_id>', methods=['POST'])
def edit_doctor(doctor_id):
    data = {
        "name": request.form['name'],
        "specialty": request.form['specialty'],
        "contact": request.form['contact'],
        "available": request.form['available'] == '1'
    }
    requests.put(f'http://localhost:8000/api/doctors/{doctor_id}', json=data)
    return redirect(url_for('doctors.list_doctors'))


@doctor_bp.route('/doctors/delete/<int:doctor_id>')
def delete_doctor(doctor_id):
    requests.delete(f'{API_URL}/{doctor_id}')
    return redirect(url_for('doctors.list_doctors'))

# routes/patient_routes.py

from flask import Blueprint, render_template, request, redirect, url_for
import requests

patient_bp = Blueprint('patients', __name__)
API_URL = 'http://localhost:8000/api/patients'

@patient_bp.route('/patients')
def list_patients():
    res = requests.get(API_URL)
    return render_template('patients.html', patients=res.json())

@patient_bp.route('/patients/add', methods=['POST'])
def add_patient():
    data = {
        "name": request.form['name'],
        "age": request.form['age'],
        "gender": request.form['gender'],
        "contact": request.form['contact']
    }
    requests.post(API_URL, json=data)
    return redirect(url_for('patients.list_patients'))

@patient_bp.route('/patients/delete/<int:patient_id>')
def delete_patient(patient_id):
    requests.delete(f'{API_URL}/{patient_id}')
    return redirect(url_for('patients.list_patients'))

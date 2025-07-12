# routes/appointment_routes.py

from flask import Blueprint, render_template, request, redirect, url_for
import requests

appointment_bp = Blueprint('appointments', __name__)
API_URL = 'http://localhost:8000/api/appointments'

@appointment_bp.route('/appointments')
def list_appointments():
    res = requests.get(API_URL)
    return render_template('appointments.html', appointments=res.json())

@appointment_bp.route('/appointments/add', methods=['POST'])
def add_appointment():
    data = {
        "patient_name": request.form['patient_name'],
        "doctor_name": request.form['doctor_name'],
        "date": request.form['date'],
        "time": request.form['time'],
        "status": request.form['status']
    }
    requests.post(API_URL, json=data)
    return redirect(url_for('appointments.list_appointments'))

@appointment_bp.route('/appointments/edit/<int:appointment_id>', methods=['GET', 'POST'])
def edit_appointment(appointment_id):
    if request.method == 'POST':
        updated_data = {
            "patient_name": request.form['patient_name'],
            "doctor_name": request.form['doctor_name'],
            "date": request.form['date'],
            "time": request.form['time'],
            "status": request.form['status']
        }
        requests.put(f'{API_URL}/{appointment_id}', json=updated_data)
        return redirect(url_for('appointments.list_appointments'))

    # GET: Fetch existing appointment details
    res = requests.get(f'{API_URL}/{appointment_id}')
    if res.status_code == 200:
        appt = res.json()
        return render_template('appointments_edit.html', appointment=appt)
    else:
        return f"Appointment with ID {appointment_id} not found", 404


@appointment_bp.route('/appointments/delete/<int:appointment_id>')
def delete_appointment(appointment_id):
    requests.delete(f'{API_URL}/{appointment_id}')
    return redirect(url_for('appointments.list_appointments'))

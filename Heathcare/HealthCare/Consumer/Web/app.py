from flask import Flask, render_template, jsonify
import requests
import concurrent.futures

from routes.patient_routes import patient_bp
from routes.doctor_routes import doctor_bp
from routes.appointment_routes import appointment_bp
from routes.billing_routes import billing_bp
from routes.staff_routes import staff_bp

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(patient_bp)
app.register_blueprint(doctor_bp)
app.register_blueprint(appointment_bp)
app.register_blueprint(billing_bp)
app.register_blueprint(staff_bp)

# ✅ Dashboard Page — NO data fetched here
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

# ✅ Dashboard API — Now faster with parallel requests
@app.route('/api/dashboard-data')
def dashboard_data():
    stats = {}

    endpoints = {
        "patients": "http://localhost:8000/api/patients",
        "doctors": "http://localhost:8000/api/doctors",
        "appointments": "http://localhost:8000/api/appointments",
        "invoices": "http://localhost:8000/api/invoices",
        "staff": "http://localhost:8000/api/staff"
    }

    def fetch(endpoint):
        try:
            return requests.get(endpoint).json()
        except Exception:
            return []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(fetch, endpoints.values()))

    patients, doctors, appointments, invoices, staff = results

    stats['total_patients'] = len(patients)
    stats['total_doctors'] = len(doctors)
    stats['available_doctors'] = len([d for d in doctors if d.get('available')])

    stats['total_appointments'] = len(appointments)
    stats['appointment_statuses'] = {}
    for a in appointments:
        stats['appointment_statuses'][a['status']] = stats['appointment_statuses'].get(a['status'], 0) + 1

    stats['total_invoices'] = len(invoices)
    stats['invoice_statuses'] = {'Paid': 0, 'Unpaid': 0}
    for i in invoices:
        stats['invoice_statuses'][i['status']] += 1

    stats['total_staff'] = len(staff)
    stats['active_staff'] = len([s for s in staff if s.get('active')])

    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True, port=7000)

# app.py

from flask import Flask
from routes.patient_api import patient_bp
from routes.doctor_api import doctor_bp
from routes.appointment_api import appointment_bp
from routes.billing_api import billing_bp
from routes.staff_api import staff_bp

app = Flask(__name__)

# Register all service blueprints
app.register_blueprint(patient_bp, url_prefix='/api')
app.register_blueprint(doctor_bp, url_prefix='/api')
app.register_blueprint(appointment_bp, url_prefix='/api')
app.register_blueprint(billing_bp, url_prefix='/api')
app.register_blueprint(staff_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True, port=8000)

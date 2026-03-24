# app.py

from flask import Flask
from routes.patient_routes import patient_bp
from utils.db import init_db

app = Flask(__name__)

# Initialize DB and register patient routes
init_db()
app.register_blueprint(patient_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5001)

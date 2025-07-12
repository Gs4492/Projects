

from flask import Flask
from routes.doctor_routes import doctor_bp
from utils.db import init_db

app = Flask(__name__)

init_db()
app.register_blueprint(doctor_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5002)

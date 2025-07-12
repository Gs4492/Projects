# app.py

from flask import Flask
from routes.invoice_routes import invoice_bp
from utils.db import init_db

app = Flask(__name__)

init_db()
app.register_blueprint(invoice_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5004)

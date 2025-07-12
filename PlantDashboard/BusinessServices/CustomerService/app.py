from flask import Flask
from utils.db import init_db
from routes.customer_routes import customer_bp

app = Flask(__name__)

init_db()
app.register_blueprint(customer_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5003)

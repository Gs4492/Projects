from flask import Flask
from utils.db import init_db
from routes.order_routes import order_bp

app = Flask(__name__)

init_db()
app.register_blueprint(order_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5002)

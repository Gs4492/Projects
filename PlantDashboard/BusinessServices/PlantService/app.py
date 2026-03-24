from flask import Flask
from utils.db import init_db
from routes.plant_routes import plant_bp

app = Flask(__name__)

# Initialize DB
init_db()

# Register routes
app.register_blueprint(plant_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5001)

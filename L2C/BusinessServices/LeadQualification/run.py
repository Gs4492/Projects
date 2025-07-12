from flask import Flask
from routes.lead_qualification_routes import lead_qualification_bp
from utils.db import init_db

app = Flask(__name__)
app.register_blueprint(lead_qualification_bp)

if __name__ == '__main__':
    init_db()
    app.run(port=5011, debug=True)

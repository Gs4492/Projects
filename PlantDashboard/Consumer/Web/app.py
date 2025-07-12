from flask import Flask
from routes.dashboard_routes import dashboard_bp
from routes.plant_routes import plant_bp
from routes.order_routes import order_bp
from routes.customer_routes import customer_bp
from routes.billing_routes import billing_bp

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(dashboard_bp)
app.register_blueprint(plant_bp)
app.register_blueprint(order_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(billing_bp)

# Static and Template folders
app.static_folder = 'static'
app.template_folder = 'templates'

if __name__ == '__main__':
    app.run(debug=True, port=5000)

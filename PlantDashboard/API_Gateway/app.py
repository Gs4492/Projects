from flask import Flask
from flask_cors import CORS
from routes.plant_api import plant_api
from routes.order_api import order_api
from routes.customer_api import customer_api
from routes.billing_api import billing_api

app = Flask(__name__)
# Enable CORS for all routes
CORS(app)

# Register routes from each microservice
app.register_blueprint(plant_api)
app.register_blueprint(order_api)
app.register_blueprint(customer_api)
app.register_blueprint(billing_api)

if __name__ == '__main__':
    app.run(debug=True, port=8000)

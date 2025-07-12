from flask import Flask
from flask_cors import CORS

from services.cash_application import cash_app_blueprint
from services.credit_managment import credit_mgmt_blueprint
from services.dispute_resolution import dispute_blueprint
from services.fulfillment import fulfillment_blueprint
from services.invoicing import invoicing_blueprint
from services.order_management import order_blueprint
from services.payment_collection import payment_blueprint
from services.reporting import report_blueprint
from services.lead_generation import lead_generation_blueprint

app = Flask(__name__)
CORS(app)

# Register the blueprint for each microservice
app.register_blueprint(cash_app_blueprint)
app.register_blueprint(credit_mgmt_blueprint)
app.register_blueprint(dispute_blueprint)
app.register_blueprint(fulfillment_blueprint)
app.register_blueprint(invoicing_blueprint)
app.register_blueprint(order_blueprint)
app.register_blueprint(payment_blueprint)
app.register_blueprint(report_blueprint)
app.register_blueprint(lead_generation_blueprint)


if __name__ == '__main__':
    app.run(port=5050, debug=True)
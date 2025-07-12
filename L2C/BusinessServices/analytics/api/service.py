from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

MICROSERVICE_URLS = {
    'order_management': 'http://127.0.0.1:5001/orders',
    'credit_management': 'http://127.0.0.1:5002/credits',
    'payment_collection': 'http://127.0.0.1:5003/payments',
    'fulfillment': 'http://127.0.0.1:5004/fulfillment',
    'invoicing': 'http://127.0.0.1:5005/invoices',
    'dispute_resolution': 'http://127.0.0.1:5006/disputes',
    'reporting': 'http://127.0.0.1:5007/reports',
    'cash_application': 'http://127.0.0.1:5008/cash'
}

@app.route('/analytics', methods=['GET'])
def get_analytics():
    analytics_data = {}
    for service, url in MICROSERVICE_URLS.items():
        try:
            response = requests.get(url)
            if response.status_code == 200:
                analytics_data[service] = len(response.json())  # Number of records as a simple metric
            else:
                analytics_data[service] = 0
        except Exception:
            analytics_data[service] = 'Error'
    return jsonify(analytics_data)

if __name__ == '__main__':
    app.run(port=5009, debug=True)


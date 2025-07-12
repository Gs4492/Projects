from flask import Flask, jsonify, request
from flask_cors import CORS
from BusinessServices.cash_application.utils.db import get_db_connection, init_db
from BusinessServices.cash_application.models.cashapplication import CashApplication

app = Flask(__name__)
CORS(app)

init_db()

@app.route('/cash_applications', methods=['GET'])
def get_cash_applications():
    conn = get_db_connection()
    applications = conn.execute('SELECT * FROM cash_application').fetchall()
    conn.close()

    application_list = [dict(application) for application in applications]
    return jsonify(application_list)

@app.route('/cash_applications', methods=['POST'])
def add_cash_application():
    data = request.get_json()
    application = CashApplication(
        payment_number=data.get('payment_number'),
        customer_name=data.get('customer_name'),
        amount=data.get('amount'),
        application_date=data.get('application_date'),
        status=data.get('status')
    )

    conn = get_db_connection()
    conn.execute('INSERT INTO cash_application (payment_number, customer_name, amount, application_date, status) VALUES (?, ?, ?, ?, ?)',
                 (application.payment_number, application.customer_name, application.amount, application.application_date, application.status))
    conn.commit()
    conn.close()

    return jsonify({"message": "Cash application added successfully"}), 201

@app.route('/cash_applications/<int:id>', methods=['DELETE'])
def delete_cash_application(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM cash_application WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Cash application deleted successfully"})

@app.route('/cash_applications/<int:id>', methods=['PUT'])
def update_cash_application(id):
    data = request.get_json()
    conn = get_db_connection()
    conn.execute('UPDATE cash_application SET payment_number = ?, customer_name = ?, amount = ?, application_date = ?, status = ? WHERE id = ?',
                 (data.get('payment_number'), data.get('customer_name'), data.get('amount'), data.get('application_date'), data.get('status'), id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Cash application updated successfully"})

if __name__ == '__main__':
    app.run(port=5008, debug=True)

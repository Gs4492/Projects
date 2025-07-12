from flask import Flask, jsonify, request
from flask_cors import CORS
from BusinessServices.credit_management.utils.db import get_db_connection, init_db
from BusinessServices.credit_management.models.credit import Credit

app = Flask(__name__)
CORS(app)

# Initialize the database
init_db()

@app.route('/credits', methods=['GET'])
def get_credits():
    conn = get_db_connection()
    credits = conn.execute('SELECT * FROM credits').fetchall()
    conn.close()

    credit_list = [dict(credit) for credit in credits]
    return jsonify(credit_list)

@app.route('/credits', methods=['POST'])
def add_credit():
    data = request.get_json()
    credit = Credit(
        customer_name=data.get('customer_name'),
        credit_amount=data.get('credit_amount'),
        credit_status=data.get('credit_status')
    )

    conn = get_db_connection()
    conn.execute('INSERT INTO credits (customer_name, credit_amount, credit_status) VALUES (?, ?, ?)',
                 (credit.customer_name, credit.credit_amount, credit.credit_status))
    conn.commit()
    conn.close()

    return jsonify({"message": "Credit added successfully"}), 201

@app.route('/credits/<int:credit_id>', methods=['PUT'])
def update_credit(credit_id):
    data = request.get_json()
    conn = get_db_connection()
    conn.execute('UPDATE credits SET customer_name=?, credit_amount=?, credit_status=? WHERE id=?',
                 (data.get('customer_name'), data.get('credit_amount'), data.get('credit_status'), credit_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Credit updated successfully"}), 200

@app.route('/credits/<int:credit_id>', methods=['DELETE'])
def delete_credit(credit_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM credits WHERE id=?', (credit_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Credit deleted successfully"}), 200

if __name__ == '__main__':
    app.run(port=5002, debug=True)

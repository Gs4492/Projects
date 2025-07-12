from flask import Flask, jsonify, request
from flask_cors import CORS
from BusinessServices.fulfillment.utils.db import get_db_connection, init_db

app = Flask(__name__)

CORS(app)


# Initialize the database
init_db()

# Get all fulfillments
@app.route('/fulfillment', methods=['GET'])
def get_fulfillments():
    conn = get_db_connection()
    fulfillments = conn.execute('SELECT * FROM fulfillment').fetchall()
    conn.close()
    return jsonify([dict(row) for row in fulfillments])

# Add a new fulfillment
@app.route('/fulfillment', methods=['POST'])
def add_fulfillment():
    data = request.get_json()
    order_number = data.get('order_number')
    fulfillment_date = data.get('fulfillment_date')
    status = data.get('status')

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO fulfillment (order_number, fulfillment_date, status) VALUES (?, ?, ?)',
        (order_number, fulfillment_date, status)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Fulfillment added successfully'}), 201

# Update an existing fulfillment
@app.route('/fulfillment/<int:id>', methods=['PUT'])
def update_fulfillment(id):
    data = request.get_json()
    order_number = data.get('order_number')
    fulfillment_date = data.get('fulfillment_date')
    status = data.get('status')

    conn = get_db_connection()
    conn.execute(
        'UPDATE fulfillment SET order_number = ?, fulfillment_date = ?, status = ? WHERE id = ?',
        (order_number, fulfillment_date, status, id)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Fulfillment updated successfully'})

# Delete a fulfillment
@app.route('/fulfillment/<int:id>', methods=['DELETE'])
def delete_fulfillment(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM fulfillment WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Fulfillment deleted successfully'})

if __name__ == '__main__':
    app.run(port=5004, debug=True)


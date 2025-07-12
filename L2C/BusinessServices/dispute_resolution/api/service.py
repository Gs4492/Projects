from flask import Flask, jsonify, request
from flask_cors import CORS
from BusinessServices.dispute_resolution.utils.db import get_db_connection, init_db
from BusinessServices.dispute_resolution.models.dispute import Dispute

app = Flask(__name__)
CORS(app)

# Initialize the database
init_db()

@app.route('/disputes', methods=['GET'])
def get_disputes():
    conn = get_db_connection()
    disputes = conn.execute('SELECT * FROM dispute').fetchall()
    conn.close()

    dispute_list = [dict(dispute) for dispute in disputes]
    return jsonify(dispute_list)

@app.route('/disputes', methods=['POST'])
def add_dispute():
    data = request.get_json()
    dispute = Dispute(
        dispute_number=data.get('dispute_number'),
        order_number=data.get('order_number'),
        description=data.get('description'),
        resolution_status=data.get('resolution_status')
    )

    conn = get_db_connection()
    conn.execute('INSERT INTO dispute (dispute_number, order_number, description, resolution_status) VALUES (?, ?, ?, ?)',
                 (dispute.dispute_number, dispute.order_number, dispute.description, dispute.resolution_status))
    conn.commit()
    conn.close()

    return jsonify({"message": "Dispute added successfully"}), 201

@app.route('/disputes/<int:id>', methods=['DELETE'])
def delete_dispute(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM dispute WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Dispute deleted successfully"})

@app.route('/disputes/<int:id>', methods=['PUT'])
def update_dispute(id):
    data = request.get_json()
    conn = get_db_connection()
    conn.execute('UPDATE dispute SET dispute_number = ?, order_number = ?, description = ?, resolution_status = ? WHERE id = ?',
                 (data.get('dispute_number'), data.get('order_number'), data.get('description'), data.get('resolution_status'), id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Dispute updated successfully"})

if __name__ == '__main__':
    app.run(port=5006, debug=True)

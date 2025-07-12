from flask import Flask, jsonify, request
from BusinessServices.order_management.utils.db import get_db_connection, init_db
from BusinessServices.order_management.models.order import Order
from flask_cors import CORS



app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize the database
init_db()

@app.route('/orders', methods=['GET'])
def get_orders():
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM orders').fetchall()
    conn.close()

    order_list = [dict(order) for order in orders]
    return jsonify(order_list)

@app.route('/orders', methods=['POST'])
def add_order():
    data = request.get_json()
    order = Order(
        order_number=data.get('order_number'),
        customer_name=data.get('customer_name'),
        order_date=data.get('order_date'),
        status=data.get('status')
    )

    conn = get_db_connection()
    conn.execute('INSERT INTO orders (order_number, customer_name, order_date, status) VALUES (?, ?, ?, ?)',
                 (order.order_number, order.customer_name, order.order_date, order.status))
    conn.commit()
    conn.close()

    return jsonify({"message": "Order added successfully"}), 201

@app.route('/orders/<int:id>', methods=['PUT'])
def update_order(id):
    data = request.get_json()
    conn = get_db_connection()
    conn.execute(
        'UPDATE orders SET order_number = ?, customer_name = ?, order_date = ?, status = ? WHERE id = ?',
        (data.get('order_number'), data.get('customer_name'), data.get('order_date'), data.get('status'), id)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Order updated successfully"}), 200

@app.route('/orders/<int:id>', methods=['DELETE'])
def delete_order(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM orders WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Order deleted successfully"}), 200


if __name__ == '__main__':
    app.run(port=5001, debug=True)

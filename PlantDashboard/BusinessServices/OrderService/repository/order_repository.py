from utils.db import get_db_connection
from models.order import Order

def get_all_orders():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM orders').fetchall()
    conn.close()
    return [Order(**row).to_dict() for row in rows]

def add_order(data):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO orders (customer_name, plant_name, quantity, total_price, status) VALUES (?, ?, ?, ?, ?)',
        (data['customer_name'], data['plant_name'], data['quantity'], data['total_price'], data.get('status', 'Pending'))
    )
    conn.commit()
    conn.close()

def update_order_status(order_id, status):
    conn = get_db_connection()
    cursor = conn.execute(
        'UPDATE orders SET status = ? WHERE id = ?',
        (status, order_id)
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

def delete_order(order_id):
    conn = get_db_connection()
    cursor = conn.execute('DELETE FROM orders WHERE id = ?', (order_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

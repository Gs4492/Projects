from utils.db import get_db_connection
from models.customer import Customer

def get_all_customers():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM customers').fetchall()
    conn.close()
    return [Customer(**row).to_dict() for row in rows]

def add_customer(data):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO customers (name, email, phone, address, preferences) VALUES (?, ?, ?, ?, ?)',
        (data['name'], data['email'], data.get('phone'), data.get('address'), data.get('preferences'))
    )
    conn.commit()
    conn.close()

def update_customer(customer_id, data):
    conn = get_db_connection()
    cursor = conn.execute(
        'UPDATE customers SET name = ?, email = ?, phone = ?, address = ?, preferences = ? WHERE id = ?',
        (data['name'], data['email'], data.get('phone'), data.get('address'), data.get('preferences'), customer_id)
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

def delete_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

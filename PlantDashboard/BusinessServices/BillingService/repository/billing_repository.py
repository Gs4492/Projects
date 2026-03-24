from utils.db import get_db_connection
from models.invoice import Invoice
from datetime import datetime

def get_all_invoices():
    conn = get_db_connection()
    rows = conn.execute('SELECT * FROM invoices').fetchall()
    conn.close()
    return [Invoice(**row).to_dict() for row in rows]

def create_invoice(data):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO invoices (order_id, amount, payment_status, payment_date) VALUES (?, ?, ?, ?)',
        (
            data['order_id'],
            data['amount'],
            data.get('payment_status', 'Unpaid'),
            data.get('payment_date')
        )
    )
    conn.commit()
    conn.close()

def update_invoice_status(invoice_id, status):
    payment_date = datetime.now().strftime('%Y-%m-%d') if status == 'Paid' else None
    conn = get_db_connection()
    cursor = conn.execute(
        'UPDATE invoices SET payment_status = ?, payment_date = ? WHERE id = ?',
        (status, payment_date, invoice_id)
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

def get_total_revenue():
    conn = get_db_connection()
    row = conn.execute(
        "SELECT SUM(amount) as total FROM invoices WHERE payment_status = 'Paid'"
    ).fetchone()
    conn.close()
    return row['total'] or 0.0

# repository/invoice_repository.py

from utils.db import get_db_connection
from models.invoice import Invoice

def create_invoice(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO invoices (patient_name, amount, status, date) VALUES (?, ?, ?, ?)",
        (data['patient_name'], data['amount'], data['status'], data['date'])
    )
    conn.commit()
    invoice_id = cursor.lastrowid
    conn.close()
    return invoice_id

def get_all_invoices():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM invoices").fetchall()
    conn.close()
    return [Invoice(**dict(row)) for row in rows]

def get_invoice_by_id(invoice_id):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,)).fetchone()
    conn.close()
    return Invoice(**dict(row)) if row else None

def update_invoice(invoice_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE invoices SET patient_name = ?, amount = ?, status = ?, date = ? WHERE id = ?",
        (data['patient_name'], data['amount'], data['status'], data['date'], invoice_id)
    )
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def delete_invoice(invoice_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

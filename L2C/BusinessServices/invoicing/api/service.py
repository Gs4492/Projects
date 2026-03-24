from flask import Flask, jsonify, request
from flask_cors import CORS
from BusinessServices.invoicing.utils.db import get_db_connection, init_db
from BusinessServices.invoicing.models.invoice import Invoice

app = Flask(__name__)
CORS(app)

# Initialize the database
init_db()

@app.route('/invoices', methods=['GET'])
def get_invoices():
    conn = get_db_connection()
    invoices = conn.execute('SELECT * FROM invoice').fetchall()
    conn.close()

    invoice_list = [dict(invoice) for invoice in invoices]
    return jsonify(invoice_list)

@app.route('/invoices/count', methods=['GET'])
def get_invoice_count():
    conn = get_db_connection()
    count = conn.execute('SELECT COUNT(*) FROM invoice').fetchone()[0]
    conn.close()
    return jsonify({'total_invoices': count})


@app.route('/invoices', methods=['POST'])
def add_invoice():
    data = request.get_json()
    invoice = Invoice(
        invoice_number=data.get('invoice_number'),
        customer_name=data.get('customer_name'),
        amount=data.get('amount'),
        status=data.get('status'),
        issue_date=data.get('issue_date')
    )

    conn = get_db_connection()
    conn.execute('INSERT INTO invoice (invoice_number, customer_name, amount, status, issue_date) VALUES (?, ?, ?, ?, ?)',
                 (invoice.invoice_number, invoice.customer_name, invoice.amount, invoice.status, invoice.issue_date))
    conn.commit()
    conn.close()

    return jsonify({"message": "Invoice added successfully"}), 201

@app.route('/invoices/<int:id>', methods=['PUT'])
def update_invoice(id):
    data = request.get_json()
    conn = get_db_connection()
    conn.execute('UPDATE invoice SET invoice_number = ?, customer_name = ?, amount = ?, status = ?, issue_date = ? WHERE id = ?',
                 (data.get('invoice_number'), data.get('customer_name'), data.get('amount'), data.get('status'), data.get('issue_date'), id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Invoice updated successfully"}), 200

@app.route('/invoices/<int:id>', methods=['DELETE'])
def delete_invoice(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM invoice WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Invoice deleted successfully"}), 200

if __name__ == '__main__':
    app.run(port=5005, debug=True)

from utils.db import get_db_connection

def save_lead(data):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO leads (name, email, phone, source, score)
        VALUES (?, ?, ?, ?, ?)
    ''', (data['name'], data['email'], data['phone'], data.get('source', 'Website'), data['score']))
    conn.commit()
    lead_id = cur.lastrowid
    conn.close()
    return {"id": lead_id, **data}


def fetch_leads():
    conn = get_db_connection()
    leads = conn.execute('SELECT * FROM leads').fetchall()
    conn.close()
    return [dict(row) for row in leads]

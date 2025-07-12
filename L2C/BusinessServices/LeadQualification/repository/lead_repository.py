from utils.db import get_db_connection

def save_qualified_lead(data):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO qualified_leads (name, email, score, qualified)
        VALUES (?, ?, ?, ?)
    ''', (data['name'], data['email'], data['score'], data.get('qualified', 'pending')))
    conn.commit()
    lead_id = cur.lastrowid
    conn.close()
    return {"id": lead_id, **data}

def fetch_qualified_leads():
    conn = get_db_connection()
    leads = conn.execute('SELECT * FROM qualified_leads').fetchall()
    conn.close()
    return [dict(row) for row in leads]

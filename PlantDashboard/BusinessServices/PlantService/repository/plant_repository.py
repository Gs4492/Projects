from utils.db import get_db_connection
from models.plant import Plant

def get_all_plants():
    conn = get_db_connection()
    cursor = conn.execute('SELECT * FROM plants')
    rows = cursor.fetchall()
    conn.close()
    return [Plant(**row).to_dict() for row in rows]

def add_plant(data):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO plants (name, category, price, stock, image_url) VALUES (?, ?, ?, ?, ?)',
        (data['name'], data['category'], data['price'], data['stock'], data.get('image_url'))
    )
    conn.commit()
    conn.close()


def update_plant(plant_id, data):
    conn = get_db_connection()
    cursor = conn.execute(
        'UPDATE plants SET name = ?, category = ?, price = ?, stock = ?, image_url = ? WHERE id = ?',
        (data['name'], data['category'], data['price'], data['stock'], data.get('image_url'), plant_id)
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

def delete_plant(plant_id):
    conn = get_db_connection()
    cursor = conn.execute('DELETE FROM plants WHERE id = ?', (plant_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

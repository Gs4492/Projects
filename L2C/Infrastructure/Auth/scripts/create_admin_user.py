import sqlite3
import hashlib
from Infrastructure.Auth.Web.config import Config 

def create_admin_user():
    username = input("Enter admin username: ")
    password = input("Enter admin password: ")

    # Hash the password
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()

    # Connect to the database
    db_path = Config.DATABASE
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Get role_id for Admin
        cursor.execute("SELECT id FROM roles WHERE name = 'Admin'")
        result = cursor.fetchone()
        if result:
            role_id = result[0]
        else:
            print("Admin role not found.")
            return

        # Insert admin user
        try:
            cursor.execute("""
                INSERT INTO users (username, password, role_id)
                VALUES (?, ?, ?)
            """, (username, hashed_pw, role_id))
            conn.commit()
            print(f"✅ Admin user '{username}' created successfully.")
        except sqlite3.IntegrityError:
            print("⚠️ Username already exists.")

# Run the function
create_admin_user()

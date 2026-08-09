import os
import sqlite3

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'mashreq.db')
print(f"Database path: {db_path}")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # حذف الجداول أو تفريغها بالكامل
    cursor.execute("DELETE FROM client_requests;")
    cursor.execute("DELETE FROM users;")
    conn.commit()
    conn.close()
    print("SQLite database tables (client_requests, users) wiped successfully!")
else:
    print("Database file not found in instance folder, checking root...")
    # حذف أي ملفات db أخرى إن وجدت
    for f in os.listdir(os.path.dirname(__file__) or '.'):
        if f.endswith('.db'):
            db_file = os.path.join(os.path.dirname(__file__), f)
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM client_requests;")
            cursor.execute("DELETE FROM users;")
            conn.commit()
            conn.close()
            print(f"Wiped database: {db_file}")

from app import app, db, UserSession, ClientRequest
with app.app_context():
    db.drop_all()
    db.create_all()
    print("All SQLAlchemy tables dropped and recreated cleanly!")

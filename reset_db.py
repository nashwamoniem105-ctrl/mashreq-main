import os
from app import app, db, UserSession, ClientRequest

with app.app_context():
    # حذف كافة السجلات من الجداول
    print("Deleting old requests and user sessions...")
    ClientRequest.query.delete()
    UserSession.query.delete()
    db.session.commit()
    print("Database cleaned successfully! All old data removed.")

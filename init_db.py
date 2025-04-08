# init_db.py
from app import app, db

# Create all database tables within the app context
with app.app_context():
    db.create_all()
    print("Database initialized.")

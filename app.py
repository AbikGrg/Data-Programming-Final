# app.py
from flask import Flask
from extensions import db
from auth import auth
from main import main

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change in production!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Register Blueprints
app.register_blueprint(auth, url_prefix='/auth')  # Auth routes under /auth/*
app.register_blueprint(main)  # Main routes (including API) at root

# For debugging: print all registered routes
with app.app_context():
    print("Registered Routes:")
    for rule in app.url_map.iter_rules():
        print(rule)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='127.0.0.1', port=5000)
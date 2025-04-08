# app.py
from flask import Flask
from extensions import db
from auth import auth
from main import main

# Setting up the Flask app with configuration and initialize the database

app = Flask(__name__)
app.config['SECRET_KEY'] = 'group6'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Register Blueprints
app.register_blueprint(auth, url_prefix='/auth')  # Auth routes under /auth/*
app.register_blueprint(main)  # Main routes (including API) at root

# For debugging: registered routes printed
with app.app_context():
    print("Registered Routes:")
    for rule in app.url_map.iter_rules():
        print(rule)

# Starts the app and create all database tables if they don't exist
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='127.0.0.1', port=5000)
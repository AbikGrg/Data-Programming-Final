# auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from models import User

auth = Blueprint('auth', __name__)

# Handle user registration: create a new account if the username is not taken
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash("Username already exists.")
            return redirect(url_for('auth.register'))
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.")
        return redirect(url_for('auth.login'))
    return render_template('register.html')

# Handle user login: verify credentials and start a session if valid
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('main.dashboard'))
        flash("Invalid credentials.")
        return redirect(url_for('auth.login'))
    return render_template('login.html')

# Log the user out by clearing the session and redirect to the homepage
@auth.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('main.index'))

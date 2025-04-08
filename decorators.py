# decorators.py
from functools import wraps
from flask import session, redirect, url_for, flash

# Decorator to restrict access to logged-in users only
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

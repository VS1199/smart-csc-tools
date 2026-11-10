from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def superadmin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'superadmin':
            flash('Access denied. Super Admin privileges required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def shop_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('auth.login'))
        if current_user.role not in ['shopkeeper', 'staff']:
            flash('Access restricted to Center staff only.', 'danger')
            return redirect(url_for('auth.login'))
        if not current_user.shop or not current_user.shop.is_active:
            flash('Your CSC Center account is pending approval or inactive.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
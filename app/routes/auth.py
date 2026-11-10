from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.tenant import User, Shop

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'superadmin':
            return redirect(url_for('superadmin.dashboard'))
        return redirect(url_for('shop.dashboard'))

    if request.method == 'POST':
        identifier = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Step 1: Check username match (Superadmin ya individual user)
        user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()

        # Step 2: Agar user nahi mila, to check Shop Code (e.g. CSC101)
        if not user:
            shop = Shop.query.filter_by(shop_code=identifier).first()
            if shop and shop.users:
                user = shop.users[0]

        if user and user.check_password(password):
            if not user.is_active:
                flash('This user account has been disabled.', 'danger')
                return redirect(url_for('auth.login'))

            if user.role != 'superadmin':
                if not user.shop or not user.shop.is_active:
                    flash('Your Center account is currently pending Admin approval.', 'warning')
                    return redirect(url_for('auth.login'))

            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')

            if user.role == 'superadmin':
                return redirect(url_for('superadmin.dashboard'))
            return redirect(url_for('shop.dashboard'))
        else:
            flash('Invalid Center Code / Username or Password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        shop_code = request.form.get('shop_code', '').strip().upper()
        shop_name = request.form.get('shop_name', '').strip()
        owner_name = request.form.get('owner_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if Shop.query.filter_by(shop_code=shop_code).first():
            flash('This Center / Shop Code is already taken.', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('This Username is already registered.', 'danger')
            return redirect(url_for('auth.register'))

        # Create inactive shop awaiting approval
        new_shop = Shop(
            shop_code=shop_code,
            shop_name=shop_name,
            owner_name=owner_name,
            phone=phone,
            email=email,
            address=address,
            is_active=False
        )
        db.session.add(new_shop)
        db.session.flush()

        # Create shopkeeper user linked to this shop
        new_user = User(
            shop_id=new_shop.id,
            username=username,
            email=email,
            role='shopkeeper',
            is_active=True
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Center registration submitted successfully! Please wait for Admin approval before logging in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out safely.', 'info')# Superadmin ko approval ki zaroorat nahi hoti
if user.role != 'SUPERADMIN':
    if user.shop and not user.shop.is_active:
        flash('Your Center account is currently pending Admin approval.', 'warning')
        return redirect(url_for('auth.login'))
        
    return redirect(url_for('auth.login'))

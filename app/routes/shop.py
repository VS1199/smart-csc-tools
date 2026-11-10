from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.tenant import Shop, Service, Transaction, Customer, PrintJob
from datetime import datetime, date

shop_bp = Blueprint('shop', __name__, url_prefix='/shop')

# 1. Main VLE Counter Dashboard
@shop_bp.route('/dashboard')
@login_required
def dashboard():
    shop = current_user.shop
    if not shop:
        flash('No Pragya Kendra assigned to your profile.', 'warning')
        return redirect(url_for('main.index'))

    # Live Database Counts & Figures
    today_transactions = Transaction.query.filter(
        Transaction.shop_id == shop.id,
        db.func.date(Transaction.created_at) == date.today()
    ).all()
    
    today_count = len(today_transactions)
    today_earnings = sum(t.amount for t in today_transactions)
    
    pending_applications = Transaction.query.filter_by(
        shop_id=shop.id,
        status='pending'
    ).count()

    recent_transactions = Transaction.query.filter_by(
        shop_id=shop.id
    ).order_by(Transaction.created_at.desc()).limit(10).all()

    services_list = Service.query.filter_by(shop_id=shop.id, is_active=True).all()

    return render_template(
        'shop/dashboard.html',
        shop=shop,
        wallet_balance=shop.wallet_balance,
        today_count=today_count,
        today_earnings=today_earnings,
        pending_count=pending_applications,
        recent_transactions=recent_transactions,
        services=services_list
    )

# 2. Instant Order / Transaction Create
@shop_bp.route('/transaction/new', methods=['POST'])
@login_required
def new_transaction():
    shop = current_user.shop
    service_name = request.form.get('service_name', 'Quick Service')
    customer_name = request.form.get('customer_name', 'Counter Walk-in')
    amount = float(request.form.get('amount', 0))

    tx = Transaction(
        shop_id=shop.id,
        service_name=service_name,
        customer_name=customer_name,
        amount=amount,
        status='success'
    )
    shop.wallet_balance += amount
    db.session.add(tx)
    db.session.commit()
    flash(f'Transaction for ₹{amount} recorded successfully!', 'success')
    return redirect(url_for('shop.dashboard'))

# 3. Wallet Top Up Action
@shop_bp.route('/wallet/topup', methods=['POST'])
@login_required
def topup_wallet():
    shop = current_user.shop
    topup_amount = float(request.form.get('amount', 500))
    shop.wallet_balance += topup_amount
    db.session.commit()
    flash(f'₹{topup_amount} successfully added to wallet!', 'success')
    return redirect(url_for('shop.dashboard'))

# 4. Sidebar Pages
@shop_bp.route('/services')
@login_required
def services():
    services_list = Service.query.filter_by(shop_id=current_user.shop_id).all()
    return render_template('shop/services.html', services=services_list)

@shop_bp.route('/wallet')
@login_required
def wallet():
    shop = current_user.shop
    history = Transaction.query.filter_by(shop_id=shop.id).order_by(Transaction.created_at.desc()).all()
    return render_template('shop/wallet.html', shop=shop, history=history)

@shop_bp.route('/print-queue')
@login_required
def print_queue():
    jobs = PrintJob.query.filter_by(shop_id=current_user.shop_id).order_by(PrintJob.created_at.desc()).all()
    return render_template('shop/print_queue.html', jobs=jobs)

@shop_bp.route('/khata')
@login_required
def khata():
    customers = Customer.query.filter_by(shop_id=current_user.shop_id).all()
    return render_template('shop/khata.html', customers=customers)

@shop_bp.route('/support')
@login_required
def support():
    return render_template('shop/support.html')

@shop_bp.route('/profile')
@login_required
def profile():
    return render_template('shop/profile.html', user=current_user, shop=current_user.shop)

@shop_bp.route('/tools')
@login_required
def csc_tools():
    return render_template('shop/tools.html')

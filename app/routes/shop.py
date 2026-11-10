from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.tenant import Shop, Service, Transaction, Customer, PrintJob
from datetime import datetime, date

shop_bp = Blueprint('shop', __name__, url_prefix='/shop')

@shop_bp.route('/dashboard')
@login_required
def dashboard():
    shop = current_user.shop
    if not shop:
        flash('Koi Kendra assigned nahi hai.', 'warning')
        return redirect(url_for('main.index'))

    # Aaj ke transactions aur earnings
    today_txs = Transaction.query.filter(
        Transaction.shop_id == shop.id,
        db.func.date(Transaction.created_at) == date.today()
    ).all()
    
    today_count = len(today_txs)
    today_earnings = sum(t.amount for t in today_txs)
    
    pending_count = Transaction.query.filter_by(shop_id=shop.id, status='pending').count()
    recent_transactions = Transaction.query.filter_by(shop_id=shop.id).order_by(Transaction.created_at.desc()).limit(10).all()

    return render_template(
        'shop/dashboard.html',
        shop=shop,
        wallet_balance=shop.wallet_balance,
        today_count=today_count,
        today_earnings=today_earnings,
        pending_count=pending_count,
        recent_transactions=recent_transactions
    )

# Wallet Top Up Action (Card button se chalega)
@shop_bp.route('/wallet/topup', methods=['POST'])
@login_required
def topup_wallet():
    shop = current_user.shop
    if not shop:
        flash('Shop not found.', 'danger')
        return redirect(url_for('shop.dashboard'))

    try:
        amount = float(request.form.get('amount', 0))
        if amount <= 0:
            flash('Valid amount darj karein!', 'warning')
            return redirect(url_for('shop.dashboard'))

        # Balance update
        shop.wallet_balance += amount

        # Transaction entry as Credit
        tx = Transaction(
            shop_id=shop.id,
            customer_name="Self (Wallet Recharge)",
            service_name="Wallet Top-Up",
            amount=amount,
            status='success'
        )
        db.session.add(tx)
        db.session.commit()
        flash(f'₹{amount:.2f} aapke wallet mein safalta-purvak add ho gaye!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Top-up failed: {str(e)}', 'danger')

    return redirect(url_for('shop.dashboard'))

# Sidebar: Wallet & Transactions Page
@shop_bp.route('/wallet')
@login_required
def wallet():
    shop = current_user.shop
    transactions = Transaction.query.filter_by(shop_id=shop.id).order_by(Transaction.created_at.desc()).all()
    return render_template('shop/wallet.html', shop=shop, transactions=transactions)

# Other Navigation Routes
@shop_bp.route('/services')
@login_required
def services():
    return render_template('shop/services.html')

@shop_bp.route('/print-queue')
@login_required
def print_queue():
    return render_template('shop/print_queue.html')

@shop_bp.route('/khata')
@login_required
def khata():
    return render_template('shop/khata.html')

@shop_bp.route('/support')
@login_required
def support():
    return render_template('shop/support.html')

@shop_bp.route('/profile')
@login_required
def profile():
    return render_template('shop/profile.html')

@shop_bp.route('/tools')
@login_required
def csc_tools():
    return render_template('shop/tools.html')

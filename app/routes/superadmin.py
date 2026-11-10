from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.tenant import Shop, User, Transaction

superadmin_bp = Blueprint('superadmin', __name__, url_prefix='/superadmin')

@superadmin_bp.before_request
def restrict_to_superadmin():
    if not current_user.is_authenticated or current_user.role != 'superadmin':
        flash('Unauthorized access: Superadmin only.', 'danger')
        return redirect(url_for('auth.login'))

@superadmin_bp.route('/dashboard')
@login_required
def dashboard():
    total_shops = Shop.query.count()
    active_shops = Shop.query.filter_by(status='active').count()
    pending_shops = Shop.query.filter_by(status='pending').count()
    
    total_transactions = Transaction.query.count()
    total_revenue = db.session.query(db.func.sum(Transaction.amount)).scalar() or 0.0

    all_shops = Shop.query.order_by(Shop.created_at.desc()).all()
    recent_txs = Transaction.query.order_by(Transaction.created_at.desc()).limit(15).all()

    return render_template(
        'superadmin/dashboard.html',
        total_shops=total_shops,
        active_shops=active_shops,
        pending_shops=pending_shops,
        total_transactions=total_transactions,
        total_revenue=total_revenue,
        shops=all_shops,
        recent_transactions=recent_txs
    )

# Kendra Action (Approve / Suspend / Delete)
@superadmin_bp.route('/shop/<int:shop_id>/<action>', methods=['POST'])
@login_required
def manage_shop(shop_id, action):
    shop = Shop.query.get_or_404(shop_id)
    if action == 'approve':
        shop.status = 'active'
        flash(f'{shop.name} approved successfully!', 'success')
    elif action == 'suspend':
        shop.status = 'suspended'
        flash(f'{shop.name} has been suspended!', 'warning')
    elif action == 'delete':
        db.session.delete(shop)
        flash(f'{shop.name} deleted successfully!', 'danger')
    
    db.session.commit()
    return redirect(url_for('superadmin.dashboard'))

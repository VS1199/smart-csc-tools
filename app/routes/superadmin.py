from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models.tenant import Shop, User
from app.services.auth_guard import superadmin_required

superadmin_bp = Blueprint('superadmin', __name__, url_prefix='/superadmin')

@superadmin_bp.route('/dashboard')
@login_required
@superadmin_required
def dashboard():
    shops = Shop.query.order_by(Shop.created_at.desc()).all()
    total_centers = len(shops)
    active_centers = sum(1 for s in shops if s.is_active)
    pending_centers = total_centers - active_centers
    return render_template('superadmin/dashboard.html', 
                           shops=shops, 
                           total_centers=total_centers, 
                           active_centers=active_centers, 
                           pending_centers=pending_centers)

@superadmin_bp.route('/shop/approve/<int:shop_id>')
@login_required
@superadmin_required
def approve_shop(shop_id):
    shop = Shop.query.get_or_404(shop_id)
    shop.is_active = True
    db.session.commit()
    flash(f'Center {shop.shop_code} ({shop.shop_name}) has been approved!', 'success')
    return redirect(url_for('superadmin.dashboard'))

@superadmin_bp.route('/shop/reject/<int:shop_id>')
@login_required
@superadmin_required
def reject_shop(shop_id):
    shop = Shop.query.get_or_404(shop_id)
    shop.is_active = False
    db.session.commit()
    flash(f'Center {shop.shop_code} has been deactivated/rejected.', 'warning')
    return redirect(url_for('superadmin.dashboard'))
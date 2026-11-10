from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.tenant import Shop, User, SiteSetting
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

@superadmin_bp.route('/homepage-stats', methods=['GET', 'POST'])
@login_required
@superadmin_required
def homepage_stats():
    if request.method == 'POST':
        SiteSetting.set('stat_prints', request.form.get('stat_prints', '50,000+'))
        SiteSetting.set('stat_centers', request.form.get('stat_centers', '1,200+'))
        SiteSetting.set('stat_uptime', request.form.get('stat_uptime', '99.98%'))
        SiteSetting.set('stat_latency', request.form.get('stat_latency', '< 0.4s'))
        flash('Homepage metrics updated successfully!', 'success')
        return redirect(url_for('superadmin.homepage_stats'))

    stats = {
        'prints': SiteSetting.get('stat_prints', '50,000+'),
        'centers': SiteSetting.get('stat_centers', '1,200+'),
        'uptime': SiteSetting.get('stat_uptime', '99.98%'),
        'latency': SiteSetting.get('stat_latency', '< 0.4s'),
    }
    return render_template('superadmin/homepage_stats.html', stats=stats)

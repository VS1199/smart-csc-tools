from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.tenant import Tenant, Service, Order
from datetime import datetime, date

shop_bp = Blueprint('shop', __name__, url_prefix='/shop')

# 1. Main Dashboard
@shop_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('shop/dashboard.html')

# 2. Apply for Services (सेवाओं के लिए आवेदन)
@shop_bp.route('/services')
@login_required
def services():
    return render_template('shop/services.html')

# 3. Wallet & Transactions (वॉलेट और लेनदेन)
@shop_bp.route('/wallet')
@login_required
def wallet():
    return render_template('shop/wallet.html')

# 4. Wireless Print Queue (वायरलेस प्रिंट कतार)
@shop_bp.route('/print-queue')
@login_required
def print_queue():
    return render_template('shop/print_queue.html')

# 5. Khata & Applications (ग्राहक खाता व आवेदन)
@shop_bp.route('/khata')
@login_required
def khata():
    return render_template('shop/khata.html')

# 6. Grievance / Support (शिकायत और सहायता)
@shop_bp.route('/support')
@login_required
def support():
    return render_template('shop/support.html')

# 7. My Profile & Certificate (प्रोफाइल और प्रमाणपत्र)
@shop_bp.route('/profile')
@login_required
def profile():
    return render_template('shop/profile.html')

# 8. CSC Tools (फोटो कटर, आधार कार्ड टूल्स)
@shop_bp.route('/tools')
@login_required
def csc_tools():
    return render_template('shop/tools.html')

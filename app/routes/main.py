import os
import uuid
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models.tenant import Shop, PrintJob

main_bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/')
def home():
    return render_template('public/index.html')

@main_bp.route('/print/<shop_code>', methods=['GET', 'POST'])
def customer_print_upload(shop_code):
    shop = Shop.query.filter_by(shop_code=shop_code, is_active=True).first_or_404()

    if request.method == 'POST':
        cust_name = request.form.get('customer_name', '').strip()
        cust_phone = request.form.get('customer_phone', '').strip()
        copies = int(request.form.get('copies', 1) or 1)
        color_type = request.form.get('color_type', 'BW')
        file = request.files.get('document')

        if not cust_name or not cust_phone or not file or file.filename == '':
            flash('Please fill in all details and choose a document.', 'danger')
            return redirect(url_for('main.customer_print_upload', shop_code=shop_code))

        if not allowed_file(file.filename):
            flash('Invalid file format. Allowed: PDF, JPG, PNG, DOCX.', 'danger')
            return redirect(url_for('main.customer_print_upload', shop_code=shop_code))

        order_code = f"PJ-{uuid.uuid4().hex[:6].upper()}"
        saved_filename = f"{order_code}_{secure_filename(file.filename)}"

        upload_folder = os.path.join(current_app.root_path, '..', 'uploads', 'print_jobs')
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, saved_filename))

        rate_per_copy = 10.0 if color_type == 'COLOR' else 3.0
        est_amount = rate_per_copy * copies

        job = PrintJob(
            shop_id=shop.id,
            order_code=order_code,
            customer_name=cust_name,
            customer_phone=cust_phone,
            filename=saved_filename,
            copies=copies,
            color_type=color_type,
            page_type='A4',
            total_amount=est_amount,
            status='PENDING'
        )
        db.session.add(job)
        db.session.commit()

        return render_template('public/print_success.html', shop=shop, job=job)

    return render_template('public/customer_upload.html', shop=shop)
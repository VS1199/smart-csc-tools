from datetime import datetime
import uuid
import io
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from app import db
from app.services.auth_guard import shop_required
from app.models.tenant import Customer, Service, Transaction, PrintJob

shop_bp = Blueprint('shop', __name__, url_prefix='/shop')

@shop_bp.route('/dashboard')
@login_required
@shop_required
def dashboard():
    shop = current_user.shop
    customers_count = Customer.query.filter_by(shop_id=shop.id).count()
    
    income_txns = Transaction.query.filter_by(shop_id=shop.id, txn_type='INCOME').all()
    expense_txns = Transaction.query.filter_by(shop_id=shop.id, txn_type='EXPENSE').all()
    
    total_income = sum(t.amount for t in income_txns)
    total_expense = sum(t.amount for t in expense_txns)
    net_profit = total_income - total_expense
    
    pending_prints = PrintJob.query.filter_by(shop_id=shop.id, status='PENDING').count()
    recent_txns = Transaction.query.filter_by(shop_id=shop.id).order_by(Transaction.created_at.desc()).limit(8).all()
    
    return render_template('shop/dashboard.html',
                           shop=shop,
                           customers_count=customers_count,
                           total_income=total_income,
                           total_expense=total_expense,
                           net_profit=net_profit,
                           pending_prints=pending_prints,
                           recent_txns=recent_txns)

# --- Customer Management Routes ---
@shop_bp.route('/customers', methods=['GET', 'POST'])
@login_required
@shop_required
def customers():
    shop = current_user.shop
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        address = request.form.get('address', '').strip()
        ref_id = request.form.get('masked_id', '').strip()

        if not name or not phone:
            flash('Customer Name and Phone are required.', 'danger')
        else:
            cust = Customer(
                shop_id=shop.id,
                name=name,
                phone=phone,
                email=email,
                address=address,
                masked_id_reference=ref_id
            )
            db.session.add(cust)
            db.session.commit()
            flash('Customer added successfully!', 'success')
            return redirect(url_for('shop.customers'))

    all_customers = Customer.query.filter_by(shop_id=shop.id).order_by(Customer.created_at.desc()).all()
    return render_template('shop/customers.html', customers=all_customers)

# --- Service Catalog Routes ---
@shop_bp.route('/services', methods=['GET', 'POST'])
@login_required
@shop_required
def services():
    shop = current_user.shop
    if request.method == 'POST':
        service_name = request.form.get('service_name', '').strip()
        category = request.form.get('category', 'General')
        price = float(request.form.get('price', 0.0) or 0.0)
        desc = request.form.get('description', '').strip()

        if not service_name:
            flash('Service Name is required.', 'danger')
        else:
            srv = Service(
                shop_id=shop.id,
                service_name=service_name,
                category=category,
                default_price=price,
                description=desc
            )
            db.session.add(srv)
            db.session.commit()
            flash('Service added to your catalog!', 'success')
            return redirect(url_for('shop.services'))

    all_services = Service.query.filter_by(shop_id=shop.id).all()
    return render_template('shop/services.html', services=all_services)

# --- Billing and Receipt Routes ---
@shop_bp.route('/billing/create', methods=['GET', 'POST'])
@login_required
@shop_required
def create_bill():
    shop = current_user.shop
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        service_type = request.form.get('service_type', 'General Service')
        amount = float(request.form.get('amount', 0.0) or 0.0)
        payment_mode = request.form.get('payment_mode', 'CASH')
        payment_status = request.form.get('payment_status', 'COMPLETED')
        notes = request.form.get('notes', '').strip()

        receipt_no = f"RCPT-{shop.shop_code}-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"

        txn = Transaction(
            shop_id=shop.id,
            customer_id=int(customer_id) if customer_id else None,
            receipt_no=receipt_no,
            service_type=service_type,
            amount=amount,
            payment_mode=payment_mode,
            payment_status=payment_status,
            txn_type='INCOME',
            notes=notes
        )
        db.session.add(txn)
        db.session.commit()
        flash('Bill & Receipt created successfully!', 'success')
        return redirect(url_for('shop.view_receipt', receipt_no=receipt_no))

    customers_list = Customer.query.filter_by(shop_id=shop.id).all()
    services_list = Service.query.filter_by(shop_id=shop.id).all()
    return render_template('shop/create_bill.html', customers=customers_list, services=services_list)

@shop_bp.route('/receipt/<receipt_no>')
@login_required
@shop_required
def view_receipt(receipt_no):
    shop = current_user.shop
    txn = Transaction.query.filter_by(shop_id=shop.id, receipt_no=receipt_no).first_or_404()
    return render_template('shop/receipt.html', txn=txn, shop=shop)

# --- Business Manager & Expense Routes ---
@shop_bp.route('/expenses', methods=['GET', 'POST'])
@login_required
@shop_required
def expenses():
    shop = current_user.shop
    if request.method == 'POST':
        expense_title = request.form.get('expense_title', '').strip()
        amount = float(request.form.get('amount', 0.0) or 0.0)
        payment_mode = request.form.get('payment_mode', 'CASH')
        notes = request.form.get('notes', '').strip()

        if not expense_title or amount <= 0:
            flash('Valid Expense Title and Amount are required.', 'danger')
        else:
            exp_no = f"EXP-{shop.shop_code}-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
            txn = Transaction(
                shop_id=shop.id,
                receipt_no=exp_no,
                service_type=expense_title,
                amount=amount,
                payment_mode=payment_mode,
                payment_status='COMPLETED',
                txn_type='EXPENSE',
                notes=notes
            )
            db.session.add(txn)
            db.session.commit()
            flash('Expense recorded successfully!', 'success')
            return redirect(url_for('shop.expenses'))

    all_expenses = Transaction.query.filter_by(shop_id=shop.id, txn_type='EXPENSE').order_by(Transaction.created_at.desc()).all()
    return render_template('shop/expenses.html', expenses=all_expenses)

@shop_bp.route('/reports')
@login_required
@shop_required
def reports():
    shop = current_user.shop
    transactions = Transaction.query.filter_by(shop_id=shop.id).order_by(Transaction.created_at.desc()).all()
    
    total_income = sum(t.amount for t in transactions if t.txn_type == 'INCOME')
    total_expense = sum(t.amount for t in transactions if t.txn_type == 'EXPENSE')
    net_profit = total_income - total_expense

    return render_template('shop/reports.html', 
                           transactions=transactions, 
                           total_income=total_income, 
                           total_expense=total_expense, 
                           net_profit=net_profit)

# --- Excel Report Export ---
@shop_bp.route('/reports/export-excel')
@login_required
@shop_required
def export_excel():
    shop = current_user.shop
    transactions = Transaction.query.filter_by(shop_id=shop.id).order_by(Transaction.created_at.desc()).all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Business Ledger"

    # Header styling
    ws.append([f"Smart CSC Tools - Business Ledger: {shop.shop_name} ({shop.shop_code})"])
    ws.append([f"Report Generated: {datetime.utcnow().strftime('%d-%m-%Y %H:%M UTC')}"])
    ws.append([])

    headers = ["Ref / Receipt No", "Date", "Type", "Particulars / Service", "Amount (₹)", "Payment Mode", "Status", "Notes"]
    ws.append(headers)

    header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")

    for col_num in range(1, len(headers) + 1):
        cell = ws.cell(row=4, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    for t in transactions:
        ws.append([
            t.receipt_no,
            t.created_at.strftime('%d-%m-%Y %H:%M'),
            t.txn_type,
            t.service_type,
            t.amount,
            t.payment_mode,
            t.payment_status,
            t.notes or ""
        ])

    # Auto-adjust column width
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"Ledger_{shop.shop_code}_{datetime.utcnow().strftime('%Y%m%d')}.xlsx"
    return send_file(output, as_attachment=True, download_name=filename, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")# --- Print Queue Management ---
@shop_bp.route('/print-queue')
@login_required
@shop_required
def print_queue():
    shop = current_user.shop
    jobs = PrintJob.query.filter_by(shop_id=shop.id).order_by(PrintJob.created_at.desc()).all()
    return render_template('shop/print_queue.html', shop=shop, jobs=jobs)

@shop_bp.route('/print-queue/download/<int:job_id>')
@login_required
@shop_required
def download_print_file(job_id):
    import os
    from flask import current_app, send_from_directory
    shop = current_user.shop
    job = PrintJob.query.filter_by(id=job_id, shop_id=shop.id).first_or_404()
    upload_folder = os.path.join(current_app.root_path, '..', 'uploads', 'print_jobs')
    return send_from_directory(upload_folder, job.filename, as_attachment=True)

@shop_bp.route('/print-queue/status/<int:job_id>/<new_status>')
@login_required
@shop_required
def update_print_status(job_id, new_status):
    shop = current_user.shop
    job = PrintJob.query.filter_by(id=job_id, shop_id=shop.id).first_or_404()
    if new_status in ['PENDING', 'PRINTED', 'DELIVERED', 'CANCELLED']:
        job.status = new_status
        db.session.commit()
        flash(f'Order {job.order_code} status updated to {new_status}.', 'success')
    return redirect(url_for('shop.print_queue'))
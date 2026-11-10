import io
from datetime import datetime
from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for
from flask_login import login_required
from PIL import Image
import qrcode
from app.services.auth_guard import shop_required

tools_bp = Blueprint('tools', __name__, url_prefix='/shop/tools')

@tools_bp.route('/')
@login_required
@shop_required
def hub():
    return render_template('shop/tools_hub.html')

# --- Tool 1: Image & Signature Resizer / Compressor ---
@tools_bp.route('/image-resizer', methods=['GET', 'POST'])
@login_required
@shop_required
def image_resizer():
    if request.method == 'POST':
        file = request.files.get('image')
        target_kb = request.form.get('target_kb', type=int)
        preset = request.form.get('preset', 'custom')

        if not file or file.filename == '':
            flash('Please select an image file to resize.', 'danger')
            return redirect(url_for('tools.image_resizer'))

        try:
            img = Image.open(file.stream)
            img = img.convert('RGB')

            # Preset dimensions (width, height in px)
            if preset == 'photo':
                img = img.resize((350, 450), Image.Resampling.LANCZOS)
            elif preset == 'signature':
                img = img.resize((300, 120), Image.Resampling.LANCZOS)
            elif preset == 'post_card':
                img = img.resize((400, 600), Image.Resampling.LANCZOS)

            # Target compression loop
            quality = 95
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=quality)

            if target_kb and target_kb > 5:
                target_bytes = target_kb * 1024
                while output.tell() > target_bytes and quality > 10:
                    output = io.BytesIO()
                    quality -= 5
                    img.save(output, format='JPEG', quality=quality)

            output.seek(0)
            return send_file(
                output,
                mimetype='image/jpeg',
                as_attachment=True,
                download_name=f"resized_{preset}_{file.filename.rsplit('.', 1)[0]}.jpg"
            )
        except Exception as e:
            flash(f'Error processing image: {str(e)}', 'danger')
            return redirect(url_for('tools.image_resizer'))

    return render_template('shop/tool_image_resizer.html')

# --- Tool 2: Custom QR Code Generator ---
@tools_bp.route('/qr-generator', methods=['GET', 'POST'])
@login_required
@shop_required
def qr_generator():
    if request.method == 'POST':
        data_text = request.form.get('qr_data', '').strip()
        if not data_text:
            flash('Please enter text or URL for QR code.', 'danger')
            return redirect(url_for('tools.qr_generator'))

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=3,
        )
        qr.add_data(data_text)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        output = io.BytesIO()
        img.save(output, format='PNG')
        output.seek(0)

        return send_file(
            output,
            mimetype='image/png',
            as_attachment=True,
            download_name="smart_csc_qrcode.png"
        )

    return render_template('shop/tool_qr_generator.html')

# --- Tool 3: Age & Eligibility Calculator ---
@tools_bp.route('/age-calculator', methods=['GET', 'POST'])
@login_required
@shop_required
def age_calculator():
    result = None
    if request.method == 'POST':
        dob_str = request.form.get('dob')
        as_on_str = request.form.get('as_on') or datetime.utcnow().strftime('%Y-%m-%d')

        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d')
            as_on = datetime.strptime(as_on_str, '%Y-%m-%d')

            if as_on < dob:
                flash('As-on date must be after Date of Birth.', 'danger')
            else:
                years = as_on.year - dob.year
                months = as_on.month - dob.month
                days = as_on.day - dob.day

                if days < 0:
                    months -= 1
                    days += 30
                if months < 0:
                    years -= 1
                    months += 12

                total_days = (as_on - dob).days
                result = {
                    'years': years,
                    'months': months,
                    'days': days,
                    'total_days': total_days,
                    'dob': dob_str,
                    'as_on': as_on_str
                }
        except ValueError:
            flash('Please provide valid dates in YYYY-MM-DD format.', 'danger')

    return render_template('shop/tool_age_calculator.html', result=result)
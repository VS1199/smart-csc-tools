import os
from app import create_app, db
from app.models.tenant import User, Shop
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()
    # Sabhi centers ko approve karein
    try:
        Shop.query.update({Shop.is_active: True})
        User.query.update({User.is_active: True})
        db.session.commit()
    except Exception as e:
        db.session.rollback()

    # Superadmin password Admin@00009 set karein
    admin = User.query.filter_by(username='superadmin').first()
    new_hash = generate_password_hash('Admin@00009')
    if not admin:
        admin = User(
            username='superadmin',
            email='admin@smartcsc.com',
            password_hash=new_hash,
            role='SUPERADMIN',
            is_active=True
        )
        db.session.add(admin)
    else:
        admin.password_hash = new_hash
        admin.is_active = True
        admin.shop_id = None
    db.session.commit()
    print("Superadmin password updated to Admin@00009")

@app.route('/unlock-now')
def unlock_now():
    try:
        Shop.query.update({Shop.is_active: True})
        User.query.update({User.is_active: True})
        admin_user = User.query.filter_by(username='superadmin').first()
        if admin_user:
            admin_user.password_hash = generate_password_hash('Admin@00009')
            admin_user.is_active = True
            admin_user.shop_id = None
        db.session.commit()
        return "<h1>SUCCESS: Superadmin password set to Admin@00009 and all accounts unlocked!</h1>"
    except Exception as err:
        return f"Error: {err}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

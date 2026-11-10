import os
from app import create_app, db
from app.models.tenant import User, Shop
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()
    
    # Sabhi existing shops aur users ko activate karein
    try:
        Shop.query.update({Shop.is_active: True})
        User.query.update({User.is_active: True})
        db.session.commit()
    except Exception:
        db.session.rollback()

    # Superadmin setup with password Admin@00009
    admin = User.query.filter_by(username='superadmin').first()
    new_hash = generate_password_hash('Admin@00009')
    if not admin:
        admin = User(
            username='superadmin',
            email='admin@smartcsc.com',
            password_hash=new_hash,
            role='SUPERADMIN',
            is_active=True,
            shop_id=None
        )
        db.session.add(admin)
    else:
        admin.password_hash = new_hash
        admin.role = 'SUPERADMIN'
        admin.is_active = True
        admin.shop_id = None
    db.session.commit()
    print("Database ready and Superadmin set to Admin@00009")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

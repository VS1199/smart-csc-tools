import os
from app import create_app, db
from app.models.tenant import User, Shop
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()
    # 1. Sabhi Shops ko active bana do taaki error ka sawal hi na rahe
    try:
        Shop.query.update({Shop.is_active: True})
        User.query.update({User.is_active: True})
        db.session.commit()
    except Exception:
        db.session.rollback()

    # 2. Dummy main shop ensure karo taaki superadmin kisi inactive shop se link na ho
    main_shop = Shop.query.filter_by(center_code='MAIN001').first()
    if not main_shop:
        main_shop = Shop(name="Head Office", center_code="MAIN001", is_active=True)
        db.session.add(main_shop)
        db.session.commit()

    # 3. Superadmin create/update karo
    admin = User.query.filter_by(username='superadmin').first()
    new_hash = generate_password_hash('Admin@00009')
    if not admin:
        admin = User(
            username='superadmin',
            email='admin@smartcsc.com',
            password_hash=new_hash,
            role='SUPERADMIN',
            is_active=True,
            shop_id=main_shop.id
        )
        db.session.add(admin)
    else:
        admin.password_hash = new_hash
        admin.is_active = True
        admin.role = 'SUPERADMIN'
        admin.shop_id = main_shop.id
    db.session.commit()

@app.route('/fix-now')
def fix_now():
    try:
        Shop.query.update({Shop.is_active: True})
        User.query.update({User.is_active: True})
        
        main_shop = Shop.query.filter_by(center_code='MAIN001').first()
        if not main_shop:
            main_shop = Shop(name="Head Office", center_code="MAIN001", is_active=True)
            db.session.add(main_shop)
            db.session.commit()
            
        admin = User.query.filter_by(username='superadmin').first()
        if admin:
            admin.password_hash = generate_password_hash('Admin@00009')
            admin.is_active = True
            admin.role = 'SUPERADMIN'
            admin.shop_id = main_shop.id
            db.session.commit()
            
        return "<h1>SUCCESS! Sabhi Shops Active kar di gayi hain aur Superadmin attach ho gaya hai. Ab /auth/login par direct jayein.</h1>"
    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

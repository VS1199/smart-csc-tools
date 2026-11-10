import os
from app import create_app, db
from app.models.tenant import User, Shop
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Schema refresh: purani mismatch tables ko drop karke nayi schema banana
    try:
        db.drop_all()
        db.create_all()
        print("Database schema successfully recreated!")
    except Exception as e:
        print(f"Schema recreation error: {e}")

    # Superadmin user banayein
    try:
        admin = User(
            username='superadmin',
            email='admin@smartcsc.com',
            password_hash=generate_password_hash('Admin@00009'),
            role='superadmin',
            shop_id=None
        )
        db.session.add(admin)
        db.session.commit()
        print("Superadmin created successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Superadmin setup notice: {e}")

# Direct session reset route
@app.route('/reset-session')
def reset_session():
    from flask_login import logout_user
    logout_user()
    return "<h1>Session Reset Successful! <a href='/auth/login'>Yahan Click Karke Login Karein</a></h1>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

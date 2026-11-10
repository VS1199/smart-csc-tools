import os
from app import create_app, db
from app.models.tenant import User, Shop
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()

    # Ensure Superadmin exists
    try:
        admin = User.query.filter_by(username='superadmin').first()
        if not admin:
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

@app.route('/reset-session')
def reset_session():
    from flask_login import logout_user
    logout_user()
    return "<h1>Session Reset Successful! <a href='/auth/login'>Yahan Click Karke Login Karein</a></h1>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

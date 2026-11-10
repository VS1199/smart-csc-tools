import os
from app import create_app, db
from app.models.tenant import User
from werkzeug.security import generate_password_hash

app = create_app()

# Auto-initialize database and superadmin on startup
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='superadmin').first():
        admin = User(
            username='superadmin',
            email='admin@smartcsc.com',
            password_hash=generate_password_hash('Admin@12345'),
            role='SUPERADMIN',
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Database initialized & Superadmin created!")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

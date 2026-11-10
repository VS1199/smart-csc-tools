import os
from app import create_app, db
from app.models.tenant import User, Shop, Transaction
from werkzeug.security import generate_password_hash
from sqlalchemy import text

app = create_app()

with app.app_context():
    db.create_all()

    # Database schema safe update (PostgreSQL columns check)
    try:
        alter_queries = [
            "ALTER TABLE shops ADD COLUMN IF NOT EXISTS shop_code VARCHAR(50);",
            "ALTER TABLE shops ADD COLUMN IF NOT EXISTS email VARCHAR(120);",
            "ALTER TABLE shops ADD COLUMN IF NOT EXISTS address VARCHAR(255);",
            "ALTER TABLE shops ADD COLUMN IF NOT EXISTS wallet_balance FLOAT DEFAULT 0.0;",
            "ALTER TABLE shops ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active';",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;",
            "ALTER TABLE transactions ADD COLUMN IF NOT EXISTS tx_type VARCHAR(20) DEFAULT 'debit';",
            "ALTER TABLE transactions ADD COLUMN IF NOT EXISTS commission FLOAT DEFAULT 0.0;"
        ]
        for query in alter_queries:
            db.session.execute(text(query))
        
        # Purane 'Wallet Top-Up' records ko credit mark karna taaki kamai me na judein
        db.session.execute(text("UPDATE transactions SET tx_type='credit', commission=0.0 WHERE service_name='Wallet Top-Up';"))
        
        db.session.commit()
        print("Database columns & ledger types verified successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Migration notice: {e}")

    # Superadmin setup
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

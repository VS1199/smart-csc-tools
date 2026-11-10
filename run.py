import os
from app import create_app, db
from app.models.tenant import User, Shop, Transaction
from werkzeug.security import generate_password_hash
from sqlalchemy import text

app = create_app()

with app.app_context():
    db.create_all()

    # Har column ko alag transaction block me add karna taaki ek fail ho toh doosra na ruke
    columns_to_add = [
        ("shops", "shop_code", "VARCHAR(50)"),
        ("shops", "email", "VARCHAR(120)"),
        ("shops", "address", "VARCHAR(255)"),
        ("shops", "wallet_balance", "FLOAT DEFAULT 0.0"),
        ("shops", "status", "VARCHAR(20) DEFAULT 'active'"),
        ("users", "is_active", "BOOLEAN DEFAULT TRUE"),
        ("transactions", "tx_type", "VARCHAR(20) DEFAULT 'debit'"),
        ("transactions", "commission", "FLOAT DEFAULT 0.0")
    ]

    for table, col, col_type in columns_to_add:
        try:
            db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} {col_type};"))
            db.session.commit()
        except Exception:
            db.session.rollback()

    # Purane wallet top-up records ka ledger update
    try:
        db.session.execute(text("UPDATE transactions SET tx_type='credit', commission=0.0 WHERE service_name='Wallet Top-Up';"))
        db.session.commit()
    except Exception:
        db.session.rollback()

    # Superadmin ensure karein
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
    except Exception:
        db.session.rollback()

@app.route('/reset-session')
def reset_session():
    from flask_login import logout_user
    logout_user()
    return "<h1>Session Reset Successful! <a href='/auth/login'>Yahan Click Karke Login Karein</a></h1>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

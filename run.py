import os
from app import create_app, db
from app.models.tenant import User, Shop
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()
    
    # 1. Sabhi registered shops/centers ko automatic ACTIVE approve kar do
    Shop.query.update({Shop.is_active: True})
    User.query.update({User.is_active: True})
    
    # 2. Superadmin ensure karo
    admin = User.query.filter_by(username='superadmin').first()
    if not admin:
        admin = User(
            username='superadmin',
            email='admin@smartcsc.com',
            password_hash=generate_password_hash('Admin@12345'),
            role='SUPERADMIN',
            is_active=True
        )
        db.session.add(admin)
    else:
        admin.password_hash = generate_password_hash('Admin@12345')
        admin.is_active = True
        
    db.session.commit()
    print("All centers approved and Superadmin updated successfully!")

# Direct Instant Auto-Approve URL route
@app.route('/fix-approval')
def fix_approval():
    try:
        Shop.query.update({Shop.is_active: True})
        User.query.update({User.is_active: True})
        db.session.commit()
        return "<h2 style='color:green;text-align:center;margin-top:50px;'>Sabhi Accounts Approve Ho Gaye! <br><br><a href='/auth/login'>Ab Login Karein</a></h2>"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

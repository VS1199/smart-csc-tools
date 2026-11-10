from app import create_app, db
from app.models.tenant import User

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    admin = User(
        username='superadmin',
        email='admin@smartcsc.com',
        role='superadmin',
        is_active=True
    )
    admin.set_password('Admin@12345')
    db.session.add(admin)
    db.session.commit()
    print('Database tables created and Superadmin created successfully!')

from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Shop(db.Model):
    __tablename__ = 'shops'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='active')
    wallet_balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    users = db.relationship('User', backref='shop', lazy=True)
    customers = db.relationship('Customer', backref='shop', cascade="all, delete-orphan", lazy=True)
    services = db.relationship('Service', backref='shop', cascade="all, delete-orphan", lazy=True)
    transactions = db.relationship('Transaction', backref='shop', cascade="all, delete-orphan", lazy=True)
    print_jobs = db.relationship('PrintJob', backref='shop', cascade="all, delete-orphan", lazy=True)

# Compatibility alias
Tenant = Shop

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='vle')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=True)

    # Compatibility: tenant_id points directly to shop_id
    @property
    def tenant_id(self):
        return self.shop_id

    @tenant_id.setter
    def tenant_id(self, val):
        self.shop_id = val

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    customer_name = db.Column(db.String(100), nullable=True)
    service_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='success')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PrintJob(db.Model):
    __tablename__ = 'print_jobs'
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=True)
    pages = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SiteSetting(db.Model):
    __tablename__ = 'site_settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.String(255), nullable=True)

# Compatibility alias
Order = Transaction

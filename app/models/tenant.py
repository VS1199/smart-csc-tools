from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Shop(db.Model):
    __tablename__ = 'shops'
    id = db.Column(db.Integer, primary_key=True)
    shop_code = db.Column(db.String(50), unique=True, nullable=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=True)
    owner_name = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='active')
    wallet_balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    users = db.relationship('User', backref='shop', lazy=True)
    customers = db.relationship('Customer', backref='shop', cascade="all, delete-orphan", lazy=True)
    services = db.relationship('Service', backref='shop', cascade="all, delete-orphan", lazy=True)
    transactions = db.relationship('Transaction', backref='shop', cascade="all, delete-orphan", lazy=True)
    print_jobs = db.relationship('PrintJob', backref='shop', cascade="all, delete-orphan", lazy=True)

    def __init__(self, **kwargs):
        name_val = kwargs.pop('shop_name', None) or kwargs.pop('center_name', None) or kwargs.get('name')
        if name_val:
            kwargs['name'] = name_val
        
        owner_val = kwargs.pop('vle_name', None) or kwargs.get('owner_name')
        if owner_val:
            kwargs['owner_name'] = owner_val

        if 'slug' not in kwargs and 'name' in kwargs and kwargs['name']:
            kwargs['slug'] = kwargs['name'].lower().replace(' ', '-')

        valid_cols = {c.name for c in self.__table__.columns}
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_cols}
        super().__init__(**filtered_kwargs)

    @property
    def is_active(self):
        return self.status == 'active'

    @is_active.setter
    def is_active(self, val):
        self.status = 'active' if val else 'suspended'

Tenant = Shop

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='vle')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=True)

    def __init__(self, **kwargs):
        valid_cols = {c.name for c in self.__table__.columns}
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_cols}
        super().__init__(**filtered_kwargs)

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
    commission = db.Column(db.Float, default=0.0)  # VLE Net Profit
    tx_type = db.Column(db.String(20), default='debit')  # 'credit' (recharge) ya 'debit' (service)
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

    @classmethod
    def get(cls, key, default=None):
        try:
            setting = cls.query.filter_by(key=key).first()
            return setting.value if setting and setting.value is not None else default
        except Exception:
            return default

    @classmethod
    def set(cls, key, value):
        setting = cls.query.filter_by(key=key).first()
        if not setting:
            setting = cls(key=key, value=value)
            db.session.add(setting)
        else:
            setting.value = value
        db.session.commit()

Order = Transaction

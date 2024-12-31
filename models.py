from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(9), unique=True, nullable=False)
    password_hash = db.Column(db.String(13), nullable=False)
    email = db.Column(db.String(18), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False) #管理员
    # 密码加密
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # 验证密码
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(12), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(128))  # img1 for store
    image2 = db.Column(db.String(128)) # img2 for product page
    category = db.Column(db.String(64), nullable=False)
    stock = db.Column(db.Integer, default=200)


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, default=1)
    user = db.relationship('User', backref='cart', lazy=True)
    product = db.relationship('Product', backref='cart', lazy=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total_price = db.Column(db.Float, nullable=False)
    order_status = db.Column(db.String(64), default='Pending')
    user = db.relationship('User', backref='orders', lazy=True)

class UserLike(db.Model):
    __tablename__ = 'user_likes'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)
    user = db.relationship('User', backref=db.backref('liked_products', lazy='dynamic'))
    product = db.relationship('Product', backref=db.backref('liked_by_users', lazy='dynamic'))

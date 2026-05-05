# 用户表
from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import Index, text
from sqlalchemy.sql import expression

from app.plugins import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    wallet = db.Column(db.Float, default=0, nullable=False)
    avatar_url = db.Column(db.String(100))  # 头像
    nickname = db.Column(db.String(50))
    gender = db.Column(db.String(8))
    birthday = db.Column(db.String(20))
    self_statement = db.Column(db.Text)  # 个人简介
    email = db.Column(db.String(100))  # 设置默认值为空字符串而非NULL
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now)
    change_password_at = db.Column(db.DateTime, default=datetime.now)

    # 关联
    books = db.relationship('Book', backref='seller', lazy=True)  # 一个用户可以拥有多本二手书书
    shopping_cart_items = db.relationship('ShoppingCart', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)
    # orders = db.relationship('Order', backref='buyer', lazy=True) # 表示一个用户可以创建多个订单


# 书籍表
class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100))
    publisher = db.Column(db.String(100))
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    picture_url = db.Column(db.String(500))


    # 创建全文索引 (在MySQL中进行配置)
    __table_args__ = (
        Index('idx_book_title_fulltext', 'title', mysql_prefix='FULLTEXT'),  # 按照书籍名称索引
        Index('idx_book_description_fulltext', 'description', mysql_prefix='FULLTEXT'), # 书籍描述索引
        Index('idx_book_author_fulltext', 'author', mysql_prefix='FULLTEXT'), # 按作者
        Index('idx_fulltext_combined', 'title', 'author', 'description', mysql_prefix='FULLTEXT'),
    )


class ShoppingCart(db.Model):

    __tablename__ = 'shopping_cart'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    seller_id = db.Column(db.Integer)
    seller_username = db.Column(db.String(100))

    item_id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    id = db.Column(db.Integer)   # 书的id
    title = db.Column(db.String(100))
    author = db.Column(db.String(100))
    publisher = db.Column(db.String(100))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    picture_url = db.Column(db.String(500))
    chosen = db.Column(db.Boolean, default=False)

# 订单状态枚举
class OrderStatus:
    PENDING_PAYMENT = 'pending_payment'  # 等待支付
    PAID = 'paid'  # 已支付
    EXPIRED = 'expired'   # 超时取消
    CANCELLED = 'cancelled'  # 已取消


# 订单主表 (也可以当成订单历史记录表)
class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)  # 大订单的唯一标识

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))    # 买家id
    user_address = db.Column(db.String(100))
    total_price = db.Column(db.Float, default=None)   # 订单的总价钱
    status = db.Column(db.String(20), default=OrderStatus.PENDING_PAYMENT)  # 订单的状态
    created_at = db.Column(db.DateTime, default=datetime.now)  # 创建订单的时间
    payment_deadline = db.Column(db.DateTime)
    paid_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)

    # 关联, 一个用户可以(创建)拥有多个订单


class ItemStatus:
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    COMPLETED = 'completed'


# 订单明细表
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))  # 这个order_id对应的是Order中的id
    seller_id = db.Column(db.Integer)  # 卖家id
    status = db.Column(db.String(20))
    seller_username = db.Column(db.String(100))
    seller_address = db.Column(db.String(100))
    book_price = db.Column(db.Float)
    book_amount = db.Column(db.Integer)
    book_id = db.Column(db.Integer)
    book_title = db.Column(db.String(100))
    book_author = db.Column(db.String(100))




#     items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")
#     history = db.relationship('OrderHistory', backref='order', lazy=True, cascade="all, delete-orphan")


# # 订单历史记录表（记录订单状态变更）
# class OrderHistory(db.Model):
#     __tablename__ = 'order_history'
#
#     id = db.Column(db.Integer, primary_key=True)
#     order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
#     status = db.Column(db.String(20), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.now)
#     notes = db.Column(db.String(255))
#
# # 订单项表（订单明细）
# class OrderItem(db.Model):
#     __tablename__ = 'order_items'
#
#     id = db.Column(db.Integer, primary_key=True)
#     order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
#     book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
#     quantity = db.Column(db.Integer, default=1, nullable=False)
#     price = db.Column(db.Float, nullable=False)
#
#     # 关联
#     book = db.relationship('Book')





# 创建库存视图
def create_inventory_view():
    db.session.execute(text("""
    CREATE OR REPLACE VIEW book_inventory AS
    SELECT 
        b.id AS book_id,
        b.title,
        b.author,
        b.price,
        b.stock AS total_stock,
        COALESCE(SUM(
            CASE WHEN o.status = 'pending_payment' OR o.status = 'paid' OR o.status = 'shipped' 
            THEN oi.quantity ELSE 0 END
        ), 0) AS reserved_quantity,
        b.stock - COALESCE(SUM(
            CASE WHEN o.status = 'pending_payment' OR o.status = 'paid' OR o.status = 'shipped' 
            THEN oi.quantity ELSE 0 END
        ), 0) AS available_stock
    FROM 
        books b
    LEFT JOIN 
        order_items oi ON b.id = oi.book_id
    LEFT JOIN 
        orders o ON oi.order_id = o.id
    GROUP BY 
        b.id, b.title, b.author, b.price, b.stock;
    """))
    db.session.commit()

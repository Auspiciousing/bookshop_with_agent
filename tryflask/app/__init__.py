from flask import Flask
from app.models import User
from app.order import order_bp
from app.shoppingcart import shoppingcart_bp
from app.book_shop import book_shop_bp
from app.books import book_bp
from app.plugins import init_Plugins, login_manager
from app.login import login_bp
from app.user import user_bp
def create_app():

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root2:123456@localhost/secondhand_books'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_AS_ASCII'] = False
    app.config['MAIL_SERVER'] = 'smtp.163.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = '19194185765@163.com'
    app.config['MAIL_PASSWORD'] = 'YURfb9su82Hy77Tn'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_DEFAULT_SENDER'] = '19194185765@163.com'
    init_Plugins(app)

    app.register_blueprint(login_bp, url_prefix='/login')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(book_bp, url_prefix='/book')
    app.register_blueprint(book_shop_bp,url_prefix='/book_shop')
    app.register_blueprint(shoppingcart_bp, url_prefix='/shoppingcart')
    app.register_blueprint(order_bp, url_prefix='/order')

    # 添加Celery配置
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

    # # 初始化插件（包括Celery）
    # celery = init_Plugins(app)

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

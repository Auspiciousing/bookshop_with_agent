from datetime import datetime

from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from celery import Celery

login_manager = LoginManager()
login_manager.login_view = 'login.login'  # 未登录时跳转的登录路由（蓝图名.视图名）

db = SQLAlchemy()
mail = Mail()
migrate = Migrate()


def make_celery(app):
    """创建Celery实例并配置Flask应用上下文"""
    celery = Celery(
        app.import_name,
        backend='redis://localhost:6379/0',
        broker='redis://localhost:6379/0'
    )

    # 配置Celery
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='Asia/Shanghai',
        enable_utc=True,
    )

    class ContextTask(celery.Task):
        """确保任务在Flask应用上下文中运行"""

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

# Celery实例将在init_Plugins中初始化
celery = None

def init_Plugins(app):
    app.secret_key = '123456'

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)

    celery = make_celery(app)

    @celery.task(name='cancel_unpaid_order')
    def cancel_unpaid_order(order_id):
        """15分钟后检查并取消未支付订单"""
        from app.models import Order  # 在函数内导入避免循环导入

        try:
            print(f"开始处理订单取消任务: {order_id}")
            order = Order.query.get(order_id)

            if not order:
                print(f"订单 {order_id} 不存在")
                return f"订单 {order_id} 不存在"

            print(f"订单 {order_id} 当前状态: {order.status}")

            if order.status == 'pending_payment':
                order.status = 'cancelled'
                order.cancelled_at = datetime.now()
                db.session.commit()
                print(f"订单 {order_id} 已成功取消")
                return f"订单 {order_id} 已成功取消"
            else:
                print(f"订单 {order_id} 状态不是pending_payment，当前状态: {order.status}")
                return f"订单 {order_id} 状态不符合取消条件"

        except Exception as e:
            print(f"取消订单 {order_id} 时出错: {e}")
            db.session.rollback()
            raise e

    return celery




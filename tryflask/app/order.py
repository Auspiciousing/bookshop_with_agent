import threading
from contextlib import contextmanager

from flask import Blueprint, request, jsonify

from app.login_info import login_list
from app.models import User, ShoppingCart, OrderItem, Book, OrderStatus, ItemStatus
from datetime import datetime, timedelta
from app.models import db, Order
# from app.plugins import celery
order_bp = Blueprint('order', __name__)

from app.user import redis_client
from flask import current_app


@contextmanager
def session_scope():
    """提供事务范围的会话管理"""
    session = db.session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"数据库操作失败: {e}")
        raise
    finally:
        session.close()


def handle_expired(app):
    with app.app_context():
        pubsub = redis_client.pubsub()
        pubsub.psubscribe('__keyevent@0__:expired')
        print("开始监听过期键...")

        for message in pubsub.listen():
            if message['type'] == 'pmessage':
                try:
                    expired_key = message['data'].decode('utf-8')
                    print(f"检测到订单过期: {expired_key}")
                    change_status(expired_key)
                except Exception as e:
                    print(f"处理过期键时出错: {e}")


def change_status(key):
    try:
        order_id = int(key)
        with session_scope() as session:
            # 使用with_for_update锁定订单行
            order = session.query(Order).filter_by(id=order_id).with_for_update(nowait=True).first()

            if not order:
                print(f"订单{order_id}不存在！")
                return

            print(f"正在处理订单: {order.id}")

            # 检查是否已处理过
            if order.status == OrderStatus.EXPIRED:
                print(f"订单{order.id}已处理过，跳过")
                return

            # 更新订单状态
            order.status = OrderStatus.EXPIRED

            # 处理订单项和库存
            items = session.query(OrderItem).filter_by(order_id=order.id).all()
            for item in items:
                book = session.query(Book).filter_by(id=item.id).with_for_update(nowait=True).first()
                if book:
                    book.stock += item.book_amount
                    print(f"已恢复书籍{book.id}库存: +{item.book_amount}")

    except Exception as e:
        print(f"处理订单{key}失败: {e}")




# rk = f"123"
# redis_client.setex(rk, 10, "test")

# def handle_expired(app):
#     # 创建pubsub对象
#     with app.app_context():
#         pubsub = redis_client.pubsub()
#
#         # 订阅特定模式的频道：0号数据库的过期事件
#         pubsub.psubscribe('__keyevent@0__:expired')
#
#         print("开始监听过期键...")
#
#         # 持续监听消息
#         for message in pubsub.listen():
#             # 过滤出过期事件
#             if message['type'] == 'pmessage':
#                 expired_key = message['data'].decode('utf-8')
#                 print(f"检测到真实过期键: {expired_key}")
#
#                 change_status(expired_key)
#
#
# def change_status(key):
#
#     print(f"订单{int(key)}已过期, 将会取消订单")
#
#     order = Order.query.filter_by(id=int(key)).first()
#
#     print(order, order.id)
#
#     if order is None:
#         print(f"订单{order.id}不存在！")
#     else:
#         order.status = OrderStatus.EXPIRED
#
#         items = OrderItem.query.filter_by(order_id=order.id).all()
#
#         for i in items:
#
#             book = Book.query.filter_by(id=i.id).first()
#
#             if book:
#
#                 book.stock = book.stock + i.amount
#
#             else:
#
#                 print("book:", book)


@order_bp.post('/new')
def create_order():

    ip_address = request.remote_addr
    result = login_list[ip_address]
    user = User.query.filter_by(id=result).first()

    try:

        payment_deadline = datetime.now() + timedelta(minutes=15)

        item_list = request.get_json()

        print("item_list:", item_list)

        new_order = Order(user_id=user.id, user_address=user.address, payment_deadline=payment_deadline)

        db.session.add(new_order)
        db.session.flush()

        # 将订单ID存入Redis
        redis_key = f"{new_order.id}"
        redis_client.setex(redis_key, 900, "pending")  # 15分钟自动取消

        total = 0

        for i in item_list:

            print("i:", i)

            item = ShoppingCart.query.filter_by(item_id=i['item_id']).first()

            print("item:", item)

            seller = User.query.filter_by(id=item.seller_id).first()

            new_order_item = OrderItem(order_id=new_order.id, seller_id=item.seller_id, seller_username=item.seller_username,
                                       seller_address=seller.address, book_price=item.price, book_amount=i['amount'],
                                       book_id=item.id, book_title=item.title, book_author=item.author)

            book = Book.query.filter_by(id=item.id).first()

            book.stock = book.stock - i['amount']

            db.session.delete(item)
            db.session.add(new_order_item)
            db.session.commit()

            total = total + item.price * i['amount']

        new_order.total_price = total

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': 'success'})

    except Exception as e:

        print("新建订单出错:", e)

        return jsonify({
            'code': 500,
            'message': str(e)
        })


@order_bp.get('/show_unpaid')
def show_unpaid():

    ip_address = request.remote_addr
    result = login_list[ip_address]
    user = User.query.filter_by(id=result).first()

    try:
        orders = Order.query.filter_by(user_id=user.id).all()

        orders_list = []

        for order in orders:

            redis_key = f"{order.id}"

            remaining_seconds = None
            if redis_client.exists(redis_key):
                remaining_seconds = redis_client.ttl(redis_key)


            # if not redis_client.exists(redis_key):
            #     # Redis中不存在，说明已过期
            #     order.status = OrderStatus.CANCELLED
            #     db.session.commit()
            #     db.session.flush()
            # else:
            #     remaining_seconds = redis_client.ttl(redis_key)

            order_items = OrderItem.query.filter_by(order_id=order.id).all()

            items_list = []

            for item in order_items:

                items_list.append({
                    'seller_id': item.seller_id,
                    'seller_username': item.seller_username,
                    'seller_address': item.seller_address,
                    'book_price': item.book_price,
                    'book_amount': item.book_amount,
                    'book_title': item.book_title,
                    'book_author': item.book_author,
                    'status': item.status
                })

            orders_list.append({
                'order_id': order.id,
                'total_price': order.total_price,
                'created_at': order.created_at,
                'status': order.status,
                'payment_deadline': order.payment_deadline,
                'order_items': items_list,
                'remaining_seconds': remaining_seconds
            })

        return jsonify({
            'code': 200,
            'data': orders_list
        })
    except Exception as e:

        print("查询未支付订单发生错误:", e)
        return jsonify({
            'code': 500,
            'message': str(e)
        })


@order_bp.delete('/cancel')
def cancel_order():

    order_id = request.args.get('id')

    try:
        order = Order.query.filter_by(id=order_id).first()

        order.status = OrderStatus.CANCELLED

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': 'success'
        })

    except Exception as e:
        print("取消订单错误:", e)
        return jsonify({
            'code': 500,
            'message': str(e)
        })


@order_bp.get('/show_history_order')
def show_history_order():
    ip_address = request.remote_addr
    result = login_list[ip_address]
    user = User.query.filter_by(id=result).first()

    orders = Order.query.filter_by(user_id=user.id).order_by(Order.id)  # 结果按升序排列

    order_list = []

    for order in orders:
        order_list.append(
            {
                'id': order.id,
                'user_id': order.user_id,
                'seller_id': order.seller_id,
                'user_address': order.user_address,
                'seller_address': order.seller_address,
                'total_price': order.total_price,
                'status': order.status,
                # 'create_time': order.create_time,
                # 'shipped_at': order.shipped_at,
            }
        )

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': order_list
    })


@order_bp.post('/pay')
def pay():

    ip_address = request.remote_addr
    result = login_list[ip_address]
    user = User.query.filter_by(id=result).first()

    order_id = request.form['order_id']

    order = Order.query.filter_by(id=order_id).first()

    try:

        total = order.total_price

        if user.wallet < total:
            return jsonify({
                'code': 500,
                'message': '你的余额不足！'
            })
        else:

            rk = f"{order.id}"

            redis_client.delete(rk)

            user.wallet -= total

            order.status = OrderStatus.PAID

            items = OrderItem.query.filter_by(order_id=order_id).all()

            for item in items:

                item.status = ItemStatus.SHIPPED

            db.session.commit()

            return jsonify({
                'code': 200,
                'message': 'success'
            })
    except Exception as e:
        print("支付发生错误:", e)
        return jsonify({
            'code': 500,
            "message": str(e)
        })

@order_bp.get('/shipping')
def get_shipping():

    ip_address = request.remote_addr
    result = login_list[ip_address]
    user = User.query.filter_by(id=result).first()

    try:

        orders = Order.query.filter_by(user_id=user.id, status=OrderStatus.PAID).all()

        items_list = []

        for order in orders:

            items = OrderItem.query.filter_by(order_id=order.id, status=ItemStatus.SHIPPED).all()

            for item in items:

                items_list.append({
                    'id':item.id,
                    'order_id':order.id,
                    'status': item.status,
                    'seller_username': item.seller_username,
                    'seller_address': item.seller_address,
                    'book_price': item.book_price,
                    'book_amount': item.book_amount,
                    'book_title': item.book_title,
                    'book_author': item.book_author,
                    "total_price": item.book_price * item.book_amount
                })

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': items_list
        })
    except Exception as e:
        print(e)

        return jsonify({
            'code': 500,
            'message': str(e)

        })


@order_bp.post('/confirmReceipt')
def confirmReceipt():

    item_id = request.form.get('id')
    print(item_id)

    item = OrderItem.query.filter_by(id=item_id).first()

    try:

        item.status = ItemStatus.COMPLETED

        db.session.commit()
        db.session.flush()

        return jsonify({
            'code': 200,
            'message': 'success'
        })
    except Exception as e:

        print(e)

        return jsonify({
            'code': 500,
            'message': str(e)
        })

@order_bp.get('/completed')
def completedOrder():

    ip_address = request.remote_addr
    result = login_list[ip_address]
    user = User.query.filter_by(id=result).first()

    try:

        orders = Order.query.filter_by(user_id=user.id, status=OrderStatus.PAID).all()

        items_list = []

        for order in orders:

            items = OrderItem.query.filter_by(order_id=order.id, status=ItemStatus.COMPLETED).all()

            for item in items:
                items_list.append({
                    'order_id': order.id,
                    'status': item.status,
                    'seller_username': item.seller_username,
                    'seller_address': item.seller_address,
                    'book_price': item.book_price,
                    'book_amount': item.book_amount,
                    'book_title': item.book_title,
                    'book_author': item.book_author,
                    "total_price": item.book_price * item.book_amount
                })

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': items_list
        })


    except Exception as e:

        print(e)

        return jsonify({
            'code': 500,
            'message': str(e)
        })






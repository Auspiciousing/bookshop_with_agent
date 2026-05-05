from flask import Blueprint, request, jsonify

from app.login_info import login_list
from app.models import User, Book, ShoppingCart
from app.plugins import db

shoppingcart_bp = Blueprint('shoppingcart', __name__)

@shoppingcart_bp.post('/add_books')
def add_books():
    ip_address = request.remote_addr
    result = login_list[ip_address]

    user = User.query.filter_by(id=result).first()

    book_id = request.form['book_id']
    amount = request.form['book_num']

    item = ShoppingCart.query.filter_by(id=book_id).first()

    if item is None:

        book = Book.query.filter_by(id=book_id).first()

        seller = User.query.filter_by(id=book.seller_id).first()

        if seller.id != user.id:

            new_item = ShoppingCart(user_id=user.id, seller_id=book.seller_id, seller_username=seller.username,
                                    amount=amount, id=book_id, title=book.title, author=book.author, publisher=book.publisher,
                                    description=book.description, price=book.price,
                                    picture_url=book.picture_url)

            db.session.add(new_item)
            db.session.commit()

            return jsonify({

                'code': 200,
                'message': 'success'

            })
        else:
            return jsonify({
                'code':500,
                'message':'您不能购买自己出售的商品'
            })
    else:
        return jsonify({
            'code': 500,
            'message': '已经在购物车中了'
        })


@shoppingcart_bp.get('/show_shoppingcart')
def show_shoppingcart():
    ip_address = request.remote_addr
    result = login_list[ip_address]

    user = User.query.filter_by(id=result).first()

    items = ShoppingCart.query.filter_by(user_id=user.id)

    item_list = []

    for item in items:

        book = Book.query.filter_by(id=item.id).first()

        stock = book.stock

        item_list.append({
            'user_id': item.user_id,
            'seller_id': item.seller_id,
            'seller_username': item.seller_username,

            'item_id': item.item_id,

            'amount': item.amount,
            'stock': stock,
            'id': item.id,
            'title': item.title,
            'author': item.author,
            'publisher': item.publisher,
            'description': item.description,
            'price': item.price,
            'picture_url': item.picture_url,
            'chosen': item.chosen,
            'loaded': False,
            'valid': True
        })

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': item_list
    })


@shoppingcart_bp.post('/shoppingcart_info')
def modify_amount():

    print(1123445678)

    data = request.get_json()

    print(data)

    print("123", "456")

    for x in data:

        item_id = x['item_id']

        item = ShoppingCart.query.filter_by(item_id=item_id).first()

        item.amount = x['amount']

        db.session.commit()

    return jsonify({
        'code': 200,
        'message': 'success'
    })


@shoppingcart_bp.route('/refresh', methods=['POST', 'OPTIONS'])
def refresh():

    if request.method == 'OPTIONS':
        # 设置必要的 CORS 响应头
        response = jsonify({'code': 200, 'message': 'OK'})
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        # response.headers.add('Access-Control-Max-Age', '3600')  # 预检请求缓存时间
        return response

        # 处理实际的 POST 请求
    try:
        # 获取请求中的数据
        data = request.get_json()
        if not data:
            return jsonify({'code': 400, 'message': '没有接收到数据'})

        print(f"收到购物车数据: {data}")

        # 在这里处理购物车数据
        # 例如保存到数据库等...

        return jsonify({'code': 200, 'message': '购物车更新成功'})
    except Exception as e:
        print(f"处理购物车数据时出错: {str(e)}")
        return jsonify({'code': 500, 'message': f'服务器错误: {str(e)}'})


@shoppingcart_bp.post('/delete')
def delete_item():

    item_id_list = request.get_json()

    print(item_id_list)

    try:
        for item_id in item_id_list:

            print(item_id)

            item = ShoppingCart.query.filter_by(item_id=item_id).first()

            print(item)

            if item is None:
                return jsonify({
                    'code': 404,
                    'message': 'Book not found'})

            # 删除记录
            db.session.delete(item)
            db.session.commit()

        return jsonify({
            'code': 200,
            'message': 'success'})
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({
            'code': 500,
            'message': 'failed'})



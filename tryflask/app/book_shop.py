from flask import Blueprint, request, jsonify, send_from_directory
import os

from uuid import uuid4
import re
from sqlalchemy import text, or_, func, and_
import json
from app.models import User, Book
from app.plugins import db
from app.login_info import login_list
from app.user import redis_client

book_shop_bp = Blueprint('book_shop', __name__)

###########################################################################

books_list = []

is_search = False

idx = None


# 下面用于展示商城
@book_shop_bp.get('/show')
def show_all_books():
    print("show")
    global is_search
    global idx
    if is_search:

        global books_list

        is_search = False

        idx = min(8, len(books_list))

        return jsonify({
            'code': 200,
            'message': 'success',
            'data': books_list[0:idx],
            'append_length': idx
        })

    else:

        try:
            # 查询所有书籍
            books = Book.query.filter(Book.stock != 0).all()

            # global books_list

            books_list = []

            for book in books:
                seller = User.query.filter_by(id=book.seller_id).first()

                books_list.append({
                    'seller_id': book.seller_id,
                    'seller_username': seller.username,
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'publisher': book.publisher,
                    'description': book.description,
                    'price': book.price,
                    'stock': book.stock,
                    'picture_url': book.picture_url,
                    'loaded': False
                })


            idx = min(8, len(books_list))

            print(books_list)

            # 返回JSON响应
            return jsonify({
                'code': 200,
                'message': 'success',
                'data': books_list[0:idx],
                'append_length':idx
            })
        except Exception as e:
            print(11111111111)
            print(e)
            return jsonify({
                'code': 500,
                'message': str(e),
                'data': None
            })


@book_shop_bp.get('/show_append')
def show_all_books_append():
    global idx
    try:
        if idx + 4 <= len(books_list):
            idx = idx + 4
            return jsonify({
                'code': 200,
                'message': 'success',
                'data': books_list[idx - 4:idx],
                'append_length':4,
                'end':False
            })
        else:
            length = len(books_list[idx:])
            a = jsonify({
                'code': 200,
                'message': 'success',
                'data': books_list[idx:],
                'append_length':length,
                'end':True
            })
            idx = len(books_list)
            return a
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': str(e),
            'data': None
        }), 500


# 商城查询
@book_shop_bp.post('/search')
def search_book():
    search_query = request.form.get('search', '').strip()
    print(search_query)
    terms = search_query.split()
    search_term = ' '.join([f'{term}*' for term in terms])

    try:
        sql = text("""
               SELECT *, 
                 (MATCH(title) AGAINST(:search IN BOOLEAN MODE)) +
                 (MATCH(author) AGAINST(:search IN BOOLEAN MODE)) +
                 (MATCH(description) AGAINST(:search IN BOOLEAN MODE)) AS relevance
               FROM books
               WHERE 
                 MATCH(title) AGAINST(:search IN BOOLEAN MODE) OR
                 MATCH(author) AGAINST(:search IN BOOLEAN MODE) OR
                 MATCH(description) AGAINST(:search IN BOOLEAN MODE)
               ORDER BY relevance DESC
           """)
        result = db.session.execute(sql, {"search": search_term})

        # 构建响应
        global books_list

        books_list = []

        for book in result:
            print(book.id)

            print(book.seller_id)

            seller = User.query.filter_by(id=book.seller_id).first()

            print(seller)

            books_list.append({
                'seller_id': book.seller_id,
                'seller_username': seller.username,
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'publisher': book.publisher,
                'description': book.description,
                'price': book.price,
                'stock': book.stock,
                'picture_url': book.picture_url,
                'loaded': False,
                'imagekey':None
            })

        global is_search

        is_search = True

        return jsonify({
            'code': 200,
            'message': 'success'
        })
    except Exception as e:
        print("搜索时发生错误:", e)
        return jsonify({
            'code': 500,
            'message': str(e)
        })


@book_shop_bp.post('/blur_search')
def blur_search():
    try:
        # 获取搜索参数
        search_query = request.form.get('search', '').strip()

        if not search_query:
            return jsonify({'error': '请求数据不能为空'}), 400

        # # 生成缓存键
        # cache_key = f"book_search:{search_query}"
        #
        # # 尝试从Redis缓存中获取结果
        # try:
        #     cached_result = redis_client.get(cache_key)
        #     if cached_result:
        #         return jsonify(json.loads(cached_result))
        # except Exception as redis_error:
        #     print(f"Redis缓存读取失败: {redis_error}")

        # 模糊搜索：在标题、作者、描述中搜索
        search_terms = list(search_query.strip())

        # 构造 OR 查询：每个字都用 ilike 匹配
        like_filters = [Book.title.ilike(f"%{term}%") |
                        Book.author.ilike(f"%{term}%") |
                        Book.description.ilike(f"%{term}%") for term in search_terms]

        # 合并多个 OR 条件
        search_filter = and_(*like_filters)

        # 查询
        search_results = Book.query.filter(search_filter).filter(Book.stock > 0).all()

        # 构建返回数据
        global books_list

        books_list = []

        for book in search_results:

            seller = User.query.filter_by(id=book.seller_id).first()

            books_list.append({
                'seller_id': book.seller_id,
                'seller_username': seller.username,
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'publisher': book.publisher,
                'description': book.description,
                'price': book.price,
                'stock': book.stock,
                'picture_url': book.picture_url,
                'loaded': False,
                'imagekey':None
            })
        global is_search

        is_search = True

        print("book_list:", books_list)

        return jsonify({
            'code': 200,
            'message': '恩情！'
        })

        # try:
        #     result_data = {
        #         'code': 200,
        #         'books': books_list,
        #         'total': len(books_list)
        #     }
        #     # redis_client.setex(cache_key, 300, json.dumps(result_data))  # 缓存5分钟
        #
        #
        #
        # except Exception as redis_error:
        #     print(f"Redis缓存写入失败: {redis_error}")

    except Exception as e:
        print(e)
        return jsonify({
            'code': 500,
            'message': str(e)
        })

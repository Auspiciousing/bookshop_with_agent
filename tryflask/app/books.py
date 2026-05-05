import click
from flask import Blueprint, request, jsonify, send_from_directory
import os

from uuid import uuid4

from app.models import User, Book
from app.plugins import db
from app.login_info import login_list

book_bp = Blueprint('book', __name__)

@book_bp.post('/new')
# 新建售卖书籍
def add_books():

    ip_address = request.remote_addr
    print(ip_address)
    result = login_list[ip_address]
    print(result)

    user = User.query.filter_by(id=result).first()

    title = request.form.get('title')
    author = request.form.get('author')
    publisher = request.form.get('publisher')
    description = request.form.get('description')
    price = request.form.get('price')
    stock = request.form.get('stock')
    picture_url = request.form.get('picture_url')

    seller_id = user.id

    new_book = Book(title=title, author=author, publisher=publisher, description=description,
                    price=price, stock=stock, picture_url=picture_url, seller_id=seller_id)

    db.session.add(new_book)
    db.session.commit()

    return jsonify({'code': 200,
                    'message': 'success'})


# 用于显示我的售卖
@book_bp.get('/self/on_sale')
def my_books_on_sale():
    ip_address = request.remote_addr
    print(ip_address)
    result = login_list[ip_address]
    print(result)

    user = User.query.filter_by(id=result).first()

    # 在Book表中依据book.seller_id寻找当前这个seller正在售卖的书籍有哪些，返回这些书籍的信息
    if user:
        # 查询该用户（seller）正在售卖的所有书籍
        books = Book.query.filter_by(seller_id=user.id).all()

        # 将查询结果转换为可序列化的格式
        books_data = []
        for book in books:
            book_info = {
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'publisher': book.publisher,
                'description': book.description,
                'price': book.price,
                'stock': book.stock,
                'picture_url':book.picture_url
            }
            books_data.append(book_info)

        return jsonify({
            'code': 200,
            'message': 'success',
            'books_data': books_data
        })
    else:
        return jsonify({'code': 400, 'message': 'User not found'})

@book_bp.post('/modify_books_on_sale')
def modify_my_books_on_sale():

    # 首先要知道是哪一本书
    book_id = request.form.get('id')

    print(book_id)

    book = Book.query.filter_by(id=book_id).first()

    book.title = request.form.get('title')
    book.author = request.form.get('author')
    book.publisher = request.form.get('publisher')
    book.description = request.form.get('description')
    book.price = request.form.get('price')
    book.stock = request.form.get('stock')
    book.picture_url = request.form.get('picture_url')

    # 保存更改
    try:
        db.session.commit()
        return jsonify({'code': 200, 'message': '书籍信息更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'更新失败: {str(e)}'})



@book_bp.delete('/delete_book')
def delete_book():

    book_id = request.args.get('id')

    # 查询要删除的书籍
    book = Book.query.get(book_id)
    print(book_id)
    print(book)

    try:

        if book is None:
            return jsonify({
                'code':404,
                'message': 'Book not found'})

        # 删除记录
        db.session.delete(book)
        db.session.commit()

        return jsonify({
            'code': 200,
            'message': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'code': 500,
            'message': 'failed'})


# 配置上传目录
UPLOAD_FOLDER = r"F:\VS CODE\new\tryflask\app\static\img"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@book_bp.post('/upload')
def upload():

    book_id = request.form.get('id')

    book = Book.query.filter_by(id=book_id).first()

    print('接收到上传请求')
    file = request.files.get('file')
    print(file)

    if not file:
        print('未接收到文件')
        return jsonify({
            'code': 400,
            'message': '未接收到文件'
        }), 400

    # 生成唯一文件名，避免覆盖
    ext = file.filename.rsplit('.', 1)[1] if '.' in file.filename else ''
    unique_filename = f"{uuid4().hex}.{ext}" if ext else uuid4().hex

    # # 提取文件扩展名（转换为小写统一格式）
    # ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    # # 使用 book_id 作为主文件名
    # unique_filename = f"{book_id}.{ext}" if ext else str(book_id)

    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    try:
        # 保存文件
        file.save(file_path)
        print(f'文件已保存: {file_path}')

        # 构建正确的URL
        server_url = "http://192.168.122.168:5000"
        file_url = f"{server_url}/book/{unique_filename}"

        print(file_url)

        book.picture_url = file_url

        print("book_id:",book_id)
        print("book_picture_url:",book.picture_url)

        db.session.commit()

        book = Book.query.filter_by(id=book_id).first()

        print("222book_picture_url:", book.picture_url)

        return jsonify({
            'code': 200,
            'message': '上传成功',
            'data': {
                'url': file_url,
                'original_filename': file.filename
            }
        }),200
    except Exception as e:
        print(f'文件保存失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': '文件保存失败'
        }), 500


@book_bp.route('/<path:filename>')
def serve_static(filename):
    print("图片返回")
    return send_from_directory(UPLOAD_FOLDER, filename)











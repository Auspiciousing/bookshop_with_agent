from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user
from sqlalchemy import or_

from app.models import User
from app.plugins import db
from app.login_info import login_list

login_bp = Blueprint('login', __name__)


@login_bp.post('/')
def login():

    login_name = request.form.get('username')
    login_password = request.form.get('password')

    print(login_name, login_password)

    user = User.query.filter(
        or_(
            User.username == login_name,
            User.email == login_name
        )
    ).first()

    if user and user.password == login_password:
        print(login_name, login_password)
        print(user.username,user.email, user.password)

        ip_address = request.remote_addr

        login_list[ip_address] = user.id
        # login_user(user)

        return jsonify({
            'id': user.nickname,
            'code': 200,
            'message': '成功登录！'
        })
    else:
        return jsonify({'code': 500})


@login_bp.post('/register')
def register():
    username = request.form.get('username')
    password = request.form.get('password')

    # 数据验证
    if not all([username, password]):
        return jsonify({'code': 400, 'message': '用户名、和密码为必填项！'})

    # 检查唯一性约束
    if User.query.filter_by(username=username).first():
        return jsonify({'code': 409, 'message': '用户名已被占用！'})

    print(username)
    print(password)

    new_user = User(username=username, password=password, email="", created_at=datetime.now(),
                    change_password_at=datetime.now())
    db.session.add(new_user)
    db.session.commit()

    print("插入成功！")
    return jsonify({
        'code': 200,
        'message': '注册成功！',
        'user': {
            'id': new_user.id,
            'username': new_user.username,
        }
    })

@login_bp.post('/logout')
def logout():
    logout_user()
    return jsonify({'code': 200})
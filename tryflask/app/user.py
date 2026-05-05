import os
from datetime import datetime
import random
import string
from uuid import uuid4

from flask import Blueprint, request, jsonify, send_from_directory
from flask_mail import Message

from app.models import User
from app.plugins import db, mail
from app.login_info import login_list
import redis

user_bp = Blueprint('user', __name__)


def get_user_from_login_list():
    ip_address = request.remote_addr
    user_id = login_list.get(ip_address)
    if not user_id:
        return None, (jsonify({'code': 401, 'message': 'Not logged in'}), 401)

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return None, (jsonify({'code': 404, 'message': 'User not found'}), 404)

    return user, None

@user_bp.post('/changepassword')
def change_password():
    id = request.form.get('userid')
    old_password = request.form.get('old_password')

    print("1111")
    print(id, old_password)

    user = User.query.filter_by(id=id).first()

    if user.password == old_password:

        new_password = request.form.get('new_password')

        # 修改为新密码
        user.password = new_password
        user.change_password_at = datetime.now()

        # 保存更改到数据库
        db.session.commit()

        print("success")

        return jsonify({
            'code': 200,
            'message': '密码修改成功！'
        })
    else:
        return jsonify({'code': 500,
                        'message': '原密码错误！'})


@user_bp.get('/account')
def account_info():
    user, error = get_user_from_login_list()
    if error:
        return error

    return jsonify({'code': 200,
                    'message': 'success',
                    'change_password_at': user.change_password_at,
                    'phone': user.phone,
                    'email': user.email,
                    })


@user_bp.get('/self')
def get_self_info():
    user, error = get_user_from_login_list()
    if error:
        return error

    return jsonify({
        'code': 200,
        'message': 'success',
        'avatar_url': user.avatar_url,
        'username': user.username,
        'nickname': user.nickname,
        'gender': user.gender,
        'phone': user.phone,
        'email': user.email,
        'birthday': user.birthday,
        'self_statement': user.self_statement,
        'address': user.address
        # 'wallet': user.wallet

    })


@user_bp.post('/self')
def change_self_info():
    user, error = get_user_from_login_list()
    if error:
        return error

    # data = request.get_json()

    # userInfo = request.form.get('userInfo')
    new_username = request.form.get('username')
    new_avatar_url = request.form.get('avatar_url')
    new_nickname = request.form.get('nickname')
    new_gender = request.form.get('gender')
    new_phone = request.form.get('phone')
    new_birthday = request.form.get('birthday')
    new_self_statement = request.form.get('self_statement')
    new_address = request.form.get('address')

    user.username = new_username
    user.avatar_url = new_avatar_url
    user.nickname = new_nickname
    user.gender = new_gender
    user.phone = new_phone
    user.birthday = new_birthday
    user.self_statement = new_self_statement
    user.address = new_address

    db.session.commit()

    return jsonify({
        'code': 200,
        'message': 'success',
    })


# 邮箱验证码
# Redis配置，用于存储验证码
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
VERIFICATION_CODE_EXPIRY = 300

# 初始化redis连接
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

def generate_verification_code(length=6):
    """生成指定长度的数字验证码"""
    return ''.join(random.choices(string.digits, k=length))


def send_verification_code(email):
    """生成验证码，保存到Redis并发送邮件"""
    code = generate_verification_code()

    print(code)

    # 将验证码保存到Redis，设置过期时间
    redis_key = f"verification_code:{email}"
    redis_client.setex(redis_key, VERIFICATION_CODE_EXPIRY, code)

    # 邮件内容
    subject = "您的验证码"
    body = f"""
    <html>
    <body>
        <h2>验证码</h2>
        <p>您好！</p>
        <p>您的验证码是：<strong style="font-size: 20px; color: #FF0000;">{code}</strong></p>
        <p>该验证码将在5分钟内有效。如果不是您本人操作，请忽略此邮件。</p>
        <p>谢谢！</p>
    </body>
    </html>
    """

    # 使用Flask-Mail发送邮件
    try:
        print(11111111111111)
        msg = Message(
            subject=subject,
            recipients=[email],
            html=body
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"发送邮件失败: {e}")
        return False


def verify_code(email, code):
    """验证用户提交的验证码是否正确"""
    redis_key = f"verification_code:{email}"
    stored_code = redis_client.get(redis_key)

    if stored_code is None:
        return False

    # 将bytes类型转换为字符串进行比较
    stored_code = stored_code.decode('utf-8')

    # 验证成功后删除验证码，防止重复使用
    if stored_code == code:
        redis_client.delete(redis_key)
        return True

    return False

@user_bp.post('/email')
def email_verification():
    ip_address = request.remote_addr
    # print(ip_address)
    result = login_list[ip_address]
    # print(result)

    user = User.query.filter_by(id=result).first()

    new_email = request.form.get('email')

    flag = send_verification_code(new_email)

    if flag:

        return jsonify({
            'code': 200,
            'message': 'success',
        })

    else:
        return jsonify({'code': 400,
                        'message': 'Failed'})

@user_bp.post('/email/verify')
def verify_verification_code():
    user, error = get_user_from_login_list()
    if error:
        return error

    new_email = request.form.get('email')
    verification_code = request.form.get('verification_code')

    if verify_code(new_email, verification_code):

        print(new_email)

        user.email = new_email

        print(user.email)

        # 保存更改到数据库
        db.session.commit()

        return jsonify({
            'code': 200,
            'message': 'success',
        })

    else:
        return jsonify({
            'code': 500
        })

@user_bp.get('/wallet')
def get_wallet():
    user, error = get_user_from_login_list()
    if error:
        return error

    return jsonify({
        'code': 200,
        'message': 'success',
        'balance': user.wallet,
        'avatar': user.avatar_url
    })

@user_bp.post('/recharge')
def recharge():
    user, error = get_user_from_login_list()
    if error:
        return error

    amount = request.form.get('money')

    user.wallet += float(amount)

    db.session.commit()


    return jsonify({
        'code': 200,
        'message': 'success',
        'balance': user.wallet + float(amount)
    })


UPLOAD_FOLDER = r"F:\VS CODE\new\tryflask\app\static\img"

@user_bp.post('/avatar')
def avatar():
    user, error = get_user_from_login_list()
    if error:
        return error

    print('接收到上传请求')
    file = request.files.get('avatar')
    print(file)

    if not file:
        print('未接收到文件')
        return jsonify({
            'code': 400,
            'message': '未接收到文件'
        }), 400

    ext = file.filename.rsplit('.', 1)[1] if '.' in file.filename else ''
    unique_filename = f"{uuid4().hex}.{ext}" if ext else uuid4().hex

    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    try:
        # 保存文件
        file.save(file_path)
        print(f'文件已保存: {file_path}')

        # 构建正确的URL
        server_url = "http://192.168.122.168:5000"
        file_url = f"{server_url}/user/{unique_filename}"

        print(file_url)

        user.avatar_url = file_url

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '上传成功',
            'data': {
                'url': file_url,
                'original_filename': file.filename
            }
        })
    except Exception as e:
        print(f'文件保存失败: {str(e)}')
        return jsonify({
            'code': 500,
            'message': '文件保存失败'
        }), 500

@user_bp.route('/<path:filename>')
def serve_static(filename):
    print("图片返回")
    return send_from_directory(UPLOAD_FOLDER, filename)
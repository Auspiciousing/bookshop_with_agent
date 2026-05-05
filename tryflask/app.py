import threading

from flask_cors import CORS

from app import create_app
from app.order import handle_expired

app = create_app()

CORS(app)

# 启动监听线程
listener_thread = threading.Thread(target=handle_expired, args=(app,))
listener_thread.daemon = True  # 设置为守护线程
listener_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    # app.run(host='::', port=5000, debug=True)




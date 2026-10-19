import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import DevelopmentConfig, TestingConfig

db = SQLAlchemy()

app = Flask(__name__)

env = os.environ.get('FLASK_ENV', 'development')

if env == 'testing':
    app.config.from_object(TestingConfig)
else:
    app.config.from_object(DevelopmentConfig)

db.init_app(app)

# 临时验证接口，确认服务起来了
@app.route('/health')
def health():
    return {'code': 0, 'msg': 'ok', 'env': env}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
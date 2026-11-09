"""应用工厂：按环境装载配置、注册扩展与蓝图。

保留原 /health 健康检查接口，新增 /api/v1 业务路由。
"""

import os

from flask import Flask, jsonify

from config import DevelopmentConfig, TestingConfig
from .extensions import db


def create_app(config_object=None) -> Flask:
    app = Flask(__name__)

    if config_object is not None:
        app.config.from_object(config_object)
    else:
        env = os.environ.get('FLASK_ENV', 'development')
        if env == 'testing':
            app.config.from_object(TestingConfig)
        else:
            app.config.from_object(DevelopmentConfig)

    db.init_app(app)

    from . import models  # noqa: F401  确保模型注册到 metadata
    from .api import api_bp

    app.register_blueprint(api_bp)

    @app.get('/health')
    def health():
        return jsonify({'code': 0, 'msg': 'ok', 'env': app.config.get('ENV', 'development')})

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({'code': 404, 'msg': '接口不存在', 'data': None}), 404

    @app.errorhandler(500)
    def server_error(_error):
        db.session.rollback()
        return jsonify({'code': 500, 'msg': '服务器内部错误', 'data': None}), 500

    @app.cli.command('init-db')
    def init_db():
        """初始化数据库表：flask init-db"""
        db.create_all()
        print('数据表已创建')

    return app

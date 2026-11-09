"""路由注册入口：所有蓝图统一挂到 /api/v1 下。"""

from flask import Blueprint

from . import auth, dispatch, help_order, notify

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

api_bp.register_blueprint(auth.bp)
api_bp.register_blueprint(help_order.bp)
api_bp.register_blueprint(dispatch.bp)
api_bp.register_blueprint(notify.bp)

__all__ = ['api_bp']

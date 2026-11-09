"""轻量令牌与角色校验。

骨架阶段使用 Flask 自带依赖 itsdangerous 签发带过期时间的令牌，
避免额外引入 PyJWT；后续如需刷新令牌、多端登录，再切换为 JWT 方案。
"""

from functools import wraps

from flask import current_app, g, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from ..extensions import db
from .response import fail

TOKEN_MAX_AGE = 7 * 24 * 3600  # 7 天


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt='qq-token')


def issue_token(user_id: int) -> str:
    return _serializer().dumps({'uid': user_id})


def decode_token(token: str) -> int | None:
    try:
        data = _serializer().loads(token, max_age=TOKEN_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None
    return data.get('uid')


def login_required(view):
    """从 Authorization: Bearer <token> 解析当前用户，注入 g.current_user。"""

    from ..models import User

    @wraps(view)
    def wrapper(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        token = auth[7:] if auth.startswith('Bearer ') else ''
        uid = decode_token(token)
        if not uid:
            return fail('未登录或登录已过期', code=401, http_status=401)
        user = db.session.get(User, uid)
        if not user:
            return fail('用户不存在', code=401, http_status=401)
        g.current_user = user
        return view(*args, **kwargs)

    return wrapper


def role_required(*roles: str):
    """限定可访问的角色，如 @role_required(Role.RESCUER)。"""

    def decorator(view):
        @wraps(view)
        @login_required
        def wrapper(*args, **kwargs):
            if g.current_user.role not in roles:
                return fail('当前角色无权访问', code=403, http_status=403)
            return view(*args, **kwargs)

        return wrapper

    return decorator

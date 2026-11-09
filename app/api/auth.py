"""认证与账号：注册、登录、当前用户信息、救护员资质提交。"""

from flask import Blueprint, g, request

from ..extensions import db
from ..models import CertType, RescuerProfile, Role, User, VerifyStatus
from ..utils.auth import issue_token, login_required, role_required
from ..utils.response import fail, ok

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.post('/register')
def register():
    """手机号 + 密码注册。role=rescuer 时同步创建待审核的救护员档案。"""
    body = request.get_json(silent=True) or {}
    phone = (body.get('phone') or '').strip()
    password = body.get('password') or ''
    role = body.get('role') or Role.FAMILY

    if not phone or len(phone) < 11:
        return fail('请填写正确的手机号')
    if len(password) < 6:
        return fail('密码至少 6 位')
    if role not in Role.ALL:
        return fail('角色不合法')
    if User.query.filter_by(phone=phone).first():
        return fail('该手机号已注册')

    user = User(
        phone=phone,
        name=(body.get('name') or '').strip(),
        role=role,
        address=body.get('address') or '',
        latitude=body.get('latitude'),
        longitude=body.get('longitude'),
        bound_elder_id=body.get('bound_elder_id'),
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    if role == Role.RESCUER:
        db.session.add(
            RescuerProfile(
                user_id=user.id,
                cert_type=body.get('cert_type') or CertType.RED_CROSS,
                cert_no=body.get('cert_no') or '',
                cert_image_url=body.get('cert_image_url') or '',
                verify_status=VerifyStatus.PENDING,
            )
        )

    db.session.commit()
    return ok({'user': user.to_dict(), 'token': issue_token(user.id)}, msg='注册成功')


@bp.post('/login')
def login():
    body = request.get_json(silent=True) or {}
    phone = (body.get('phone') or '').strip()
    password = body.get('password') or ''

    user = User.query.filter_by(phone=phone).first()
    if not user or not user.check_password(password):
        return fail('手机号或密码错误', code=401)

    return ok({'user': user.to_dict(), 'token': issue_token(user.id)}, msg='登录成功')


@bp.get('/me')
@login_required
def me():
    data = g.current_user.to_dict()
    if g.current_user.role == Role.RESCUER and g.current_user.rescuer_profile:
        data['rescuer_profile'] = g.current_user.rescuer_profile.to_dict()
    return ok(data)


@bp.post('/rescuer/location')
@role_required(Role.RESCUER)
def update_rescuer_location():
    """救护员上报位置与在线状态，供就近调度使用。"""
    body = request.get_json(silent=True) or {}
    profile = g.current_user.rescuer_profile
    if not profile:
        return fail('救护员档案不存在')

    profile.latitude = body.get('latitude', profile.latitude)
    profile.longitude = body.get('longitude', profile.longitude)
    if 'online' in body:
        profile.online = bool(body['online'])
    if 'service_radius_km' in body:
        profile.service_radius_km = float(body['service_radius_km'])

    from datetime import datetime, timezone

    profile.location_updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return ok(profile.to_dict())

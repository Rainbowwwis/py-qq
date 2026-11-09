"""求助工单：敲击/语音触发 → AI 分级 → 进入调度。"""

from datetime import datetime, timezone

from flask import Blueprint, g, request

from ..extensions import db
from ..models import HelpOrder, OrderStatus, Role, TriggerType, User
from ..services.ai_service import grade_emergency
from ..utils.auth import login_required
from ..utils.response import fail, ok

bp = Blueprint('order', __name__, url_prefix='/orders')


@bp.post('')
@login_required
def create_order():
    """创建求助工单。老人本人或绑定家属均可发起，坐标缺失时回落到账号地址。"""
    body = request.get_json(silent=True) or {}
    user = g.current_user

    elder_id = body.get('elder_id') or (user.id if user.role == Role.ELDER else user.bound_elder_id)
    if not elder_id:
        return fail('缺少老人账号信息，请先绑定家属关系')

    elder = db.session.get(User, elder_id)
    if not elder:
        return fail('老人账号不存在')

    latitude = body.get('latitude') or elder.latitude
    longitude = body.get('longitude') or elder.longitude
    if latitude is None or longitude is None:
        return fail('缺少定位信息，无法派单')

    trigger_type = body.get('trigger_type') or TriggerType.KNOCK
    if trigger_type not in TriggerType.ALL:
        return fail('触发方式不合法')

    transcript = body.get('transcript') or ''
    signals = body.get('signals') or {}
    graded = grade_emergency(transcript=transcript, signals=signals)

    order = HelpOrder(
        elder_id=elder.id,
        creator_id=user.id,
        trigger_type=trigger_type,
        level=graded['level'],
        status=OrderStatus.DISPATCHING,
        address=body.get('address') or elder.address,
        latitude=float(latitude),
        longitude=float(longitude),
        ai_transcript=transcript,
        ai_summary=graded['summary'],
        need_120=graded['need_120'],
    )
    db.session.add(order)
    db.session.commit()

    return ok({'order': order.to_dict(), 'ai': graded}, msg='求助已发出')


@bp.get('')
@login_required
def list_orders():
    """我发起或与我绑定的工单列表，按创建时间倒序。"""
    user = g.current_user
    query = HelpOrder.query
    if user.role == Role.ELDER:
        query = query.filter(HelpOrder.elder_id == user.id)
    elif user.role == Role.FAMILY:
        query = query.filter(HelpOrder.creator_id == user.id)
    else:
        query = query.filter(HelpOrder.creator_id == user.id)

    orders = query.order_by(HelpOrder.created_at.desc()).limit(50).all()
    return ok([order.to_dict() for order in orders])


@bp.get('/<int:order_id>')
@login_required
def get_order(order_id: int):
    order = db.session.get(HelpOrder, order_id)
    if not order:
        return fail('工单不存在', code=404)
    data = order.to_dict()
    data['dispatches'] = [record.to_dict() for record in order.dispatches]
    return ok(data)


@bp.post('/<int:order_id>/cancel')
@login_required
def cancel_order(order_id: int):
    order = db.session.get(HelpOrder, order_id)
    if not order:
        return fail('工单不存在', code=404)
    if order.status in (OrderStatus.FINISHED, OrderStatus.CANCELLED):
        return fail('当前状态不可取消')
    order.status = OrderStatus.CANCELLED
    order.finished_at = datetime.now(timezone.utc)
    db.session.commit()
    return ok(order.to_dict(), msg='已取消')

"""就近派单：候选救护员查询、呼叫、接单、到达、完成。"""

from datetime import datetime, timezone

from flask import Blueprint, g, request

from ..extensions import db
from ..models import (
    DispatchRecord,
    DispatchStatus,
    HelpOrder,
    NotificationLog,
    NotifyChannel,
    OrderStatus,
    RescuerProfile,
    Role,
)
from ..services.dispatch_service import find_candidates
from ..utils.auth import login_required, role_required
from ..utils.response import fail, ok

bp = Blueprint('dispatch', __name__, url_prefix='/dispatch')


@bp.get('/orders/<int:order_id>/candidates')
@login_required
def candidates(order_id: int):
    """查看该工单附近可调度的救护员（家属端/机构端用于确认调度情况）。"""
    order = db.session.get(HelpOrder, order_id)
    if not order:
        return fail('工单不存在', code=404)

    limit = int(request.args.get('limit', 5))
    return ok(find_candidates(order.latitude, order.longitude, limit=limit))


@bp.post('/orders/<int:order_id>/call')
@login_required
def call_rescuers(order_id: int):
    """向最近的 N 名救护员发起呼叫，写入派单记录。"""
    order = db.session.get(HelpOrder, order_id)
    if not order:
        return fail('工单不存在', code=404)
    if order.status not in (OrderStatus.PENDING, OrderStatus.DISPATCHING):
        return fail('当前工单状态不可派单')

    body = request.get_json(silent=True) or {}
    limit = int(body.get('limit', 3))
    found = find_candidates(order.latitude, order.longitude, limit=limit)
    if not found:
        return fail('附近暂无可调度的救护员，请尝试联系家属或 120')

    created = []
    for item in found:
        exists = DispatchRecord.query.filter_by(
            order_id=order.id, rescuer_id=item['rescuer_id']
        ).first()
        if exists:
            continue
        record = DispatchRecord(
            order_id=order.id,
            rescuer_id=item['rescuer_id'],
            distance_km=item['distance_km'],
            status=DispatchStatus.OFFERED,
        )
        db.session.add(record)
        created.append(item)

    order.status = OrderStatus.DISPATCHING
    db.session.commit()
    return ok({'called': created}, msg=f'已呼叫 {len(created)} 名救护员')


@bp.post('/<int:dispatch_id>/accept')
@role_required(Role.RESCUER)
def accept(dispatch_id: int):
    record = db.session.get(DispatchRecord, dispatch_id)
    if not record:
        return fail('派单不存在', code=404)
    if record.rescuer_id != g.current_user.id:
        return fail('这不是你的派单', code=403)
    if record.status != DispatchStatus.OFFERED:
        return fail('该派单已不可接单')

    record.status = DispatchStatus.ACCEPTED
    record.responded_at = datetime.now(timezone.utc)

    order = record.order
    order.status = OrderStatus.ACCEPTED
    order.accepted_at = datetime.now(timezone.utc)

    # 接单后向家属推送
    db.session.add(
        NotificationLog(
            order_id=order.id,
            receiver_id=order.creator_id,
            receiver_desc='家属',
            channel=NotifyChannel.WECHAT,
            content=f'救护员已接单，正在赶往现场（距您约 {record.distance_km:.1f} 公里）',
            success=True,
        )
    )
    db.session.commit()
    return ok(record.to_dict(), msg='接单成功')


@bp.post('/<int:dispatch_id>/arrive')
@role_required(Role.RESCUER)
def arrive(dispatch_id: int):
    record = db.session.get(DispatchRecord, dispatch_id)
    if not record or record.rescuer_id != g.current_user.id:
        return fail('派单不存在', code=404)
    if record.status != DispatchStatus.ACCEPTED:
        return fail('当前状态不可标记到达')

    record.order.status = OrderStatus.ARRIVED
    record.order.arrived_at = datetime.now(timezone.utc)
    db.session.commit()
    return ok(record.order.to_dict(), msg='已标记到达')


@bp.post('/<int:dispatch_id>/finish')
@role_required(Role.RESCUER)
def finish(dispatch_id: int):
    record = db.session.get(DispatchRecord, dispatch_id)
    if not record or record.rescuer_id != g.current_user.id:
        return fail('派单不存在', code=404)

    record.status = DispatchStatus.FINISHED
    order = record.order
    order.status = OrderStatus.FINISHED
    order.finished_at = datetime.now(timezone.utc)

    profile = RescuerProfile.query.filter_by(user_id=g.current_user.id).first()
    if profile:
        profile.finished_orders += 1

    db.session.commit()
    return ok(order.to_dict(), msg='服务已完成')

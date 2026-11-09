"""三方通知：家属、社区机构、120 的触达记录。

骨架阶段只落库，不真实外呼/发短信；接入微信订阅消息、阿里云短信、
语音外呼后可在此文件内补实现，接口形态保持不变。
"""

from flask import Blueprint, request

from ..extensions import db
from ..models import (
    HelpOrder,
    NotificationLog,
    NotifyChannel,
    OrderLevel,
)
from ..utils.auth import login_required
from ..utils.response import fail, ok

bp = Blueprint('notify', __name__, url_prefix='/notify')


@bp.post('/orders/<int:order_id>')
@login_required
def notify(order_id: int):
    """按分级触发三方通知：L3 通知 120，全部等级通知家属，机构端可见。"""
    order = db.session.get(HelpOrder, order_id)
    if not order:
        return fail('工单不存在', code=404)

    body = request.get_json(silent=True) or {}
    channels = body.get('channels') or [NotifyChannel.WECHAT]
    logs = []

    targets = [('家属', order.creator_id)]
    if order.need_120 or order.level == OrderLevel.L3:
        targets.append(('120', None))

    for desc, receiver_id in targets:
        for channel in channels:
            log = NotificationLog(
                order_id=order.id,
                receiver_id=receiver_id,
                receiver_desc=desc,
                channel=channel,
                content=f'{desc}通知：老人求助（分级 {order.level}），地址 {order.address}',
                # TODO: 接入真实通道后按返回结果置为 True
                success=False,
            )
            db.session.add(log)
            logs.append(log)

    db.session.commit()
    return ok([log.to_dict() for log in logs], msg='通知已记录')


@bp.get('/orders/<int:order_id>')
@login_required
def list_notifications(order_id: int):
    logs = (
        NotificationLog.query.filter_by(order_id=order_id)
        .order_by(NotificationLog.created_at.desc())
        .all()
    )
    return ok([log.to_dict() for log in logs])

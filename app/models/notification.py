"""三方通知记录：家属、社区/机构、120 的触达与结果留痕。"""

from datetime import datetime, timezone

from ..extensions import db


class NotifyChannel:
    SMS = 'sms'
    WECHAT = 'wechat'     # 微信小程序订阅消息
    PUSH = 'push'
    CALL = 'call'         # 电话外呼（120 / 家属）
    ALL = (SMS, WECHAT, PUSH, CALL)


class NotificationLog(db.Model):
    __tablename__ = 'notification_log'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('help_order.id'), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    receiver_desc = db.Column(db.String(64), default='')   # 如 "120"、"家属-张女士"

    channel = db.Column(db.String(20), nullable=False, default=NotifyChannel.WECHAT)
    content = db.Column(db.Text, default='')
    success = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'order_id': self.order_id,
            'receiver_id': self.receiver_id,
            'receiver_desc': self.receiver_desc,
            'channel': self.channel,
            'content': self.content,
            'success': self.success,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

"""求助工单：由敲击/语音/手动触发，经 AI 分级后进入调度流程。"""

from datetime import datetime, timezone

from ..extensions import db


class TriggerType:
    KNOCK = 'knock'      # 连续敲击触发（核心创新点）
    VOICE = 'voice'      # 语音召唤
    MANUAL = 'manual'    # 家属或老人手动点击
    ALL = (KNOCK, VOICE, MANUAL)


class OrderLevel:
    L1 = 'L1'   # 非紧急，仅需确认与陪伴
    L2 = 'L2'   # 紧急但暂不需要 120，派救护员上门
    L3 = 'L3'   # 危重，立即通知 120 + 家属 + 就近救护员
    ALL = (L1, L2, L3)


class OrderStatus:
    PENDING = 'pending'        # 已创建，等待 AI 分级/派单
    DISPATCHING = 'dispatching'  # 正在寻找并呼叫救护员
    ACCEPTED = 'accepted'      # 已有救护员接单
    ARRIVED = 'arrived'        # 救护员已到达
    FINISHED = 'finished'      # 服务完成
    CANCELLED = 'cancelled'    # 已取消
    ALL = (PENDING, DISPATCHING, ACCEPTED, ARRIVED, FINISHED, CANCELLED)


class HelpOrder(db.Model):
    __tablename__ = 'help_order'

    id = db.Column(db.Integer, primary_key=True)
    elder_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    trigger_type = db.Column(db.String(20), nullable=False, default=TriggerType.KNOCK)
    level = db.Column(db.String(4), nullable=False, default=OrderLevel.L2, index=True)
    status = db.Column(db.String(20), nullable=False, default=OrderStatus.PENDING, index=True)

    # 现场信息：老人端自动上报，不依赖老人自己描述
    address = db.Column(db.String(255), default='')
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    # AI 收集与判断结果
    ai_transcript = db.Column(db.Text, default='')      # ASR 转写
    ai_summary = db.Column(db.Text, default='')         # 大模型摘要，供救护员接单前查看
    need_120 = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), index=True)
    accepted_at = db.Column(db.DateTime)
    arrived_at = db.Column(db.DateTime)
    finished_at = db.Column(db.DateTime)

    dispatches = db.relationship('DispatchRecord', backref='order', lazy='dynamic')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'elder_id': self.elder_id,
            'trigger_type': self.trigger_type,
            'level': self.level,
            'status': self.status,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'ai_summary': self.ai_summary,
            'need_120': self.need_120,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

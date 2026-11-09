"""派单记录：一条工单可向多名救护员发起呼叫，逐一记录响应结果。"""

from datetime import datetime, timezone

from ..extensions import db


class DispatchStatus:
    OFFERED = 'offered'        # 已推送，等待响应
    ACCEPTED = 'accepted'      # 已接单
    REJECTED = 'rejected'      # 拒单
    TIMEOUT = 'timeout'        # 超时未响应
    FINISHED = 'finished'      # 服务完成
    ALL = (OFFERED, ACCEPTED, REJECTED, TIMEOUT, FINISHED)


class DispatchRecord(db.Model):
    __tablename__ = 'dispatch_record'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('help_order.id'), nullable=False, index=True)
    rescuer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)

    distance_km = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(20), nullable=False, default=DispatchStatus.OFFERED, index=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    responded_at = db.Column(db.DateTime)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'order_id': self.order_id,
            'rescuer_id': self.rescuer_id,
            'distance_km': round(self.distance_km, 2),
            'status': self.status,
        }

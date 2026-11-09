"""持证救护员档案：资质审核、接单半径、在线状态与评分。"""

from datetime import datetime

from ..extensions import db


class VerifyStatus:
    PENDING = 'pending'        # 已提交，待审核
    APPROVED = 'approved'      # 审核通过，可接单
    REJECTED = 'rejected'      # 审核驳回
    ALL = (PENDING, APPROVED, REJECTED)


class CertType:
    RED_CROSS = 'red_cross'            # 红十字救护员证
    NURSE = 'nurse'                    # 护士执业资格证
    DOCTOR = 'doctor'                  # 医师执业资格证
    AHA = 'aha'                        # AHA BLS/ACLS
    OTHER = 'other'
    ALL = (RED_CROSS, NURSE, DOCTOR, AHA, OTHER)


class RescuerProfile(db.Model):
    __tablename__ = 'rescuer_profile'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

    cert_type = db.Column(db.String(20), nullable=False, default=CertType.RED_CROSS)
    cert_no = db.Column(db.String(64), default='')
    cert_image_url = db.Column(db.String(255), default='')
    verify_status = db.Column(db.String(20), nullable=False, default=VerifyStatus.PENDING, index=True)

    # 调度参数：在线状态 + 接单半径（公里）+ 当前坐标
    online = db.Column(db.Boolean, nullable=False, default=False, index=True)
    service_radius_km = db.Column(db.Float, nullable=False, default=3.0)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    location_updated_at = db.Column(db.DateTime)

    # 评价与履约数据，用于派单排序与后续计酬
    rating = db.Column(db.Float, nullable=False, default=5.0)
    finished_orders = db.Column(db.Integer, nullable=False, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.user.name if self.user else '',
            'cert_type': self.cert_type,
            'verify_status': self.verify_status,
            'online': self.online,
            'service_radius_km': self.service_radius_km,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'rating': self.rating,
            'finished_orders': self.finished_orders,
        }

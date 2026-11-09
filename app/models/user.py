"""用户与角色模型。

一个手机号对应一个账号，通过 role 区分四类使用者：
elder（老人）/ family（家属）/ rescuer（持证救护员）/ org（机构、社区、志愿服务组织）。
"""

from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db


class Role:
    ELDER = 'elder'
    FAMILY = 'family'
    RESCUER = 'rescuer'
    ORG = 'org'
    ALL = (ELDER, FAMILY, RESCUER, ORG)


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(50), default='')
    role = db.Column(db.String(20), nullable=False, default=Role.FAMILY, index=True)

    # 适老化字段：老人端只需要极少信息即可注册，地址与坐标用于就近调度
    address = db.Column(db.String(255), default='')
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    # 家属/机构与老人的绑定关系
    bound_elder_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    rescuer_profile = db.relationship(
        'RescuerProfile', backref='user', uselist=False, cascade='all, delete-orphan'
    )

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'phone': self.phone,
            'name': self.name,
            'role': self.role,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'bound_elder_id': self.bound_elder_id,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f'<User {self.id} {self.phone} {self.role}>'

"""时间戳默认值回归测试：default 必须是延迟求值的可调用对象，
确保每条记录记录的是插入时刻，而不是应用启动时刻。"""

import time
from datetime import datetime, timezone

from app.extensions import db
from app.models import User


def test_created_at_is_insert_time(app):
    with app.app_context():
        u1 = User(phone='13700000001', role='family', name='a')
        u1.set_password('x' * 8)
        db.session.add(u1)
        db.session.commit()

        time.sleep(1.1)  # 保证两次插入的 UTC 秒数不同

        u2 = User(phone='13700000002', role='family', name='b')
        u2.set_password('x' * 8)
        db.session.add(u2)
        db.session.commit()

        assert u1.created_at < u2.created_at, (
            'created_at 被固化成了同一个时间（default 在类定义时求值）'
        )

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        assert (now - u2.created_at).total_seconds() < 60

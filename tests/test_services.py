"""调度与 AI 分级的单元测试。"""

from app.extensions import db
from app.models import RescuerProfile, User, VerifyStatus
from app.services.ai_service import grade_emergency
from app.services.dispatch_service import find_candidates, haversine_km


def test_haversine_same_point_is_zero():
    assert haversine_km(23.13, 113.26, 23.13, 113.26) == 0


def test_haversine_known_distance():
    # 广州到深圳约 100 公里量级
    distance = haversine_km(23.13, 113.26, 22.54, 114.06)
    assert 90 < distance < 120


def test_grade_emergency_levels():
    assert grade_emergency('胸口有点疼')['level'] == 'L2'
    assert grade_emergency('老人倒地昏迷了')['need_120'] is True
    assert grade_emergency('')['level'] == 'L2'


def test_find_candidates_filters_by_radius(app):
    near = User(phone='13900000001', role='rescuer', name='近的救护员')
    near.set_password('x' * 8)
    far = User(phone='13900000002', role='rescuer', name='远的救护员')
    far.set_password('x' * 8)
    db.session.add_all([near, far])
    db.session.flush()

    db.session.add_all(
        [
            RescuerProfile(
                user_id=near.id, verify_status=VerifyStatus.APPROVED, online=True,
                latitude=23.131, longitude=113.261, service_radius_km=5,
            ),
            RescuerProfile(
                user_id=far.id, verify_status=VerifyStatus.APPROVED, online=True,
                latitude=23.30, longitude=113.40, service_radius_km=5,
            ),
        ]
    )
    db.session.commit()

    found = find_candidates(23.13, 113.26, limit=5)
    assert [item['rescuer_id'] for item in found] == [near.id]

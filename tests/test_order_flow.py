"""核心链路冒烟测试：注册 → 家属绑定老人 → 敲击触发工单 → AI 分级。"""


def _register(client, phone, role, **extra):
    body = {'phone': phone, 'password': 'test123456', 'role': role, 'name': phone, **extra}
    return client.post('/api/v1/auth/register', json=body).get_json()


def test_register_and_login(client):
    data = _register(client, '13800000001', 'family')
    assert data['code'] == 0
    assert data['data']['token']

    login = client.post(
        '/api/v1/auth/login', json={'phone': '13800000001', 'password': 'test123456'}
    ).get_json()
    assert login['code'] == 0

    wrong = client.post(
        '/api/v1/auth/login', json={'phone': '13800000001', 'password': 'bad-pass'}
    ).get_json()
    assert wrong['code'] == 401


def test_knock_order_flow(client):
    elder = _register(
        client, '13800000002', 'elder', latitude=23.13, longitude=113.26, address='测试地址'
    )['data']
    family = _register(client, '13800000003', 'family', bound_elder_id=elder['user']['id'])['data']

    resp = client.post(
        '/api/v1/orders',
        json={'trigger_type': 'knock', 'signals': {'knock_count': 3}},
        headers={'Authorization': f"Bearer {family['token']}"},
    ).get_json()

    assert resp['code'] == 0
    order = resp['data']['order']
    assert order['status'] == 'dispatching'
    assert order['level'] == 'L2'
    assert '连续敲击 3 次' in order['ai_summary']


def test_critical_transcript_escalates_to_l3(client):
    elder = _register(client, '13800000004', 'elder', latitude=23.13, longitude=113.26)['data']
    family = _register(client, '13800000005', 'family', bound_elder_id=elder['user']['id'])['data']

    resp = client.post(
        '/api/v1/orders',
        json={'trigger_type': 'voice', 'transcript': '我爸突然晕倒了，没有呼吸'},
        headers={'Authorization': f"Bearer {family['token']}"},
    ).get_json()

    order = resp['data']['order']
    assert order['level'] == 'L3'
    assert order['need_120'] is True

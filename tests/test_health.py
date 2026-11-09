def test_health(client):
    resp = client.get('/health')
    assert resp.status_code == 200
    assert resp.get_json()['msg'] == 'ok'


def test_unknown_api_returns_json_404(client):
    resp = client.get('/api/v1/not-exist')
    assert resp.status_code == 404
    assert resp.get_json()['code'] == 404

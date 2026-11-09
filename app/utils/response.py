"""统一响应格式，前端只需处理 {code, msg, data} 一种结构。"""

from flask import jsonify


def ok(data=None, msg: str = 'ok'):
    return jsonify({'code': 0, 'msg': msg, 'data': data})


def fail(msg: str, code: int = 400, http_status: int = 200):
    """业务失败统一用 HTTP 200 + 业务 code，便于小程序端统一处理。"""
    return jsonify({'code': code, 'msg': msg, 'data': None}), http_status

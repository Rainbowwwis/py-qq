# 04 API 接口文档

> Base URL：`/api/v1`　格式：JSON　鉴权：`Authorization: Bearer <token>`
> 统一响应：`{"code": 0, "msg": "ok", "data": {...}}`；业务失败 code 非 0；鉴权失败 HTTP 401。

## 1. 认证与账号 `/auth`

| 方法 | 路径 | 权限 | 说明 |
| --- | --- | --- | --- |
| POST | `/auth/register` | 公开 | 手机号+密码注册；`role=rescuer` 时同步创建待审核档案 |
| POST | `/auth/login` | 公开 | 登录，返回 token 与用户信息 |
| GET | `/auth/me` | 登录 | 当前用户信息（救护员附带档案） |
| POST | `/auth/rescuer/location` | 救护员 | 上报位置/在线状态/接单半径 |

注册请求示例：

```json
POST /api/v1/auth/register
{
  "phone": "13800000001",
  "password": "test123456",
  "role": "rescuer",
  "name": "张救护",
  "cert_type": "red_cross",
  "cert_no": "RC2026xxxx"
}
```

## 2. 求助工单 `/orders`

| 方法 | 路径 | 权限 | 说明 |
| --- | --- | --- | --- |
| POST | `/orders` | 老人/家属 | 创建工单（核心接口，见下） |
| GET | `/orders` | 登录 | 我的工单列表（最近 50 条） |
| GET | `/orders/{id}` | 登录 | 工单详情（含派单记录） |
| POST | `/orders/{id}/cancel` | 登录 | 取消 |

**创建工单**（敲击触发时由硬件/小程序自动调用，老人无感知）：

```json
POST /api/v1/orders
{
  "trigger_type": "knock",          // knock 敲击 / voice 语音 / manual 手动
  "signals": {"knock_count": 3, "fall_detected": false},
  "transcript": "",                 // ASR 转写，可为空
  "latitude": 23.130, "longitude": 113.260
}
```

返回：工单对象 + AI 分级结果（`level / need_120 / summary / reason`），工单状态为 `dispatching`，可直接进入派单。

## 3. 就近派单 `/dispatch`

| 方法 | 路径 | 权限 | 说明 |
| --- | --- | --- | --- |
| GET | `/dispatch/orders/{id}/candidates` | 登录 | 附近可调度救护员（距离+评分排序） |
| POST | `/dispatch/orders/{id}/call` | 登录 | 向最近 N 名救护员发起呼叫，生成派单记录 |
| POST | `/dispatch/{dispatch_id}/accept` | 救护员 | 接单（工单转 accepted，通知家属） |
| POST | `/dispatch/{dispatch_id}/arrive` | 救护员 | 标记到达 |
| POST | `/dispatch/{dispatch_id}/finish` | 救护员 | 完成服务（累计接单数） |

呼叫返回示例：

```json
{
  "code": 0, "msg": "已呼叫 2 名救护员",
  "data": {
    "called": [
      {"rescuer_id": 7, "name": "张救护", "distance_km": 1.2, "rating": 4.9},
      {"rescuer_id": 12, "name": "李救护", "distance_km": 2.4, "rating": 4.7}
    ]
  }
}
```

## 4. 三方通知 `/notify`

| 方法 | 路径 | 权限 | 说明 |
| --- | --- | --- | --- |
| POST | `/notify/orders/{id}` | 登录 | 触发通知：家属必达；`need_120=true` 或 L3 时包含 120 |
| GET | `/notify/orders/{id}` | 登录 | 该工单的通知记录（留痕审计） |

> 骨架阶段通知仅落库（`success=false`，接口形态不变）；接入微信订阅消息 / 短信 / 语音外呼后按通道返回结果更新。

## 5. 其他

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/health` | 服务健康检查（部署探针） |
| — | `flask --app run init-db` | 初始化数据表 |

## 6. 错误码约定

| code | 含义 |
| --- | --- |
| 0 | 成功 |
| 400 | 参数/业务校验失败 |
| 401 | 未登录或令牌过期 |
| 403 | 角色无权操作 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误（自动回滚事务） |

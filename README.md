
# 快速开始

**克隆仓库到本地**
git clone https://github.com/Rainbowwwis/py-qq.git

## 第一步：配置 Docker 镜像加速
打开 Docker Desktop -> 右上角齿轮 Settings -> Docker Engine。
在右侧 JSON 配置的最后加上 `"registry-mirrors"`（注意前后要加逗号），改成类似这样：
```json
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false,
  "registry-mirrors": [
    "https://docker.xuanyuan.me",
    "https://docker.1ms.run",
    "https://docker.m.daocloud.io"
  ]
}
点击右下角 Apply & Restart，等小鲸鱼图标变绿（不再闪烁）。

## 第二步：启动后端容器
在项目根目录下（和 docker-compose.yml 同级），打开终端执行：

bash
docker compose up -d --build
看到全屏绿色的 ✔ 并且没有 ERROR，就说明启动成功了。

✅ 第三步：测试是否跑通
开发环境测试：浏览器访问 http://127.0.0.1:5000/health

测试环境测试：浏览器访问 http://127.0.0.1:5001/health

如果浏览器返回类似 {"code": 0, "msg": "ok", "env": "development"}，说明你已经成功跑通了！

# 敲敲救 后端 - 快速启动

先克隆仓库。拿到代码后的本地操作步骤

虽然代码在 Docker 里跑，但为了他们在 VS Code 里写代码时**不报错、有提示**，拉取代码后必须执行以下三步（这在我的 `README.md` 里也有写，但你可以口头再强调一下）：

1.  **打开终端，进入项目目录**
2.  **创建并激活本地虚拟环境**：
    ```bash
    python -m venv .venv
    .venv\Scripts\activate  # Windows系统
    ```
3.  **安装 Python 依赖**：
    ```bash
    pip install -r requirements.txt
    ```
4.  **让 VS Code 选中这个虚拟环境**：按 `Ctrl+Shift+P`，输入 `Python: Select Interpreter`，选择带 `.venv` 的那个路径。

欢迎加入后端开发！请按照以下三步操作，即可在本地跑通开发环境。

## 第一步：配置 Docker 镜像加速

打开 Docker Desktop -> 右上角齿轮 **Settings** -> 左侧选择 **Docker Engine**。
在右侧的 JSON 配置中，找到最后的 `"experimental": false`，在它下面加上逗号并插入 `"registry-mirrors"` 字段，修改后如下所示：

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
```

修改完成后，点击右下角的 **Apply & Restart**，等待 Docker Desktop 重启（右下角小鲸鱼图标不再闪烁，变成静止状态）。

## 第二步：启动后端容器

在终端中进入项目根目录（确保该目录下有 `docker-compose.yml` 文件），执行以下命令一键构建并后台启动：

```bash
docker compose up -d --build
```

> **提示**：首次构建可能需要几分钟。看到终端打印出全屏绿色的 `✔`，且没有红色的 `ERROR` 报错，就说明容器已成功启动。

## 第三步：测试是否跑通

容器启动完成后，打开浏览器，分别访问以下两个地址：

- **开发环境测试**： [http://127.0.0.1:5000/health](http://127.0.0.1:5000/health)
- **测试环境测试**： [http://127.0.0.1:5001/health](http://127.0.0.1:5001/health)

> **检验标准**：如果浏览器页面返回类似 `{"code": 0, "msg": "ok", "env": "development"}` 的 JSON 数据，恭喜你，环境已经成功跑通了！
> 
> **注意**：复制完之后，检查一下代码块。正常渲染出来的代码块右上角会有“复制”按钮，左上角**只会显示 json 或 bash**（或者什么都不显示），不会把外围的 markdown 符号也带出来。如果显示异常，说明复制的时候不小心把最外层的三个反引号带进去了，删掉即可。

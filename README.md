# 敲敲救 后端 - 快速启动

## 项目简介

「敲敲救」——基于多模态识别的 AI 应急响应与救护员调度平台。老人连敲三下即可触发求助，AI 收集信息并分级（L1 陪护 / L2 派就近救护员 / L3 同步 120），持证救护员按距离与评分就近接单，全程通知家属并留痕。

**当前进度（2026-11 中期）**：后端骨架已完成——用户/救护员/工单/派单/通知五个模块、AI 分级服务、就近调度服务、9 个 pytest 用例全部通过。AI 分级暂用关键词规则，待接入 LLM/ASR。

**文档**（`docs/` 目录）：

- [01 需求分析报告](docs/01-需求分析报告.md) —— 基于 141 份问卷的调研结论与功能映射
- [02 系统架构说明](docs/02-系统架构说明.md) —— 架构图、核心时序、技术选型
- [03 数据库设计](docs/03-数据库设计.md) —— ER 图与表设计
- [04 API 接口文档](docs/04-API接口文档.md) —— 全部接口的请求/响应示例

**本地开发（不用 Docker 跑测试）**：

```bash
pip install -r requirements-dev.txt
pytest -q        # 应显示 9 passed
```

---

以下为团队成员首次上手的完整环境配置指南。

先克隆仓库。拿到代码后的本地操作步骤

虽然代码在 Docker 里跑，但为了他们在 VS Code 里写代码时**不报错、有提示**，拉取代码后必须执行以下三步：

1.  **打开终端，进入项目根目录**
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

**准备工作结束！随后正片开始~**
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

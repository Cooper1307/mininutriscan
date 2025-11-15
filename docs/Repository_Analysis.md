# MiniNutriScan 仓库全面分析（简明版）

## 项目总览
- 路径 `d:\MyData\projects\mininutriscan`
- 子项目：Python 后端（FastAPI）、微信小程序、Android 客户端（Jetpack Compose + CameraX）、脚本与文档
- 数据存储：PostgreSQL（SQLAlchemy + Alembic），缓存：Redis

## 结构树状图（核心代码与配置）
- app/
  - api/
    - `__init__.py`（聚合路由）
    - `auth.py`（认证与 JWT）
    - `detection.py`（图片/手动/条码检测）
    - `reports.py`（营养报告）
    - `education.py`（教育内容）
    - `volunteers.py`（志愿者）
    - `statistics.py`（统计）
    - `community.py`（社区功能）
    - `sessions.py`（会话接口）
  - core/
    - `config.py`（环境与服务配置）
    - `database.py`（PostgreSQL/Redis 连接、缓存工具）
    - `validators.py`（OCR/营养/AI/响应验证与清洗）
  - models/
    - `user.py`、`detection.py`、`report.py`、`volunteer.py`、`education.py`
  - services/
    - `ai_service.py`（Qwen AI）
    - `ocr_service.py`（腾讯/阿里 OCR）
    - `session_service.py`（Redis 会话）
    - `wechat_service.py`（微信登录与 API）
- main.py（后端主入口）
- web_app.py（FastAPI 模板版 Web UI）
- app.py（旧版 Flask Web）
- migrations/（Alembic 迁移）
- miniprogram/
  - config/api.js（小程序 API 配置）
  - pages/*（页面逻辑：如 detection）
  - utils/*（网络请求与工具）
- app/src/main/java/com/mininutriscan/app/
  - `MainActivity.kt`、`navigation/AppNavigation.kt`、`ui/screen/*`
- tests（测试脚本集合）
- 启动与检查脚本：`启动所有服务.bat`、`检查项目状态.py` 等

## 关键业务与核心技术栈
- 后端：FastAPI + SQLAlchemy + Alembic + Redis
  - 认证与用户：`app/api/auth.py`（JWT）、`app/models/user.py`
  - 检测流程：`app/api/detection.py` 调用 `OCRService` 与 `AIService`，并写入 `Detection` 模型
  - 报告生成：`app/models/report.py` + `services/ai_service.py`（汇总与建议）
  - 会话与缓存：`app/core/database.py`（Redis 客户端）+ `session_service.py`
- AI/OCR：Qwen 文本生成（需 `QWEN_API_KEY`），腾讯/阿里 OCR（需云密钥）
- 前端：
  - 微信小程序：`miniprogram/config/api.js` 指向后端；页面调用 `/api/v1` 路由（如 `/detection/analyze-base64`）
  - Android：Compose + CameraX 拍照，导航与占位页面已接入

## 主要入口点与核心类（含代码定位）
- 后端入口 `main.py:25` 创建应用；路由聚合 `app/api/__init__.py:16`
- 健康检查 `main.py:79`；静态挂载 `main.py:56`（上传目录）
- 数据连接 `app/core/database.py:22`（PostgreSQL），`app/core/database.py:107`（Redis）
- 检测 API 上传图片 `app/api/detection.py:235`；Base64 检测 `app/api/detection.py:246`
- 用户与认证：`app/api/auth.py:200`（微信登录）、`app/api/auth.py:523`（传统登录）
- 模型：`app/models/user.py:30`、`app/models/detection.py:40`、`app/models/report.py:34`
- 服务：`app/services/ai_service.py:10`、`app/services/ocr_service.py:32`、`app/services/wechat_service.py:10`
- 小程序入口：`miniprogram/app.json`；检测页逻辑 `miniprogram/pages/detection/detection.js`
- Android 入口：`app/src/main/java/com/mininutriscan/app/MainActivity.kt:14` 与导航 `AppNavigation.kt:20`

## 构建与部署流程（新手友好）
- 后端
  - `pip install -r requirements.txt`
  - 编辑 `.env`（数据库、Redis、JWT、Qwen、OCR、微信）
  - 迁移：`alembic upgrade head`
  - 启动：`uvicorn main:app --reload --host 127.0.0.1 --port 8000`
- 微信小程序
  - 在 `miniprogram/config/api.js` 设 `CURRENT_ENV='development'`，确保 `BASE_URL` 指向后端
  - 使用微信开发者工具导入运行
- Android
  - Android Studio 打开根工程，运行 `:app` 模块
- 脚本
  - 一键启动：`启动所有服务.bat`；体检：`检查项目状态.py`

## 依赖与配置
- Python 依赖见 `requirements.txt`（FastAPI、SQLAlchemy、Redis、httpx、Pillow、Alembic 等）
- 数据库与服务配置：`app/core/config.py` 提供所有关键字段与校验方法

## 测试与文档
- 测试：`test_api_endpoints.py`、`test_fastapi_server.py`、`test_system.py`、`test_end_to_end.py` 等
- 文档：`README.md`、`快速使用指南.md`、`项目工具总览.md`、竞赛与方案材料位于 `docs/`

## 代码规范与架构特点
- 分层清晰：API 路由（api）→ 服务（services）→ 模型（models）→ 基础设施（core）
- 依赖注入：数据库 `get_db()`、配置 `get_settings()`、Redis `get_redis()`
- 验证与清洗：`validators.py` 对 OCR、营养、AI 与响应进行校验与清洗
- 异常统一：`main.py` 注册全局异常处理器，返回一致的 JSON 格式
- 配置安全：使用 `.env` 加载敏感信息；日志中隐藏密钥

## 版本控制历史
- 当前目录未发现 `.git/`，无法读取提交历史；如需历史请初始化 Git 或提供远端仓库地址

## 已知问题
- 认证模块使用 `import jwt` 与 `jwt.PyJWTError`（见 `app/api/auth.py`），但依赖中列出的是 `python-jose`；建议统一 JWT 库并对齐 `requirements.txt`

---
（本文件为自动生成的仓库分析摘要，面向新手提供一目了然的导航与落地步骤）
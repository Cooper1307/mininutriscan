# 🛡️ 社区食安AI小卫士

> AI赋能社区食品安全共治新生态 - 微信小程序

[![项目状态](https://img.shields.io/badge/状态-稳定版-success.svg)](#)
[![技术栈](https://img.shields.io/badge/技术栈-微信小程序-green.svg)](#)
[![AI驱动](https://img.shields.io/badge/AI-Qwen大模型-blue.svg)](#)
[![社区共治](https://img.shields.io/badge/模式-社区共治-orange.svg)](#)

## 📖 项目简介

**社区食安AI小卫士**是一个基于AI技术的社区食品安全共治平台，通过微信小程序为社区居民提供智能化的食品安全服务。项目致力于构建“居民参与、志愿者协助、政府监管”的三位一体食品安全治理模式，推动社区食品安全治理现代化。

### 🎯 项目愿景

构建以AI技术为核心的社区食品安全共治平台，实现:
- 🏘️ **社区自治**: 居民主动参与食品安全监督
- 🤖 **AI赋能**: 智能识别和咨询服务
- 👥 **志愿协助**: 专业志愿者团队支持
- 🏛️ **政府监管**: 官方部门有效监管

## ✨ 核心功能

- **🔍 AI智能检测**: 通过OCR技术识别食品标签，利用AI分析营养成分、保质期，并进行安全评估。
- **📢 社区举报系统**: 提供便捷的食品安全问题举报流程，并实时跟踪处理状态。
- **👥 志愿者管理**: 包含志愿者注册、任务分配、服务激励与专业培训。
- **📚 科普教育**: 提供丰富的食品安全知识库、AI智能问答和个性化内容推荐。
- **📊 数据统计**: 实时监控社区食品安全状况，进行趋势分析与效果评估。

## 🏗️ 技术架构

### 前端技术栈
```
微信小程序原生框架
├── WeUI组件库
├── 多角色界面适配
├── 响应式设计
└── 适老化设计
```

### 后端技术栈
```
Python + FastAPI
├── PostgreSQL
├── Redis
├── Docker
└── 云服务器部署
```

### AI服务层
```
AI智能服务
├── Qwen大语言模型
├── OCR图像识别API
├── 个性化推荐算法
└── 数据分析模块
```

## 🚀 快速开始

### 🛠️ 一键式工具（推荐）

为了方便您快速部署和体验，项目提供了一系列一键式配置脚本。

```powershell
# 推荐使用PowerShell运行完整设置脚本
powershell -ExecutionPolicy Bypass -File .\setup_complete.ps1
```
该脚本将引导您完成环境检查、依赖安装、数据库初始化和AI服务配置等所有步骤。

### 📖 手动安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/Cooper1307/mininutriscan.git
   cd mininutriscan
   ```

2. **前端配置**
   - 使用微信开发者工具打开项目根目录。
   - 在 `project.config.json` 中配置您的小程序AppID。

3. **后端配置**
   ```bash
   # 创建并激活Python虚拟环境
   python -m venv venv
   .\venv\Scripts\activate
   
   # 安装依赖
   pip install -r requirements.txt
   
   # 配置环境变量
   # 复制 .env.example 为 .env，并填入数据库连接信息和API密钥
   ```

4. **启动服务**
   ```bash
   # 启动后端FastAPI服务
   uvicorn main:app --reload --port 8000
   ```

## 📊 项目进度

- **[✅] 核心开发 (第1-2周)**: 完成了技术架构升级、核心功能开发和数据持久化。
- **[✅] 功能扩展 (第3-4周)**: 实现了举报管理、志愿者平台、科普教育和数据后台。
- **[✅] 实践与总结 (第5-6周)**: 完成了社区试点部署、用户培训、数据收集，并完成了项目答辩材料。
- **[🔄] 当前状态**: 项目核心功能已全部完成，进入维护与迭代阶段。

## 🤝 贡献指南

欢迎您为这个项目贡献力量！

1. **Fork** 本项目。
2. 创建您的功能分支 (`git checkout -b feature/YourAmazingFeature`)。
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)。
4. 推送到分支 (`git push origin feature/YourAmazingFeature`)。
5. 创建一个 **Pull Request**。

如有问题，请通过 [Issues](https://github.com/Cooper1307/mininutriscan/issues) 反馈。

## 📄 文档目录

- 📋 [项目计划书](./小程序项目计划书.md)
- 🎨 [UI设计图](./小程序UI设计图.md)
- 🛠️ [开发指南](./微信小程序开发完整指南.md)
- 🎓 [答辩方案](./答辩方案/答辩方案.md)
- 🎤 [答辩PPT大纲](./答辩方案/答辩PPT大纲.md)

## 🔑 主要入口点
- 后端服务入口 `main.py:25` 创建 `FastAPI` 应用并挂载路由；健康检查在 `main.py:79`。
- API 路由聚合 `app/api/__init__.py:16`，子模块如检测 `app/api/detection.py:235`、认证 `app/api/auth.py:200`。
- 数据与缓存连接 `app/core/database.py:22`（PostgreSQL）与 `app/core/database.py:107`（Redis）。
- 业务模型：用户 `app/models/user.py:30`、检测 `app/models/detection.py:40`、报告 `app/models/report.py:34`。
- 服务层：AI 服务 `app/services/ai_service.py:10`、OCR 服务 `app/services/ocr_service.py:32`、微信服务 `app/services/wechat_service.py:10`。
- 微信小程序入口 `miniprogram/app.json` 与页面逻辑示例 `miniprogram/pages/detection/detection.js`。
- Android 客户端入口 `app/src/main/java/com/mininutriscan/app/MainActivity.kt:14` 与导航 `AppNavigation.kt:20`。

## 🧭 构建与部署概览
- Python 后端
  - 安装依赖：在虚拟环境中执行 `pip install -r requirements.txt`
  - 配置环境：在 `.env` 设置数据库、Redis、JWT、OCR、Qwen 等键值（参考 `app/core/config.py` 字段）
  - 数据库迁移：设置好 `DATABASE_URL` 后运行 `alembic upgrade head` 应用 `migrations/versions` 里的变更
  - 启动开发：`uvicorn main:app --reload --host 127.0.0.1 --port 8000`
- 微信小程序
  - 在 `miniprogram/config/api.js` 将 `CURRENT_ENV` 设为 `development` 并确保 `BASE_URL` 指向后端
  - 使用微信开发者工具导入 `miniprogram/` 并运行
- Android 客户端
  - 使用 Android Studio 打开根工程，Gradle 版本见 `gradle/libs.versions.toml`
  - 运行 `:app` 模块（CameraX 扫描与 Compose UI 已接入）
- 脚本辅助
  - Windows 一键启动：`启动所有服务.bat`（含 Redis 可选启动与后端启动）
  - 项目体检：`检查项目状态.py` 会检查依赖、配置、数据库与 FastAPI 文档可用性

## ⚠️ 已知问题与建议
- 认证模块当前使用 `import jwt` 并引用 `jwt.PyJWTError`（见 `app/api/auth.py`），而 `requirements.txt` 列的是 `python-jose`，可能存在库不一致。建议统一为同一 JWT 实现并在 `requirements.txt` 对齐。

## 📜 许可证

本项目采用 [MIT License](LICENSE) 许可证。

---

<div align="center">
**🛡️ 守护社区食品安全，共建美好生活 🛡️**
</div>

# TestHub 开发总则

你是当前仓库的开发助手。默认目标不是写“理想模板代码”，而是在 `TestHub` 现有架构下交付可运行、可验证、可维护的改动。

## 1. 规则优先级
发生冲突时，按以下顺序执行：
1. 用户当前回合的明确要求
2. 本文件 `.antigravity/prompt.md`
3. `.antigravity/workflow_rules.md`
4. `.antigravity/architecture.md`
5. `.antigravity/storage_rules.md`
6. `.antigravity/project_rules.md`
7. 代码库现状与最小惊扰原则

补充说明：
- `workflow_rules.md` 优先级提高，表示当前项目默认按 TDD/验证优先的开发流程执行。
- `workflow_rules.md` 约束的是实现顺序、验证方式和交付方式，不得用于突破 `architecture.md` 中已经明确写死的架构红线。

## 2. 默认行为
- 先读相关代码，再做判断。
- 优先复用现有目录、工具函数、序列化器、接口封装和配置模型。
- 不为了“显得先进”替换当前技术路线。
- 不把一次需求扩展成全仓重构。
- 遇到历史债务时，优先在本次改动范围内止血，不顺手扩大清理面。

## 3. 当前仓库认知
- 后端根目录是 Django 项目：`manage.py`、`backend`、`apps`。
- 前端目录是 `frontend`，请求中枢在 `frontend/src/utils/api.js`，共享状态在 `frontend/src/stores`。
- 后端技术栈：Django 4.2 + DRF + MySQL + SimpleJWT + Channels + Celery + Selenium/Playwright/Airtest。
- 前端技术栈：Vue 3 + Vite + Pinia + Element Plus，以 JavaScript 为主，少量 TypeScript 辅助。
- 这是智能测试管理平台，不是通用后台模板；任何改动都要考虑认证、执行、结果落库、报告、通知、媒体文件、AI 配置这些业务闭环。

## 4. 沟通语言
- 与用户沟通统一使用中文。
- 所有新增或修改的规范文件、设计文档、任务文档、交付说明统一使用中文。
- 所有新增或修改的代码注释统一使用中文；接口字段名、协议关键字、库名和第三方能力名可保留英文原文。
- 输出尽量直接，先说结果和风险，再补细节。
- 若无法验证，明确说明没验证什么、为什么没验证。

## 5. 开发边界
- 后端接口统一从 `apps/*/urls.py` 暴露，经 `views.py` 或 `views_*.py` 进入；复杂流程优先下沉到 `serializers.py`、`tasks.py`、`services/`、`executors/`、`runners/`、`utils/`。
- 数据库存储统一通过 `apps/*/models.py` 和迁移体系维护，不在业务视图里散写表结构假设。
- 前端请求优先复用 `frontend/src/api/*` 和 `frontend/src/utils/api.js`；若现有页面已经直接使用 `@/utils/api`，小改可沿用，但不得新增裸 `axios` 或硬编码主机地址。
- 认证、AI、执行器、WebSocket、通知、调度、报告生成属于高风险链路，优先沿用既有模块，不另起平行体系。

## 6. 代码质量底线
- 改动必须可解释：改了什么、为什么这样改、影响范围是什么。
- 改动必须可验证：至少给出已执行的检查或明确未执行原因。
- 新增逻辑不得破坏现有 JWT 刷新链路、媒体路径、任务状态流转、报告输出路径和前端请求封装方式。
- 高风险链路默认谨慎处理：登录、权限、AI 模型配置、Celery 任务、Channels 推送、设备状态、报告结果。

## 7. 配置与敏感信息
- 后端运行配置优先收敛到根目录 `.env` 和 `backend/settings.py`。
- 前端构建与代理配置优先收敛到 `frontend/vite.config.js`，新增运行变量优先进入 `frontend/.env.*`。
- 不在规范、代码、示例里新增真实密钥、真实账号、真实公网地址。
- 如果发现现有硬编码敏感信息，除非用户要求处理，否则只在修改范围内避免继续扩散。

## 8. 编码规则
- 统一使用 UTF-8。
- 当前仓库存在中文乱码风险；修改规则文件和新建文件时必须保证 UTF-8 正常可读。

## 9. 交付要求
每次完成后至少说明：
- 改了哪些文件
- 为什么这么改
- 做了哪些验证
- 还剩什么风险或后续建议

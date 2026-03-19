# TestHub 存储与访问规则

本文约束数据访问、配置访问、设备访问与文件落盘路径，避免把当前项目越改越散。

## 1. 前端访问链路
统一链路：
`View -> src/api 或 utils/api.js -> axios interceptor -> Django API`

必须遵守：
- 页面不得直接写裸请求主机地址。
- token、refresh token 注入沿用 `frontend/src/utils/api.js` 与 `frontend/src/stores/user.js` 现有拦截器链路。
- 本地存储只放前端运行所需信息，如 token、用户基础信息、轻量 UI 状态；真实业务结果不得长期缓存到浏览器代替后端。

## 2. 后端访问链路
统一链路：
`urls.py -> views/viewsets -> serializers/services/executors/tasks -> models/database/filesystem`

必须遵守：
- Django / DRF 视图只负责收参、调度、返回。
- 数据库存取优先通过 Django ORM 查询与更新。
- 复杂执行流程放到 serializer、service、executor、runner 或 Celery task。

## 3. 数据库存储规则
- MySQL 连接统一从根目录 `.env` 与 `backend/settings.py` 读取。
- 新增表结构时，先修改对应 `models.py`，再补迁移说明；不要只改库不改模型，也不要只改模型不考虑迁移。
- 改 `JSONField`、状态字段、报告字段时，要同步考虑 serializer、查询过滤、前端消费和历史数据兼容。
- 统一保持当前字段命名习惯，避免前后端同义字段并存。

## 4. 文件与媒体存储规则
- 需求文档、截图、视频、Allure 报告、上传文件统一走项目既有 `media`、`allure` 或模块内已约定目录体系。
- 新增媒体文件时，必须落到与业务结果可追溯的目录结构下，不写临时散落文件。
- 前端展示媒体地址时，统一通过后端静态资源挂载路径或配置中的来源地址生成。
- 生成报告、截图、录屏时，必须同时考虑数据库记录、文件路径和前端访问路径是否一致。

## 5. 设备与平台访问规则
- ADB、Airtest、Selenium、Playwright、Browser-use 等执行逻辑只能在后端或 worker 中执行。
- 前端只能通过接口请求设备或执行器相关操作，不能新增任何绕过后端的控制方案。
- 设备状态、执行进度、WebSocket 推送内容必须同时考虑数据库状态、执行状态、前端展示状态是否一致。

## 6. 配置访问规则
- Django、数据库、Redis、邮件、日志、CORS、媒体目录等配置统一收敛到根目录 `.env` 和 `backend/settings.py`。
- 前端代理、构建、静态资源访问配置统一收敛到 `frontend/vite.config.js`，新增运行变量优先进入 `frontend/.env.*`。
- 不允许为单次开发方便把 IP、端口、密钥直接硬编码进页面、组件、视图、任务或执行器。
- 现有历史硬编码如果本次未触达，可记录为债务，但不得继续扩散。

## 7. 通知与外部服务规则
- 企业微信、钉钉、飞书、邮件等外部通知优先复用 `apps.core.models.UnifiedNotificationConfig` 与现有通知日志链路。
- 新通知类型优先在现有通知模块上扩展，不平行复制一套发送逻辑。
- AI 提供商配置优先复用 `AIModelConfig`、`DifyConfig`、API 测试现有配置模型或统一服务层，不在多个业务模块重复定义相同配置结构。
- 敏感配置不得写死到新增代码中；已有硬编码问题只能在本次需求明确覆盖时再处理。

## 8. 查询与分页规则
- 列表接口优先沿用 DRF 分页、过滤和排序体系。
- 树形和层级数据优先复用后端已有数据结构，不在前端重新拼一套平行结构。
- 不在页面侧复制后端业务规则来“修正”接口返回，确需适配时放到接口层或页面局部适配层。

## 9. 明确禁止
- Vue 页面直接访问数据库或本地文件系统概念上的“替代方案”。
- 在后端视图里到处散写文件路径拼接和媒体 URL 生成。
- 同一份业务数据既存数据库又存浏览器缓存，并靠猜测谁更新。
- 绕开现有 `frontend/src/utils/api.js`、Django ORM、Celery、通知配置链路另起一套通路。

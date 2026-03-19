# TestHub 架构规则

本文定义当前仓库必须遵守的架构边界。目标不是做“理想化重构”，而是让改动能在现有项目里稳定落地。

## 1. 适用范围
- 适用于 `e:\testhub_platform-main\testhub_platform-main` 当前仓库。
- 以当前仓库真实结构为准，不为了“规范完整”强推大迁移。
- 新增代码优先贴合现有目录和调用方式，再考虑抽象升级。

## 2. 项目全局结构
- 根目录包含 `manage.py`、`backend`、`apps`、`frontend`、`media`、`logs`、`allure`、`docs`。
- `backend` 是 Django 项目配置层，负责全局设置、URL 汇总、中间件、ASGI/WSGI、Celery 启动入口。
- `apps` 是 Django 业务应用层，负责用户、项目、需求分析、测试执行、AI、通知、自动化等模块。
- `frontend` 是 Vue 3 前端，负责页面、交互、状态管理、接口调用和可视化展示。
- 这是前后端分离项目。前端负责页面和接口消费；后端负责业务、数据、执行器、调度、通知、媒体文件和 AI 服务接入。

## 3. 工程配置边界
- 后端运行配置统一从根目录 `.env` 与 `backend/settings.py` 读取，默认值只作为兜底，不再把真实环境写死在源码里。
- 前端开发代理和构建配置统一收敛到 `frontend/vite.config.js`，新增运行变量优先进入 `frontend/.env.*`。
- JWT、邮件、Redis、Channels、Celery、媒体目录、报告目录都属于配置层，不得散落在业务页面和视图细节中。
- 新增 AI 提供商、模型或模式切换，应优先进入统一配置模型或服务层，不允许把 `provider / api_key / base_url` 判断散落到多个页面和 ViewSet 中。

## 4. 后端目录职责
- `backend/settings.py`：全局配置、已安装应用、中间件、数据库、JWT、Channels、Celery、静态资源、邮件与跨域设置。
- `backend/urls.py`：全局 URL 汇总、媒体和报告静态挂载。
- `apps/<module>/models.py`：数据库模型与字段语义定义。
- `apps/<module>/serializers.py`：请求校验、字段转换、响应序列化。
- `apps/<module>/views.py` / `views_*.py`：DRF 入口层，只做收参、调度、返回。
- `apps/<module>/urls.py`：模块路由注册。
- `apps/<module>/tasks.py`：Celery 异步任务、状态推进、通知触发。
- `apps/<module>/executors/`、`runners/`、`services/`、`utils/`：复杂业务逻辑、执行器、流程编排、外部服务封装。
- `apps/<module>/management/commands/`：初始化、调度器、驱动安装等管理命令。

## 5. 后端强约束
- ViewSet、APIView、函数视图不得堆积复杂业务逻辑。复杂流程必须下沉到 serializer、service、executor、runner 或 task。
- `models.py` 只做数据定义和少量模型级辅助方法，不写控制器流程，不夹带接口逻辑。
- 请求校验优先放在 serializer 或专门的服务层，而不是直接在 view 里散写大量字段判断。
- 新增数据库访问优先沿用 Django ORM 和迁移体系，不混入另一套 ORM 或随意原生 SQL，除非当前模块已有明确历史原因。
- 调度、执行器、通知、报告链路属于高风险区域，修改时必须保持状态更新、结果落库、日志或通知至少三者中的必要闭环。

## 6. 前端目录职责
- `frontend/src/views`：页面和页面级组件，负责展示、事件触发、局部状态。
- `frontend/src/api`：可复用的接口封装，适合跨页面共享调用。
- `frontend/src/utils/api.js`：axios 实例、JWT 注入、刷新队列、统一错误处理。
- `frontend/src/stores`：跨页面共享状态，如用户认证、全局应用状态。
- `frontend/src/router/index.js`：路由表与守卫。
- `frontend/src/locales`：国际化文案。
- `frontend/src/assets`、`components`、`layout`：公共资源、组件与布局壳。

## 7. 前端强约束
- 页面组件不得直接拼后端主机地址；请求必须走 `frontend/src/utils/api.js` 或 `frontend/src/api/*`。
- 页面内部可以管理本页状态，但跨页面共享状态必须进 Pinia。
- token、refresh token、用户态和认证跳转只能在 `utils/api.js`、`stores/user.js`、`router/index.js` 既有链路上扩展，不要在页面里重复实现。
- 新功能优先沿用现有 Vue 3 Composition API + Element Plus 风格；当前仓库以 JavaScript 为主，不强行为了“统一”把局部改成另一套范式。
- 若一个功能已经走真实后端接口，就不要再补一套本地 JSON 假数据逻辑。

## 8. 前后端联动边界
- 前端数据结构必须以真实后端 serializer / response 为准，不能只为了页面方便私自改字段名。
- 后端接口字段若变更，必须同步检查 `frontend/src/api`、页面表单、表格、路由跳转、报告页和本地缓存。
- 涉及执行结果、报告、媒体路径、状态流转、推送消息的字段变更，必须同时检查数据库模型、接口返回、文件目录和前端展示。

## 9. 当前项目的真实业务边界
- 业务基础模块：`users`、`projects`、`versions`、`testcases`、`testsuites`、`reviews`、`executions`、`reports`。
- AI 相关模块：`requirement_analysis`、`assistant`、`api_testing` 中的 AI 服务配置、`ui_automation` 智能模式。
- 自动化测试模块：`api_testing`、`ui_automation`、`app_automation`。
- 平台能力模块：`core`（统一通知与管理命令）、`data_factory`（测试数据与工具）、`backend`（全局配置）。

## 10. 新功能放置规则
- 新的后端业务模块优先放到 `apps/<module>` 下成套新增 `models.py`、`serializers.py`、`views.py`、`urls.py`，复杂流程再放 `tasks.py`、`services/`、`executors/`。
- 新的前端业务页面优先放到 `frontend/src/views/<module>`，跨页面复用接口放 `frontend/src/api/<module>`。
- 若只是补充现有模块能力，优先在原模块内扩展，不另起一套平行目录。

## 11. 明确禁止
- 把执行器、AI 调用或调度逻辑直接写进 Django 视图函数。
- 在 Vue 页面里直接发裸 axios 请求或直接写死后端主机地址。
- 同一个业务同时维护两套字段定义，只靠“页面猜字段”去兼容。
- 为了单次需求引入新的前端状态管理、UI 框架、Python Web 框架或 ORM。
- 修改 IP、端口、路径、密钥时散落多处硬编码，不回收到配置层。

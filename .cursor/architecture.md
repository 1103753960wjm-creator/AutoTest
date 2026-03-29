# TestHub 架构规则

## 1. 文件职责

本文件属于 B 层“项目规则”，用于定义当前仓库长期有效的架构边界和模块职责。

## 2. 项目全局结构

- `backend`：Django 项目入口、全局设置、中间件、Celery/ASGI/WSGI 配置
- `apps`：按业务域拆分的 Django 应用
- `frontend`：Vue 3 管理台
- `docs`：规则、设计、说明和阶段文档
- `media`：上传物、截图、报告等运行产物
- `logs`：日志产物
- `allure`：Allure 工具和配置

## 3. 后端架构边界

后端统一链路：

`backend/urls.py -> apps/<module>/urls.py -> views -> serializers/services/models`

职责约束：

- `backend/settings.py`、`backend/urls.py`、`backend/asgi.py`、`backend/celery.py` 负责全局配置与入口注册。
- `apps/<module>/urls.py` 负责模块路由分发。
- `apps/<module>/views.py` 或 `views/*` 负责接口入口、请求调度和响应组织。
- `apps/<module>/serializers.py` 负责参数校验、对象序列化和字段约束。
- `apps/<module>/models.py` 负责数据模型和数据关系定义。
- `services.py`、`utils.py`、执行器、管理器等负责复杂业务流程、第三方调用和多步骤编排。

强约束：

- 接口入口不得堆积复杂流程；跨模型、多步骤、副作用明显的逻辑应下沉到服务层、执行器或工具层。
- 新增数据访问优先沿用 Django ORM 和当前 app 内模式，不随意引入并行 ORM 或散写原生 SQL。
- 认证、通知、执行器、异步任务、报告生成属于高风险链路，修改时必须同时考虑状态、结果、日志和前端展示影响。

## 4. 前端架构边界

前端统一链路：

`View -> src/api/* -> src/utils/api.js -> Backend /api/*`

职责约束：

- `frontend/src/views`：页面和页面级交互逻辑
- `frontend/src/api`：所有后端接口封装
- `frontend/src/utils/api.js`：axios 实例、请求/响应拦截器、鉴权续期逻辑
- `frontend/src/stores`：Pinia 全局状态
- `frontend/src/router`：静态路由、路由守卫、深链接和 route meta
- `frontend/src/layout`：平台壳层、全局头部、侧边导航、页面头部
- `frontend/src/components`：可复用组件
- `frontend/src/config`：导航等前端配置真源

强约束：

- 页面和组件不得直接散写裸 axios 请求。
- token、登录态、用户信息、最近访问、全局搜索等跨页面状态必须沿用既有 router/store/utils 链路扩展。
- 新功能优先沿用现有 Vue 3 SFC、Pinia、Element Plus 和平台壳组织方式。
- 若一个功能已经走真实后端接口，不再平行维护一套本地假数据流程。

## 5. 前后端联动边界

- 前端字段命名、路由参数和页面展示应以真实后端接口为准，不为了页面方便私改后端语义。
- 后端接口字段变更时，必须同步检查 `frontend/src/api/*`、相关页面、表单、表格、路由回跳和文档。
- 新增 route meta 字段时，必须同步更新 `frontend/src/types/router-meta.d.ts`。

## 6. AI 能力接入边界

- 新增 AI 能力不得继续在普通页面、零散工具函数或无统一配置的脚本中直连模型。
- 新增 AI 接入应优先复用 `apps.assistant`、`apps.requirement_analysis` 或已有 AI 服务封装层，并将模型配置、提示词配置、行为配置统一收敛到既有配置链路。
- 若历史代码已存在散点调用，本轮新增改动不得继续扩散新的并行入口。

## 7. 明确禁止

- 在页面组件中直接拼接后端绝对地址或裸请求。
- 在 Django 入口层塞入跨多个对象和副作用链路的大段业务逻辑。
- 为局部需求引入与现有技术栈冲突的新框架、新状态管理或新请求通路。
- 在业务模块中散写环境地址、密钥、路径和模型调用入口。

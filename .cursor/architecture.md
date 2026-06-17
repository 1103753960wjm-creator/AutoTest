# TestHub 架构规则

## 1. 文件职责

本文件属于 B 层“项目规则”，用于定义当前仓库长期有效的：

- 模块职责边界
- 前后端统一链路
- AI 接入红线
- 实现方式红线

## 2. 项目全局结构

- `backend`：Django 项目入口、全局设置、中间件、Celery / ASGI / WSGI 配置
- `apps`：按业务域拆分的 Django 应用
- `frontend`：Vue 3 管理台
- `docs`：规则、设计、说明和阶段文档
- `media`：上传物、截图、报告等运行产物
- `logs`：日志产物
- `allure`：Allure 工具和配置

## 3. 后端统一链路

统一链路：

`backend/urls.py -> apps/<module>/urls.py -> views -> serializers/services/models`

职责分工：

- `backend/settings.py`、`backend/urls.py`、`backend/asgi.py`、`backend/celery.py`：全局配置和入口注册
- `apps/<module>/urls.py`：模块路由分发
- `views.py` 或 `views/*`：接口入口、收参、鉴权、调度、响应组织
- `serializers.py`：参数校验、字段约束、对象序列化
- `models.py`：数据模型与关系定义
- `services.py`、执行器、管理器、工具层：复杂流程、第三方调用、多步骤编排和副作用链

强约束：

- `views` 不得堆积跨对象、多步骤、副作用明显的大段业务逻辑
- 跨模型状态流转、执行器编排、第三方调用必须下沉到 service / executor / 工具层
- 新增数据访问优先沿用 Django ORM 和当前 app 组织方式，不随意引入并行 ORM 或散写原生 SQL

## 4. 前端统一链路

统一链路：

`View -> frontend/src/api/* -> frontend/src/utils/api.js -> Backend /api/*`

职责分工：

- `frontend/src/views`：页面和页面级交互逻辑
- `frontend/src/api`：所有后端接口封装
- `frontend/src/utils/api.js`：axios 实例、请求/响应拦截、鉴权续期逻辑
- `frontend/src/stores`：Pinia 全局状态
- `frontend/src/router`：静态路由、路由守卫、深链接和 route meta
- `frontend/src/layout`：平台壳层、全局头部、侧边导航、页面头部
- `frontend/src/components`：可复用组件
- `frontend/src/config`：导航等前端配置真源

强约束：

- 页面和组件不得直接散写裸 axios 请求
- token、登录态、用户信息、最近访问、全局搜索等跨页面状态必须沿用现有 router / store / utils 链路扩展
- 已有真实后端接口的功能，不再平行维护一套本地假数据流程
- 登录后业务页面必须共用稳定的根层 Layout，不能按模块或物理路由销毁整套平台壳；模块切换应由 `frontend/src/layout/index.vue` 内部状态和内容路由完成
- 认证失效、退出登录和 refresh 失败回登录必须走统一认证导航工具，不得在 store、api 拦截器或页面中散写浏览器跳转

## 5. AI 接入边界

- 新增 AI 能力不得在普通页面、零散工具函数或无统一配置的脚本中直连模型
- 新增 AI 接入应优先复用 `apps.assistant`、`apps.requirement_analysis` 或既有 AI 服务封装层
- 模型配置、提示词配置、行为配置必须统一收敛到既有配置链路
- 历史代码若存在散点调用，本轮新增改动不得继续扩散新的并行入口

## 6. 前端请求编排红线

- `keepAlive` 页面不得由 `onMounted`、`activated`、`watch` 各自直发同一请求
- 同一页面的首屏数据必须汇总到单一 `refresh/load` 入口，生命周期只负责触发该入口
- 默认列表页禁止通过超大 `page_size` 拉全量数据代替分页、聚合或导出接口
- 轮询必须具备最小间隔、终态停止、页面失焦暂停和重复订阅去重机制
- route meta、导航真源、全局状态改动属于高风险改动，必须同步说明回归面
- 根层 `router-view`、Layout key、侧边栏导航和统一导航调度器改动属于高风险改动，必须补跑跨顶部模块快速切换验证

## 7. 后端副作用与观测红线

- 认证、通知、执行器、异步任务、报告生成属于高风险副作用链路，修改时必须同时考虑状态、结果、日志和前端展示影响
- 日志注册必须保证幂等，避免开发环境重复输出同一条 access log
- 不允许在接口入口层散写运行产物目录拼接、复杂文件落盘逻辑和跨对象副作用链
- 生产环境安全配置必须显式化，不得用“方便启动”的默认值放开 hosts、CORS 或 API CSRF

## 8. 明确禁止

- 在页面组件中直接拼接后端绝对地址或裸请求
- 在 Django 入口层塞入跨多个对象和副作用链路的大段业务逻辑
- 为局部需求引入与现有技术栈冲突的新框架、新状态管理或新请求通路
- 在业务模块中散写环境地址、密钥、路径和模型调用入口
- 用 `window.location.reload()`、`window.location.href` 或整页刷新兜底 SPA 导航和认证跳转

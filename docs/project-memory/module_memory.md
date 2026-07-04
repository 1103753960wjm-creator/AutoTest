# TestHub 模块记忆

更新时间：2026-07-04

## 1. 文件职责

本文文件属于 C 层“正式项目记忆”，用于记录各模块当前稳定有效的局部边界、局部风险与开发注意事项。

使用原则：

- 只记录模块局部真相，不重复抄写全局规则
- 只记录对后续开发持续有帮助的边界、风险与经验
- 若本文与实际代码冲突，以实际代码为准，并及时回写本文
- 规则红线仍以 `AGENTS.md` 与 `.cursor/*.md` 为准
- 已证明会重复出现的跨模块错误模式统一沉淀到 `docs/project-memory/error_prevention_log.md`

## 2. frontend

### 2.1 模块职责

- 承接平台页面、路由、状态管理、统一页面壳与业务交互

### 2.2 当前边界

- 所有后端请求统一通过 `frontend/src/api/*`
- `route meta` 是页面标题、模块归属、面包屑与页面类型的重要真源
- 列表页、详情页、编辑页、结果页的页面职责已经在规则层冻结，不应互相越界

### 2.3 高风险点

- `keepAlive` 页面中的重复请求链
- route meta、导航守卫、全局布局壳变更
- 超大 `page_size` 或一次性全量拉取
- token、登录、退出、401 刷新链路
- `router-view` 的 `:key` 与 `keep-alive` 的 `include` 匹配维度不一致
- 根层 `App.vue` 的 `router-view` key 过细，导致跨顶部模块切换时销毁整套 Layout 并打断导航队列
- 侧边栏多事件触发或导航调度器排队阻塞，会导致快速跨顶部模块与子模块切换时侧栏、URL、页面标题和正文不一致
- `platform-route-wrapper` 的 overflow/height 内联样式影响子页面滚动
- `<form>` / `<el-form>` 缺少 `@submit.prevent`，或原生 `<button>` 缺少显式 `type`，会让 Enter 键或按钮点击触发浏览器默认提交，绕开 SPA 路由形成整页刷新体感
- Element Plus 服务式组件（如 `ElMessageBox`、`ElMessage`、`ElLoading`）直接通过 JS API 调用时，不会被模板组件自动解析器兜底样式；若全局入口没有引入对应 style，可能出现弹窗裸样式、遮罩缺失或不居中
- 业务页面或认证跳转中直接使用 `window.location.href`、`window.location.assign`、`window.location.reload`
- 前端 Excel 导出散落页面并继续依赖 `xlsx`
- Vite dev server 依赖优化配置错误，尤其是长期保留 `optimizeDeps.force: true`，会让首次访问懒加载页面时出现 `504 Outdated Optimize Dep`、动态 import 失败和整页刷新体感

### 2.4 开发注意事项

- 首屏数据优先通过单一 `refresh/load` 收口
- 轮询必须具备最小间隔、终态停止、失焦暂停或降频、同对象去重
- 新增 route meta 字段时同步更新 `frontend/src/types/router-meta.d.ts`
- 根层 `App.vue` 登录后业务页面必须使用稳定 `layout:authenticated`，禁止按模块、物理顶层路由、`fullPath` 或 `params` 销毁平台壳
- 内容层 `layout/index.vue` 的 `router-view` 组件 key 必须使用 `currentRoute.name || currentRoute.path`，禁止使用 `fullPath`
- 顶部模块、侧边栏、搜索、最近访问、收藏和用户资料入口必须统一走 `layout/index.vue` 的导航调度器，不能绕过它直接 `router.push`
- 侧边栏导航只允许通过 `el-menu @select` 触发一次，不得重新加 `pointerdown.capture` 或 `click.capture` 抢跑导航
- `layout/index.vue` 导航调度必须保持“最后一次点击优先”，旧导航被取消时不得阻塞最新点击目标
- `router.afterEach` 写浏览器标题时必须确认当前真实路由仍是本次目标，避免旧导航晚到覆盖新页面标题
- SPA 页面中的 `<form>` 与 Element Plus `<el-form>` 必须添加 `@submit.prevent`；原生 `<button>` 必须显式声明 `type="button"`，除非明确存在 `type="submit"` 的业务提交链路
- 认证失效、退出登录和 refresh 失败回登录统一走 `frontend/src/utils/authNavigation.js`
- Excel 导出统一走 `frontend/src/utils/excelExport.js`，不得在新页面或文档模板中继续引入 `xlsx`
- 在 `ListShell` 的 `#filters` 插槽中，所有 `el-select` 和 `el-input` 必须设置 `width: 100%`，`el-col` span 参考评审列表（每列 span 8）
- 使用 `ElMessageBox`、`ElMessage`、`ElNotification`、`ElLoading` 等服务式 API 前，先确认 `frontend/src/main.js` 或全局样式入口已引入对应 `element-plus/es/components/*/style/css`
- 接口自动化“接口测试用例”正式入口为 `/api-testing/test-cases`，该入口必须是用例资产列表页；旧 `/api-testing/interfaces` 只能作为隐藏兼容入口，不得再把“接口管理”或旧调试树作为唯一用例入口
- `InterfaceManagement.vue` 当前只复用为接口测试用例隐藏调试工作区，路径为 `/api-testing/test-cases/workspace?caseId={id}`；业务请求必须经由 `frontend/src/api/api-testing.js`，不要重新直接导入 `@/utils/api`
- 隐藏调试工作区必须保留返回用例列表的显式入口，避免从资产列表进入调试后只能依赖浏览器返回
- 从接口测试用例列表跳转到隐藏调试工作区时要带 `caseId` 和 `projectId`；工作区是 `keepAlive` 页面，必须监听 query 变化重选目标用例，不能靠销毁重建来切换详情
- 接口测试用例列表涉及搜索、分页、项目切换等并发请求时，必须采用“最后一次请求优先”或等价机制，避免旧响应晚返回覆盖最新列表
- P0 阶段接口测试用例技术载体仍是 `ApiRequest`，项目归属来自 `ApiCollection`；新建用例必须选择集合，加入测试套件必须限制同项目
- 接口测试用例资产列表固定字段为：用例名称、请求方法、URL、所属项目、所属集合、断言数、来源、最近执行状态、更新时间、操作；筛选项至少包含项目、集合、请求方法、关键词
- 接口测试用例列表的最近执行状态必须由后端 `ApiRequest` 列表聚合最近一条 `RequestHistory` 返回，前端不得为了表格状态逐行请求历史形成 N+1
- 接口测试用例列表的“加入套件”必须有明确交互反馈：行操作要阻止表格行事件冒泡；套件加载中或无可用套件时禁用确认；未归属集合、无套件、加载失败、未选择套件、加入成功和加入失败都必须给出清晰弹窗提示，不得静默失败
- 接口测试用例和测试套件是两个对象：`ApiRequest` 是原子接口用例资产，`TestSuite + TestSuiteRequest` 是套件编排资产；AI 生成 `api_test_case` 时只应生成 `ApiRequest` 兼容字段，不应直接生成或修改测试套件
- 接口测试用例移动集合必须走 `POST /api-testing/requests/{id}/move-collection/`，后端校验同项目和用户项目权限；前端只能展示同项目集合，不能靠页面筛选替代后端校验
- 请求历史清空必须走 `POST /api-testing/histories/clear/`，并按当前筛选范围清空；确认文案必须说明范围，失败时不能清空前端列表制造假成功
- 测试套件页 `/api-testing/test-suites` 的套件级断言必须保存到 `TestSuiteRequest.assertions`；套件执行优先使用套件级断言，空时才回退到 `ApiRequest.assertions`
- `TestSuiteRequest.assertions` 与旧断言数据需要兼容 `expected` 和 `value` 两种期望值字段，避免旧数据执行结果变化
- 项目负责人字段当前前端只读展示，不向后端提交 `owner`；后续如要支持负责人转移，必须单独做权限、接口和审计设计
- 接口自动化测试套件正式侧边栏入口为 `/api-testing/test-suites`；旧 `/api-testing/automation` 只能作为隐藏兼容重定向，不得重新作为可见入口或 Dashboard 主入口
- 修改 `frontend/vite.config.js` 的 `optimizeDeps` 时，必须保留对懒加载页面和 Element Plus 按需样式的预优化覆盖；不要长期恢复 `force: true`，否则本地开发首次切页会重新出现整页刷新体感

## 3. backend

### 3.1 模块职责

- 承接后端主路由、配置入口、接口分发、权限控制与统一后端组织方式

### 3.2 当前边界

- 统一链路为 `backend/urls.py -> apps/<module>/urls.py -> views -> serializers/services/models`
- `views` 只负责收参、鉴权、调度与响应组织
- 多步骤流程、跨对象状态变更、第三方调用应进入服务层、执行器或工具层

### 3.3 高风险点

- JWT 登录与刷新
- Celery 异步任务
- Channels / WebSocket
- 执行器链路、Allure 报告、通知链路
- AI 统一接入入口
- 生产配置缺失或非法时仍能启动，导致 CORS、hosts、CSRF 等安全兜底不可控

### 3.4 开发注意事项

- 新增配置统一收敛到 `backend/settings.py`、`decouple.config` 或既有集中配置入口
- `DEBUG`、`DISABLE_CSRF_FOR_API` 等关键布尔配置必须走项目级严格解析，非法值直接 `ImproperlyConfigured`
- 生产环境必须显式配置 `ALLOWED_HOSTS`、`CORS_ALLOWED_ORIGINS` 和安全 `SECRET_KEY`，禁止 `ALLOWED_HOSTS=*`
- 生产环境禁止开启 `DISABLE_CSRF_FOR_API=True`
- 避免新增重复访问日志、重复异常日志与无上下文日志
- 改共享字段、状态字段、来源标签时必须同步检查前端消费端与文档
- 接口自动化单接口执行后，`RequestHistory.assertions_results` 必须真实落库；只在响应体临时补断言结果不算闭环
- 接口自动化移动集合、清空历史和套件级断言保存都必须继续从当前用户可见 queryset 出发做权限过滤；不能只按传入 id 直接更新或删除
- `RequestHistory` 清空范围必须由后端根据筛选参数执行，避免前端只传当前页 id 或只隐藏列表造成数据真源不一致

## 4. requirement_analysis

### 4.1 模块职责

- 承接需求分析、AI 生成任务、结果批次、自动评审入口与来源回链语义

### 4.2 当前边界

- 任务对象、结果对象、正式资产对象已经形成分层边界
- `TaskDetail` 负责任务对象与结果入口
- `GeneratedTestCaseList` 负责结果批次与结果处理状态表达
- 正式测试资产层只轻量承接来源关系

### 4.3 高风险点

- 任务状态与结果状态混淆
- 采纳、弃用、来源标签回写的幂等性
- 自动评审记录与人工评审记录语义混用
- 同一 `taskId` 被多个页面或组件重复轮询

### 4.4 开发注意事项

- 进度轮询优先复用统一 tracker 或统一轮询入口
- 老数据必须允许“来源未记录 / AI 来源待补齐”等兼容态
- 结果对象的处理状态与正式资产对象的来源摘要不要互相伪装
- 从 `TaskDetail` 通过 `taskId` 进入 `GeneratedTestCaseList` 时，结果批次页必须真实按该任务收口数据，不能只显示“焦点任务”文案而仍加载全量列表
- 正式测试资产层中的 `sourceTaskId` 当前只作为来源上下文提示，不作为正式资产列表的结果层过滤条件
- `TaskDetail` 当前只保留结果预览、处理状态与结果批次入口；批量采纳、弃用等结果处理主动作应继续收口在结果批次页
- P0-2 AI 生成目标类型只能套用现有生成链路：允许新增 `target_type`、Prompt 按类型选择、任务固化和结果字段适配；禁止重写生成任务创建、模型调用、流式输出、取消、自动评审、轮询恢复和功能测试采纳主链
- `api_test_case` 结果的字段适配应作为目标类型分支下的轻量归一化，不能替换原功能测试用例解析路径；旧功能测试生成和采纳必须作为回归主线

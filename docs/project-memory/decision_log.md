# TestHub 决策日志

更新时间：2026-06-19

## 1. 文件职责

本文文件属于 C 层“正式项目记忆”，用于记录已经确认并冻结的关键决策、取舍理由、影响范围与不可回退口径。

使用原则：

- 只记录已经确认的决策，不记录尚未定案的讨论草稿
- 只记录对后续开发仍有持续影响的取舍，不记录一次性的零碎操作
- 若本文与实际代码冲突，以实际代码为准，并及时回写本文
- 正式规则以 `AGENTS.md` 与仓库内 `.cursor/*.md` 为准
- 阶段事实以 `docs/project-memory/current_phase.md` 为准
- 最近任务交接以 `docs/project-memory/task_handoff.md` 为准

## 2. 记录模板

建议后续新增决策时保持以下结构：

- 决策标题
- 决策时间
- 背景
- 决策内容
- 影响范围
- 不再采用的替代方案

## 3. 已冻结决策

### 3.1 规则体系采用“全局入口 + 分层规则 + 目录级 AGENTS”

- 决策时间：2026-04-15
- 背景：随着规则增多，根入口文件已经不适合继续堆叠所有项目细节，AI 也需要按目录读取最近规则
- 决策内容：根 `AGENTS.md` 只保留读文件顺序、流程闸门、全仓红线、验证入口和目录路由；具体项目规则收敛到 `.cursor/*.md`，高频高风险目录使用局部 `AGENTS.md`
- 影响范围：整个仓库的规则读取方式、后续新增局部规则的扩展方式
- 不再采用的替代方案：继续把所有规则都堆在根 `AGENTS.md`

### 3.2 默认开发流程固定为 `Spec/SDD -> TDD -> Execution -> VDD`

- 决策时间：2026-04-01
- 背景：跨模块开发、高风险链路改动和规则重构都需要先对齐边界，不能直接开始实现
- 决策内容：非“小修小改”场景下，必须先完成 `Spec/SDD` 并等待用户确认，再进入 `TDD`；完成 `TDD` 后，再等待用户确认进入 `Execution`
- 影响范围：所有新功能、规则重构、接口协议变化、AI 接入方式变化
- 不再采用的替代方案：由 AI 在存在歧义时自行做取舍并继续编码

### 3.3 AI 能力必须通过统一入口接入

- 决策时间：2026-04-01
- 背景：项目后续会持续扩展 AI 生成、评审、配置与调用链，若散接模型调用会快速失控
- 决策内容：新增 AI 能力必须通过统一入口、统一服务层或统一配置链路接入，禁止在业务模块直接散接模型调用
- 影响范围：`apps/requirement_analysis`、配置中心、后续 AI 业务扩展
- 不再采用的替代方案：每个业务模块各自维护独立模型调用实现

### 3.4 测试设计 2.2 主链以“任务对象 -> 结果对象 -> 正式资产对象”分层推进

- 决策时间：2026-03-26
- 背景：AI 生成链路经历多轮调整后，需要避免任务页、结果页、正式资产页互相越界
- 决策内容：`TaskDetail` 负责任务对象与结果入口，`GeneratedTestCaseList` 承担结果批次页职责，正式测试资产层只轻量承接来源关系，不反向承担生成任务主战场
- 影响范围：`apps/requirement_analysis`、`apps/testcases`、前端测试设计模块
- 不再采用的替代方案：让任务页继续膨胀为结果处理主页面，或让正式资产页伪装成强回链中心

### 3.5 前端请求统一走 `frontend/src/api/* -> frontend/src/utils/api.js`

- 决策时间：2026-04-15
- 背景：重复请求、认证处理分散和分页失控都与请求入口不统一强相关
- 决策内容：页面和组件不得绕过 `frontend/src/api/*` 直接请求后端；认证头、token 刷新和 401 处理统一通过 `frontend/src/utils/api.js`
- 影响范围：前端所有页面、全局认证链路、分页与轮询行为
- 不再采用的替代方案：在页面组件内直接写裸请求或重复处理认证逻辑

### 3.6 Vue 3 路由缓存架构禁止在容器层混用 v-if

- 决策时间：2026-05-30
- 背景：侧边栏在含有表格/表单的复杂页面高频切换时，发生了严重崩溃 Cannot read properties of null (reading 'parentNode'/'exposed')。
- 决策内容：彻底废弃在 `<router-view>` 插槽内通过 `v-if` 条件渲染来切换缓存与非缓存容器。按需缓存必须且只能使用基于路由白名单的 `<keep-alive :include="cachedViews">` 模式，确保渲染器与组件卸载流程不受上层容器频繁销毁的影响。
- 影响范围：全局平台壳层 (`frontend/src/layout/index.vue`)，以及所有涉及动态渲染路由出口的子组件。
- 不再采用的替代方案：在缓存插槽层动态组合 div 容器与 `<keep-alive>`。

### 3.7 登录后业务页面共用稳定根层 Layout

- 决策时间：2026-06-16
- 背景：顶部大模块切换后立即点击侧边栏子模块，会出现页面停在大模块默认页、需要刷新后才恢复的体验问题。现场监控确认不是每次都发生浏览器硬刷新，而是根层 `router-view` key 导致整套 `Layout` 被销毁重建，导航队列和侧边栏事件在重建窗口内被打断。
- 决策内容：`frontend/src/App.vue` 对所有登录后业务页面统一使用 `layout:authenticated` 作为根层 key；模块切换只更新 `layout/index.vue` 内部模块态、侧边栏菜单态和内容路由，不销毁整个平台壳。登录页、注册页等壳外页面仍保持独立 key。
- 影响范围：`frontend/src/App.vue`、`frontend/src/layout/index.vue`、顶部模块导航、侧边栏导航、全局搜索、最近访问、收藏、个人资料入口。
- 不再采用的替代方案：按 `route.meta.module`、物理顶层路由、`fullPath` 或 `params` 给根层 Layout 加 key；用 `window.location.reload()` 或硬刷新兜底导航状态。

### 3.8 认证失效跳转统一走 authNavigation

- 决策时间：2026-06-16
- 背景：`userStore` 和 `api` 拦截器各自直接写 `window.location.href = '/login'`，会绕开 Vue Router，制造整页刷新体感，并与路由注册、历史记录和导航监控口径不一致。
- 决策内容：认证失效、退出登录、refresh token 失败后的登录页跳转统一通过 `frontend/src/utils/authNavigation.js`。已注册 router 时优先 `router.replace('/login')`，无法使用 router 时才降级到浏览器跳转。
- 影响范围：`frontend/src/stores/user.js`、`frontend/src/utils/api.js`、`frontend/src/router/index.js`、登录态和 401 刷新链路。
- 不再采用的替代方案：在 store、axios 拦截器或业务页面中散写 `window.location.href`、`window.location.assign`、`location.reload`。

### 3.9 生产配置必须显式安全化

- 决策时间：2026-06-16
- 背景：旧配置允许生产态缺省 CORS 后默认放开全部来源，`DEBUG=release` 等非法布尔值会抛出底层异常，API CSRF 禁用没有生产态硬拦截。
- 决策内容：后端关键布尔环境变量统一走项目级严格解析；生产态必须显式配置 `ALLOWED_HOSTS` 和 `CORS_ALLOWED_ORIGINS`；生产态禁止 `ALLOWED_HOSTS=*` 与 `DISABLE_CSRF_FOR_API=True`；生产态不能使用默认开发 `SECRET_KEY`。
- 影响范围：`backend/settings.py`、`backend/middleware.py`、`.env.example`、部署文档和启动检查流程。
- 不再采用的替代方案：生产态使用通配 hosts、缺省放开 CORS、全局禁用 API CSRF、依赖第三方布尔转换的底层错误提示。

### 3.10 前端 Excel 导出统一改用 write-excel-file

- 决策时间：2026-06-16
- 背景：`xlsx` 依赖存在无修复版本的安全风险，且导出逻辑散落在多个页面。
- 决策内容：移除 `xlsx`，新增 `frontend/src/utils/excelExport.js`，统一基于 `write-excel-file` 导出 Excel。测试用例列表、需求分析页、任务详情页已经迁移；后续文档模板和新页面示例不得继续引入 `xlsx`。
- 影响范围：`frontend/package.json`、`frontend/src/utils/excelExport.js`、所有前端 Excel 导出页面和文档模板。
- 不再采用的替代方案：继续在页面内直接 `import * as XLSX from 'xlsx'` 并手写 workbook / worksheet。

### 3.11 接口自动化 P0-1 以 ApiRequest 承接接口测试用例

- 决策时间：2026-06-17
- 背景：接口自动化没有正式“接口测试用例”子模块，导致接口自动化测试闭环只能靠“接口管理”心智承接；同时前端封装存在旧执行路径，单接口断言结果只返回不落库。
- 决策内容：P0-1 不新增 `ApiTestCase` 表，继续以 `ApiRequest` 作为接口测试用例技术载体；正式可见入口改为 `/api-testing/test-cases`，旧 `/api-testing/interfaces` 仅作为隐藏兼容入口重定向；单接口执行断言结果必须写入 `RequestHistory.assertions_results`。
- 影响范围：接口自动化路由、导航真源、API 封装、接口测试用例工作区、请求历史断言展示。
- 不再采用的替代方案：继续把“接口管理”作为唯一正式用例入口；新增空壳 `ApiTestCase` 表但不补迁移和执行闭环；前端继续调用 `/api-testing/api-requests/{id}/execute/`。

### 3.12 接口测试用例入口必须是资产列表，不得退回旧调试树首页

- 决策时间：2026-06-17
- 背景：P0-1 初版虽然补了“接口测试用例”入口，但页面形态仍接近旧接口调试工作台，用户会感知为“只是把测试套件或接口管理改了名字”，不符合测试用例资产管理心智。
- 决策内容：`/api-testing/test-cases` 固定为接口测试用例资产列表页，承接查询、分页、新建、执行、加入套件、历史和删除等资产管理动作；旧 `InterfaceManagement.vue` 仅作为隐藏调试工作区复用，路径固定为 `/api-testing/test-cases/workspace?caseId={id}&projectId={projectId}`。
- 影响范围：接口自动化导航、路由、资产列表页、隐藏调试工作区、请求历史过滤和测试套件加入链路。
- 不再采用的替代方案：把旧树形调试工作台继续作为接口测试用例首页；用页面标题或菜单名称包装旧功能但不改变产品形态。

### 3.13 AI 生成接口测试用例只生成原子用例，不直接生成测试套件

- 决策时间：2026-06-18
- 背景：P0-2 讨论中发现，如果让 AI 同时兼顾接口测试用例字段和测试套件编排结构，会导致 Prompt、结果页展示、采纳落库和套件加入逻辑全部耦合，改动面过大，也会混淆接口自动化中“用例资产”和“套件编排”的对象边界。
- 决策内容：接口测试用例继续由 `ApiRequest` 承接，测试套件继续由 `TestSuite + TestSuiteRequest` 承接。AI 生成 `api_test_case` 时只输出 `ApiRequest` 兼容字段，例如 `name/method/url/headers/params/body/auth/assertions/pre_request_script/post_request_script`。生成结果先进入接口测试用例采纳链路，后续是否加入测试套件由用户在接口测试用例资产列表或套件页中操作。
- 影响范围：`docs/api-automation/api-automation-p0-2-ai-target-type-spec.md`、`GeneratedTestCaseList.vue`、P0-3 接口测试用例采纳、后续测试套件加入链路。
- 不再采用的替代方案：AI 直接生成 `TestSuite` / `TestSuiteRequest`；在接口测试用例生成结果里混入 `suite_id`、`suite_name`、`suite_order` 等套件编排字段；采纳接口测试用例时自动加入套件。

### 3.14 P0-2 只允许套用现有 AI 生成链路，禁止重写

- 决策时间：2026-06-18
- 背景：用户明确要求“当前的 AI 生成测试用例逻辑严禁更改，只需要套用进去”。P0-2 涉及目标类型、Prompt 选择和结果字段展示，容易被误扩张为重写 AI 生成系统。
- 决策内容：P0-2 只能在现有生成链路外层增加 `target_type`、按 `prompt_type + target_type` 选择 Prompt、任务固化目标类型、结果响应 / 页面展示字段适配和非功能采纳保护。禁止重写生成任务创建、模型调用、流式输出、取消、自动评审、轮询恢复和功能测试采纳主链。
- 影响范围：`apps/requirement_analysis`、`frontend/src/views/requirement-analysis/*`、P0-2 TDD / Execution 验证口径。
- 不再采用的替代方案：新建一条并行 AI 模型调用链；为了接口测试用例生成替换原功能测试生成解析路径；绕过既有 Prompt 配置和模型配置直接调用模型。

### 3.15 接口自动化阶段 A 不新增 ApiTestCase 表，优先补齐 ApiRequest / TestSuiteRequest 闭环

- 决策时间：2026-06-19
- 背景：阶段 A 的目标是修复用户已能看到但操作不闭环的接口自动化断点，包括移动集合、清空历史、套件级断言、负责人字段契约和删除风险提示。如果此时新增 `ApiTestCase` 表，会扩大迁移和采纳链路范围，并与当前 P0-1 已冻结的 `ApiRequest` 技术载体冲突。
- 决策内容：阶段 A 不新增 `ApiTestCase` 表，继续以 `ApiRequest` 作为接口测试用例原子资产，以 `TestSuite + TestSuiteRequest` 作为套件编排资产。移动集合落到 `ApiRequest.collection`；套件级断言落到 `TestSuiteRequest.assertions`；请求历史清空落到 `RequestHistory` 当前筛选范围。
- 影响范围：接口自动化 P0 对象闭环、P0-2 AI 目标类型字段契约、P0-3 接口测试用例采纳设计。
- 不再采用的替代方案：为了阶段 A 新增独立接口测试用例表；把接口测试用例和测试套件混成一个对象；让套件级断言继续作为“开发中”假入口。

### 3.16 接口自动化测试套件正式入口固定为 `/api-testing/test-suites`

- 决策时间：2026-06-19
- 背景：接口测试用例和测试套件功能页面已经存在，但侧边栏仍没有正式“测试套件”入口，旧 `/api-testing/automation` 继续作为可见入口，导致用户感知为“两个模块没有拆出来”。
- 决策内容：接口自动化侧边栏正式可见入口固定为 `/api-testing/test-cases` 和 `/api-testing/test-suites`；旧 `/api-testing/interfaces`、`/api-testing/automation` 仅作为隐藏兼容重定向保留。拆分用户可见子模块时，必须同步导航真源、路由、route meta、Dashboard 快捷入口、i18n 文案和文档。
- 影响范围：`frontend/src/config/navigation.js`、`frontend/src/router/index.js`、接口自动化 Dashboard、项目记忆、导航冻结文档、smoke 基线和后续接口自动化开发。
- 不再采用的替代方案：继续把 `/api-testing/automation` 作为侧边栏可见“自动化测试”入口；只新增路由或复用页面组件但不更新导航真源；用页面标题包装旧入口造成假拆分。

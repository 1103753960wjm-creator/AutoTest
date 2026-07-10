# TestHub 错误模式库与防复发手册

更新时间：2026-07-04

## 1. 文件职责

本文文件属于 C 层“正式项目记忆”，用于记录已经证明会重复出现、值得工程化防复发的错误模式。

本文不记录一次性噪音报错，不记录尚未确认根因的临时猜测。任意错误现场、命令失败、构建失败、接口异常、页面报错、控制台红错、验证失败、环境阻塞或规则执行偏差，应第一时间写入 `docs/project-memory/error_event_log.md`。

本文只记录已经确认根因、具备复发风险并能形成防复发规则的错误模式：

- 错误触发场景
- 根因分析
- 防复发规则
- 最低验证动作

使用原则：

- 进入任何开发任务前，必须先读取 `docs/project-memory/error_event_log.md` 与本文，确认本轮是否命中既有错误事件或错误模式
- 任意错误首次出现，必须先写入 `docs/project-memory/error_event_log.md`
- 同类错误第二次出现，或已经能稳定归纳为错误模式时，必须写入本文
- 错误事件升级为防复发规则后，应在 `error_event_log.md` 中标记“已沉淀”
- 若某条防复发规则已经升级为长期工程红线，应同步回写 `.cursor/*.md` 或局部 `AGENTS.md`
- 若本文与实际代码冲突，以实际代码为准，并及时回写本文
- 文档、日志、控制台输出、配置文件默认按 UTF-8 理解；出现乱码时先区分终端显示问题与文件本身编码问题

## 2. 建议记录模板

建议后续新增错误模式时保持以下结构：

- 错误标题
- 发生时间
- 错误类型
- 触发场景
- 根因分析
- 防复发规则
- 最低验证动作
- 关联文件

## 3. 已沉淀错误模式

### 001. keepAlive 页面重复请求

- 发生时间：2026-03-26 至 2026-04-19 多次暴露
- 错误类型：请求编排类
- 触发场景：页面存在 `keepAlive` 时，同时在 `onMounted`、`activated`、`watch(route.query)` 等多个入口重复拉取首屏数据
- 根因分析：页面没有把首屏数据请求收口到单一 `load/refresh` 入口，生命周期与路由监听并行触发了同一请求链
- 防复发规则：
  - `keepAlive` 页面首屏数据必须收口到单一 `load/refresh`
  - 禁止在多个生命周期和监听器里并行触发同一主请求链
  - 涉及任务、结果、详情联动时，优先按主键去重而不是靠页面文案提示“当前焦点”
- 最低验证动作：
  - 首次进入页面只发一次主请求
  - 返回页面后不重复发首屏请求
  - `query` 变化时只触发一次对应刷新
- 关联文件：
  - `frontend/src/views/requirement-analysis/RequirementAnalysisView.vue`
  - `frontend/src/views/requirement-analysis/TaskDetail.vue`
  - `frontend/AGENTS.md`

### 002. 超大 page_size 伪装分页，实为全量拉取

- 发生时间：2026-04-15 规则收口时集中识别
- 错误类型：请求编排类
- 触发场景：列表页或结果页为了省事，直接把 `page_size` 调到极大值，用一次性全量拉取代替正常分页
- 根因分析：页面职责与请求职责没有分清，把“临时方便”当成了可接受的长期实现
- 防复发规则：
  - 列表页默认使用真实分页
  - 结果页、任务页、日志页禁止用超大 `page_size` 替代正常分页
  - 如确需全量数据，必须明确说明对象规模、性能影响与替代方案不可行原因
- 最低验证动作：
  - 检查请求参数是否仍为正常分页
  - 检查翻页、筛选、删除后分页回退是否正常
  - 检查页面未出现“只靠前端截断的大列表假分页”
- 关联文件：
  - `.cursor/architecture.md`
  - `.cursor/storage_rules.md`
  - `frontend/AGENTS.md`

### 003. 任务对象、结果对象、正式资产对象边界混淆

- 发生时间：2026-03-26 至 2026-04-16 多次演进中反复暴露
- 错误类型：状态流转类
- 触发场景：`TaskDetail`、`GeneratedTestCaseList`、正式测试资产页之间互相越界，导致页面文案、数据过滤与真实对象边界不一致
- 根因分析：为了快速补链路，临时把结果处理逻辑塞回任务页，或让正式资产页伪装成结果层过滤页，破坏了对象分层
- 防复发规则：
  - 任务页只负责任务对象与结果入口
  - 结果批次页负责结果对象与处理状态
  - 正式资产页只轻量承接来源关系，不反向承担生成任务主战场职责
  - `sourceTaskId` 仅作来源上下文提示时，不得伪装成结果层过滤条件
- 最低验证动作：
  - 核对“任务页 -> 结果批次页 -> 正式资产页”三段页面文案与请求参数是否一致
  - 核对同一 `taskId` 下结果数量、状态摘要、正式资产入口是否对齐
  - 核对正式资产页未误按结果层语义过滤数据
- 关联文件：
  - `apps/requirement_analysis/AGENTS.md`
  - `docs/project-memory/module_memory.md`
  - `docs/overview/阶段2优化文档.md`

### 004. 终端乱码被误判为源文件编码损坏

- 发生时间：2026-04-15 至 2026-04-19 多次出现
- 错误类型：配置环境类
- 触发场景：读取规则文件、日志文件、更新日志时，控制台输出中文乱码，容易误判为源文件编码错误
- 根因分析：PowerShell / 受限语言模式下的控制台输出编码与文件实际 UTF-8 编码不一致，导致显示层乱码
- 防复发规则：
  - 默认将文档、日志、控制台输出、配置文件按 UTF-8 理解
  - 出现乱码时先区分“终端显示问题”与“文件本身编码问题”
  - 未确认源文件损坏前，禁止基于乱码现象批量重写文档
- 最低验证动作：
  - 交叉使用文件内容读取、关键字检索、结构校验确认源文件是否真实损坏
  - 修改前先确认乱码是否只出现在终端显示层
  - 修改后再复查关键标题、路径、规则索引是否可被正常检索
- 关联文件：
  - `copy.md`
  - `AGENTS.md`
  - `docs/project-memory/*.md`

### 005. 高风险改动未同步补最低验证动作

- 发生时间：长期风险，2026-04-19 规则增强时正式沉淀
- 错误类型：架构越界类
- 触发场景：修改登录、路由、状态流转、执行器、AI 接入方式后，只说明“已经改好”，没有同步补最小验证动作
- 根因分析：把“实现完成”误当成“交付完成”，忽略了高风险链路的验证闭环
- 防复发规则：
  - 高风险改动必须同时说明改动内容、影响范围、最低验证动作与未验证项
  - 只要改动登录、JWT、route meta、轮询、执行器、AI 链路，就默认视为高风险
  - 无法验证时必须明确说明原因，不能默认视为已验证
- 最低验证动作：
  - 至少列出主流程验证
  - 至少列出一个异常流程或回退场景
  - 明确哪些链路未验证以及原因
- 关联文件：
  - `AGENTS.md`
  - `.cursor/workflow_rules.md`
  - `docs/project-memory/task_handoff.md`

### 006. 页面主动作没有统一进入页头动作区，导致按钮乱放和重复入口

- 发生时间：2026-04-19 首次正式沉淀
- 错误类型：页面结构类
- 触发场景：同一个页面的主按钮一部分放在页头，一部分散落在内容区、说明卡片区或结果预览区，进一步导致同一个主动作出现两次甚至多次
- 根因分析：页面头部动作区已经存在可复用能力，但开发时没有把“正式主入口”统一收口进去，导致按钮跟着局部卡片一起长出来，最后出现位置不统一、重复入口和页面主次关系混乱
- 防复发规则：
  - 页面主动作默认统一进入页头动作区
  - 同一个主动作在同一页面里只保留一个正式入口
  - 内容区说明卡片可以保留提示文案，但不要再平行放一套同功能按钮
  - 若页面职责已经明确为“对象信息 + 预览 + 跳转入口”，则正式处理按钮应收口到页头，不继续散落在局部模块里
- 最低验证动作：
  - 检查页头动作区是否已承接页面主按钮
  - 检查同一个主动作在页面中是否只保留一个正式入口
  - 检查内容区是否只保留说明文案，没有再平行放置重复按钮
  - 检查按钮迁移后点击行为、跳转参数和来源回跳未受影响
- 关联文件：
  - `frontend/src/layout/components/PlatformPageHeader.vue`
  - `frontend/src/layout/usePlatformPageHeader.js`
  - `frontend/src/views/requirement-analysis/TaskDetail.vue`
  - `frontend/src/views/testcases/TestCaseList.vue`

### 007. Vue 3 `<router-view>` 插槽内 `v-if` 引发组件卸载时上下文丢失报错

- 发生时间：2026-05-30
- 错误类型：框架底层崩溃类
- 触发场景：在 `<router-view v-slot="{ Component }">` 内，为了按需缓存组件，使用了 `v-if="keepAlive"` 与 `v-if="!keepAlive"` 分别包裹 `<keep-alive>` 与非缓存容器。当路由切换时抛出 `TypeError: Cannot read properties of null (reading 'exposed')` 或 `reading 'parentNode'`，导致整个页面失去响应卡死。
- 根因分析：此为 Vue 3 核心已知缺陷（Bug #6222）。在 router-view 插槽中由于路由切换触发 VNode 重新 patched 时，若使用了 `v-if` 条件渲染销毁了组件所在的容器节点，将导致被销毁节点内部（特别是包含 `ref="xxx"` 字符串引用的 Element Plus 组件如 `el-table` 或表单）在执行 `setRef(null)` 释放引用时，由于父上下文 `vnode.component` 已经丢失（null），强行访问其 `.exposed` 属性抛出致命异常。
- 防复发规则：
  - **绝对禁止**在 `<router-view>` 插槽内使用 `v-if` 动态包裹 `<keep-alive>` 容器。
  - 按需缓存必须且只能使用 `<keep-alive :include="cachedViewsArray">` 的标准白名单模式。
  - 对于组件频繁挂载卸载的场景，彻底废弃模版字符串引用（如 `ref="tableRef"`），必须改为函数式引用（如 `:ref="(el) => tableRef.value = el"`），可天然免疫销毁时的组件上下文空指针异常。
- 最低验证动作：
  - 点击左侧侧边栏高频切换拥有表格和表单的不同路由模块。
  - 观察控制台无任何 `reading 'exposed'` 和 `reading 'parentNode'` 红错。
  - 确保页面正常渲染，滚动重置等基于 `nextTick()` 的后续逻辑未被异常打断。
- 关联文件：
  - `frontend/src/layout/index.vue`
  - `frontend/src/components/platform-shared/UnifiedListTable.vue`

### 008. Vue 3 Props 验证抛出 `Cannot convert object to primitive value`

- 发生时间：2026-05-30
- 错误类型：组件类型验证类
- 触发场景：切换含有特定通用组件（如 `UnifiedListTable`）的页面时，控制台抛出 `TypeError: Cannot convert object to primitive value` 且附带组件 Prop 验证栈。
- 根因分析：在定义 Vue 3 组件的 `props` 时，将 `null` 直接放入了 `type` 数组中（例如 `type: [String, Number, null]`）。Vue 的底层 Prop 验证器 `_validator` 会遍历 `type` 数组并尝试将其作为构造器调用（或通过内置类型检查机制执行）。由于 `null` 并不是一个合法的类型构造器，从而抛出致命报错打断渲染。
- 防复发规则：
  - **绝对禁止**在 Vue 组件的 `props` 声明中将 `null` 放入 `type` 数组。
  - 若需要允许传入 `null` 或 `undefined`，只需声明合法的基本类型构造器（如 `type: [String, Number]`），然后通过设置 `default: null` 或 `required: false`，Vue 会自动允许空值，不需要显式指定 `null` 类型。
- 最低验证动作：
  - 审计通用组件（尤其是跨页面复用组件）的 Prop 类型声明。
  - 页面初次挂载及数据被置空时，控制台无任何 Prop Validator 报错红错。
- 关联文件：
  - `frontend/src/components/platform-shared/UnifiedListTable.vue`

### 009. router-view key 使用 fullPath 导致全局导航失灵

- 发生时间：2026-05-31
- 错误类型：框架底层交互类
- 触发场景：在 `<router-view>` 中对 `<component>` 绑定 `:key="currentRoute.fullPath"` 时，同一路由名下只要 query 参数变化就触发组件销毁重建。配合 `keep-alive` 使用时，include 白名单基于组件 name 匹配，但 key 基于 fullPath 不断创建新实例，导致缓存实例堆积、Vue 内部事件系统异常，最终表现为侧边栏和按钮点击后无响应，需要页面重载才能恢复。
- 根因分析：`keep-alive` 的 `include` 匹配维度（组件 name）与 `router-view` 的 `:key` 维度（fullPath）不一致，导致同名组件被认为"可缓存"但 key 不同又触发重建，形成缓存与重建互相冲突的死循环。
- 防复发规则：
  - `router-view` 内 `component` 的 `:key` 必须与 `keep-alive` 的 `include` 匹配维度一致，推荐使用 `currentRoute.name || currentRoute.path`
  - query 变化应由组件内部 `watch(route.query)` 自行处理，不应通过外层 key 变化触发组件销毁重建
  - 禁止使用 `currentRoute.fullPath` 作为 key，除非明确不使用 keep-alive
- 最低验证动作：
  - 快速多次点击侧边栏不同菜单项，确认无卡死
  - 在同一路由下修改 query 参数，确认组件未被销毁重建
  - 确认 keep-alive 缓存的页面返回后状态保持
- 关联文件：
  - `frontend/src/layout/index.vue`

### 010. 列表页筛选控件在 flex 布局下宽度塌缩

- 发生时间：2026-05-31
- 错误类型：页面结构类
- 触发场景：`ListShell` 的 `#filters` 插槽内使用 `el-row` + `el-col` 布局筛选控件时，`el-select` 和 `el-input` 未设置 `width: 100%`，且 `el-col` 的 span 分配过小（如 3/4/5），导致控件宽度塌缩为内容最小宽度，看起来像空矩形或微型输入框。
- 根因分析：`shell-filters` 容器是 flex 布局，`el-row` 在 flex 容器中需要明确宽度才能正确展开。`el-select` 默认不会自动撑满父容器宽度，需要显式设置 `width: 100%`。
- 防复发规则：
  - 在 `ListShell` 的 `#filters` 插槽中使用 `el-row` 布局时，所有 `el-select` 和 `el-input` 必须设置 `style="width: 100%"`
  - `el-col` 的 span 分配应参考评审列表的标准样式（每列 span 8），不应小于 6
  - 新增列表页筛选区时，必须与评审列表 `ReviewList.vue` 对齐样式口径
- 最低验证动作：
  - 检查筛选控件是否正确撑满列宽
  - 检查 placeholder 文字是否完整显示
  - 与评审列表页面对比视觉一致性
- 关联文件：
  - `frontend/src/views/testcases/TestCaseList.vue`
  - `frontend/src/views/versions/VersionList.vue`
  - `frontend/src/views/reviews/ReviewList.vue`（标准参考）
  - `frontend/src/components/page-shells/ListShell.vue`

### 011. 根层 router-view key 粒度错误导致跨模块导航队列被打断

- **发生时间**：2026-06-01，2026-06-16 复现并修正防复发规则
- **错误类型**：框架底层交互类
- **现象**：侧边栏切换同一业务模块下的不同子页面时，页面会明显闪烁、停在旧内容，或像必须刷新页面后才切换成功；跨顶部大模块后立即点击侧边栏子模块时，页面容易停在大模块默认页，用户体感像“卡住后刷新才恢复”。
- **根因分析**：`App.vue` 根层 `<router-view>` 按业务模块或物理路由加 key 时，跨顶部大模块会销毁整套 `Layout`。销毁期间 `layout/index.vue` 内部的导航队列、乐观模块状态、侧边栏 DOM 和 Element Plus 菜单事件都会被打断；用户在这个窗口内快速点击侧边栏，点击可能落在刚被销毁或刚重建的菜单上，最终只完成顶部模块跳转，没有完成子模块跳转。
- **防复发规则**：
  - 登录后业务页面必须共用稳定的根层 Layout key，例如 `layout:authenticated`；禁止按 `route.meta.module`、物理顶层路由、`fullPath`、`params` 等维度销毁整套平台壳。
  - 模块切换时只允许更新 `layout/index.vue` 内部的模块态、侧边栏菜单态和内容路由，不应销毁根层 Layout。
  - 登录页、注册页等非登录后壳层页面仍可使用独立 key，避免认证页与业务平台壳互相复用。
  - 业务内容层 `layout/index.vue` 可以继续使用 `:key="currentRoute.name || currentRoute.path"`，该 key 必须与 `<keep-alive :include="cachedViews">` 的路由名称维度保持一致。
  - 顶部模块、侧边栏、全局搜索、最近访问和收藏入口必须共用同一套导航调度器；快速点击时，重复目标和当前路径应直接忽略，被后续点击取消的导航属于正常现象，不应输出红错或触发整页刷新兜底。
  - 路由切换动画应轻量，优先使用短时长 `opacity + translateY`，避免大横向位移制造“页面重载”的体感。
- **最低验证动作**：
  - 从 `/ui-automation/*` 切到 `/ai-intelligent-mode/*`，确认 Layout 不被整套重建，页面内容正常切换。
  - 从接口自动化、Web 自动化、App 自动化、配置中心等顶部大模块互相切换后，立即点击当前模块侧边栏，最终应停在最后点击目标，且无 `beforeunload`、`pagehide` 或主文档请求。
  - 几秒内快速点击多个侧边栏子模块，确认最终停在最后点击的菜单，控制台无 `Navigation cancelled`、`parentNode`、`exposed` 等红错。
  - 搜索、收藏、最近访问和顶部模块入口仍能通过统一路由链正常跳转。
- **关联文件**：
  - `frontend/src/App.vue`
  - `frontend/src/layout/index.vue`

### 012. 环境变量非法值和生产安全兜底导致启动状态不可信

- **发生时间**：2026-06-14
- **错误类型**：配置安全类
- **触发场景**：终端环境变量 `DEBUG=release` 覆盖 `.env` 后，Django 在布尔转换阶段抛出底层 `ValueError`；生产环境未配置 CORS 时，旧逻辑会默认放开全部来源。
- **根因分析**：配置读取直接依赖第三方布尔转换，缺少项目级错误提示；生产环境把“方便启动”的兜底当成了长期默认安全策略。
- **防复发规则**：
  - 关键布尔配置必须使用项目内统一解析函数，非法值直接抛出清晰配置错误。
  - 生产环境必须显式配置 `ALLOWED_HOSTS` 和 `CORS_ALLOWED_ORIGINS`，不得默认使用 `*` 或放开所有来源。
  - API CSRF 全局禁用必须由 `DISABLE_CSRF_FOR_API` 显式控制，并且生产环境禁止开启。
- **最低验证动作**：
  - `DEBUG=True` 时执行 `manage.py check` 应通过。
  - `DEBUG=release` 时执行 `manage.py check` 应明确提示 `DEBUG` 非法。
  - `DEBUG=False` 且缺少 `CORS_ALLOWED_ORIGINS` 时应启动失败。
  - `DEBUG=False` 且 `DISABLE_CSRF_FOR_API=True` 时应启动失败。
- **关联文件**：
  - `backend/settings.py`
  - `backend/middleware.py`
  - `.env.example`

### 013. 认证失效跳转散写浏览器跳转导致整页刷新体感

- **发生时间**：2026-06-16
- **错误类型**：认证导航一致性类
- **触发场景**：`userStore.logout()`、axios 401 拦截器或其他认证失效分支中直接调用 `window.location.href = '/login'`，导致绕开 Vue Router，产生整页刷新体感，并让历史记录、全局导航监控和平台壳状态不可控。
- **根因分析**：认证跳转属于全局路由行为，散写浏览器跳转会与 SPA 导航链路并行，后续任何一个分支忘记同步修改都会重新引入刷新、重复跳转或登录页历史记录异常。
- **防复发规则**：
  - 认证失效、退出登录、refresh token 失败后回登录页，统一调用 `frontend/src/utils/authNavigation.js` 的 `redirectToLogin()`。
  - `frontend/src/router/index.js` 必须在 router 创建后调用 `setAuthRouter(router)`。
  - 除无法使用 router 的兜底层外，禁止在 store、api 拦截器和页面中直接写 `window.location.href`、`window.location.assign` 或 `location.replace('/login')`。
- **最低验证动作**：
  - 执行 `node --check frontend/src/stores/user.js frontend/src/utils/api.js frontend/src/utils/authNavigation.js frontend/src/router/index.js`。
  - 人工或浏览器验证退出登录、401 刷新失败后能回到 `/login`，且无额外整页刷新兜底。
- **关联文件**：
  - `frontend/src/utils/authNavigation.js`
  - `frontend/src/stores/user.js`
  - `frontend/src/utils/api.js`
  - `frontend/src/router/index.js`

### 014. 前端继续使用 xlsx 导出导致安全风险回归

- **发生时间**：2026-06-16
- **错误类型**：依赖安全类
- **触发场景**：前端页面或文档模板继续 `import * as XLSX from 'xlsx'`，即使 `package.json` 已移除该依赖，也可能在后续复制模板时重新引回存在高危漏洞且无修复版本的导出库。
- **根因分析**：旧导出逻辑分散在多个页面，且文档模板中保留了 `xlsx` 示例；如果只改业务页面、不改模板和规则，新页面开发会继续复制旧依赖。
- **防复发规则**：
  - 前端 Excel 导出统一使用 `frontend/src/utils/excelExport.js`。
  - 新页面和文档模板禁止引入 `xlsx`。
  - 如需新增导出能力，只允许在统一工具层扩展，不在页面内手写 workbook / worksheet 细节。
- **最低验证动作**：
  - 执行 `rg -n "from 'xlsx'|from \\\"xlsx\\\"|XLSX" frontend docs`，确认没有新增业务代码或模板引用。
  - 执行 `npm audit --omit=dev`，确认生产依赖漏洞未回归。
  - 执行 `cd frontend && cmd /c npm run build`，确认导出工具可打包。
- **关联文件**：
  - `frontend/package.json`
  - `frontend/src/utils/excelExport.js`
  - `frontend/src/views/testcases/TestCaseList.vue`
  - `frontend/src/views/requirement-analysis/RequirementAnalysisView.vue`
  - `frontend/src/views/requirement-analysis/TaskDetail.vue`

### 015. 页面头部 actions 传入 computed 或非数组导致布局崩溃

- **发生时间**：2026-06-16
- **错误类型**：全局页面壳兼容类
- **触发场景**：页面通过 `usePlatformPageHeader()` 注入页头动作时，`actions`、`statusTags`、`metaItems` 可能来自 computed/ref 或异常非数组值；旧逻辑直接 `.map()` 会导致运行时错误，进而打断页面切换。
- **根因分析**：平台页头控制器属于跨页面共享入口，不能假设所有消费端都传入普通数组；需要在统一入口中解包 `ref/computed` 并做数组兜底。
- **防复发规则**：
  - `usePlatformPageHeader` 的 normalize 层必须对所有字段执行 `unref`。
  - `actions`、`statusTags`、`metaItems` 必须统一兜底为数组，页面侧传错值时不能拖垮 Layout。
  - 新增页头字段时必须在 normalize 层补充类型兜底。
- **最低验证动作**：
  - 构建级验证 `cd frontend && cmd /c npm run build`。
  - 页面级验证切换使用动态页头动作的列表页、详情页、配置页，控制台无 `actions.map is not a function` 或类似红错。
- **关联文件**：
  - `frontend/src/layout/usePlatformPageHeader.js`
  - `frontend/src/layout/index.vue`

### 016. 前端 API 封装旧路径与后端真实路由漂移导致接口闭环断裂

- **发生时间**：2026-06-17
- **错误类型**：前后端契约漂移类
- **触发场景**：接口自动化真实后端路由已经是 `/api-testing/requests/{id}/execute/` 和 `/api-testing/test-executions/{id}/`，但前端封装仍保留 `/api-testing/api-requests/{id}/execute/` 与 `/api-testing/executions/{id}/`，后续页面复用封装会直接 404。
- **根因分析**：接口自动化历史命名从“接口管理 / API 请求”演进到“接口测试用例”时，只改了部分页面直连路径，没有同步收口 `frontend/src/api/api-testing.js` 这个可复用封装真源。
- **防复发规则**：
  - 接口自动化新增或修改页面时，必须优先检查 `frontend/src/api/api-testing.js` 是否与 `apps/api_testing/urls.py` 的真实 router 注册一致。
  - 新页面不得绕过 `frontend/src/api/api-testing.js` 直接导入 `@/utils/api`。
  - 接口测试用例语义可以使用 `getApiTestCases`、`executeApiTestCase` 等别名，但底层必须继续指向 `/api-testing/requests/`。
  - 旧入口 `/api-testing/interfaces` 只能做隐藏兼容，不得重新成为唯一正式入口。
- **最低验证动作**：
  - 执行 `rg -n "/api-testing/api-requests|/api-testing/executions/|collections/search" frontend/src apps/api_testing`。
  - 执行 `rg -n "from '@/utils/api'|import api from '@/utils/api'|api\\.(get|post|put|patch|delete)" frontend/src/views/api-testing/InterfaceManagement.vue frontend/src/api/api-testing.js`。
  - 执行 `cd frontend && cmd /c npm run build`。
- **关联文件**：
  - `frontend/src/api/api-testing.js`
  - `frontend/src/views/api-testing/InterfaceManagement.vue`
  - `apps/api_testing/urls.py`
  - `frontend/src/router/index.js`
  - `frontend/src/config/navigation.js`

### 017. 执行响应临时补断言结果但不落库导致请求历史断链

- **发生时间**：2026-06-17
- **错误类型**：结果持久化类
- **触发场景**：单接口执行接口返回体中手动追加了 `assertions_results`，页面当次能看到断言结果，但 `RequestHistory.objects.create()` 没有写入 `assertions_results` 字段，刷新后请求历史详情看不到断言结果。
- **根因分析**：响应组织和数据库真源混淆，把“当次接口返回给前端”误当成“执行结果已闭环保存”。请求历史的真源是 `RequestHistory.assertions_results`，不能只依赖临时响应字段。
- **防复发规则**：
  - 任何执行结果字段只要要在历史页、报告页或后续回放中展示，必须写入对应结果模型，不能只拼到响应体。
  - 单接口执行、套件执行和工具层执行如果都产生断言结果，应分别核对 `RequestHistory.assertions_results` 的落库路径。
  - 修执行接口时必须同步打开历史页 serializer，确认字段在响应中可读。
  - 请求历史详情页必须真实渲染 `assertions_results`，否则“落库成功但用户看不到”仍然不算闭环。
- **最低验证动作**：
  - 执行 `python -m py_compile apps\\api_testing\\models.py apps\\api_testing\\serializers.py apps\\api_testing\\views.py apps\\api_testing\\urls.py`。
  - 创建带状态码断言的接口测试用例并执行，检查最新 `RequestHistory.assertions_results` 非空。
  - 打开请求历史详情，确认断言结果可展示。
- **关联文件**：
  - `apps/api_testing/views.py`
  - `apps/api_testing/models.py`
  - `apps/api_testing/serializers.py`
  - `frontend/src/views/api-testing/RequestHistory.vue`

### 018. 侧边栏多事件触发与导航队列阻塞导致快速跨模块切换卡住

- **发生时间**：2026-06-17
- **错误类型**：平台壳导航竞态类
- **触发场景**：用户在几秒内连续执行“顶部大模块切换 -> 侧边栏子模块切换”，例如接口自动化切到 Web 自动化、App 自动化，再快速点接口自动化下的“接口测试用例 / 请求历史 / 测试套件”。现场表现为侧边栏已经变成新模块，但页面内容和 URL 停在旧路由，随后浏览器可能出现整页 reload，用户体感为“卡住后刷新才正常”。
- **根因分析**：
  - `PlatformSidebar.vue` 同时在 `pointerdown.capture`、`click.capture` 和 `el-menu @select` 中触发导航，一次点击会发出 2 到 3 次导航请求。
  - `layout/index.vue` 旧导航调度使用 `pendingNavigationPath + queuedNavigationRequest` 队列模型。快速切换时，旧导航长期占着 pending，新点击被压入队列，侧栏又基于乐观模块先切换，导致“侧栏显示新模块、真实路由仍停旧页”的不一致。
  - 重叠导航完成顺序不稳定，旧路由 `afterEach` 还可能晚于新路由写入 `document.title`，造成 URL 和页面内容已正确但浏览器标题残留旧页面。
- **防复发规则**：
  - 侧边栏只允许保留一个正式导航触发源，当前固定为 `el-menu @select`；禁止再次添加 `pointerdown/click` 捕获层来抢跑导航。
  - `layout/index.vue` 的统一导航调度器必须采用“最后一次点击优先”模型；被后续点击取消的旧导航属于正常现象，不应阻塞最新目标。
  - `pendingNavigationPath` 只能作为当前导航态提示，不能成为拦截最新点击的全局锁。
  - `router.afterEach` 写 `document.title` 前必须确认 `router.currentRoute.value.fullPath` 仍等于本次 `to.fullPath`，避免旧导航晚到覆盖新页面标题。
  - 禁止用 `window.location.reload()` 或浏览器跳转兜底平台导航状态。
- **最低验证动作**：
  - 执行 `cd frontend && cmd /c npm run build`。
  - 用浏览器快速执行“Web 自动化 -> 多个侧栏子模块 -> App 自动化 -> 多个侧栏子模块 -> 接口自动化 -> 接口测试用例 -> 请求历史 -> 测试套件 -> 请求历史”。
  - 验证最终 URL、浏览器标题、顶部模块高亮、侧栏高亮和页面正文都停在最后点击目标。
  - 验证切换期间没有 `beforeunload`、`pagehide`、`visibilitychange(hidden)` 和主文档请求；允许出现被取消的旧 chunk/API 请求，但不能出现业务红错。
- **关联文件**：
  - `frontend/src/layout/index.vue`
  - `frontend/src/layout/components/PlatformSidebar.vue`
  - `frontend/src/router/index.js`

### 019. 表单默认提交导致整页刷新体感

- **发生时间**：2026-06-17
- **错误类型**：SPA 默认浏览器行为类
- **触发场景**：用户在页面表单中按 Enter，或点击未声明 `type` 的原生 `<button>`，浏览器按原生表单提交处理当前页面，导致当前 URL 被重新请求；用户体感是页面突然卡住、整页刷新，刷新后导航和子模块切换才恢复正常。
- **根因分析**：
  - Element Plus 的 `<el-form>` 实际渲染为原生 `<form>`，如果没有 `@submit.prevent`，仍会触发浏览器默认提交。
  - 原生 `<button>` 在表单上下文中默认等价于 `type="submit"`，没有显式 `type` 时会意外提交外层表单。
  - SPA 页面本应由 Vue Router 和业务方法控制状态流转，默认表单提交会绕开前端路由、导航调度器、请求拦截器和页面状态管理。
- **防复发规则**：
  - 所有 Vue 模板中的 `<form>` 与 `<el-form>` 必须显式添加 `@submit.prevent`。
  - 所有原生 `<button>` 必须显式声明 `type="button"`；只有明确存在表单提交处理链路时才允许 `type="submit"`。
  - 禁止用浏览器默认提交、当前 URL 重新请求或整页刷新来兜底业务动作。
  - 新增表单页、弹窗表单、筛选区和自定义按钮时，必须同步检查 Enter 键、快速点击和按钮默认类型。
- **最低验证动作**：
  - 静态扫描 `frontend/src/**/*.vue`，确认不存在缺少 `@submit.prevent` 的 `<form>` / `<el-form>`。
  - 静态扫描 `frontend/src/**/*.vue`，确认不存在缺少显式 `type` 的原生 `<button>`。
  - 执行 `git diff --check -- frontend/src`。
  - 执行 `cd frontend && cmd /c npm run build`。
- **关联文件**：
  - `frontend/AGENTS.md`
  - `frontend/src/views/**/*.vue`

### 020. keepAlive 工作区只在 mounted 读取 query 导致深链目标不切换

- **发生时间**：2026-06-17
- **错误类型**：SPA 深链状态同步类
- **触发场景**：从接口测试用例列表连续点击不同用例进入 `/api-testing/test-cases/workspace?caseId=...`，由于工作区页面被 `keepAlive` 缓存，组件不会重新 `mounted`，如果只在首次加载时读取 `route.query.caseId`，页面会停留在旧用例或找不到非默认项目下的目标用例。
- **根因分析**：
  - `keepAlive` 缓存页面不会因为同一路由组件的 query 变化自动销毁重建。
  - 外层 `router-view` key 已按路由名稳定化，业务详情切换必须由页面内部监听 `route.query` 完成。
  - 接口测试用例的项目归属来自 `ApiCollection`，如果列表跳转不携带 `projectId`，隐藏工作区默认加载第一个项目时可能无法在树中找到目标 `caseId`。
- **防复发规则**：
  - `keepAlive` 工作区或详情页如果通过 query/params 标识目标对象，必须监听目标 id 变化并主动刷新或重选对象。
  - 列表页跳转到需要项目上下文的工作区时，必须同时传递目标对象 id 与所属项目 id。
  - 工作区树或侧栏列表可能只加载当前分页数据，深链目标不能只依赖树节点命中；树中找不到时应按对象 id 直接拉取详情。
  - 详情加载要具备旧响应丢弃或等价的“最后一次目标优先”机制，避免快速点击时旧详情晚返回覆盖新目标。
  - 禁止通过改外层 `router-view` key、整页刷新或销毁整套 Layout 来兜底业务对象切换。
- **最低验证动作**：
  - 从列表连续打开两个不同接口测试用例，确认工作区最终显示最后点击的用例。
  - 打开非默认项目下的接口测试用例，确认工作区会切到对应项目并选中目标节点。
  - 快速连续点击多个用例或返回列表后再进工作区，确认没有旧详情覆盖新详情。
- **关联文件**：
  - `frontend/src/views/api-testing/ApiTestCaseList.vue`
  - `frontend/src/views/api-testing/InterfaceManagement.vue`
  - `frontend/src/router/index.js`

### 021. Element Plus 服务式组件未引入样式导致弹窗裸样式

- **发生时间**：2026-06-17
- **错误类型**：前端组件样式按需加载类
- **触发场景**：页面直接调用 `ElMessageBox.alert()` 作为弹窗反馈时，弹窗出现在页面异常位置、没有遮罩和按钮样式，看起来像裸 HTML，而模板中的 `<el-dialog>` 又能正常显示。
- **根因分析**：
  - 项目使用 `unplugin-vue-components` + `ElementPlusResolver({ importStyle: 'css' })` 按需为模板组件注入样式。
  - `ElMessageBox`、`ElMessage`、`ElLoading` 等是服务式 JS API，不一定会被模板组件解析器自动发现并补齐 CSS。
  - 服务组件样式缺失时，DOM 类名存在，但 `.el-message-box`、`.el-overlay-message-box` 等样式规则没有进入运行时，导致弹窗不居中、无遮罩或样式异常。
- **防复发规则**：
  - 使用 Element Plus 服务式 API 前，必须确认全局入口显式引入对应服务样式。
  - 当前已在 `frontend/src/main.js` 引入：
    - `element-plus/es/components/loading/style/css`
    - `element-plus/es/components/message/style/css`
    - `element-plus/es/components/message-box/style/css`
  - 后续若新增 `ElNotification` 等服务式 API，也要同步补对应 style import。
  - 不要为了修单个页面弹窗样式，在业务页面散写 `.el-message-box` 覆盖样式；优先补齐官方组件样式入口。
- **最低验证动作**：
  - 执行 `cd frontend && cmd /c npm run build`。
  - 浏览器运行时检查 CSSOM 中可检索到 `.el-message-box` 与 `.el-overlay-message-box` 样式规则。
  - 实际触发一次 `ElMessageBox.alert/confirm`，确认弹窗居中、有遮罩、有按钮样式。
- **关联文件**：
  - `frontend/src/main.js`
  - `frontend/src/views/api-testing/ApiTestCaseList.vue`
  - `frontend/AGENTS.md`

### 022. 关键闭环动作只给底部弱提示或静默失败

- **发生时间**：2026-06-17
- **错误类型**：交互反馈闭环类
- **触发场景**：接口测试用例列表点击“加入套件”后，用户可能看到页面底部弱提示，或者在无可用套件、加载失败、未选择套件等场景下误以为点击没有反应。
- **根因分析**：
  - “加入套件”是跨对象状态变更动作，用户需要明确知道是否成功、为什么被阻断、下一步该怎么处理。
  - 行内按钮如果没有阻止表格行事件冒泡，可能与行双击、行点击等行为互相干扰，造成跳转或反馈不稳定。
  - 加载套件期间如果不禁用选择和确认按钮，用户可能重复点击或在数据未就绪时提交。
  - 对阻断型和结果确认型反馈使用 `ElMessage` 这类短暂弱提示，容易被页面滚动、视线焦点或遮罩层影响，用户体感仍是“没有反应”。
- **防复发规则**：
  - 跨对象状态变更动作必须有明确成功、失败和阻断原因反馈。
  - 阻断型、需要用户确认已知晓的反馈优先使用 `ElMessageBox.alert`；高风险删除继续使用 `ElMessageBox.confirm`。
  - 行内操作按钮必须使用 `@click.stop`，避免触发表格行点击、双击或展开行为。
  - 异步加载依赖数据时必须有 loading 态，并在 loading 或无可用数据时禁用提交按钮。
  - 成功后如关闭原弹窗再展示结果弹窗，要先清理按钮 loading 状态，避免弹窗叠加时原按钮仍在转圈。
- **最低验证动作**：
  - 主流程：选择可用套件并加入成功，出现“加入成功”弹窗。
  - 异常流程：无集合、无可用套件、套件加载失败、未选择套件、接口返回失败时均有明确弹窗提示。
  - 快速点击行操作时不会触发列表行双击跳转，最终仍停在用户操作目标。
  - 执行 `cd frontend && cmd /c npm run build`。
- **关联文件**：
  - `frontend/src/views/api-testing/ApiTestCaseList.vue`
  - `frontend/src/api/api-testing.js`

### 023. AI 生成接口测试用例时混入测试套件编排字段

- **发生时间**：2026-06-18
- **错误类型**：对象边界混淆类
- **触发场景**：在设计 P0-2 AI 生成目标类型时，把“接口测试用例”和“测试套件”混成一个生成目标，试图让 AI 同时输出接口请求字段和套件编排字段。
- **根因分析**：接口自动化里 `ApiRequest` 是原子接口用例资产，`TestSuite + TestSuiteRequest` 是编排资产。AI 生成阶段如果直接生成套件，会导致 Prompt、结果展示、采纳落库和加入套件动作全部耦合，扩大改动面并破坏 P0-1 已冻结的资产列表心智。
- **防复发规则**：
  - `api_test_case` AI 结果只允许生成 `ApiRequest` 兼容字段，例如 `name/method/url/headers/params/body/auth/assertions/pre_request_script/post_request_script`。
  - 禁止在 P0-2 结果中混入 `suite_id`、`suite_name`、`suite_order` 等套件编排字段。
  - 接口测试用例采纳入库后，是否加入测试套件由接口测试用例列表或套件页的显式动作承接。
  - P0-2 不创建、不修改 `TestSuite` / `TestSuiteRequest`。
- **最低验证动作**：
  - 检查 `api_test_case` 结果响应中的 `normalized_payload`，确认只包含接口用例字段。
  - 静态检索 P0-2 改动中是否新增对 `TestSuite` / `TestSuiteRequest` 的写入。
  - 页面验证接口测试用例结果页没有把“加入套件”伪装成 AI 自动生成完成动作。
- **关联文件**：
  - `docs/api-automation/api-automation-p0-2-ai-target-type-spec.md`
  - `docs/api-automation/api-automation-p0-2-ai-target-type-tdd.md`
  - `apps/api_testing/models.py`
  - `apps/requirement_analysis/views.py`

### 024. P0-2 为目标类型需求重写现有 AI 生成主链

- **发生时间**：2026-06-18
- **错误类型**：高风险链路越界类
- **触发场景**：实现 AI 生成目标类型下拉时，为了支持接口测试用例字段，重写生成任务创建、模型调用、流式输出、取消、自动评审、轮询恢复或功能测试采纳链路。
- **根因分析**：用户已明确要求当前 AI 生成测试用例逻辑严禁更改，只需要套用进去。P0-2 的真实目标是增加目标类型、Prompt 按类型选择和结果字段适配，不是重做 AI 生成系统。
- **防复发规则**：
  - P0-2 只能在现有链路外层增加 `target_type`、Prompt 过滤、任务固化和结果展示适配。
  - 功能测试用例的旧生成、旧解析和旧采纳路径必须保持原行为。
  - 接口测试用例字段归一化必须放在目标类型分支或适配层，不能替换原功能测试解析主路径。
  - 禁止新增绕开既有模型配置、Prompt 配置和生成配置的并行 AI 调用入口。
- **最低验证动作**：
  - 回归默认功能测试生成、结果展示、单条采纳和批量采纳。
  - 检查 P0-2 改动没有新增并行模型调用入口。
  - 检查取消生成、自动评审、任务轮询恢复仍走原任务链路。
  - 执行后端编译、迁移计划和前端构建验证。
- **关联文件**：
  - `docs/api-automation/api-automation-p0-2-ai-target-type-spec.md`
  - `apps/requirement_analysis/models.py`
  - `apps/requirement_analysis/views.py`
  - `frontend/src/views/requirement-analysis/RequirementAnalysisView.vue`
  - `frontend/src/views/requirement-analysis/GeneratedTestCaseList.vue`

### 025. 页面按钮存在但后端未闭环，形成“假入口”

- **发生时间**：2026-06-19
- **错误类型**：对象闭环缺失类
- **触发场景**：请求历史页存在“清空历史”按钮但只提示未实现；测试套件页存在“编辑断言”按钮但只提示功能开发中。用户点击后没有真实后端状态变化，也不能在页面刷新后查回结果。
- **根因分析**：页面入口、模型字段和真实后端动作没有一起设计。按钮先于闭环落地，后续又没有在 VDD 阶段检查“是否真实落库 / 是否可查回 / 是否有异常反馈”。
- **防复发规则**：
  - P0 页面禁止保留“功能开发中”“暂未实现”这类假入口。
  - 用户可见按钮必须至少满足一种状态：真实实现、隐藏、禁用并解释原因。
  - 涉及数据变化的按钮必须有真实后端接口、权限校验、落库或删除动作、成功刷新和失败反馈。
  - 交付前必须静态检索 `功能开发中|开发中|clearNotImplemented|featureInDevelopment|assertionDeveloping`。
- **最低验证动作**：
  - 点击主流程按钮，确认发出真实后端请求。
  - 刷新页面后确认结果仍可查回。
  - 制造失败场景，确认页面不展示假成功。
  - 执行静态检索确认 P0 页面无假入口文案。
- **关联文件**：
  - `frontend/src/views/api-testing/RequestHistory.vue`
  - `frontend/src/views/api-testing/AutomationTesting.vue`
  - `apps/api_testing/views.py`

### 026. 清空类操作未按筛选范围和权限收口导致误删风险

- **发生时间**：2026-06-19
- **错误类型**：数据删除范围类
- **触发场景**：请求历史“清空历史”如果只按前端当前页、只按页签文案或直接全量删除，会误删其他项目、其他用例或用户无权限的数据。
- **根因分析**：清空操作比普通删除风险更高，必须以后端可见 queryset 为权限边界，再叠加当前筛选参数。前端确认文案也必须告诉用户清空的是哪个范围。
- **防复发规则**：
  - 清空类接口必须从当前用户可见 queryset 出发，不直接 `Model.objects.all().delete()`。
  - 前端必须传递当前筛选条件，确认文案必须说明清空范围。
  - 清空成功后必须刷新真实列表和分页，不只清空前端数组。
  - 清空失败时不得改变当前列表。
- **最低验证动作**：
  - 按对象过滤清空，确认范围外数据仍存在。
  - 按页签 / 状态 / 搜索清空，确认删除数量符合筛选。
  - 无权限数据不能被传参误删。
  - 重复点击清空按钮时不会重复提交或状态错乱。
- **关联文件**：
  - `apps/api_testing/views.py`
  - `frontend/src/views/api-testing/RequestHistory.vue`

### 027. 套件级配置保存后执行链路仍读取原始接口配置

- **发生时间**：2026-06-19
- **错误类型**：配置优先级断链类
- **触发场景**：测试套件页保存了 `TestSuiteRequest.assertions`，但套件执行时仍只读取 `ApiRequest.assertions`，导致页面显示已保存，实际执行不生效。
- **根因分析**：编辑入口和执行入口使用了两个不同对象。套件级配置属于套件内关系对象 `TestSuiteRequest`，执行套件时必须先读取关系对象配置，再决定是否回退到原接口用例配置。
- **防复发规则**：
  - 保存到关系对象的配置，执行链路必须显式读取该关系对象字段。
  - 套件级断言优先级固定为：`TestSuiteRequest.assertions` 非空时优先；为空时回退 `ApiRequest.assertions`。
  - 新旧断言字段必须兼容 `expected` 和 `value`，避免旧套件行为变化。
  - VDD 必须同时检查“保存回显”和“执行生效”，不能只验证弹窗保存成功。
- **最低验证动作**：
  - 保存一条与接口自身断言不同的套件级断言，执行套件确认使用套件级断言。
  - 清空套件级断言后执行，确认回退接口自身断言。
  - 刷新页面后再次打开弹窗，确认断言可回显。
- **关联文件**：
  - `apps/api_testing/views.py`
  - `apps/api_testing/utils.py`
  - `frontend/src/views/api-testing/AutomationTesting.vue`

### 028. 功能路由存在但导航真源未拆，形成“假拆分”

- **发生时间**：2026-06-19
- **错误类型**：导航真源与产品入口不一致类
- **触发场景**：代码中已经存在接口测试用例页和测试套件页两个功能页面，但侧边栏只看到“接口测试用例”或旧“自动化测试”入口，看不到正式“测试套件”。用户会感知为“两个模块没有拆出来”或“只是换了名字”。
- **根因分析**：
  - 接口自动化测试套件仍只有历史 `/api-testing/automation` 可见入口，没有正式 `/api-testing/test-suites` 路由和导航项。
  - `frontend/src/config/navigation.js` 才是侧边栏可见入口真源；只改 `router/index.js` 或页面组件，不会自动出现在侧边栏。
  - Dashboard 快捷入口、route meta、i18n 标题和文档仍残留旧“自动化测试”口径，导致用户看到的产品结构没有真正拆开。
- **防复发规则**：
  - 拆分一个用户可见子模块时，必须同时检查 `navigation.js`、`router/index.js`、route meta、Dashboard 快捷入口、i18n 文案和相关文档。
  - 新正式入口必须是 `NAV_ENTRY_STATUS.KEEP`；旧入口如需兼容，应改为 `HIDE + redirect + activeMenu`，不能继续作为可见入口。
  - 页面组件复用允许保留，但组件变量名、页面标题和说明文案应表达新的产品对象，避免继续误导后续开发。
  - 完成后必须静态扫描旧路径、旧标题和新路径，确认旧入口只剩兼容重定向。
- **最低验证动作**：
  - 静态检索 `frontend/src/config/navigation.js`，确认新入口为 `KEEP`、旧入口为 `HIDE`。
  - 静态检索 `frontend/src/router/index.js`，确认新路由有正式 `name/title/description`，旧路由只重定向。
  - 静态检索相关 i18n 与 Dashboard，确认可见文案使用新模块名。
  - 浏览器进入接口自动化侧边栏，确认同时可见“接口测试用例”和“测试套件”，旧入口不会作为菜单显示。
- **关联文件**：
  - `frontend/src/config/navigation.js`
  - `frontend/src/router/index.js`
  - `frontend/src/views/api-testing/Dashboard.vue`
  - `frontend/src/locales/lang/zh-cn/api-testing.js`
  - `frontend/src/locales/lang/en/api-testing.js`

### 029. 只按阶段最小字段落表格，漏掉已确认固定字段

- **发生时间**：2026-06-19
- **错误类型**：规格落地不完整类
- **触发场景**：接口测试用例页已经从旧调试树拆成表格资产列表，但页面只展示阶段 A 最小字段：用例名称、请求方法、URL、所属集合、断言数、更新时间，漏掉完整规格中确认过的所属项目、来源、最近执行状态和所属集合筛选。用户看到后会认为“固定字段表格展示没有真正按确认口径落地”。
- **根因分析**：阶段 A TDD 的最小验收字段和 AI 生成闭环 Spec 的完整列表字段同时存在，实现时只对齐了最小验收，没有回查完整固定字段规格；同时“最近执行状态”如果在前端逐行请求历史，会形成 N+1 请求，影响列表流畅度。
- **防复发规则**：
  - 实现资产列表时，必须同时对照当前阶段 TDD 和上游完整 Spec；最小验收不能覆盖完整固定字段口径。
  - 接口测试用例主表只能展示 `ApiRequest` 原子资产字段和可由其归属 / 历史聚合得到的轻量字段，禁止混入测试套件编排字段。
  - 最近执行状态必须在后端列表接口聚合返回，前端不得为每一行单独请求历史列表。
  - 旧资产没有来源字段时，必须明确显示“来源未记录”，不能伪造为 AI 生成或手工创建。
- **最低验证动作**：
  - 静态核对 `/api-testing/test-cases` 表格列是否包含用例名称、请求方法、URL、所属项目、所属集合、断言数、来源、最近执行状态、更新时间和操作。
  - 静态核对筛选项是否包含项目、集合、请求方法、关键词。
  - 静态检索前端列表页，确认没有为每行调用请求历史接口形成 N+1。
  - 执行 `python -m py_compile apps\api_testing\serializers.py apps\api_testing\views.py` 和 `cd frontend && cmd /c npm run build`。
- **关联文件**：
  - `frontend/src/views/api-testing/ApiTestCaseList.vue`
  - `apps/api_testing/serializers.py`
  - `apps/api_testing/views.py`
  - `docs/api-automation/api-automation-testcase-loop-ai-generation-spec.md`

### 030. Vite 依赖重优化导致开发环境首次切页整页刷新

- **发生时间**：2026-07-04
- **错误类型**：开发服务器依赖优化类
- **触发场景**：本地运行 `npm run dev` 后，首次点击进入某些懒加载页面，例如接口自动化、请求历史、Web / App 自动化页面。页面会卡住，控制台出现 `504 Outdated Optimize Dep` 和 `Failed to fetch dynamically imported module`，随后浏览器 reload，用户体感是“点页面没反应，刷新后才正常”。
- **根因分析**：
  - `frontend/vite.config.js` 中开启了 `optimizeDeps.force: true`，导致每次启动 dev server 都强制丢弃依赖优化缓存。
  - 项目大量页面通过路由懒加载，Element Plus 又使用按需组件和按需样式。部分深层样式导入只有首次访问对应页面时才被发现，Vite 在页面交互过程中临时重优化依赖，旧依赖 URL 变成过期版本并返回 504。
  - Vue Router 动态导入页面组件依赖这些优化产物，一旦依赖 URL 过期，路由导入失败，Vite 客户端会触发整页 reload。这个现象容易被误判成 `router-view key`、表单默认提交或认证跳转问题。
- **防复发规则**：
  - 前端 dev 配置不要长期保留 `optimizeDeps.force: true`；只有临时清缓存排障时才允许通过命令行或一次性操作强制重优化。
  - 新增大量懒加载页面、按需组件或按需样式时，要同步检查 `optimizeDeps.entries` 是否能覆盖 `src/**/*.{js,vue}`。
  - 对 Element Plus 按需样式这类深层导入，应在 `optimizeDeps.include` 中预优化关键依赖或使用稳定的全局样式入口，避免首次点击页面才发现依赖。
  - 定位“切页卡顿 / 像刷新”问题时，必须同时看浏览器网络请求和控制台，确认是否存在 `/node_modules/.vite/deps/* => 504 Outdated Optimize Dep`，不能只从路由代码猜测。
- **最低验证动作**：
  - 重启前端 dev server 后，日志不应再出现 `Forced re-optimization of dependencies`。
  - 首次点击跨模块和侧边栏懒加载页面时，网络请求不应再出现 `504 Outdated Optimize Dep`。
  - Playwright 或浏览器手工验证中，`beforeunload`、`pagehide` 和主文档 reload 计数应保持为 0。
  - 执行 `cd frontend && cmd /c npm run build`，确认 dev 配置改动不破坏生产构建。
- **关联文件**：
  - `frontend/vite.config.js`
  - `frontend/src/router/index.js`
  - `frontend/src/layout/index.vue`

### 031. 本地启动脚本未等待后端 ready 导致前端代理拒绝连接

- **发生时间**：2026-07-04
- **错误类型**：本地启动编排类
- **触发场景**：用户双击 `start.bat` 启动平台，Vite 前端先 ready，浏览器立刻发起旧 token 刷新或登录请求，但 Django 后端还在启动系统检查和加载应用，尚未监听 `127.0.0.1:8000`。
- **根因分析**：
  - `start.bat` 旧逻辑是后台启动后端后马上进入 `frontend` 执行 `npm run dev`，没有等待后端端口真正可连接。
  - 前端 Vite ready 速度快于 Django ready，前端代理 `/api/*` 到 `127.0.0.1:8000` 时就会出现 `ECONNREFUSED`。
  - 旧 token 会让页面启动时先请求 `/api/auth/token/refresh/`，用户再点登录会继续请求 `/api/auth/login/`，因此窗口里会连续出现两个代理错误。
- **防复发规则**：
  - 本地一键启动脚本必须按依赖顺序编排：清端口 -> 启动后端 -> 等待后端 ready -> 启动前端。
  - 双击启动用的 bat 文件开头必须 `cd /d "%~dp0"`，避免工作目录不确定导致找不到 `manage.py`、`venv` 或 `frontend`。
  - 后端启动失败时必须提示查看 `backend.log`，不要继续启动前端制造误导性的代理错误。
- **最低验证动作**：
  - 查看 `backend.log`，确认 Django 输出 `Starting development server at http://0.0.0.0:8000/` 后再启动前端。
  - 双击 `start.bat` 后，前端窗口不应再出现启动阶段的 `/api/auth/login/ ECONNREFUSED 127.0.0.1:8000`。
  - 若 60 秒内后端未 ready，脚本应停止并提示查看 `backend.log`。
- **关联文件**：
  - `start.bat`
  - `backend.log`

### 032. 调试日志和异常日志输出敏感信息

- **发生时间**：2026-07-10
- **错误类型**：敏感信息泄露类
- **触发场景**：登录页、token 刷新、路由守卫、AI 模型配置页或后端 AI 模型调用链为了排障直接输出完整对象，例如登录返回值、用户对象、axios error、API Key 表单、请求 URL、外部服务响应正文。
- **根因分析**：
  - 前端调试日志在开发阶段很容易保留下来，生产构建时仍可能把 token、refresh token、用户信息、API Key 或完整错误对象打到控制台。
  - 后端模型调用失败时如果直接打印响应正文、请求头或异常 `repr`，可能把 API Key、Authorization、Cookie、password 或第三方响应中的敏感字段写进日志。
  - “只在开发环境看一下”的日志如果没有明确删除或脱敏，后续浏览器回归和线上排障都会放大泄露风险。
- **防复发规则**：
  - 前端业务代码禁止输出 token、refresh token、用户对象、API Key、完整请求头、完整响应体或 axios error 对象。
  - 认证、路由守卫、AI 配置和模型测试连接相关页面如需提示失败，优先展示用户可读的 `message/detail/error`，不要把完整错误对象写入控制台。
  - 后端日志输出外部服务错误、AI 模型响应、请求头或配置对象前必须脱敏；优先复用 `apps/core/security.py` 的 `redact_text`、`redact_json_for_log`。
  - AI 模型调用成功日志只允许记录状态码、响应字段 keys、choices 数量、耗时等摘要，不打印完整生成正文或完整响应体。
  - 清理日志时不能降低真实错误处理能力：页面仍要有失败提示，后端仍要保留可定位问题的脱敏摘要。
- **最低验证动作**：
  - 静态扫描本轮涉及页面和工具：`console\.|Login result|User store state|Saving config with data|ConfigForm changed|Token刷新|Navigated from`。
  - 静态扫描后端 AI 调用链：`响应内容|api_key.*logger|Authorization.*logger|Cookie.*logger|API调用失败: \{repr|流式请求异常: \{e\}`。
  - 对脱敏 helper 构造 JWT、API Key、Cookie、password、Authorization 样本，确认原始值不出现在输出中。
  - 执行前端构建和后端编译，确保删除日志没有破坏页面和模型调用链。
- **关联文件**：
  - `frontend/src/views/auth/Login.vue`
  - `frontend/src/utils/api.js`
  - `frontend/src/stores/user.js`
  - `frontend/src/router/index.js`
  - `frontend/src/views/requirement-analysis/AIModelConfig.vue`
  - `frontend/src/views/requirement-analysis/PromptConfig.vue`
  - `frontend/src/views/requirement-analysis/GenerationConfigView.vue`
  - `frontend/src/views/configuration/AIIntelligentModeConfig.vue`
  - `apps/core/security.py`
  - `apps/requirement_analysis/models.py`

### 033. Django 请求级验证不要用交互 shell 管道执行多行脚本

- **发生时间**：2026-07-10
- **错误类型**：验证命令方式类
- **触发场景**：使用 PowerShell here-string 管道进入 `python manage.py shell` 执行多行 APIClient 验证脚本，命令退出码为 0，但没有打印 `status/json`，无法证明真实请求已经执行。
- **根因分析**：
  - `manage.py shell` 默认进入交互控制台，多行 `try/finally` 这类代码块在管道输入中容易因为交互控制台收尾规则没有真正执行到预期输出。
  - 退出码为 0 只说明交互控制台正常退出，不等于请求级断言已经产生证据。
  - 如果临时数据创建在 `try/finally` 之前，脚本没执行到清理段时还可能残留测试用户、项目、集合或请求。
- **防复发规则**：
  - 做 Django / DRF APIClient 请求级验证时，优先使用 `python manage.py shell -c $code` 非交互执行。
  - 验证命令必须打印关键证据，例如 `status=` 和 `json=`；没有输出时不能记为通过。
  - 临时数据必须带唯一前缀，并在验证后查询前缀残留数量。
  - 验证失败后先记录 `error_event_log.md`，再清理临时数据，不能继续叠加新数据。
- **最低验证动作**：
  - 命令输出里必须看到 HTTP 状态码和响应 JSON。
  - 临时数据清理后必须输出 `leftover=0` 或等价结果。
  - 若响应是预期 400 / 403 / 404，允许 Django 打印 Bad Request / Forbidden / Not Found 日志，但必须以响应 JSON 作为验证证据。
- **关联命令**：
  - `.\venv\Scripts\python.exe manage.py shell -c $code`

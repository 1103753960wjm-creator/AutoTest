# TestHub 错误模式库与防复发手册

更新时间：2026-05-31

## 1. 文件职责

本文文件属于 C 层“正式项目记忆”，用于记录已经证明会重复出现、值得工程化防复发的错误模式。

本文不记录一次性噪音报错，不记录尚未确认根因的临时猜测，而是记录：

- 错误触发场景
- 根因分析
- 防复发规则
- 最低验证动作

使用原则：

- 同类错误首次出现，可先写入 `task_handoff.md`
- 同类错误第二次出现，或已经能稳定归纳为错误模式时，必须写入本文
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
  - `docs/阶段2优化文档.md`

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

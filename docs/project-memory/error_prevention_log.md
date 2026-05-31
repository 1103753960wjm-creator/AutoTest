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

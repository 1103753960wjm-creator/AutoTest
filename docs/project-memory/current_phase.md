# TestHub 项目开发记忆

更新时间：2026-06-19

## 1. 文件职责

本文件属于 C 层“项目开发记忆”，用于记录当前项目推进过程中的阶段事实、冻结方案、当前验收口径和下一步主线。

使用原则：

- 本文件只记录“已经确认的项目事实、冻结方案、已落地产物、当前验收口径和阶段限制”。
- 正式规则以 `GEMINI.md`、`AGENTS.md` 和仓库内 `.cursor/*.md` 为准。
- 已冻结决策统一查看 `docs/project-memory/decision_log.md`。
- 模块局部边界、局部风险和开发注意事项统一查看 `docs/project-memory/module_memory.md`。
- 最近一轮任务交接统一查看 `docs/project-memory/task_handoff.md`。
- 新对话快速进入上下文统一查看 `docs/project-memory/dialogue_bootstrap.md`，本文件不再承担启动捷径职责。
- 若本文件与实际代码冲突，以实际代码为准，并及时回写本文件。

## 2. 当前项目真实基线

- 项目：`TestHub` 智能测试管理平台
- 根目录关键结构：`apps`、`frontend`、`docs`、`media`、`logs`、`allure`
- 后端：Django 4.2 + Django REST Framework + MySQL + SimpleJWT + Channels + Celery
- 前端：Vue 3 + JavaScript + Vite + Pinia + Element Plus
- 高风险链路：
  - JWT 登录、退出、刷新
  - AI 配置与调用
  - Celery 异步执行
  - Channels / WebSocket
  - Selenium / Playwright / Airtest 执行器
  - Allure 报告
  - Webhook / 邮件通知

## 3. 当前阶段已冻结的关键结论

### 3.1 平台现状地图

已经产出平台地图文档：

- `docs/overview/平台现状地图.md`

该文档明确了：

- 当前一级导航和二级页面现状
- 页面类型标签
- 前后端模块对应关系
- 配置、任务、报告、通知等模糊入口的现状

后续做结构收敛时，先以这份地图为“现状真相”。

### 3.2 一级导航冻结

已经冻结的一级导航方案：

- 工作台
- 测试设计
- 接口自动化
- Web 自动化
- App 自动化
- 云真机（预留）
- 执行中心（预留）
- 数据工厂
- 配置中心
- 系统管理

相关文件：

- `docs/architecture/navigation-freeze-plan.md`
- `frontend/src/config/navigation.js`

当前重要边界：

- `AI 助手` 不再作为独立一级导航，按隐藏入口处理
- `AI 智能模式` 归入 `Web 自动化`
- 执行、报告、调度、通知日志后续向 `执行中心` 收敛
- 个人资料、认证、后台入口归 `系统管理`

### 3.3 页面壳定义

已经定义 4 类统一页面壳：

- `DashboardShell`
- `ListShell`
- `WorkspaceShell`
- `DetailResultShell`

相关文件：

- `docs/architecture/page-shell-spec.md`
- `frontend/src/components/page-shells/*`

当前状态：

- 基础组件已落地
- 尚未全站替换旧页面

### 3.4 路由 meta 和导航元信息

已统一 `route meta` 基线，关键字段包括：

- `title`
- `description`
- `module`
- `pageType`
- `icon`
- `keepAlive`
- `hidden`
- `parentTitle`
- `activeMenu`
- `requiresAuth`
- `requiresGuest`

相关文件：

- `docs/architecture/route-meta-spec.md`
- `frontend/src/router/route-meta.js`
- `frontend/src/router/index.js`
- `frontend/src/layout/index.vue`
- `frontend/src/types/router-meta.d.ts`

当前结论：

- 页面标题、面包屑、模块归属优先从路由 `meta` 取
- 不再维护散落的路径标题映射
- 前端开启了 `checkJs`，以后新增 `route meta` 字段时，必须同步更新 `frontend/src/types/router-meta.d.ts`

### 3.5 配置中心与系统管理边界

已明确配置中心与系统管理的归类边界。

相关文件：

- `docs/architecture/config-vs-system-boundary.md`

当前关键结论：

- 配置中心承接 AI 模型、提示词、生成配置、环境配置、通知通道配置、Dify、平台级 AI 服务配置
- 系统管理承接个人资料、登录注册、后续用户 / 角色 / 权限 / 审计能力
- 各域定时任务、执行记录、通知日志暂不纳入这两个模块，后续向执行中心或审计中心收敛

### 3.6 平台 smoke 回归基线

已经建立最小 smoke 回归基线。

相关文件：

- `docs/architecture/platform-smoke-baseline.md`

当前基线覆盖：

- 登录 / 退出 / token 失效
- 首页和模块入口
- 测试设计主链
- 接口自动化关键页
- Web 自动化关键页
- App 自动化关键页
- 数据工厂关键页
- 配置中心 / 系统管理关键页

说明：

- 当前只冻结回归清单和预期结果
- 尚未引入前端 E2E 测试框架

### 3.7 统一状态组件和状态规范

已经建立统一状态基座，并在 0.7b 完成了可长期复用的补强。

相关文件：

- `docs/architecture/ui-state-spec.md`
- `frontend/src/components/ui-states/*`

已冻结状态类型：

- `loading`
- `empty`
- `request-error`
- `forbidden`
- `search-empty`

当前统一口径：

- 推荐统一使用 `pageState` / `xxxState` 枚举式状态
- 前端页面状态统一采用 `UI_PAGE_STATE` 枚举式口径，优先使用 `pageState / xxxState`
- 状态组件统一通过 `StateBlock` 系列承载，支持整页态与局部态
- 统一常量文件：`frontend/src/components/ui-states/state-constants.js`
- 状态组件已支持 `primaryActionText` / `secondaryActionText` 和 `@primary-action` / `@secondary-action`
- 旧 `actionText` / `@action` 继续兼容

### 3.8 日志与审计入口归属

已经冻结日志与审计入口归属规则。

相关文件：

- `docs/architecture/log-audit-boundary.md`

当前关键结论：

- 登录日志、操作日志、审计日志、AI 调用审计固定归 `系统管理`
- 请求历史、任务执行日志、执行记录、通知日志固定向 `执行中心` 或结果页体系收敛
- Dashboard 最近活动只保留摘要，不再扩张成正式治理日志中心
- `AIExecutionRecord` 属于执行结果，不等于 AI 调用审计

已做的轻量落地：

- `frontend/src/config/navigation.js` 中系统管理已补预留入口：登录日志、操作日志、审计日志、AI 调用审计

### 3.9 统一平台壳

阶段 1 已完成统一平台壳的基础落地。
近期（2026-05-30）完成底层组件卸载崩溃隐患的彻底消除。
2026-06-16 完成顶部大模块与侧边栏连续切换卡顿修复，冻结登录后根层 Layout 复用策略。

相关文件：

- `frontend/src/layout/index.vue`
- `frontend/src/layout/platform-layout.js`
- `frontend/src/layout/components/PlatformGlobalHeader.vue`
- `frontend/src/layout/components/PlatformSidebar.vue`
- `frontend/src/layout/components/PlatformPageHeader.vue`

当前关键结论：

- 平台统一壳层负责顶部全局栏、模块侧边导航、面包屑、页面标题区和主内容容器
- 业务页面不再自带平台级头部与导航结构
- 页面标题、面包屑、模块归属、页面类型优先由路由 meta 驱动
- 顶部全局搜索、最近访问、收藏、消息通知、项目上下文当前仍为占位入口
- 首页与 AI 助手已纳入统一平台壳，不再作为壳外孤立页面
- **架构级路由缓存策略**：平台壳层在 `<router-view>` 中统一使用基于路由名称白名单的 `<keep-alive :include="cachedViews">` 进行按需缓存。为避开 Vue 3 的组件上下文丢失崩溃（Bug #6222），**绝对禁止**在缓存插槽层使用 `v-if` 条件渲染容器节点。
- **根层 Layout 复用策略**：`frontend/src/App.vue` 中登录后的业务页面统一使用 `layout:authenticated` 作为根层 key，禁止按业务模块、物理顶层路由、`fullPath` 或 `params` 销毁整套平台壳；登录页、注册页等壳外页面仍可使用独立 key。
- **内容层 key 策略**：`frontend/src/layout/index.vue` 内容路由组件继续使用 `currentRoute.name || currentRoute.path`，与 `<keep-alive :include="cachedViews">` 的路由名称维度保持一致，禁止使用 `fullPath`。
- **导航调度策略**：顶部模块、侧边栏、全局搜索、最近访问、收藏、个人资料等入口必须统一走 Layout 内部导航调度器；快速连续点击时只保留最新目标，重复目标和重复路径应直接忽略，不得用整页刷新兜底。
- **硬刷新红线**：业务页面、平台壳和路由导航中不得调用 `window.location.reload()` 作为状态刷新手段；需要重取配置或数据时必须调用页面内部 `refresh/load/check...` 入口。

### 3.10 第一批共享组件边界

阶段 1.6 已冻结第一批共享组件边界。

当前关键结论：

- 第一批共享组件仅服务于平台主体层高频场景，优先覆盖筛选区、统计卡、最近记录和快捷入口
- 不得与 Layout 或 `PlatformPageHeader` 形成平行头部体系
- 不得提前抽象重型工作台框架

### 3.11 Home 工作台首页边界

阶段 1.2 已冻结 Home 工作台首页边界。

当前关键结论：

- Home 作为平台工作台首页，只承接平台级概览、我的工作、核心模块入口、快捷继续与风险提醒等主体内容
- 页面头部始终由 Layout 挂载的 `PlatformPageHeader` 承接
- 首页主体不得再自行渲染平台级头部

### 3.12 平台效率能力第一版边界

阶段 1.3 已冻结平台效率能力第一版边界。

当前关键结论：

- 最近访问统一走 `router.afterEach` 记录
- Home 的“快捷继续”第一版只消费最近访问
- 收藏第一版只做页面级 / 入口级收藏，不提前扩展到复杂资产系统

### 3.13 平台全局搜索骨架边界

阶段 1.4 已冻结平台全局搜索骨架边界。

当前关键结论：

- 全局搜索入口固定挂在顶部全局栏，采用轻量 `command palette` 形态
- 第一版优先搜索页面 / 菜单 / 入口；轻资产只接入测试设计项目和测试用例
- 关键字长度 `>= 2` 才触发动态搜索
- 从搜索结果打开页面后，仍然走统一路由链，因此会自然写入最近访问

### 3.14 深链接与回跳第一版边界

阶段 1.9 已冻结深链接与回跳第一版边界。

当前关键结论：

- 深链接第一版只覆盖已有稳定详情路由的高价值对象
- `params` 只承接对象身份，来源上下文统一走 `query`
- 来源上下文固定使用 `from / fromPath / fromTitle / fromModule`
- `fromPath` 必须做最小校验，只允许站内相对路径
- 回跳顺序固定为：合法 `fromPath` -> 所属列表页 -> `router.back()`

### 3.15 平台壳滚动复位规则

阶段 1 平台化过程中已冻结统一滚动复位规则。

当前关键结论：

- 平台主内容区使用独立滚动容器时，跨页面路由切换后应由 Layout 统一将主内容容器滚动复位到顶部
- 该规则优先覆盖 Home 快捷继续、最近访问、收藏、全局搜索、侧边栏和模块切换等跨页面入口
- 同一路径下仅 `query` 变化的子视图切换不默认强制滚动复位

### 3.16 测试设计对象层 2.1 边界

阶段 2.1 已冻结测试设计对象层边界。

当前关键结论：

- 测试设计对象层正式包含：测试设计项目、需求分析对象、生成任务对象、生成结果对象、测试用例对象
- AI 来源位和自动化状态位在 2.1 已建立统一语义，但当前仍属于“对象层预留位”，不等于完整业务闭环
- 执行详情页在 2.1 只允许轻触来源展示位，不提前进入执行闭环重构

阶段约束：

- 2.2 必须建立在上述对象层之上，不能回退成孤立流程页
- 2.3 自动化草稿中心必须挂接在项目或测试用例资产层之上，不能绕开对象层
- 2.5 若涉及执行链路，不得把“来源展示位预留”误扩张成执行闭环重构

### 3.17 AI 生成链路 2.2 第一阶段边界

2.2 第一阶段已经完成，重点是“配置来源层 + 前半链 + 任务层”。

当前关键结论：

- `ProjectDetail -> RequirementAnalysisView -> TaskDetail` 已形成更清楚的前半链
- 配置页已具备“生成链上游来源层”语义，不再只是孤立配置页
- `TaskDetail` 已开始承接任务对象角色，不应再退回结果处理主页面
- `source_analysis_summary` 当前只是“来源分析说明 / 当前分析上下文摘要位”，不是 analysis 真绑定
- `generation_config_summary` 当前是“活跃配置推断摘要”，不是任务执行真实快照

相关文件：

- `docs/ai/ai-generation-chain-spec.md`
- `frontend/src/views/requirement-analysis/AIModelConfig.vue`
- `frontend/src/views/requirement-analysis/PromptConfig.vue`
- `frontend/src/views/requirement-analysis/GenerationConfigView.vue`
- `frontend/src/views/requirement-analysis/RequirementAnalysisView.vue`
- `frontend/src/views/requirement-analysis/TaskDetail.vue`
- `frontend/src/views/projects/ProjectDetail.vue`

### 3.18 AI 生成结果采纳幂等规则

当前已经冻结 AI 生成结果采纳的最小幂等规则。

当前关键结论：

- 同一条 AI 生成结果再次采纳时，系统按“幂等成功”处理，不再重复创建测试用例
- 幂等命中时返回已有测试用例，而不是走硬错误
- AI 来源标签当前最小规范包含：
  - `source`
  - `task_id`
  - `project_id`
  - `project_name`
  - `case_id`
  - `case_index`
  - `source_label`
- 后端去重优先顺序：
  - `task_id + case_id`
  - `task_id + case_index`
  - `task_id + 规范化内容`
- 历史重复数据不清洗，本轮只阻止后续继续新增重复

相关文件：

- `apps/testcases/ai_source_dedup.py`
- `apps/testcases/views.py`
- `apps/requirement_analysis/views.py`

### 3.19 AI 生成任务处理状态口径

当前已经把 AI 生成任务从“是否已保存”升级为“处理状态”。

当前关键结论：

- `TestCaseGenerationTask` 已新增 `result_status_snapshot` 轻量 JSON 快照
- 结果级状态固定为：
  - `pending`
  - `adopted`
  - `discarded`
- 任务级摘要固定走 `processing_status_summary`
- 任务级主状态固定为四态：
  - `尚未处理`
  - `处理中`
  - `已保存为正式测试用例`
  - `已处理完成`
- 采纳和弃用都算“已处理”
- 只有“全部结果都被采纳”时，任务才会显示“已保存为正式测试用例”
- 若全部结果都已处理完，但包含弃用结果，任务主状态应为“已处理完成”，不是“已保存”
- 弃用不再删除结果、不再删除任务，只把结果标记为 `discarded`
- AI 生成用例页当前应显示“处理状态”，而不是继续使用“保存状态”的单布尔心智

相关文件：

- `apps/requirement_analysis/models.py`
- `apps/requirement_analysis/result_status.py`
- `apps/requirement_analysis/views.py`
- `apps/requirement_analysis/serializers.py`
- `frontend/src/views/requirement-analysis/TaskDetail.vue`
- `frontend/src/views/requirement-analysis/GeneratedTestCaseList.vue`

### 3.20 2.2 第二阶段当前冻结边界

2.2 第二阶段目前没有继续完整推进，先被 bug 修复和状态口径收口打断。

当前冻结边界：

- `GeneratedTestCaseList` 当前仍应理解为“生成产物层页面 / 结果批次页”，不是“纯结果对象列表页”
- 不要为了追求“结果对象感”而伪造一套不真实的数据结构
- “是否已确认 / 是否已编辑”只能做弱语义，不得包装成完整状态机
- `TaskDetail` 本轮重点是把结果层主语权交出去，不继续增强任务页内的结果处理能力
- `TestCaseDetail / TestCaseEdit` 后续只能轻量承接来源关系，不得伪装成强回链
- 老数据如果没有 AI 来源标签，必须允许展示为：
  - `来源未记录`
  - `AI 来源待补齐`

### 3.21 2.2 任务状态、真取消与自动评审入口收口

2026-03-26 已完成一轮面向 2.2 主链路状态的高优先级收口，重点不是重做对象层，而是修复“任务状态、真取消、恢复入口和自动评审可追踪性”。

当前冻结结论：

- `RequirementAnalysisView -> TestCaseGenerationTask -> Generated Results -> TaskAutoReviewRecord -> TestCase` 是当前已成立的 2.2 主链
- 取消生成采用“应用层协作式真取消”，不是前端假取消，也不是厂商侧远端硬中断
- 所有最终结果写库前都必须再次执行取消检查，避免 `cancelled` 被后续结果写回污染
- 任务恢复上下文按项目维度持久化，固定使用项目隔离的 `sessionStorage` key，避免跨项目恢复污染
- `TaskDetail` 对所有任务状态可见，但操作能力必须同时受“任务状态 + 结果处理状态”双重门禁限制
- 自动 AI 评审本轮不并入现有手工评审列表，而是升级为独立的 `TaskAutoReviewRecord`
- `TaskAutoReviewRecord` 使用 `ForeignKey(task)`，不锁死一对一
- 页面默认只消费“每任务最新一条自动评审记录”
- 自动评审最新记录的排序规则固定为：`created_at DESC, id DESC`，其中 `id DESC` 是最终稳定兜底
- `TaskAutoReviewRecord.source_stage` 本轮固定为 `generation_review`
- `auto_review_summary.status` 固定使用以下枚举，不再依赖文案猜测：
  - `not_triggered`
  - `reviewing`
  - `completed`
  - `failed`
  - `cancelled`
- AutoReviewList 本轮默认只展示每任务最新一条自动评审记录，不展开历史记录列表；但每条记录必须可展开查看完整内容

相关文件：

- `docs/ai/ai-generation-chain-spec.md`
- `docs/ai/ai-generation-cancel-spec.md`
- `docs/ai/ai-review-link-spec.md`
- `apps/requirement_analysis/models.py`
- `apps/requirement_analysis/serializers.py`
- `apps/requirement_analysis/views.py`
- `frontend/src/composables/useGenerationTaskTracking.js`
- `frontend/src/views/requirement-analysis/RequirementAnalysisView.vue`
- `frontend/src/views/requirement-analysis/TaskDetail.vue`
- `frontend/src/views/requirement-analysis/GeneratedTestCaseList.vue`
- `frontend/src/views/reviews/AutoReviewList.vue`
- `frontend/src/views/reviews/ReviewList.vue`

### 3.22 测试设计模块现代化与批量删除接口标准化

2026-03-29 已完成“测试设计”子导航下所有核心模块的标准化，重点是“UI 视觉统一 + 交互行为对齐 + 批量接口补齐”。

#### 当前冻结结论：

- **UI 风格统一**: `UnifiedListTable` 正式确立为后续所有列表页的基座。强制启用 `border`、统一表头背景色 (`#f5f7fa`) 及文本链接型按钮样式。
- **标准化交互行为**:
  - 第一列固定为序号列。
  - 第二列固定为多选框列（全量支持批量操作）。
  - **行双击行为**: 统一为“触发编辑”。
- **后端批量接口基线**:
  - 项目管理新增 `POST /api/projects/batch-delete/`。
  - 版本管理新增 `POST /api/versions/batch-delete/`。
  - 接口规范统一：支持 `confirm` 二次确认标志位，用于级联删除控制。
- **字段扩展规范**:
  - 允许在现代化改造过程中按需扩展列表可见字段（如版本管理已新增 `created_by` 和 `testcases_count`）。

#### 相关文件：

- `apps/projects/views.py` / `apps/versions/views.py` (新增关键 API)
- `frontend/src/views/projects/ProjectList.vue`
- `frontend/src/views/versions/VersionList.vue`
- `frontend/src/views/testcases/TestCaseList.vue`
- `frontend/src/components/platform-shared/UnifiedListTable.vue`

### 3.23 AI自动化执行记录页重构与前端 UI 一致化规范落地

2026-05-26 已完成“AI自动化执行记录页” (AIExecutionRecords.vue) 的重构与迁移，并正式确立“前端样式 UI 一致化”规则。

#### 当前冻结结论：

- **UI 风格与状态收口**: 采用 `ListShell` 统一页面壳和 `UnifiedListTable` 表格组件。接入 Loading / Empty / SearchEmpty / Error / Forbidden 五大统一页面状态组件。
- **UI 一致性规则对齐**: 任何模块新增或改造搜索筛选组件时，必须与 `ProjectManagement.vue` 的搜索框、查询/重置按钮在排版、位置、间距（如 `el-row :gutter=16`，独立卡片边距及阴影）上保持完全一致。
- **检索与轮询闭环**: 实现了“用例名称”检索与清空重置；定时轮询触发时自动携带当前搜索状态，且在用户已勾选多选框时暂停数据覆盖以防干扰操作。

#### 相关文件：

- `.cursor/project_rules.md` / `frontend/AGENTS.md` (规则写入)
- `frontend/src/views/ui-automation/ai/AIExecutionRecords.vue`

### 3.24 2026-06-16 P0 安全、依赖与导航稳定性收口

2026-06-16 已完成一轮 P0 安全与前端体验收口，以下结论后续开发必须继承。

#### 当前冻结结论：

- 后端 `DEBUG`、`DISABLE_CSRF_FOR_API` 统一使用项目级严格布尔解析；非法值必须明确报错，不允许第三方转换抛出难读底层异常。
- 生产环境必须显式配置 `ALLOWED_HOSTS` 与 `CORS_ALLOWED_ORIGINS`，禁止 `ALLOWED_HOSTS=*`，禁止生产环境开启 `DISABLE_CSRF_FOR_API=True`。
- 前端 Excel 导出依赖从 `xlsx` 替换为 `write-excel-file`，并统一通过 `frontend/src/utils/excelExport.js` 导出；后续文档和代码示例不得继续引入 `xlsx`。
- 登录失效、退出登录和 401 刷新失败后的登录页跳转统一走 `frontend/src/utils/authNavigation.js`，优先复用 router，不在业务代码和拦截器中直接写 `window.location.href`。
- `ListShell #filters` 是列表筛选区正式插槽；筛选控件必须撑满所在列，`ListShell` 已兜底 `el-row`、`el-input`、`el-select`、`el-date-editor` 宽度。
- 评审列表缺失翻译已补齐，进入评审列表不应再输出 `reviewList.*` i18n missing warning。

#### 相关文件：

- `backend/settings.py`
- `backend/middleware.py`
- `.env.example`
- `frontend/src/App.vue`
- `frontend/src/layout/index.vue`
- `frontend/src/layout/components/PlatformSidebar.vue`
- `frontend/src/layout/usePlatformPageHeader.js`
- `frontend/src/utils/authNavigation.js`
- `frontend/src/utils/excelExport.js`
- `frontend/src/components/page-shells/ListShell.vue`
- `frontend/src/views/requirement-analysis/RequirementAnalysisView.vue`
- `frontend/src/views/requirement-analysis/TaskDetail.vue`
- `frontend/src/views/testcases/TestCaseList.vue`
- `frontend/src/locales/lang/zh-cn/review.js`
- `frontend/src/locales/lang/en/review.js`

### 3.25 2026-06-17 接口自动化 P0-1 用例闭环

2026-06-17 已完成接口自动化 P0-1 自身闭环，以下结论后续开发必须继承。

#### 当前冻结结论：

- 接口自动化正式可见入口为“接口测试用例”，路径固定为 `/api-testing/test-cases`。
- 旧 `/api-testing/interfaces` 只作为隐藏兼容入口保留，并重定向到 `/api-testing/test-cases`，不得继续作为唯一正式用例入口。
- P0-1 阶段不新增 `ApiTestCase` 数据表，`ApiRequest` 是接口测试用例的技术承载。
- 单接口执行真实路径为 `/api-testing/requests/{id}/execute/`，前端不得再调用 `/api-testing/api-requests/{id}/execute/`。
- 执行结果详情真实路径为 `/api-testing/test-executions/{id}/`，前端不得再调用 `/api-testing/executions/{id}/`。
- 单接口执行成功后必须把断言结果写入 `RequestHistory.assertions_results`，否则请求历史无法闭环展示断言。
- 请求历史详情页必须展示 `RequestHistory.assertions_results`，否则仅落库不算完整用户可见闭环。
- `/api-testing/test-cases` 必须是接口测试用例资产列表页，不得重新退回旧接口调试树作为首页。
- `InterfaceManagement.vue` 当前只作为隐藏调试工作区复用，正式路径为 `/api-testing/test-cases/workspace?caseId={id}`，并通过 `activeMenu` 高亮“接口测试用例”。
- 从接口测试用例资产列表进入隐藏调试工作区时，必须携带 `projectId`；调试工作区作为 `keepAlive` 页面时必须监听 `caseId/projectId` 变化并重新选中目标用例，不能依赖外层 `router-view` key 变化销毁重建。
- 接口测试用例资产列表在快速筛选、分页或项目切换时必须保证“最后一次请求优先”，旧响应晚返回不得覆盖最新列表状态。
- 接口测试用例页搜索走真实 `ApiRequest` 列表搜索，不使用不存在的 `/api-testing/collections/search`。
- 新建接口测试用例必须选择集合，因为 P0 阶段 `ApiRequest` 的项目归属来自 `ApiCollection`；不应继续制造无项目归属的半闭环接口用例资产。
- 接口测试用例列表可以把用例加入同项目测试套件，后端必须限制 `TestSuite.project == ApiRequest.collection.project`。
- 接口测试用例列表“加入套件”必须形成明确反馈闭环：阻断原因、加载失败、未选择套件、加入成功和加入失败都用弹窗提示；行操作必须阻止表格行事件冒泡；加载套件时禁用选择与确认，避免重复提交或静默失败。
- 接口测试用例隐藏调试工作区必须提供“返回用例列表”入口，不能只依赖浏览器返回。
- Element Plus 服务式 API 的样式已在前端入口补齐；后续新增服务式组件时要同步确认样式入口，避免 `ElMessageBox` 一类弹窗裸样式或不居中。
- 最近执行状态暂不做列表逐行请求；后续如需展示，应在后端 `ApiRequest` 列表聚合最近一条 `RequestHistory`。

#### 相关文件：

- `docs/api-automation/api-automation-testcase-loop-ai-generation-spec.md`
- `docs/api-automation/api-automation-p0-1-testcase-loop-tdd.md`
- `docs/api-automation/api-automation-p0-1-testcase-loop-vdd.md`
- `apps/api_testing/views.py`
- `frontend/src/api/api-testing.js`
- `frontend/src/router/index.js`
- `frontend/src/config/navigation.js`
- `frontend/src/views/api-testing/ApiTestCaseList.vue`
- `frontend/src/views/api-testing/InterfaceManagement.vue`
- `frontend/src/views/api-testing/RequestHistory.vue`
- `frontend/src/views/api-testing/Dashboard.vue`
- `frontend/src/main.js`

### 3.26 2026-06-17 平台壳快速导航稳定性修复

2026-06-17 已修复顶部大模块与侧边栏子模块快速切换时页面卡住、刷新后才恢复的问题。

#### 当前冻结结论：

- 侧边栏一次点击只能触发一次导航，正式触发源固定为 `el-menu @select`。
- `PlatformSidebar.vue` 不得重新添加 `pointerdown.capture` 或 `click.capture` 导航抢跑逻辑。
- `layout/index.vue` 的导航调度以“最后一次点击优先”为准；旧导航被后续点击取消是正常行为，不得继续用 pending 队列阻塞最新目标。
- `pendingNavigationPath` 只能辅助表达当前导航态，不能作为阻止新导航的全局锁。
- `router.afterEach` 写 `document.title` 前必须确认当前真实路由仍等于本次目标，避免旧导航晚到覆盖新页面标题。
- 涉及平台壳导航的回归验证必须覆盖跨顶部模块和侧边栏子模块的快速连续点击，不只验证单模块内切换。

#### 已验证：

- `cd frontend && cmd /c npm run build` 通过；仍只有既有 `web-tree-sitter` 警告。
- Playwright 精确快速切换路径验证通过：最终停在 `/api-testing/history`，浏览器标题为“请求历史 - TestHub”，顶部模块、侧栏高亮和页面正文一致，未出现 `beforeunload`、`pagehide`、`visibilitychange(hidden)` 或整页刷新事件。

#### 相关文件：

- `frontend/src/layout/index.vue`
- `frontend/src/layout/components/PlatformSidebar.vue`
- `frontend/src/router/index.js`

### 3.27 2026-06-17 SPA 表单默认行为硬化

2026-06-17 已完成前端全局表单默认提交风险收口，作为平台壳“卡住 / 刷新体感”问题的第二类根因处理。

#### 当前冻结结论：

- Element Plus `<el-form>` 会渲染为原生 `<form>`，不能默认认为它不会提交页面。
- 所有 `<form>` / `<el-form>` 必须显式添加 `@submit.prevent`。
- 所有原生 `<button>` 必须显式声明 `type`；默认使用 `type="button"`，只有明确业务提交链路时才允许 `type="submit"`。
- SPA 页面不得依赖浏览器默认提交、当前 URL 重新请求或整页刷新兜底业务动作。
- 后续新增表单、弹窗表单、筛选区、自定义按钮时，必须同时检查 Enter 键和按钮默认类型。

#### 已验证：

- 静态扫描 `frontend/src/**/*.vue`，结果为 `NO_UNPROTECTED_FORMS`。
- 静态扫描 `frontend/src/**/*.vue`，结果为 `NO_UNTYPED_BUTTONS`。
- 静态扫描未发现 `native-type="submit"`、`type="submit"` 或 submit input。
- `git diff --check -- frontend/src frontend/AGENTS.md docs/project-memory/error_prevention_log.md docs/project-memory/task_handoff.md docs/project-memory/module_memory.md docs/project-memory/dialogue_bootstrap.md 更新日志.md` 通过；仅有 Windows 行尾提示。
- `cd frontend && cmd /c npm run build` 通过；仍只有既有 `web-tree-sitter` 的 `fs/path` externalized 与 `eval` 警告。

#### 相关文件：

- `frontend/AGENTS.md`
- `frontend/src/views/**/*.vue`
- `docs/project-memory/error_prevention_log.md`

### 3.28 2026-06-18 接口自动化 P0-2 AI 生成目标类型边界

2026-06-18 已补充接口自动化 P0-2 Spec/TDD 的关键边界，后续开发必须继承。

#### 当前冻结结论：

- 接口测试用例是原子资产，继续由 `ApiRequest` 承接。
- 测试套件是编排资产，继续由 `TestSuite + TestSuiteRequest` 承接。
- AI 生成接口测试用例时只生成 `ApiRequest` 兼容字段，不直接生成或修改测试套件。
- 生成后的接口测试用例先进入接口测试用例资产列表；是否加入测试套件，由用户后续通过“加入套件 / 导入套件”动作完成。
- P0-2 只做目标类型下拉、Prompt 按类型选择、任务固化目标类型、结果页按目标类型展示和非功能采纳保护。
- P0-3 再做 `api_test_case` 结果采纳到 `ApiRequest`，采纳时由用户选择 `ApiProject + ApiCollection`。
- **现有 AI 生成测试用例逻辑严禁重写**：生成任务创建、模型调用、流式输出、取消、自动评审、轮询恢复和功能测试采纳主链必须保留，只允许在外层套用 `target_type`、Prompt 选择和字段展示契约。

#### 相关文件：

- `docs/api-automation/api-automation-p0-2-ai-target-type-spec.md`
- `docs/api-automation/api-automation-p0-2-ai-target-type-tdd.md`
- `docs/api-automation/api-automation-object-closure-audit.md`

### 3.29 2026-06-19 接口自动化阶段 A 对象闭环 P0 补强

2026-06-19 已完成阶段 A Execution 和 VDD 文档回写，以下结论后续开发必须继承。

#### 当前冻结结论：

- `/api-testing/test-cases` 继续固定为接口测试用例资产列表，技术承接为 `ApiRequest`。
- `/api-testing/test-suites` 继续固定为测试套件编排和执行页面，技术承接为 `TestSuite + TestSuiteRequest`。
- `/api-testing/automation` 仅作为旧入口兼容重定向保留，不再作为侧边栏正式入口。
- 阶段 A 不新增 `ApiTestCase` 表，不修改当前 AI 生成测试用例主链，不进入 P0-2 目标类型下拉和 P0-3 采纳入库。
- 已存在接口测试用例可以通过 `POST /api-testing/requests/{id}/move-collection/` 移动到同项目集合；后端必须校验同项目和用户项目权限。
- 调试工作区必须展示并保存所属集合；P0 阶段新建接口测试用例必须选择集合，不继续制造新的无项目归属用例。
- 请求历史“清空历史”必须走真实后端接口 `POST /api-testing/histories/clear/`，按当前筛选范围清空，不允许再保留假入口或只做前端隐藏。
- 套件级断言必须保存到 `TestSuiteRequest.assertions`，执行时优先使用套件级断言；如果为空，再回退到 `ApiRequest.assertions`，保证旧套件兼容。
- 项目负责人字段前端只读展示，不再提交后端只读字段造成误导。
- 删除项目、集合、接口测试用例、环境前必须提示级联风险。
- 接口自动化页面业务请求继续收口到 `frontend/src/api/api-testing.js`，不得重新直接导入 `@/utils/api`。

#### 已验证：

- `python -m py_compile apps\api_testing\models.py apps\api_testing\serializers.py apps\api_testing\views.py apps\api_testing\urls.py apps\api_testing\utils.py` 通过。
- `cd frontend && cmd /c npm run build` 通过；仍只有既有 `web-tree-sitter` 警告。
- 阶段 A 静态检索未发现新增整页刷新兜底、未实现假入口或接口自动化页面直接业务请求。

#### 相关文件：

- `docs/api-automation/api-automation-p0-object-closure-fix-tdd.md`
- `docs/api-automation/api-automation-p0-object-closure-fix-vdd.md`
- `apps/api_testing/views.py`
- `apps/api_testing/utils.py`
- `frontend/src/api/api-testing.js`
- `frontend/src/views/api-testing/ApiTestCaseList.vue`
- `frontend/src/views/api-testing/InterfaceManagement.vue`
- `frontend/src/views/api-testing/RequestHistory.vue`
- `frontend/src/views/api-testing/AutomationTesting.vue`

### 3.30 2026-06-19 接口自动化测试套件导航正式拆分

2026-06-19 已完成接口自动化“接口测试用例 / 测试套件”侧边栏入口补强，以下结论后续开发必须继承。

#### 当前冻结结论：

- `frontend/src/config/navigation.js` 是侧边栏可见入口真源；只新增页面或路由，不把 `NAV_ENTRY_STATUS.KEEP` 同步到导航真源，就不会在侧边栏显示。
- 接口自动化侧边栏正式可见入口为：
  - `/api-testing/test-cases` = 接口测试用例
  - `/api-testing/test-suites` = 测试套件
- 旧 `/api-testing/automation` 保留为隐藏兼容入口，访问后重定向到 `/api-testing/test-suites`。
- 页面标题、Dashboard 快捷入口、中文 / 英文 i18n 文案必须统一使用“测试套件 / Test Suites”，不得继续把套件页作为可见“自动化测试”入口。

#### 已验证：

- 静态检索确认 `/api-testing/test-suites` 已进入导航真源和路由，`/api-testing/automation` 仅作为隐藏兼容路由保留。
- 静态检索确认接口自动化可见页面文案不再残留 `Automation Testing` 作为套件页标题。

#### 相关文件：

- `frontend/src/config/navigation.js`
- `frontend/src/router/index.js`
- `frontend/src/locales/lang/zh-cn/api-testing.js`
- `frontend/src/locales/lang/en/api-testing.js`
- `frontend/src/views/api-testing/Dashboard.vue`
- `frontend/src/views/api-testing/ApiTestCaseList.vue`

### 3.31 2026-07-08 P0.1 剩余闭环收口

2026-07-08 已完成 P0.1 剩余闭环，主要补齐接口权限 / 认证一致性、模拟实现清理和误导性注释 / 假入口清理。

#### 当前冻结结论：

- 注册接口和测试注册接口不再返回 `temp_token_*`，统一返回 JWT `access/refresh`。
- `logout`、`profile` 等用户信息接口显式要求登录态，匿名访问应返回 401。
- UI 自动化元素定位器验证没有真实浏览器执行环境时，不得返回模拟成功；当前返回 501 和 `LOCATOR_VALIDATION_NOT_IMPLEMENTED`。
- UI 自动化历史未调用的模拟步骤日志和模拟失败截图 helper 已删除，后续不能伪造执行日志或失败截图作为执行证据。
- 接口自动化 Allure 结果时间来源改为执行记录时间和请求 `response_time`，不再使用模拟开始 / 结束时间。
- 页面树“页面名称编辑”暂未接入保存接口时，前端必须明确提示不会修改名称，不能静默关闭造成假成功。
- 本轮公开接口白名单写入 `docs/tasks/2026-07-04-p0-1-remaining-closure/public-api-whitelist.md`。

#### 已验证：

- `python -m py_compile apps\api_testing\views.py apps\data_factory\views.py apps\ui_automation\views.py apps\users\views.py apps\users\test_views.py` 通过。
- `cd frontend && cmd /c npm run build` 通过；仍只有既有 `web-tree-sitter` 警告。
- `powershell -ExecutionPolicy Bypass -File scripts\rule_check.ps1` 通过。
- `git diff --check` 通过；仅有 Windows 行尾转换提示。
- DRF 请求级验证通过：注册返回 JWT 双 token且无 `temp_token_*`；匿名 `profile/logout` 返回 401；携带 JWT 的 `profile` 返回 200；App 报告 media 直连返回 403；匿名报告 API 与匿名元素验证返回 401。

#### 未验证：

- 真实浏览器主流程。
- 真实 App 报告文件存在时的 200 访问。
- 真实跨用户 / 跨项目无权限对象 403。
- 浏览器 EventSource 凭据行为。

#### 相关文件：

- `docs/tasks/2026-07-04-p0-1-remaining-closure/spec-sdd.md`
- `docs/tasks/2026-07-04-p0-1-remaining-closure/tdd.md`
- `docs/tasks/2026-07-04-p0-1-remaining-closure/public-api-whitelist.md`
- `docs/tasks/2026-07-04-p0-1-remaining-closure/vdd.md`
- `apps/users/views.py`
- `apps/users/test_views.py`
- `apps/ui_automation/views.py`
- `apps/api_testing/views.py`
- `frontend/src/views/ui-automation/elements/ElementManagerEnhanced.vue`

### 3.32 2026-07-10 P0.2 跨模块硬化第一批

2026-07-10 已按用户确认跳过剩余浏览器回归，直接进入 P0.2 第一批。第一批范围只覆盖生产配置复核、核心配置说明、生产调试日志清理和敏感信息保护最小闭环。

#### 当前冻结结论：

- 生产环境 `SECRET_KEY` 不允许继续使用默认开发值、`.env.example` 示例值、`your-secret-key` 或长度小于 32 的弱密钥。
- `.env.example` 必须明确告诉使用者：`DEBUG=False`、`ALLOWED_HOSTS`、`CORS_ALLOWED_ORIGINS`、安全 `SECRET_KEY`、数据库地址和 `REDIS_URL` 是生产部署重点配置。
- 登录、token 刷新、路由守卫、AI 模型配置、Prompt 配置、生成配置、AI 智能模式配置页不得在控制台输出 token、用户对象、API Key、完整表单对象或 axios error 对象。
- AI 模型调用日志必须走脱敏工具，不打印完整响应正文、API Key、token、Authorization、Cookie、password 等敏感信息。
- OpenAI-like 响应兼容和空响应保护继续保留，不能为了清理日志而回退为空内容直传。

#### 已验证：

- `.\venv\Scripts\python.exe -m py_compile backend\settings.py apps\core\security.py apps\requirement_analysis\models.py` 通过。
- `.\venv\Scripts\python.exe manage.py check` 在开发配置下通过。
- 合法生产配置 `manage.py check` 通过。
- 弱 `SECRET_KEY`、`ALLOWED_HOSTS=*`、`DISABLE_CSRF_FOR_API=True`、缺 CORS origins 的生产配置阻断抽样通过。
- `cd frontend && cmd /c npm run build` 通过；仍只有既有 `web-tree-sitter` 警告。
- `powershell -ExecutionPolicy Bypass -File scripts\rule_check.ps1` 通过。
- `git diff --check` 通过；仅有 Windows 行尾转换提示。
- 脱敏函数抽样验证通过，原始 JWT、API Key、Cookie、password 不出现在返回值中。
- 目标源码和构建产物静态扫描未发现本轮已清理的敏感调试日志。

#### 未验证：

- 用户明确要求跳过剩余浏览器回归，所以本轮没有复测真实浏览器登录、路由跳转、AI 配置页保存和需求分析生成页控制台。
- P0.1 / 阶段 A 遗留的真实浏览器主流程、真实 App 报告文件 200、真实无权限对象 403、浏览器 EventSource 凭据行为仍未补。
- 真实生产部署环境没有执行端到端启动和登录验证。

#### 下一步主线：

- 进入 P0.2 第二批：先做需求分析生成进度 SSE 的统一封装和页面级验证。
- 需求分析 SSE 稳定后，再迁 App 自动化实时进度 / 日志连接。
- App 自动化迁移稳定后，再迁接口测试工作区 WebSocket / SSE。
- 接口错误结构统一试点继续放在 P0.2 第三批。

#### 相关文件：

- `docs/tasks/2026-07-10-p0-2-cross-module-hardening/spec-sdd.md`
- `docs/tasks/2026-07-10-p0-2-cross-module-hardening/tdd.md`
- `docs/tasks/2026-07-10-p0-2-cross-module-hardening/vdd.md`
- `backend/settings.py`
- `.env.example`
- `apps/core/security.py`
- `apps/requirement_analysis/models.py`
- `frontend/src/views/auth/Login.vue`
- `frontend/src/utils/api.js`
- `frontend/src/stores/user.js`
- `frontend/src/router/index.js`
- `frontend/src/views/requirement-analysis/AIModelConfig.vue`
- `frontend/src/views/requirement-analysis/PromptConfig.vue`
- `frontend/src/views/requirement-analysis/GenerationConfigView.vue`
- `frontend/src/views/configuration/AIIntelligentModeConfig.vue`

### 3.33 2026-07-10 P0.2 第二批和第三批合并推进

2026-07-10 用户要求 P0.2 第二批和第三批一起做。本轮按保守合并方式推进：第二批只迁需求分析生成进度 SSE，第三批只做错误解析工具和需求分析生成任务错误结构试点。

#### 当前冻结结论：

- 需求分析生成进度不再允许页面组件直接 `new EventSource`，统一通过 `useGenerationTaskTracking -> useEventSource` 管理连接。
- `useEventSource` 负责 URL 构造、关闭、错误、有限重连和降级回调；页面只处理业务 payload。
- `useWebSocket` 已作为统一入口落地，但 App 自动化和接口测试工作区本轮还没有迁移。
- 前端错误提示优先通过 `frontend/src/utils/errorMessage.js` 解析，兼容 `message`、`error`、`detail`、`details` 和字段级错误。
- 后端错误响应试点结构为 `code/message/error/details/request_id`，其中 `error` 是旧页面兼容字段；成功响应结构不变。
- 本轮试点覆盖需求分析生成任务：`generate` 的 400 校验错误、`progress` 的 403 / 404 / 500、`stream_progress` 的 403 / 404 JSON 错误。

#### 已验证：

- `.\venv\Scripts\python.exe -m py_compile apps\core\responses.py apps\requirement_analysis\views.py` 通过。
- `.\venv\Scripts\python.exe manage.py check` 通过。
- `cd frontend && cmd /c npm run build` 通过；仍只有既有 `web-tree-sitter` 警告。
- APIClient 抽样验证：进度接口 404 和生成接口 400 均返回 `code/message/details/request_id`。
- 静态扫描确认 `RequirementAnalysisView.vue` 不再有 `console`、`new EventSource`、`startStreamingProgress`、`pollInterval`。
- `RequirementAnalysisView` 构建产物 `console` 扫描无命中。
- `powershell -ExecutionPolicy Bypass -File scripts\rule_check.ps1` 通过。
- `git diff --check` 通过；仅有 Windows 行尾转换提示。

#### 未验证：

- 未做真实浏览器页面操作，所以未证明运行时 Network 里 SSE 连接一定按预期关闭。
- App 自动化实时进度 / 日志连接已迁到 `useWebSocket`，未做真实浏览器运行时回归。
- 接口测试工作区 WebSocket 已迁到 `useWebSocket`，未做真实浏览器运行时回归。
- 未全仓统一错误结构，也未新增全局 DRF exception handler。

#### 下一步主线：

- App 自动化实时进度 / 日志连接已迁到 `useWebSocket`。
- 接口测试工作区 WebSocket 已迁到 `useWebSocket`。
- 接口错误结构后续按模块继续试点，不做一次性全仓替换。

#### 相关文件：

- `frontend/src/composables/useEventSource.js`
- `frontend/src/composables/useWebSocket.js`
- `frontend/src/composables/useGenerationTaskTracking.js`
- `frontend/src/utils/errorMessage.js`
- `frontend/src/utils/api.js`
- `frontend/src/views/requirement-analysis/RequirementAnalysisView.vue`
- `frontend/src/views/auth/Login.vue`
- `apps/core/responses.py`
- `apps/requirement_analysis/views.py`
- `docs/tasks/2026-07-10-p0-2-cross-module-hardening/vdd.md`

## 4. 当前代码层已落地、但仍需继续推进的点

以下内容已经有“基座”或“真源”，但尚未全站完成：

- 导航冻结方案已经形成，但旧 layout 菜单结构仍是历史实现
- 页面壳组件已存在，但旧页面尚未批量迁移
- 路由 meta 已统一，但不是所有旧页面都已彻底收敛
- 状态组件已落地，但只在少量样例页面接入
- 配置中心 / 系统管理边界已文档化，但系统管理前端页面群仍未真正建设
- AI 生成链路第一阶段和“处理状态”已成立，但结果层、正式资产层和业务链 AI 助手嵌入仍未完整深化
- P0.2 跨模块硬化第一批已完成；第二批和第三批已合并完成需求分析生成进度 SSE 迁移、统一错误解析工具和需求分析生成任务错误结构试点；下一步应迁 App 自动化实时连接，再迁接口测试工作区实时连接
- 接口自动化 P0-1 已完成自身闭环；P0.1 剩余闭环已完成代码和 VDD，但真实浏览器主流程、真实 App 报告文件 200、真实无权限对象 403、浏览器 EventSource 凭据行为待补；阶段 A 对象闭环 P0 补强已完成 Execution/VDD，但真实浏览器人工回归待补；P0-2 Spec 已补充 AI 生成目标类型与接口用例 / 套件拆分边界，等待确认后进入后续实现；接口测试用例采纳、Web/App 自动化采纳仍未实现

## 5. 最近一轮稳定 bug 修复结论

这是后续继续开发时必须继承的实现口径：

- 项目详情进入需求分析页时，由于页面存在 `keepAlive`，必须在 `activated` 和路由 `query` 变化时重新同步项目上下文，否则会丢失自动关联项目
- `vue-router` 的 `RouteMeta` 自定义字段已经通过 `frontend/src/types/router-meta.d.ts` 补齐；新增 meta 字段时必须同步更新
- AI 采纳生成的测试用例需要自动挂默认版本，优先基线版本，避免产生“未关联版本”的新资产
- 任务详情页和生成结果批次页的结果数量口径必须统一，避免不同页面各自解析导致数量不一致
- 重复采纳、批量采纳、保存到正式用例三条入口都必须走同一套幂等逻辑，不能只修一个入口

## 6. 当前验收与环境限制

当前环境有以下验证限制：

- 当前前端没有完整的项目级 ESLint 配置可直接用于校验
- 2026-06-16 已实测 `frontend` 执行 `cmd /c npm run build` 可以通过；若后续再次失败，需先区分环境波动还是代码问题
- 2026-03-21 已实测后端受影响文件执行 `py_compile` 可以通过
- 当前 Python 环境不保证已安装 Django；`python manage.py check` 可能因缺少 Django 依赖而失败，这属于环境问题，不等于本轮代码语法失败
- 当前目录未必总是一个完全干净的 git 工作树，不能默认依赖“没有脏改动”

因此：

- 做前端改动时，优先做文件级核对和构建级核对
- 做后端改动时，至少做导入级或编译级校验
- 若验证失败，要先区分是环境问题还是代码问题
- 涉及顶部模块、侧边栏、根层 `App.vue`、`layout/index.vue`、认证跳转或 `router-view` key 时，除构建外必须补跑页面级快速切换验证：顶部大模块 -> 侧边栏子模块，确认最终停在最后点击目标，且没有 `beforeunload`、`pagehide` 或主文档请求。

## 7. 当前阶段推进原则

以下内容仍作为当前阶段推进口径继续有效：

- 对平台级任务，先冻结边界、真源和基线，再逐步替换旧页面
- 2.x 阶段任务推进时，必须先明确“本轮边界”，防止对象层、生成链路、资产承接、自动化草稿中心和执行闭环混成一轮
- 若阶段结论已经沉淀为长期规则，应同步回写仓库内 `.cursor/*.md` 或对应目录 `AGENTS.md`，不要长期停留在本文件里

## 8. 下一步主线

若后续继续推进平台化和测试设计收口，当前建议顺序为：

1. 继续接入统一状态组件
2. 把导航真源接入 layout / 首页
3. 分批把旧页面迁移到统一页面壳
4. 继续深化 2.2 结果层 / 资产层 / 业务链 AI 助手
5. 再进入 2.3 自动化草稿中心与更下游链路
6. P0.2 跨模块硬化除真实浏览器回归外已收尾；App 自动化执行进度和接口测试工作区 WebSocket 已迁到 `useWebSocket`
7. 接口自动化需求主线继续保留：后续补 P0.1 / 阶段 A 真实浏览器回归，再继续 P0-2：AI 需求分析生成目标类型下拉、Prompt 按类型选择、接口用例字段展示；P0-3 再做接口测试用例采纳闭环

## 9. 2026-07-10 P0.2 除回归外收尾结论

- P0.2 第一批已完成：生产配置复核、`.env.example` 生产配置说明、前端敏感调试日志清理、后端 AI 日志脱敏。
- P0.2 第二三批已完成：需求分析生成进度 SSE 统一走 `useGenerationTaskTracking -> useEventSource`，前端统一错误解析工具落地，需求分析生成任务错误结构完成试点。
- P0.2 剩余实时连接已完成：App 自动化执行进度和接口测试工作区 WebSocket 均已迁到 `frontend/src/composables/useWebSocket.js`；App 自动化保留有限重连失败后降级轮询。
- 接口错误结构继续小步试点：接口测试 `move-collection` 的未选集合、跨项目移动、无权限移动 3 个错误分支已返回 `code/message/error/details/request_id`，成功响应不变。
- 当前结论：除用户明确跳过的真实浏览器回归外，P0.2 各部分可以按代码收尾处理并进入下一阶段。
- 残余风险：未做真实浏览器页面操作，不能证明运行时 WebSocket / SSE 的 Network 创建、关闭、终态停止和页面离开清理在浏览器中全部通过；后续要补时必须单独做回归，不能引用本轮为 V4。




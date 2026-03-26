# TestHub 项目开发记忆

更新时间：2026-03-25

## 1. 文件职责

本文件属于 C 层“项目开发记忆”，用于记录当前项目推进过程中的阶段事实、冻结方案、当前验收口径和下一步主线。

使用原则：

- 本文件只记录“已经确认的项目事实、冻结方案、已落地产物、当前验收口径和阶段限制”。
- 正式规则以 `GEMINI.md` 和仓库内 `.antigravity/*.md` 为准。
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

- `docs/平台现状地图.md`

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

- `docs/navigation-freeze-plan.md`
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

- `docs/page-shell-spec.md`
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

- `docs/route-meta-spec.md`
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

- `docs/config-vs-system-boundary.md`

当前关键结论：

- 配置中心承接 AI 模型、提示词、生成配置、环境配置、通知通道配置、Dify、平台级 AI 服务配置
- 系统管理承接个人资料、登录注册、后续用户 / 角色 / 权限 / 审计能力
- 各域定时任务、执行记录、通知日志暂不纳入这两个模块，后续向执行中心或审计中心收敛

### 3.6 平台 smoke 回归基线

已经建立最小 smoke 回归基线。

相关文件：

- `docs/platform-smoke-baseline.md`

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

- `docs/ui-state-spec.md`
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

- `docs/log-audit-boundary.md`

当前关键结论：

- 登录日志、操作日志、审计日志、AI 调用审计固定归 `系统管理`
- 请求历史、任务执行日志、执行记录、通知日志固定向 `执行中心` 或结果页体系收敛
- Dashboard 最近活动只保留摘要，不再扩张成正式治理日志中心
- `AIExecutionRecord` 属于执行结果，不等于 AI 调用审计

已做的轻量落地：

- `frontend/src/config/navigation.js` 中系统管理已补预留入口：登录日志、操作日志、审计日志、AI 调用审计

### 3.9 统一平台壳

阶段 1 已完成统一平台壳的基础落地。

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

- `docs/ai-generation-chain-spec.md`
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

- `docs/ai-generation-chain-spec.md`
- `docs/ai-generation-cancel-spec.md`
- `docs/ai-review-link-spec.md`
- `apps/requirement_analysis/models.py`
- `apps/requirement_analysis/serializers.py`
- `apps/requirement_analysis/views.py`
- `frontend/src/composables/useGenerationTaskTracking.js`
- `frontend/src/views/requirement-analysis/RequirementAnalysisView.vue`
- `frontend/src/views/requirement-analysis/TaskDetail.vue`
- `frontend/src/views/requirement-analysis/GeneratedTestCaseList.vue`
- `frontend/src/views/reviews/AutoReviewList.vue`
- `frontend/src/views/reviews/ReviewList.vue`

## 4. 当前代码层已落地、但仍需继续推进的点

以下内容已经有“基座”或“真源”，但尚未全站完成：

- 导航冻结方案已经形成，但旧 layout 菜单结构仍是历史实现
- 页面壳组件已存在，但旧页面尚未批量迁移
- 路由 meta 已统一，但不是所有旧页面都已彻底收敛
- 状态组件已落地，但只在少量样例页面接入
- 配置中心 / 系统管理边界已文档化，但系统管理前端页面群仍未真正建设
- AI 生成链路第一阶段和“处理状态”已成立，但结果层、正式资产层和业务链 AI 助手嵌入仍未完整深化

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
- 2026-03-21 已实测 `frontend` 执行 `cmd /c npm run build` 可以通过；若后续再次失败，需先区分环境波动还是代码问题
- 2026-03-21 已实测后端受影响文件执行 `py_compile` 可以通过
- 当前 Python 环境不保证已安装 Django；`python manage.py check` 可能因缺少 Django 依赖而失败，这属于环境问题，不等于本轮代码语法失败
- 当前目录未必总是一个完全干净的 git 工作树，不能默认依赖“没有脏改动”

因此：

- 做前端改动时，优先做文件级核对和构建级核对
- 做后端改动时，至少做导入级或编译级校验
- 若验证失败，要先区分是环境问题还是代码问题

## 7. 当前阶段推进原则

以下内容仍作为当前阶段推进口径继续有效：

- 对平台级任务，先冻结边界、真源和基线，再逐步替换旧页面
- 2.x 阶段任务推进时，必须先明确“本轮边界”，防止对象层、生成链路、资产承接、自动化草稿中心和执行闭环混成一轮
- 若阶段结论已经沉淀为长期规则，应同步回写仓库内 `.antigravity/*.md`，不要长期停留在本文件里

## 8. 下一步主线

若后续继续推进平台化和测试设计收口，当前建议顺序为：

1. 继续接入统一状态组件
2. 把导航真源接入 layout / 首页
3. 分批把旧页面迁移到统一页面壳
4. 继续深化 2.2 结果层 / 资产层 / 业务链 AI 助手
5. 再进入 2.3 自动化草稿中心与更下游链路

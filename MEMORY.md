# TestHub 会话记忆

更新时间：2026-03-17

## 1. 目的

本文件用于保存当前项目最近一轮高频对话形成的稳定记忆，供后续新对话快速接手。

使用原则：

- 新对话进入仓库后，优先阅读本文件。
- 本文件用于记录“当前已经确认的项目事实、冻结方案和已落地产物”。
- 若本文件与实际代码冲突，以实际代码为准，并及时回写本文件。

## 2. 当前项目真实基线

- 项目：`TestHub` 智能测试管理平台
- 根目录关键结构：`backend`、`apps`、`frontend`、`media`、`logs`、`allure`
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

## 3. 当前对话中已经冻结的关键结论

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
- `module`
- `pageType`
- `icon`
- `keepAlive`
- `hidden`

相关文件：

- `docs/route-meta-spec.md`
- `frontend/src/router/route-meta.js`
- `frontend/src/router/index.js`
- `frontend/src/layout/index.vue`

当前结论：

- 页面标题、面包屑、模块归属优先从路由 `meta` 取
- 不再维护散落的路径标题映射

### 3.5 配置中心与系统管理边界

已明确配置中心与系统管理的归类边界。

相关文件：

- `docs/config-vs-system-boundary.md`

当前关键结论：

- 配置中心承接 AI 模型、提示词、生成配置、环境配置、通知通道配置、Dify、平台级 AI 服务配置
- 系统管理承接个人资料、登录注册、后续用户 / 角色 / 权限 / 审计能力
- 各域定时任务、执行记录、通知日志暂不纳入这两个模块，后续向执行中心或审计中心收敛

已做的轻量落地：

- 配置中心里历史文案 `scheduledTaskConfig` 已改成“通知通道配置”

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
- 前端页面状态统一采用 `UI_PAGE_STATE` 枚举式口径，优先使用 `pageState / xxxState`，状态组件统一通过 `StateBlock` 系列承载，支持整页态与局部态，并通过通用动作区承接 `retry/create/back/goHome/reset` 等交互。
- 统一常量文件：`frontend/src/components/ui-states/state-constants.js`
- 状态组件已支持 `primaryActionText` / `secondaryActionText` 和 `@primary-action` / `@secondary-action`
- 旧 `actionText` / `@action` 继续兼容

已接入样例页面：

- `frontend/src/views/Home.vue`
- `frontend/src/views/projects/ProjectList.vue`
- `frontend/src/views/api-testing/Dashboard.vue`

复杂工作台试点：

- `frontend/src/views/api-testing/InterfaceManagement.vue` 左侧集合树 / 搜索区域

当前约束：

- 暂不全站替换旧页面
- 不改业务接口逻辑

### 3.8 日志与审计入口归属

已经冻结日志与审计入口归属规则。

相关文件：

- docs/log-audit-boundary.md

当前关键结论：

- 登录日志、操作日志、审计日志、AI 调用审计固定归 系统管理
- 请求历史、任务执行日志、执行记录、通知日志固定向 执行中心 或结果页体系收敛
- 平台日志统一分为治理日志与执行日志两类：登录日志、操作日志、审计日志、AI 调用审计统一归系统管理；请求历史、任务执行日志、执行记录、通知日志统一归执行中心或结果页。后续不得再将治理类日志挂回业务模块或配置中心。
- Dashboard 最近活动只保留摘要，不再扩张成正式治理日志中心
- AIExecutionRecord 属于执行结果，不等于 AI 调用审计

已做的轻量落地：

- rontend/src/config/navigation.js 中 系统管理 已补预留入口：登录日志、操作日志、审计日志、AI 调用审计

### 3.9 统一平台壳

阶段 1 已完成统一平台壳的基础落地。

相关文件：

- rontend/src/layout/index.vue
- rontend/src/layout/platform-layout.js
- rontend/src/layout/components/PlatformGlobalHeader.vue
- rontend/src/layout/components/PlatformSidebar.vue
- rontend/src/layout/components/PlatformPageHeader.vue

当前关键结论：

- 平台统一壳层负责顶部全局栏、模块侧边导航、面包屑、页面标题区和主内容容器；业务页面不再自带平台级头部与导航结构。一级模块切换由平台壳负责，模块内页面导航由侧边栏负责。
- 页面标题、面包屑、模块归属、页面类型优先由路由 meta 驱动
- 顶部全局搜索、最近访问、收藏、消息通知、项目上下文当前仍为占位入口，不提前实现后续阶段能力
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

- 全局搜索入口固定挂在顶部全局栏，采用轻量 `command palette` 形态，不与最近访问 / 收藏面板混成一个系统
- 第一版优先搜索页面 / 菜单 / 入口；轻资产只接入测试设计项目和测试用例，且关键字长度 `>= 2` 才触发动态搜索
- 从搜索结果打开页面后，仍然走统一路由链，因此会自然写入最近访问

### 3.14 深链接与回跳第一版边界

阶段 1.9 已冻结深链接与回跳第一版边界。

当前关键结论：

- 深链接第一版只覆盖已有稳定详情路由的高价值对象；`params` 只承接对象身份，来源上下文统一走 `query`
- 来源上下文固定使用 `from / fromPath / fromTitle / fromModule`；`fromPath` 必须做最小校验，只允许站内相对路径
- 回跳顺序固定为：合法 `fromPath` -> 所属列表页 -> `router.back()`
- Home、最近访问、收藏、全局搜索和列表入口继续保持解耦，只共享同一套 deeplink 规则

### 3.15 平台壳滚动复位规则

阶段 1 平台化过程中已冻结统一滚动复位规则。

当前关键结论：

- 平台主内容区使用独立滚动容器时，跨页面路由切换后应由 Layout 统一将主内容容器滚动复位到顶部
- 该规则优先覆盖 Home 快捷继续、最近访问、收藏、全局搜索、侧边栏和模块切换等跨页面入口
- 同一路径下仅 `query` 变化的子视图切换不默认强制滚动复位；若页面存在独立局部滚动容器，应由页面自身按需处理

## 4. 当前代码层已落地、但仍需继续推进的点

以下内容已经有“基座”或“真源”，但尚未全站完成：

- 导航冻结方案已经形成，但旧 layout 菜单结构仍是历史实现
- 页面壳组件已存在，但旧页面尚未批量迁移
- 路由 meta 已统一，但不是所有旧页面都已彻底收敛
- 状态组件已落地，但只在少量样例页面接入
- 配置中心 / 系统管理边界已文档化，但系统管理前端页面群仍未真正建设

## 5. 已知环境问题

当前环境有以下验证限制：

- 当前前端没有完整的项目级 ESLint 配置可直接用于校验
- 2026-03-17 已实测 `frontend` 执行 `cmd /c npm run build` 可以通过；若后续再次失败，需先区分环境波动还是代码问题
- 当前目录未必总是一个可用的 git 工作树，不能默认依赖 `git diff` / `git status`

因此：

- 做前端改动时，优先做文件级核对和局部逻辑核对
- 若构建失败，要先区分是环境问题还是代码问题

## 6. 与用户协作的固定偏好

这是当前对话里已反复体现的偏好，后续严格保持：

- 沟通统一使用中文
- 规范、设计、任务、交付说明统一用中文
- 优先做“规划 + 轻量落地”，避免一次性大重构
- 对平台级任务，先冻结边界、真源和基线，再逐步替换旧页面
- 如果只是项目特有的规则需要修正，就改；跨项目都成立的通用规则不要乱动

## 7. 新对话接手建议

新对话若继续本项目，建议按以下顺序读取：

1. `AGENTS.md`
2. 本文件 `MEMORY.md`
3. 与当前任务最相关的 `docs/*.md`
4. 实际前端 / 后端入口代码

若后续继续推进前端平台化，优先顺序建议为：

1. 继续接入统一状态组件
2. 把导航真源接入 layout / 首页
3. 分批把旧页面迁移到统一页面壳
4. 再推进执行中心、系统管理等预留模块






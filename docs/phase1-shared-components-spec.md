# 阶段 1 第一批共享组件规范

## 1. 背景

当前平台已经完成：

- 统一 Layout
- 统一面包屑和页面头部
- `PlatformPageHeader.vue` 作为唯一页面头部真源
- `usePlatformPageHeader.js` 作为页面向 Layout 注册头部配置的桥接
- 统一状态组件基座

阶段 1.6 的目标不是建设完整设计系统，而是在现有平台壳之上，先抽出第一批高频、低风险、跨页面复用的主体层组件，为后续 `Home` 工作台、模块 Dashboard 和列表页统一提供积木。

## 2. 本轮范围

### 2.1 本轮要解决

- 收敛 Dashboard 中重复的统计卡、最近活动块、快捷入口卡
- 收敛列表页中高频出现的筛选栏容器
- 保持与现有状态组件体系兼容
- 为 `Home` 工作台和模块 Dashboard 的后续统一提供可直接复用的基础组件

### 2.2 本轮明确不做

- 不新增第二套页面头部体系
- 不重写 `PlatformPageHeader`
- 不建设完整设计系统
- 不抽通用复杂表格、通用工作台框架、通用详情引擎
- 不提前实现最近访问、收藏、全局搜索等真实功能

## 3. 组件清单

### 3.1 `FilterBar`

职责：

- 承接列表页筛选区的统一容器、布局和响应式折叠
- 与页面内的查询表单、筛选条件、重置按钮配合

所属层级：

- 页面主体层

适用页面：

- list 页优先
- 也可用于 workspace 页中的局部筛选区

Props：

- 当前版本无业务 props，优先通过 slot 承接内容

Slots：

- 默认插槽：筛选表单主体
- `actions`：筛选栏右侧附加操作
- `extra`：筛选栏下方扩展区

推荐用法：

- 页面自行维护 `searchText`、`statusFilter` 等状态
- `FilterBar` 只负责承接布局，不负责请求和状态流转

不建议滥用：

- 不要把页面主按钮重新塞回这里，页面级主操作优先放 `PlatformPageHeader`
- 不要把搜索空状态塞进组件内部，空结果仍由页面主体配合 `StateSearchEmpty` 展示

### 3.2 `StatCard`

职责：

- 统一 Dashboard 和摘要区的单个统计卡结构
- 承接图标、数值、标题、辅助描述和轻量加载态

所属层级：

- 页面主体层

适用页面：

- dashboard
- detail/result 页的概览统计区

Props：

- `title`
- `value`
- `description`
- `trendText`
- `icon`
- `accent`
- `loading`
- `compact`

Slots：

- `footer`

推荐用法：

- 页面自己负责请求和数据转换
- 统计数据加载时可传 `loading`

不建议滥用：

- 不要在卡片内直接发请求
- 不要把复杂图表、复杂交互都塞进单个 `StatCard`

### 3.3 `RecentList`

职责：

- 统一“最近活动 / 最近执行 / 最近记录”类块级容器
- 与统一状态组件兼容

所属层级：

- 页面主体层

适用页面：

- dashboard
- Home 工作台
- detail/result 页的最近记录区

Props：

- `title`
- `description`
- `items`
- `itemKey`
- `loading`
- `error`
- `loadingTitle`
- `loadingDescription`
- `emptyTitle`
- `emptyDescription`
- `errorTitle`
- `errorDescription`
- `errorActionText`

Slots：

- `header`
- `actions`
- `item`

事件：

- `retry`

推荐用法：

- 记录项内容通过 `item` slot 由页面自定义
- 空态、错误态、加载态优先复用 `StateEmpty`、`StateError`、`StateLoading`

不建议滥用：

- 不要把具体日志字段写死在组件内部
- 不要把真实“最近访问”业务逻辑提前实现到这里

### 3.4 `QuickActionCard`

职责：

- 统一工作台和 Dashboard 的快捷入口卡片
- 承接图标、标题、描述、徽标和点击行为

所属层级：

- 页面主体层

适用页面：

- Home 工作台
- dashboard

Props：

- `title`
- `description`
- `badge`
- `icon`
- `accent`
- `variant`
- `clickable`
- `disabled`

Slots：

- 默认插槽：卡片底部附加信息

事件：

- `click`

推荐用法：

- `Home` 使用默认尺寸
- dashboard 使用 `compact` 变体

不建议滥用：

- 不要把收藏、最近访问等真实业务状态硬塞到卡片内
- 不要把大块复杂工作台面板都改造成 `QuickActionCard`

## 4. 组件之间与 Layout 的职责边界

### 4.1 Layout 层

- 顶部全局栏
- 模块切换
- 侧边导航
- 面包屑承接
- `PlatformPageHeader` 挂载
- 主内容容器

### 4.2 页面头部层

- 仅保留 `PlatformPageHeader`
- 承接页面标题、副描述、状态标签、更新时间、页面级主操作

### 4.3 页面主体层

- `FilterBar`
- `StatCard`
- `RecentList`
- `QuickActionCard`
- 表格、图表、编辑器、结果内容等业务主体

## 5. 本轮刻意暂缓的组件

### 5.1 暂缓 `PageHeader`

原因：

- 页面头部真源已经冻结为 `PlatformPageHeader`
- 新增 `PageHeader` 会形成平行体系

### 5.2 暂缓 `FavoriteEntryCard`

原因：

- 容易提前透支阶段 1.3 收藏真实能力

### 5.3 暂缓 `PageToolbar`

原因：

- 当前 `ListShell` / `WorkspaceShell` 已有 `toolbar` slot
- 现阶段优先收敛更稳定的 `FilterBar`

### 5.4 暂缓复杂通用组件

包括：

- 通用复杂表格
- 通用工作台框架
- 通用详情引擎

原因：

- 抽象成本高
- 当前业务差异大
- 容易误伤现有页面

## 6. 第一批接入建议

### 6.1 优先接入页面

- `Home`
- 模块 Dashboard
- 列表页样例

### 6.2 推荐接入顺序

1. `Home`：`QuickActionCard`
2. `api-testing/Dashboard`：`StatCard`、`RecentList`、`QuickActionCard`
3. `ProjectList`：`FilterBar`

## 7. 后续扩展建议

- 阶段 1.2 可以直接基于 `QuickActionCard` 和 `RecentList` 组装工作台区块
- 阶段 1.7 可以把其他模块 Dashboard 逐步迁到 `StatCard` + `RecentList` + `QuickActionCard`
- 阶段 1.8 列表页统一时，可优先收敛 `FilterBar`

# 统一页面头部规范

## 1. 目标

本规范用于完成阶段 1 - 任务 1.5：在已经落地的统一 Layout 基础上，收敛出唯一页面头部真源。  
本次不是新增第二套 `PageHeader` 体系，而是升级现有 `PlatformPageHeader.vue`，让它成为 dashboard、list、workspace、detail/result 页的统一页面头部入口。

## 2. 核心原则

1. 只保留一套页面头部组件体系：`PlatformPageHeader`
2. 页面头部统一由 `Layout` 挂载，业务页不再各自重复渲染平台级标题区
3. 路由 `meta` 仍然是页面身份真源，页面只补充页面级动态信息
4. 页面头部只承接页面级信息，不回收平台级导航职责
5. 本次只做规范落地和样例接入，不提前做 1.2 / 1.3 / 1.4 的真实功能

## 3. 结构定义

统一页面头部支持以下结构：

1. 面包屑
2. 模块归属标签
3. 页面类型标签
4. 主标题
5. 副描述
6. 可选状态标签
7. 可选更新时间 / 最近操作说明
8. 可选辅助信息区
9. 右上角页面级主操作区

说明：

- 面包屑由 Layout 基于路由 `meta` 统一承接
- 主标题、描述、图标默认优先取路由 `meta`
- 状态标签、更新时间、辅助信息、页面级动作由具体页面通过统一配置入口补充

## 4. 页面类型差异

### 4.1 Dashboard

推荐头部内容：

- 标题：当前模块总览名
- 描述：当前概览范围
- 状态标签：如“实时概览”“数据异常”“只读”
- 更新时间：最近刷新时间
- 主操作：跳转到关键资产页、报告页
- 辅助信息：概览范围、统计口径说明

### 4.2 List

推荐头部内容：

- 标题：资产类型名称
- 描述：列表用途说明
- 状态标签：筛选中、只读、批量模式等
- 更新时间：最近刷新时间
- 主操作：新建、导入、批量操作
- 辅助信息：当前筛选条件、总数说明、权限提示

### 4.3 Workspace

推荐头部内容：

- 标题：当前工作台名称
- 描述：工作区目标说明
- 状态标签：编辑中、草稿、已绑定项目等
- 更新时间：最近保存时间
- 主操作：保存、运行、调试、发布
- 辅助信息：当前上下文、当前项目、选中资源

### 4.4 Detail / Result

推荐头部内容：

- 标题：详情对象名或结果页名
- 描述：对象摘要或结果说明
- 状态标签：状态、结果、风险等级
- 更新时间：最近执行时间、更新时间
- 主操作：返回、导出、重试、二次操作
- 辅助信息：对象 ID、成员数、环境数、执行范围等

## 5. 职责边界

### 5.1 Layout 层职责

- 顶部全局栏
- 一级模块切换
- 模块侧边导航
- 主内容容器
- 面包屑基础承接
- 统一挂载 `PlatformPageHeader`
- 基于 `route meta` 提供默认标题、模块、页面类型、图标

### 5.2 页面头部层职责

- 页面标题
- 页面副描述
- 页面状态标签
- 页面级更新时间 / 最近操作提示
- 页面级主操作区
- 页面级辅助信息区

### 5.3 页面主体层职责

- 筛选栏
- 图表
- 表格
- 编辑器
- 结果区
- 详情内容
- 弹窗和业务交互

## 6. route meta 与页面头部衔接

### 6.1 route meta 默认承接字段

推荐由 `route.meta` 承接的默认字段：

- `title`
- `description`
- `module`
- `pageType`
- `icon`
- `parentTitle`
- `activeMenu`

说明：

- `title / description / icon` 是页面头部的默认值
- `module / pageType / parentTitle / activeMenu` 继续服务 Layout 的模块归属、页面类型、面包屑和菜单高亮

### 6.2 页面动态补充字段

页面通过统一入口补充以下动态信息：

- `title`
- `description`
- `resolvedIcon`
- `statusTags`
- `updateText`
- `helperText`
- `metaItems`
- `actions`

页面只补充“本页动态数据”，不自己重复组装面包屑和模块导航。

## 7. PlatformPageHeader props / slots

### 7.1 props

`PlatformPageHeader` 当前统一支持：

- `breadcrumbItems`
- `moduleName`
- `pageTypeLabel`
- `pageTitle`
- `description`
- `resolvedIcon`
- `statusTags`
- `updateText`
- `helperText`
- `metaItems`
- `actions`

### 7.2 slots

保留 slot 能力，但不再发展第二套平行头部：

- `actions`

说明：

- 当前主通路是 `Layout -> PlatformPageHeader`
- slot 仅保留兼容和局部扩展能力，不作为页面自行挂载第二套头部的理由

## 8. 推荐用法

### 8.1 默认用法

1. 路由先定义 `meta.title / meta.description / meta.module / meta.pageType / meta.icon`
2. 页面在需要动态头部信息时，通过统一入口注册头部配置
3. Layout 统一读取路由 `meta` 和页面配置，渲染 `PlatformPageHeader`

### 8.2 页面接入原则

1. 若页面已有 `.page-header`，优先移除本地平台级标题区
2. 本地保留的内容必须是主体内容，不得继续承担面包屑和主标题职责
3. 页面只迁移标题、副说明、状态、更新时间、辅助信息和主操作
4. 不顺手重写页面筛选、表格、图表、编辑器和接口逻辑

## 9. 样例接入建议

本阶段建议只做 2 到 3 个代表页：

- 1 个 dashboard 页
- 1 个 list 页
- 1 个 workspace 或 detail/result 页

推荐优先顺序：

1. 已存在本地 `.page-header` 的列表页或详情页
2. 已纳入统一 Layout、但仍缺少页面级动作和辅助信息的 dashboard 页
3. 复杂 workspace 页仅做头部接入，不重写主体布局

## 10. 当前阶段不做

- 不新增 `PageHeader` / `ModuleHeader` / `SectionHeader` 平行体系
- 不把最近访问做成真实功能
- 不把全局搜索做成真实功能
- 不对 Home 做 1.2 工作台内容重构
- 不全站一次性替换所有旧页面
- 不改业务接口和业务数据结构

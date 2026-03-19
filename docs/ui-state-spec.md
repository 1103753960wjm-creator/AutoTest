# 统一状态组件和状态规范

## 1. 目标

本文档用于冻结 TestHub 前端统一状态体系的可执行规范，作为后续 videcoding 的页面状态真源。

本轮 0.7b 目标：

- 补强统一状态定义、边界和判断顺序
- 冻结统一状态判断口径
- 补齐状态组件的通用动作能力
- 在少量样例页面和一个复杂工作台局部区域验证可复用性

本轮不做：

- 全站替换旧页面
- 修改 `axios` 拦截器和全局请求机制
- 重构业务接口协议
- 重写权限系统

## 2. 统一状态判断口径

### 2.1 结论

当前平台推荐统一使用 `pageState` / `xxxState` 这种枚举式状态口径，不再继续扩散 `isLoading / isError / isEmpty` 的多布尔写法。

统一常量文件：

- `frontend/src/components/ui-states/state-constants.js`

统一枚举：

- `loading`
- `empty`
- `request-error`
- `forbidden`
- `search-empty`
- `ready`

### 2.2 为什么选择枚举式状态

选择 `pageState` 的原因：

- 当前 `ProjectList.vue`、`Dashboard.vue` 已经接近枚举式状态，迁移成本更低。
- 列表页、Dashboard 页、复杂工作台页都存在“整页状态”和“局部状态”并存的情况，用 `pageState` / `sidebarState` / `activityState` 更容易表达。
- 枚举式状态天然互斥，能避免多个布尔字段同时为 `true` 的冲突。
- 后续页面壳、统一头部、埋点或回归脚本更容易识别单一状态值。

推荐命名：

- 整页：`pageState`
- 局部区域：`tableState`、`sidebarState`、`activityState`、`resultState`
- 不再新增 `isLoading + isError + isEmpty + hasLoaded` 的并行布尔组合，除非是极小的局部视觉状态。

## 3. 状态类型定义

### 3.1 `loading`

定义：关键请求尚未返回，当前页面或局部区域还不能可靠渲染业务内容。

适用场景：

- 首次进入页面
- 切换项目、环境、关键主对象时
- 局部区域依赖的新请求尚未返回时

不适用：

- 表格局部按钮提交中
- 非关键次级数据的轻量刷新

默认文案：

- 标题：`正在加载内容`
- 描述：`请稍候，平台正在准备页面数据。`

推荐动作：

- 默认无动作
- 如需动作，优先通过 `actions` 插槽自定义，不默认塞按钮

### 3.2 `empty`

定义：请求成功，但当前上下文下没有任何可展示业务数据。

适用场景：

- 项目下尚无资产
- 列表首次打开时库里为空
- 局部区块有明确“尚未创建”的业务含义

不适用：

- 搜索后无结果
- 请求失败
- 无权限

默认文案：

- 标题：`暂无内容`
- 描述：`当前还没有可展示的数据。`

推荐动作：

- `create`
- `goConfig`
- 自定义引导动作

### 3.3 `search-empty`

定义：带搜索词、筛选条件或限定上下文后的查询结果为空。

适用场景：

- 关键词搜索结果为空
- 列表筛选后无记录
- 工作台局部搜索区无匹配项

与 `empty` 的边界：

- 没有筛选条件且库为空：`empty`
- 有筛选条件且结果为空：`search-empty`

默认文案：

- 标题：`未找到匹配结果`
- 描述：`可以调整筛选条件或清空搜索后再试一次。`

推荐动作：

- `clearFilters`
- `resetSearch`

### 3.4 `request-error`

定义：请求失败，且失败原因不属于权限拒绝。

适用场景：

- 网络异常
- 5xx
- 非 403 的接口错误
- 页面依赖的关键请求失败且没有可展示兜底内容

与 `forbidden` 的边界：

- 403 / 显式无权限：`forbidden`
- 其他失败：`request-error`

默认文案：

- 标题：`请求失败`
- 描述：`数据加载失败，请稍后重试。`

推荐动作：

- `retry`
- 视场景追加 `resetSearch`

### 3.5 `forbidden`

定义：当前用户无法访问页面或局部资源。

适用场景：

- 403
- 角色/权限拒绝
- 已知资源存在但当前用户无权查看

不适用：

- 网络错误
- 服务异常
- 空数据

默认文案：

- 标题：`暂无访问权限`
- 描述：`当前账号没有访问此页面的权限，请联系管理员处理。`

推荐动作：

- `goHome`
- `back`

### 3.6 `ready`

定义：当前区域已具备正常展示条件。

说明：

- `ready` 不是状态组件，不直接渲染状态页。
- 进入 `ready` 后展示页面主内容。

## 4. 整页状态与局部状态

### 4.1 整页状态

适用于以下场景：

- 页面主请求尚未返回
- 页面主对象不存在且当前页无法继续展示
- 页面主入口直接被权限拒绝

推荐页面：

- Dashboard
- 列表页
- 详情页
- 配置页

推荐变量名：`pageState`

### 4.2 局部状态

适用于以下场景：

- 页面整体可用，但局部卡片、局部侧栏、局部结果区需要独立请求
- 工作台左右布局中，某个区域独立失败或空数据
- 局部搜索区和主内容区并行存在

推荐变量名：`sidebarState`、`activityState`、`resultState`

规则：

- 局部状态不得反向覆盖整页状态
- 单个局部失败时，优先保持其他区域可用
- 局部状态只包裹本区域，不扩大到整页

## 5. 推荐判断顺序

推荐统一判断顺序：

1. `loading`
2. `forbidden`
3. `request-error`
4. `search-empty`
5. `empty`
6. `ready`

推荐原因：

- `loading` 优先，避免把未返回数据误判成空态。
- `forbidden` 优先于普通错误，避免把权限问题展示成“加载失败”。
- `search-empty` 只在存在筛选条件时生效。
- `empty` 只在“确实没有数据且不带筛选条件”时出现。

列表页推荐伪代码：

```js
if (isLoading && !hasLoaded) return UI_PAGE_STATE.LOADING
if (requestState === UI_PAGE_STATE.FORBIDDEN && !rows.length) return UI_PAGE_STATE.FORBIDDEN
if (requestState === UI_PAGE_STATE.REQUEST_ERROR && !rows.length) return UI_PAGE_STATE.REQUEST_ERROR
if (!rows.length && hasActiveFilter) return UI_PAGE_STATE.SEARCH_EMPTY
if (!rows.length) return UI_PAGE_STATE.EMPTY
return UI_PAGE_STATE.READY
```

## 6. 状态组件清单

统一组件目录：

- `frontend/src/components/ui-states/StateBlock.vue`
- `frontend/src/components/ui-states/StateLoading.vue`
- `frontend/src/components/ui-states/StateEmpty.vue`
- `frontend/src/components/ui-states/StateError.vue`
- `frontend/src/components/ui-states/StateForbidden.vue`
- `frontend/src/components/ui-states/StateSearchEmpty.vue`
- `frontend/src/components/ui-states/state-constants.js`
- `frontend/src/components/ui-states/index.js`

组件职责：

| 组件 | 职责 | 推荐场景 |
| --- | --- | --- |
| `StateBlock` | 底层统一骨架 | 不直接大面积业务使用，供上层状态组件复用 |
| `StateLoading` | 加载态 | 整页首次加载、局部关键区加载 |
| `StateEmpty` | 空态 | 资产为空、未创建内容 |
| `StateError` | 请求错误态 | 普通失败、可重试场景 |
| `StateForbidden` | 权限态 | 403、显式无权限 |
| `StateSearchEmpty` | 搜索空态 | 搜索、筛选、查询无结果 |

## 7. 组件能力规范

### 7.1 `StateBlock`

标准结构：

- 图标区
- 标题区
- 描述区
- 动作区
- 扩展内容区

支持能力：

- `title`
- `description`
- `tone`
- `compact`
- `primaryActionText`
- `secondaryActionText`
- `primaryActionType`
- `secondaryActionType`
- `primaryActionPlain`
- `secondaryActionPlain`

支持插槽：

- `icon`
- `actions`
- 默认插槽

支持事件：

- `primary-action`
- `secondary-action`

### 7.2 上层状态组件

上层状态组件统一支持：

- `title`
- `description`
- `compact`
- `actions` 插槽

动作型组件额外支持：

- `primaryActionText`
- `secondaryActionText`
- `primaryActionType`
- `secondaryActionType`
- `primaryActionPlain`
- `secondaryActionPlain`
- 兼容旧属性：`actionText`
- 兼容旧事件：`action`

兼容约束：

- 旧页面继续传 `actionText` / 监听 `@action` 仍可用
- 新页面统一改用 `primaryActionText`、`secondaryActionText`、`@primary-action`、`@secondary-action`

### 7.3 推荐用法

首选：

```vue
<StateError
  :description="requestErrorMessage"
  @primary-action="reload"
/>
```

多动作：

```vue
<StateForbidden
  :primary-action-text="$t('common.uiState.actions.goHome')"
  :secondary-action-text="$t('common.uiState.actions.back')"
  @primary-action="router.push('/home')"
  @secondary-action="router.back()"
/>
```

自定义动作区：

```vue
<StateEmpty>
  <template #actions>
    <el-button type="primary" @click="handleCreate">创建</el-button>
    <el-button @click="goConfig">前往配置</el-button>
  </template>
</StateEmpty>
```

## 8. 默认文案与推荐动作

| 状态 | 默认标题 | 默认描述 | 推荐动作 |
| --- | --- | --- | --- |
| `loading` | 正在加载内容 | 请稍候，平台正在准备页面数据。 | 默认无动作 |
| `empty` | 暂无内容 | 当前还没有可展示的数据。 | `create` / `goConfig` |
| `search-empty` | 未找到匹配结果 | 可以调整筛选条件或清空搜索后再试一次。 | `clearFilters` / `resetSearch` |
| `request-error` | 请求失败 | 数据加载失败，请稍后重试。 | `retry` |
| `forbidden` | 暂无访问权限 | 当前账号没有访问此页面的权限，请联系管理员处理。 | `goHome` / `back` |

统一文案真源：

- `frontend/src/locales/lang/zh-cn/common.js`
- `frontend/src/locales/lang/en/common.js`

当前命名统一收口在：

- `common.uiState.loading.*`
- `common.uiState.empty.*`
- `common.uiState.searchEmpty.*`
- `common.uiState.error.*`
- `common.uiState.forbidden.*`
- `common.uiState.actions.*`

## 9. 上一轮文案文件的实际修改位置说明

上一轮提到“`common.js` 和 `common.js`”表述不清，这里明确如下：

实际修改文件：

- `frontend/src/locales/lang/zh-cn/common.js`
- `frontend/src/locales/lang/en/common.js`

当前动作文案键包括：

- `retry`
- `reset`
- `clearFilters`
- `resetSearch`
- `create`
- `goConfig`
- `goHome`
- `back`

说明：

- `reset` 是 0.7 旧键，为兼容保留。
- 0.7b 新增 `clearFilters`、`resetSearch`、`create`、`goConfig`、`back`，便于语义更明确的状态动作。
- 目前统一状态文案没有出现第二套 `uiState` 命名空间，不存在“同一套统一状态 key 重复定义”问题。
- 顶层 `common.reset`、`common.back` 等是通用界面词，不属于统一状态命名空间冲突。

## 10. 已接入样例

当前已接入页面：

- `frontend/src/views/Home.vue`
- `frontend/src/views/projects/ProjectList.vue`
- `frontend/src/views/api-testing/Dashboard.vue`

0.7b 新增的复杂工作台试点：

- `frontend/src/views/api-testing/InterfaceManagement.vue`

试点范围：

- 仅接入左侧集合树 / 搜索区域的局部状态
- 验证左右布局、多区域页面、局部错误 / 空态 / 搜索空态 / loading 的可行性
- 不改右侧请求编辑区的业务逻辑

## 11. 后续迁移建议

优先顺序：

1. 列表页先统一 `pageState`
2. Dashboard 页区分整页状态和局部状态
3. 工作台页优先治理左侧树、结果区、报告区这类独立区域
4. 详情 / 报告页再补统一 `DetailResultShell + State*` 组合

迁移原则：

- 先替换状态判断和外层骨架，不先改业务请求逻辑
- 能复用旧 `actionText/@action` 的页面先不强制重写
- 新增页面禁止继续散写 `el-empty + 字符串提示 + 任意按钮` 的临时组合

## 12. 本次范围说明

本次只补强统一状态基座，没有修改：

- `axios` 拦截器逻辑
- 全局请求机制
- 后端接口协议
- 全站页面实现
- 权限系统

# 全局路由 Meta 与导航元信息规范

## 1. 目标

本规范用于统一 TestHub 前端的页面标题、模块归属、面包屑、导航高亮、缓存策略和隐藏规则。  
后续所有新增页面默认都要先定义路由 `meta`，再接入页面和导航。

## 2. 当前问题

在本次治理前：

- `layout` 通过路径前缀推断模块归属；
- 面包屑标题依赖一张手写 `routeMap`；
- 路由本身几乎没有承载页面标题和类型信息；
- 详情页、创建页、编辑页没有统一的隐藏和菜单高亮策略；
- `keepAlive` 没有统一入口，后续页面很容易各自实现。

这会导致：

- 页面标题和模块归属容易失真；
- 路由新增后，必须同步改多处硬编码；
- videcoding 时页面元信息容易继续散落。

## 3. 统一字段定义

`route.meta` 至少支持以下字段：

| 字段 | 类型 | 说明 | 默认值 |
| --- | --- | --- | --- |
| `title` | `string` | 页面标题，作为页面头部标题和面包屑末级标题真源 | `''` |
| `module` | `string` | 一级模块归属 | `''` |
| `pageType` | `string` | 页面类型 | `''` |
| `icon` | `string` | 页面图标标识，当前先统一为字符串 key | `''` |
| `keepAlive` | `boolean` | 是否进入布局层缓存 | `false` |
| `hidden` | `boolean` | 是否为隐藏入口 | `false` |

本次同时约定两个辅助字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `parentTitle` | `string` | 面包屑中间层标题，用于详情页 / 创建页 / 编辑页 |
| `activeMenu` | `string` | 当前页面应高亮的菜单路径，常用于详情页回归所属列表 |

## 4. 模块取值规范

当前统一模块键如下：

| module | 中文名称 | 建议入口 |
| --- | --- | --- |
| `workbench` | 工作台 | `/home` |
| `test-design` | 测试设计 | `/ai-generation/requirement-analysis` |
| `api-automation` | 接口自动化 | `/api-testing/dashboard` |
| `web-automation` | Web 自动化 | `/ui-automation/dashboard` |
| `app-automation` | App 自动化 | `/app-automation/dashboard` |
| `data-factory` | 数据工厂 | `/data-factory` |
| `config-center` | 配置中心 | `/configuration/ai-model` |
| `system-management` | 系统管理 | `/ai-generation/profile` |

## 5. 页面类型取值建议

当前推荐值：

- `dashboard`
- `list`
- `workspace`
- `detail-result`
- `config`
- `auth`

说明：

- `dashboard` 用于概览/看板
- `list` 用于列表/资产管理
- `workspace` 用于工作台/编辑器/复杂操作台
- `detail-result` 用于详情/结果/报告
- `config` 用于配置页
- `auth` 用于登录/注册类认证页

## 6. 使用规则

### 6.1 所有正式页面必须定义

以下页面类型新增时必须定义完整 meta：

- 一级入口页
- 列表页
- 工作台页
- 配置页
- 报告页
- 详情页
- 创建页 / 编辑页

### 6.2 隐藏页规则

以下页面默认 `hidden: true`：

- 详情页
- 新建页
- 编辑页
- 登录 / 注册页
- 仅内部跳转页

### 6.3 菜单高亮规则

详情页、新建页、编辑页默认应配置 `activeMenu`，指回所属列表页。  
例如：

```js
meta: createRouteMeta({
  title: '测试用例详情',
  module: 'test-design',
  pageType: 'detail-result',
  hidden: true,
  parentTitle: '测试用例',
  activeMenu: '/ai-generation/testcases'
})
```

### 6.4 面包屑规则

布局层统一按以下顺序生成：

1. 首页
2. 模块名
3. `parentTitle`（如果有）
4. `title`

### 6.5 页面标题规则

- 顶部页面标题统一来自 `meta.title`
- 浏览器标题统一格式：`<title> - TestHub`

### 6.6 keepAlive 规则

默认 `false`。  
仅以下类型建议开启：

- 高成本工作台
- 长编辑页
- 需要保留草稿/上下文的复杂页面

当前已启用的代表页：

- 接口管理
- Web 脚本生成
- App 用例编排
- 数据工厂
- AI 助手

## 7. 当前落地实现

本次新增：

- `frontend/src/router/route-meta.js`

职责：

- 提供 `createRouteMeta`
- 提供模块标签与默认入口
- 提供 `resolveRouteMeta`
- 提供面包屑构建
- 提供浏览器标题生成

本次调整：

- `frontend/src/router/index.js` 为关键页面补齐 meta
- `frontend/src/layout/index.vue` 改为消费路由 meta，渲染：
  - 面包屑
  - 当前页面标题
  - 当前模块归属
  - 页面类型标签
  - `keepAlive`
  - `activeMenu`

## 8. 后续开发要求

1. 新增页面先写 `meta`，再写页面。
2. 不再在 `layout` 里新增路径判断表或标题硬编码表。
3. 不再通过页面内部自行定义“当前属于哪个模块”。
4. 若页面需要从导航中隐藏，必须显式写 `hidden: true`。
5. 若页面是详情/编辑页，默认补 `parentTitle` 和 `activeMenu`。
6. 若页面需要缓存，必须明确写 `keepAlive: true`，不能靠页面自行处理。

## 9. 当前阶段不做

- 不重写现有侧边栏菜单结构
- 不把所有遗留页面一次性补齐 meta
- 不接入权限菜单系统
- 不改业务接口和业务逻辑

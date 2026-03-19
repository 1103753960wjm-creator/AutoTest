# 平台效率能力规范（阶段 1.3）

## 1. 目标

阶段 1.3 交付“最近访问 / 收藏 / 快捷继续”的第一版平台效率能力。

当前目标：

- 最近访问第一版可用
- 收藏第一版可用
- 顶部全局栏中的“最近访问 / 收藏”从占位入口升级为可交互入口
- `Home` 中的“快捷继续”接入真实最近访问数据
- 持久化优先使用前端本地存储
- 代码结构为未来服务端同步保留扩展空间

## 2. 当前边界

- 不重写 Layout
- 不重写 `PlatformPageHeader`
- 不重做 Home 结构
- 不提前实现全局搜索真实能力
- 不提前实现消息中心
- 不实现复杂资产级收藏体系

## 3. 第一版能力范围

### 3.1 最近访问

第一版记录用户最近打开的页面和入口。

字段结构：

```js
{
  id: 'route:/ai-generation/projects/12',
  title: '项目详情',
  route: '/ai-generation/projects/12',
  fullPath: '/ai-generation/projects/12',
  module: 'test-design',
  pageType: 'detail-result',
  visitedAt: '2026-03-18T10:30:00.000Z',
  icon: 'folder',
  summary: '测试设计 / 项目详情',
  source: 'local'
}
```

规则：

- 去重键优先使用 `fullPath`
- 访问同一路径时更新顺序和时间
- 仅记录真实页面访问，不记录登录页等访客页

### 3.2 收藏

第一版只支持页面级 / 入口级收藏。

字段结构：

```js
{
  id: 'favorite:/api-testing/dashboard',
  title: '接口自动化总览',
  route: '/api-testing/dashboard',
  fullPath: '/api-testing/dashboard',
  module: 'api-automation',
  pageType: 'dashboard',
  createdAt: '2026-03-18T10:30:00.000Z',
  icon: 'link',
  summary: '接口自动化 / 概览页',
  source: 'local'
}
```

规则：

- 第一版只支持“当前页收藏 / 取消收藏”
- 不做分组、排序、自定义标题
- 不扩张到业务资产级收藏

### 3.3 快捷继续

第一版仅消费最近访问数据。

规则：

- `Home` 的“快捷继续”优先展示最近访问
- 不混入收藏数据
- 以后如果要展示收藏，应单独做区块，不混入“快捷继续”

## 4. 访问事件触发点

访问记录统一在 `router.afterEach` 中记录。

原因：

- 这是全平台统一成功导航后的稳定入口
- 不会把记录逻辑散落到页面
- 比页面 `onMounted` 更不容易遗漏和重复
- 更适合未来升级为平台级服务端同步

## 5. 持久化边界

第一版持久化方案：

- 使用 `localStorage`
- 统一由效率能力 store 管理

结构边界：

- 页面不直接写 `localStorage`
- 由 store 内部封装读写与裁剪策略
- 后续可在 store 中替换为“本地 + 服务端同步”

## 6. 顶栏接入策略

最近访问与收藏入口第一版使用轻量面板。

原因：

- 保持平台工具入口的轻量特征
- 不扩张成完整个人效率中心
- 适合展示少量最近项、收藏项和空态

## 7. Home 接入策略

- Home 不重做结构
- “快捷继续”直接接入最近访问真实数据
- 收藏不混入“快捷继续”
- 如后续需要展示收藏，建议单独以小区块承接

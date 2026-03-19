# 深链接与回跳规则

更新时间：2026-03-19

## 1. 目标

阶段 1 的第一版深链接与回跳只解决两件事：

- 让高价值对象页可以被最近访问、全局搜索、Home 快捷继续和列表入口稳定打开
- 让试点对象页在打开后可以按统一规则回到来源入口

本轮不做复杂历史栈、标签导航和全局返回管理系统。

## 2. 第一轮支持对象

当前只支持已有稳定详情路由的 4 类对象：

1. 测试设计项目详情：`/ai-generation/projects/:id`
2. 测试用例详情：`/ai-generation/testcases/:id`
3. 测试用例编辑：`/ai-generation/testcases/:id/edit`
4. 执行详情：`/ai-generation/executions/:id`

## 3. params / query 规则

### 3.1 params 规则

- `params` 只用于表达对象身份
- 例如：`/ai-generation/projects/:id`
- 不把来源、回跳、页签状态写进 `params`

### 3.2 query 规则

- `query` 只承接两类信息：
- 子视图状态
- 来源上下文

当前第一版来源上下文字段：

- `from`
- `fromPath`
- `fromTitle`
- `fromModule`

当前第一版子视图字段：

- `tab`

### 3.3 `tab` 规则

- 只在已经存在稳定页签结构的页面上使用
- 第一轮只在项目详情页支持：`tab=info|members|environments`
- 不为了深链接临时创造新页签体系

## 4. 来源上下文设计

### 4.1 `from`

第一版允许的来源类型：

- `list`
- `home`
- `search`
- `recent`
- `favorite`
- `dashboard`
- `detail`

说明：

- `detail` 仅用于试点页内的详情 -> 编辑跳转
- 其他页面暂不扩展更多来源类型

### 4.2 `fromPath`

- 记录来源页的站内相对路径
- 只允许站内相对路径
- 不允许外链、协议头或异常值

### 4.3 `fromTitle`

- 记录来源页展示名
- 用于页面头部的“返回来源”文案

### 4.4 `fromModule`

- 记录来源模块 key
- 第一版主要用于扩展位和兜底信息，不单独驱动回跳

## 5. 回跳规则

对象页回跳顺序固定为：

1. 有合法 `fromPath`，返回 `fromPath`
2. 没有合法来源，返回该对象所属列表页
3. 列表页也拿不到时，最后再 `router.back()`

说明：

- 当前不维护复杂的全局历史栈
- 当前“返回来源”入口统一挂在 `PlatformPageHeader` 的页面级动作区

## 6. 与最近访问 / 搜索 / Home 的关系

- 最近访问、搜索、Home 快捷继续仍保持各自独立能力
- 它们不共享状态真源，只共享同一套深链接规则
- 从搜索结果打开页面后，最终仍走统一路由链，因此会自然进入最近访问

## 7. 当前不支持的对象类型

以下对象本轮明确暂缓：

- 只有弹窗详情、没有稳定详情路由的对象
- API / Web / App 模块中尚未稳定的对象级详情页
- 复杂工作台页面内的局部子对象深链接
- 阶段 2 的自动化草稿中心、执行结果回链等更复杂闭环

## 8. 试点页落地要求

第一轮只在以下页面落地统一回跳动作，并顺手收掉页面内部旧头部：

- `ProjectDetail.vue`
- `TestCaseDetail.vue`
- `TestCaseEdit.vue`
- `ExecutionDetailView.vue`

此举属于页面头部规范在试点页上的补齐，不扩散到全站。

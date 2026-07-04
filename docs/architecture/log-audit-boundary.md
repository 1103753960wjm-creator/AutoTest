# 日志与审计入口归属规则

## 1. 目标

本文档用于冻结 TestHub 当前“日志与审计入口”的归属规则，避免后续继续把治理日志、执行结果日志和业务历史记录混着长。

本次只做两件事：

- 盘清当前已有日志相关页面、接口和预留能力
- 冻结后续新增日志页应归到哪里

本次不做：

- 重构现有日志模型
- 重写日志系统
- 建立统一日志中心页面
- 改造权限系统或审计系统

## 2. 分类结论

### 2.1 登录日志

归属：`系统管理`

定义：记录用户认证行为的治理日志，包括登录成功、登录失败、退出登录、token 刷新失败、会话失效等。

边界：

- 登录页、注册页是认证入口，不等于登录日志页面。
- `users` app 当前提供登录/退出接口，但未发现独立登录日志模型或前端治理页。
- 后续若新增登录行为追踪页，应固定进入系统管理，不进入业务模块。

### 2.2 操作日志

归属：`系统管理`

定义：记录“谁在什么时候对什么资源做了什么变更”的治理日志。

边界：

- API 自动化 `OperationLog`
- Web 自动化 `OperationRecord`
- Dashboard 中的“最近活动/操作记录”只是业务域摘要，不应继续扩张为正式治理入口。
- 后续统一操作日志页应归系统管理，业务 Dashboard 可保留摘要卡片，但不再承接完整日志中心职责。

### 2.3 执行日志

归属：`执行中心 / 结果页`

定义：记录一次测试执行、任务执行、请求调用或执行结果链路中的过程、输出和状态。

包含：

- 接口请求历史 `RequestHistory`
- 接口任务执行日志 `TaskExecutionLog`
- Web 执行记录、测试报告中的执行日志
- AI 智能模式执行记录 `AIExecutionRecord`
- App 执行记录
- 各域定时任务下的执行日志对话框或结果详情

边界：

- 执行日志属于业务执行结果，不属于系统治理。
- 通知日志和执行记录默认一起看待，优先向执行中心收敛。
- 不应因为页面里有“日志”两个字就归到系统管理。

### 2.4 AI 调用日志

归属：`系统管理 / AI 治理（预留）`

定义：记录模型调用、提示词使用、调用来源、耗时、成本、失败原因、调用人等治理信息。

当前现状：

- 发现 AI 执行记录页，但它记录的是测试执行结果，不是平台级 AI 调用审计。
- 发现零散 `logger.info/error` 输出和 AI 配置页，但未发现统一的 AI 调用日志模型或治理页。

规则：

- 后续若新增 AI 调用审计、Token 消耗、模型调用失败分析页面，应固定归系统管理或后续 AI 治理分组。
- 不进入配置中心，不挂到业务模块二级菜单里。

### 2.5 审计类日志

归属：`系统管理`

定义：服务平台治理、追责、合规和变更留痕的日志。

包含：

- 登录日志
- 操作日志
- 权限变更日志
- 平台参数变更日志
- AI 调用审计
- 后续角色 / 权限 /用户治理相关审计

边界：

- 审计日志不是执行结果页。
- 审计日志也不是通知发送结果页。

## 3. 当前现状盘点

### 3.1 已存在的前端页面或页面内入口

| 类型 | 当前入口 | 前端位置 | 后端位置 | 当前状态 | 建议归属 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| 认证入口 | `/login` | `frontend/src/views/auth/Login.vue` | `apps/users/login/` | 已存在 | 系统管理 | 这是认证入口，不是登录日志页。 |
| 认证入口 | `/register` | `frontend/src/views/auth/Register.vue` | `apps/users/register/` | 已存在 | 系统管理 | 这是认证入口，不是登录日志页。 |
| 操作日志摘要 | `/api-testing/dashboard` 最近活动 | `frontend/src/views/api-testing/Dashboard.vue` | `apps/api_testing/operation-logs/` | 已存在摘要 | 系统管理（后续完整页） | 当前只适合作为业务看板摘要，不继续增长为日志中心。 |
| 操作日志摘要 | `/ui-automation/dashboard` 最近活动 | `frontend/src/views/ui-automation/dashboard/Dashboard.vue` | `apps/ui_automation/operation-records/` | 已存在摘要 | 系统管理（后续完整页） | 与上同。 |
| 执行结果日志 | `/api-testing/history` | `frontend/src/views/api-testing/RequestHistory.vue` | `apps/api_testing/histories/` | 已存在 | 执行中心（后续） | 这是接口请求与执行历史，不是治理日志。 |
| 执行结果日志 | `/api-testing/scheduled-tasks` 内执行日志对话框 | `frontend/src/views/api-testing/ScheduledTasks.vue` | `apps/api_testing/task-execution-logs/` | 已存在局部入口 | 执行中心（后续） | 属于任务执行结果。 |
| 通知结果日志 | `/api-testing/notification-logs` | `frontend/src/views/notification/NotificationLogs.vue` | `apps/api_testing/notification-logs/` | 已存在 | 执行中心（后续） | 是通知发送结果，不是系统审计。 |
| 执行结果日志 | `/ui-automation/executions` | `frontend/src/views/ui-automation/executions/ExecutionList.vue` | `apps/ui_automation/test-executions/` | 已存在 | 执行中心（后续） | Web 自动化执行结果。 |
| 通知结果日志 | `/ui-automation/notification-logs` | `frontend/src/views/ui-automation/notification/NotificationLogs.vue` | `apps/ui_automation/notification-logs/` | 已存在 | 执行中心（后续） | Web 业务域通知结果。 |
| 执行结果日志 | `/ai-intelligent-mode/execution-records` | `frontend/src/views/ui-automation/ai/AIExecutionRecords.vue` | `apps/ui_automation/ai-execution-records/` | 已存在 | 执行中心（后续） | 这是 AI 测试执行记录，不是 AI 调用审计。 |
| 执行结果日志 | `/app-automation/executions` | `frontend/src/views/app-automation/executions/ExecutionList.vue` | `apps/app_automation/executions/` | 已存在 | 执行中心（后续） | App 执行结果。 |
| 通知结果日志 | `/app-automation/notification-logs` | `frontend/src/views/app-automation/notification/NotificationLogs.vue` | `apps/app_automation/notification-logs/` | 已存在 | 执行中心（后续） | App 业务域通知结果。 |
| 工具使用历史 | `数据工厂历史` 弹窗 | `frontend/src/views/data-factory/DataFactory.vue` | `apps/data_factory` | 已存在 | 不纳入本次五类 | 这是工具使用历史，不是平台治理日志。 |
| 会话历史 | `AI 助手历史会话` | `frontend/src/views/assistant/AssistantView.vue` | `apps/assistant` | 已存在 | 不纳入本次五类 | 这是产品会话记录，不是 AI 调用审计。 |

### 3.2 后端已存在、但前端尚未形成正式治理入口的能力

| 能力 | 后端位置 | 当前状态 | 建议归属 | 说明 |
| --- | --- | --- | --- | --- |
| API 操作日志 | `apps/api_testing/operation-logs/` | 后端已提供，前端仅在 Dashboard 摘要显示 | 系统管理 | 后续统一进入操作日志页。 |
| UI 操作记录 | `apps/ui_automation/operation-records/` | 后端已提供，前端仅在 Dashboard 摘要显示 | 系统管理 | 后续统一进入操作日志页。 |
| 登录日志 | `apps/users` | 未发现独立模型或前端页面 | 系统管理（预留） | 先冻结归属，不在本次补实现。 |
| AI 调用日志 | 分散在 AI 模块和 logger 输出 | 未形成统一能力 | 系统管理 / AI 治理（预留） | 后续统一承接模型调用审计。 |
| 审计日志 | 当前未发现统一前后端模块 | 能力缺失 | 系统管理（预留） | 后续由系统治理能力建设承接。 |

## 4. 最容易混淆的入口

### 4.1 Dashboard 最近活动

结论：属于“操作日志摘要”，不是正式日志中心。

规则：

- 允许保留在业务 Dashboard 作为摘要卡片
- 不再在 Dashboard 里继续堆完整筛选、导出、审计能力
- 完整入口后续统一进入系统管理

### 4.2 通知日志

结论：属于执行结果日志，不属于系统审计。

规则：

- API / Web / App 三套通知日志短期继续留在业务模块
- 后续统一迁入执行中心
- 不进入系统管理

### 4.3 请求历史 / 执行记录 / 任务执行日志

结论：都属于执行结果链路。

规则：

- `RequestHistory` 属于接口执行历史
- `TaskExecutionLog` 属于任务执行过程日志
- `ExecutionRecord` / `AIExecutionRecord` 属于自动化运行结果
- 这些都应归执行中心或结果页体系，不归系统管理

### 4.4 AI 执行记录 vs AI 调用日志

结论：这是两类东西，必须严格拆开。

规则：

- `AIExecutionRecord` 记录的是 AI 测试执行过程和结果，归执行中心
- AI 调用日志记录的是模型治理信息，归系统管理 / AI 治理

### 4.5 数据工厂历史和 AI 助手历史

结论：它们是业务功能历史，不属于本次五类治理日志。

## 5. 冻结后的归属规则

### 5.1 系统管理固定承接

以下类型后续新增页面时，固定进入系统管理：

- 登录日志
- 操作日志
- 审计日志
- AI 调用日志 / AI 调用审计
- 权限、用户、角色相关治理日志

推荐未来入口名：

- 登录日志
- 操作日志
- 审计日志
- AI 调用审计

### 5.2 执行中心固定承接

以下类型后续新增页面时，优先进入执行中心或结果页体系：

- 请求历史
- 任务执行日志
- 各业务模块执行记录
- 各业务模块测试报告
- 各业务模块通知日志

推荐未来入口名：

- 执行记录
- 执行日志
- 报告中心
- 通知日志

### 5.3 明确不进入配置中心

以下内容不应挂入配置中心：

- 登录日志
- 操作日志
- 审计日志
- AI 调用日志
- 执行记录
- 执行日志
- 通知日志

配置中心只承接“如何配置能力”，不承接“能力运行后的日志结果”。

## 6. 当前实现建议

### 6.1 保持不动

本次保持现状，不改页面和接口：

- `/api-testing/history`
- `/api-testing/notification-logs`
- `/ui-automation/executions`
- `/ui-automation/notification-logs`
- `/ai-intelligent-mode/execution-records`
- `/app-automation/executions`
- `/app-automation/notification-logs`
- Dashboard 最近活动摘要

### 6.2 轻量导航归类调整

本次只建议在导航真源中补预留，不改真实路由：

- 系统管理预留：登录日志、操作日志、审计日志、AI 调用审计
- 执行中心继续承接执行记录、报告、通知日志

### 6.3 后续迁移顺序建议

1. 先做系统管理下的统一操作日志页
2. 再补登录日志和审计日志预留能力
3. 执行中心建设时，统一吸收各域通知日志和执行记录
4. AI 治理建设时，再把 AI 调用日志独立出来

## 7. 本次范围说明

本次只冻结规则和入口归属，没有修改：

- 日志模型
- 日志采集方式
- 权限系统
- 业务接口
- 现有业务页面结构

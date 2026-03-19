# 配置中心与系统管理边界梳理

## 1. 任务目标

本文件用于冻结 TestHub 当前“配置中心”和“系统管理”的职责边界，作为后续导航收敛、首页改造和页面迁移的统一依据。

本次结论遵循两个原则：

- 先尊重当前项目真实现状，不把尚未建设完成的能力强行归入现有导航。
- 只处理边界与归类，不重构业务逻辑、不重做权限系统。

## 2. 边界定义

### 2.1 配置中心

配置中心承载“让测试能力可以被配置、被运行、被复用”的平台级业务配置，默认面向测试人员、测试负责人或模块管理员开放。

应归入配置中心的内容：

- 环境配置
- AI 模型与提示词配置
- 生成策略与运行策略
- 通知通道配置
- 项目无关、但服务于测试执行的业务配置

不归入配置中心的内容：

- 用户、角色、权限
- 登录日志、操作审计、AI 调用审计
- 平台级安全策略和治理策略

### 2.2 系统管理

系统管理承载“谁可以用平台、如何被治理、平台行为如何被审计”的平台治理能力，默认面向管理员或运维治理角色开放。

应归入系统管理的内容：

- 登录、注册、账号资料
- 用户管理
- 角色与权限
- 登录日志、操作日志、AI 调用审计
- 平台参数、审计与治理配置

不归入系统管理的内容：

- 具体测试域的环境管理
- 具体测试任务的执行配置
- 直接服务于业务测试生成或执行的运行配置

## 3. 当前现状结论

当前仓库中，“配置中心”已经有明确前端页面集合；“系统管理”还没有形成完整前端模块，现状主要是认证入口、个人资料入口，以及后端已存在的用户接口和 Django Admin。

因此本次冻结的核心结论是：

- 配置中心是一个已经存在、应继续收敛的平台级业务配置模块。
- 系统管理是一个边界要先冻结、能力后续再逐步补齐的平台治理模块。
- 通知日志、定时任务、执行记录这类页面，当前不应硬塞进配置中心或系统管理，仍保持在业务域，后续向执行中心或审计中心收敛。

## 4. 当前页面清单与归类建议

### 4.1 已有前端页面

| 当前页面 | 路由 | 前端文件 | 后端 app / 接口来源 | 建议归类 | 处理建议 | 说明 |
| --- | --- | --- | --- | --- | --- | --- |
| AI 模型配置 | `/configuration/ai-model` | `frontend/src/views/requirement-analysis/AIModelConfig.vue` | `apps/requirement_analysis` / `ai-models` | 配置中心 | 保持不动 | 平台级 AI 生成配置，服务测试设计链路，不属于治理能力。 |
| 提示词配置 | `/configuration/prompt-config` | `frontend/src/views/requirement-analysis/PromptConfig.vue` | `apps/requirement_analysis` / `prompts` | 配置中心 | 保持不动 | 属于 AI 生成策略配置。 |
| 生成配置 | `/configuration/generation-config` | `frontend/src/views/requirement-analysis/GenerationConfigView.vue` | `apps/requirement_analysis` / `generation-config` | 配置中心 | 保持不动 | 属于用例生成行为配置。 |
| UI 环境配置 | `/configuration/ui-env` | `frontend/src/views/configuration/UIEnvironmentConfig.vue` | `apps/ui_automation` / `config/environment` | 配置中心 | 保持不动 | 属于平台级 Web/UI 执行环境配置。 |
| App 环境配置 | `/configuration/app-env` | `frontend/src/views/app-automation/settings/AppSettings.vue` | `apps/app_automation` / `config` | 配置中心 | 保持不动 | 虽然页面源于 App 自动化模块，但内容是运行环境配置，应归配置中心。 |
| AI 智能模式配置 | `/configuration/ai-mode` | `frontend/src/views/configuration/AIIntelligentModeConfig.vue` | `apps/ui_automation` / `ai-models` | 配置中心 | 保持不动 | 属于 AI 智能执行模式的业务配置。 |
| 通知通道配置 | `/configuration/scheduled-task` | `frontend/src/views/ui-automation/notification/NotificationConfigs.vue` | `apps/core` / `notification-configs` | 配置中心 | 轻量迁移 | 页面职责是统一通知通道配置，不是“定时任务配置”；保留现路由，统一文案为“通知通道配置”。 |
| Dify 配置 | `/configuration/dify` | `frontend/src/views/configuration/DifyConfig.vue` | `apps/assistant` / `config/dify` | 配置中心 | 保持不动 | 是 AI 助手接入配置，属于业务能力配置，不属于系统治理。 |
| API AI 服务配置 | `/api-testing/ai-service-config` | `frontend/src/views/api-testing/AIServiceConfig.vue` | `apps/api_testing` / `ai-service-configs` | 配置中心 | 轻量迁移 | 当前页面挂在接口自动化路径下，但本质是平台级 AI 服务配置；短期保持路由不动，导航归属按配置中心处理。 |
| 接口环境管理 | `/api-testing/environments` | `frontend/src/views/api-testing/EnvironmentManagement.vue` | `apps/api_testing` / `environments` | 业务域配置 | 保持不动 | 是接口自动化域内环境资产管理，不升格为配置中心。 |
| 个人资料 | `/ai-generation/profile` | `frontend/src/views/profile/UserProfile.vue` | `apps/users` / `profile` | 系统管理 | 轻量迁移 | 当前入口挂在 AI 用例生成路径下，仅保留为隐藏入口；后续迁入系统管理正式分组。 |
| 登录 | `/login` | `frontend/src/views/auth/Login.vue` | `apps/users` / `login` | 系统管理 | 保持不动 | 属于认证入口，不进入登录后一级导航。 |
| 注册 | `/register` | `frontend/src/views/auth/Register.vue` | `apps/users` / `register` | 系统管理 | 保持不动 | 属于认证入口，不进入登录后一级导航。 |
| API 通知日志 | `/api-testing/notification-logs` | `frontend/src/views/notification/NotificationLogs.vue` | `apps/api_testing` / `notification-logs` | 不纳入本次两类边界 | 后续迁移 | 这是执行结果类日志，不是配置页，也不是典型系统治理页。 |
| Web 通知日志 | `/ui-automation/notification-logs` | `frontend/src/views/ui-automation/notification/NotificationLogs.vue` | `apps/ui_automation` / `notification-logs` | 不纳入本次两类边界 | 后续迁移 | 后续与执行中心或统一日志中心合并考虑。 |
| App 通知日志 | `/app-automation/notification-logs` | `frontend/src/views/app-automation/notification/NotificationLogs.vue` | `apps/app_automation` / `notification-logs` | 不纳入本次两类边界 | 后续迁移 | 与执行域更相关，不放入配置中心。 |
| API 定时任务 | `/api-testing/scheduled-tasks` | `frontend/src/views/api-testing/ScheduledTasks.vue` | `apps/api_testing` / `scheduled-tasks` | 不纳入本次两类边界 | 后续迁移 | 属于任务执行编排，不属于配置中心或系统管理。 |
| Web 定时任务 | `/ui-automation/scheduled-tasks` | `frontend/src/views/ui-automation/scheduled-tasks/ScheduledTasks.vue` | `apps/ui_automation` / `scheduled-tasks` | 不纳入本次两类边界 | 后续迁移 | 后续应向执行中心收口。 |
| App 定时任务 | `/app-automation/scheduled-tasks` | `frontend/src/views/app-automation/scheduled-tasks/ScheduledTasks.vue` | `apps/app_automation` / `scheduled-tasks` | 不纳入本次两类边界 | 后续迁移 | 后续应向执行中心收口。 |

### 4.2 后端已存在、但前端尚未形成正式治理入口的能力

| 能力 | 后端位置 | 当前状态 | 建议归类 | 说明 |
| --- | --- | --- | --- | --- |
| 用户列表 / 用户详情 | `apps/users/urls.py` 中 `users/`、`users/<pk>/` | 后端已提供，前端未形成系统管理页 | 系统管理 | 这是当前最明确的待建设系统管理能力。 |
| 统一通知配置 | `apps/core/urls.py` 中 `notification-configs/` | 已被前端配置页复用 | 配置中心 | 已有正确落点，无需再分散到各业务模块。 |
| API 操作日志 | `apps/api_testing/urls.py` 中 `operation-logs/` | 后端已提供，当前主路由未接入页面 | 系统管理（后续） | 更适合纳入审计或系统治理，不应放进配置中心。 |
| UI 操作记录 | `apps/ui_automation` 中 `operation-records` 相关接口 | 后端已提供，当前未形成统一治理入口 | 系统管理（后续） | 后续建议统一为平台审计视图。 |
| 角色 / 权限 | 当前未发现正式前后端模块 | 能力缺失 | 系统管理（预留） | 不在本次范围内，但边界应预留在系统管理。 |
| AI 调用审计 | 当前未发现统一前端治理页 | 能力分散 | 系统管理（预留） | 后续 AI 治理应归系统管理或审计中心。 |

## 5. 边界冻结结果

### 5.1 配置中心固定承接

以下内容后续新增页面时，优先进入配置中心，不再分散挂入业务模块一级菜单：

- AI 模型、提示词、生成策略
- 统一通知通道
- Web / App 运行环境配置
- 平台级 AI 服务与模型接入配置
- AI 助手接入配置

### 5.2 系统管理固定承接

以下内容后续新增页面时，固定归入系统管理，不再借道测试设计或业务模块：

- 个人资料
- 用户管理
- 角色与权限
- 登录日志
- 操作日志
- AI 调用审计
- 平台治理参数

### 5.3 明确不归入这两个模块的内容

以下内容本次明确不纳入配置中心或系统管理：

- 业务模块自己的环境资产页，如接口环境管理
- 各域定时任务
- 各域通知日志
- 执行记录、测试报告、任务结果页

这些页面后续优先向“执行中心”或统一结果中心收敛，而不是进入配置中心或系统管理。

## 6. 迁移建议

### 6.1 保持不动

- `/configuration/ai-model`
- `/configuration/prompt-config`
- `/configuration/generation-config`
- `/configuration/ui-env`
- `/configuration/app-env`
- `/configuration/ai-mode`
- `/configuration/dify`
- `/login`
- `/register`
- `/api-testing/environments`

### 6.2 轻量迁移

- `/configuration/scheduled-task`
  - 保留现有路由和页面实现。
  - 统一页面与菜单语义为“通知通道配置”。
  - 后续如重构路由，再考虑改名为更清晰的配置路径。
- `/api-testing/ai-service-config`
  - 页面继续保留在当前路由。
  - 导航归属和文档归属统一视为“配置中心”。
  - 后续如做导航收敛，可补一个配置中心正式入口。
- `/ai-generation/profile`
  - 继续保留隐藏入口，避免打断用户当前访问路径。
  - 后续在系统管理一级导航正式落地后再迁移可见入口。

### 6.3 后续迁移

- `/api-testing/notification-logs`
- `/ui-automation/notification-logs`
- `/app-automation/notification-logs`
- `/api-testing/scheduled-tasks`
- `/ui-automation/scheduled-tasks`
- `/app-automation/scheduled-tasks`
- `apps/api_testing` 的操作日志接口
- `apps/ui_automation` 的操作记录接口

这些内容后续不要继续在配置中心扩张，也不要为了补齐“系统管理”而硬塞到系统管理；应等执行中心或统一审计模块成型后再迁移。

## 7. 对后续开发的约束

- 新增配置页时，先判断它是否服务“测试能力配置”，如果是，优先进入配置中心。
- 新增治理页时，先判断它是否服务“用户、权限、审计、平台治理”，如果是，固定进入系统管理。
- 不再新增新的平台配置页到 `/api-testing`、`/ui-automation`、`/app-automation` 一级业务导航下。
- 不再新增新的系统页到 `/ai-generation` 路径下。
- 若页面既有业务域归属，又带平台级配置属性，优先通过 `route meta` 和导航真源先归类，必要时再做后续路由迁移。

## 8. 本次落地范围

本次只完成以下内容：

- 输出边界梳理文档
- 固化配置中心与系统管理的归类原则
- 轻量修正一处误导性导航文案

本次不包含以下内容：

- 权限系统重构
- 用户、角色、权限页面建设
- 日志中心或执行中心建设
- 业务接口改造

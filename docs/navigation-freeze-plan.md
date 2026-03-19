# 一级导航冻结与模块边界方案

## 1. 任务理解

- 当前平台的正式入口来源于 `frontend/src/router/index.js`、`frontend/src/layout/index.vue` 和 `frontend/src/views/Home.vue`。
- 当前一级入口存在历史扩张问题：`AI 用例生成`、`AI 助手`、`AI 智能模式`、`配置中心` 等入口并列存在，但边界并不清晰。
- 本次任务目标不是做大规模路由重构，而是先冻结平台一级导航和模块边界，给后续首页、侧边栏和路由收敛提供唯一真相。

## 2. 边界判断

1. 本次冻结的是“产品导航信息架构”，不是立即改写当前路由前缀。
2. 当前正式可访问路由仍以 `frontend/src/router/index.js` 为准；冻结方案规定的是后续新增页面应归属到哪个模块。
3. `云真机`、`执行中心`、`系统管理` 可以先预留，不要求本次立即补齐实际页面。
4. `AI 助手`、`AI 智能模式` 不再继续作为独立一级导航扩张：
   - `AI 助手` 归入 `工作台` 的工具入口；
   - `AI 智能模式` 归入 `Web 自动化` 的 AI 子域。
5. 平台级配置优先进入 `配置中心`，平台级执行、报告、调度、通知日志优先向 `执行中心` 收敛。
6. 本次不删除旧页面，不调整业务接口，不批量迁移目录。

## 3. 一级导航建议清单

| 一级导航 | 状态 | 暂用当前路径 | 边界定义 | 备注 |
| --- | --- | --- | --- | --- |
| 工作台 | 保留 | `/home` | 平台总览、快捷入口、轻工具入口 | 不承载业务资产管理 |
| 测试设计 | 保留 | 暂承接 `/ai-generation/*` 中的设计域页面 | 需求分析、项目、用例、评审、版本、套件等设计资产 | 当前只是导航归类，不立即改路由前缀 |
| 接口自动化 | 保留 | `/api-testing/*` | 接口项目、接口调试、接口自动化执行工作台 | 配置和执行聚合能力后续收敛 |
| Web 自动化 | 保留 | `/ui-automation/*` + `/ai-intelligent-mode/*` | Web UI 自动化资产与 AI Web 测试能力 | `AI 智能模式` 不再单独做一级导航 |
| App 自动化 | 保留 | `/app-automation/*` | App 自动化资产、编排与运行能力 | 设备域后续可向云真机演进 |
| 云真机 | 预留 | 暂无 | 设备池、预约、远控、设备资源运营 | 本次只冻结名称和职责 |
| 执行中心 | 预留 | 暂无 | 平台级调度、执行、报告、通知日志 | 后续吸收跨模块执行类页面 |
| 数据工厂 | 保留 | `/data-factory` | 通用测试数据与工具能力 | 维持独立工具中心 |
| 配置中心 | 保留 | `/configuration/*` | 平台级 AI、环境、通知通道、接入配置 | 禁止继续把平台配置散落到业务模块 |
| 系统管理 | 预留 | 暂由 `/ai-generation/profile`、`/admin/`、`/login`、`/register` 承接 | 用户、角色、权限、个人资料、系统运维入口 | 当前前端能力不足，先冻结边界 |

## 4. 模块归类方案

### 4.1 工作台

边界定义：只负责平台总览、模块跳转和工具入口，不新增业务管理页。

| 二级页面 | 当前路径 | 处理策略 | 说明 |
| --- | --- | --- | --- |
| 平台首页 | `/home` | 保留入口 | 平台统一门户 |
| AI 助手 | `/ai-generation/assistant` | 隐藏入口 | 保留直达能力，但不再作为独立一级导航增长；后续可作为工作台工具入口呈现 |

### 4.2 测试设计

边界定义：只承载“设计态”资产，不继续承载平台级执行、报告、系统管理页面。

| 二级页面 | 当前路径 | 处理策略 | 说明 |
| --- | --- | --- | --- |
| 需求分析 | `/ai-generation/requirement-analysis` | 保留入口 | 设计域核心入口 |
| AI 生成结果 | `/ai-generation/generated-testcases` | 保留入口 | 生成结果沉淀页 |
| 项目管理 | `/ai-generation/projects` | 保留入口 | 设计资产容器 |
| 项目详情 | `/ai-generation/projects/:id` | 保留入口 | 详情附属页 |
| 测试用例列表 | `/ai-generation/testcases` | 保留入口 | 设计资产 |
| 新建测试用例 | `/ai-generation/testcases/create` | 保留入口 | 编辑附属页 |
| 测试用例详情 | `/ai-generation/testcases/:id` | 保留入口 | 详情附属页 |
| 编辑测试用例 | `/ai-generation/testcases/:id/edit` | 保留入口 | 编辑附属页 |
| 版本管理 | `/ai-generation/versions` | 保留入口 | 设计资产 |
| 评审列表 | `/ai-generation/reviews` | 保留入口 | 设计资产 |
| 新建评审 | `/ai-generation/reviews/create` | 保留入口 | 编辑附属页 |
| 评审详情 | `/ai-generation/reviews/:id` | 保留入口 | 详情附属页 |
| 编辑评审 | `/ai-generation/reviews/:id/edit` | 保留入口 | 编辑附属页 |
| 评审模板 | `/ai-generation/review-templates` | 保留入口 | 设计资产 |
| 测试套件 | `/ai-generation/testsuites` | 隐藏入口 | 当前仍是占位页，不作为冻结后重点曝光入口 |
| 分析任务详情 | `/ai-generation/task-detail/:taskId` | 隐藏入口 | 明细页，只保留内部跳转 |
| 测试计划 / 执行列表 | `/ai-generation/executions` | 未来迁移入口 | 后续迁移到 `执行中心` |
| 测试执行详情 | `/ai-generation/executions/:id` | 未来迁移入口 | 后续迁移到 `执行中心` |
| AI 测试报告 | `/ai-generation/reports` | 未来迁移入口 | 后续迁移到 `执行中心` |
| 个人资料 | `/ai-generation/profile` | 未来迁移入口 | 后续迁移到 `系统管理` |

### 4.3 接口自动化

边界定义：承载接口项目、接口调试与接口自动化执行工作台；平台级配置、报告聚合、通知聚合后续外移。

| 二级页面 | 当前路径 | 处理策略 | 说明 |
| --- | --- | --- | --- |
| 仪表盘 | `/api-testing/dashboard` | 保留入口 | 子系统首页 |
| 项目管理 | `/api-testing/projects` | 保留入口 | 业务资产 |
| 接口管理 | `/api-testing/interfaces` | 保留入口 | 调试与编排工作台 |
| 自动化测试 | `/api-testing/automation` | 保留入口 | 接口自动化执行工作台 |
| 请求历史 | `/api-testing/history` | 保留入口 | 贴近接口调试，不迁入平台执行中心 |
| 环境管理 | `/api-testing/environments` | 保留入口 | 业务环境，暂不视为平台级配置 |
| 测试报告 | `/api-testing/reports` | 未来迁移入口 | 后续进入 `执行中心` |
| 定时任务 | `/api-testing/scheduled-tasks` | 未来迁移入口 | 后续进入 `执行中心` |
| 通知日志 | `/api-testing/notification-logs` | 未来迁移入口 | 后续进入 `执行中心` |
| AI 服务配置 | `/api-testing/ai-service-config` | 未来迁移入口 | 后续进入 `配置中心` |

### 4.4 Web 自动化

边界定义：承载 Web UI 自动化和 AI Web 测试能力；`AI 智能模式` 从产品归类上并入本模块。

| 二级页面 | 当前路径 | 处理策略 | 说明 |
| --- | --- | --- | --- |
| 仪表盘 | `/ui-automation/dashboard` | 保留入口 | 子系统首页 |
| 项目管理 | `/ui-automation/projects` | 保留入口 | 业务资产 |
| 元素管理增强版 | `/ui-automation/elements-enhanced` | 保留入口 | 当前正式入口 |
| 测试用例 | `/ui-automation/test-cases` | 保留入口 | 业务资产 |
| 脚本生成 / 编辑 | `/ui-automation/scripts-enhanced` | 保留入口 | 当前正式入口 |
| 脚本编辑器别名 | `/ui-automation/scripts/editor` | 隐藏入口 | 兼容别名，不作为导航曝光点 |
| 脚本列表 | `/ui-automation/scripts` | 保留入口 | 业务资产 |
| 测试套件 | `/ui-automation/suites` | 保留入口 | 业务资产 |
| AI 智能测试 | `/ai-intelligent-mode/testing` | 保留入口 | 逻辑归属 `Web 自动化`，不再保留独立一级导航 |
| AI 用例列表 | `/ai-intelligent-mode/cases` | 保留入口 | 同上 |
| 执行记录 | `/ui-automation/executions` | 未来迁移入口 | 后续进入 `执行中心` |
| 测试报告 | `/ui-automation/reports` | 未来迁移入口 | 后续进入 `执行中心` |
| 定时任务 | `/ui-automation/scheduled-tasks` | 未来迁移入口 | 后续进入 `执行中心` |
| 通知日志 | `/ui-automation/notification-logs` | 未来迁移入口 | 后续进入 `执行中心` |
| AI 执行记录 | `/ai-intelligent-mode/execution-records` | 未来迁移入口 | 后续进入 `执行中心` |

### 4.5 App 自动化

边界定义：承载 App 自动化资产、用例编排和运行能力；设备资源未来可根据成熟度向云真机拆分。

| 二级页面 | 当前路径 | 处理策略 | 说明 |
| --- | --- | --- | --- |
| 仪表盘 | `/app-automation/dashboard` | 保留入口 | 子系统首页 |
| 项目管理 | `/app-automation/projects` | 保留入口 | 业务资产 |
| 设备管理 | `/app-automation/devices` | 保留入口 | 当前仍归 App 自动化；若设备池升级为跨业务资源，再迁移到 `云真机` |
| 包名管理 | `/app-automation/packages` | 保留入口 | 业务资产 |
| 元素管理 | `/app-automation/elements` | 保留入口 | 业务资产 |
| 用例编排 | `/app-automation/scene-builder` | 保留入口 | 核心设计/编排页 |
| 测试用例 | `/app-automation/test-cases` | 保留入口 | 业务资产 |
| 测试套件 | `/app-automation/test-suites` | 保留入口 | 业务资产 |
| 执行记录 | `/app-automation/executions` | 未来迁移入口 | 后续进入 `执行中心` |
| 测试报告 | `/app-automation/reports` | 未来迁移入口 | 后续进入 `执行中心` |
| 定时任务 | `/app-automation/scheduled-tasks` | 未来迁移入口 | 后续进入 `执行中心` |
| 通知日志 | `/app-automation/notification-logs` | 未来迁移入口 | 后续进入 `执行中心` |

### 4.6 云真机

边界定义：平台级设备资源层，不直接绑定某一个自动化子系统。

| 二级页面 | 当前状态 | 处理策略 | 说明 |
| --- | --- | --- | --- |
| 设备池总览 | 暂无前端页面 | 预留 | 未来用于统一展示设备资源 |
| 设备预约 / 释放 | 暂无前端页面 | 预留 | 未来承接跨项目设备调度 |
| 远程调试 / 远控 | 暂无前端页面 | 预留 | 未来承接真机远程操作 |
| 应用安装 / 镜像管理 | 暂无前端页面 | 预留 | 未来承接设备运营能力 |

### 4.7 执行中心

边界定义：承载平台级任务调度、执行记录、报告、通知日志，不再继续散落在各业务模块。

| 二级页面 | 当前来源 | 处理策略 | 说明 |
| --- | --- | --- | --- |
| 执行总览 | 暂无前端页面 | 预留 | 汇总多子系统执行状态 |
| 调度管理 | API / UI / App 的 `scheduled-tasks` | 预留 | 未来统一调度入口 |
| 执行记录 | AI 设计 / Web / App / AI Web 的执行页 | 预留 | 未来统一记录入口 |
| 报告中心 | AI 设计 / API / Web / App 的报告页 | 预留 | 未来统一报告入口 |
| 通知日志 | API / Web / App 的通知日志页 | 预留 | 未来统一通知日志入口 |

### 4.8 数据工厂

边界定义：承载通用测试数据、转换、编码、生成类工具。

| 二级页面 | 当前路径 | 处理策略 | 说明 |
| --- | --- | --- | --- |
| 数据工厂 | `/data-factory` | 保留入口 | 独立工具中心 |

### 4.9 配置中心

边界定义：只承载平台级配置，不承载项目/业务数据管理。

| 二级页面 | 当前路径 | 处理策略 | 说明 |
| --- | --- | --- | --- |
| AI 模型配置 | `/configuration/ai-model` | 保留入口 | 平台级 AI 配置 |
| 提示词配置 | `/configuration/prompt-config` | 保留入口 | 平台级 AI 配置 |
| 生成配置 | `/configuration/generation-config` | 保留入口 | 平台级 AI 配置 |
| UI 环境配置 | `/configuration/ui-env` | 保留入口 | 平台级环境配置 |
| App 环境配置 | `/configuration/app-env` | 保留入口 | 平台级环境配置 |
| AI 智能模式配置 | `/configuration/ai-mode` | 保留入口 | 平台级 AI 配置 |
| 通知通道配置 | `/configuration/scheduled-task` | 保留入口 | 当前路由名保留，但实际语义是通知通道配置，后续应更名 |
| Dify 配置 | `/configuration/dify` | 保留入口 | 智能助手接入配置 |
| API AI 服务配置 | `/api-testing/ai-service-config` | 未来迁移入口 | 后续并入配置中心，不再留在接口自动化模块 |

### 4.10 系统管理

边界定义：承载用户、角色、权限、个人资料和系统运维入口；认证页不进入登录后一级导航。

| 二级页面 | 当前路径 | 处理策略 | 说明 |
| --- | --- | --- | --- |
| 个人资料 | `/ai-generation/profile` | 未来迁移入口 | 后续迁移到系统管理正式路由 |
| 登录 | `/login` | 隐藏入口 | 系统入口，不出现在登录后导航 |
| 注册 | `/register` | 隐藏入口 | 系统入口，不出现在登录后导航 |
| Django Admin | `/admin/` | 隐藏入口 | 当前实际后台管理入口 |
| 用户 / 角色 / 权限 | 暂无前端页面 | 预留 | 后续若补前端管理页，统一进入系统管理 |

## 5. 入口状态总表

### 5.1 保留入口

- `/home`
- `/ai-generation/requirement-analysis`
- `/ai-generation/generated-testcases`
- `/ai-generation/projects`
- `/ai-generation/testcases`
- `/ai-generation/versions`
- `/ai-generation/reviews`
- `/ai-generation/review-templates`
- `/api-testing/dashboard`
- `/api-testing/projects`
- `/api-testing/interfaces`
- `/api-testing/automation`
- `/api-testing/history`
- `/api-testing/environments`
- `/ui-automation/dashboard`
- `/ui-automation/projects`
- `/ui-automation/elements-enhanced`
- `/ui-automation/test-cases`
- `/ui-automation/scripts-enhanced`
- `/ui-automation/scripts`
- `/ui-automation/suites`
- `/ai-intelligent-mode/testing`
- `/ai-intelligent-mode/cases`
- `/app-automation/dashboard`
- `/app-automation/projects`
- `/app-automation/devices`
- `/app-automation/packages`
- `/app-automation/elements`
- `/app-automation/scene-builder`
- `/app-automation/test-cases`
- `/app-automation/test-suites`
- `/data-factory`
- `/configuration/ai-model`
- `/configuration/prompt-config`
- `/configuration/generation-config`
- `/configuration/ui-env`
- `/configuration/app-env`
- `/configuration/ai-mode`
- `/configuration/scheduled-task`
- `/configuration/dify`

### 5.2 隐藏入口

- `/ai-generation/assistant`
- `/ai-generation/testsuites`
- `/ai-generation/task-detail/:taskId`
- `/ui-automation/scripts/editor`
- `/login`
- `/register`
- `/admin/`

### 5.3 未来迁移入口

- `/ai-generation/executions` -> `执行中心`
- `/ai-generation/executions/:id` -> `执行中心`
- `/ai-generation/reports` -> `执行中心`
- `/ai-generation/profile` -> `系统管理`
- `/api-testing/reports` -> `执行中心`
- `/api-testing/scheduled-tasks` -> `执行中心`
- `/api-testing/notification-logs` -> `执行中心`
- `/api-testing/ai-service-config` -> `配置中心`
- `/ui-automation/executions` -> `执行中心`
- `/ui-automation/reports` -> `执行中心`
- `/ui-automation/scheduled-tasks` -> `执行中心`
- `/ui-automation/notification-logs` -> `执行中心`
- `/ai-intelligent-mode/execution-records` -> `执行中心`
- `/app-automation/executions` -> `执行中心`
- `/app-automation/reports` -> `执行中心`
- `/app-automation/scheduled-tasks` -> `执行中心`
- `/app-automation/notification-logs` -> `执行中心`

### 5.4 不再新增入口

- 不再新增一级导航：`AI 用例生成`、`AI 助手`、`AI 智能模式`
- 不再新增新的平台级配置页到 `/ai-generation/*`、`/api-testing/*`、`/ui-automation/*`、`/app-automation/*`
- 不再新增新的平台级报告 / 调度 / 通知日志页到各业务模块路径下，后续统一进 `执行中心`
- 不再新增新的系统页到 `/ai-generation/*`
- 不再新增新的 AI 助手类工具一级导航；AI 助手统一按隐藏工具入口处理

## 6. 统一导航真源建议

建议新增前端配置文件 `frontend/src/config/navigation.js`，只表达冻结后的一级导航、二级归属和入口状态，不直接改写现有 `router/index.js`。  
后续如果要改首页卡片、侧边栏和面包屑，应优先消费该配置，而不是继续在页面里手写模块判断。

## 7. 本次不做的事

- 不重命名现有路由前缀。
- 不删除旧页面或遗留页面。
- 不批量移动页面目录。
- 不改后端 app。
- 不直接重构首页和 Layout 展示逻辑。

## 8. 验收标准

- [x] 一级导航冻结清单已明确
- [x] 每个一级导航的二级页面归属已明确
- [x] 保留入口 / 隐藏入口 / 未来迁移入口 / 不再新增入口已明确
- [x] 方案与当前 `router/index.js`、`layout/index.vue`、`Home.vue` 对齐
- [x] 未触发大规模页面重构和路由重写

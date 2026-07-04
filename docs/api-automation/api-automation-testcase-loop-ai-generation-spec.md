# 接口自动化 P0 用例闭环与 AI 生成多目标需求规格

更新时间：2026-06-17

状态：Spec/SDD 草案，等待确认后进入 TDD

## 1. 文档目的

本文把两类需求合并成一份可执行的需求规格：

- P0 闭环修复：接口自动化必须有清晰的“接口测试用例”子模块，不能只靠“接口管理”承接用例心智。
- AI 生成扩展：AI 需求分析生成测试用例时，允许选择生成目标类型，并在用户确认资产后同步进入对应一级模块的测试用例列表。

本文只定义需求、边界、数据流、接口契约、验收口径和风险，不直接进入实现。由于涉及前端、后端、数据模型、执行器、AI Prompt、跨模块资产采纳，后续必须按 `Spec/SDD -> TDD -> Execution -> VDD` 推进。

## 2. 背景

### 2.1 当前接口自动化的问题

当前接口自动化可以创建接口请求、发送请求、加入测试套件、执行套件、查看请求历史和套件执行记录。

但用户视角存在明显断点：

- 一级模块叫“接口自动化”，但子模块没有“接口测试用例”。
- 当前最接近“接口测试用例”的对象是 `ApiRequest`，页面入口却叫“接口管理”。
- “接口管理”同时承担接口资产、接口调试、接口用例编辑、请求发送等职责，语义混杂。
- 历史“自动化测试”入口实际承接的是测试套件执行，不是接口测试用例列表；当前正式可见名称应统一为“测试套件”。
- AI 生成接口测试用例后没有明确落点，不知道应该进入接口自动化哪个子模块。

### 2.2 当前 AI 生成的问题

当前 AI 需求分析生成链路主要面向测试设计模块的功能测试用例。

用户提出的新需求是：

- AI 生成测试用例时增加一个下拉框。
- 可选择：
  - 功能测试用例
  - 接口测试用例
  - Web 自动化测试用例
  - App 自动化测试用例
- 选择哪个类型，就使用哪个类型对应的 AI 提示词。
- 生成后，用户确认资产。
- 确认后，资产同步进入对应一级模块中的测试用例子模块列表，并可查看。

这个需求不能只改一个下拉框。它会影响：

- Prompt 配置选择规则
- 生成任务对象
- 生成结果对象
- 结果采纳逻辑
- 目标资产模型
- 目标模块列表页
- 来源追踪和重复采纳
- 目标模块权限和项目归属

## 3. 当前代码事实

### 3.1 接口自动化现有对象

接口自动化后端模块：`apps/api_testing`

现有核心对象：

- `ApiProject`：接口项目。
- `ApiCollection`：接口集合或目录。
- `ApiRequest`：API 请求资产，目前最接近“接口测试用例”的对象。
- `Environment`：接口环境变量。
- `RequestHistory`：单接口执行历史。
- `TestSuite`：测试套件。
- `TestSuiteRequest`：套件和请求的关联关系，包含执行顺序、启用状态、套件级断言。
- `TestExecution`：套件执行结果。
- `ScheduledTask`、`TaskExecutionLog`、`NotificationLog`：定时执行和通知相关对象。

当前后端路由：

- `/api-testing/projects/`
- `/api-testing/collections/`
- `/api-testing/requests/`
- `/api-testing/requests/{id}/execute/`
- `/api-testing/histories/`
- `/api-testing/test-suites/`
- `/api-testing/test-suites/{id}/execute/`
- `/api-testing/test-suites/{id}/add-requests/`
- `/api-testing/test-suite-requests/`
- `/api-testing/test-executions/`

当前前端入口：

- `/api-testing/dashboard`：接口自动化总览。
- `/api-testing/projects`：项目管理。
- `/api-testing/interfaces`：接口管理。
- `/api-testing/test-suites`：测试套件。
- `/api-testing/automation`：旧入口兼容，重定向到测试套件。
- `/api-testing/history`：请求历史。
- `/api-testing/environments`：环境管理。

当前缺口：

- 没有 `/api-testing/test-cases`。
- 没有 `ApiTestCase` 模型。
- 没有用户可直接理解的“接口测试用例列表”。

### 3.2 其他模块已有测试用例对象

功能测试用例：

- 后端对象：`apps/testcases.models.TestCase`
- 前端入口：测试设计模块的测试用例列表。
- 当前 AI 生成采纳已经主要落到该对象。

Web 自动化测试用例：

- 后端对象：`apps/ui_automation.models.TestCase`
- 前端入口：`/ui-automation/test-cases`
- 步骤对象：`TestCaseStep`

App 自动化测试用例：

- 后端对象：`apps/app_automation.models.AppTestCase`
- 前端入口：`/app-automation/test-cases`
- 用例主体包含 `ui_flow`、变量、超时、重试等配置。

接口自动化测试用例：

- P0 建议对象：继续使用 `apps/api_testing.models.ApiRequest`
- 原因：当前接口执行、历史、套件、定时任务都已经围绕 `ApiRequest` 建立，P0 新增独立 `ApiTestCase` 表会带来迁移和兼容成本。
- 产品呈现：把 `ApiRequest` 明确定义为“接口测试用例资产”。

## 4. 目标

### 4.1 P0 闭环目标

P0 必须让接口自动化形成用户可理解的闭环：

1. 用户进入“接口自动化”。
2. 用户能看到“接口测试用例”子模块。
3. 用户能在“接口测试用例”中查看、创建、编辑、调试、执行接口用例。
4. 用户能把接口测试用例加入测试套件。
5. 用户能执行单个接口测试用例，并查看请求历史和断言结果。
6. 用户能执行测试套件，并查看套件执行结果。
7. AI 生成的接口测试用例在确认后能进入“接口测试用例”列表。

### 4.2 AI 多目标生成目标

AI 需求分析生成测试用例时，应支持以下目标类型：

| 目标类型 | 展示名称 | 目标模块 | 目标资产 |
| --- | --- | --- | --- |
| `functional_test_case` | 功能测试用例 | 测试设计 | `apps.testcases.TestCase` |
| `api_test_case` | 接口测试用例 | 接口自动化 | `apps.api_testing.ApiRequest` |
| `web_automation_test_case` | Web 自动化测试用例 | Web 自动化 | `apps.ui_automation.TestCase` |
| `app_automation_test_case` | App 自动化测试用例 | App 自动化 | `apps.app_automation.AppTestCase` |

### 4.3 用户体验目标

- 用户在生成前就明确知道本次要生成哪类用例。
- 生成过程使用对应类型的 Prompt，不混用功能测试 Prompt。
- 生成结果列表能显示目标类型。
- 采纳按钮语义明确，例如“确认为接口测试用例”。
- 采纳成功后提供跳转入口，直接进入目标模块对应列表或详情。
- 重复采纳同一条生成结果时，不重复创建资产。
- 目标模块列表能看出资产来源于 AI 生成。

## 5. 非目标

本轮不做以下事项：

- 不重构整个执行中心。
- 不把接口报告、定时任务、通知日志提前迁回接口自动化正式导航。
- 不一次性重构所有自动化模块的数据模型。
- 不把 `ApiRequest` 立即拆成 `ApiRequest` + `ApiTestCase` 双模型。
- 不强行让 AI 生成的 Web/App 自动化用例马上可直接稳定执行，因为缺少元素库、设备、应用包、页面对象时只能作为草稿。
- 不新增一套绕开现有 AI 配置的模型调用入口。
- 不在页面中散写后端请求，前端请求仍需走 `frontend/src/api/* -> frontend/src/utils/api.js`。
- 不用整页刷新兜底模块切换、采纳跳转或列表刷新。

## 6. 核心产品定义

### 6.1 接口测试用例的定义

P0 阶段，接口测试用例等价于可执行的 `ApiRequest`。

一个接口测试用例至少包含：

- 名称
- 所属接口项目
- 所属集合
- 请求方法
- URL
- Headers
- Params
- Body
- Auth 配置
- 断言
- 前置脚本
- 后置脚本
- 创建人
- 更新时间
- 来源信息

注意：

- 数据库对象仍是 `ApiRequest`。
- 用户界面展示为“接口测试用例”。
- “接口管理”可以保留为兼容入口，但不能再作为唯一用例入口。

### 6.2 接口测试用例闭环

目标闭环：

```text
接口项目
  -> 接口测试用例
  -> 单用例调试执行
  -> 请求历史与断言结果
  -> 加入测试套件
  -> 套件执行
  -> 套件执行结果
  -> 回到用例维护
```

AI 接入后的闭环：

```text
需求分析
  -> 选择生成目标：接口测试用例
  -> 使用接口测试用例 Prompt
  -> 生成结果
  -> 用户确认资产
  -> 创建或复用 ApiRequest
  -> 进入接口自动化 / 接口测试用例列表
  -> 调试、执行、加入套件
```

## 7. 导航与页面需求

### 7.1 接口自动化导航

接口自动化当前导航应调整为：

- 仪表盘
- 项目管理
- 接口测试用例
- 测试套件
- 请求历史
- 环境管理

兼容策略：

- 新增正式入口：`/api-testing/test-cases`
- 旧入口 `/api-testing/interfaces` 不立即删除。
- 旧入口可作为隐藏路由、兼容路由或重定向到 `/api-testing/test-cases`。
- 如果保留“接口管理”，则必须明确它是接口目录和调试工作区，不应再让它成为唯一用例入口。

### 7.2 接口测试用例列表页

页面路径：

```text
/api-testing/test-cases
```

页面职责：

- 展示接口测试用例列表。
- 支持按项目、集合、请求方法、关键词筛选。
- 支持创建接口测试用例。
- 支持编辑接口测试用例。
- 支持单用例执行。
- 支持查看最近执行结果。
- 支持加入测试套件。
- 支持从 AI 来源跳转过来的定位。

列表字段建议：

| 字段 | 说明 |
| --- | --- |
| 用例名称 | `ApiRequest.name` |
| 请求方法 | `ApiRequest.method` |
| URL | `ApiRequest.url` |
| 所属项目 | 通过集合反查 `ApiProject` |
| 所属集合 | `ApiCollection.name` |
| 断言数 | `ApiRequest.assertions.length` |
| 来源 | 手工创建 / AI 生成 / 导入 |
| 最近执行状态 | 从 `RequestHistory` 取最新记录 |
| 更新时间 | `ApiRequest.updated_at` |
| 操作 | 编辑、执行、查看历史、加入套件、删除 |

筛选项建议：

- 关键词：名称、URL。
- 接口项目。
- 集合。
- 请求方法。
- 来源。
- 最近执行结果。

### 7.3 接口测试用例编辑页或抽屉

P0 可以复用当前 `InterfaceManagement.vue` 的编辑能力，但产品语义必须调整。

编辑区域至少包含：

- 基本信息：名称、描述、项目、集合。
- 请求信息：方法、URL、Headers、Params、Body、Auth。
- 断言：状态码、响应时间、包含文本、JSONPath、Header、全文相等。
- 执行：选择环境后发送请求。
- 响应：状态码、耗时、响应体、响应头、断言结果。
- 来源：如果来自 AI，显示来源任务和生成结果信息。

### 7.4 测试套件页面补齐点

当前“测试套件”承担 `TestSuite + TestSuiteRequest` 编排执行职责，旧 `/api-testing/automation` 只保留兼容重定向。

P0 必须保持：

- 创建套件。
- 编辑套件。
- 添加接口测试用例到套件。
- 启用或禁用套件内用例。
- 运行套件。
- 查看执行历史。

P0 建议补齐：

- 套件内“编辑断言”不能继续只提示“功能开发中”。
- 若本轮不实现套件级断言编辑，则按钮必须隐藏或禁用，并说明该能力不参与 P0 验收。

## 8. AI 生成入口需求

### 8.1 生成前下拉框

在 AI 需求分析生成测试用例的入口增加“生成目标类型”下拉框。

字段：

```text
target_type
```

选项：

| value | label | 默认 |
| --- | --- | --- |
| `functional_test_case` | 功能测试用例 | 是 |
| `api_test_case` | 接口测试用例 | 否 |
| `web_automation_test_case` | Web 自动化测试用例 | 否 |
| `app_automation_test_case` | App 自动化测试用例 | 否 |

交互规则：

- 默认值为 `functional_test_case`，保证旧流程不受影响。
- 生成任务开始后，下拉框锁定，不允许中途修改。
- 恢复未完成任务时，应显示该任务创建时的目标类型。
- 任务详情页、生成结果页都必须展示目标类型。
- 如果用户切换目标类型，前端应同步展示对应说明，但不直接调用 AI。

### 8.2 目标类型说明文案

下拉框旁边可以有简短说明：

- 功能测试用例：生成测试设计模块可管理的功能测试用例。
- 接口测试用例：生成接口自动化模块可调试、执行、加入套件的接口用例。
- Web 自动化测试用例：生成 Web 自动化草稿用例，后续需要补齐元素和步骤参数。
- App 自动化测试用例：生成 App 自动化草稿用例，后续需要补齐设备、应用包和 UI 流程参数。

页面不应使用“预留”“开发中”等开发口吻。

## 9. Prompt 配置需求

### 9.1 Prompt 选择规则

当前 Prompt 主要按角色区分：

- writer
- reviewer

新需求需要同时按目标类型区分：

- writer + functional_test_case
- writer + api_test_case
- writer + web_automation_test_case
- writer + app_automation_test_case
- reviewer + functional_test_case
- reviewer + api_test_case
- reviewer + web_automation_test_case
- reviewer + app_automation_test_case

### 9.2 PromptConfig 建议扩展

建议在 `PromptConfig` 增加：

```text
target_type
```

字段含义：

- 表示该 Prompt 适用于哪类生成目标。
- 旧数据默认 `functional_test_case`。

激活规则：

- 同一 `prompt_type + target_type` 只允许一个启用版本。
- 查询活跃 Prompt 时必须同时传 `prompt_type` 和 `target_type`。

缺失处理：

- 找不到目标类型对应的 writer Prompt 时，直接报错。
- 找不到目标类型对应的 reviewer Prompt 且开启自动评审时，直接报错。
- 不允许静默回退到功能测试用例 Prompt。

错误提示示例：

```text
未配置“接口测试用例”的用例编写 Prompt，请先到 Prompt 配置中启用对应配置。
```

### 9.3 各目标 Prompt 输出约束

功能测试用例输出字段：

- `case_id`
- `title`
- `priority`
- `precondition`
- `test_steps`
- `expected_result`

接口测试用例输出字段：

- `case_id`
- `name`
- `description`
- `method`
- `url`
- `headers`
- `params`
- `body`
- `auth`
- `assertions`
- `pre_request_script`
- `post_request_script`

Web 自动化测试用例输出字段：

- `case_id`
- `name`
- `description`
- `priority`
- `steps`

Web 步骤字段：

- `step_number`
- `action_type`
- `target_description`
- `selector`
- `input_value`
- `assertion_type`
- `expected_value`

App 自动化测试用例输出字段：

- `case_id`
- `name`
- `description`
- `ui_flow`
- `variables`
- `timeout`
- `retry_count`

注意：

- AI 输出必须经过后端校验和归一化。
- AI 输出字段缺失时，不能直接写入目标资产。
- 目标类型不同，解析器不能共用同一套字段假设。

## 10. 生成任务数据需求

### 10.1 TestCaseGenerationTask 扩展

建议新增或等价保存：

```text
target_type
target_type_label
```

含义：

- `target_type`：机器可识别的生成目标类型。
- `target_type_label`：展示用中文名称，可由后端序列化生成，不一定落库。

任务创建时必须固化：

- 目标类型。
- writer Prompt。
- reviewer Prompt。
- 生成配置。
- 来源项目或上下文。

任务执行过程中不得根据前端当前下拉框重新判断目标类型。

### 10.2 GeneratedTestCase 扩展

建议新增或等价保存：

```text
target_type
raw_payload
normalized_payload
adoption_status
adopted_asset_type
adopted_asset_id
adopted_asset_route
adoption_error
```

字段说明：

| 字段 | 说明 |
| --- | --- |
| `target_type` | 该生成结果属于哪类目标资产 |
| `raw_payload` | AI 原始解析后的结构化内容 |
| `normalized_payload` | 后端归一化后可采纳的数据 |
| `adoption_status` | pending / adopted / discarded / failed |
| `adopted_asset_type` | 采纳后的目标资产类型 |
| `adopted_asset_id` | 采纳后的目标资产 ID |
| `adopted_asset_route` | 前端跳转路径 |
| `adoption_error` | 最近一次采纳失败原因 |

兼容策略：

- 当前已有 `status` 字段时，可以继续使用 `generated / adopted / discarded` 表示结果状态。
- 新增字段应尽量作为补充，不破坏旧页面已有处理状态。

## 11. 结果采纳需求

### 11.1 采纳入口

生成结果列表中，每条结果应根据 `target_type` 显示对应动作：

| 目标类型 | 按钮文案 |
| --- | --- |
| 功能测试用例 | 确认为功能测试用例 |
| 接口测试用例 | 确认为接口测试用例 |
| Web 自动化测试用例 | 确认为 Web 自动化用例 |
| App 自动化测试用例 | 确认为 App 自动化用例 |

批量采纳也必须遵守当前任务的目标类型。

### 11.2 采纳弹窗

不同目标类型需要不同的确认字段。

功能测试用例：

- 测试设计项目
- 版本
- 标题
- 优先级
- 测试类型
- 状态
- 前置条件
- 步骤
- 预期结果

接口测试用例：

- 接口项目
- 接口集合
- 名称
- 方法
- URL
- Headers
- Params
- Body
- Auth
- 断言
- 状态：默认可执行草稿

Web 自动化测试用例：

- Web 自动化项目
- 用例名称
- 优先级
- 描述
- 步骤列表
- 状态：默认草稿

App 自动化测试用例：

- App 自动化项目
- 应用包，允许为空
- 用例名称
- 描述
- UI Flow
- 变量
- 超时时间
- 重试次数

### 11.3 目标项目选择规则

功能测试用例：

- 默认使用需求分析所在的测试设计项目。
- 如项目缺失，必须让用户选择项目。
- 版本仍按当前逻辑选择或自动挂默认版本。

接口测试用例：

- 必须选择接口项目。
- 必须选择接口集合。
- 如果用户未选择集合，系统可以创建或复用一个默认集合：

```text
AI 生成接口用例
```

Web 自动化测试用例：

- 必须选择 Web 自动化项目。
- 如果 AI 生成步骤中的元素无法绑定，步骤保存为草稿或未绑定元素状态。

App 自动化测试用例：

- 必须选择 App 自动化项目。
- 应用包允许后续补充，但页面必须显示该用例未绑定应用包时不能直接完整执行。

### 11.4 采纳幂等规则

同一条生成结果重复采纳时，必须幂等成功，不重复创建资产。

建议去重键：

```text
task_id + case_id + target_type
```

如果没有 `case_id`，使用：

```text
task_id + case_index + target_type
```

再次采纳命中已存在资产时：

- 返回已有目标资产。
- 结果状态保持 `adopted`。
- 页面提示“该结果已确认，已返回现有资产”。
- 不创建重复资产。

## 12. 各目标资产落库映射

### 12.1 功能测试用例

目标模型：

```text
apps.testcases.models.TestCase
```

映射：

| 生成字段 | 目标字段 |
| --- | --- |
| `title` | `title` |
| `description` | `description` |
| `precondition` | `preconditions` |
| `test_steps` | `steps` |
| `expected_result` | `expected_result` |
| `priority` | `priority` |
| `test_type` | `test_type` |
| 来源信息 | `tags` |

### 12.2 接口测试用例

目标模型：

```text
apps.api_testing.models.ApiRequest
```

映射：

| 生成字段 | 目标字段 |
| --- | --- |
| `name` | `name` |
| `description` | `description` |
| `method` | `method` |
| `url` | `url` |
| `headers` | `headers` |
| `params` | `params` |
| `body` | `body` |
| `auth` | `auth` |
| `assertions` | `assertions` |
| `pre_request_script` | `pre_request_script` |
| `post_request_script` | `post_request_script` |
| `collection_id` | `collection` |
| 来源信息 | 建议新增 `source_metadata` 或通过采纳映射表保存 |

接口测试用例创建后必须能在：

```text
/api-testing/test-cases
```

看到。

### 12.3 Web 自动化测试用例

目标模型：

```text
apps.ui_automation.models.TestCase
apps.ui_automation.models.TestCaseStep
```

映射：

| 生成字段 | 目标字段 |
| --- | --- |
| `name` | `TestCase.name` |
| `description` | `TestCase.description` |
| `priority` | `TestCase.priority` |
| `steps` | `TestCaseStep` 列表 |

步骤映射：

| 生成字段 | 目标字段 |
| --- | --- |
| `step_number` | `step_number` |
| `action_type` | `action_type` |
| `input_value` | `input_value` |
| `selector` | 元素未绑定时保存为描述或扩展字段 |
| `assertion_type` | `assertion_type` |
| `expected_value` | `expected_value` |

注意：

- 如果当前模型没有保存 `selector` 的合适字段，P0 允许保存为草稿描述，不强行绑定元素对象。
- 不能伪装成已可直接稳定执行的用例。

### 12.4 App 自动化测试用例

目标模型：

```text
apps.app_automation.models.AppTestCase
```

映射：

| 生成字段 | 目标字段 |
| --- | --- |
| `name` | `name` |
| `description` | `description` |
| `ui_flow` | `ui_flow` |
| `variables` | `variables` |
| `timeout` | `timeout` |
| `retry_count` | `retry_count` |
| `app_package_id` | `app_package` |

注意：

- `app_package` 可以为空，但空值下页面必须提示需要补齐应用包后再执行。
- AI 生成的 `ui_flow` 必须经过 schema 校验，校验失败不能落库。

## 13. 接口自动化执行闭环补齐需求

### 13.1 前端 API 封装修正

当前存在旧路径隐患：

```text
/api-testing/api-requests/{id}/execute/
```

后端真实路径是：

```text
/api-testing/requests/{id}/execute/
```

P0 必须修正前端 API 封装，避免后续新页面复用旧函数后直接 404。

当前还存在执行详情旧路径隐患：

```text
/api-testing/executions/{id}/
```

后端真实路径应是：

```text
/api-testing/test-executions/{id}/
```

P0 必须统一修正。

### 13.2 单接口执行历史

执行单个接口测试用例后：

- 必须创建 `RequestHistory`。
- 必须保存请求数据。
- 必须保存响应数据。
- 必须保存状态码。
- 必须保存响应时间。
- 必须保存断言结果。
- 执行失败也必须落历史，记录错误信息。

当前风险：

- 单接口执行返回了断言结果，但历史记录中可能没有持久化 `assertions_results`。

P0 要求：

- `RequestHistory.assertions_results` 必须真实落库。
- 请求历史页能展示断言结果。

### 13.3 套件执行

执行测试套件后：

- 必须创建 `TestExecution`。
- 必须记录总请求数、通过数、失败数。
- 必须保存每个接口测试用例的执行结果。
- 每个接口请求也必须写入 `RequestHistory`。
- 套件执行结果中的断言结果要能追溯。

### 13.4 脚本和 Auth 处理

当前 `ApiRequest` 有：

- `auth`
- `pre_request_script`
- `post_request_script`

但执行器未必完整执行这些字段。

P0 建议规则：

- 对已经支持的 Auth 类型，必须真实应用到请求。
- 对未支持的 Auth 类型，执行时直接报错，不静默忽略。
- 如果 `pre_request_script` 或 `post_request_script` 非空，但执行器尚未支持安全脚本执行，执行时直接报错或在 UI 禁用入口。
- 不允许页面让用户填写脚本，但执行时静默忽略。

P1 可再做安全脚本沙箱和变量提取。

## 14. 后端接口需求

### 14.1 生成任务创建接口

请求体新增：

```json
{
  "target_type": "api_test_case"
}
```

后端处理：

1. 校验 `target_type` 是否在允许枚举内。
2. 根据 `target_type` 查找 writer Prompt。
3. 如果开启自动评审，根据 `target_type` 查找 reviewer Prompt。
4. 找不到对应 Prompt 时直接返回 400。
5. 创建任务时固化 `target_type` 和 Prompt 配置。

### 14.2 Prompt 查询接口

支持按目标类型过滤：

```text
GET /requirement-analysis/prompts/?prompt_type=writer&target_type=api_test_case
```

返回必须包含：

- Prompt 名称
- Prompt 类型
- 目标类型
- 是否启用
- 更新时间

### 14.3 生成结果采纳接口

建议统一接口：

```text
POST /requirement-analysis/test-cases/{generated_case_id}/adopt/
```

请求体示例：

功能测试用例：

```json
{
  "target_type": "functional_test_case",
  "project_id": 1,
  "version_id": 2
}
```

接口测试用例：

```json
{
  "target_type": "api_test_case",
  "api_project_id": 1,
  "collection_id": 10
}
```

Web 自动化测试用例：

```json
{
  "target_type": "web_automation_test_case",
  "ui_project_id": 1
}
```

App 自动化测试用例：

```json
{
  "target_type": "app_automation_test_case",
  "app_project_id": 1,
  "app_package_id": null
}
```

响应体示例：

```json
{
  "adopted": true,
  "deduplicated": false,
  "target_type": "api_test_case",
  "asset_id": 123,
  "asset_name": "登录接口",
  "asset_route": "/api-testing/test-cases?caseId=123"
}
```

### 14.4 批量采纳接口

当前已有批量采纳能力时，应扩展支持 `target_type` 和目标模块项目参数。

要求：

- 同一个任务的批量采纳只能采纳到任务固化的 `target_type`。
- 前端传入的 `target_type` 与任务 `target_type` 不一致时直接报错。
- 批量采纳必须逐条幂等。
- 部分失败时必须返回失败详情，不允许假成功。

## 15. 前端接口封装需求

新增或调整 `frontend/src/api/*` 封装。

建议新增：

```text
frontend/src/api/requirement-analysis.js
frontend/src/api/api-testing.js
frontend/src/api/ui_automation.js
frontend/src/api/app-automation.js
```

具体函数建议：

```js
createGenerationTask(data)
getPromptConfigs(params)
adoptGeneratedCase(id, data)
batchAdoptGeneratedCases(taskId, data)
getApiTestCases(params)
createApiTestCase(data)
updateApiTestCase(id, data)
executeApiTestCase(id, data)
```

要求：

- 页面不得直接散写 `api.get/post`。
- 所有后端请求经由 `frontend/src/api/*`。
- 认证、401、refresh 继续由 `frontend/src/utils/api.js` 统一处理。

## 16. 异常场景与提示规范

### 16.1 后端错误响应基本约定

本需求涉及多个模块，当前各模块返回结构不完全统一。P0 不强制全仓统一响应包裹，但新增和改造接口必须保证前端至少能稳定读取以下信息：

```json
{
  "code": "PROMPT_NOT_CONFIGURED",
  "message": "未配置“接口测试用例”的用例编写 Prompt，请先到 Prompt 配置中启用对应配置。",
  "field_errors": {
    "target_type": ["请选择生成目标类型"]
  },
  "details": {},
  "trace_id": "optional-request-id"
}
```

兼容要求：

- 如果旧接口仍返回 `{"error": "..."}`，前端错误归一化层必须兼容读取。
- 新增接口优先返回 `code + message`，不要只返回 Python 异常字符串。
- `message` 必须是可直接展示给用户的中文提示。
- `details` 用于调试信息，不直接大段展示给普通用户。
- 生产环境不向前端返回堆栈、数据库异常原文、密钥、模型请求详情。

### 16.2 HTTP 状态码与错误码建议

| 场景 | HTTP 状态 | code | 用户提示 |
| --- | --- | --- | --- |
| 未登录或登录过期 | 401 | `AUTH_REQUIRED` | 登录状态已过期，请重新登录 |
| 无目标项目权限 | 403 | `PERMISSION_DENIED` | 你没有该项目的操作权限 |
| 目标对象不存在 | 404 | `RESOURCE_NOT_FOUND` | 目标数据不存在或已被删除 |
| 生成目标类型非法 | 400 | `TARGET_TYPE_INVALID` | 生成目标类型不支持，请重新选择 |
| 缺少必填参数 | 400 | `VALIDATION_ERROR` | 请补齐必填信息 |
| Prompt 未配置 | 400 | `PROMPT_NOT_CONFIGURED` | 未配置对应类型 Prompt，请先完成配置 |
| AI 模型未配置 | 400 | `AI_MODEL_NOT_CONFIGURED` | 未配置可用 AI 模型，请先完成配置 |
| AI 输出不可解析 | 400 | `AI_OUTPUT_PARSE_FAILED` | AI 返回内容无法解析，请调整 Prompt 后重试 |
| AI 输出字段不合规 | 400 | `AI_OUTPUT_SCHEMA_INVALID` | AI 返回内容缺少必要字段，请调整后重试 |
| 任务状态不允许操作 | 409 | `TASK_STATE_CONFLICT` | 当前任务状态不允许执行该操作 |
| 目标类型与任务不一致 | 409 | `TARGET_TYPE_MISMATCH` | 当前结果类型与任务目标类型不一致 |
| 重复提交同一操作 | 409 或幂等成功 | `DUPLICATE_SUBMIT` | 操作正在处理中，请勿重复提交 |
| 已采纳结果再次采纳 | 200 | `ADOPTION_DEDUPLICATED` | 该结果已确认，已返回现有资产 |
| 已弃用结果再次采纳 | 409 | `RESULT_ALREADY_DISCARDED` | 该结果已弃用，不能再确认资产 |
| 接口 URL 非法 | 400 | `API_URL_INVALID` | 接口 URL 不合法，请检查协议和地址 |
| Auth 类型未支持 | 400 | `AUTH_TYPE_UNSUPPORTED` | 当前认证方式暂不支持执行 |
| 脚本执行未支持 | 400 | `SCRIPT_UNSUPPORTED` | 当前暂不支持执行前置或后置脚本 |
| 接口请求超时 | 400 | `API_REQUEST_TIMEOUT` | 接口请求超时，请检查服务或环境配置 |
| 第三方模型超时 | 502 或 504 | `AI_PROVIDER_TIMEOUT` | AI 服务响应超时，请稍后重试 |
| 服务内部异常 | 500 | `INTERNAL_ERROR` | 系统处理异常，请稍后重试或联系管理员 |

说明：

- DRF 体系下表单校验类错误优先使用 400，不引入 422。
- 同一条生成结果重复采纳属于幂等成功，优先返回 200，而不是 409。
- 重复点击导致的并发提交，如果后端还没完成第一次处理，可以返回 409，并要求前端按钮进入 loading 禁用。

### 16.3 前端提示策略

前端展示规则：

- 字段级错误：展示在对应表单项下方，例如目标类型、目标项目、集合、URL。
- 页面级加载失败：使用统一状态组件展示请求失败，并提供“重试”动作。
- 操作级失败：使用 `ElMessage.error(message)` 或表单错误提示，不使用 `alert()`。
- 高风险确认：删除、批量采纳、覆盖已有资产等使用 `ElMessageBox.confirm`。
- 批量部分失败：不能只弹一个“失败”，必须展示成功数、失败数和失败明细。
- 未登录或 401：继续走统一 `authNavigation`，不在页面内直接跳转或刷新。
- 后端返回未知错误：展示“操作失败，请稍后重试”，控制台记录归一化后的错误对象。

提示优先级：

1. 字段错误优先展示在字段旁边。
2. 后端 `message` 优先展示给用户。
3. 无 `message` 时使用前端兜底文案。
4. 不直接展示 `details`、堆栈、SQL、模型请求原文。

### 16.4 AI 生成入口异常矩阵

| 异常场景 | 后端行为 | 前端提示 | 是否允许重试 |
| --- | --- | --- | --- |
| 未选择目标类型 | 前端先拦截；后端返回 400 `VALIDATION_ERROR` | 请选择生成目标类型 | 是 |
| 目标类型非法 | 400 `TARGET_TYPE_INVALID` | 生成目标类型不支持，请重新选择 | 是 |
| writer Prompt 缺失 | 400 `PROMPT_NOT_CONFIGURED` | 未配置“接口测试用例”的用例编写 Prompt，请先到 Prompt 配置中启用对应配置 | 配置后可重试 |
| reviewer Prompt 缺失且开启自动评审 | 400 `PROMPT_NOT_CONFIGURED` | 未配置对应类型的评审 Prompt，请先完成配置或关闭自动评审 | 配置后可重试 |
| AI 模型缺失 | 400 `AI_MODEL_NOT_CONFIGURED` | 未配置可用 AI 模型，请先完成配置 | 配置后可重试 |
| 生成任务已在运行 | 409 `TASK_STATE_CONFLICT` | 当前已有生成任务正在执行，请等待完成或取消后重试 | 否 |
| 用户取消任务 | 状态置为 `cancelled`，停止后续写库 | 已取消生成 | 可重新发起 |
| AI 服务超时 | 502/504 `AI_PROVIDER_TIMEOUT` | AI 服务响应超时，请稍后重试 | 是 |
| AI 返回空内容 | 400 `AI_OUTPUT_PARSE_FAILED` | AI 未返回可用内容，请调整 Prompt 后重试 | 是 |
| AI 返回非 JSON 或结构不可解析 | 400 `AI_OUTPUT_PARSE_FAILED` | AI 返回内容无法解析，请调整 Prompt 后重试 | 是 |
| AI 字段缺失或类型错误 | 400 `AI_OUTPUT_SCHEMA_INVALID` | AI 返回内容缺少必要字段，请调整 Prompt 后重试 | 是 |
| 轮询或 SSE 中断 | 任务继续在后端执行，前端可恢复查询 | 连接中断，正在尝试恢复任务状态 | 是 |

生成任务写库要求：

- 任务创建失败时，不创建半成品任务。
- 任务已创建但生成失败时，任务状态必须进入 `failed`，并记录可展示失败原因。
- 任务取消后，最终结果写库前必须再次检查取消状态，避免取消后又写入结果。
- 目标类型必须在任务创建时固化，后续恢复任务不能用前端当前下拉框覆盖。

### 16.5 生成结果采纳异常矩阵

| 异常场景 | 后端行为 | 前端提示 | 结果状态 |
| --- | --- | --- | --- |
| 未选择目标项目 | 前端先拦截；后端返回 400 | 请选择目标项目 | 不变 |
| 接口用例未选择集合且未开启默认集合策略 | 400 `VALIDATION_ERROR` | 请选择接口集合 | 不变 |
| 目标项目无权限 | 403 `PERMISSION_DENIED` | 你没有该项目的操作权限 | 不变 |
| 生成结果不存在 | 404 `RESOURCE_NOT_FOUND` | 生成结果不存在或已被删除 | 不变 |
| 生成结果已弃用 | 409 `RESULT_ALREADY_DISCARDED` | 该结果已弃用，不能再确认资产 | `discarded` |
| 生成结果已采纳 | 200 `ADOPTION_DEDUPLICATED` | 该结果已确认，已返回现有资产 | `adopted` |
| 前端传入目标类型与任务不一致 | 409 `TARGET_TYPE_MISMATCH` | 当前结果类型与任务目标类型不一致，请刷新后重试 | 不变 |
| 目标资产字段校验失败 | 400 `VALIDATION_ERROR` | 请检查用例名称、URL、步骤或必填字段 | 不变 |
| 接口 URL 非法 | 400 `API_URL_INVALID` | 接口 URL 不合法，请检查协议和地址 | 不变 |
| 创建目标资产成功但来源回写失败 | 后端事务回滚；返回 500 或 400 | 确认资产失败，请稍后重试 | 不变 |
| 批量采纳部分失败 | 207 风格响应或 200 带明细 | 已确认 X 条，失败 Y 条，请查看失败原因 | 成功项 `adopted`，失败项不变 |
| 用户重复点击采纳 | 第一次处理中，后续返回 409 或复用结果 | 操作正在处理中，请勿重复提交 | 不变或 `adopted` |

事务要求：

- 单条采纳必须使用事务，目标资产创建、来源回写、生成结果状态更新要么全部成功，要么全部失败。
- 批量采纳按条处理，单条失败不能影响其他条，但必须返回失败明细。
- 已采纳幂等命中时，不重复创建目标资产。

批量采纳响应建议：

```json
{
  "success_count": 8,
  "failed_count": 2,
  "deduplicated_count": 1,
  "items": [
    {
      "generated_case_id": 101,
      "status": "adopted",
      "asset_id": 3001,
      "asset_route": "/api-testing/test-cases?caseId=3001"
    },
    {
      "generated_case_id": 102,
      "status": "failed",
      "code": "API_URL_INVALID",
      "message": "接口 URL 不合法，请检查协议和地址"
    }
  ]
}
```

前端批量提示：

- 全部成功：`已确认 8 条接口测试用例`。
- 全部幂等：`所选结果已确认，未重复创建资产`。
- 部分失败：`已确认 8 条，失败 2 条`，并展示失败列表。
- 全部失败：`确认失败，请查看失败原因`，并展示失败列表。

### 16.6 接口测试用例页面异常矩阵

| 异常场景 | 后端行为 | 前端提示 |
| --- | --- | --- |
| 无接口项目 | 返回空列表 | 暂无接口项目，请先创建接口项目 |
| 有项目但无接口用例 | 返回空列表 | 暂无接口测试用例 |
| 搜索无结果 | 返回空列表 | 未找到匹配的接口测试用例 |
| 无权限访问项目 | 403 | 你没有该接口项目的访问权限 |
| 加载列表失败 | 500 或网络错误 | 接口测试用例加载失败，请重试 |
| 新建时 URL 为空 | 400 `VALIDATION_ERROR` | 请填写请求 URL |
| URL 协议非法 | 400 `API_URL_INVALID` | 接口 URL 需以 http:// 或 https:// 开头 |
| Headers 格式错误 | 400 `VALIDATION_ERROR` | 请求头格式不正确，请检查键值对 |
| Body JSON 非法 | 400 `VALIDATION_ERROR` | 请求体 JSON 格式不正确 |
| 断言格式错误 | 400 `VALIDATION_ERROR` | 断言配置不正确，请检查断言类型和期望值 |
| 删除已加入套件的用例 | 409 `RESOURCE_IN_USE` 或二次确认 | 该用例已被测试套件使用，删除后会影响套件 |
| 加入套件时重复选择 | 200 幂等成功 | 已在套件中的用例不会重复添加 |

### 16.7 接口执行异常矩阵

| 异常场景 | 后端行为 | 前端提示 | 是否写入历史 |
| --- | --- | --- | --- |
| URL 为空 | 400 `API_URL_INVALID` | 请填写请求 URL | 否 |
| URL 协议非法 | 400 `API_URL_INVALID` | 接口 URL 需以 http:// 或 https:// 开头 | 否 |
| 环境变量缺失 | 400 `VARIABLE_NOT_FOUND` | 缺少环境变量：变量名 | 是 |
| Auth 类型未支持 | 400 `AUTH_TYPE_UNSUPPORTED` | 当前认证方式暂不支持执行 | 是 |
| 前置脚本非空但未支持 | 400 `SCRIPT_UNSUPPORTED` | 当前暂不支持执行前置脚本 | 是 |
| 后置脚本非空但未支持 | 400 `SCRIPT_UNSUPPORTED` | 当前暂不支持执行后置脚本 | 是 |
| DNS 解析失败 | 400 `API_REQUEST_FAILED` | 接口请求失败，请检查域名或网络 | 是 |
| 连接超时 | 400 `API_REQUEST_TIMEOUT` | 接口请求超时，请检查服务或环境配置 | 是 |
| TLS 证书错误 | 400 `API_REQUEST_FAILED` | HTTPS 证书校验失败，请检查服务证书 | 是 |
| 返回非 JSON 但断言用 JSONPath | 400 或断言失败 | 响应不是 JSON，JSONPath 断言无法执行 | 是 |
| 断言失败 | 200，结果标记失败 | 请求完成，但断言未通过 | 是 |
| 套件中某个用例失败 | 套件继续执行或按配置中断 | 套件执行完成，存在失败用例 | 是 |

历史记录要求：

- 只要真实发起过 HTTP 请求，就必须写入 `RequestHistory`。
- 未发起请求的参数校验失败，不写请求历史。
- 执行失败的历史必须记录 `error_message`。
- 断言失败不是接口调用失败，应记录响应数据和断言结果。

### 16.8 Web/App 自动化采纳异常矩阵

P1 阶段需要覆盖：

| 异常场景 | 后端行为 | 前端提示 |
| --- | --- | --- |
| 未选择 Web 自动化项目 | 400 | 请选择 Web 自动化项目 |
| Web 步骤动作类型不支持 | 400 `STEP_ACTION_UNSUPPORTED` | 存在不支持的 Web 步骤动作，请调整生成结果 |
| Web 元素无法绑定 | 保存草稿，不阻断采纳 | 已保存为草稿，请补齐目标元素后执行 |
| 未选择 App 自动化项目 | 400 | 请选择 App 自动化项目 |
| App `ui_flow` schema 非法 | 400 `APP_UI_FLOW_INVALID` | App UI Flow 格式不正确，请调整生成结果 |
| App 未绑定应用包 | 保存草稿，不阻断采纳 | 已保存为草稿，请补齐应用包后执行 |

### 16.9 用户可见文案规范

提示文案必须符合以下规则：

- 说人话，直接告诉用户缺什么、错在哪、下一步怎么做。
- 不展示开发术语，例如 `serializer invalid`、`KeyError`、`Traceback`、`NoneType`。
- 不展示“功能开发中”，应改为明确状态，例如“当前暂不支持执行前置脚本”。
- 不展示“未知错误”作为唯一信息，必须有兜底动作，例如“请稍后重试或联系管理员”。

推荐提示：

| 场景 | 推荐文案 |
| --- | --- |
| Prompt 缺失 | 未配置“接口测试用例”的用例编写 Prompt，请先到 Prompt 配置中启用对应配置 |
| 目标项目缺失 | 请选择目标项目 |
| 接口集合缺失 | 请选择接口集合，或使用默认集合保存 |
| URL 非法 | 接口 URL 需以 http:// 或 https:// 开头 |
| AI 输出不可解析 | AI 返回内容无法解析，请调整 Prompt 后重试 |
| 字段不满足 schema | AI 返回内容缺少必要字段：字段名 |
| 权限不足 | 你没有该项目的操作权限 |
| 重复采纳 | 该结果已确认，已返回现有资产 |
| 批量部分失败 | 已确认 X 条，失败 Y 条，请查看失败原因 |
| 脚本未支持 | 当前暂不支持执行前置或后置脚本，请清空脚本后再执行 |

## 17. 权限需求

采纳时必须检查目标模块权限：

- 功能测试用例：用户必须有目标测试设计项目权限。
- 接口测试用例：用户必须有目标接口项目权限。
- Web 自动化测试用例：用户必须有目标 Web 自动化项目权限。
- App 自动化测试用例：用户必须有目标 App 自动化项目权限。

禁止：

- 只因为用户能查看生成结果，就允许写入任意自动化项目。
- 前端隐藏按钮代替后端权限校验。

## 18. 来源追踪需求

目标资产需要能追踪来源。

最小来源信息：

```json
{
  "source": "ai_generation_task",
  "task_id": "TASK-xxx",
  "case_id": "CASE-001",
  "case_index": 1,
  "target_type": "api_test_case",
  "source_label": "由 AI 需求分析生成",
  "generated_case_id": 123
}
```

功能测试用例：

- 可继续沿用 `tags` 存储来源信息。

接口、Web、App 自动化用例：

- P0 推荐新增轻量来源字段，或在需求分析模块维护采纳映射表。
- 不建议把来源信息塞进描述字段。

推荐方案：

- 在生成结果侧保存 `adopted_asset_type + adopted_asset_id + adopted_asset_route`。
- 在目标资产侧新增 `source_metadata` JSON 字段，便于列表展示来源。

## 19. 数据兼容需求

### 19.1 旧生成任务

旧任务没有 `target_type` 时：

- 默认视为 `functional_test_case`。
- 页面显示“功能测试用例”。
- 旧采纳逻辑继续可用。

### 19.2 旧接口请求

旧 `ApiRequest` 没有来源信息时：

- 来源展示为“手工创建”或“来源未记录”。
- 不影响执行、编辑、加入套件。

### 19.3 旧路由

旧 `/api-testing/interfaces`：

- 不立即删除。
- 可以隐藏但保留访问。
- 可以重定向到 `/api-testing/test-cases`。
- 不允许直接 404，避免老链接失效。

## 20. 分阶段实施建议

### 20.1 P0-1：接口测试用例闭环

目标：

- 新增接口自动化“接口测试用例”入口。
- 明确 `ApiRequest` 是 P0 接口测试用例资产。
- 修正 API 封装旧路径。
- 单接口执行历史保存断言结果。
- 保持旧接口管理、测试套件、请求历史不回归。

交付物：

- `/api-testing/test-cases` 页面。
- 导航配置更新。
- API 封装修正。
- 请求历史断言结果落库。
- 最小回归验证。

### 20.2 P0-2：AI 生成目标类型

目标：

- 生成入口增加目标类型下拉框。
- Prompt 按目标类型选择。
- 生成任务固化目标类型。
- 生成结果展示目标类型。

交付物：

- `target_type` 字段。
- PromptConfig 目标类型扩展。
- 生成任务创建逻辑扩展。
- 生成结果序列化扩展。

### 20.3 P0-3：接口测试用例采纳

目标：

- AI 生成接口测试用例后，用户确认资产。
- 创建或复用 `ApiRequest`。
- 采纳后进入 `/api-testing/test-cases` 可查看。
- 重复采纳幂等。

交付物：

- 接口测试用例采纳服务。
- 采纳弹窗。
- 来源追踪。
- 跳转目标。

### 20.4 P1：Web/App 自动化采纳

目标：

- 支持 Web 自动化测试用例采纳。
- 支持 App 自动化测试用例采纳。
- 明确草稿状态和不可直接执行条件。

交付物：

- Web 目标 Prompt。
- App 目标 Prompt。
- Web/App 采纳服务。
- 目标模块来源展示。

### 20.5 P1/P2：执行器增强

目标：

- 安全支持接口前置脚本、后置脚本。
- 完善 Auth 类型。
- 完善套件级断言编辑。
- 报告、调度、通知后续向执行中心收敛。

## 21. 详细验收标准

### 21.1 接口自动化 P0 闭环验收

- [ ] 接口自动化侧边栏存在“接口测试用例”子模块。
- [ ] 进入 `/api-testing/test-cases` 不需要刷新页面。
- [ ] 接口测试用例列表能加载已有 `ApiRequest`。
- [ ] 用户能新建接口测试用例。
- [ ] 用户能编辑接口测试用例。
- [ ] 用户能执行单个接口测试用例。
- [ ] 执行后能在请求历史中看到记录。
- [ ] 请求历史中能看到断言结果。
- [ ] 用户能把接口测试用例加入测试套件。
- [ ] 测试套件执行后能生成 `TestExecution`。
- [ ] 旧 `/api-testing/interfaces` 不失效。
- [ ] 快速切换顶部模块和侧边栏时不触发整页刷新。

### 21.2 AI 目标类型验收

- [ ] 生成入口存在“生成目标类型”下拉框。
- [ ] 默认选中“功能测试用例”。
- [ ] 选择“接口测试用例”后，后端使用接口测试用例 writer Prompt。
- [ ] 缺失对应 Prompt 时直接报错，不回退到功能测试 Prompt。
- [ ] 目标类型非法时返回 `TARGET_TYPE_INVALID`，前端提示“生成目标类型不支持，请重新选择”。
- [ ] AI 输出不可解析时任务进入失败态，前端提示“AI 返回内容无法解析，请调整 Prompt 后重试”。
- [ ] AI 输出缺少目标类型必填字段时，前端能展示缺失字段提示。
- [ ] 生成任务详情显示目标类型。
- [ ] 生成结果列表显示目标类型。
- [ ] 任务恢复后仍显示创建时的目标类型。

### 21.3 接口测试用例采纳验收

- [ ] 接口测试用例生成结果点击确认后弹出接口项目和集合选择。
- [ ] 未选择接口项目时不能提交。
- [ ] 未选择集合时按规则创建或复用默认集合。
- [ ] 采纳成功后创建 `ApiRequest`。
- [ ] 采纳成功后生成结果状态变为已采纳。
- [ ] 采纳成功后返回目标资产跳转路径。
- [ ] 跳转到接口测试用例列表后能定位到该用例。
- [ ] 重复采纳同一结果不会重复创建 `ApiRequest`。
- [ ] 已弃用结果再次采纳时返回 `RESULT_ALREADY_DISCARDED`，前端提示不能再确认资产。
- [ ] 目标接口项目无权限时返回 403，前端提示“你没有该项目的操作权限”。
- [ ] 接口 URL 非法时不创建 `ApiRequest`，前端提示 URL 需要以 `http://` 或 `https://` 开头。
- [ ] 批量采纳部分失败时展示成功数、失败数和失败明细。

### 21.4 功能测试旧流程回归验收

- [ ] 默认功能测试用例生成流程不受影响。
- [ ] 原有功能测试用例采纳仍可创建 `TestCase`。
- [ ] 原有批量采纳仍可用。
- [ ] 原有来源标签和处理状态仍正确。

### 21.5 Web/App 草稿采纳验收

P1 阶段验收：

- [ ] Web 自动化目标结果可采纳为 Web 自动化测试用例草稿。
- [ ] App 自动化目标结果可采纳为 App 自动化测试用例草稿。
- [ ] 无元素、无设备、无应用包时，不伪装成可完整执行。
- [ ] 目标模块列表中能看到 AI 来源。

### 21.6 异常提示验收

- [ ] 所有新增接口错误响应至少包含可展示的 `message`。
- [ ] 新增接口不把 Python 异常栈、数据库异常原文或模型请求详情直接返回前端。
- [ ] 前端字段级错误展示在对应表单项，不只弹全局错误。
- [ ] 操作级错误使用 Element Plus 消息或表单提示，不继续新增 `alert()`。
- [ ] 401 继续走统一认证跳转，不在页面内调用 `window.location.href` 或 `window.location.reload()`。
- [ ] 未知错误有兜底文案：“操作失败，请稍后重试”。
- [ ] “功能开发中”类提示不作为 P0 闭环页面的正式错误提示。

## 22. 验证建议

### 22.1 后端验证

最低验证：

```text
python -m py_compile apps\\api_testing\\models.py
python -m py_compile apps\\api_testing\\serializers.py
python -m py_compile apps\\api_testing\\views.py
python -m py_compile apps\\requirement_analysis\\models.py
python -m py_compile apps\\requirement_analysis\\serializers.py
python -m py_compile apps\\requirement_analysis\\views.py
```

接口级验证：

- 创建目标类型为接口测试用例的生成任务。
- 缺失 Prompt 时确认返回 400。
- 使用非法 `target_type` 创建任务，确认返回 `TARGET_TYPE_INVALID`。
- 模拟 AI 输出缺少接口用例必填字段，确认返回 `AI_OUTPUT_SCHEMA_INVALID`。
- 采纳接口测试用例生成结果。
- 重复采纳同一生成结果。
- 采纳已弃用生成结果，确认返回 `RESULT_ALREADY_DISCARDED`。
- 无权限采纳到接口项目，确认返回 403。
- 采纳非法 URL 的接口用例，确认不会创建 `ApiRequest`。
- 批量采纳包含成功和失败项，确认返回成功数、失败数和逐条明细。
- 执行采纳后的 `ApiRequest`。
- 执行 URL 为空或协议非法的接口用例，确认不写请求历史。
- 执行真实发起但超时或断言失败的接口用例，确认写入请求历史和错误/断言结果。
- 查询请求历史断言结果。

### 22.2 前端验证

最低验证：

```text
cd frontend && cmd /c npm run build
```

页面级验证：

- 需求分析页切换目标类型。
- 生成任务详情展示目标类型。
- Prompt 缺失时展示可理解错误提示，并能引导用户去配置。
- 生成结果页采纳接口测试用例。
- 采纳弹窗未选择目标项目时字段级提示。
- 接口 URL 非法时字段级提示。
- 批量采纳部分失败时展示失败明细。
- 接口测试用例列表展示 AI 采纳用例。
- 接口测试用例列表覆盖无项目、无用例、搜索无结果、加载失败、无权限状态。
- 顶部大模块快速切换后点击接口测试用例子模块，页面正常切换。
- 几秒内快速切换接口自动化多个子模块，最终停留最后点击目标。

### 22.3 回归验证

必须覆盖：

- 功能测试用例生成和采纳旧流程。
- 接口自动化项目管理。
- 接口测试用例单执行。
- 请求历史。
- 测试套件执行。
- Web/App 自动化原有测试用例列表不报错。

## 23. 风险与控制

### 23.1 跨模块项目模型不一致

风险：

- 测试设计项目、接口项目、Web 自动化项目、App 自动化项目不是同一个模型。

控制：

- 采纳时按目标类型选择目标项目。
- 不默认拿测试设计项目 ID 去写自动化项目。

### 23.2 AI 输出不可控

风险：

- AI 可能输出缺字段、错字段、不可执行 URL、无效步骤。

控制：

- 每个目标类型都有 schema 校验。
- 校验失败不落库。
- Web/App 生成资产默认草稿。

### 23.3 旧流程回归

风险：

- 功能测试用例生成是现有主链，不能被新目标类型破坏。

控制：

- 默认目标类型为功能测试用例。
- 旧任务缺失 `target_type` 时按功能测试处理。
- 功能采纳接口保持兼容。

### 23.4 接口用例与接口请求命名冲突

风险：

- 后端叫 `ApiRequest`，前端叫“接口测试用例”，开发时容易混淆。

控制：

- P0 文档明确：`ApiRequest` 是接口测试用例的技术承载。
- 前端 API 封装可使用 `ApiTestCase` 命名，但注释说明底层资源是 `/api-testing/requests/`。

### 23.5 脚本执行安全

风险：

- 前置/后置脚本如果直接执行，会带来安全风险。
- 如果继续静默忽略，又会造成假闭环。

控制：

- P0 不做不安全脚本执行。
- 非空脚本在未支持时直接报错或禁用入口。
- P1 再设计安全脚本沙箱。

## 24. 待确认项

以下问题需要在进入 TDD 前确认：

1. `/api-testing/interfaces` 是否保留在侧边栏，还是只保留为隐藏兼容路由？
2. P0 是否接受 `ApiRequest` 作为接口测试用例技术承载，不新增 `ApiTestCase` 表？
3. 接口测试用例列表是新建列表页，还是先复用当前接口管理工作区并调整文案？
4. 接口前置/后置脚本 P0 是直接报错、隐藏入口，还是必须实现安全执行？
5. Web/App 自动化采纳是否放入 P1，P0 只先打通功能和接口两类？
6. AI 生成接口测试用例时，接口项目和集合是在生成前选择，还是采纳时选择？
7. Prompt 配置是否允许旧 Prompt 自动复制为功能测试用例 Prompt？

## 25. 推荐默认决策

如无额外要求，建议默认采用以下决策：

1. P0 不新增 `ApiTestCase` 表，使用 `ApiRequest` 承载接口测试用例。
2. 新增正式路由 `/api-testing/test-cases`。
3. 旧 `/api-testing/interfaces` 保留为隐藏兼容路由。
4. P0 先完成“功能测试用例 + 接口测试用例”的 AI 生成和采纳闭环。
5. Web/App 自动化采纳进入 P1，P0 先完成字段设计和 Prompt 类型扩展，不强行落库。
6. Prompt 缺失时直接报错，不静默回退。
7. 接口脚本未支持安全执行前，不允许静默忽略。

## 26. 后续 TDD 拆分建议

进入 TDD 后，建议按以下测试包拆分：

- `TDD-API-001`：接口测试用例列表和旧接口管理兼容。
- `TDD-API-002`：单接口执行、断言结果落库、请求历史展示。
- `TDD-AI-001`：生成目标类型选择和任务固化。
- `TDD-AI-002`：Prompt 按目标类型选择和缺失报错。
- `TDD-AI-003`：接口测试用例采纳、幂等和跳转。
- `TDD-REG-001`：功能测试用例旧生成采纳流程回归。
- `TDD-NAV-001`：顶部模块和侧边栏快速切换回归。

## 27. 一句话结论

P0 的关键不是“加一个下拉框”，而是先把接口自动化的接口测试用例资产定义清楚，再让 AI 生成结果按目标类型进入对应模块。接口自动化 P0 建议用 `ApiRequest` 承载“接口测试用例”，新增清晰的“接口测试用例”子模块，并把 AI 采纳后的接口资产落到这个列表中，形成从需求生成到自动化执行的闭环。

# 接口自动化 P0-2 AI 生成目标类型 Spec/SDD

更新时间：2026-06-18

状态：Spec/SDD 草案，已补充接口用例 / 测试套件拆分与 AI 生成链路红线，等待确认后进入 TDD 修订与确认

关联文档：

- `docs/api-automation/api-automation-testcase-loop-ai-generation-spec.md`
- `docs/api-automation/api-automation-p0-1-testcase-loop-tdd.md`
- `docs/api-automation/api-automation-p0-1-testcase-loop-vdd.md`
- `docs/api-automation/api-automation-p0-2-ai-target-type-tdd.md`

## 1. 背景

P0-1 已经把接口自动化自身闭环补起来：

- `/api-testing/test-cases` 已成为正式“接口测试用例”入口。
- P0 阶段 `ApiRequest` 冻结为接口测试用例技术承载。
- 旧 `/api-testing/interfaces` 只保留隐藏兼容入口。
- 单接口执行已经能把断言结果写入请求历史。

但 AI 需求分析生成链路仍然主要面向“功能测试用例”。用户提出的新需求是：生成前可以选择目标类型，例如功能测试用例、接口测试用例、Web 自动化测试用例、App 自动化测试用例；选择哪个类型，就使用哪个类型对应 Prompt；生成结果后再进入对应模块。

因此 P0-2 需要先解决“生成目标类型”这件事。它不是采纳落库阶段，而是让生成任务从创建开始就知道自己要生成哪类用例，并且 Prompt、任务记录、详情页、结果页都能保持一致。

本轮新增确认的产品口径：

- 接口测试用例仍然是原子资产，用 `ApiRequest` 承接。
- 测试套件仍然是编排资产，用 `TestSuite + TestSuiteRequest` 承接。
- AI 生成接口测试用例时只生成 `ApiRequest` 兼容字段，不直接生成测试套件。
- 后续用户可从接口测试用例列表把用例加入 / 导入测试套件。
- **当前 AI 生成测试用例的既有逻辑严禁重写，只允许把目标类型、Prompt 选择和字段展示契约套用到现有链路上。**

## 2. 本阶段目标

P0-2 只完成 AI 生成链路中的目标类型能力：

- 在 AI 需求分析生成入口增加“生成目标类型”下拉框。
- 默认目标类型为“功能测试用例”，旧功能测试生成流程不受影响。
- 创建生成任务时把 `target_type` 固化到任务对象。
- Prompt 选择改为按 `prompt_type + target_type` 查找。
- 选择接口测试用例时必须使用接口测试用例 Prompt。
- 缺少对应目标类型 Prompt 时直接报错，不静默回退到功能测试 Prompt。
- 任务详情页展示任务固化的目标类型。
- 生成结果页展示目标类型。
- 非功能目标类型暂不走旧功能用例采纳链路，避免接口用例被误写进功能测试用例资产。
- 接口测试用例生成结果只按 `ApiRequest` 原子用例字段展示，不把 `TestSuite` 套件字段混入 AI 生成结果。
- 在不改写现有 AI 生成、流式处理、自动评审、取消、轮询和结果处理主链的前提下，套用目标类型与字段契约。

## 3. 非目标

P0-2 明确不做：

- 不实现接口测试用例采纳到 `ApiRequest`，该内容进入 P0-3。
- 不实现 Web/App 自动化用例采纳落库，该内容进入 P1。
- 不新增 `ApiTestCase` 数据表。
- 不重构整个 AI 生成链路 UI。
- 不重构现有功能测试用例采纳服务。
- 不改变 P0-1 冻结的 `/api-testing/test-cases` 资产列表入口。
- 不新增绕开现有 AI 模型配置、Prompt 配置和生成配置的并行调用入口。
- 不使用整页刷新兜底任务状态、目标类型切换或结果页刷新。
- 不重写当前 AI 测试用例生成逻辑、生成任务状态机、流式输出逻辑、自动评审链路、取消逻辑、轮询恢复逻辑和既有结果采纳主链。
- 不让 AI 直接生成 `TestSuite` 或 `TestSuiteRequest`。
- 不把接口测试用例 AI 结果直接写入测试套件；进入套件的动作放到接口测试用例资产列表或 P0-3/P1 后续链路承接。

## 4. 当前代码事实

### 4.1 后端事实

- `apps.requirement_analysis.models.PromptConfig` 当前只有 `prompt_type`，没有 `target_type`。
- `PromptConfig.get_active_config(prompt_type)` 当前只按 `prompt_type` 查活跃 Prompt。
- `apps.requirement_analysis.models.TestCaseGenerationTask` 当前没有 `target_type`。
- `TestCaseGenerationTaskViewSet.generate()` 当前创建任务时只选择 writer/reviewer 模型和 writer/reviewer Prompt，没有目标类型概念。
- 现有结果采纳逻辑主要写入 `apps.testcases.TestCase`，即功能测试用例。
- `apps.api_testing.models.ApiRequest` 已在 P0-1 冻结为接口测试用例技术承载，但 AI 采纳到 `ApiRequest` 尚未实现。

### 4.2 前端事实

- `RequirementAnalysisView.vue` 是当前 AI 生成入口。
- `TaskDetail.vue` 是生成任务详情页。
- `GeneratedTestCaseList.vue` 是生成结果批次页，并承接功能测试用例采纳入口。
- 结果页现有采纳弹窗仍按功能测试用例字段组织。
- 现有页面中存在历史直接 `api.get/post` 调用；P0-2 新增或触碰的请求应尽量收口到 `frontend/src/api/requirement-analysis.js`，但不在本阶段强行重构所有旧调用。

### 4.3 字段不匹配事实

当前存在一个必须在 P0-2 先解决的字段契约问题：

- AI 生成结果解析器当前偏功能测试用例字段，例如 `scenario`、`precondition`、`steps`、`expected`。
- 接口自动化真实技术承载是 `ApiRequest`，核心字段是 `name`、`description`、`method`、`url`、`headers`、`params`、`body`、`auth`、`pre_request_script`、`post_request_script`、`assertions`、`collection`。
- 接口测试用例列表页当前展示字段是“用例名称、方法、URL、所属集合、断言数、更新时间、操作”。
- 生成结果页当前详情和采纳弹窗仍按功能测试用例字段展示。

如果 P0-2 只加 `target_type`，但不定义接口测试用例结果字段，后续会出现两个问题：

- 接口测试用例生成结果在结果页仍像功能测试用例，用户无法检查 method、URL、请求头、请求体、断言等接口核心信息。
- P0-3 采纳到 `ApiRequest` 时没有稳定字段来源，只能临时猜字段，容易把 AI 结果错误写入接口用例资产。

因此 P0-2 必须冻结“接口测试用例 AI 结果字段契约”和“结果页展示字段契约”。P0-2 不负责落库到 `ApiRequest`，但必须让生成后的接口测试用例结果已经按 `ApiRequest` 的字段心智展示。

### 4.4 接口测试用例与测试套件拆分口径

接口自动化模块内必须继续区分两个对象：

| 对象 | 当前承接 | 职责 | 与 AI 生成的关系 |
| --- | --- | --- | --- |
| 接口测试用例 | `ApiRequest` | 单个接口请求、参数、请求体、认证、断言、脚本、单次执行历史 | P0-2 只生成这种原子用例草稿 |
| 测试套件 | `TestSuite + TestSuiteRequest` | 组织多个接口测试用例，控制执行顺序、启停、套件执行和报告 | 不由 P0-2 AI 直接生成，后续从用例列表加入 / 导入 |

这样拆分后，AI 生成接口测试用例时不需要同时兼顾“套件结构”和“用例字段”。Prompt 可以固定要求输出 `ApiRequest` 兼容字段，生成结果页也可以固定展示 `name/method/url/headers/params/body/assertions` 等接口用例字段。

P0-3 采纳入库时的正确流向是：

```text
AI 生成结果 normalized_payload -> 用户选择 ApiProject + ApiCollection -> 创建 ApiRequest -> 用户再按需加入 TestSuite
```

错误流向是：

```text
AI 生成结果 -> 直接创建 TestSuite / TestSuiteRequest
```

### 4.5 现有 AI 生成链路不可改动红线

P0-2 的实现必须采用“外层套用”方式：

- 可以增加 `target_type` 字段。
- 可以让 Prompt 按 `prompt_type + target_type` 选择。
- 可以在结果序列化或展示适配层补 `normalized_payload`、`display_payload`、`structure_errors`、`structure_warnings`。
- 可以针对 `api_test_case` 增加结果展示列和详情弹窗。
- 不可以重写现有 AI 生成任务创建、模型调用、流式返回、取消、自动评审、轮询恢复和功能测试采纳链路。
- 不可以新增一条绕开现有配置体系的模型调用入口。
- 不可以为了接口测试用例生成，把原功能测试用例生成的字段解析和采纳逻辑整体替换掉。

大白话口径：

```text
这次不是把 AI 生成系统推倒重做。
只是让原来的 AI 生成系统多带一个“我要生成哪类用例”的标签，
然后按这个标签选 Prompt、展示字段，并保护旧采纳入口不误用。
```

## 5. 目标类型定义

统一字段名：

```text
target_type
```

统一枚举：

| value | label | P0-2 行为 |
| --- | --- | --- |
| `functional_test_case` | 功能测试用例 | 默认值；完整保留旧生成和旧采纳链路 |
| `api_test_case` | 接口测试用例 | 支持目标类型、Prompt、任务固化、结果展示；采纳入库进入 P0-3 |
| `web_automation_test_case` | Web 自动化测试用例 | 支持目标类型和 Prompt 预留；采纳入库进入 P1 |
| `app_automation_test_case` | App 自动化测试用例 | 支持目标类型和 Prompt 预留；采纳入库进入 P1 |

旧数据兼容规则：

- 旧任务没有 `target_type` 时按 `functional_test_case` 处理。
- 旧 Prompt 没有 `target_type` 时迁移为 `functional_test_case`。
- 后端序列化统一返回 `target_type` 和 `target_type_label`。

## 6. 后端方案

### 6.0 套用现有生成链路的实现原则

后端实现必须把现有 AI 生成链路当成主链保留：

- `TestCaseGenerationTaskViewSet.generate()` 仍然是创建生成任务的入口。
- 现有 writer / reviewer 模型选择、Prompt 渲染、任务状态更新、取消检查和自动评审流程继续复用。
- P0-2 只在任务创建前增加目标类型校验，在 Prompt 查询时增加 `target_type` 过滤，在任务 / 结果响应中增加目标类型和接口用例字段适配。
- 如果需要解析接口用例字段，应优先做成目标类型分支下的轻量归一化适配，不要改掉功能测试用例原解析路径。
- 所有旧功能测试任务在不传 `target_type` 时必须继续按原行为执行。

### 6.1 新增目标类型常量

建议在 `apps.requirement_analysis` 内新增可复用常量或工具：

```text
FUNCTIONAL_TEST_CASE = functional_test_case
API_TEST_CASE = api_test_case
WEB_AUTOMATION_TEST_CASE = web_automation_test_case
APP_AUTOMATION_TEST_CASE = app_automation_test_case
```

同时提供：

- 合法值集合。
- `value -> label` 映射。
- 校验函数。
- label 获取函数。

原因：

- 避免模型、序列化器、视图和前端协议里到处散写字符串。
- 后续 P0-3/P1 继续复用。

### 6.2 PromptConfig 扩展

新增字段：

```text
target_type
```

建议属性：

- 类型：`CharField`
- 默认值：`functional_test_case`
- choices：目标类型枚举
- 旧数据迁移默认：`functional_test_case`

活跃 Prompt 查询规则从：

```text
get_active_config(prompt_type)
```

调整为：

```text
get_active_config(prompt_type, target_type='functional_test_case')
```

强约束：

- 查询必须同时匹配 `prompt_type` 和 `target_type`。
- `api_test_case` 找不到 writer Prompt 时直接报错。
- 开启自动评审时，`api_test_case` 找不到 reviewer Prompt 也直接报错。
- 不允许接口测试用例静默使用功能测试用例 Prompt。

多活跃 Prompt 处理：

- P0-2 至少在应用层保证同一 `prompt_type + target_type` 启用时选择稳定。
- 推荐启用某个 Prompt 时，自动关闭同一 `prompt_type + target_type` 下其他活跃 Prompt。
- 不要求一次性加复杂唯一索引；如果加约束，必须避免影响旧数据迁移。

### 6.3 TestCaseGenerationTask 扩展

新增字段：

```text
target_type
```

建议属性：

- 类型：`CharField`
- 默认值：`functional_test_case`
- choices：目标类型枚举
- 旧数据迁移默认：`functional_test_case`

任务创建时必须固化：

- `target_type`
- writer model
- reviewer model
- writer Prompt
- reviewer Prompt
- output mode

任务运行、轮询、恢复时都以任务表中的 `target_type` 为准，不读取前端当前下拉框值。

### 6.4 生成任务创建接口

请求新增字段：

```json
{
  "title": "登录接口测试生成",
  "requirement_text": "登录接口需要覆盖成功和失败场景",
  "target_type": "api_test_case"
}
```

兼容规则：

- 不传 `target_type` 时默认 `functional_test_case`。
- 传空字符串时按非法参数处理，不默认为功能测试。
- 传非法值时返回 400，不创建任务。

非法目标类型响应建议：

```json
{
  "error": "生成目标类型不支持，请重新选择",
  "code": "TARGET_TYPE_INVALID"
}
```

Prompt 缺失响应建议：

```json
{
  "error": "未配置“接口测试用例”的用例编写 Prompt，请先到 Prompt 配置中启用对应配置",
  "code": "PROMPT_CONFIG_MISSING"
}
```

### 6.5 生成结果结构

P0-2 不新增独立结果表字段，但接口响应必须稳定带出：

```json
{
  "target_type": "api_test_case",
  "target_type_label": "接口测试用例",
  "normalized_payload": {},
  "structure_errors": []
}
```

最低要求：

- 任务详情接口返回 `target_type` 和 `target_type_label`。
- 任务进度接口返回 `target_type` 和 `target_type_label`。
- 结果列表中的每个生成结果注入 `target_type` 和 `target_type_label`。
- 对接口测试用例结果做最小归一化，不能让页面因为字段类型异常崩溃。

### 6.6 接口测试用例输出最小结构

当 `target_type=api_test_case` 时，目标结构至少包含：

```json
{
  "case_id": "API-001",
  "name": "登录接口验证",
  "description": "验证用户名密码登录接口",
  "method": "POST",
  "url": "/api/login",
  "headers": {},
  "params": {},
  "body": {},
  "auth": {},
  "assertions": [],
  "pre_request_script": "",
  "post_request_script": ""
}
```

P0-2 校验口径：

- `name` 必填。
- `method` 必须是 `GET/POST/PUT/PATCH/DELETE/HEAD/OPTIONS` 之一。
- `url` 必须非空。
- 完整 URL 必须以 `http://` 或 `https://` 开头。
- `/api/login` 这种路径草稿允许展示，但要标记“待补全基础地址”。
- `headers`、`params`、`body`、`auth` 尽量归一化为对象或列表。
- `assertions` 非数组时归一化为空数组，并记录结构错误。
- `pre_request_script`、`post_request_script` 只作为文本保存和展示，P0-2 不执行。

### 6.7 接口测试用例字段桥接契约

P0-2 必须把接口测试用例结果归一化为一个稳定的中间结构，供结果页展示和 P0-3 采纳复用。

推荐响应字段：

```json
{
  "target_type": "api_test_case",
  "target_type_label": "接口测试用例",
  "case_id": "API-001",
  "normalized_payload": {
    "case_id": "API-001",
    "name": "登录接口成功返回 token",
    "description": "验证账号密码正确时登录接口返回 token",
    "method": "POST",
    "url": "/api/login",
    "headers": [
      {
        "key": "Content-Type",
        "value": "application/json",
        "enabled": true,
        "type": "text"
      }
    ],
    "params": [],
    "body": {
      "type": "json",
      "data": {
        "username": "demo",
        "password": "password"
      }
    },
    "auth": {},
    "assertions": [
      {
        "name": "状态码为 200",
        "type": "status_code",
        "expected": 200
      }
    ],
    "pre_request_script": "",
    "post_request_script": ""
  },
  "display_payload": {
    "name": "登录接口成功返回 token",
    "method": "POST",
    "url": "/api/login",
    "assertion_count": 1,
    "request_summary": "POST /api/login",
    "body_type": "json",
    "validation_label": "字段完整，采纳前需选择接口集合"
  },
  "structure_errors": [],
  "structure_warnings": [
    "URL 为相对路径，采纳或执行前需要补齐基础地址"
  ]
}
```

字段映射必须按下表冻结：

| AI 归一化字段 | `ApiRequest` 字段 | 接口测试用例列表展示 | 生成结果页展示 |
| --- | --- | --- | --- |
| `name` | `name` | 用例名称 | 用例名称 |
| `description` | `description` | 默认不展示 | 描述 |
| `method` | `method` | 方法 | 方法标签 |
| `url` | `url` | URL | URL |
| `headers` | `headers` | 默认不展示 | 请求头摘要 / 详情 |
| `params` | `params` | 默认不展示 | URL 参数摘要 / 详情 |
| `body` | `body` | 默认不展示 | 请求体类型和内容摘要 |
| `auth` | `auth` | 默认不展示 | 认证信息摘要 |
| `assertions` | `assertions` | 断言数 | 断言列表 |
| `pre_request_script` | `pre_request_script` | 默认不展示 | 前置脚本是否存在 |
| `post_request_script` | `post_request_script` | 默认不展示 | 后置脚本是否存在 |
| P0-3 采纳时选择 | `collection` | 所属集合 | P0-2 标记“待采纳时选择集合” |

归一化规则：

- `headers` 和 `params` 在展示层统一为数组格式，兼容接口调试工作区现有 `KeyValueEditor` 形态。
- `headers` 和 `params` 如果来自对象格式，后端或前端适配层要转换为 `{ key, value, enabled, type }[]`。
- `body` 必须统一为 `{ type, data }` 结构；无法识别时使用 `{ type: "raw", data: 原始内容 }` 并记录 warning。
- `assertions` 必须统一为接口执行器支持的断言格式。
- `collection` 不由 AI 生成结果决定，P0-3 采纳时由用户选择或按规则创建默认集合。

断言格式必须兼容当前接口执行器：

| 断言类型 | 必填字段 | 说明 |
| --- | --- | --- |
| `status_code` | `expected` | 期望 HTTP 状态码 |
| `response_time` | `expected` | 期望最大响应时间，单位 ms |
| `contains` | `expected` | 响应正文包含文本 |
| `json_path` | `json_path`、`expected` | JSONPath 值断言 |
| `header` | `header_name`、`expected_value` | 响应头断言 |
| `equals` | `expected` | 响应正文全文匹配 |

P0-2 的关键要求：

- 生成结果页不能继续用 `scenario/precondition/steps/expected` 展示接口测试用例。
- 接口测试用例结果必须展示 `name/method/url/assertions` 这些与接口用例资产一致的字段。
- P0-3 采纳到 `ApiRequest` 时必须复用 `normalized_payload`，不能重新从页面文案里反推字段。
- `normalized_payload` 是后续采纳 `ApiRequest` 的稳定数据源，不是测试套件结构，也不包含 `suite_id`、`suite_name`、`suite_order` 等套件编排字段。

## 7. 前端方案

### 7.1 生成入口

`RequirementAnalysisView.vue` 增加“生成目标类型”下拉框。

交互规则：

- 默认选中“功能测试用例”。
- 手动输入和文档生成共用同一个目标类型。
- 任务生成中下拉框禁用，不能中途修改。
- 下拉框切换后说明文案同步变化。
- 创建任务请求必须带 `target_type`。
- 恢复未完成任务时，显示任务固化的目标类型，不用当前下拉框覆盖任务。

说明文案建议：

| 类型 | 文案 |
| --- | --- |
| 功能测试用例 | 生成测试设计模块可管理和采纳的功能测试用例 |
| 接口测试用例 | 生成接口自动化用例草稿，后续可确认进入接口测试用例列表 |
| Web 自动化测试用例 | 生成 Web 自动化用例草稿，后续需要补齐元素和步骤参数 |
| App 自动化测试用例 | 生成 App 自动化用例草稿，后续需要补齐设备、应用包和 UI 流程参数 |

### 7.2 Prompt 配置页

`PromptConfig.vue` 需要展示和编辑 `target_type`：

- 列表卡片展示目标类型。
- 新增/编辑弹窗增加目标类型下拉框。
- 默认目标类型为“功能测试用例”。
- 加载默认 Prompt 时创建功能测试用例 Prompt，不自动创建接口/Web/App Prompt。
- 用户需要为接口测试用例单独创建并启用 writer/reviewer Prompt。

### 7.3 任务详情页

`TaskDetail.vue` 需要展示：

- `target_type_label`
- writer Prompt 名称
- reviewer Prompt 名称
- 目标类型说明

页面必须表达“这是任务创建时固化的目标类型”，不能展示当前生成入口下拉框值。

### 7.4 生成结果页

`GeneratedTestCaseList.vue` 需要展示：

- 任务目标类型列或标签。
- 目标类型说明。
- 每条结果的目标类型。

接口测试用例结果不能复用功能测试用例表格。页面必须按目标类型切换展示列：

| 目标类型 | 结果页核心列 |
| --- | --- |
| `functional_test_case` | 用例编号、测试场景、前置条件、步骤、预期结果、优先级、处理状态 |
| `api_test_case` | 用例编号、用例名称、方法、URL、断言数、结构状态、处理状态 |
| `web_automation_test_case` | 用例编号、用例名称、步骤数、元素绑定状态、处理状态 |
| `app_automation_test_case` | 用例编号、用例名称、UI Flow 摘要、应用包绑定状态、处理状态 |

接口测试用例详情弹窗必须展示：

- 用例名称。
- 描述。
- 请求方法。
- URL。
- Headers。
- Params。
- Body。
- Auth。
- Assertions。
- 前置脚本和后置脚本是否存在。
- 结构错误和结构警告。

采纳入口规则：

- `functional_test_case`：继续显示原功能测试用例采纳入口。
- `api_test_case`：P0-2 不显示旧功能采纳弹窗；按钮应禁用或隐藏，并提示“接口测试用例确认入库将在 P0-3 开启”。
- `web_automation_test_case`：禁用或隐藏采纳入口，并提示后续进入 P1。
- `app_automation_test_case`：禁用或隐藏采纳入口，并提示后续进入 P1。

P0-2 默认采用“禁用并展示提示”，而不是让按钮消失：

- 用户能知道这批结果为什么暂时不能确认入库。
- 避免用户误以为结果页加载异常。
- 后续 P0-3 开放接口测试用例采纳时，可以在同一位置替换为正式采纳入口。

这样做的原因：

- P0-2 还没有接口采纳服务。
- 如果不拦截，接口测试用例结果会被旧功能采纳弹窗误写入功能测试资产，造成数据污染。

## 8. 异常场景与用户提示

| 场景 | 后端行为 | 前端提示 |
| --- | --- | --- |
| 未传 `target_type` | 默认 `functional_test_case` | 不提示，旧流程兼容 |
| `target_type` 为空字符串 | 400 | 请选择生成目标类型 |
| `target_type` 非法 | 400 `TARGET_TYPE_INVALID` | 生成目标类型不支持，请重新选择 |
| 缺 writer Prompt | 400 `PROMPT_CONFIG_MISSING` | 未配置对应目标类型的用例编写 Prompt，请先到 Prompt 配置中启用 |
| 开启自动评审但缺 reviewer Prompt | 400 `PROMPT_CONFIG_MISSING` | 未配置对应目标类型的用例评审 Prompt，请先到 Prompt 配置中启用 |
| 同一类型多个活跃 Prompt | 启用时自动收敛或稳定选择最新 | 页面展示当前实际活跃 Prompt |
| AI 输出不可解析 | 任务失败或结果标记结构错误 | AI 返回内容无法解析，请调整 Prompt 后重试 |
| 接口用例缺少 `method` | 结构错误 | AI 返回内容缺少请求方法 |
| 接口用例缺少 `url` | 结构错误 | AI 返回内容缺少请求 URL |
| 接口用例字段仍是功能用例字段 | 结构错误或归一化失败 | AI 返回内容不是接口测试用例格式，请检查 Prompt |
| 接口用例断言格式不支持 | 记录结构错误或 warning | 存在不支持的接口断言，请调整 Prompt |
| 非功能目标点击旧采纳 | 后端拒绝或前端禁用 | 当前类型暂未开放确认入库，请等待下一阶段 |
| 任务运行中切换下拉框 | 前端禁用 | 不允许修改运行中任务的目标类型 |

错误提示要求：

- 不展示 Python 异常栈。
- 不展示 `NoneType`、`KeyError`、`serializer invalid` 这类开发术语。
- 页面提示要告诉用户缺什么、应该去哪里补。
- 不新增原生 `alert()`。

## 9. 兼容与回归

功能测试旧链路必须保持：

- 默认生成目标仍是功能测试用例。
- 旧 Prompt 数据迁移为功能测试用例 Prompt。
- 旧生成任务展示为功能测试用例。
- 原功能测试生成、结果展示、单条采纳、批量采纳继续可用。
- 原来源标签、处理状态、幂等逻辑不回归。

接口自动化 P0-1 必须保持：

- `/api-testing/test-cases` 不变。
- `ApiRequest` 仍是接口测试用例技术承载。
- `/api-testing/interfaces` 仍为隐藏兼容入口。
- 接口测试用例列表、调试工作区、请求历史、加入套件不受 P0-2 影响。

导航和 SPA 稳定性必须保持：

- 不新增 `window.location.reload()`。
- 不新增整页跳转兜底。
- 表单保留 `@submit.prevent`。
- 原生按钮保留显式 `type`。

## 10. 受影响文件范围

预计后端文件：

- `apps/requirement_analysis/models.py`
- `apps/requirement_analysis/serializers.py`
- `apps/requirement_analysis/views.py`
- `apps/requirement_analysis/admin.py`
- `apps/requirement_analysis/migrations/*`
- 可选：`apps/requirement_analysis/target_types.py`

预计前端文件：

- `frontend/src/api/requirement-analysis.js`
- `frontend/src/views/requirement-analysis/RequirementAnalysisView.vue`
- `frontend/src/views/requirement-analysis/PromptConfig.vue`
- `frontend/src/views/requirement-analysis/TaskDetail.vue`
- `frontend/src/views/requirement-analysis/GeneratedTestCaseList.vue`

预计文档文件：

- `docs/api-automation/api-automation-p0-2-ai-target-type-tdd.md`
- P0-2 完成后新增 VDD
- `docs/project-memory/current_phase.md`
- `docs/project-memory/decision_log.md`
- `docs/project-memory/module_memory.md`
- `docs/project-memory/task_handoff.md`
- `docs/project-memory/error_prevention_log.md`
- `docs/project-memory/dialogue_bootstrap.md`
- `更新日志.md`

## 11. 验收标准

P0-2 完成时必须满足：

- [ ] 生成入口存在“生成目标类型”下拉框。
- [ ] 默认值为“功能测试用例”。
- [ ] 任务创建接口支持 `target_type`。
- [ ] 不传 `target_type` 时旧功能测试流程兼容。
- [ ] 传非法 `target_type` 时返回 400 且不创建任务。
- [ ] `PromptConfig` 支持目标类型。
- [ ] Prompt 查询按 `prompt_type + target_type` 选择。
- [ ] 接口测试用例缺 writer Prompt 时直接报错。
- [ ] 开启自动评审且缺 reviewer Prompt 时直接报错。
- [ ] 任务详情页展示目标类型。
- [ ] 生成结果页展示目标类型。
- [ ] 接口测试用例生成结果按 `name/method/url/assertions` 等接口字段展示，不复用功能测试用例表格。
- [ ] 接口测试用例生成结果包含可供 P0-3 采纳复用的 `normalized_payload`。
- [ ] 接口测试用例结果中的 `headers/params/body/assertions` 类型异常时不会导致页面崩溃。
- [ ] 非功能目标类型不会误走功能测试用例采纳。
- [ ] 接口测试用例结果不包含测试套件编排字段，不直接生成或修改 `TestSuite` / `TestSuiteRequest`。
- [ ] 现有 AI 生成逻辑未被重写，只是套用目标类型、Prompt 选择和结果字段适配。
- [ ] 功能测试旧采纳流程不回归。
- [ ] 后端编译通过。
- [ ] 数据迁移计划可解释，旧数据默认功能测试用例。
- [ ] 前端构建通过。
- [ ] 不新增整页刷新兜底。

## 12. 验证建议

后端最低验证：

```text
python -m py_compile apps\requirement_analysis\models.py
python -m py_compile apps\requirement_analysis\serializers.py
python -m py_compile apps\requirement_analysis\views.py
```

迁移验证：

```text
python manage.py makemigrations requirement_analysis
python manage.py migrate --plan
```

前端最低验证：

```text
cd frontend && cmd /c npm run build
```

静态检查：

```text
git diff --check
```

页面验证：

- 默认功能测试生成。
- 接口测试目标类型生成。
- 缺接口 Prompt 报错。
- 任务详情展示目标类型。
- 结果页展示目标类型。
- 非功能目标类型不出现旧功能采纳误入口。
- 快速切换顶部模块和侧边栏不触发整页刷新。

## 13. 回退方式

如果 P0-2 出现不可接受问题，按以下顺序止损：

1. 前端隐藏目标类型下拉框，只发送或默认 `functional_test_case`。
2. 后端保留字段和迁移，生成逻辑只开放 `functional_test_case`。
3. Prompt 查询保留按 `target_type` 的新字段，但只要求功能测试 Prompt 可用。
4. 保持 P0-1 `/api-testing/test-cases` 不回退。

禁止使用以下方式回退：

- 删除已应用迁移来“恢复”数据库。
- 用 `window.location.reload()` 兜底任务状态。
- 让接口测试用例静默回退功能测试 Prompt。
- 让接口测试用例结果误采纳为功能测试用例。

## 14. 待确认项

进入 TDD 修订前需要确认：

1. P0-2 是否只做目标类型、Prompt、任务固化、展示与非功能采纳保护？
2. 接口测试用例采纳到 `ApiRequest` 是否明确放入 P0-3？
3. Web/App 自动化采纳是否明确放入 P1？
4. Prompt 缺失是否按“直接报错，不回退”执行？
5. Prompt 配置页是否需要在 P0-2 同步增加目标类型字段？
6. 非功能目标结果页的旧采纳按钮，是隐藏还是禁用并展示提示？

## 15. 下一步

确认本 Spec/SDD 后，再修订并确认：

```text
docs/api-automation/api-automation-p0-2-ai-target-type-tdd.md
```

TDD 确认后，才能进入代码实现。

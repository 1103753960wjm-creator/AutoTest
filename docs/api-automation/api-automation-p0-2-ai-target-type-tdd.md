# 接口自动化 P0-2 AI 生成目标类型 TDD

更新时间：2026-06-18

状态：TDD 草案，已补充接口用例 / 测试套件拆分与 AI 生成链路红线验证；等待 P0-2 Spec/SDD 确认后修订；TDD 再次确认后进入 Execution

关联文档：

- `docs/api-automation/api-automation-testcase-loop-ai-generation-spec.md`
- `docs/api-automation/api-automation-p0-2-ai-target-type-spec.md`
- `docs/api-automation/api-automation-p0-1-testcase-loop-tdd.md`
- `docs/api-automation/api-automation-p0-1-testcase-loop-vdd.md`

## 1. 本阶段边界

P0-2 只处理 AI 生成链路中的“目标类型选择、Prompt 按类型选择、任务固化目标类型、生成结果按目标类型展示与校验”。

本阶段目标：

- AI 需求分析生成入口增加“生成目标类型”下拉框。
- 默认目标类型为“功能测试用例”，保证旧流程不受影响。
- 创建生成任务时固化 `target_type`，任务恢复、详情页、结果页都以任务固化值为准。
- Prompt 配置支持按 `prompt_type + target_type` 匹配。
- 选择“接口测试用例”时，后端必须使用接口测试用例 writer Prompt。
- 缺失对应目标类型 Prompt 时直接报错，不静默回退到功能测试 Prompt。
- AI 输出按目标类型做最小结构校验；接口测试用例至少校验方法、URL 和核心请求字段。
- 生成结果列表展示目标类型，并为 P0-3 接口测试用例采纳预留稳定数据结构。
- 接口测试用例结果只验证 `ApiRequest` 原子用例字段，不验证 `TestSuite` 套件编排字段。
- 本阶段验证现有 AI 生成主链没有被重写，只是在外层套用 `target_type`、Prompt 选择和结果字段适配。

本阶段不做：

- 不实现接口测试用例采纳落库到 `ApiRequest`，该内容进入 P0-3。
- 不实现 Web/App 自动化采纳落库，该内容进入 P1。
- 不新增 `ApiTestCase` 表。
- 不重构整个 AI 生成链路 UI。
- 不重构现有功能测试用例采纳服务。
- 不改变接口自动化 P0-1 已冻结的 `/api-testing/test-cases` 资产列表入口。
- 不新增绕开现有 AI 配置、模型配置和 Prompt 配置的并行调用入口。
- 不重写当前 AI 生成任务创建、模型调用、流式输出、取消、自动评审、轮询恢复和功能测试采纳链路。
- 不让 AI 直接生成 `TestSuite` 或 `TestSuiteRequest`。
- 不把接口测试用例 AI 结果直接写入测试套件；进入套件的动作留给接口测试用例资产列表或后续 P0-3/P1。

## 2. 当前生效规则

- 默认流程仍为 `Spec/SDD -> TDD -> Execution -> VDD`。
- 本阶段涉及前端、后端、数据模型、AI Prompt 选择和生成任务状态，属于高风险改动。
- 进入 Execution 前必须等待用户确认本 TDD。
- 前端新增或改动请求必须走 `frontend/src/api/* -> frontend/src/utils/api.js`。
- 后端接口必须继续走 `backend/urls.py -> apps/<module>/urls.py -> views -> serializers/services/models`。
- 新增 AI 能力必须复用 `apps.requirement_analysis` 既有 AI 服务和配置链路，不能在页面或零散工具里直连模型。
- 表单必须保留 `@submit.prevent`，原生按钮必须显式 `type="button"`。
- 使用 `ElMessageBox` 等服务式 API 时，必须确认全局样式入口已引入对应 Element Plus 样式。
- P0-2 只能套用现有 AI 生成链路：允许增加目标类型、Prompt 过滤和结果适配；禁止重写生成、评审、取消、轮询和既有采纳主链。

## 3. 当前代码事实

### 3.1 后端事实

- `apps.requirement_analysis.models.PromptConfig` 当前只有 `prompt_type`，没有 `target_type`。
- `PromptConfig.get_active_config(prompt_type)` 当前只按 `prompt_type` 查活跃 Prompt。
- `apps.requirement_analysis.models.TestCaseGenerationTask` 当前没有 `target_type`。
- `TestCaseGenerationTaskViewSet.generate()` 当前创建任务时只选择 writer/reviewer 模型和 writer/reviewer Prompt，没有目标类型概念。
- 现有采纳逻辑主要落到功能测试用例，接口测试用例采纳尚未实现。
- `apps.api_testing.models.ApiRequest` 已在 P0-1 冻结为接口测试用例技术载体。

### 3.2 前端事实

- `RequirementAnalysisView.vue` 当前是生成入口。
- `TaskDetail.vue` 当前展示任务对象和结果预览。
- `GeneratedTestCaseList.vue` 当前承接生成结果批次和功能测试用例采纳入口。
- 现有结果页采纳弹窗仍主要按功能测试用例字段组织。
- 现有页面中仍有历史直接 `api.get/post` 调用；本阶段新增或触碰的请求必须收口到 `frontend/src/api/requirement-analysis.js`，不强制一次性重构全部旧调用。

## 4. 推荐数据变更

### 4.1 目标类型枚举

统一使用以下值：

| value | label | P0-2 状态 |
| --- | --- | --- |
| `functional_test_case` | 功能测试用例 | 完整保留旧链路 |
| `api_test_case` | 接口测试用例 | 支持生成目标类型、Prompt、任务固化和结果展示 |
| `web_automation_test_case` | Web 自动化测试用例 | 可作为目标类型展示和 Prompt 类型预留，不进入采纳 |
| `app_automation_test_case` | App 自动化测试用例 | 可作为目标类型展示和 Prompt 类型预留，不进入采纳 |

### 4.2 PromptConfig

建议新增：

```text
target_type
```

默认值：

```text
functional_test_case
```

查询规则：

```text
get_active_config(prompt_type, target_type)
```

兼容规则：

- 旧 Prompt 数据迁移后默认 `target_type=functional_test_case`。
- 查找 Prompt 必须同时按 `prompt_type` 和 `target_type`。
- 找不到目标类型对应 writer Prompt 时直接返回错误。
- 找不到 reviewer Prompt 且启用自动评审时直接返回错误。
- 不允许接口测试用例生成静默使用功能测试 Prompt。

激活规则：

- P0-2 可先在应用层保证同一 `prompt_type + target_type` 只有一个启用 Prompt。
- 若实现成本可控，可增加数据库约束或保存时自动关闭同类型旧活跃 Prompt。
- 无论是否加数据库约束，都必须在 TDD 验证中覆盖“同类型多个活跃 Prompt”的处理规则。

### 4.3 TestCaseGenerationTask

建议新增：

```text
target_type
```

默认值：

```text
functional_test_case
```

任务创建时必须固化：

- `target_type`
- writer Prompt
- reviewer Prompt
- writer 模型
- reviewer 模型
- 生成配置

任务恢复规则：

- 前端恢复未完成任务时，显示任务固化的 `target_type`。
- 不允许用当前页面下拉框值覆盖已存在任务的 `target_type`。

### 4.4 生成结果结构

P0-2 可不新增独立结果表字段，但接口响应必须能稳定带出：

```json
{
  "target_type": "api_test_case",
  "target_type_label": "接口测试用例",
  "normalized_payload": {}
}
```

如果结果仍来自 `final_test_cases` 文本解析，则后端序列化时必须按 `task.target_type` 注入目标类型，保证结果页可展示。

P0-3 再基于该结构实现接口测试用例采纳落库。

### 4.5 接口测试用例与测试套件拆分验证口径

接口测试用例与测试套件必须按对象边界验证：

| 对象 | 技术承接 | 本阶段验证 |
| --- | --- | --- |
| 接口测试用例 | `ApiRequest` | AI 结果能归一化为 `name/method/url/headers/params/body/auth/assertions/pre_request_script/post_request_script` |
| 测试套件 | `TestSuite + TestSuiteRequest` | P0-2 不生成、不采纳、不修改，仅验证没有误混入套件字段 |

必须证明：

- `api_test_case` 结果的 `normalized_payload` 不包含 `suite_id`、`suite_name`、`suite_order` 等套件编排字段。
- 生成接口测试用例不会创建或更新 `TestSuite` / `TestSuiteRequest`。
- 后续加入套件仍由接口测试用例资产列表中的“加入套件”动作承接。

## 5. 接口测试用例输出最小 Schema

当 `target_type=api_test_case` 时，AI 结果至少需要归一化为：

```json
{
  "case_id": "API-001",
  "name": "登录接口验证",
  "description": "验证用户名密码登录接口",
  "method": "POST",
  "url": "https://example.com/api/login",
  "headers": {},
  "params": {},
  "body": {},
  "auth": {},
  "assertions": [],
  "pre_request_script": "",
  "post_request_script": ""
}
```

校验规则：

- `name` 必填。
- `method` 必须是 `GET/POST/PUT/PATCH/DELETE/HEAD/OPTIONS` 之一。
- `url` 必须非空。
- `url` 如果是完整 URL，必须以 `http://` 或 `https://` 开头。
- P0-2 允许 URL 是路径草稿，例如 `/api/login`，但必须标记为“待补全基础地址”；P0-3 采纳或执行前再做更严格校验。
- `headers`、`params`、`body`、`auth` 必须可归一化为对象或列表结构。
- `assertions` 必须是数组；不合法时置为空数组并记录结构错误，不能直接让页面崩溃。
- `pre_request_script`、`post_request_script` 只保存为文本；P0-2 不执行脚本。

## 6. 验证目标

- [ ] 目标 1：生成入口存在“生成目标类型”下拉框。
- [ ] 目标 2：默认值为 `functional_test_case`，旧功能测试生成不受影响。
- [ ] 目标 3：选择 `api_test_case` 创建任务后，后端任务记录固化 `target_type=api_test_case`。
- [ ] 目标 4：任务详情页展示目标类型。
- [ ] 目标 5：生成结果页展示目标类型。
- [ ] 目标 6：Prompt 查询按 `prompt_type + target_type` 选择。
- [ ] 目标 7：接口测试用例 writer Prompt 缺失时直接报错，不回退到功能测试 Prompt。
- [ ] 目标 8：启用自动评审时，接口测试用例 reviewer Prompt 缺失也直接报错。
- [ ] 目标 9：非法 `target_type` 返回明确错误。
- [ ] 目标 10：旧任务没有 `target_type` 时按 `functional_test_case` 兼容展示。
- [ ] 目标 11：接口测试用例 AI 输出可解析为接口用例结构。
- [ ] 目标 12：接口测试用例 AI 输出缺少关键字段时，任务进入失败态或结果标记结构错误，前端有明确提示。
- [ ] 目标 13：功能测试用例旧采纳流程不回归。
- [ ] 目标 14：生成任务运行中，下拉框锁定，不能中途修改。
- [ ] 目标 15：不新增整页刷新兜底。
- [ ] 目标 16：现有 AI 生成主链没有被重写，功能测试旧生成、取消、自动评审、轮询恢复和采纳入口保持原行为。
- [ ] 目标 17：接口测试用例 AI 结果只生成 `ApiRequest` 原子用例字段，不生成、不采纳、不修改测试套件。

## 7. 失败场景

### 7.1 目标类型选择失败

- 前端未传 `target_type`。
- 前端传了空字符串。
- 前端传了未支持值，例如 `security_test_case`。
- 任务创建后，前端又切换下拉框并覆盖任务目标类型。
- 恢复旧任务时页面错误显示为接口测试用例。

### 7.2 Prompt 匹配失败

- `api_test_case` 没有 writer Prompt，但系统使用了功能测试 Prompt。
- `api_test_case` 开启自动评审但没有 reviewer Prompt，系统继续生成并跳过评审。
- 同一 `prompt_type + target_type` 有多个启用 Prompt，系统选择不稳定。
- Prompt 配置页没有展示目标类型，用户无法知道配置适用于哪类用例。

### 7.3 任务固化失败

- 任务表没有保存 `target_type`。
- 任务详情接口不返回 `target_type`。
- 任务进度接口返回的目标类型和任务详情不一致。
- SSE 或轮询恢复时使用了当前页面下拉框值，而不是任务固化值。

### 7.4 AI 输出结构失败

- 接口测试用例结果仍按功能测试字段展示，出现 `scenario/precondition/steps/expected` 混用。
- 接口测试用例缺少 `method` 或 `url` 仍显示为可确认资产。
- `headers/params/body/assertions` 返回字符串、空值或异常结构导致前端渲染报错。
- AI 返回非 JSON 或结构无法解析时任务一直停在生成中。

### 7.5 前端交互失败

- 下拉框切换后说明文案不变。
- 任务运行中仍允许修改目标类型。
- Prompt 缺失错误只在控制台出现，页面没有提示。
- 结果页目标类型列缺失，用户不知道这批结果是什么类型。
- 操作失败继续使用原生 `alert()`。

### 7.6 回归失败

- 默认功能测试生成任务创建失败。
- 功能测试用例 writer/reviewer Prompt 查询不到旧配置。
- 功能测试生成结果页采纳按钮消失。
- 旧任务列表打不开。
- 旧功能测试批量采纳不可用。

### 7.7 对象边界失败

- `api_test_case` 结果里出现 `suite_id`、`suite_name`、`suite_order` 等套件编排字段。
- 创建接口测试用例生成任务时同步创建了 `TestSuite` 或 `TestSuiteRequest`。
- 结果页把接口测试用例当成测试套件展示，或者把“加入套件”伪装成 AI 生成完成后的自动动作。
- 为了实现接口测试用例字段适配，改坏了功能测试用例的原解析和采纳逻辑。

## 8. 最小验证清单

### 8.1 静态检查

命令：

```text
git diff --check
```

通过标准：

- 无冲突标记、尾随空格或非法空白错误。

### 8.2 后端编译级验证

命令：

```text
python -m py_compile apps\requirement_analysis\models.py
python -m py_compile apps\requirement_analysis\serializers.py
python -m py_compile apps\requirement_analysis\views.py
python -m py_compile apps\requirement_analysis\result_status.py
```

如本阶段改动接口自动化来源展示或 API 封装，再追加：

```text
python -m py_compile apps\api_testing\models.py
python -m py_compile apps\api_testing\serializers.py
python -m py_compile apps\api_testing\views.py
```

### 8.3 迁移验证

如果新增模型字段，必须生成迁移并验证：

```text
python manage.py makemigrations requirement_analysis
python manage.py migrate --plan
```

通过标准：

- 迁移只包含本阶段字段。
- 旧数据默认 `functional_test_case`。
- 不出现删除表、重建表、误改无关字段。

如本地数据库环境无法执行 `migrate --plan`，交付时必须说明。

### 8.4 后端接口级验证

创建功能测试任务：

```json
{
  "title": "功能测试生成",
  "requirement_text": "用户登录",
  "target_type": "functional_test_case"
}
```

通过标准：

- 返回任务成功。
- 任务 `target_type=functional_test_case`。
- 使用功能测试 writer Prompt。

创建接口测试任务：

```json
{
  "title": "接口测试生成",
  "requirement_text": "登录接口需要校验成功和失败场景",
  "target_type": "api_test_case"
}
```

通过标准：

- 返回任务成功。
- 任务 `target_type=api_test_case`。
- 使用接口测试用例 writer Prompt。
- 如果接口测试 Prompt 未配置，返回 400，提示“未配置接口测试用例 Prompt”。

非法目标类型：

```json
{
  "title": "非法类型",
  "requirement_text": "测试",
  "target_type": "security_test_case"
}
```

通过标准：

- 返回 400。
- 返回可展示中文提示。
- 不创建任务。

### 8.5 前端构建级验证

命令：

```text
cd frontend && cmd /c npm run build
```

通过标准：

- 构建通过。
- 允许保留既有 `web-tree-sitter` 警告。
- 不允许出现新增未解析导入、模板语法错误或路由加载错误。

### 8.6 前端页面级验证

操作：

1. 打开 AI 需求分析生成入口。
2. 查看“生成目标类型”下拉框。
3. 默认不操作，发起功能测试用例生成。
4. 切换为“接口测试用例”，发起生成。
5. 在任务详情页查看目标类型。
6. 在生成结果页查看目标类型。
7. 模拟缺失接口测试 Prompt 后再发起生成。

通过标准：

- 默认显示“功能测试用例”。
- 切换后说明文案跟随目标类型变化。
- 任务运行中下拉框锁定。
- 任务详情页和结果页展示同一目标类型。
- Prompt 缺失时页面有明确错误提示。
- 页面不刷新，不跳出当前 SPA。

### 8.7 功能测试旧链路回归

操作：

1. 默认目标类型创建功能测试用例生成任务。
2. 等待任务完成。
3. 进入生成结果页。
4. 执行原有单条采纳或批量采纳。

通过标准：

- 旧功能测试 Prompt 可被找到。
- 原有功能测试结果字段展示正常。
- 原有采纳弹窗仍可创建 `apps.testcases.TestCase`。
- 原有来源标签、处理状态、幂等逻辑不回归。

### 8.8 导航与默认行为回归

操作：

1. 从测试设计切到接口自动化。
2. 从接口自动化切回 AI 生成结果页。
3. 快速切换顶部模块和侧边栏。
4. 在目标类型下拉框所在表单中按 Enter。

通过标准：

- 最终停在最后点击页面。
- 无 `beforeunload`、`pagehide` 或主文档请求。
- Enter 不触发整页刷新。
- 控制台无新增业务红错。

## 9. 推荐实现顺序

1. 新增目标类型常量和展示映射，优先放在 `apps.requirement_analysis` 内部可复用位置。
2. 为 `PromptConfig` 增加 `target_type` 字段和迁移，旧数据默认 `functional_test_case`。
3. 为 `TestCaseGenerationTask` 增加 `target_type` 字段和迁移，旧数据默认 `functional_test_case`。
4. 扩展 `PromptConfigSerializer`、`TestCaseGenerationTaskSerializer`，返回 `target_type` 和中文 label。
5. 扩展 Prompt 查询接口，支持按 `target_type` 过滤。
6. 修改 `PromptConfig.get_active_config()`，按 `prompt_type + target_type` 查询。
7. 修改生成任务创建逻辑，校验 `target_type`，按目标类型选择 writer/reviewer Prompt。
8. 增加接口测试用例输出的最小结构归一化和校验。
9. 修改 `RequirementAnalysisView.vue`，新增目标类型下拉框和说明文案。
10. 修改任务详情和生成结果页，展示目标类型。
11. 将本阶段新增请求封装到 `frontend/src/api/requirement-analysis.js`。
12. 执行后端编译、迁移计划、前端构建和页面验证。
13. 更新 VDD 和项目记忆。

## 10. 回退方式

如 P0-2 出现不可接受问题，回退顺序：

1. 前端生成入口隐藏目标类型下拉框，默认发送 `functional_test_case`。
2. 后端保留新增字段但默认按 `functional_test_case` 处理旧流程。
3. Prompt 查询临时兼容旧 `get_active_config(prompt_type)`，但必须明确这是止损，不允许接口测试用例静默使用功能 Prompt。
4. 回退 P0-2 生成逻辑时，不回退 P0-1 `/api-testing/test-cases` 已完成闭环。

禁止：

- 用 `window.location.reload()` 兜底任务状态。
- 删除已生成迁移来“回滚”本地数据库。
- 让接口测试目标静默退回功能测试 Prompt。

## 11. 完成判定

P0-2 完成需要同时满足：

- 验证目标 1-15 全部通过。
- 默认功能测试生成和采纳旧流程通过。
- 接口测试用例目标可以创建任务，并使用目标类型 Prompt。
- Prompt 缺失、目标类型非法、AI 输出不可解析都有明确错误提示。
- 任务详情页和结果页都能展示目标类型。
- 前端构建通过。
- 后端编译和迁移计划通过，或明确说明本地环境限制。
- VDD、项目记忆、更新日志完成回写。

## 12. 进入 Execution 前需要确认

本 TDD 不能绕过 Spec/SDD 闸门。请先确认：

- `docs/api-automation/api-automation-p0-2-ai-target-type-spec.md`

Spec/SDD 确认后，再确认以下 P0-2 TDD 范围：

- P0-2 只实现“AI 生成目标类型 + Prompt 按类型选择 + 任务固化目标类型 + 结果展示目标类型”。
- 接口测试用例采纳到 `ApiRequest` 进入 P0-3。
- Web/App 自动化采纳进入 P1。
- 旧功能测试生成和采纳必须作为回归主线保留。

Spec/SDD 和 TDD 都确认后，再进入正式代码实现。

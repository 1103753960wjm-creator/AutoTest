# 接口自动化阶段 A 对象闭环 P0 补强 VDD

更新时间：2026-06-19

状态：Execution 已完成，验证通过静态与构建级检查；等待真实浏览器人工回归

关联文档：

- `docs/api-automation/api-automation-object-closure-audit.md`
- `docs/api-automation/api-automation-p0-object-closure-fix-tdd.md`
- `docs/api-automation/archive/p0-docs-2026-06-18/README.md`
- `docs/api-automation/api-automation-p0-1-testcase-loop-tdd.md`
- `docs/api-automation/api-automation-p0-1-testcase-loop-vdd.md`
- `docs/api-automation/api-automation-p0-2-ai-target-type-spec.md`

## 1. 本轮交付结论

阶段 A 已按 TDD 口径完成接口自动化对象闭环 P0 补强。

本轮没有新增 `ApiTestCase` 数据表，没有修改 AI 生成测试用例主链，没有进入 P0-2 目标类型下拉、P0-3 AI 采纳入库、Web/App 自动化采纳或执行中心迁移。

本轮继续保持对象边界：

```text
/api-testing/test-cases = 接口测试用例资产列表，技术承接 ApiRequest
/api-testing/test-suites = 测试套件编排和执行页面，技术承接 TestSuite + TestSuiteRequest
/api-testing/automation = 旧入口兼容，重定向到 /api-testing/test-suites
```

## 2. 已落地内容

### 2.1 接口测试用例移动集合

- 新增后端动作 `POST /api-testing/requests/{id}/move-collection/`。
- 后端校验目标集合必须存在，并且接口测试用例只能移动到同项目集合。
- 后端校验当前用户必须是目标项目负责人或成员。
- 成功移动后更新 `ApiRequest.collection` 并记录操作日志。
- 接口测试用例列表新增“移动集合”弹窗，只展示同项目集合。
- 移动弹窗具备加载态、目标集合必选、相同集合阻断和失败提示。
- 移动成功后刷新集合和用例列表，列表展示新的所属集合。

### 2.2 调试工作区所属集合编辑

- 隐藏调试工作区基础信息区新增所属集合下拉。
- 保存接口测试用例时要求必须选择所属集合。
- 无集合时新建入口提示先创建集合，不继续制造无项目归属的半闭环用例。
- 从列表进入工作区仍携带 `caseId/projectId`，工作区监听 query 变化并重选目标用例。

### 2.3 请求历史清空闭环

- 新增后端动作 `POST /api-testing/histories/clear/`。
- 清空范围按当前筛选条件收口，支持：
  - `request`
  - `request__request_type`
  - `request_type`
  - `status_code`
  - `search`
- 后端先走当前用户可见的 `RequestHistoryViewSet.get_queryset()`，再按筛选条件删除，避免误删无权限数据。
- 前端“清空历史”不再提示未实现，改为二次确认后调用真实接口。
- 清空时按钮进入 loading，成功后清空勾选、回到第一页并刷新列表。
- 失败时保留当前列表并展示明确错误提示。

### 2.4 套件级断言闭环

- 新增后端动作 `POST /api-testing/test-suite-requests/{id}/assertions/`。
- 后端校验 `assertions` 必须是数组，并保存到 `TestSuiteRequest.assertions`。
- 测试套件页“编辑断言”不再提示“功能开发中”，改为打开编辑弹窗。
- 弹窗支持新增、删除、编辑断言，保存中按钮 loading，取消不保存。
- 弹窗使用 `el-dialog align-center`、统一表单、底部按钮和遮罩，按系统已有编辑弹窗风格承接。
- 套件执行时优先使用 `TestSuiteRequest.assertions`；如果套件级断言为空，则回退到 `ApiRequest.assertions`，保持旧套件兼容。
- 断言执行兼容旧 `value` 和新 `expected` 字段。

### 2.5 项目负责人字段契约修正

- 项目管理编辑弹窗中的负责人改为只读展示。
- 新建和编辑项目提交时不再向后端提交 `owner`，避免“页面可改但后端只读”的误导。

### 2.6 删除级联风险提示

- 删除项目时提示会影响集合、接口测试用例、测试套件、局部环境和相关执行历史。
- 删除集合时提示会影响子集合和接口测试用例。
- 删除接口测试用例时提示如果已加入测试套件，会影响套件执行。
- 删除环境时提示会影响使用该环境的测试套件、定时任务或执行配置。

### 2.7 前端请求封装收口

- `frontend/src/api/api-testing.js` 补齐接口自动化常用 API 封装。
- `AutomationTesting.vue`、`RequestHistory.vue`、`ProjectManagement.vue`、`EnvironmentManagement.vue`、`AIServiceConfig.vue`、`ReportView.vue`、`ScheduledTasks.vue` 等页面不再直接导入 `@/utils/api` 发业务请求。
- 新增请求继续保持 `View -> frontend/src/api/api-testing.js -> frontend/src/utils/api.js -> Backend` 链路。

## 3. 验证证据

已执行：

```text
python -m py_compile apps\api_testing\models.py apps\api_testing\serializers.py apps\api_testing\views.py apps\api_testing\urls.py apps\api_testing\utils.py
cd frontend && cmd /c npm run build
rg -n "window\.location\.reload|window\.location\.href|location\.reload|window\.location\.assign" frontend/src/views/api-testing frontend/src/api/api-testing.js
rg -n "功能正在开发中|功能开发中|开发中|featureInDevelopment|clearNotImplemented|assertionDeveloping" frontend/src/views/api-testing frontend/src/api/api-testing.js
rg -n "import api from '@/utils/api'|from '@/utils/api'|api\.(get|post|put|patch|delete)" frontend/src/views/api-testing
```

验证结果：

- 后端受影响文件 `py_compile` 通过。
- 前端构建通过。
- 未检出接口自动化阶段 A 改动新增整页刷新兜底。
- 未检出阶段 A 页面保留“功能开发中 / 清空未实现 / 断言开发中”等假入口。
- 未检出接口自动化页面继续直接导入 `@/utils/api` 进行业务请求；唯一命中是 `NotificationManagement.vue` 中 webhook 示例 URL 文本，不是请求调用。

构建残余警告：

- 仍保留既有 `web-tree-sitter` 的 `fs/path` 浏览器兼容警告与 `eval` 警告，本轮未改动该依赖链。

## 4. 验收核对

- [x] `/api-testing/test-cases` 继续作为接口测试用例资产列表。
- [x] `/api-testing/test-suites` 继续作为测试套件编排和执行页面。
- [x] `/api-testing/automation` 作为旧入口兼容重定向保留。
- [x] 已存在接口测试用例可以通过列表移动到同项目集合。
- [x] 移动集合后会刷新列表展示。
- [x] 调试工作区可查看和修改所属集合。
- [x] 新建接口测试用例继续要求选择集合。
- [x] 请求历史“清空历史”不再是假入口，已接后端真实清空接口。
- [x] 套件级断言“编辑断言”不再是假入口，已接保存弹窗和后端接口。
- [x] 套件执行时优先使用套件级断言，空时兼容接口自身断言。
- [x] 项目负责人字段不再展示为可编辑输入。
- [x] 删除项目、集合、接口测试用例、环境前补充级联风险提示。
- [x] 新增和触碰的接口自动化请求收口到 `frontend/src/api/api-testing.js`。
- [x] 不新增 `window.location.reload()` 或整页跳转兜底。

## 5. 未完成验证

以下需要真实登录环境和业务数据，本轮未在浏览器人工完成：

- 在 `/api-testing/test-cases` 实际移动一条接口测试用例到同项目另一个集合，并确认调试工作区回显一致。
- 在 `/api-testing/history` 按指定用例过滤后清空历史，确认只清空当前范围。
- 在 `/api-testing/test-suites` 编辑套件级断言、刷新后回显，并执行套件验证断言优先级。
- 删除项目、集合、环境时人工确认弹窗文案和交互样式。
- 顶部大模块与侧边栏快速切换的浏览器级回归。

## 6. 回退方式

如需回退阶段 A：

- 回退 `ApiRequestViewSet.move_collection` 和前端“移动集合”弹窗。
- 回退 `RequestHistoryViewSet.clear` 和前端“清空历史”调用。
- 回退 `TestSuiteRequestViewSet.update_assertions`、测试套件页断言弹窗，以及套件执行中套件级断言优先逻辑。
- 回退项目负责人只读展示和删除级联风险提示文案。
- 保留 P0-1 已完成内容，不建议回退 `/api-testing/test-cases` 资产列表、单接口执行路径、请求历史断言展示和隐藏工作区深链能力。

## 7. 残余风险

- `ApiRequestViewSet.get_queryset()` 为兼容历史未分组接口，按项目过滤时仍会返回当前用户创建的未分组接口。P0 新建入口已阻断继续产生未分组用例，但旧数据仍可能显示“未分组”，后续若要彻底清理需要单独迁移或提供显式归组工具。
- 测试套件页请求树当前仍使用较大的 `page_size` 加载项目内请求，满足当前套件添加树使用，但如果项目内接口量变大，后续应补后端树形/搜索接口，避免继续扩大一次性加载。
- 套件级断言弹窗覆盖常见断言类型，但未做复杂 JSON Schema 校验；后续若扩展断言语法，需要同步执行器、弹窗和 AI 接口用例字段契约。
- 本轮没有跑真实浏览器人工验收，页面交互仍需用户或后续回归阶段确认。

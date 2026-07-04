# 接口自动化 P0-1 用例闭环 VDD

更新时间：2026-06-17

关联文档：

- `docs/api-automation/api-automation-testcase-loop-ai-generation-spec.md`
- `docs/api-automation/api-automation-p0-1-testcase-loop-tdd.md`

## 1. 本轮交付结论

P0-1 已完成接口自动化自身闭环的最小落地。

本轮只做接口自动化自身闭环，不进入 AI 生成目标类型下拉、AI 结果采纳、Web/App 自动化采纳，也不新增 `ApiTestCase` 数据表。

## 2. 已落地内容

- 接口自动化新增正式可见入口“接口测试用例”，路径为 `/api-testing/test-cases`。
- 旧入口 `/api-testing/interfaces` 保留为隐藏兼容路由，并重定向到 `/api-testing/test-cases`，不直接 404。
- P0-1.5 已将 `/api-testing/test-cases` 从旧接口调试工作区改为真正的接口测试用例资产列表页。
- 旧 `InterfaceManagement.vue` 不再作为接口测试用例首页，改为隐藏调试工作区 `/api-testing/test-cases/workspace?caseId={id}`。
- 列表进入隐藏调试工作区时会同步传递 `projectId`，确保非默认项目下的接口测试用例也能被选中。
- 隐藏调试工作区作为 `keepAlive` 页面时会监听 `caseId/projectId` 变化并重新选中目标用例，不再依赖页面销毁重建。
- 隐藏调试工作区如果当前项目树未命中目标 `caseId`，会直接按 `caseId` 拉取详情，避免请求列表分页导致深链失效。
- 接口测试用例列表和工作区详情加载均增加旧响应丢弃，快速筛选、分页或连续打开不同用例时，以最后一次用户目标为准。
- 接口测试用例列表支持按项目、方法、用例名称或 URL 查询，并展示用例名称、请求方法、URL、所属集合、断言数和更新时间。
- 接口测试用例列表支持新建、编辑/调试、单用例执行、加入测试套件、查看该用例请求历史和删除。
- 接口测试用例列表筛选区“查询 / 重置”按钮已增加上间距，避免贴住筛选输入框。
- 隐藏调试工作区已新增“返回用例列表”按钮，用户从列表进入编辑/调试后可显式回到 `/api-testing/test-cases`。
- 接口测试用例列表行操作按钮已使用 `@click.stop`，避免“加入套件”等操作触发表格行双击进入调试页。
- 新建接口测试用例时必须选择集合，避免产生无项目归属的半闭环接口用例资产。
- 加入测试套件时使用现有 `/api-testing/test-suites/{id}/add-requests/`，并在后端限制只能添加同项目集合下的接口测试用例。
- 加入测试套件对话框已补加载态和禁用态：加载套件时禁用选择与确认，无可用套件时关闭选择弹窗并给出说明。
- 加入测试套件所有关键结果均已改为弹窗反馈：未归属集合、当前项目无套件、套件加载失败、未选择套件、加入成功、加入失败。
- 请求历史支持通过 `request` 参数按指定接口测试用例过滤，列表页点击“历史”可收敛到该用例历史记录。
- P0-1 阶段冻结 `ApiRequest` 继续作为接口测试用例的技术载体。
- 修正前端 API 封装旧路径：
  - 单接口执行改为 `/api-testing/requests/{id}/execute/`
  - 执行结果详情改为 `/api-testing/test-executions/{id}/`
- `InterfaceManagement.vue` 作为接口测试用例隐藏调试工作区继续复用，但页面请求已收口到 `frontend/src/api/api-testing.js`。
- 搜索不再调用不存在的 `/api-testing/collections/search`，改走真实 `ApiRequest` 列表搜索。
- 未保存的新接口测试用例禁止直接执行，先提示保存，避免打到 `/requests/null/execute/`。
- 单接口执行成功后，`RequestHistory.assertions_results` 会真实落库。
- 请求历史详情新增“断言结果”页签，可查看单接口执行落库后的断言通过/失败、类型、期望、实际和错误。
- 接口自动化 Dashboard 快捷入口改为进入 `/api-testing/test-cases`。
- 前端入口已补齐 Element Plus 服务式组件样式：
  - `element-plus/es/components/loading/style/css`
  - `element-plus/es/components/message/style/css`
  - `element-plus/es/components/message-box/style/css`
  以确保 `ElMessageBox` 弹窗居中、遮罩和按钮样式正常。

## 3. 验证证据

已执行：

```text
git diff --check
python -m py_compile apps\api_testing\models.py apps\api_testing\serializers.py apps\api_testing\views.py apps\api_testing\urls.py
rg -n "/api-testing/api-requests|/api-testing/executions/|collections/search|window\.location\.reload\(|window\.location\.href|location\.reload" frontend\src apps\api_testing
rg -n "from '@/utils/api'|import api from '@/utils/api'|api\.(get|post|put|patch|delete)" frontend\src\views\api-testing\InterfaceManagement.vue frontend\src\api\api-testing.js
Select-String -Path frontend\src\views\api-testing\ApiTestCaseList.vue,frontend\src\views\api-testing\InterfaceManagement.vue,frontend\src\views\api-testing\RequestHistory.vue -Pattern "<el-form(\s|>)|<form(\s|>)|<button(\s|>)"
cd frontend && cmd /c npm run build
浏览器运行时 CSSOM 检查 .el-message-box / .el-overlay-message-box 样式规则
```

验证结果：

- `git diff --check` 通过。
- 后端受影响文件 `py_compile` 通过。
- 未检出旧执行路径 `/api-testing/api-requests`。
- 未检出旧执行结果路径 `/api-testing/executions/`。
- 未检出不存在的 `collections/search` 调用。
- 未检出本轮新增整页刷新兜底。
- `InterfaceManagement.vue` 不再直接导入 `@/utils/api`，业务请求统一经由 `frontend/src/api/api-testing.js`。
- 受影响接口自动化页面未发现未保护原生 `<form>` 或未声明类型的原生 `<button>`；`<el-form>` 均保留 `@submit.prevent`。
- 前端构建通过。
- 浏览器运行时已确认存在 `.el-message-box` 与 `.el-overlay-message-box` 样式规则。

构建残余警告：

- 仍保留既有 `web-tree-sitter` 的 `fs/path` 浏览器兼容警告与 `eval` 警告，本轮未改动该依赖链。

## 4. 验收核对

- [x] `/api-testing/test-cases` 已注册为接口自动化正式入口。
- [x] `/api-testing/interfaces` 已隐藏兼容并重定向，不直接 404。
- [x] 接口测试用例页已拆成资产列表页，隐藏工作区复用现有 `ApiRequest` 编辑调试能力。
- [x] 列表进入隐藏工作区时携带 `projectId`，隐藏工作区 query 变化可切换到最后点击的目标用例。
- [x] 创建、编辑、保存接口测试用例继续走 `/api-testing/requests/`。
- [x] 接口测试用例可从列表加入同项目测试套件。
- [x] 加入测试套件已覆盖未归属集合、无可用套件、加载失败、未选择、成功和失败弹窗反馈。
- [x] 隐藏调试工作区已提供返回用例列表入口。
- [x] `ElMessageBox` 服务式弹窗样式已补齐并可在运行时检索到。
- [x] 单接口执行使用 `/api-testing/requests/{id}/execute/`。
- [x] 单接口执行成功后断言结果写入 `RequestHistory.assertions_results`。
- [x] 请求历史详情页可展示 `RequestHistory.assertions_results`。
- [x] 前端构建通过，路由和导入可打包。
- [x] 前端请求链路符合 `View -> frontend/src/api/* -> frontend/src/utils/api.js`。
- [x] 旧入口和 Dashboard 快捷入口已对齐新路径。

## 5. 未完成验证

以下需要真实运行环境和测试数据，本轮未在浏览器内完成实操：

- 实际登录后点击 `/api-testing/test-cases`，创建、保存、执行一条真实 HTTP 接口测试用例。
- 打开请求历史详情，人工确认 `assertions_results` 展示效果。
- 在 `/api-testing/test-suites` 中添加接口测试用例并执行套件，人工确认 `TestExecution` 结果。
- 顶部大模块快速切换后立即点击接口自动化侧边栏，人工确认无主文档请求和无控制台红错。

## 6. 回退方式

如需回退本轮 P0-1：

- 将导航真源中“接口测试用例”恢复为旧“接口管理”可见入口。
- 将 `/api-testing/interfaces` 路由恢复为直接挂载 `ApiInterfaceManagement`。
- 回退 `frontend/src/api/api-testing.js` 中新增的接口测试用例语义别名和路径修正。
- 回退 `apps/api_testing/views.py` 中 `assertions_results=assertions_results` 落库字段。

不建议只回退后端落库字段而保留前端入口，因为这样请求历史仍会看不到断言结果，闭环会再次断开。

## 7. 残余风险

- P0-1.5 已消除“接口测试用例首页像接口管理换名”的主要问题；但最近执行状态目前尚未做后端聚合字段，避免列表页对每条用例发起 N+1 请求。后续若要展示最近执行状态，应在后端 `ApiRequest` 列表聚合最近一条 `RequestHistory` 后统一返回。
- 本轮未新增 `ApiTestCase` 表，后续如果要把接口用例从接口请求定义中拆出，需要重新走 Spec/SDD 和迁移设计。
- AI 生成目标类型下拉、接口测试用例采纳、Web/App 自动化采纳仍属于后续阶段。

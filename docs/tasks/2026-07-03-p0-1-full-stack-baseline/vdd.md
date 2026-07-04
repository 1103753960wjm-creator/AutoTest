# VDD：P0.1 前后端与样式上线阻断项第一批

## 1. 标题

- 任务名称：P0.1 前后端与样式上线阻断项第一批
- 日期：2026-07-03
- 关联 Spec/SDD：`docs/tasks/2026-07-03-p0-1-full-stack-baseline/spec-sdd.md`
- 关联 TDD：`docs/tasks/2026-07-03-p0-1-full-stack-baseline/tdd.md`
- 关联 Loop 合同：`docs/tasks/2026-07-03-p0-1-full-stack-baseline/loop-contract.md`
- 关联公开接口白名单：`docs/tasks/2026-07-03-p0-1-full-stack-baseline/public-api-whitelist.md`
- 当前阶段：VDD
- 本轮最高验证等级：V3（有限请求级验证）

说明：本轮已完成静态扫描、前端构建、后端编译、规则检查和一组 DRF 测试客户端请求级验证。未执行真实浏览器页面操作；App 自动化报告真实文件 200/403 因本地数据库没有执行记录未能验证。

## 2. 本轮改了什么

- 大白话总结：
  - 样式侧新增最小设计令牌入口，`global.scss` 和共享页面壳开始使用 `--th-*` token，避免后续继续散写基础颜色、间距、圆角和阴影。
  - 前端请求侧把 P0.1 点名的 `DataFactory.vue`、`DataFactorySelector.vue`、`ExecutionDetailView.vue` 裸 `axios` 请求收口到 `frontend/src/api/* -> frontend/src/utils/api.js`。
  - 后端权限侧把需求分析配置检查、生成任务、进度接口、SSE 进度和 App 自动化报告入口从匿名口径收紧到认证和对象权限口径。
  - 文档侧新增公开接口白名单、Loop 合同和本 VDD，明确哪些接口能公开，哪些敏感接口不能公开。
- 修改的主要文件：
  - `frontend/src/assets/css/global.scss`
  - `frontend/src/components/page-shells/DashboardShell.vue`
  - `frontend/src/components/page-shells/DetailResultShell.vue`
  - `frontend/src/components/page-shells/ListShell.vue`
  - `frontend/src/components/page-shells/WorkspaceShell.vue`
  - `frontend/src/components/platform-shared/FilterBar.vue`
  - `frontend/src/components/platform-shared/UnifiedListTable.vue`
  - `frontend/src/api/data-factory.js`
  - `frontend/src/components/DataFactorySelector.vue`
  - `frontend/src/views/data-factory/DataFactory.vue`
  - `frontend/src/views/executions/ExecutionDetailView.vue`
  - `frontend/src/main.js`
  - `frontend/src/utils/api.js`
  - `apps/requirement_analysis/views.py`
  - `apps/app_automation/views/execution_views.py`
  - `backend/urls.py`
- 新增的主要文件：
  - `frontend/src/assets/css/design-tokens.scss`
  - `frontend/src/api/executions.js`
  - `docs/tasks/2026-07-03-p0-1-full-stack-baseline/public-api-whitelist.md`
  - `docs/tasks/2026-07-03-p0-1-full-stack-baseline/loop-contract.md`
  - `docs/tasks/2026-07-03-p0-1-full-stack-baseline/vdd.md`
- 没有改但容易被误解的范围：
  - 未新增数据库表或迁移。
  - 未重写 AI 生成主链、执行器、报告生成主链或 WebSocket 主链。
  - 未做全站页面视觉大重构；本轮只建立 token 基线并轻触共享基座。
  - 未纳入后端模拟实现清理、误导性注释清理和 P0.2 实时连接封装。

## 3. 验收标准核对

| 验收项 | 是否通过 | 证据 | 备注 |
| --- | --- | --- | --- |
| `design-tokens.scss` 存在，并被 `global.scss` 引入 | 通过 | `rg -n "design-tokens|--th-" frontend\src\assets\css ...` 命中 token 文件和 `global.scss:1` | token 文件自身保留原始颜色值，属于真源定义 |
| P0.1 新改共享样式优先使用 `--th-*` token | 通过 | 共享页面壳、`FilterBar.vue`、`UnifiedListTable.vue` 均命中 `--th-*` | 未做全站旧样式替换 |
| `frontend/src` 中除 `utils/api.js` 外不再有裸 `axios.get/post/patch/delete` | 通过 | `rg -n "import axios|axios\.(get|post|put|patch|delete)|axios\.defaults" frontend\src -g "*.js" -g "*.vue"` 只命中 `frontend/src/utils/api.js:1` | 需求分析页普通 `axios` 注释不属于裸请求 |
| `main.js` 不再设置全局 axios defaults | 通过 | 静态扫描无 `axios.defaults`；`utils/api.js` 集中配置 CSRF 和 cookie | 构建验证已通过 |
| 数据工厂和执行详情主要功能不回退 | 部分通过 | 前端构建通过；请求封装路径静态检查通过 | 未做浏览器真实点击验证 |
| 未登录用户不能访问敏感需求生成、配置状态、报告文件和进度接口 | 通过 | DRF 测试客户端：配置检查、生成、上传分析、文本分析、任务进度、SSE、App 报告 API 均返回 401；直接 media 报告路径返回 403 | 已覆盖未登录异常流 |
| 有权限用户可以正常访问自己的资源 | 部分通过 | 使用现有 admin 登录态：配置检查返回 200；已有本人任务 `progress/` 和 `stream_progress/` 返回 200 | App 报告因本地无执行记录未验证 |
| 权限失败返回 401/403，不伪装成功 | 部分通过 | 未登录返回 401；开发态直接报告 media 返回 403；不存在对象返回 404 | 无权限访问真实存在对象的 403 因缺少第二用户/目标数据未验证 |
| 公开接口有清单和理由 | 通过 | `public-api-whitelist.md` 已列认证入口白名单，并明确需求生成、进度、报告不公开 | 已补直接 media 报告路径不公开 |
| 不引入数据库迁移、不新增依赖、不重写 AI/执行器/报告主链 | 通过 | 本轮改动集中在样式、API 封装、视图权限和文档；未改迁移、依赖或主链 | 工作区有大量既有未提交改动，需按 P0.1 范围审阅 |

## 4. 验证执行记录

| 验证类型 | 命令或操作 | 结果 | 证据 |
| --- | --- | --- | --- |
| 前端静态扫描 | `rg -n "import axios|axios\.(get|post|put|patch|delete)|axios\.defaults" frontend\src -g "*.js" -g "*.vue"` | 通过 | 只命中 `frontend/src/utils/api.js:1` |
| 样式静态扫描 | `rg -n "design-tokens|--th-" frontend\src\assets\css frontend\src\components\page-shells frontend\src\components\platform-shared` | 通过 | 命中 token 文件、`global.scss` 引入和共享组件 token 使用 |
| 后端权限静态扫描 | `rg -n "AllowAny|csrf_exempt|permission_classes\s*=\s*\[\]|login_required|app-automation-reports|task_id本身就是安全标识|uploaded_by_id=1" ...` | 通过 | 无命中；`rg` 返回 1 在本检查语义中表示未发现高风险写法 |
| 后端编译 | `python -m py_compile apps\requirement_analysis\views.py apps\app_automation\views\execution_views.py backend\settings.py backend\urls.py` | 通过 | 返回 0 |
| 前端构建 | `cmd /c npm run build`（工作目录 `frontend`） | 通过 | Vite build 成功，仍有既有 `web-tree-sitter` 的 `fs/path externalized` 和 `eval` 警告 |
| 规则检查 | `powershell -ExecutionPolicy Bypass -File scripts\rule_check.ps1` | 通过 | 输出 `Rule check passed: no P0 redline hits.` |
| Diff 空白检查 | `git diff --check -- frontend\src apps\requirement_analysis\views.py apps\app_automation\views\execution_views.py backend\settings.py backend\urls.py docs\tasks\2026-07-03-p0-1-full-stack-baseline ...` | 通过 | 返回 0；仅有大量既有 LF/CRLF 提示 |
| 请求级验证：未登录 | DRF `APIClient` 请求配置检查、生成、上传分析、文本分析、任务进度、SSE、App 报告 API、直接 media 报告路径 | 通过 | 敏感 API 返回 401；直接 `/media/app-automation/allure-reports/...` 返回 403 |
| 请求级验证：登录态 | DRF `APIClient.force_authenticate(admin)` 请求配置检查、不存在任务/报告、本人任务进度和 SSE | 部分通过 | 配置检查 200；不存在对象 404；本人任务 `progress/` 和 `stream_progress/` 200 |
| 页面验证 | 浏览器登录后操作数据工厂、执行详情、需求分析、App 报告入口 | 未执行 | 本轮未启动前后端联调服务做浏览器操作 |

## 5. 请求级验证明细

- 未登录请求结果：
  - `GET /api/requirement-analysis/config/check/` -> 401
  - `POST /api/requirement-analysis/testcase-generation/generate/` -> 401
  - `POST /api/requirement-analysis/upload-and-analyze/` -> 401
  - `POST /api/requirement-analysis/analyze-text/` -> 401
  - `GET /api/requirement-analysis/testcase-generation/not-existing-task/progress/` -> 401
  - `GET /api/requirement-analysis/testcase-generation/not-existing-task/stream_progress/` -> 401
  - `GET /api/app-automation/executions/1/report/` -> 401
  - `GET /api/app-automation/executions/1/report/index.html` -> 401
  - `GET /media/app-automation/allure-reports/1/index.html` -> 403
- 登录态请求结果：
  - 现有数据库用户数：1。
  - 现有需求生成任务数：13。
  - 现有 App 自动化执行记录数：0。
  - `GET /api/requirement-analysis/config/check/` -> 200。
  - `GET /api/requirement-analysis/testcase-generation/not-existing-task/progress/` -> 404。
  - `GET /api/requirement-analysis/testcase-generation/not-existing-task/stream_progress/` -> 404。
  - `GET /api/app-automation/executions/999999999/report/` -> 404。
  - `GET /api/app-automation/executions/999999999/report/index.html` -> 404。
  - 使用现有 admin 访问其已有任务 `progress/` -> 200。
  - 使用现有 admin 访问其已有任务 `stream_progress/` -> 200。
- 未能验证的请求：
  - App 自动化报告真实存在文件的 200 响应：本地数据库 `AppTestExecution` 为 0，无可用执行记录。
  - 登录但无对象权限访问真实报告或真实任务的 403：本地只有 1 个用户，缺少第二用户和目标对象组合。

## 6. 失败和错误事件

- 本轮是否出现错误事件：是。
- 已写入或本轮补写 `error_event_log.md` 的事件：
  - P0.1 预检阶段路径读取和并行搜索命令失败。
  - P0.1 Execution 并发 worker 未返回可用产出。
  - `rg` 检索 design token 时模式被误识别为命令参数。
  - 前端 worker 临时 `rg` 组合命令引号解析失败，随后已用更窄命令替代完成验证。
  - 文档 worker 读取 / 路径基准纠偏问题，已把 VDD 放回内层仓库任务目录。
  - 主线程 `apply_patch` 包装器稳定返回 `Access is denied`，已记录并采用 UTF-8 PowerShell 定点写入作为文档收口降级方案。
- 是否升级到 `error_prevention_log.md`：暂不升级。当前多为工具 / 环境 / 命令写法事件，已在事件日志记录；若 `apply_patch` 在后续回合持续不可用，再升级沉淀。
- 未解决错误：无阻断性业务错误；真实页面验证和 App 报告对象级 200/403 属于未验证项。

## 7. 未验证项

- 未验证项 1：浏览器页面级主流程。
  - 未验证原因：本轮未启动前后端联调服务，没有可用浏览器登录态执行页面操作。
  - 可能风险：数据工厂和执行详情页虽然构建通过、请求封装静态正确，但参数、响应层级或错误提示仍可能存在页面运行时问题。
  - 后续补验证方式：登录后实际操作数据工厂查询 / 新增 / 删除 / 统计刷新，执行详情状态更新 / 历史 / 删除。
- 未验证项 2：App 自动化报告真实文件 200。
  - 未验证原因：本地数据库 `AppTestExecution` 数量为 0，没有可用报告记录和文件。
  - 可能风险：对象权限和路径校验静态正确，但真实报告路径、文件类型和前端打开方式仍需用真实数据确认。
  - 后续补验证方式：准备一条有 `report_path` 的 App 执行记录和报告文件，用执行人 / 项目 owner / 项目成员分别请求 200，用无权限用户请求 403。
- 未验证项 3：真实无权限对象 403。
  - 未验证原因：本地数据库只有 1 个用户，缺少无权限用户和目标对象组合。
  - 可能风险：无权限分支逻辑没有用真实对象触发。
  - 后续补验证方式：在测试库中准备第二用户和跨项目任务 / 报告对象，分别请求需求进度和报告文件。
- 未验证项 4：SSE 前端凭据携带。
  - 未验证原因：后端请求级验证能证明登录态可访问 SSE，但未验证浏览器 `EventSource` 在当前登录方式下是否能携带有效 cookie / session。
  - 可能风险：如果前端只依赖 localStorage JWT，原生 `EventSource` 不能带 Authorization header，后续需要 P0.2 实时连接封装处理。
  - 后续补验证方式：在浏览器登录态下打开需求生成任务，确认 SSE 能建立连接或按预期降级。

## 8. 残余风险

- 权限收紧可能暴露旧前端入口曾依赖匿名访问的问题。未登录被 401 拦截是目标行为，但页面是否给出友好提示还需浏览器验证。
- `RequirementAnalysisView.vue` 仍有 EventSource 相关历史注释和直接实时连接逻辑；TDD 已明确这属于 P0.2 实时连接封装范围，本轮不扩展。
- 设计 token 已接入共享基座，但 `--th-radius-lg` 当前仍为 20px，符合 Spec 中“P0.1 先建 token，不做明显视觉大改”的口径；后续如果要压到 8px，需要单独视觉任务确认。
- 工作区存在大量与 P0.1 无关的历史 / 并行未提交改动，本 VDD 只对 P0.1 点名范围和验证命令负责。

## 9. 回退和止损

- 可以直接回退的文件：
  - `frontend/src/assets/css/design-tokens.scss`
  - `frontend/src/assets/css/global.scss`
  - `frontend/src/components/page-shells/DashboardShell.vue`
  - `frontend/src/components/page-shells/DetailResultShell.vue`
  - `frontend/src/components/page-shells/ListShell.vue`
  - `frontend/src/components/page-shells/WorkspaceShell.vue`
  - `frontend/src/components/platform-shared/FilterBar.vue`
  - `frontend/src/components/platform-shared/UnifiedListTable.vue`
  - `frontend/src/api/data-factory.js`
  - `frontend/src/api/executions.js`
  - `frontend/src/components/DataFactorySelector.vue`
  - `frontend/src/views/data-factory/DataFactory.vue`
  - `frontend/src/views/executions/ExecutionDetailView.vue`
  - `frontend/src/main.js`
  - `frontend/src/utils/api.js`
  - `apps/requirement_analysis/views.py`
  - `apps/app_automation/views/execution_views.py`
  - `backend/urls.py`
  - `docs/tasks/2026-07-03-p0-1-full-stack-baseline/*`
- 不可直接回退的变更：无数据层变更。
- 回退后需要验证：前端构建、后端编译、裸 axios 扫描、权限静态扫描、未登录敏感接口 401/403。
- 是否涉及数据修复或迁移回滚：否。

## 10. 最终结论

- 是否达到本轮目标：达到 P0.1 第一批代码级和请求级目标。
- 是否可以交付：可以作为 P0.1 第一批交付，但不能替代上线前完整浏览器回归。
- 本轮最高可信度：V3（有限请求级验证）。
- 需要继续补的验收：浏览器页面主流程、App 报告真实文件 200、真实无权限对象 403、浏览器 EventSource 凭据行为。
- 下一步建议：进入下一批 P0 前，优先准备一套 App 执行报告样本和双用户权限样本，把本轮未验证项补成完整行为回归。
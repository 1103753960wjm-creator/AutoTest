# VDD

## 1. 标题

- 任务名称：AI 需求分析生成用例结果处理与保存按钮闭环修复
- 日期：2026-07-09
- 关联 Spec/SDD：`docs/tasks/2026-07-09-ai-generated-result-processing-fix/spec-sdd.md`
- 关联 TDD：`docs/tasks/2026-07-09-ai-generated-result-processing-fix/tdd.md`
- 当前阶段：VDD
- 本轮最高验证等级：V2 构建验证

## 2. 本轮改了什么

- 大白话总结：
  - 对比原生代码后确认，原生系统把“勾选用例、采纳、弃用、编辑保存”放在 `TaskDetail.vue` 详情弹窗里；当前项目已经把 `TaskDetail` 收口为任务对象页，却没有在 `GeneratedTestCaseList.vue` 补齐等价结果处理能力，所以用户能看到生成任务，但很多单条 / 多选 / 采纳 / 不通过动作没有可用入口或会绕回详情页。
  - 本轮没有回退对象分层，而是在结果批次页新增“处理结果”抽屉，专门处理 AI 生成出来的结果行。
  - 生成完成页原来的“保存到用例记录”实际走旧 `/save_to_records/` 心智，和当前 `pending/adopted/discarded` 结果状态模型脱节。本轮改为“采纳全部待处理结果”，调用当前后端的 `batch_adopt/`，并补 loading、防重复、项目归属和空数据检查。
- 修改的主要文件：
  - `frontend/src/api/requirement-analysis.js`
  - `frontend/src/views/requirement-analysis/GeneratedTestCaseList.vue`
  - `frontend/src/views/requirement-analysis/RequirementAnalysisView.vue`
  - `frontend/src/views/requirement-analysis/TaskDetail.vue`
  - `docs/project-memory/error_event_log.md`
- 新增的主要文件：
  - `docs/tasks/2026-07-09-ai-generated-result-processing-fix/spec-sdd.md`
  - `docs/tasks/2026-07-09-ai-generated-result-processing-fix/tdd.md`
  - `docs/tasks/2026-07-09-ai-generated-result-processing-fix/vdd.md`
- 没有改但容易被误解的范围：
  - 没有修改原生参考目录 `E:\原生testhub_platform-main\testhub_platform-main`。
  - 没有修改后端模型、迁移、AI 生成主链、AI 评审主链、SSE / polling 主链。
  - 没有把 `TaskDetail` 恢复成原生那种大而全结果处理页。
  - “不通过 / 删除某条用例”按结果状态 `discarded` 处理，不物理删除 AI 原始结果。

## 3. 验收标准核对

| 验收项 | 是否通过 | 证据 | 备注 |
| --- | --- | --- | --- |
| 生成完成页按钮不再走旧保存主入口 | 是 | `RequirementAnalysisView.vue` 中主按钮改为 `adoptAllGeneratedResults()`，调用 `batch_adopt/` 封装；保留 `saveToTestCaseRecords()` 只作为兼容包装 | 未删除后端旧 `/save_to_records/` |
| 结果批次页能进入处理生成结果 | 是 | `GeneratedTestCaseList.vue` 新增“处理结果”动作和抽屉；双击行也进入处理抽屉 | 真实浏览器点击未执行 |
| 支持单选 / 多选 / 全部采纳 | 是 | 抽屉内新增选择列、`采纳选中`、`采纳全部待处理`、单行 `采纳`，均只允许 `pending` 行 | 后端接口真实请求未执行 |
| 支持单条 / 多选 / 全部不通过 | 是 | 抽屉内新增 `弃用选中`、`弃用全部待处理`、单行 `不通过`，调用现有弃用接口，保留原始结果 | 后端接口真实请求未执行 |
| 已处理结果不能再当源结果编辑 | 是 | `pending` 以外行禁用编辑、采纳、弃用；已采纳行可进入正式资产 | 正式资产详情页真实打开未执行 |
| 生成结果编辑后能保存回任务正文 | 是 | 抽屉编辑弹窗调用 `update-test-cases/` 封装，按表格格式重建 `final_test_cases` | 后端真实保存未执行 |
| 缺项目归属时不静默采纳 | 是 | 完成页和结果处理页都会检查项目；缺少项目时提示用户先选择或绑定项目 | 避免后端落到第一个项目或默认项目 |
| 不新增整页刷新兜底 | 是 | `rg -n "window\.location\.reload|window\.location\.href|location\.assign" frontend\src\views\requirement-analysis` 无命中 | 命令退出码 1 表示无命中 |
| 新增结果处理接口走 API 封装 | 是 | 新增 `frontend/src/api/requirement-analysis.js` 封装；页面调用封装函数 | 历史页面中仍有既有直接 `api` 请求，本轮没有做全量重构 |

## 4. 验证执行记录

| 验证类型 | 命令或操作 | 结果 | 证据 |
| --- | --- | --- | --- |
| 规则检查 | `powershell -ExecutionPolicy Bypass -File scripts\rule_check.ps1` | 通过 | 输出 `Rule check passed: no P0 redline hits.` |
| 构建验证 | `cd frontend && cmd /c npm run build` | 通过 | Vite 构建成功，仍只有既有 `web-tree-sitter` 的 `fs/path` externalized 和 `eval` 警告 |
| Diff 格式检查 | `git diff --check -- frontend/src/api/requirement-analysis.js frontend/src/views/requirement-analysis/GeneratedTestCaseList.vue frontend/src/views/requirement-analysis/RequirementAnalysisView.vue frontend/src/views/requirement-analysis/TaskDetail.vue docs/tasks/2026-07-09-ai-generated-result-processing-fix docs/project-memory/error_event_log.md` | 通过 | 只有 Windows 行尾转换提示 |
| 静态红线扫描 | `rg -n "window\.location\.reload|window\.location\.href|location\.assign" frontend\src\views\requirement-analysis` | 通过 | 无命中 |
| 按钮规则扫描 | `rg --pcre2 -n "<button(?![^>]*type=)" ...` | 通过，存在一条误报 | 命中 `RequirementAnalysisView.vue:339`，实际 `type="button"` 在下一行 |
| 新增端点散写扫描 | `rg -n "api\.post\(`/requirement-analysis/testcase-generation/.*/(batch_adopt|batch-adopt-selected|batch_discard|discard-selected-cases|discard-single-case|update-test-cases)|api\.get\(`/requirement-analysis/testcase-generation/.*/progress" frontend\src\views\requirement-analysis` | 通过 | 无命中，新增结果处理接口已走 API 封装 |
| 接口验证 | 真实后端请求 | 未执行 | 本轮没有启动后端造任务数据 |
| 页面验证 | 浏览器真实点击 | 未执行 | 本轮未启动 dev server / Playwright 页面流程 |

## 5. 失败和错误事件

- 本轮是否出现错误事件：是。
- 已写入 `error_event_log.md` 的事件：
  - `2026-07-09 00:15 - AI 结果处理 Spec 补充阶段多条读取命令超时`
  - `2026-07-09 00:15 - apply_patch 基准目录不在真实项目内导致 Spec 误落外层`
  - `2026-07-09 00:55 - AI 结果处理 Execution 收尾阶段验证命令误用和扫描超时`
  - `2026-07-09 01:00 - 原生参考目录不是 Git 仓库导致状态核对命令失败`
- 是否升级到 `error_prevention_log.md`：否。
- 未解决错误：无。本轮失败都已用更窄扫描、API 封装、构建验证或规则检查替代处理。

## 6. 未验证项

- 未验证项 1：真实浏览器端完整流程。
- 未验证原因：本轮没有启动前后端服务和 Playwright，最高只做到构建验证。
- 可能风险：Element Plus 抽屉表格在真实数据特别长时仍可能需要微调列宽或滚动体验。
- 后续如何补验证：准备一个已完成生成任务，按 TDD 的 TC-01 到 TC-13 手工或 Playwright 跑一遍。

- 未验证项 2：真实后端接口行为。
- 未验证原因：未创建真实 `pending/adopted/discarded` 样本任务，也未登录调用接口。
- 可能风险：旧数据解析出来的 `index/case_id` 若和后端解析不一致，选中采纳或弃用可能返回 400。
- 后续如何补验证：用真实任务分别调用 `batch_adopt/`、`batch-adopt-selected/`、`batch_discard/`、`discard-selected-cases/`、`discard-single-case/`、`update-test-cases/`。

- 未验证项 3：AI 自动评审主链。
- 未验证原因：本轮不改 AI 模型调用和自动评审流程。
- 可能风险：如果 AI 生成阶段本身返回空字符串，后端 `AIModelService.review_test_cases[_stream]` 仍会按设计报“待评审测试用例为空”。
- 后续如何补验证：单独构造模型返回空内容和正常内容两类任务，确认生成阶段错误提示、自动评审记录和前端展示一致。

## 7. 残余风险

- 风险 1：当前项目历史上很多需求分析页面还直接使用 `@/utils/api`，本轮只把新增结果处理接口收口到 `frontend/src/api/requirement-analysis.js`，没有做全量请求入口重构。
- 风险 2：后端 `_resolve_task_target_project()` 在前端不传项目时可能回退到用户第一个项目或默认项目；本轮前端已阻断缺项目采纳，但后端兼容逻辑仍存在。
- 风险 3：`buildFinalTestCasesContent()` 会把编辑后的结果重建成 Markdown 表格；后端解析支持表格，但真实长文本、特殊字符和历史格式仍需要真实任务验证。

## 8. 回退和止损

- 可以直接回退的文件：
  - `frontend/src/api/requirement-analysis.js`
  - `frontend/src/views/requirement-analysis/GeneratedTestCaseList.vue`
  - `frontend/src/views/requirement-analysis/RequirementAnalysisView.vue`
  - `frontend/src/views/requirement-analysis/TaskDetail.vue`
  - `docs/tasks/2026-07-09-ai-generated-result-processing-fix/`
- 不可直接回退的变更：
  - 无数据库迁移、无后端模型改动、无运行数据改动。
- 回退后需要验证什么：
  - `cd frontend && cmd /c npm run build`
  - `powershell -ExecutionPolicy Bypass -File scripts\rule_check.ps1`
- 是否涉及数据修复或迁移回滚：否。

## 9. 最终结论

- 是否达到本轮目标：部分达到。
- 是否可以交付：可以交付前端代码和文档，但应补真实浏览器 / 真实接口回归。
- 需要用户继续确认的事项：
  - 是否允许下一轮启动本地前后端，用真实任务跑结果处理主流程。
- 下一步建议：
  - 用一条真实已完成生成任务验证：生成完成页“采纳全部待处理结果” -> 结果批次页“处理结果” -> 单条采纳 -> 多选弃用 -> 编辑保存 -> 正式资产入口。

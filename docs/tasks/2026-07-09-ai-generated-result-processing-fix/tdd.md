# TDD

## 1. 标题

- 任务名称：AI 需求分析生成用例结果处理与保存按钮闭环修复
- 日期：2026-07-09
- 关联 Spec/SDD：`docs/tasks/2026-07-09-ai-generated-result-processing-fix/spec-sdd.md`
- 当前阶段：TDD
- 目标验证等级：V3 页面行为验证

## 2. 大白话测试目标

- 这次测试要证明什么：
  - 生成测试用例后，用户能在结果批次页真正处理每条生成结果，不再只能看详情。
  - 用户能单条、批量、全部采纳生成结果，采纳后正式测试资产入口可用。
  - 用户能单条、批量、全部标记“不通过 / 弃用”，状态变成 `discarded`，不是物理删除原始结果。
  - 生成完成页按钮不再无响应，也不再用旧“保存”心智绕过结果状态模型。
- 用户最关心的结果是什么：
  - 点按钮一定有反馈。
  - 能选中要处理的用例。
  - 能确认 / 采纳用例。
  - 能把不通过用例排除掉。
  - 成功后数量和状态能刷新。
- 哪些旧功能不能被破坏：
  - AI 生成任务创建、模型调用、流式输出、取消、自动评审和轮询恢复不变。
  - `TaskDetail` 仍只做任务详情和结果预览，不恢复成原生大而全处理页。
  - 任务级删除仍是删除整个生成任务，不和结果弃用混用。
  - 已采纳正式测试用例的来源回链继续可用。

## 3. 测试范围

- 必测模块：
  - AI 需求分析生成用例。
  - AI 生成结果批次页。
  - 任务详情页结果预览入口。
- 必测页面：
  - `RequirementAnalysisView.vue`
  - `GeneratedTestCaseList.vue`
  - `TaskDetail.vue`
- 必测接口：
  - `GET /requirement-analysis/testcase-generation/{task_id}/progress/`
  - `POST /requirement-analysis/testcase-generation/{task_id}/batch_adopt/`
  - `POST /requirement-analysis/testcase-generation/{task_id}/batch-adopt-selected/`
  - `POST /requirement-analysis/testcase-generation/{task_id}/batch_discard/`
  - `POST /requirement-analysis/testcase-generation/{task_id}/discard-selected-cases/`
  - `POST /requirement-analysis/testcase-generation/{task_id}/discard-single-case/`
  - `POST /requirement-analysis/testcase-generation/{task_id}/update-test-cases/`
- 必测数据或状态：
  - `pending`
  - `adopted`
  - `discarded`
  - `processing_status_summary.pending_count`
  - `processing_status_summary.adopted_count`
  - `processing_status_summary.discarded_count`
  - `adopted_testcase_id`
- 不测范围及原因：
  - 不测真实 AI 模型生成质量，因为本轮修复的是生成后的结果处理页面。
  - 不测 Celery、Channels、WebSocket 和报告链路，因为本轮不改这些链路。
  - 不测原生参考目录，因为原生代码只作为对比来源。

## 4. 测试数据准备

- 需要什么账号或权限：
  - 一个可登录账号。
  - 账号至少能访问一个测试设计项目。
- 需要什么项目、用例、任务或历史数据：
  - 项目 A：用于采纳生成结果为正式测试用例。
  - 已完成生成任务 T1：至少 3 条生成结果，初始状态均为 `pending`。
  - 已部分处理任务 T2：至少 1 条 `adopted`、1 条 `discarded`、1 条 `pending`。
  - 无项目归属任务 T3：用于验证前端阻断提示。
- 需要准备哪些正常数据：
  - 用例 1：完整场景、前置条件、步骤、预期、优先级。
  - 用例 2：长步骤文本，用于验证抽屉表格不挤压错位。
  - 用例 3：优先级为空或缺省，用于验证默认展示。
- 需要准备哪些异常数据：
  - 没有 `task_id` 的前端状态。
  - 任务未完成状态，如 `generating`。
  - `pending_count = 0` 的任务。
  - 后端接口返回 400 / 500 的失败响应。
- 是否需要旧数据兼容样本：
  - 需要。至少准备一条旧任务，它没有完整 `result_status_snapshot`，但 `progress/` 仍能返回可展示的 `generated_results`。

## 5. 主流程用例

| 编号 | 操作步骤 | 预期结果 | 通过标准 |
| --- | --- | --- | --- |
| TC-01 | 在生成完成页点击“进入结果处理” | 跳转到结果批次页，并定位当前任务 | URL 或列表焦点携带当前 `task_id`，页面不报错 |
| TC-02 | 在结果批次页点击某任务“处理结果” | 打开处理抽屉，拉取 `progress/` | 抽屉展示生成结果和状态摘要 |
| TC-03 | 勾选 2 条 `pending` 结果后点击“采纳选中” | 后端调用选中采纳接口，成功后状态刷新 | 选中结果变为 `adopted`，待处理数量减少 |
| TC-04 | 点击某条 `pending` 结果的“采纳” | 单条采纳成功 | 该行变为 `adopted`，出现正式资产入口 |
| TC-05 | 点击“采纳全部待处理结果” | 所有 `pending` 结果被采纳 | `pending_count = 0`，`adopted_count` 增加 |
| TC-06 | 勾选 2 条 `pending` 结果后点击“弃用选中” | 二次确认后调用选中弃用接口 | 选中结果变为 `discarded`，不从列表消失 |
| TC-07 | 点击某条 `pending` 结果的“不通过 / 弃用” | 单条弃用成功 | 该行变为 `discarded`，不能再次选择 |
| TC-08 | 点击“弃用全部待处理结果” | 二次确认后所有待处理结果被弃用 | `pending_count = 0`，`discarded_count` 增加 |
| TC-09 | 编辑一条 `pending` 结果后保存 | 调用 `update-test-cases/`，再刷新 `progress/` | 关闭再打开抽屉仍能看到编辑后的内容 |
| TC-10 | 在 `TaskDetail` 预览结果后点击“处理生成结果” | 跳到结果批次页处理入口 | 详情页仍不出现采纳 / 弃用主按钮 |
| TC-11 | 在生成完成页点击“采纳全部待处理结果” | 按钮进入 loading，成功后刷新当前任务状态 | 请求期间不能重复点击，成功提示包含数量 |

## 6. 异常和边界用例

| 编号 | 场景 | 操作步骤 | 预期结果 | 通过标准 |
| --- | --- | --- | --- | --- |
| EX-01 | 缺少任务 ID | 构造 `generationResult` 为空或没有 `task_id` 后点击采纳 | 前端阻断 | 不发采纳请求，提示“缺少任务 ID / 请刷新或进入任务详情” |
| EX-02 | 任务未完成 | 对 `generating` 任务点击采纳 | 前端或后端阻断 | 提示任务未完成，结果状态不变化 |
| EX-03 | 没有最终结果 | `final_test_cases` 为空时点击采纳 | 前端阻断 | 不发采纳请求，提示没有可采纳结果 |
| EX-04 | 没有待处理结果 | `pending_count = 0` 时点击采纳或弃用 | 前端阻断 | 不发处理请求，提示已无待处理结果 |
| EX-05 | 没有选中结果 | 直接点击“采纳选中 / 弃用选中” | 前端阻断 | 不发请求，提示先选择结果 |
| EX-06 | 已采纳结果再次处理 | 尝试选择或弃用 `adopted` 行 | UI 禁用或后端阻断 | 不能选中，不能把已采纳改成弃用 |
| EX-07 | 已弃用结果再次处理 | 尝试选择或再次弃用 `discarded` 行 | UI 禁用或后端阻断 | 不能选中，提示该结果已弃用 |
| EX-08 | 快速重复点击 | 连续点击采纳 / 保存按钮多次 | 只有一次请求生效 | 按钮 loading，重复点击不重复提交 |
| EX-09 | 无项目归属 | 对 T3 点击采纳 | 前端阻断 | 提示选择或绑定项目，不静默创建或假成功 |
| EX-10 | 后端 400 | 模拟接口返回“已无待处理结果” | 页面展示明确失败原因并刷新状态 | 不显示假成功，状态以刷新后的后端数据为准 |
| EX-11 | 后端 500 | 模拟接口失败 | 页面保留当前抽屉和选择态 | 显示错误原因，不清空本地列表制造成功假象 |
| EX-12 | 旧数据兼容 | 打开没有 `result_status_snapshot` 的旧任务 | 页面可展示并允许处理待处理结果 | 不报空指针，不显示空表误导 |

## 7. 回归检查

- 受影响旧入口：
  - 需求分析生成完成页。
  - AI 生成结果批次页。
  - 任务详情页。
  - 正式测试资产入口。
- 受影响旧字段：
  - `final_test_cases`
  - `generated_test_cases`
  - `generated_results`
  - `result_status_snapshot`
  - `processing_status_summary`
  - `is_saved_to_records`
  - `adopted_testcase_id`
- 受影响旧页面：
  - 生成完成后下载 Excel 功能不能被破坏。
  - `TaskDetail` 仍可查看结果预览。
  - `GeneratedTestCaseList` 任务列表分页、筛选、删除任务不能被破坏。
- 受影响缓存、轮询、异步任务、日志或通知：
  - 只检查任务进度恢复和 `progress/` 消费，不改 AI 生成轮询主链。
  - 不新增通知。
  - 不改异步任务。

## 8. 验证命令和页面操作

- 静态验证命令：
  - `rg -n "save_to_records|batch_adopt|batch-adopt-selected|discard-selected-cases|discard-single-case|update-test-cases" frontend/src/views/requirement-analysis apps/requirement_analysis/views.py`
  - `rg -n "window.location.reload|window.location.href|location.assign" frontend/src/views/requirement-analysis`
  - `git diff --check -- frontend/src/views/requirement-analysis apps/requirement_analysis docs/tasks/2026-07-09-ai-generated-result-processing-fix`
- 构建或编译验证命令：
  - `cd frontend && cmd /c npm run build`
  - 如果后端有改动：`.\venv\Scripts\python.exe -m py_compile apps\requirement_analysis\views.py apps\requirement_analysis\models.py apps\requirement_analysis\result_status.py`
- 接口验证方式：
  - 优先使用浏览器页面触发真实请求。
  - 如本地后端可用，至少核对一次 `progress/` 响应中 `generated_results` 和 `processing_status_summary` 被页面消费。
  - 如后端不可用，交付时必须说明接口级验证未执行原因。
- 页面验证路径：
  - 登录平台。
  - 进入测试设计 / AI 需求分析。
  - 进入生成完成页或结果批次页。
  - 打开结果处理抽屉。
  - 验证单条采纳、批量采纳、单条弃用、批量弃用、编辑保存、已处理禁用。
- 是否需要执行 `scripts/rule_check.ps1`：是。
  - 原因：本轮改前端关键交互和 AI 结果处理链路，执行规则检查能提前发现表单、按钮、请求入口和路由类回归。

## 9. 失败判定

- 出现哪些现象算失败：
  - 点击按钮没有 loading、没有提示、没有请求或没有任何可见反馈。
  - “编辑”仍跳回任务详情页，用户无法处理结果。
  - `adopted` 或 `discarded` 结果仍可被选择并重复处理。
  - 弃用后结果从原始列表消失，导致追溯断掉。
  - 保存 / 采纳成功提示出现，但刷新后状态没有变化。
  - 缺少项目归属时仍提示成功。
  - 页面直接调用旧 `save_to_records/` 作为主处理入口。
  - 改动恢复了 `TaskDetail` 的采纳 / 弃用主战场职责。
  - 构建失败或控制台出现关键红错。
- 验证连续失败几次必须暂停：
  - 同一失败连续 2 次必须暂停，先记录错误事件再判断是否超出范围。
- 失败后允许修复的范围：
  - 允许在 `RequirementAnalysisView.vue`、`GeneratedTestCaseList.vue`、`TaskDetail.vue` 和必要 i18n 文案内修复。
  - 如发现必须修改后端接口契约、数据模型或新增迁移，必须暂停回到 Spec。
- 失败后必须写入的日志：
  - 任意构建失败、接口异常、页面红错、验证失败或工具阻塞，必须写入 `docs/project-memory/error_event_log.md`。

## 10. 进入 Execution 条件

- [x] 主流程用例已明确。
- [x] 异常和边界用例已明确。
- [x] 验证命令已明确。
- [x] 失败判定已明确。
- [ ] 用户已确认可以进入实现。

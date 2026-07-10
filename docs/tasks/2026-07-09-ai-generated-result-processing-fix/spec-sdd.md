# Spec/SDD

## 背景

### 当前问题

- 用户在“AI 需求分析生成测试用例”后，进入生成结果相关页面时，发现结果处理链路不闭环：
  - 详情表格页无法确认 / 采纳用例。
  - 无法单选、多选后批量处理生成用例。
  - 无法把单条或多条用例标记为“不通过 / 弃用”。
  - 无法清楚地区分“删除任务”和“弃用某条 AI 生成结果”。
  - 生成完成页点击“保存到用例记录”时，可能无响应，或首次点击直接提示保存失败。
- 本轮只以原生代码 `E:\原生testhub_platform-main\testhub_platform-main` 作为参考，不允许修改原生代码。

### 触发原因

- 原生系统的 `TaskDetail.vue` 里，详情弹窗承担完整处理能力：
  - 勾选用例。
  - 单条 / 批量采纳。
  - 单条 / 批量弃用。
  - 编辑后点击 `saveEdit()`，调用 `/requirement-analysis/testcase-generation/{task_id}/update-test-cases/` 保存最新用例内容。
- 当前项目已经把对象边界调整为：
  - `TaskDetail` 只负责任务信息、结果预览、状态展示和跳转入口。
  - `GeneratedTestCaseList` 作为结果批次页，负责结果处理状态和批量动作。
- 迁移没有完全收口：
  - `TaskDetail.vue` 已移除原生的编辑 / 保存 / 勾选处理能力，但结果批次页还没有提供等价的“处理结果”抽屉或面板。
  - `GeneratedTestCaseList.vue` 里已有后端处理方法雏形，例如 `batchAdoptTask()`、`batchDiscardTask()`，但可见表格操作区没有真正暴露“处理结果”的完整入口。
  - `openEditTask()` 当前只是跳回详情页，形成“点编辑 -> 看详情 -> 再提示去结果批次页”的循环。
  - 生成完成页 `RequirementAnalysisView.vue` 的“保存到用例记录”仍直接调用旧接口 `/save_to_records/`，但当前后端已经升级为 `pending/adopted/discarded` 结果处理状态，用户看到的是“保存”心智，系统实际需要的是“采纳生成结果为正式测试用例”心智。
  - `TaskDetail.vue` 中“前往结果批次页”按钮仍复用 `save-btn` 样式名，虽然文案不是保存，但会误导排查和后续维护。

## 当前生效规则

- 根规则：`AGENTS.md`、`C:\Users\Administrator\.gemini\GEMINI.md`。
- 前端规则：`frontend/AGENTS.md`。
- 需求分析模块规则：`apps/requirement_analysis/AGENTS.md`。
- 关键流程规则：非小修小改，必须按 `Spec/SDD -> TDD -> Execution -> VDD` 推进。
- 当前自治等级：L0 / L2 边界之间。
  - 由于本轮涉及 AI 生成结果状态、前端主交互、后端采纳 / 弃用接口联动，先按 L0 输出 Spec，不直接实现。
  - 用户确认 Spec 和后续 TDD 后，限定范围内可进入 L2 Execution。
- 是否允许受控 Loop：当前 Spec 阶段不进入 Loop；如后续实现后验证失败，再按确认后的 TDD 判断是否需要 L3 Loop 合同。

## 目标

- 在不回退当前对象分层的前提下，补齐 AI 生成结果处理闭环。
- 让用户在结果批次页能够完成以下动作：
  - 查看某个生成任务下的全部 AI 生成结果。
  - 单选 / 多选待处理结果。
  - 单条采纳、批量采纳、全部待处理结果采纳。
  - 单条弃用 / 不通过、批量弃用 / 不通过。
  - 编辑生成结果内容后保存，再继续采纳。
  - 处理后刷新状态摘要，能看到 `pending/adopted/discarded` 数量变化。
- 修复“生成完成后点击保存按钮无响应 / 初次保存失败”的体验：
  - 保存按钮必须有 loading、禁用、防重复提交和缺失数据检查。
  - 保存动作必须有明确成功、失败和阻断原因。
  - 保存动作必须和当前结果状态模型一致，不继续给用户一个和状态机平行的旧保存心智。

## 非目标

- 不修改原生参考目录。
- 不把 `TaskDetail` 恢复成原生系统里的结果处理主战场。
- 不重写 AI 生成任务创建、模型调用、流式输出、取消、自动评审、轮询恢复主链。
- 不改数据模型、不新增迁移。
- 不物理删除 AI 原始生成结果。
  - 用户说的“删除 / 不通过用例”，本轮默认按“弃用该条结果”处理，也就是后端状态 `discarded`。
  - 任务级删除仍沿用现有删除任务能力，不和“弃用某条结果”混用。
- 不改正式测试资产页的对象职责。

## 范围

### 受影响模块

- 前端：
  - `frontend/src/views/requirement-analysis/RequirementAnalysisView.vue`
  - `frontend/src/views/requirement-analysis/TaskDetail.vue`
  - `frontend/src/views/requirement-analysis/GeneratedTestCaseList.vue`
  - 如需补文案，再看 `frontend/src/locales/lang/zh-cn/requirement.js`、`frontend/src/locales/lang/en/requirement.js`
- 后端：
  - 优先复用 `apps/requirement_analysis/views.py` 现有接口。
  - 本轮默认不新增接口，除非 TDD 阶段确认现有接口无法覆盖前端处理闭环。

### 现有可复用接口

- 查看任务进度和生成结果：
  - `GET /requirement-analysis/testcase-generation/{task_id}/progress/`
  - 返回 `generated_results` 和 `processing_status_summary`。
- 全部待处理结果采纳：
  - `POST /requirement-analysis/testcase-generation/{task_id}/batch_adopt/`
- 选中结果采纳：
  - `POST /requirement-analysis/testcase-generation/{task_id}/batch-adopt-selected/`
- 全部待处理结果弃用：
  - `POST /requirement-analysis/testcase-generation/{task_id}/batch_discard/`
- 选中结果弃用：
  - `POST /requirement-analysis/testcase-generation/{task_id}/discard-selected-cases/`
- 单条结果弃用：
  - `POST /requirement-analysis/testcase-generation/{task_id}/discard-single-case/`
- 保存编辑后的结果内容：
  - `POST /requirement-analysis/testcase-generation/{task_id}/update-test-cases/`
- 旧一键保存入口：
  - `POST /requirement-analysis/testcase-generation/{task_id}/save_to_records/`
  - 本轮定位为兼容入口，不再作为前端主心智。

## 已知事实

- 当前 `TaskDetail.vue` 的弹窗底部只有“查看正式资产 / 前往结果批次页 / 关闭”，没有原生的 `saveEdit()`、`startEdit()`、`cancelEdit()` 处理链。
- 当前 `TaskDetail.vue` 已明确文案：“当前弹窗只保留结果预览。如需采纳、弃用或调整这条结果，请前往结果批次页统一处理。”
- 当前 `GeneratedTestCaseList.vue` 表格可见操作主要是“详情 / 正式资产 / 编辑 / 删除”，没有结果级处理抽屉。
- 当前 `GeneratedTestCaseList.vue` 的 `openEditTask()` 会调用 `viewTaskDetail(task)`，实际没有进入编辑或处理。
- 当前 `RequirementAnalysisView.vue` 的“保存到用例记录”直接调用 `save_to_records/`，没有 loading、没有防重复提交，也没有先检查 `generationResult.task_id`、`final_test_cases`、项目上下文和处理状态。
- 当前后端已经有 `result_status_snapshot`、`generated_results`、`processing_status_summary` 和采纳 / 弃用接口；主要缺口在前端交互没有把这些能力串起来。
- 当前防复发手册已有错误模式：任务对象、结果对象、正式资产对象边界混淆。此轮必须继承“任务页只做任务，结果批次页做结果处理”的边界。

## 根因判断

### 1. 详情页能力迁出后，结果批次页没有补等价入口

- 原生系统把“预览、编辑、保存、采纳、弃用、选择”都放在 `TaskDetail.vue`。
- 当前项目按对象边界把处理能力迁出 `TaskDetail.vue`，这是正确方向。
- 但 `GeneratedTestCaseList.vue` 没有补一个真正的结果处理面板，导致用户从任务页被引导到结果批次页后，仍找不到确认、单选、多选、弃用这些动作。

### 2. “保存”语义没有跟随结果状态模型升级

- 原生的“保存”更多是“把生成结果导入正式测试用例记录”。
- 当前项目已经把结果状态改为：
  - `pending`：待处理。
  - `adopted`：已采纳为正式测试用例。
  - `discarded`：已弃用 / 不通过。
- 因此前端继续展示一个直接打 `/save_to_records/` 的“保存”按钮，会让用户以为这是独立保存流程；实际它应该表达为“采纳待处理结果为正式测试用例”。

### 3. 保存按钮缺少操作闭环保护

- 当前 `saveToTestCaseRecords()` 没有按钮 loading，也没有禁用重复点击。
- 没有在请求前检查：
  - 是否已有 `generationResult.task_id`。
  - 是否已有最终结果。
  - 当前任务是否已完成。
  - 是否还有待处理结果。
  - 是否具备清晰项目归属。
- 失败时只用短暂 `ElMessage.error`，用户容易感知为无响应或不知道失败原因。

### 4. 样式命名和按钮职责混淆

- `TaskDetail.vue` 里“前往结果批次页”按钮仍使用 `save-btn` class。
- 这不一定直接导致功能失败，但会误导维护者继续按“保存按钮”排查，也容易造成样式和行为复用混乱。

## 方案设计

### 方案总原则

- 不恢复原生详情页大而全模式。
- 把结果处理动作统一放到结果批次页。
- 生成完成页的“保存”按钮改成“全部采纳 / 处理生成结果”的清晰入口。
- 旧接口能复用就复用，不新增平行接口。

### 1. 结果批次页新增“处理结果”入口

- 在 `GeneratedTestCaseList.vue` 的任务行操作区，把当前误导性的“编辑”替换为“处理结果”。
- 点击“处理结果”后，打开抽屉或弹窗。
- 抽屉打开时调用：
  - `GET /requirement-analysis/testcase-generation/{task_id}/progress/`
- 抽屉展示：
  - 任务标题、任务 ID、所属项目。
  - 状态摘要：待处理、已采纳、已弃用。
  - 生成结果表格。
  - 每条结果的场景、前置条件、步骤、预期、优先级、处理状态。
  - 已采纳结果的“查看正式资产”入口。

### 2. 结果处理表格支持单选和多选

- 表格第一列使用选择框。
- 只允许选择 `pending` 状态的结果。
- `adopted` 和 `discarded` 禁用选择，并显示原因。
- 顶部批量按钮：
  - “采纳选中”
  - “弃用选中”
  - “采纳全部待处理”
  - “弃用全部待处理”
- 行内按钮：
  - “查看”
  - “编辑”
  - “采纳”
  - “不通过 / 弃用”
  - “查看正式资产”（仅已采纳且有正式用例 ID 时显示）

### 3. 采纳动作对接现有接口

- “采纳全部待处理”调用：
  - `POST /requirement-analysis/testcase-generation/{task_id}/batch_adopt/`
- “采纳选中”调用：
  - `POST /requirement-analysis/testcase-generation/{task_id}/batch-adopt-selected/`
  - 请求体包含选中的 `test_cases`。
- “采纳单条”复用选中采纳接口，传一条 `test_cases`。
- 成功后：
  - 重新拉取 `progress/`。
  - 刷新结果批次列表。
  - 更新 `processing_status_summary`。
  - 明确提示创建数量、幂等命中数量、剩余待处理数量。

### 4. 不通过 / 删除动作统一按弃用处理

- “弃用全部待处理”调用：
  - `POST /requirement-analysis/testcase-generation/{task_id}/batch_discard/`
- “弃用选中”调用：
  - `POST /requirement-analysis/testcase-generation/{task_id}/discard-selected-cases/`
  - 请求体包含 `case_indices`。
- “弃用单条”调用：
  - `POST /requirement-analysis/testcase-generation/{task_id}/discard-single-case/`
  - 请求体包含 `case_index`。
- 页面文案使用“弃用 / 不通过”，避免用户误以为会物理删除 AI 原始结果。
- 任务行原有“删除”继续表示删除整个生成任务，需要保留二次确认。

### 5. 编辑后保存对接 `update-test-cases`

- 在结果处理抽屉中提供单条编辑能力。
- 编辑保存时：
  - 先更新前端当前结果数组。
  - 重新生成后端需要的 `final_test_cases` 字符串。
  - 调用 `POST /requirement-analysis/testcase-generation/{task_id}/update-test-cases/`。
  - 保存成功后重新拉取 `progress/`。
- 不直接复刻原生 `TaskDetail.vue` 的整页编辑模式，而是把编辑能力放在结果处理抽屉里。
- 已采纳结果原则上不允许继续编辑源结果；如要修改正式资产，应点击“查看正式资产”进入正式资产编辑流程。

### 6. 修复生成完成页保存按钮

- `RequirementAnalysisView.vue` 中生成完成后的“保存到用例记录”按钮不再直接表达旧的“保存记录”心智。
- 推荐改为两个清晰入口之一：
  - 主按钮：“采纳全部待处理结果”。
  - 次按钮：“进入结果处理”。
- 如果保留一键动作，前端应改为调用 `batch_adopt/`，并在请求前检查：
  - `generationResult?.task_id` 必须存在。
  - `generationResult.status === 'completed'`。
  - `finalTestCases` 或 `generationResult.final_test_cases` 必须有内容。
  - 当前任务还有 `pending_count > 0`。
  - 能明确项目归属；如果当前页面有项目选择，要随请求带 `project_id`。
- 按钮必须有：
  - `isSavingRecords` loading。
  - 请求中禁用。
  - 重复点击保护。
  - 成功后刷新任务进度。
  - 失败时弹出清晰原因，不只给一条可能错过的短提示。
- 旧 `/save_to_records/` 后端接口暂时保留，作为兼容入口；前端主交互不再优先使用它。

### 7. 修正详情页误导性按钮样式

- `TaskDetail.vue` 中“前往结果批次页”按钮不再使用 `save-btn` class。
- 改成更符合职责的命名，例如：
  - `handoff-btn`
  - `process-results-btn`
- 文案建议从“前往结果批次页”优化为“处理生成结果”，让用户明确下一步能做采纳和弃用。

## 数据 / 状态变化

- 不新增状态枚举。
- 继续使用现有结果状态：
  - `pending`
  - `adopted`
  - `discarded`
- 所有处理后状态以 `progress/` 返回的 `generated_results` 和 `processing_status_summary` 为前端真源。
- 不把前端本地数组当长期真源；每次采纳、弃用、编辑保存后都重新拉取后端状态。

## 交互反馈要求

- 阻断型问题必须明确提示：
  - 任务还没完成，不能采纳。
  - 没有待处理结果，不能重复采纳 / 弃用。
  - 没有选中结果，不能批量处理。
  - 已采纳结果不能再弃用。
  - 已弃用结果不能重复弃用。
  - 缺少任务 ID 或最终结果，提示刷新或进入任务详情。
- 高风险动作必须二次确认：
  - 批量弃用。
  - 弃用全部。
  - 删除整个生成任务。
- 成功反馈必须包含数量：
  - 新建正式用例数量。
  - 幂等命中数量。
  - 已弃用数量。
  - 剩余待处理数量。

## 风险点

- 风险 1：把“删除”理解为物理删除，会破坏 AI 原始结果可追溯性。
  - 控制方式：本轮统一按 `discarded` 弃用，不物理删除结果。
- 风险 2：结果处理页和任务详情页职责再次混淆。
  - 控制方式：`TaskDetail` 只保留预览和处理入口，不恢复采纳 / 弃用主动作。
- 风险 3：旧 `save_to_records/` 和新 `batch_adopt/` 并存，可能造成前端入口语义混乱。
  - 控制方式：前端主入口统一表达“采纳”，旧接口只作为兼容入口。
- 风险 4：编辑后重新生成 `final_test_cases` 字符串时，格式可能和后端解析预期不一致。
  - 控制方式：优先复用当前页面已有解析 / 生成逻辑，并在 TDD 中加入“编辑后保存再采纳”的验证用例。
- 风险 5：任务没有项目归属时，采纳到正式资产的项目选择不清楚。
  - 控制方式：优先传当前页面或任务已有 `project_id`；没有明确项目时前端先阻断并提示用户选择 / 绑定项目，是否允许后端自动创建默认项目需单独确认。

## 待确认项

- “删除生成用例”是否按本 Spec 默认理解为“弃用 / 不通过”，即保留原始结果但状态变成 `discarded`？
- 生成完成页的按钮文案是否改为“采纳全部待处理结果”和“进入结果处理”？
- 对没有项目归属的生成任务，是否允许沿用后端当前“自动选择 / 创建默认项目”的行为，还是必须让用户明确选择项目后才能采纳？
- 已采纳结果是否禁止再编辑源结果，统一去正式测试资产页修改？

### 2026-07-09 用户确认结论

- “删除生成用例 / 不通过用例”按 `discarded` 弃用处理，不物理删除 AI 原始生成结果。
- 生成完成页按钮文案按“采纳全部待处理结果”和“进入结果处理”设计。
- 没有明确项目归属时，前端先阻断并提示用户选择 / 绑定项目，不再让用户误以为已经保存成功。
- 已采纳结果禁止继续编辑源结果，后续修改应进入正式测试资产页处理。

## 验收标准

- [ ] 从生成完成页点击主按钮，不再出现无响应；请求中有 loading 和禁用态。
- [ ] 生成完成页在缺少任务 ID、缺少最终结果、任务未完成、无待处理结果时，能给出明确阻断提示。
- [ ] 结果批次页任务行有清晰“处理结果”入口，不再用“编辑”跳回详情页制造循环。
- [ ] 处理结果抽屉能展示当前任务的 `generated_results` 和处理状态摘要。
- [ ] 待处理结果支持单选、多选、全选。
- [ ] 已采纳 / 已弃用结果不能被再次选中处理。
- [ ] 单条采纳、批量采纳、全部采纳成功后，状态变为 `adopted`，正式资产入口可用。
- [ ] 单条弃用、批量弃用、全部弃用成功后，状态变为 `discarded`。
- [ ] 编辑待处理结果后保存成功，刷新后仍能看到修改后的内容。
- [ ] `TaskDetail` 仍是预览页，不出现采纳 / 弃用主处理按钮。
- [ ] 旧的任务删除动作和结果弃用动作不混淆。
- [ ] 不修改原生参考目录。

## 回退方式

- 前端回退：
  - 回退 `RequirementAnalysisView.vue` 中保存按钮行为和新增 loading 状态。
  - 回退 `GeneratedTestCaseList.vue` 中处理结果抽屉 / 面板。
  - 回退 `TaskDetail.vue` 中按钮文案 / class 调整。
- 后端回退：
  - 如果本轮后续确认不需要改后端，则无需回退后端。
  - 如果后续 TDD / Execution 增加了兼容修正，则按对应 diff 回退。
- 数据回退：
  - 本轮设计不新增迁移，不物理删除生成结果。
  - 已采纳生成的正式测试用例属于真实业务数据；如误采纳，需要用户在正式测试资产页按现有删除 / 作废流程处理。

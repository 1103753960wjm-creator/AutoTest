# AI 生成链路规范

## 1. 文档目标

本文档用于约束阶段 2.2 当前轮次的 AI 生成链路收口范围，聚焦以下 5 个问题：

- 真取消
- 刷新恢复
- SSE / 轮询 / 本地状态一致性
- 保存后边界
- 自动 AI 评审记录与统一入口

本轮不回头重做 2.1 对象层，也不进入 2.3 自动化草稿中心。

## 2. 本轮对象关系

当前链路按如下对象关系承接：

`RequirementAnalysisView -> TestCaseGenerationTask -> Generated Results -> TaskAutoReviewRecord -> TestCase`

对象职责如下：

- 需求分析对象：承接项目上下文、输入上下文、当前任务入口和最近任务入口
- 生成任务对象：承接任务状态、配置来源、处理状态、取消状态、自动评审摘要和结果入口
- 生成结果对象：承接任务内中间产物，仅在任务层与结果批次页中查看和处理
- 自动 AI 评审对象：承接生成链中的自动评审记录，不并入现有手工评审对象
- 测试用例对象：承接正式测试资产，生成结果进入正式资产后回到测试用例资产页继续维护

## 3. 本轮必做范围

- 真取消
- 刷新恢复
- SSE / polling / local state 收口
- 保存后边界稳定化
- 自动 AI 评审记录对象化和统一入口

## 4. 本轮明确不做

- 不回头重做 2.1 对象层
- 不做自动化草稿中心
- 不重写 AssistantView
- 不重构模型配置 / Prompt / 生成配置体系
- 不重构整套异步任务架构
- 不把自动 AI 评审强塞进现有手工评审列表
- 不重做 reviews 域现有分配、待办、审批流
- 不做执行闭环
- 不做复杂任务恢复中心
- 不做 AI 厂商侧远端硬中断

## 5. 取消语义

本轮采用“应用层协作式真取消”。

冻结规则如下：

- 前端点击取消必须调用真实后端取消接口
- 后端一旦写入 `status = cancelled`，后台执行链必须在关键阶段停止推进
- 所有最终结果写库前必须再次执行取消检查
- 已取消任务不得再被后续流程覆写成 `completed` 或 `failed`
- 已取消前产生的中间内容允许保留，但取消后不得继续写新的最终结果

## 6. 刷新恢复语义

本轮恢复采用以下组合：

- `route.query.taskId`
- `sessionStorage`
- `progress` 接口

恢复上下文按项目维度持久化，避免跨项目恢复污染。

固定 key 规则：

- `testhub.ai-generation.current-task.project:{projectId}`
- 无项目时：`testhub.ai-generation.current-task.project:none`

恢复优先级：

1. `route.query.taskId`
2. 当前项目对应的 `sessionStorage`
3. 无恢复上下文

终态任务上下文保留 30 分钟，超时后不再自动恢复。

## 7. SSE / 轮询 / 本地状态收口原则

- RequirementAnalysisView 只能存在一个活跃 tracker
- 页面切换、keepAlive deactivated、beforeUnmount 都必须清理旧 tracker
- SSE 失败只能降级出一个 polling
- `completed / failed / cancelled` 一律视为终态，进入终态后统一关闭 SSE / polling
- TaskDetail 不恢复完整流式显示，只做轻量 polling 刷新任务对象与结果状态

## 8. 保存后边界

生成结果对象与正式测试资产对象必须区分。

冻结规则如下：

- `pending` 结果：可查看、可编辑、可采纳、可弃用
- `adopted` 结果：任务层只读，可跳正式测试资产，不可再采纳 / 弃用
- `discarded` 结果：任务层只读，不可再采纳 / 弃用
- `processing_status_summary.pending_count = 0` 时，任务层整体只读
- `task.status in ['cancelled', 'failed']` 时，任务详情可见，但不允许继续处理结果

## 9. 自动 AI 评审对象

### 9.1 模型定位

新增 `TaskAutoReviewRecord`，定位为“生成链中的自动 AI 评审记录对象”。

本轮明确：

- 不等于手工评审对象
- 不并入现有 `apps/reviews.TestCaseReview`
- 使用 `ForeignKey(task)`，不锁死一对一

### 9.2 字段

固定字段如下：

- `task = ForeignKey(TestCaseGenerationTask, related_name='auto_review_records')`
- `project = ForeignKey(Project, null=True, blank=True, related_name='task_auto_review_records')`
- `review_source = 'ai_auto'`
- `source_stage = 'generation_review'`
- `review_status = reviewing / completed / failed / cancelled`
- `review_summary`
- `review_content`
- `reviewer_model_name`
- `reviewer_prompt_name`
- `result_identity_snapshot`
- `failure_message`
- `created_at`
- `updated_at`
- `completed_at`

### 9.3 最新记录规则

页面默认只展示“每个任务最新一条自动评审记录”。

最新记录排序规则固定为：

- 主排序：`created_at DESC`
- 稳定兜底：`id DESC`

### 9.4 统一入口

本轮提供独立统一入口：

- 路由：`/ai-generation/reviews/ai-auto`
- 页面：`AutoReviewList`

列表页默认不展开历史记录，但每条记录必须支持展开查看完整评审内容。

## 10. auto_review_summary 语义

后后端统一固定状态枚举，不靠文案猜测：

- `not_triggered`
- `reviewing`
- `completed`
- `failed`
- `cancelled`

前端只负责映射 label 和 tag。

固定结构如下：

```json
{
  "has_record": true,
  "review_id": 12,
  "status": "completed",
  "label": "已生成 AI 自动评审",
  "detail": "来自当前生成任务的自动评审记录，可进入统一 AI 评审入口查看",
  "entry_path": "/ai-generation/reviews/ai-auto?taskId=TASK_XXXX",
  "created_at": "2026-03-25T10:00:00+08:00"
}
```

无记录时：

- `has_record = false`
- `status = not_triggered`

## 11. 页面职责

### RequirementAnalysisView

- 承接当前项目上下文
- 承接当前生成任务
- 提供真取消入口
- 提供任务恢复入口

### TaskDetail

- 对所有任务状态可见
- 承接任务对象状态、配置来源、处理状态、自动评审摘要
- 操作能力受“任务状态 + 结果处理状态”双重限制

### GeneratedTestCaseList

- 继续作为结果批次 / 产物层页面
- 所有任务状态都允许进入任务详情
- 列表展示处理状态和自动评审摘要入口

### AutoReviewList

- 统一 AI 自动评审入口页
- 默认展示每任务最新一条自动评审记录
- 可按项目 / 任务 / 状态筛选
- 每条记录可展开查看完整内容，并跳回任务详情

## 12. 验收标准

- 取消生成不再是假取消
- 刷新页面后不再轻易丢失当前生成任务
- 页面状态、轮询 / SSE 状态、后端任务状态更一致
- 自动 AI 评审不再“生成过但找不到”
- 任务详情页更像生成任务对象页
- 生成结果与正式测试用例保存关系更清楚
- 没有破坏阶段 1 已完成的平台骨架，也没有回头推翻 2.1

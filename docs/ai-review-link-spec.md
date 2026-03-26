# 自动 AI 评审入口收口规范

## 1. 文档目标

本文档用于约束“生成任务中的自动 AI 评审”如何升级为可追踪对象，以及它如何进入统一入口。

本轮不重做整套评审系统，也不把自动评审强塞进现有手工评审列表。

## 2. 当前问题

当前自动 AI 评审真实发生了，但主要停留在：

- `TestCaseGenerationTask.review_feedback`

这导致：

- 自动评审内容会生成
- 但没有统一对象记录
- 没有统一入口
- 用户容易出现“任务里看过，但后来找不到”的感知断裂

## 3. 本轮对象结论

新增对象：

- `TaskAutoReviewRecord`

对象定位：

- 生成链中的自动评审记录
- 不等于手工评审对象
- 不并入 `apps/reviews.TestCaseReview`

## 4. 字段冻结

本轮固定字段如下：

- `task`
- `project`
- `review_source = ai_auto`
- `source_stage = generation_review`
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

## 5. 最新记录规则

页面默认只展示每任务最新一条记录。

排序规则固定为：

- `created_at DESC`
- `id DESC`

`id DESC` 作为最终稳定兜底。

## 6. auto_review_summary

任务对象侧统一输出 `auto_review_summary`。

固定状态枚举：

- `not_triggered`
- `reviewing`
- `completed`
- `failed`
- `cancelled`

前端只映射 label，不依赖文案猜状态。

## 7. 统一入口

新增统一入口：

- 页面：`AutoReviewList`
- 路由：`/ai-generation/reviews/ai-auto`

列表页冻结规则：

- 默认只展示每任务最新一条自动评审记录
- 本轮不展开历史记录列表
- 但每条记录必须支持展开查看完整评审内容
- 每条记录必须支持跳回任务详情页

## 8. 与现有评审列表的关系

本轮只做轻量挂接：

- 现有 `ReviewList` 顶部增加“查看 AI 自动评审”入口
- 跳转到 `AutoReviewList`

本轮不做：

- 不并入现有手工评审列表数据模型
- 不复用手工评审的待办、分配、审批流
- 不重写现有 reviews 域

## 9. 验收标准

- 自动 AI 评审不再只是任务内文本
- 自动 AI 评审有稳定可追踪记录
- TaskDetail、GeneratedTestCaseList、AutoReviewList 都能找到对应入口
- 失败 / 取消 / 未触发三类状态都能稳定表达

# AI 生成任务取消语义修复 Spec

## 背景

当前 AI 需求分析页已经支持发起生成任务，也存在“取消生成”按钮，但现状并不是真正的任务取消能力，存在明显语义断裂：

- 前端 [frontend/src/views/requirement-analysis/RequirementAnalysisView.vue](E:/testhub_platform-main/testhub_platform-main/frontend/src/views/requirement-analysis/RequirementAnalysisView.vue) 的 `cancelGeneration()` 当前只会：
  - 停止前端轮询
  - 清空 `currentTaskId`
  - 关闭本地 `isGenerating`
  - 弹出“已取消”提示
- 前端当前没有调用后端 [apps/requirement_analysis/views.py](E:/testhub_platform-main/testhub_platform-main/apps/requirement_analysis/views.py) 中已经存在的 `cancel` action
- 后端 `cancel` action 当前也只是把 `task.status = 'cancelled'` 写库，并没有真正中断后台线程或 AI 调用
- 后台生成线程在 [apps/requirement_analysis/views.py](E:/testhub_platform-main/testhub_platform-main/apps/requirement_analysis/views.py) 的 `execute_task()` 中运行，当前没有任何“检测到已取消就立即停止”的协作式检查
- 结果是：
  - 前端会以为“任务已取消”
  - 后台实际可能继续生成、评审、改写
  - 最终任务甚至可能被覆盖成 `completed` 或 `failed`

这会直接造成“页面认知”和“真实任务状态”不一致。

## 目标

本次要解决的是“取消生成”的真实语义问题，至少要把以下三点收清：

- 用户点击取消后，前端不能再假装任务已经取消成功
- 后端必须形成稳定一致的取消状态语义
- 后台执行链必须能在安全边界内停下来，而不是继续跑完再覆盖状态

## 非目标

- 不重构整套 AI 生成链路
- 不重做 RequirementAnalysisView 的整体布局
- 不引入复杂任务治理后台
- 不改 2.1 的对象层边界
- 不推进 2.2 第二阶段结果确认流
- 不做任务恢复 / 重试 / 回滚完整体系
- 不做多租户级任务调度器重构

## 当前真实现状

### 1. 前端当前是“本地假取消”

当前需求分析页的取消行为只是本地停止展示，不是后端取消：

- 停止轮询
- 清空 `currentTaskId`
- 设置 `isGenerating = false`
- 显示取消提示

这意味着：

- 用户看起来像取消成功了
- 但任务仍可能继续在后端运行
- 用户此时已经失去当前任务上下文

### 2. 后端当前是“软取消”

后端已存在 `cancel` 接口，但当前只做：

- 如果任务未结束，则把 `status` 改成 `cancelled`

没有做：

- 中断执行线程
- 中断 AI 生成 / 评审 / 改写调用
- 在执行流程中检查“任务是否已取消”

### 3. 执行线程当前会继续覆盖状态

后台线程正常跑完后，会继续把任务写成：

- `status = completed`
- `progress = 100`
- `completed_at` 写入
- `final_test_cases` 保存

如果中间报错，也会改成：

- `status = failed`

因此当前真实风险是：

- 任务短时间内可能先显示 `cancelled`
- 后面又被覆盖成 `completed` 或 `failed`

### 4. SSE 和轮询会把 `cancelled` 当终态

当前 SSE 推送逻辑已经把以下状态当作终态：

- `completed`
- `failed`
- `cancelled`

所以一旦任务库状态先被写成 `cancelled`，SSE 会提前结束，但后台线程仍可能继续工作。

## 冻结的产品语义

### 1. 本轮必须先区分三件事

- 前端停止等待
- 任务被标记为取消中 / 已取消
- 后台真实停止执行

这三件事不能再混成一个“取消了”。

### 2. 默认语义应为“协作式真取消”

本轮推荐口径：

- 点击取消后，前端先发起真实取消请求
- 后端把任务切到“取消中 / 已取消”控制语义
- 后台线程在关键阶段检查取消标记并尽快安全退出

不再接受“只关前端，不管后端”的本地假取消。

### 3. 取消成功后的稳定结果

取消成功后，任务最终应稳定停在：

- `cancelled`

而不是：

- 先 `cancelled`，后又被线程覆盖成 `completed` 或 `failed`

### 4. 已产生的中间内容允许保留，但不能继续推进

如果取消发生时已经有部分输出：

- 已写入的 `stream_buffer`
- 已写入的 `generated_test_cases`
- 已写入的 `review_feedback`
- 已写入的部分 `final_test_cases`

可以保留为“取消前中间产物”，但取消后不应再继续推进后续阶段或覆盖最终状态。

## 方案边界

### 第一阶段建议只做以下内容

#### 前端

- RequirementAnalysisView 的取消按钮必须改为调用真实后端取消接口
- 取消请求成功后，不立即丢失任务上下文
- 页面应展示“已取消”或“取消中”，并允许用户继续查看该任务的最终状态

#### 后端

- 保留现有 `cancel` action，但补强为真实可消费的取消入口
- 在线程执行链的关键阶段增加“任务是否已取消”的检查
- 一旦命中取消，线程应停止后续阶段推进，不再把任务覆盖成 `completed`

#### 状态语义

- 维持现有 `cancelled` 状态，不额外引入复杂状态机
- 若需要轻量提示，可通过返回字段补 `is_cancellable` 或 `cancel_state_summary`
- 但本轮不强制引入新的数据库状态枚举

### 本轮暂不处理

- 任务恢复
- 取消后继续从中间步骤恢复
- 多次取消 / 并发取消的复杂治理
- AI 厂商调用侧真正的远端中断能力
- 跨进程 / Celery 任务级统一取消治理

## 关键实现约束

### 1. 前端不能再本地假取消

RequirementAnalysisView 当前的 `cancelGeneration()` 必须改造：

- 先调用后端取消接口
- 成功后再更新页面本地状态
- 不应直接清空 `currentTaskId`

否则用户会失去任务追踪入口。

### 2. 后端线程必须协作式检查取消

建议在以下阶段前后增加取消检查：

- 生成开始前
- 生成完成后、评审前
- 评审完成后、改写前
- 最终保存前

一旦发现任务已是 `cancelled`：

- 立即停止继续执行
- 不再进入下一阶段
- 不再写入 `completed`

### 3. 最终状态写入必须防覆盖

当前 `execute_task()` 结束时无条件写 `completed`，这是必须修的点。

必须改成：

- 写最终状态前先 `refresh_from_db()`
- 若状态已是 `cancelled`，则直接退出
- 不再覆盖为 `completed`

### 4. 错误态不能吞掉取消态

若取消发生后，后台线程某个异步调用又抛异常：

- 不应把已取消任务覆盖成 `failed`
- 取消优先级应高于后续异常覆盖

## 推荐接口语义

### 1. 取消接口

建议继续使用当前后端已有 action：

- `POST /api/requirement-analysis/testcase-generation/{task_id}/cancel/`

建议最少返回：

```json
{
  "message": "任务已取消",
  "task_id": "xxx",
  "status": "cancelled"
}
```

### 2. 进度接口

当前 `progress` 和 `stream_progress` 已能承接 `cancelled`，本轮不必重构协议。

但必须保证：

- 一旦任务取消后，后续不会再被写成 `completed`

## 失败场景

### 场景 1：用户点击取消，但后端取消请求失败

预期：

- 前端提示取消失败
- 保留当前任务上下文
- 不假装取消成功

### 场景 2：用户点击取消时，后台正处于生成中

预期：

- 任务尽快停止
- 最终状态稳定为 `cancelled`
- 页面仍可查看取消前已产生的中间内容

### 场景 3：用户点击取消时，后台刚好已完成

预期：

- 若任务已进入终态，则取消接口返回“无法取消”
- 前端应以真实终态展示，不伪装成取消成功

### 场景 4：取消后线程后续仍抛异常

预期：

- 不覆盖取消态
- 最终仍保持 `cancelled`

### 场景 5：前端关闭页面后再回来

预期：

- 仍可通过任务详情或列表看到真实最终状态
- 不因本地状态清空而丢失任务

## 验收标准

- 点击取消时，前端不再只是本地停轮询，而会调用真实后端取消接口
- 取消后任务最终不会再被覆盖成 `completed`
- 取消后任务详情 / 任务列表能稳定显示 `cancelled`
- 取消前已经生成的中间内容可保留，但不会继续推进后续阶段
- 前端取消失败时不会假装成功

## 风险点

- 当前执行逻辑在线程中直接跑，取消只能做“协作式停止”，不能保证立刻硬中断外部模型调用
- 流式回调过程中可能已写入部分内容，本轮只能保证“停止继续推进”，不能保证“完全无中间残留”
- 如果未来迁移到 Celery 或独立任务执行器，还需要重新定义更底层的任务取消机制

## 建议的实施顺序

1. 先修 RequirementAnalysisView，取消按钮调用真实后端取消接口
2. 再修后端 `cancel` 与执行线程的协作式取消检查
3. 最后补任务详情 / 列表 / SSE 的联动回归验证

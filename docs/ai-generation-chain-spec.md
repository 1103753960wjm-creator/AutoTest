# AI 生成链路规范（2.2 第一阶段）

## 1. 文档目标

本规范用于约束阶段 2.2 第一阶段《AI 生成链路与 AI 助手收口》的实现范围。

本阶段只处理以下三层：

- 配置来源层
- `ProjectDetail -> RequirementAnalysisView -> TaskDetail` 前半链
- 生成任务对象页基础收口

本阶段不处理生成结果确认层、正式测试资产回链深化、业务链 AI 助手重构、自动化草稿中心和执行闭环。

## 2. 本阶段边界

### 2.1 本阶段要解决的问题

- 让 `AIModelConfig`、`PromptConfig`、`GenerationConfigView` 不再只是孤立配置页，而是生成链上游来源层
- 让用户看懂一次任务是从哪个项目、哪个分析上下文中发起
- 让 `RequirementAnalysisView` 更像“分析对象页 + 发起任务节点”
- 让 `TaskDetail` 更像“生成链核心对象页”，而不是纯进度页
- 在语义上明确区分“当前活跃配置推断摘要”和“任务执行时使用信息”
- 轻量补最少可用的失败信息表达与下游入口位

### 2.2 本阶段明确不处理

- 不深改 `GeneratedTestCaseList`
- 不深改 `TestCaseDetail` / `TestCaseEdit`
- 不重写 `AssistantView`
- 不展开完整结果确认 / 编辑 / 保存流程
- 不深化正式测试用例资产回链
- 不做自动化草稿中心
- 不做执行闭环
- 不做复杂 AI 调用治理后台
- 不重构 AI 模型配置体系
- 不重构 Prompt 配置体系
- 不建设真正的历史配置快照系统

## 3. 链路范围

本阶段固定的主链路如下：

`配置来源层 -> ProjectDetail -> RequirementAnalysisView -> 发起生成任务 -> TaskDetail`

说明：

- `ProjectDetail` 继续作为测试设计源头对象页
- `RequirementAnalysisView` 承接当前项目下的需求输入、分析上下文和任务发起动作
- `TaskDetail` 承接生成任务对象本身的来源、配置、状态、失败和下游入口位
- 生成结果层和正式资产层仅保留关系预留，不在本阶段深化

## 4. 配置来源层语义

### 4.1 配置来源层对象

- `AIModelConfig`
- `PromptConfig`
- `GenerationConfigView`

### 4.2 本阶段职责

- 提供可被分析页和任务页稳定消费的来源摘要
- 说明当前活跃配置的可用状态
- 说明这些配置将服务于哪些生成链节点

### 4.3 必须区分的两类语义

#### 当前活跃配置推断摘要

定义：

- 基于当前数据库中 `is_active = true` 的配置对象推断出的来源摘要

适用场景：

- `RequirementAnalysisView` 的配置来源展示
- `TaskDetail` 中无法取得真实快照时的兜底摘要

展示要求：

- 必须明确标记为“当前活跃配置”
- 必须说明这是推断摘要，不等于任务执行时的历史快照

#### 任务执行时使用信息

定义：

- 任务模型中真实持有的模型、Prompt 等字段

本阶段现状：

- 当前任务模型已有 `writer_model_config`、`reviewer_model_config`、`writer_prompt_config`、`reviewer_prompt_config`
- 当前任务模型没有 `generation_config` 快照字段
- 当前任务模型没有 `analysis` 外键

展示要求：

- 对已有真实字段，按“任务执行时使用信息”展示
- 对缺失字段，只能展示“当前活跃配置推断摘要”，不得伪装成真实执行快照

## 5. 前半链关系

### 5.1 ProjectDetail

本阶段职责：

- 继续作为设计源头对象页
- 明确挂接到需求分析页
- 明确挂接到任务链入口
- 保持 2.1 已建立的对象层结构，不重做大布局

本阶段应体现：

- 项目级需求分析摘要
- 项目级 AI 任务摘要
- 前往需求分析的稳定入口
- 前往最近任务或任务链入口的稳定入口

### 5.2 RequirementAnalysisView

本阶段职责：

- 承接“当前分析对象”
- 承接“当前项目上下文”
- 承接“配置来源摘要”
- 承接“发起任务动作”
- 承接“已有关联任务入口”

本阶段应体现：

- 当前关联项目
- 当前分析对象身份
- 当前依赖的配置来源摘要
- 当前任务状态或最近任务提示
- 发起任务入口

### 5.3 关于“来源分析对象摘要位”的强约束

当前任务模型没有 `analysis` 外键，因此：

- 只能做“来源分析对象摘要位”
- 只能表达“当前分析上下文摘要 / 来源分析说明”
- 不得伪造真实对象绑定
- 不得把它包装成强回链真数据

推荐语义：

- `source_analysis_summary`
- `is_inferred = true`
- `label`
- `detail`

## 6. TaskDetail 的核心页定位

`TaskDetail` 在 2.2 第一阶段中的定位是：

- 生成链核心对象页
- 不是纯进度页
- 也不是结果确认流程页

本阶段 `TaskDetail` 必须承接：

- 来源项目
- 来源分析对象摘要位
- 模型摘要
- Prompt 摘要
- 生成配置摘要
- 触发时间
- 任务状态
- 结果数量摘要
- 保存状态摘要
- 失败信息摘要
- 下游入口位

### 6.1 结果区处理原则

可以做：

- 弱化结果处理页感
- 将结果区降级为摘要区或次级区块
- 为后续结果层保留入口

不可以做：

- 不顺手重做 `GeneratedTestCaseList`
- 不展开完整确认流
- 不把本阶段变成结果层重构

## 7. 失败信息与最少可用留痕

本阶段只做最少可用语义：

- 当前任务状态
- 失败信息摘要
- 保存状态摘要
- 配置来源摘要

本阶段不做：

- 全量 AI 调用治理后台
- 完整阶段化失败审计
- 执行级链路追踪系统

推荐展示口径：

- 是否成功
- 若失败，失败发生在任务链中的哪一类阶段
- 用户下一步可以做什么，例如返回、重试、检查配置、查看结果页

## 8. 页面约束

- 页面头部只能由 `PlatformPageHeader` 承接
- 不允许新增第二套页面头部体系
- 深链接与回跳规则继续适用
- 不破坏阶段 1 的 Layout、Home、搜索、最近访问、收藏体系
- 不回头重做 2.1 已稳定的对象层结构

## 9. 后端约束

- 优先补摘要字段和轻量聚合字段
- 优先增强 `RequirementAnalysisView`、`TaskDetail`、`ProjectDetail` 相关接口
- 不大规模重构模型结构
- 不要求现在补真正的 `generation_config` 历史快照
- 不要求现在补 `analysis` 外键绑定

## 10. 本阶段推荐字段

### 10.1 分析页推荐摘要

- `config_source_summary`
- `analysis_context_summary`
- `task_entry_summary`

### 10.2 任务页推荐摘要

- `source_summary`
- `source_analysis_summary`
- `model_source_summary`
- `prompt_source_summary`
- `generation_config_summary`
- `result_count`
- `save_status_summary`
- `failure_summary`
- `downstream_summary`

说明：

- 上述字段允许以轻量聚合形式存在
- 但必须显式区分真实字段和推断字段

## 11. 后续阶段挂接说明

### 11.1 2.2 下一阶段

后续再进入：

- 生成结果层深化
- 确认 / 编辑 / 保存关系深化
- 正式资产层回链深化

### 11.2 2.3 自动化草稿中心

推荐挂接位：

- 主挂接位在正式测试用例资产层
- 项目层提供聚合入口
- 任务层和结果层只提供来源说明，不作为自动化草稿中心的最终归属层

## 12. 验收标准

- 配置页开始具备“生成链上游来源层”语义
- `RequirementAnalysisView` 更像分析对象页和发起任务节点
- `ProjectDetail -> RequirementAnalysisView -> TaskDetail` 前半链更清楚
- `TaskDetail` 更像生成链核心对象页，而不是纯进度页
- 用户能够区分“当前活跃配置推断摘要”和“任务执行时使用信息”
- 没有提前混入结果确认层、正式资产层、助手重构、自动化草稿中心
- 没有破坏阶段 1 已完成的平台骨架

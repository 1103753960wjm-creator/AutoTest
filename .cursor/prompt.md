# TestHub 项目规则总览

## 1. 文件职责

本文件属于 B 层“项目规则”，用于定义当前仓库长期有效的：

- 规则优先级
- 工程基线
- 分层职责
- 高风险链路
- 默认协作原则

本文件不记录阶段性冻结事实，也不承载局部目录的实现细节。

## 2. 规则优先级

发生冲突时，按以下顺序执行：

1. 用户当前回合的明确要求
2. `C:\Users\Administrator\.gemini\GEMINI.md`
3. 本文件 `.cursor/prompt.md`
4. `.cursor/workflow_rules.md`
5. `.cursor/architecture.md`
6. `.cursor/storage_rules.md`
7. `.cursor/project_rules.md`
8. `docs/project-memory/current_phase.md`
9. 代码库现状与最小惊扰原则

补充说明：

- `workflow_rules.md` 只负责流程闸门、任务分级、验证口径与文档回写，不得用于突破 `architecture.md` 的架构红线
- `docs/project-memory/dialogue_bootstrap.md` 属于 D 层，仅用于快速进入上下文，不参与正式规则优先级比较
- 若 `current_phase.md` 与实际代码冲突，以实际代码为准，并及时回写该文件

## 3. 工程基线

- 项目：`TestHub` 智能测试管理平台
- 根目录关键结构：`backend`、`apps`、`frontend`、`docs`、`media`、`logs`、`allure`
- 后端：Django 4.2 + Django REST Framework + MySQL + SimpleJWT + Channels + Celery
- 前端：Vue 3 + JavaScript + Vite + Pinia + Element Plus

高风险链路：

- JWT 登录、退出、刷新
- AI 配置与调用
- Celery 异步执行
- Channels / WebSocket
- Selenium / Playwright / Airtest 执行器
- Allure 报告
- Webhook / 邮件通知

## 4. 分层职责

### 4.1 全局规则层

- `C:\Users\Administrator\.gemini\GEMINI.md`
- 只定义跨项目通用的方法论、流程底线和交付底线

### 4.2 项目规则层

- `.cursor/*.md`
- 根 `AGENTS.md`
- 只定义当前仓库长期有效的规则、架构边界、存储边界与项目实现细则

### 4.3 局部目录规则层

- `frontend/AGENTS.md`
- `backend/AGENTS.md`
- `apps/requirement_analysis/AGENTS.md`
- 只定义最近目录内的实现约束、局部红线与最低验证方式

### 4.4 项目记忆层

- `docs/project-memory/current_phase.md`
- 记录当前阶段事实、冻结方案、验收口径和下一步主线

### 4.5 启动摘要层

- `docs/project-memory/dialogue_bootstrap.md`
- 仅用于新对话快速进入上下文，不承载正式规则

## 5. 默认协作原则

- 先读相关代码、规则和文档，再做判断
- 默认按 `Spec/SDD -> TDD -> Execution -> VDD` 流程推进
- 优先复用现有目录、接口封装、返回结构、状态管理和工具函数
- 默认做最小可落地改动，不把一次需求扩展成全仓重构
- 规则问题归规则层，阶段结论归记忆层，启动摘要归启动层，不混写
- 输出优先给出结果、风险和验证结论，再补充细节

# TestHub 项目规则总览

## 1. 文件职责

本文件属于 B 层“项目规则”，用于定义当前仓库长期有效的默认行为、规则优先级、工程基线和协作边界。

本文件不承担以下职责：

- 不记录阶段推进过程中的临时结论；这类内容进入 `docs/project-memory/current_phase.md`
- 不承担新对话快速启动摘要；这类内容进入 `docs/project-memory/dialogue_bootstrap.md`

## 2. 规则优先级

发生冲突时，按以下顺序执行：

1. 用户当前回合的明确要求
2. 全局规则 `C:\Users\Administrator\.gemini\GEMINI.md`
3. 本文件 `.cursor/prompt.md`
4. `.cursor/workflow_rules.md`
5. `.cursor/architecture.md`
6. `.cursor/storage_rules.md`
7. `.cursor/project_rules.md`
8. `docs/project-memory/current_phase.md`
9. 代码库现状与最小惊扰原则

补充说明：

- `workflow_rules.md` 约束的是实现顺序、测试设计、验证方式和交付方式，不得用于突破 `architecture.md` 中已明确的架构红线。
- `docs/project-memory/dialogue_bootstrap.md` 属于 D 层，仅用于新对话快速进入上下文，不参与正式规则优先级比较。
- 若 `current_phase.md` 与实际代码冲突，以实际代码为准，并及时回写该文件。

## 3. 当前仓库工程基线

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

## 4. 默认工作方式

- 先读相关代码、规则和文档，再做判断。
- 默认按全局 `Spec/SDD -> TDD -> Execution -> VDD` 流程推进。
- 优先复用现有目录、接口封装、返回结构、状态管理和工具函数。
- 默认做最小可落地改动，不把一次需求扩展成全仓重构。
- 规则问题归规则层，阶段结论归项目开发记忆层，启动摘要归对话启动记忆层，不混写。

## 5. 项目级硬边界

- 前端接口调用统一通过 `frontend/src/api/*` 和 `frontend/src/utils/api.js` 链路进入。
- 后端接口统一从 `backend/urls.py -> apps/<module>/urls.py -> views` 链路进入。
- 新增配置统一进入配置层，不得在业务模块散写地址、密钥、路径和环境判断。
- 新增 AI 能力必须通过统一入口或统一服务层接入，不得在业务页面、普通工具函数或零散脚本中继续扩散模型直连调用。

## 6. 沟通与文档要求

- 与用户沟通统一使用中文。
- 所有新增或修改的规范文件、设计文档、任务文档、交付说明统一使用中文。
- 所有新增或修改的代码注释统一使用中文；字段名、协议关键字、库名、框架名和第三方服务名可保留英文原文。
- 输出优先给出结果、风险、验证结论，再补充细节。

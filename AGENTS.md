#TestHub Agent 入口规则

## 1. 文件职责

本文件是 TestHub 仓库内的 agent 总入口，只负责：

- 说明读取顺序
- 说明规则优先级
- 说明默认流程闸门
- 说明受控自治与 Loop 规则入口
- 说明全仓硬红线
- 提供常用验证命令入口
- 指引进入子目录后继续读取最近的 `AGENTS.md`

本文件不承载阶段性冻结事实，也不展开具体业务域细则。

## 2. 读取顺序

进入仓库后，按以下顺序读取并遵守：

1. `C:\Users\Administrator\.gemini\GEMINI.md`
2. 当前仓库 `.cursor/prompt.md`
3. 当前仓库 `.cursor/workflow_rules.md`
4. 当前仓库 `.cursor/autonomy_rules.md`
5. 当前仓库 `.cursor/loop_rules.md`
6. 当前仓库 `.cursor/architecture.md`
7. 当前仓库 `.cursor/storage_rules.md`
8. 当前仓库 `.cursor/project_rules.md`
9. `docs/project-memory/development_checklist.md`（如存在，用于开发前短清单）
10. `docs/task-templates/README.md`（如存在，用于查看任务文档模板规则）
11. `docs/project-memory/error_event_log.md`（如存在，用于查看最近错误事件现场记录）
12. `docs/project-memory/error_prevention_log.md`（如存在，用于查看已沉淀的错误模式与防复发规则）
13. `docs/project-memory/current_phase.md`（如存在）
14. `docs/project-memory/decision_log.md`（如存在，用于查看已冻结决策）
15. `docs/project-memory/module_memory.md`（如存在，用于查看模块局部记忆）
16. `docs/project-memory/task_handoff.md`（如存在，用于查看最近任务交接）
17. `docs/project-memory/loop_run_log.md`（如存在，用于查看受控 Loop 执行记录）
18. `docs/project-memory/dialogue_bootstrap.md`（如存在，仅用于快速进入上下文）

读取硬规则：

- 读取中文规则、文档、日志和源码时，必须显式使用 UTF-8 或确认工具默认按 UTF-8 处理
- 用户是中国国内的软件测试工程师，所有需求确认、`Spec/SDD`、`TDD`、`VDD` 和交付说明必须使用中文大白话、细颗粒度表达
- 技术名词、接口名、字段名、路径和库名可以保留英文原文，但必须补充业务含义或测试视角解释
- 非“小修小改”任务的 `Spec/SDD`、`TDD`、`VDD` 必须按 `docs/task-templates/` 模板编写，并默认落盘到 `docs/tasks/YYYY-MM-DD-任务名/`

## 3. 项目基线

- 项目：`TestHub` 智能测试管理平台
- 后端目录：`backend` + `apps`
- 前端目录：`frontend`
- 后端技术栈：Django 4.2 + Django REST Framework + MySQL + SimpleJWT + Channels + Celery
- 前端技术栈：Vue 3 + JavaScript + Vite + Pinia + Element Plus

高风险链路：

- JWT 登录、退出、刷新
- AI 配置与模型调用
- Celery 异步执行
- Channels / WebSocket
- Selenium / Playwright / Airtest 执行器
- Allure 报告
- Webhook / 邮件通知

## 4. 默认开发流程

默认按以下顺序推进：

1. `Spec/SDD`
2. `TDD`
3. `Execution`
4. `VDD`

默认存在“Spec 确认闸门”：

- 未完成 `Spec/SDD` 对齐前，不进入正式实现
- `Spec/SDD` 阶段存在不确定、歧义、取舍问题时，必须先询问用户
- 非“小修小改”场景下，必须等待用户确认 `Spec/SDD` 后才能进入 `TDD`
- 完成 `TDD` 后，必须等待用户确认可以进入 `Execution` 才能正式修改文件

开始正式修改前，必须明确：

- 当前生效规则
- 本轮自治等级 L0-L4
- 是否允许进入受控 Loop
- 范围边界
- 验收标准
- 验证目标与失败场景

受控自治与 Loop 闸门：

- 未判断自治等级前，不得进入实现
- L0 / L4 场景只能审计、解释、提方案和等待用户确认，不能直接实现
- L3 受控 Loop 必须先写清 Loop 合同，并在 `docs/project-memory/loop_run_log.md` 记录执行过程
- AI 可以决定已确认范围内的实现细节，不能替用户决定范围扩大、契约变化、风险接受或验证降级

错误记录闸门：

- 进入任何开发任务前，必须先读取 `docs/project-memory/error_event_log.md` 与 `docs/project-memory/error_prevention_log.md`
- 开发中遇到命令失败、构建失败、接口异常、页面报错、控制台红错、验证失败、环境阻塞或规则执行偏差时，必须第一时间写入 `docs/project-memory/error_event_log.md`
- 任务收尾时必须判断本轮错误事件是否需要升级沉淀到 `docs/project-memory/error_prevention_log.md`

## 5. 全仓硬红线

- `workflow_rules.md` 不得突破 `architecture.md` 已定义的架构红线
- 前端请求必须统一经由 `frontend/src/api/* -> frontend/src/utils/api.js`
- 后端接口必须统一经由 `backend/urls.py -> apps/<module>/urls.py -> views`
- 新增配置必须进入配置层，不得在业务模块散写地址、密钥、路径与环境判断
- 新增 AI 能力必须通过统一入口或统一服务层接入，禁止在业务模块直接散接模型调用
- 所有新增或修改的规范文件、设计文档、任务文档、交付说明统一使用中文
- 所有新增或修改的代码注释统一使用中文；字段名、协议关键字、库名和第三方服务名可保留英文原文
- 提交 Git 或推送 GitHub 时，`commit message` 必须使用中文总结当前提交内容，禁止只写无法表达范围的空泛信息

## 6. 常用验证命令

按改动类型选择最低验证：

- 前端构建级验证：`cd frontend && cmd /c npm run build`
- 后端编译级验证：`python -m py_compile apps\\...` 或 `python -m py_compile backend\\...`
- 后端请求级验证：至少核对一次真实请求参数、响应结构和页面消费一致性

若验证受环境限制无法执行，必须在交付时如实说明原因。

## 7. 子目录规则入口

进入以下目录后，继续读取最近规则：

- `frontend/**`：先读 `frontend/AGENTS.md`
- `backend/**`：先读 `backend/AGENTS.md`
- `apps/requirement_analysis/**`：先读 `apps/requirement_analysis/AGENTS.md`

若后续其他业务域出现稳定的局部规则，应在对应目录新增 `AGENTS.md`，不要继续堆回根入口。

## 8. 文档回写规则

- 长期规则变化：更新 `.cursor/*.md` 或对应子目录 `AGENTS.md`
- 阶段边界、验收口径、下一步主线变化：更新 `docs/project-memory/current_phase.md`
- 已确认的关键取舍、冻结口径、不可回退决策：更新 `docs/project-memory/decision_log.md`
- 模块级边界、局部风险、开发注意事项变化：更新 `docs/project-memory/module_memory.md`
- 一轮任务完成后的最近进展、未完成项、阻塞项与下一步建议：更新 `docs/project-memory/task_handoff.md`
- L3 受控 Loop 的执行过程、循环次数、验证证据与暂停原因：更新 `docs/project-memory/loop_run_log.md`
- 非“小修小改”任务的 `Spec/SDD`、`TDD`、`VDD`：写入 `docs/tasks/YYYY-MM-DD-任务名/`
- 任意错误现场、命令失败、构建失败、接口异常、页面报错、控制台红错、验证失败、环境阻塞或规则执行偏差：先更新 `docs/project-memory/error_event_log.md`
- 已证明会重复出现的错误模式、根因分析、防复发规则与最低验证动作：更新 `docs/project-memory/error_prevention_log.md`
- 对话启动摘要变化：更新 `docs/project-memory/dialogue_bootstrap.md`
- 显著规则、功能或文档变更：更新 `更新日志.md`

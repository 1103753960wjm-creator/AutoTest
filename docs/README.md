# TestHub 文档索引

## 1. 文档目录分类

本文是 `docs` 目录入口，用于快速找到项目文档。新增文档时优先放入对应分类目录，不再堆回 `docs` 根目录。

## 2. 常用入口

| 文档 | 用途 |
| --- | --- |
| `guides/AI开发规范迁移复用提示词.md` | 新项目迁移本套 AI 开发规范，或项目稳定后二次优化规范体系 |
| `task-templates/README.md` | 查看 `Spec/SDD`、`TDD`、`VDD` 和 Loop 合同模板规则 |
| `project-memory/error_event_log.md` | 查看最近错误事件，开发前必须先读 |
| `project-memory/error_prevention_log.md` | 查看已沉淀的防复发规则，开发前必须先读 |
| `project-memory/dialogue_bootstrap.md` | 新对话快速进入上下文 |

## 3. 分类说明

| 目录 | 用途 |
| --- | --- |
| `overview/` | 平台现状、阶段总纲、全局优化规划 |
| `architecture/` | 平台架构、导航、页面壳、路由、状态、审计边界等规范 |
| `ai/` | AI 生成链路、取消、自动评审等规范 |
| `api/` | 平台 API 汇总文档 |
| `api-automation/` | 接口自动化对象闭环、P0/P1/P2 任务文档与归档 |
| `data-factory/` | 数据工厂功能、快速开始、API 和使用说明 |
| `guides/` | 使用说明、排查指南、测试人员说明和专项工具说明 |
| `operations/` | 部署、运维和环境说明 |
| `planning/` | 跨模块优化计划和实施计划 |
| `APP/` | App 自动化历史集成文档 |
| `project-memory/` | 当前阶段事实、决策、模块记忆、交接、错误事件和防复发手册 |
| `task-templates/` | `Spec/SDD`、`TDD`、`VDD` 和 Loop 合同模板 |
| `tasks/` | 每轮非“小修小改”任务的过程文档 |

## 4. 新增文档规则

- 规则、任务、设计和交付文档统一使用中文。
- 文件统一使用 UTF-8 编码。
- 非“小修小改”任务文档统一写入 `docs/tasks/YYYY-MM-DD-任务名/`。
- 长期规则优先写入 `.cursor/*.md` 或对应目录 `AGENTS.md`，不要散落在普通说明文档里。
- 阶段事实、错误事件、Loop 记录等项目记忆只写入 `project-memory/`。

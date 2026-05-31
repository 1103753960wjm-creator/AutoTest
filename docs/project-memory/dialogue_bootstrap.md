# TestHub 对话启动记忆

更新时间：2026-05-26

## 1. 文件职责

本文件属于 D 层，仅用于让新对话快速进入上下文。

注意：

- 本文件不是正式规则来源。
- 全局规则以 `GEMINI.md` 为准。
- 项目规则以 `AGENTS.md` 与仓库内 `.cursor/*.md` 为准。
- 阶段事实以 `docs/project-memory/current_phase.md` 为准。
- 已冻结决策以 `docs/project-memory/decision_log.md` 为准。
- 模块局部记忆以 `docs/project-memory/module_memory.md` 为准。
- 最近任务交接以 `docs/project-memory/task_handoff.md` 为准。
- 已沉淀错误模式与防复发规则以 `docs/project-memory/error_prevention_log.md` 为准。

## 2. 30 秒项目摘要

- 项目：`TestHub` 智能测试管理平台
- 后端：Django 4.2 + Django REST Framework + MySQL + SimpleJWT + Channels + Celery
- 前端：Vue 3 + JavaScript + Vite + Pinia + Element Plus
- 当前高频主题：平台统一壳、导航真源、统一状态组件、测试设计 2.1/2.2、AI 生成链路

## 3. 新对话接手顺序

1. 先读 `AGENTS.md`
2. 再读 `docs/project-memory/current_phase.md`
3. 再读当前任务最相关的 `docs/*.md`
4. 最后进入对应前后端入口代码

## 4. 常用真源索引

- 平台现状地图：`docs/平台现状地图.md`
- 导航冻结方案：`docs/navigation-freeze-plan.md`
- 路由 meta 规范：`docs/route-meta-spec.md`
- 页面壳规范：`docs/page-shell-spec.md`
- AI 生成链路：`docs/ai-generation-chain-spec.md`
- smoke 回归基线：`docs/platform-smoke-baseline.md`
- 决策日志：`docs/project-memory/decision_log.md`
- 模块记忆：`docs/project-memory/module_memory.md`
- 任务交接：`docs/project-memory/task_handoff.md`
- 统一表格与状态模板规范：[unified-table-template-spec.md](file:///e:/testhub_platform-main/testhub_platform-main/docs/unified-table-template-spec.md)
- 错误模式库：`docs/project-memory/error_prevention_log.md`

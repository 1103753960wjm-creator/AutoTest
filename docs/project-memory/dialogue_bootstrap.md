# TestHub 对话启动记忆

更新时间：2026-07-10

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
- 当前高频主题：平台统一壳、导航真源、顶部/侧边栏快速切换稳定性、P0/P0.2 安全配置、敏感日志脱敏、统一状态组件、AI 生成链路、接口自动化 P0 闭环。
- 最新冻结点：登录后业务页面共用 `layout:authenticated` 根层 Layout key；顶部模块、侧边栏、搜索、最近访问、收藏和用户资料入口统一走 Layout 导航调度器；认证失效跳转统一走 `authNavigation`；Excel 导出统一走 `excelExport` + `write-excel-file`；接口自动化正式“接口测试用例”入口为 `/api-testing/test-cases`，接口自动化正式“测试套件”入口为 `/api-testing/test-suites`；P0.1 剩余闭环已完成，注册接口返回 JWT 双 token，不再返回 `temp_token_*`，UI 元素定位器验证未接入真实浏览器时返回 501，不再模拟通过；AI 生成结果处理主入口在 `GeneratedTestCaseList.vue` 的“处理结果”抽屉，`TaskDetail.vue` 只做任务对象摘要和入口；P0.2 第一批已完成生产配置复核、配置说明、前端敏感调试日志清理和后端 AI 日志脱敏；P0.2 第二三批已完成需求分析生成进度 SSE 迁移和错误结构试点；P0.2 剩余实时连接已完成 App 自动化执行进度和接口测试工作区 WebSocket 迁移；统一实时连接入口为 `useEventSource` / `useWebSocket`，错误提示优先走 `frontend/src/utils/errorMessage.js`，后端错误响应试点优先走 `apps/core/responses.py`。
- 下一步主线：P0.2 除真实浏览器回归外已收尾，可以进入下一阶段。用户已要求跳过剩余浏览器回归，未执行项只能作为残余风险，不能写成已通过；后续如要补回归，需要单独验证 WebSocket / SSE 的 Network 创建、关闭、终态停止和页面离开清理。
- 最新验证口径：改 `App.vue`、`layout/index.vue`、侧边栏、认证跳转或路由 key 时，除 `npm run build` 外，必须补跑顶部大模块 -> 侧边栏子模块快速切换，确认无 `beforeunload`、`pagehide` 和主文档请求。

## 3. 新对话接手顺序

1. 先读 `AGENTS.md`
2. 再读 `docs/project-memory/current_phase.md`
3. 再读当前任务最相关的 `docs/*.md`
4. 最后进入对应前后端入口代码

## 4. 常用真源索引

- 平台现状地图：`docs/overview/平台现状地图.md`
- 导航冻结方案：`docs/architecture/navigation-freeze-plan.md`
- 路由 meta 规范：`docs/architecture/route-meta-spec.md`
- 页面壳规范：`docs/architecture/page-shell-spec.md`
- AI 生成链路：`docs/ai/ai-generation-chain-spec.md`
- smoke 回归基线：`docs/architecture/platform-smoke-baseline.md`
- 决策日志：`docs/project-memory/decision_log.md`
- 模块记忆：`docs/project-memory/module_memory.md`
- 任务交接：`docs/project-memory/task_handoff.md`
- 统一表格与状态模板规范：[unified-table-template-spec.md](file:///e:/testhub_platform-main/testhub_platform-main/docs/architecture/unified-table-template-spec.md)
- 接口自动化 P0/P1 需求：`docs/api-automation/api-automation-testcase-loop-ai-generation-spec.md`
- 接口自动化 P0-1 TDD/VDD：`docs/api-automation/api-automation-p0-1-testcase-loop-tdd.md`、`docs/api-automation/api-automation-p0-1-testcase-loop-vdd.md`
- 接口自动化 P0-2 Spec/TDD：`docs/api-automation/api-automation-p0-2-ai-target-type-spec.md`、`docs/api-automation/api-automation-p0-2-ai-target-type-tdd.md`
- 接口自动化对象级闭环审计：`docs/api-automation/api-automation-object-closure-audit.md`
- 接口自动化阶段 A TDD/VDD：`docs/api-automation/api-automation-p0-object-closure-fix-tdd.md`、`docs/api-automation/api-automation-p0-object-closure-fix-vdd.md`
- 错误模式库：`docs/project-memory/error_prevention_log.md`
- P0.2 跨模块硬化任务文档：`docs/tasks/2026-07-10-p0-2-cross-module-hardening/spec-sdd.md`、`docs/tasks/2026-07-10-p0-2-cross-module-hardening/tdd.md`、`docs/tasks/2026-07-10-p0-2-cross-module-hardening/vdd.md`
- Excel 导出统一工具：`frontend/src/utils/excelExport.js`
- 认证跳转统一工具：`frontend/src/utils/authNavigation.js`

# TestHub 对话启动记忆

更新时间：2026-06-19

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
- 当前高频主题：平台统一壳、导航真源、顶部/侧边栏快速切换稳定性、P0 安全配置、统一状态组件、测试设计 2.1/2.2、AI 生成链路、接口自动化 P0 闭环。
- 最新冻结点：登录后业务页面共用 `layout:authenticated` 根层 Layout key；顶部模块、侧边栏、搜索、最近访问、收藏和用户资料入口统一走 Layout 导航调度器；`<form>` / `<el-form>` 必须有 `@submit.prevent`，原生 `<button>` 必须显式声明 `type`；认证失效跳转统一走 `authNavigation`；Excel 导出统一走 `excelExport` + `write-excel-file`；接口自动化正式“接口测试用例”入口为 `/api-testing/test-cases`，P0-1 以 `ApiRequest` 承接接口测试用例，旧 `/api-testing/interfaces` 仅隐藏兼容；接口自动化正式“测试套件”入口为 `/api-testing/test-suites`，旧 `/api-testing/automation` 仅隐藏兼容重定向；`/api-testing/test-cases` 当前是资产列表页，旧调试树只作为 `/api-testing/test-cases/workspace?caseId={id}&projectId={projectId}` 隐藏工作区；阶段 A 已补齐移动集合、请求历史清空、套件级断言编辑保存、负责人只读和删除级联风险提示；套件执行优先使用 `TestSuiteRequest.assertions`，空时回退 `ApiRequest.assertions`；P0-2 已冻结接口测试用例 / 测试套件拆分口径，AI 生成 `api_test_case` 只生成 `ApiRequest` 兼容字段，不直接生成套件；当前 AI 生成测试用例逻辑严禁重写，只允许套用目标类型、Prompt 选择和字段展示契约。
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
- Excel 导出统一工具：`frontend/src/utils/excelExport.js`
- 认证跳转统一工具：`frontend/src/utils/authNavigation.js`

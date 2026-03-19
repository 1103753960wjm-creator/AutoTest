# 全局开发规则与项目基线

本文件是 AI 助手的全局记忆，用于约束跨项目的默认开发行为，以及当前 `AutoTest / L-Tester` 仓库的规则优先级。

---

## 1. 全局提示规则

你是当前仓库的开发助手。默认目标不是写“理想模板代码”，而是在现有架构下交付可运行、可验证、可维护的改动。

### 规则优先级
发生冲突时，按以下顺序执行：
1. 用户当前回合的明确要求
2. 全局记忆文件 `GEMINI.md`
3. 项目内 `.antigravity/prompt.md`
4. 项目内 `.antigravity/workflow_rules.md`
5. 项目内 `.antigravity/architecture.md`
6. 项目内 `.antigravity/storage_rules.md`
7. 项目内 `.antigravity/project_rules.md`
8. 代码库现状与最小惊扰原则

补充说明：
- `workflow_rules.md` 优先级提高，表示当前项目默认按 TDD/验证优先的开发流程执行。
- `workflow_rules.md` 约束的是实现顺序、验证方式和交付方式，不得用于突破 `architecture.md` 中已经明确写死的架构红线。

### 默认行为
- 先读相关代码，再做判断。
- 优先复用现有目录、工具函数、返回结构、接口封装。
- 不为了“显得先进”替换当前技术路线。
- 不把一次需求扩展成全仓重构。

### 外部文档与 MCP
- 当用户明确要求 use context7，或任务依赖某个框架/库的官方文档实现细节时，优先使用 Context7 MCP，不凭记忆直接实现。
- 使用顺序固定为：先 Resolve Context7 Library ID，再 Query Documentation。
- 通过 Context7 获取资料时，优先参考官方文档、官方示例和官方推荐写法。
- 如果用户明确写出类似以下指令，视为必须走 Context7：
- Create a Next.js middleware that checks for a valid JWT in cookies and redirects unauthenticated users to /login. use context7
- Configure a Cloudflare Worker script to cache JSON API responses for five minutes. use context7
- 这类任务的交付默认要体现“依据官方文档实现”，不要只给经验写法。
- 如果用户没有显式写 use context7，但任务明显依赖官方最新文档、框架约定、SDK/云平台配置或版本化 API，允许 AI 自动判断并优先调用 Context7 MCP。
- 自动调用 MCP 的前提是：本地代码、项目规范和现有上下文不足以稳定确定正确实现；如果本地仓库已经有明确模式或任务主要是仓内逻辑改动，则先读本地代码，不默认调用 MCP。
- 不允许把“自动调用 MCP”扩展成“所有技术问题一律查文档”；只有当官方文档对正确实现有决定性影响时才触发。

### 沟通与文档要求
- 与用户沟通统一使用中文。
- 所有新增或修改的规范文件、设计文档、任务文档、交付说明统一使用中文。
- 所有新增或修改的代码注释统一使用中文；字段名、协议关键字、库名、框架名和第三方服务名可保留英文原文。
- 输出尽量直接，先说结果和风险，再补细节。
- 无法验证时必须明确说明原因。

---

## 2. 当前项目工程规则

### 项目结构
- `l-tester-master` 是 Python 后端，技术栈为 FastAPI + Tortoise ORM + MySQL。
- `l-vue-ui-master` 是前端管理台，技术栈为 Vue 3 + TypeScript + Vite + Pinia + Element Plus。
- 这是前后端分离测试平台，不是通用后台模板；任何改动都要考虑脚本执行、结果落库、报表、通知这些业务闭环。

### 后端边界
- 路由函数不得堆积复杂业务逻辑。
- `*_model.py` 只做数据定义，不写业务流程。
- 新接口优先复用统一返回结构：`{"code": ..., "message": ..., "data": ...}`。
- 执行器、调度、通知属于高风险链路，修改时必须同步考虑结果、状态、日志。

### 前端边界
- 页面组件不得直接拼后端 URL，必须通过 `src/api/*` 统一封装。
- 动态路由、用户信息、token 相关逻辑只能在 router/store/utils 既有链路上扩展。
- 已经走真实后端接口的功能，不再补一套本地 JSON 假数据流程。

### 存储与配置边界
- 前端访问链路：`View -> src/api -> axios interceptor -> Backend API`
- 后端访问链路：`router/view -> module common/script/process -> model/database`
- 数据库存取优先通过 Tortoise model。
- 文件、媒体统一走项目既有路径体系。
- 配置优先收敛到现有配置文件，不散落硬编码。
- 新增后端运行配置统一进入 `l-tester-master/.env` 或 `.env.local`。
- 新增前端运行配置统一进入 `l-vue-ui-master/.env.*`。
- 后续三模式切换 `none / local_llm / remote_llm` 只能从统一配置层或网关层进入，不得散写到具体业务模块。

---

## 3. 工作流规则

### 默认工作方式
- 先读代码，再下手。
- 默认按 `Spec -> TDD -> Execution` 的顺序执行开发：先对齐需求和验收标准，再明确行为与失败场景，最后实现并回归验证。
- 对新功能、跨模块改动、高风险链路，优先做 spec 对齐，再写测试设计或验证清单，最后改业务代码。
- 遇到平台级重构任务时，必须先对齐阶段目标、范围边界和验收标准，再进入实现。

### 验证规则
- 后端改动：至少做导入级或调用级验证；能跑 pytest 就跑受影响范围。
- 前端改动：至少做 TypeScript 或构建级验证；能跑页面相关检查就跑受影响范围。
- 前后端联动：至少检查请求参数、响应结构、页面展示三者一致。
- 无法验证时必须明确说明原因，不能假装已经验证。

### TDD 最低门槛
- 新增后端业务接口：优先补 pytest 或最小调用级验证。
- 新增前端关键交互：优先补类型校验、构建校验，条件允许时补组件或页面级验证。
- 改登录、权限、调度、执行器、通知、报告：必须先列失败场景，再改实现。
- 没有自动化测试条件，不等于可以跳过测试设计。



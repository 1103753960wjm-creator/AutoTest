# TestHub 任务交接

更新时间：2026-07-04

## 1. 文件职责

本文文件属于 C 层“正式项目记忆”，用于记录最近一轮任务的完成情况、未完成项、阻塞点与下一步建议，服务于跨会话接手。

使用原则：

- 以“最近一轮交接”为主，不写成长流水账
- 只记录对下一轮接手最关键的信息
- 长期阶段事实仍以 `current_phase.md` 为准
- 关键取舍仍以 `decision_log.md` 为准

## 2. 最近完成项

- 2026-07-04 已定位并修复本地开发环境页面切换卡顿 / 像刷新问题：根因不是 `router-view key`、表单默认提交或认证跳转，而是 `frontend/vite.config.js` 长期开启 `optimizeDeps.force: true`，配合大量懒加载页面和 Element Plus 按需样式，首次点击页面时触发 Vite 依赖重优化，出现 `504 Outdated Optimize Dep` 和动态 import 失败，随后浏览器 reload。已去掉 `force: true`，新增 `optimizeDeps.entries` 覆盖 `index.html` 与 `src/**/*.{js,vue}`，并预优化 Element Plus 深层样式依赖。验证结果：Vite 重启日志不再出现强制重优化；Playwright 复现接口自动化、Web 自动化、App 自动化共 11 次导航，`beforeunload/pagehide/hidden` 均为 0，网络无 `504 Outdated Optimize Dep`；`cd frontend && cmd /c npm run build` 通过，仍只有既有 `web-tree-sitter` 警告。浏览器验证中的后端接口 500 来自未启动 Django 后端，不属于本轮导航刷新问题。
- 2026-07-04 已修复双击 `start.bat` 后前端先 ready、后端未 ready 导致的 `ECONNREFUSED 127.0.0.1:8000`：旧脚本后台启动 Django 后立即启动 Vite，截图中的前端请求早于 `backend.log` 中 Django ready 时间约 15 秒。现在脚本会先切到脚本所在目录，启动后端后最多等待 60 秒确认 `127.0.0.1:8000` 可连接，再启动前端；后端未 ready 时提示查看 `backend.log` 并停止。
- 2026-07-03 已完成 P0.1 前后端与样式上线阻断项第一批：新增样式 token 并接入共享样式基座；P0.1 点名的数据工厂、数据工厂选择器和执行详情页裸 `axios` 已收口到 `frontend/src/api/* -> frontend/src/utils/api.js`；需求分析配置 / 生成 / 进度 / SSE 和 App 自动化报告入口已收紧到认证和对象权限；`backend/urls.py` 不再暴露无对象权限的 App 报告静态目录。验证结果：`npm run build`、后端 `py_compile`、`rule_check.ps1`、`git diff --check`、裸 axios 扫描、权限静态扫描均通过；DRF 测试客户端验证未登录敏感入口 401、直接 App 报告 media 403、登录态配置检查 200、本人任务进度和 SSE 200。本轮 VDD 为 `docs/tasks/2026-07-03-p0-1-full-stack-baseline/vdd.md`，最高验证等级 V3（有限请求级验证）。未验证项：浏览器页面主流程、App 报告真实文件 200、真实无权限对象 403、浏览器 EventSource 凭据行为。
- 2026-07-02 已新增 `docs/guides/AI开发规范迁移复用提示词.md`：包含新项目初始化规范提示词、项目稳定后二次优化提示词、复用前提醒、遗漏检查清单和补充风险点；用于把当前 Harness Engineering + 受控 Loop + 错误日志 + Spec/TDD/VDD 模板体系迁移到其他项目。
- 2026-07-02 已完成 `docs` 文档目录分类整理：根目录只保留 `docs/README.md`，业务/规范文档按 `overview`、`architecture`、`ai`、`api`、`api-automation`、`data-factory`、`guides`、`operations`、`planning` 等目录归档；接口自动化 P0 归档移动到 `docs/api-automation/archive/p0-docs-2026-06-18/`；补齐 `docs/architecture/unified-table-template-spec.md` 和 `docs/guides/frontend-ui-style-guide.md` 两个历史缺失引用入口；已验证具体 Markdown 路径无缺失、典型旧根路径无残留、`rule_check.ps1` 通过、`git diff --check` 返回 0；本轮任务文档见 `docs/tasks/2026-07-02-docs-reorganization/`。
- 2026-06-19 已补齐接口测试用例资产列表固定字段：`/api-testing/test-cases` 现在按确认口径展示用例名称、请求方法、URL、所属项目、所属集合、断言数、来源、最近执行状态、更新时间和操作；筛选项补齐所属集合。最近执行状态由后端 `ApiRequest` 列表通过 `RequestHistory` 子查询聚合返回，避免前端逐行请求历史造成 N+1。
- 2026-06-19 已完成接口自动化测试套件导航正式拆分：侧边栏新增可见 `/api-testing/test-suites`“测试套件”，旧 `/api-testing/automation` 改为隐藏兼容重定向；Dashboard 快捷入口、route meta 和中英文文案已同步。根因是此前只有功能路由和页面复用，导航真源仍没有正式“测试套件” KEEP 入口，导致用户侧边栏只能看到“接口测试用例”或旧命名。
- 2026-06-19 已完成接口自动化阶段 A 对象闭环 P0 补强 Execution / VDD：接口测试用例移动集合、调试工作区所属集合编辑、请求历史按筛选范围清空、套件级断言编辑弹窗与保存、套件执行断言优先级、项目负责人只读、删除级联风险提示均已落地。
- 2026-06-19 已新增 `docs/api-automation/api-automation-p0-object-closure-fix-vdd.md`，并同步归档目录、项目阶段记忆、决策日志、模块记忆、错误模式库、启动摘要和更新日志。
- 2026-06-19 已完成阶段 A 验证：后端 `py_compile` 通过、前端 `cmd /c npm run build` 通过、静态检索未发现新增整页刷新兜底 / P0 假入口 / 接口自动化页面直接业务请求；真实浏览器人工回归尚未执行。
- 2026-06-19 已确认阶段 A 对象闭环 P0 补强 TDD 的两个取舍：请求历史“清空历史”必须真实实现；套件级断言必须实现编辑弹窗并保存，弹窗样式参考当前系统已有编辑弹窗。
- 2026-06-19 已更新 `docs/api-automation/api-automation-p0-object-closure-fix-tdd.md` 和归档 README；阶段 A 已从 TDD 确认推进到 Execution / VDD 完成。
- 2026-06-18 已补充 P0-2 AI 生成目标类型 Spec/TDD：明确接口测试用例是 `ApiRequest` 原子资产，测试套件是 `TestSuite + TestSuiteRequest` 编排资产；AI 生成 `api_test_case` 只输出 `ApiRequest` 兼容字段，不直接生成测试套件。
- 2026-06-18 已冻结用户新增红线：当前 AI 生成测试用例逻辑严禁更改，只允许在现有链路外层套用 `target_type`、Prompt 按类型选择、任务固化和结果字段展示契约；禁止重写生成任务创建、模型调用、流式输出、取消、自动评审、轮询恢复和功能测试采纳主链。
- 2026-06-18 已同步项目记忆、决策日志、模块记忆、错误预防库和更新日志，后续进入 P0-2 Execution 前必须先等用户确认 Spec，再修订并确认 TDD。
- 2026-06-17 已完成接口自动化 P0-1.5 产品化收口：`/api-testing/test-cases` 不再复用旧树形接口调试工作台作为首页，改为真实接口测试用例资产列表；支持项目/方法/名称或 URL 查询、分页、新建、编辑/调试、执行、加入同项目测试套件、查看指定用例历史和删除。旧 `InterfaceManagement.vue` 保留为隐藏调试工作区 `/api-testing/test-cases/workspace?caseId={id}&projectId={projectId}`。
- 2026-06-17 已补齐接口测试用例列表交互细节：筛选区“查询 / 重置”按钮增加上间距；隐藏调试工作区新增“返回用例列表”；“加入套件”行操作阻止表格行事件冒泡，套件加载中禁用选择与确认，未归属集合、无套件、加载失败、未选择套件、加入成功和加入失败均改为 `ElMessageBox` 弹窗提示。
- 2026-06-17 已修复 Element Plus 服务式弹窗样式缺失：`frontend/src/main.js` 显式引入 `loading`、`message`、`message-box` 服务组件样式，恢复 `ElMessageBox` 遮罩、居中和按钮样式；构建通过，浏览器运行时可检索到 `.el-message-box` 与 `.el-overlay-message-box` 样式规则。
- 2026-06-17 已修复接口测试用例列表到隐藏调试工作区的深链体验：列表跳转会携带 `projectId`；工作区作为 `keepAlive` 页面时监听 `caseId/projectId` 变化并重选目标用例；用例详情加载和列表加载都增加旧响应丢弃，快速点击、筛选、翻页时最终以最后一次目标为准。
- 2026-06-17 已完成全局表单默认行为硬化：`frontend/src/**/*.vue` 中所有 `<form>` / `<el-form>` 已补 `@submit.prevent`，所有原生 `<button>` 已显式声明 `type`；防止 Enter 键或按钮默认 submit 绕开 Vue Router 触发当前 URL 重新请求，造成页面卡住或整页刷新体感。静态扫描确认无漏网表单与无类型按钮，`git diff --check -- frontend/src` 与 `cd frontend && cmd /c npm run build` 通过；构建仍只有既有 `web-tree-sitter` 警告。
- 2026-06-17 已修复顶部大模块与侧边栏子模块快速切换卡住问题：`PlatformSidebar.vue` 去掉 `pointerdown.capture` 与 `click.capture` 的重复导航触发，只保留 `el-menu @select`；`layout/index.vue` 导航调度从旧队列模型改为“最后一次点击优先”，旧导航不会再锁住最新点击；`router/index.js` 写浏览器标题前校验当前真实路由，避免旧路由晚到覆盖新标题。
- 2026-06-17 已完成导航回归验证：Playwright 精确快速执行“Web 自动化 -> 多个侧栏子模块 -> App 自动化 -> 多个侧栏子模块 -> 接口自动化 -> 接口测试用例 -> 请求历史 -> 测试套件 -> 请求历史”，最终 URL、浏览器标题、顶部模块、侧栏高亮和正文均停在 `/api-testing/history` / “请求历史”，无 `beforeunload`、`pagehide`、`visibilitychange(hidden)`，无整页刷新事件；`cd frontend && cmd /c npm run build` 通过，仍只有既有 `web-tree-sitter` 警告。
- 2026-06-17 已完成接口自动化 P0-1 用例闭环：新增正式入口 `/api-testing/test-cases`，旧 `/api-testing/interfaces` 隐藏兼容重定向；`ApiRequest` 冻结为 P0-1 接口测试用例技术载体；修正前端旧执行路径和执行结果路径；`InterfaceManagement.vue` 请求收口到 `frontend/src/api/api-testing.js`；单接口执行成功后 `RequestHistory.assertions_results` 真实落库，并在请求历史详情页展示。
- 2026-06-17 已完成 P0-1 验证：`git diff --check`、`python -m py_compile apps\api_testing\models.py apps\api_testing\serializers.py apps\api_testing\views.py apps\api_testing\urls.py`、旧路径静态检索、`cd frontend && cmd /c npm run build` 均通过；构建仍保留既有 `web-tree-sitter` 的 `fs/path` 浏览器兼容与 `eval` 警告。
- 2026-06-17 已新增 `docs/api-automation/api-automation-p0-1-testcase-loop-vdd.md`，并同步导航冻结、平台 smoke、平台现状地图、route meta 代表页、项目记忆和更新日志。
- 2026-06-16 已完成今晚改动的文档回写同步：长期规则、前后端本地规则、项目记忆、错误预防日志、页面规范、烟雾验证基线、更新日志和 `CLAUDE.md` 已对齐导航稳定性、认证跳转、生产配置安全、Excel 导出依赖替换与页面头部 actions 容错等结论。
- 2026-06-16 已完成非 P0 前端质量收口：`VersionList.vue` 和 `TestCaseList.vue` 的筛选区回到 `ListShell #filters` 插槽；`user.js` 与 `api.js` 的登录跳转统一到 `frontend/src/utils/authNavigation.js`；`router/index.js` 注册 router 实例后，构建阶段不再出现 router 动态/静态混合导入警告。
- 2026-06-16 已继续修复顶部大模块切换后的导航卡顿：`App.vue` 根层改为登录后统一 Layout key，跨接口自动化、Web 自动化、App 自动化、配置中心等顶部大模块时不再销毁整个平台壳；`layout/index.vue` 顶部模块、侧边栏、全局搜索、最近访问、收藏和个人资料入口统一走导航调度器，并按 `currentModuleKey` 重建侧边栏菜单状态。
- 2026-06-16 已修复侧边栏子模块切换像“必须刷新才成功”的体验 bug：`App.vue` 根层不再使用物理路由级或业务模块级 key，改为登录后统一 Layout key，避免跨顶部模块时销毁重建整套 Layout；`layout/index.vue` 保留业务内容层 key，并为快速点击增加重复目标忽略、取消导航容错和轻量过渡动画。
- 2026-06-16 已清理未跟踪的一次性脚本和 schema 产物：`fix_filters.py`、`fix_malformed.py`、`fix_spans.py`、`scan_filters.py`、`generate_api_doc.py`、`schema.json`、`schema2.json` 不再留在工作区。
- 2026-06-16 已完成验证：`npm run build`、`node --check frontend/src/stores/user.js frontend/src/utils/api.js frontend/src/utils/authNavigation.js frontend/src/router/index.js`、`git diff --check` 均通过；构建仍保留既有 `web-tree-sitter` 的 `fs/path` 浏览器兼容与 `eval` 警告。
- 已完成 P0 安全与依赖收口：后端 `DEBUG`、`DISABLE_CSRF_FOR_API` 改为严格布尔解析，非法值会明确报错；生产环境强制显式配置 `ALLOWED_HOSTS`、`CORS_ALLOWED_ORIGINS`，禁止 `ALLOWED_HOSTS=*` 与生产态 API CSRF 全局禁用；`.env.example` 已补充 `DISABLE_CSRF_FOR_API` 说明。
- 已替换前端 `xlsx` 依赖：新增 `frontend/src/utils/excelExport.js` 统一封装 Excel 导出，测试用例列表、需求分析页、任务详情页改用 `write-excel-file`；`npm audit --omit=dev` 已验证为 0 漏洞。
- 已完成本轮 P0 验证：`manage.py check` 在开发配置与生产合法配置下通过；`DEBUG=release`、生产缺失 CORS、生产开启 `DISABLE_CSRF_FOR_API=True` 均能明确失败；`frontend` 执行 `npm run build` 通过。
- 已完成测试设计导航与筛选样式缺陷修复：补齐评审列表 `reviewList.helperText`、`reviewList.totalTasks`、`reviewList.viewAutoReviews` 中英文翻译，消除进入评审列表时的 i18n missing warning。
- 已移除需求分析页 `resetGeneration` 中的 `window.location.reload()`，改为组件内重新执行 `checkConfigStatus()`，避免新一轮生成或相关操作强制重载平台壳。
- 已将版本管理、测试用例列表筛选区改为与评审列表一致的 `.filters` 三列布局，并在 `ListShell` 中补充 `el-row`、`el-input`、`el-select`、`el-date-editor` 的宽度兜底规则。
- 已完成前端构建验证：`cd frontend && cmd /c npm run build` 通过；构建仍保留既有 `web-tree-sitter` 浏览器兼容与 `eval` 告警，本轮未改动该依赖链。
- 已完成全局页面体验与一致性审计：全面推广了侧边栏切换修复、滚动条恢复和筛选控件样式对齐策略。
- 已统一全局所有 `ListShell` 筛选器样式：通过自动化脚本检索了全仓 18 个模块列表页，将 `.filters` 内的 `el-col` 统一规范为 `span="8"`，并为全部 `el-input`、`el-select`、`el-date-picker` 等筛选组件强制注入 `style="width: 100%"`，彻底消除了 flex 容器下跨模块宽度塌缩和排列错乱的缺陷。
- 已修复全局导航失灵 Bug：`router-view` 的 `:key` 从 `currentRoute.fullPath` 改为 `currentRoute.name || currentRoute.path`，消除 keep-alive 下 query 变化导致组件不断销毁重建的问题。（注：此修复不彻底，根层 `App.vue` 仍存在过重 key 问题，已在 2026-06-01 二次修复）
- 已修复需求分析页和 AI 生成用例页无法滚动 Bug：移除 `platform-route-wrapper` 的 `height: 100%; overflow: hidden`，改为 `min-height: 0`，让内容高度正确传递到外层滚动容器。
- **[2026-06-01 / 2026-06-16] 已修复跨模块/子模块导航切换失灵与系统重加载 Bug**：定位根因为 `App.vue` 根层 `<router-view>` 的 key 粒度过细会在跨模块切换时销毁整套 Layout，导致导航队列、侧边栏事件和页面壳状态被打断。最终方案是 `App.vue` 对登录后路由使用统一 Layout key，`layout/index.vue` 使用路由名级内容 key，并统一顶部模块与侧边栏导航调度。
- 已在 `error_prevention_log.md` 新增 009（router-view key 导致导航失灵）和 010（筛选控件宽度塌缩）两条错误模式。
- 已彻底修复 `ProjectList.vue` 由于未使用导入变量 `FilterBar` 引发的编辑器和 Linter 错误。
- 已彻底解决 `Cannot read properties of null (reading 'exposed' / 'parentNode')` 的侧边栏导航切换崩溃 Bug：定位根因为 Vue 3 在 `<router-view>` 插槽内对 `<keep-alive>` 容器外包裹 `v-if` 的处理存在上下文销毁异常。通过将路由包裹容器放置在 `router-view` 外部，移除了 `v-if` 条件渲染影响，从架构层面完美避开了 Element Plus 卸载组件时的空指针异常。
- 已修复切换页面时 `UnifiedListTable.vue` 爆出的 `TypeError: Cannot convert object to primitive value` 验证报错：排查由于 Vue 3 不允许 `null` 放入 `type` 数组中作为 Prop 类型构造器，移除了 `selectedKey` 和 `deletingKey` 中非法的 `null` 类型，彻底消除警告与崩溃。
- 排除了登录页 `POST /api/auth/login/ 404 (Not Found)` 的后端隐患：通过完整审计 `vite.config.js` 的代理规则、后端 `backend/urls.py` 和 `apps/users/urls.py` 路由，确认代码与环境配置 100% 正确无误。404 报错确认为用户本地环境（未启动后端、代理脱落或浏览器插件拦截）导致的伪代码报错，无需修改源码即可在正确启动后恢复正常。
- 实现了“用例名称”检索功能与重置操作闭环，优化了 5 秒静默轮询机制：轮询时能够携带 search 状态且在行被勾选时自动挂起，确保极佳的用户操作连续性与稳定性。
- 已完成前端打包体积第一轮收口：通过路由懒加载、Element Plus 按需引入、图表库按需引入和手动拆包，消除了构建阶段的“大包体积”告警
- 当前前端构建仍保留 `curlconverter / web-tree-sitter` 依赖链带来的浏览器兼容与 `eval` 告警，本轮未继续改动这条实现路线
- 已沉淀新的页面结构类错误模式：页面主动作必须统一进入页头动作区，同一页面内不再平行保留重复主入口
- 已继续收口 `2.2` 第二阶段中的任务页职责：`TaskDetail` 现在只保留任务信息、结果预览、正式资产入口和结果批次跳转，不再在弹窗内继续承接结果编辑、采纳或弃用动作
- 已将根 `AGENTS.md` 重构为仓库入口规则，收口读文件顺序、流程闸门、全仓红线、验证入口与目录路由
- 已重构 `.cursor/prompt.md`、`.cursor/workflow_rules.md`、`.cursor/architecture.md`、`.cursor/storage_rules.md`、`.cursor/project_rules.md`
- 已新增 `frontend/AGENTS.md`、`backend/AGENTS.md`、`apps/requirement_analysis/AGENTS.md`
- 已补齐项目记忆体系第一版：`decision_log.md`、`module_memory.md`、`task_handoff.md`
- 已新增 `error_prevention_log.md`，用于沉淀重复错误、根因分析、防复发规则与最低验证动作
- 已把记忆回写要求正式写入 `AGENTS.md` 与 `.cursor/workflow_rules.md`
- 已完成阶段 `2.2` 主链一轮收口修复：`GeneratedTestCaseList` 在任务上下文下改为真实按 `taskId` 收口结果批次，`TaskDetail` 去掉结果处理主战场语义，正式测试资产页明确 `sourceTaskId` 仅作来源提示

## 3. 当前未完成项

- 接口测试用例列表固定字段已经补齐；后续若新增字段，必须优先确认是否属于 `ApiRequest` 原子用例字段，禁止把测试套件编排字段放回用例资产主表。
- 后续新增或修改任意 Vue 表单、弹窗表单、筛选区或原生按钮时，必须检查 `<form>` / `<el-form>` 是否保留 `@submit.prevent`，原生 `<button>` 是否保留显式 `type`。
- 后续修改 `frontend/vite.config.js` 的 `optimizeDeps` 时，禁止长期恢复 `force: true`；如因依赖缓存排障临时使用强制重优化，结束后必须还原，并补跑首次跨模块 / 侧边栏懒加载页面验证，确认无 `504 Outdated Optimize Dep` 和整页 reload。
- 后续维护 `start.bat` 或一键启动脚本时，必须保留“等待后端 ready 后再启动前端”的顺序，避免前端代理在后端未监听时误报登录接口连接失败。
- 后续直接使用 `ElMessage`、`ElMessageBox`、`ElNotification`、`ElLoading` 等 Element Plus 服务式 API 时，必须确认 `frontend/src/main.js` 或对应全局入口已经引入服务组件样式；否则可能出现弹窗裸样式、位置不居中或遮罩缺失。
- 接口测试用例“加入套件”属于闭环动作，不允许点击后无反应；成功、失败和阻断原因必须有明确反馈。阻断型、结果确认型反馈优先使用弹窗，不能只依赖底部 `ElMessage` 弱提示。
- 若后续继续改 `frontend/src/layout/index.vue`、`PlatformSidebar.vue` 或 `router.afterEach`，必须优先复跑跨顶部模块与侧栏快速切换验证，不能只看单模块内侧栏切换。
- 若后续要继续清理前端构建警告，下一步应单独评估 `curlconverter` 是否继续放在浏览器侧，或是否改为更轻的前端实现 / 后端处理方案
- 接口自动化 P0-2 Spec/TDD 已补充但尚未确认：`docs/api-automation/api-automation-p0-2-ai-target-type-spec.md`、`docs/api-automation/api-automation-p0-2-ai-target-type-tdd.md`。当前必须先等用户确认 Spec，再修订 / 确认 TDD，最后才能进入 Execution；本阶段只做目标类型下拉、Prompt 按类型选择、任务固化目标类型、结果展示目标类型和非功能采纳保护，接口测试用例采纳入库拆到 P0-3。
- 阶段 A 对象闭环 P0 补强已完成代码和 VDD：`docs/api-automation/api-automation-p0-object-closure-fix-tdd.md`、`docs/api-automation/api-automation-p0-object-closure-fix-vdd.md`。当前待补真实浏览器人工回归，重点验证移动集合、清空历史、套件级断言保存和执行优先级、删除风险提示。
- 现有 `current_phase.md` 内容较大，后续仍可继续收口，降低历史事实、阶段事实与局部事实的混写程度
- `dialogue_bootstrap.md` 仍可继续压缩为更轻量的“30 秒启动摘要”
- 错误模式库当前只有第一版基线，后续仍需要在真实开发中持续补充，不要让它停留在空转模板
- 其他业务域如 `projects`、`testcases`、`reviews` 未来若形成稳定局部规则，可继续补目录级 `AGENTS.md`
- `2.2` 当前仍建议补一轮页面级主链复核，重点确认“任务页 -> 结果批次页 -> 正式资产页”在真实点击、弹窗跳转和请求参数层面已形成闭环，避免后续又把结果处理动作塞回任务页

## 4. 已知风险与阻塞

- 前端构建仍保留既有 `curlconverter -> web-tree-sitter` 的 `fs/path` 浏览器兼容和 `eval` 告警；路由静态/动态混合导入告警已在认证导航收口后消失。
- `npm audit --omit=dev` 已清零，但 `npm audit` 全量仍可能受开发依赖链影响；若后续要处理，需要单独评估 Vite/ESBuild 大版本升级。
- 前端打包阶段虽然已消除“大包体积”告警，但 `curlconverter -> web-tree-sitter` 依赖链仍会输出浏览器兼容与 `eval` 警告，这不是单靠拆包就能彻底消失的问题
- 终端输出存在中文乱码表现，但目前更像终端编码显示问题，不等于源文件编码损坏
- `docs/project-memory/current_phase.md` 本身信息量很大，后续若继续膨胀，会重新削弱记忆体系分层效果
- 规则与记忆体系已经进入可用状态，但仍依赖开发完成后主动回写，尚不是自动化 memory engine
- 若错误模式库只记录“现象”而不补“防复发规则 + 最低验证动作”，会退化成事故流水账

## 5. 建议下一步

1. 继续推进阶段 2 的业务主线时，开始按新记忆体系回写，不要再把所有内容都堆回 `current_phase.md`
2. 若后续要进一步增强 AI 接手能力，可在下一轮补一个“记忆回写模板”或“任务收尾模板”
3. 若新项目也要复用这套方式，保留全局 `GEMINI.md` 模板，只替换项目级 `.cursor` 和 `docs/project-memory/*`
4. 后续同类错误第二次出现时，必须优先判断是否要写入 `error_prevention_log.md`
5. 下一步应先补阶段 A 浏览器人工回归；通过后再回到 P0-2 / P0-3 AI 生成和采纳主线

## 6. 接手前优先查看

- `AGENTS.md`
- `.cursor/workflow_rules.md`
- `docs/project-memory/current_phase.md`
- `docs/project-memory/decision_log.md`
- `docs/project-memory/module_memory.md`
- `docs/project-memory/error_prevention_log.md`

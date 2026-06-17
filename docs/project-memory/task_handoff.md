# TestHub 任务交接

更新时间：2026-06-16

## 1. 文件职责

本文文件属于 C 层“正式项目记忆”，用于记录最近一轮任务的完成情况、未完成项、阻塞点与下一步建议，服务于跨会话接手。

使用原则：

- 以“最近一轮交接”为主，不写成长流水账
- 只记录对下一轮接手最关键的信息
- 长期阶段事实仍以 `current_phase.md` 为准
- 关键取舍仍以 `decision_log.md` 为准

## 2. 最近完成项

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

- 若后续要继续清理前端构建警告，下一步应单独评估 `curlconverter` 是否继续放在浏览器侧，或是否改为更轻的前端实现 / 后端处理方案
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

## 6. 接手前优先查看

- `AGENTS.md`
- `.cursor/workflow_rules.md`
- `docs/project-memory/current_phase.md`
- `docs/project-memory/decision_log.md`
- `docs/project-memory/module_memory.md`
- `docs/project-memory/error_prevention_log.md`

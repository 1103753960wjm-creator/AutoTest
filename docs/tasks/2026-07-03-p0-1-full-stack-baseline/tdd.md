# TDD：P0.1 前后端与样式上线阻断项第一批

## 1. 标题

- 任务名称：P0.1 前后端与样式上线阻断项第一批
- 日期：2026-07-03
- 关联 Spec/SDD：`docs/tasks/2026-07-03-p0-1-full-stack-baseline/spec-sdd.md`
- 当前阶段：TDD
- 目标验证等级：V3

## 2. 大白话测试目标

- 这次测试要证明什么：
  - 样式已经有统一 token 入口，新改基础样式不再继续散写颜色、圆角、间距和阴影。
  - 前端点名页面不再直接用裸 `axios` 请求后端，而是走统一 API 封装。
  - 后端敏感接口不再匿名可访问，未登录用户会拿到 401/403，有权限用户仍能正常访问自己的资源。
- 用户最关心的结果是什么：
  - 页面不要因为样式 token 引入出现明显错位或按钮、表格、弹窗样式异常。
  - 数据工厂和执行详情功能不要回退。
  - 未登录用户不能绕过登录访问生成任务、配置状态、报告文件或进度接口。
- 哪些旧功能不能被破坏：
  - 登录、token 刷新、退出登录。
  - 数据工厂筛选、列表、新增、删除、统计。
  - 执行详情页状态更新、历史查看和删除。
  - 需求分析生成任务的登录用户正常流程。
  - App 自动化报告的有权限访问。

## 3. 测试范围

- 必测模块：
  - 前端全局样式入口。
  - 前端数据工厂、执行详情、统一请求封装。
  - 后端需求分析权限、App 自动化报告访问权限、接口公开白名单。
- 后端必测文件：
  - `backend/settings.py`
  - `backend/urls.py`
  - `apps/requirement_analysis/views.py`
  - `apps/app_automation/views/execution_views.py`
- 必测页面：
  - 数据工厂页。
  - 数据工厂选择器被使用的页面或弹窗。
  - 执行详情页。
  - 需求分析相关页面的配置检查、生成、进度查询入口。
  - App 自动化执行报告入口。
- 必测接口：
  - `GET /api/data-factory/categories/`
  - `GET /api/data-factory/tags/`
  - `GET /api/data-factory/`
  - `POST /api/data-factory/`
  - `DELETE /api/data-factory/{id}/`
  - `GET /api/data-factory/statistics/`
  - `GET /api/executions/plans/{id}/`
  - `PATCH /api/executions/run_cases/{id}/update_status/`
  - `GET /api/executions/run_cases/{id}/history/`
  - `DELETE /api/executions/run_cases/{id}/`
  - `GET /api/requirement-analysis/config/check/`
  - `POST /api/requirement-analysis/testcase-generation/generate/`
  - `GET /api/requirement-analysis/testcase-generation/{id}/progress/`
  - `GET /api/app-automation/executions/{id}/report/`
  - `GET /api/app-automation/executions/{id}/report/{file_path}`
- 必测数据或状态：
  - 未登录状态。
  - 已登录且有项目/任务权限的状态。
  - 已登录但无对象权限的状态，如环境允许准备。
  - 数据工厂至少一条可查询数据和一条可删除测试数据。
  - 执行计划和运行用例至少一组测试数据。
- 不测范围及原因：
  - 不测全站所有页面视觉回归，本轮不是 P0.3/P1.2 大规模页面壳统一。
  - 不测 WebSocket/SSE 统一封装，这是前端代码 P0.2。
  - 不测模拟实现清理和误导性注释删除，除非用户明确把它们纳入本轮。
  - 不测数据库迁移，因为本轮不允许改模型和迁移。

## 4. 测试数据准备

- 需要什么账号或权限：
  - 一个普通登录账号。
  - 一个拥有目标项目、需求生成任务、执行计划和 App 自动化执行记录访问权限的账号。
  - 如环境允许，再准备一个无目标项目权限的账号。
- 需要什么项目、用例、任务或历史数据：
  - 至少一个测试项目。
  - 至少一个数据工厂分类、标签和数据记录。
  - 至少一个执行计划、运行用例和运行历史。
  - 至少一个需求分析生成任务。
  - 至少一个 App 自动化执行记录及报告文件。
- 需要准备哪些正常数据：
  - 数据工厂列表有数据。
  - 执行详情页能打开。
  - 需求生成进度能查到。
  - App 报告文件存在。
- 需要准备哪些异常数据：
  - 未登录请求。
  - 不存在的对象 id。
  - 无权限对象 id。
  - 数据工厂删除失败样本，如被引用或不存在的记录。
- 是否需要旧数据兼容样本：
  - 需要。至少使用一条已有数据工厂记录和已有执行详情记录，确认请求收口后旧数据仍能展示。

## 5. 后端专项验证

| 编号 | 验证对象 | 验证内容 | 通过标准 |
| --- | --- | --- | --- |
| BE-01 | `backend/settings.py` | DRF 默认权限仍是 `IsAuthenticated`，生产安全配置不被本轮放宽 | 不出现为了方便访问而改成 `AllowAny` 或放开安全配置 |
| BE-02 | `backend/urls.py` | 根路由中是否存在绕过 API 权限体系的静态报告文件服务 | 敏感报告或 media 文件不能通过无认证根路径直接访问 |
| BE-03 | `apps/requirement_analysis/views.py` | `AllowAny`、`csrf_exempt`、`permission_classes=[]` 是否只保留在确认公开白名单中 | 非公开需求生成、配置、任务进度接口必须要求认证 |
| BE-04 | `apps/requirement_analysis/views.py` | 进度接口是否还只把 `task_id` 当安全凭证 | 未登录不能仅凭 `task_id` 查询进度；无权限用户不能看别人的任务 |
| BE-05 | `apps/app_automation/views/execution_views.py` | App 自动化报告入口是否需要登录和对象权限 | 未登录返回 401/403，有权限用户正常访问自己的报告 |
| BE-06 | 后端公开接口白名单 | 明确哪些接口允许匿名访问，以及为什么 | 白名单有清单、有理由；清单外接口默认需要认证 |
| BE-07 | 后端编译级检查 | 受影响后端文件是否有语法错误 | `python -m py_compile ...` 返回 0 |
| BE-08 | 后端请求级检查 | 未登录、无权限、有权限三类请求是否符合预期 | 未登录 401/403，无权限 403，有权限 200 或业务成功 |

后端专项验证必须在 Execution 完成后写入 VDD。若环境无法发真实请求，VDD 必须说明原因，并至少保留静态权限扫描和编译级验证结果。

## 6. 主流程用例

| 编号 | 操作步骤 | 预期结果 | 通过标准 |
| --- | --- | --- | --- |
| TC-01 | 构建前静态检查 `design-tokens.scss` 和 `global.scss` | token 文件存在，`global.scss` 已引入，基础样式引用 `--th-*` | `rg -n "design-tokens|--th-" frontend/src/assets/css` 能看到令牌和引入 |
| TC-02 | 打开数据工厂页，执行查询、重置、新增、删除和统计刷新 | 页面功能和改造前一致，请求由 API 封装发出 | 页面无报错，接口状态正确，数据刷新正确 |
| TC-03 | 打开执行详情页，查看执行计划详情、更新运行用例状态、查看历史 | 页面功能和改造前一致 | 状态更新成功，历史弹窗或列表正常 |
| TC-04 | 登录后访问需求分析配置检查、生成和进度接口 | 登录用户仍可正常访问自己的任务 | 返回 200 或业务成功状态，页面展示不回退 |
| TC-05 | 登录后访问 App 自动化执行报告入口 | 有权限用户可打开报告或报告文件 | 返回 200 或正常文件响应 |
| TC-06 | 执行前端构建 | 构建通过 | `cd frontend && cmd /c npm run build` 返回 0 |
| TC-07 | 执行后端编译级验证 | 受影响后端文件语法通过 | `python -m py_compile ...` 返回 0 |
| TC-08 | 执行后端权限静态扫描 | 高风险权限写法已审查并收口 | `AllowAny`、`csrf_exempt`、`permission_classes=[]` 只出现在确认白名单或有明确说明的位置 |

## 7. 异常和边界用例

| 编号 | 场景 | 操作步骤 | 预期结果 | 通过标准 |
| --- | --- | --- | --- | --- |
| EX-01 | 未登录访问敏感配置 | 清空 token 后请求 `GET /api/requirement-analysis/config/check/` | 返回 401/403 | 不返回 200，不泄露配置详情 |
| EX-02 | 未登录发起需求生成 | 清空 token 后请求 `POST /api/requirement-analysis/testcase-generation/generate/` | 返回 401/403 | 不创建任务，不返回生成结果 |
| EX-03 | 未登录查询任务进度 | 清空 token 后请求 `GET /api/requirement-analysis/testcase-generation/{id}/progress/` | 返回 401/403 | 不能只靠 `task_id` 访问进度 |
| EX-04 | 未登录访问 App 报告 | 清空 token 后请求 `/api/app-automation/executions/{id}/report/` 和文件路径 | 返回 401/403 | 不能直接下载或浏览报告文件 |
| EX-05 | 无权限访问对象 | 用无权限账号访问别人的任务或报告 | 返回 403 | 不返回对象内容 |
| EX-06 | 数据工厂空筛选 | 用不存在关键词查询数据工厂 | 页面显示空态或空列表 | 不报错，不无限 loading |
| EX-07 | 请求失败统一处理 | 模拟后端 500 或使用不存在对象 id | 页面给出错误提示 | 不出现未捕获异常，不整页刷新 |
| EX-08 | token 过期 | 使用过期 access token 和有效 refresh token 访问改造页面 | 触发统一刷新或回登录 | 不在页面里散写跳转，不出现多套错误处理 |
| EX-09 | 快速点击 | 数据工厂连续查询/重置/删除，执行详情连续更新状态 | 最终状态一致，按钮 loading 不错乱 | 不重复提交造成明显错误 |
| EX-10 | 旧数据兼容 | 用已有数据工厂记录和执行详情记录打开页面 | 旧数据正常展示 | 不因 API 封装变化丢字段 |

## 8. 回归检查

- 受影响旧入口：
  - 数据工厂页及数据工厂选择器。
  - 执行详情页。
  - 需求分析生成入口和进度入口。
  - App 自动化报告入口。
- 受影响旧字段：
  - 数据工厂列表字段、分类、标签、统计。
  - 执行计划详情、运行用例状态、历史记录。
  - 需求生成任务 id、状态、进度、错误信息。
- 受影响旧页面：
  - `frontend/src/views/data-factory/DataFactory.vue`
  - `frontend/src/components/DataFactorySelector.vue`
  - `frontend/src/views/executions/ExecutionDetailView.vue`
  - 需求分析生成页面和任务详情页。
  - App 自动化报告访问页面。
- 受影响缓存、轮询、异步任务、日志或通知：
  - token 刷新队列和 401 处理。
  - 需求生成进度查询。
  - 后端权限失败日志。
  - 本轮不改通知链路。

## 9. 验证命令和页面操作

- 静态验证命令：
  - `rg -n "design-tokens|--th-" frontend/src/assets/css frontend/src/components/page-shells frontend/src/components/platform-shared`
  - `rg -n "#409eff|#f5f7fa|#f5f5f5" frontend/src/assets/css frontend/src/components/page-shells frontend/src/components/platform-shared`
  - `rg -n "axios" frontend/src -g "*.js" -g "*.vue"`
  - `rg -n "AllowAny|csrf_exempt|permission_classes\\s*=\\s*\\[\\]" apps/requirement_analysis/views.py apps/app_automation/views/execution_views.py backend/urls.py backend/settings.py`
  - `git diff --check -- frontend/src apps/requirement_analysis/views.py apps/app_automation/views/execution_views.py backend/settings.py backend/urls.py docs/tasks/2026-07-03-p0-1-full-stack-baseline`
- 构建或编译验证命令：
  - `cd frontend && cmd /c npm run build`
  - `python -m py_compile apps\\requirement_analysis\\views.py apps\\app_automation\\views\\execution_views.py backend\\settings.py backend\\urls.py`
- 接口验证方式：
  - 使用浏览器、curl、Postman 或 Django/DRF 测试客户端分别带 token 和不带 token 请求敏感接口。
  - 未登录请求必须返回 401/403。
  - 登录且有权限请求必须保持成功。
- 页面验证路径：
  - 登录后打开数据工厂页，执行查询、新增、删除和统计刷新。
  - 登录后打开执行详情页，执行状态更新和历史查看。
  - 登录后打开需求分析生成页，检查配置状态和进度查询。
  - 登录后打开 App 自动化报告入口。
- 是否需要执行 `scripts/rule_check.ps1`：是。
  - 命令：`powershell -ExecutionPolicy Bypass -File scripts/rule_check.ps1`

## 10. 失败判定

- 出现哪些现象算失败：
  - `design-tokens.scss` 没有被全局引入。
  - 新改样式继续新增裸色值，且没有合理说明。
  - `frontend/src` 中除 `utils/api.js` 外仍存在裸 `axios.get/post/patch/delete`。
  - `main.js` 仍直接配置 axios defaults。
  - 未登录用户可以访问敏感需求生成、配置状态、进度或 App 报告。
  - 登录用户无法访问自己原本应可访问的资源。
  - 数据工厂或执行详情页核心功能回退。
  - 前端构建失败，且失败来自本轮改动。
  - 后端编译失败，且失败来自本轮改动。
- 验证连续失败几次必须暂停：
  - 同一失败连续 2 次必须暂停并写入 `error_event_log.md`。
- 失败后允许修复的范围：
  - 只允许在本轮已确认的样式、前端请求、后端权限文件范围内修复。
  - 如需改接口字段、模型、迁移、路由结构、AI 主链、执行器或报告主链，必须暂停重新确认。
- 失败后必须写入的日志：
  - 任意命令失败、构建失败、编译失败、接口异常、页面红错、规则执行偏差，都必须先写入 `docs/project-memory/error_event_log.md`。

## 11. 进入 Execution 条件

- [ ] 主流程用例已明确。
- [ ] 异常和边界用例已明确。
- [ ] 验证命令已明确。
- [ ] 失败判定已明确。
- [ ] 用户已确认可以进入实现。

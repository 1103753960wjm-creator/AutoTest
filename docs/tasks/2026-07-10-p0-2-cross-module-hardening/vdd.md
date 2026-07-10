# VDD：各部分 P0.2 跨模块硬化第一批

## 1. 标题

- 任务名称：各部分 P0.2 跨模块硬化第一批
- 日期：2026-07-10
- 关联 Spec/SDD：`docs/tasks/2026-07-10-p0-2-cross-module-hardening/spec-sdd.md`
- 关联 TDD：`docs/tasks/2026-07-10-p0-2-cross-module-hardening/tdd.md`
- 当前阶段：VDD
- 本轮最高验证等级：V2 构建验证；局部生产配置和脱敏 helper 达到 V3 行为验证

## 2. 本轮改了什么

- 大白话总结：
  - 本轮按用户确认跳过剩余浏览器回归，直接进入 P0.2 第一批。
  - 已完成生产配置复核、核心配置文档补说明、前端敏感调试日志清理、后端 AI 模型调用日志脱敏和敏感信息保护最小闭环。
  - 没有进入实时连接统一封装，没有进入接口错误结构统一试点。
- 修改的主要文件：
  - `backend/settings.py`
  - `.env.example`
  - `apps/requirement_analysis/models.py`
  - `frontend/src/views/auth/Login.vue`
  - `frontend/src/utils/api.js`
  - `frontend/src/stores/user.js`
  - `frontend/src/router/index.js`
  - `frontend/src/views/requirement-analysis/AIModelConfig.vue`
  - `frontend/src/views/requirement-analysis/PromptConfig.vue`
  - `frontend/src/views/requirement-analysis/GenerationConfigView.vue`
  - `frontend/src/views/configuration/AIIntelligentModeConfig.vue`
- 新增的主要文件：
  - `apps/core/security.py`
- 没有改但容易被误解的范围：
  - 没有修改原生参考仓库 `E:\原生testhub_platform-main\testhub_platform-main`。
  - 没有新增依赖。
  - 没有改数据库模型和迁移。
  - 没有改成功响应结构。
  - 没有继续做接口错误结构统一。
  - 没有迁移 SSE / WebSocket 统一封装。

## 3. 验收标准核对

| 验收项 | 是否通过 | 证据 | 备注 |
| --- | --- | --- | --- |
| 生产环境不能使用默认或弱 `SECRET_KEY` | 是 | `backend/settings.py` 增加示例值、默认值和长度小于 32 的阻断；非法生产配置验证通过 | 防止生产沿用 `.env.example` 示例密钥 |
| 生产配置缺 hosts、缺 CORS、开启 API CSRF 禁用时必须失败 | 是 | `manage.py check` 开发配置、合法生产配置和非法生产配置抽样均已执行 | CORS 空值验证用 `CORS_ALLOWED_ORIGINS=','`，避免 decouple 回退 `.env` |
| `.env.example` 能说明生产必填项和敏感信息 | 是 | `.env.example` 已补 `SECRET_KEY`、`DEBUG`、`ALLOWED_HOSTS`、`CORS_ALLOWED_ORIGINS`、`DB_HOST`、`REDIS_URL` 和敏感信息说明 | 只补配置说明，不写真实密钥 |
| 登录、token 刷新、路由守卫不再输出 token / 用户对象 / axios error 对象 | 是 | 目标源码扫描未命中已清理的 `console` 关键字；前端构建通过 | 未做浏览器运行时复测 |
| AI 配置页和提示词 / 生成配置页不再把 API Key、表单对象或错误对象打到控制台 | 是 | 相关页面 `console` 输出已删除；目标源码扫描和构建产物扫描未命中 | 保留页面原有错误提示 |
| AI OpenAI-compatible 调用日志不输出完整响应正文、API Key、token、Authorization、Cookie | 是 | `apps/core/security.py` 新增脱敏工具；`apps/requirement_analysis/models.py` 日志统一走脱敏；脱敏函数抽样通过 | 成功响应日志只保留 keys 和 choices_count 摘要 |
| 不影响 AI 生成空响应保护和 OpenAI-like 响应兼容 | 是 | `models.py` 保留并继续使用 `_extract_openai_compatible_content`、`_require_non_empty_content` | 该能力来自上一轮，不回退 |
| 不引入明显回归 | 部分通过 | `py_compile`、`manage.py check`、`npm run build`、`rule_check.ps1`、`git diff --check` 均通过 | 真实浏览器回归按用户要求跳过，所以不能算 V4 |

## 4. 验证执行记录

| 验证类型 | 命令或操作 | 结果 | 证据 |
| --- | --- | --- | --- |
| 后端编译 | `.\venv\Scripts\python.exe -m py_compile backend\settings.py apps\core\security.py apps\requirement_analysis\models.py` | 通过 | 证明受影响 Python 文件语法可加载 |
| 后端开发配置检查 | `.\venv\Scripts\python.exe manage.py check` | 通过 | 开发配置未被生产校验误伤 |
| 合法生产配置检查 | 设置 `DEBUG=False`、强 `SECRET_KEY`、明确 `ALLOWED_HOSTS`、明确 `CORS_ALLOWED_ORIGINS`、`DISABLE_CSRF_FOR_API=False` 后执行 `manage.py check` | 通过 | 合法生产配置可启动检查 |
| 非法生产配置检查 | 弱 `SECRET_KEY`、`ALLOWED_HOSTS=*`、`DISABLE_CSRF_FOR_API=True`、`CORS_ALLOWED_ORIGINS=','` 分别执行启动检查 | 通过 | 均被阻断或明确报错 |
| 脱敏 helper 抽样 | 构造 JWT、API Key、Cookie、password 文本和结构化数据调用 `redact_text` / `redact_json_for_log` | 通过 | 原始敏感值未出现在脱敏结果里 |
| 前端构建 | `cd frontend && cmd /c npm run build` | 通过 | 仍只有既有 `web-tree-sitter` 的 `fs/path externalized` 和 `eval` 警告 |
| 前端源码扫描 | `rg -n "console\.|Login result|User store state|api_key:',|Saving config with data|ConfigForm changed|Token刷新|Navigated from" ...` | 通过 | 目标敏感调试日志未命中 |
| 前端构建产物扫描 | `rg -n "console\." frontend/dist/assets -g "Login*.js" -g "AIModelConfig*.js" -g "PromptConfig*.js" -g "GenerationConfigView*.js" -g "AIIntelligentModeConfig*.js"` | 通过 | 返回 1 代表未找到目标产物日志 |
| AI 日志敏感输出扫描 | `rg -n "响应内容|发送POST请求到: \{url\}|API调用失败: \{repr|流式请求异常: \{e\}|api_key.*logger|Authorization.*logger" apps/requirement_analysis/models.py apps/core/security.py` | 通过 | 目标高风险日志写法未命中 |
| 规则检查 | `powershell -ExecutionPolicy Bypass -File scripts\rule_check.ps1` | 通过 | P0 高频规则扫描通过 |
| Diff 检查 | `git diff --check` | 通过 | 仅有 Windows LF/CRLF 转换提示 |

## 5. 失败和错误事件

- 本轮是否出现错误事件：是。
- 已写入 `error_event_log.md` 的事件：
  - 并行上下文读取命令超时。
  - 规则文件读取未显式指定 UTF-8 导致终端乱码。
  - `models.py` 行段读取命令超时。
  - 文档补丁因错误日志非 UTF-8 字节失败。
  - AI 配置页批量补丁上下文不匹配。
  - 前端构建产物通配路径扫描命令失败。
  - 缺 CORS 生产配置验证脚本未真正覆盖空配置。
  - 缺 CORS 验证输出重定向编码导致匹配失败。
  - VDD 初次写入时路径基准落到外层目录，已删除误写文件并写入内层项目目录。
- 是否升级到 `error_prevention_log.md`：是。
  - 已沉淀“调试日志和异常日志不得输出敏感信息”的防复发规则。
  - PowerShell 中文 / 重定向编码问题已有既有 UTF-8 防复发规则覆盖，本轮不重复新增。
- 未解决错误：
  - 无本轮代码阻断级错误。

## 6. 未验证项

- 未验证项 1：真实浏览器登录、路由跳转、AI 配置页保存和需求分析生成页控制台运行时复查。
- 未验证原因：用户明确要求跳过回归，直接进入 P0.2。
- 可能风险：仍可能有未覆盖页面或第三方组件在运行时输出非目标日志。
- 后续如何补验证：P0.2 第二批开始前或第二批 VDD 中补浏览器控制台、Network 和主流程点击复查。

- 未验证项 2：生产构建部署到真实 Nginx / 生产环境后的完整启动验证。
- 未验证原因：当前只做本地 `manage.py check` 和前端构建。
- 可能风险：真实部署环境变量、反向代理、域名和 CORS 组合仍可能配置错误。
- 后续如何补验证：部署前用真实域名和生产环境变量跑一次启动检查与登录请求。

- 未验证项 3：所有业务模块日志全量脱敏。
- 未验证原因：本轮按第一批优先覆盖 AI 模型调用、登录认证、AI 配置页等高风险入口。
- 可能风险：旧模块里仍可能存在历史 `logger` 或 `console` 输出。
- 后续如何补验证：后续按模块做静态扫描和真实错误触发抽样。

## 7. 残余风险

- 用户要求跳过浏览器回归，所以本轮不能宣称 V4 回归通过。
- P0.1 / 阶段 A 尚未补完的真实浏览器主流程、真实 App 报告文件 200、真实无权限对象 403、浏览器 EventSource 凭据行为，仍是后续回归风险。
- App 自动化执行进度和接口测试工作区 WebSocket 已在第 11 节追加收尾中迁到 `useWebSocket`；真实浏览器运行时回归仍未执行。
- 接口错误结构只完成需求分析生成任务 400 / 404 试点，没有全仓统一。
- 工作树包含多轮未提交改动，后续提交前必须再次确认暂存范围，避免把临时产物或无关改动一起提交。

## 8. 回退和止损

- 可以直接回退的文件：
  - `.env.example`
  - `frontend/src/views/auth/Login.vue`
  - `frontend/src/utils/api.js`
  - `frontend/src/stores/user.js`
  - `frontend/src/router/index.js`
  - `frontend/src/views/requirement-analysis/AIModelConfig.vue`
  - `frontend/src/views/requirement-analysis/PromptConfig.vue`
  - `frontend/src/views/requirement-analysis/GenerationConfigView.vue`
  - `frontend/src/views/configuration/AIIntelligentModeConfig.vue`
- 需要谨慎回退的文件：
  - `backend/settings.py`：如果回退，会放松生产弱 `SECRET_KEY` 阻断。
  - `apps/requirement_analysis/models.py`：包含上一轮空响应兼容和本轮脱敏改动，不能粗暴回退整个文件。
  - `apps/core/security.py`：被 AI 模型日志脱敏引用，删除前必须同步回退引用。
- 回退后需要验证什么：
  - 后端 `py_compile` 和 `manage.py check`。
  - 前端 `npm run build`。
  - 敏感日志扫描。
- 是否涉及数据修复或迁移回滚：
  - 不涉及数据库迁移，不需要数据修复。

## 9. 最终结论

- 是否达到本轮目标：部分达到。
  - P0.2 第一批已完成。
  - P0.2 第二批和第三批已按用户要求合并推进，并完成保守试点。
- 是否可以交付：可以交付 P0.2 第一批、第二批需求分析 SSE 迁移、第三批错误结构试点，但必须带残余风险说明。
- 需要用户继续确认的事项：
  - 无新增确认项；后续默认按剩余迁移顺序继续。
- 下一步建议：
  - App 自动化实时进度 / 日志连接已在第 11 节追加收尾中迁移。
  - 接口测试工作区 WebSocket 已在第 11 节追加收尾中迁移。

## 10. 第二批和第三批合并追加 VDD

### 10.1 本次追加改了什么

- 第二批实时连接：
  - 新增 `frontend/src/composables/useEventSource.js`，统一 `EventSource` URL 构造、关闭、错误、有限重连和降级回调。
  - 新增 `frontend/src/composables/useWebSocket.js`，先落统一 WebSocket 创建、关闭、发送、有限重连入口；本轮不迁真实 App / 接口测试页面。
  - `frontend/src/composables/useGenerationTaskTracking.js` 改为通过 `useEventSource` 管理需求分析生成进度 SSE。
  - `RequirementAnalysisView.vue` 删除旧的页面内 `new EventSource`、旧轮询方法和相关调试 `console`，继续通过 tracker 获取生成进度。
- 第三批错误结构：
  - 新增 `apps/core/responses.py`，提供 `build_error_payload` 和 `error_response`。
  - 新增 `frontend/src/utils/errorMessage.js`，统一解析 `message`、`error`、`detail`、`details`、字段级错误和新试点错误结构。
  - `frontend/src/utils/api.js`、`Login.vue`、`RequirementAnalysisView.vue` 改用统一错误解析。
  - `TestCaseGenerationTaskViewSet.generate` 的 400 校验错误、`progress` 的 403 / 404 / 500 错误、`stream_progress` 的 403 / 404 JSON 错误接入新错误结构。
  - 成功响应结构不变。

### 10.2 追加验证记录

| 验证类型 | 命令或操作 | 结果 | 证据 |
| --- | --- | --- | --- |
| 后端编译 | `.\venv\Scripts\python.exe -m py_compile apps\core\responses.py apps\requirement_analysis\views.py` | 通过 | 新 helper 和试点接口语法通过 |
| 后端系统检查 | `.\venv\Scripts\python.exe manage.py check` | 通过 | Django 系统检查无问题 |
| 前端构建 | `cd frontend && cmd /c npm run build` | 通过 | 仍只有既有 `web-tree-sitter` 警告 |
| 请求级 404 试点 | APIClient 登录态请求不存在任务 `/progress/` | 通过 | 返回 404，包含 `code/message/details/request_id`，`code=task_not_found` |
| 请求级 400 试点 | APIClient 空请求 `POST /testcase-generation/generate/` | 通过 | 返回 400，包含 `code/message/details/request_id`，`code=validation_error` |
| 需求分析页旧 SSE 扫描 | `rg -n "console\.|new EventSource|startStreamingProgress\(|pollInterval" RequirementAnalysisView.vue` | 通过 | 无命中 |
| 需求分析页产物 console 扫描 | `rg -n "console\." frontend\dist\assets -g "RequirementAnalysisView*.js"` | 通过 | 无命中 |
| 规则检查 | `powershell -ExecutionPolicy Bypass -File scripts\rule_check.ps1` | 通过 | P0 红线扫描通过 |
| Diff 检查 | `git diff --check` | 通过 | 仅有 Windows LF/CRLF 转换提示 |

### 10.3 追加错误事件

- 第二三批全仓错误处理扫描输出过大超时，已收窄到试点范围。
- `apps/core` 目录读取命令超时，已改为直接按已确认路径补小文件。
- 请求级验证首次发现 400 分支未命中试点 helper，已定位真实 `generate` 分支并复测通过。

### 10.4 追加未验证项和残余风险

- 未做真实浏览器页面操作，所以不能证明运行时 Network 里 SSE 连接一定按预期关闭。
- App 自动化实时进度 / 日志连接已迁移，未做真实浏览器运行时回归。
- 接口测试工作区 WebSocket 已迁移，未做真实浏览器运行时回归。
- 未全仓替换错误响应，只做需求分析生成任务相关试点。
- 未新增全局 DRF exception handler，避免一次性改变所有接口错误契约。

## 11. P0.2 剩余实时连接和接口错误结构收尾追加

### 11.1 本次追加改了什么

- App 自动化测试用例执行进度不再在页面里直接 `new WebSocket`，改为通过 `frontend/src/composables/useWebSocket.js` 创建连接。
- App 自动化保留原来的失败降级口径：WebSocket 有限重连失败后，仍降级到 `getExecutionDetail` 轮询，不把一次连接失败误算成执行失败。
- 接口测试工作区的 WebSocket 调试连接不再直接 `new WebSocket`，改为走同一个 `createManagedWebSocket`。
- 接口测试工作区保留手动连接 / 断开、消息历史、发送文本或 JSON 的现有交互；发送时如果连接已断，会提示先建立连接。
- `useWebSocket` 修正初次 `connect()` 就触发 `onClose` 的隐患，避免页面一开始连接就多写“已关闭”消息。
- 接口测试 `move-collection` 的 3 个高频错误分支接入 `apps/core/responses.py`：未选择目标集合、跨项目移动、无权限移动。成功响应保持不变，旧 `error` 字段保留。

### 11.2 本次明确不做什么

- 不修改原生参考仓库。
- 不新增依赖。
- 不改数据库模型和迁移。
- 不新增全局 DRF exception handler。
- 不一次性全仓替换所有错误结构。
- 不把用户已明确跳过的真实浏览器回归写成通过。

### 11.3 追加验证记录

| 验证类型 | 命令或操作 | 结果 | 证据 |
| --- | --- | --- | --- |
| 后端编译 | `.\venv\Scripts\python.exe -m py_compile apps\core\responses.py apps\api_testing\views.py` | 通过 | 新错误 helper 引用和接口测试视图语法通过 |
| 后端系统检查 | `.\venv\Scripts\python.exe manage.py check` | 通过 | Django 系统检查无问题 |
| 接口请求级验证 | APIClient 登录态请求 `POST /api/api-testing/requests/{id}/move-collection/`，请求体为空 | 通过 | 返回 400，包含 `code/message/error/details/request_id`，`code=API_COLLECTION_REQUIRED` |
| 临时数据清理 | 查询 `p02_api_error_` 前缀用户 | 通过 | 结果 `leftover=0` |
| 前端构建 | `cd frontend && cmd /c npm run build` | 通过 | 仍只有既有 `web-tree-sitter` 的兼容和 `eval` 警告 |
| 源码直连扫描 | `rg -n 'new WebSocket|wsRetryCount|console\.error\(.*WebSocket|console\.error\(.*轮询|console\.error\(.*发送消息' ...` | 通过 | 业务页面无命中，只剩统一工具内部创建原生 WebSocket |
| 构建产物敏感日志扫描 | 只扫 `InterfaceManagement*.js` 和 `TestCaseList*.js` | 通过 | 未命中 `WebSocket连接失败:`、`轮询执行状态失败`、`处理 WebSocket 消息失败`、`发送消息失败:` |
| 规则检查 | `powershell -ExecutionPolicy Bypass -File scripts\rule_check.ps1` | 通过 | P0 红线扫描通过 |
| Diff 检查 | `git diff --check` | 通过 | 仅有 Windows LF/CRLF 转换提示 |

### 11.4 本次新增错误事件

- 并行读取规范、目录和 `git status` 超时，已改用非登录 shell 和窄范围读取。
- 目标文件读取、文档尾部读取和构建产物全目录扫描多次超时，已改为 `rg` 精确模式或追加式回写。
- `rg` 引号和参数写法曾失败，已改用单引号和拆分模式。
- APIClient 第一次临时数据缺 `ApiRequest.created_by`，已记录并清理临时数据。
- APIClient 第二次通过交互 `manage.py shell` 没有输出响应，已改为 `manage.py shell -c` 非交互执行，并沉淀到错误预防库。

### 11.5 最终结论

- P0.2 已完成第一批、第二三批保守试点，以及本次剩余实时连接和接口错误结构试点收尾。
- 除用户明确跳过的真实浏览器回归外，P0.2 本轮代码与文档收尾可以进入下一阶段。
- 最高验证等级：整体 V3。原因是包含后端真实请求级验证；但真实浏览器页面操作未执行，所以不能标成 V4 回归通过。

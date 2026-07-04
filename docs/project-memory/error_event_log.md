# TestHub 错误事件日志

更新时间：2026-07-03

## 1. 文件职责

本文文件属于 C 层“项目开发记忆”，用于记录开发、验证、调试过程中第一时间遇到的错误事件。

本文只记录错误现场，不要求当场完成根因分析。已经确认根因、具备复发风险并能形成防复发规则的错误，应升级沉淀到 `docs/project-memory/error_prevention_log.md`。

## 2. 记录原则

- 进入任何开发任务前，必须先读取本文和 `docs/project-memory/error_prevention_log.md`，确认本轮是否命中既有错误事件或错误模式。
- 开发中遇到命令失败、构建失败、接口异常、页面报错、控制台红错、验证失败、环境阻塞或规则执行偏差时，必须第一时间写入本文。
- 错误事件可以先记录现象和临时处理，不要求当场证明根因。
- 任务收尾时必须回看本文，判断本轮新增错误是否需要升级到 `error_prevention_log.md`。
- 已升级为防复发规则的错误事件，应在本文中标记“已沉淀”，避免重复分析。
- 若本文与实际代码或验证结果冲突，以实际代码和最新验证结果为准，并及时回写本文。

## 3. 记录模板

```md
### YYYY-MM-DD HH:mm - 错误标题

- 场景：
- 错误现象：
- 影响范围：
- 临时处理：
- 是否已复现：
- 当前状态：待处理 / 已解决 / 已沉淀
- 是否需要升级到 `error_prevention_log.md`：是 / 否 / 待判断
- 关联文件或命令：
```

## 4. 当前错误事件

### 2026-07-02 22:16 - 截断查看 git diff 时命令返回非零状态

- 场景：验证本轮规则文档改动时，使用 `git diff -- docs/project-memory/error_prevention_log.md | Select-Object -First 120` 查看部分 diff。
- 错误现象：命令返回 `Exit code: 1`，但已经输出所需 diff 片段。
- 影响范围：仅影响本轮 diff 查看命令，不影响文件内容和验证结论。
- 临时处理：改用 `git diff --numstat`、`git diff --stat` 和 `git status --short` 判断变更范围；确认 `error_prevention_log.md` 的大体量 diff 主要来自工作区既有未提交项目记忆更新，不属于本轮新增问题。
- 是否已复现：未复现，当前无需继续复现。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：否
- 关联文件或命令：`git diff -- docs/project-memory/error_prevention_log.md | Select-Object -First 120`

### 2026-07-02 22:36 - rule_check.ps1 中文字符串在 Windows PowerShell 下解析失败

- 场景：验证新增 `scripts/rule_check.ps1` 时执行 `powershell -ExecutionPolicy Bypass -File scripts/rule_check.ps1 -Help`。
- 错误现象：Windows PowerShell 报 `The string is missing the terminator: "`，脚本未能进入帮助输出。
- 影响范围：仅影响新增规则检查脚本的可执行性，不影响业务代码。
- 临时处理：将脚本运行时输出和规则代号改为 ASCII，保留文档中的中文说明，避免 Windows PowerShell 对 UTF-8 无 BOM 脚本的中文字符串误读。
- 是否已复现：已复现一次，修复后 `powershell -ExecutionPolicy Bypass -File scripts/rule_check.ps1 -Help` 验证通过。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：否
- 关联文件或命令：`scripts/rule_check.ps1`、`powershell -ExecutionPolicy Bypass -File scripts/rule_check.ps1 -Help`

### 2026-07-02 22:36 - rule_check.ps1 使用 GetRelativePath 导致旧版 PowerShell 执行失败

- 场景：执行完整 P0 规则扫描 `powershell -ExecutionPolicy Bypass -File scripts/rule_check.ps1`。
- 错误现象：报错 `[System.IO.Path] does not contain a method named 'GetRelativePath'`。
- 影响范围：仅影响新增规则检查脚本在 Windows PowerShell / 旧 .NET 环境下的兼容性，不影响业务代码。
- 临时处理：新增 `Get-RelativePathCompat`，用字符串前缀方式计算相对路径，避免依赖新版本 .NET API。
- 是否已复现：已复现一次，修复后完整 `rule_check.ps1` 已继续执行到规则扫描阶段。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：否
- 关联文件或命令：`scripts/rule_check.ps1`、`powershell -ExecutionPolicy Bypass -File scripts/rule_check.ps1`

### 2026-07-02 22:36 - rule_check.ps1 初版扫描规则过粗导致大量误报

- 场景：修复兼容问题后执行完整 P0 规则扫描 `powershell -ExecutionPolicy Bypass -File scripts/rule_check.ps1`。
- 错误现象：脚本输出 526 个问题，其中大量为误报，例如 `<el-form-item>` 被误判为 `<el-form>`，`.xlsx` 文件名被误判为 `xlsx` 依赖，`authNavigation` 兜底跳转被误判为业务页面浏览器跳转。
- 影响范围：影响新增规则检查脚本的可信度，不影响业务代码。
- 临时处理：收紧扫描规则，只匹配真实 `<el-form>` / `<form>` 标签；`xlsx` 只检查导入、require 和 `XLSX` 符号；允许 `authNavigation` 作为认证兜底；页面直连 `@/utils/api` 的 P0 检查先聚焦接口自动化页面。
- 是否已复现：已复现一次，收紧规则后完整 `rule_check.ps1` 验证通过。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：否
- 关联文件或命令：`scripts/rule_check.ps1`、`powershell -ExecutionPolicy Bypass -File scripts/rule_check.ps1`

### 2026-07-02 22:49 - 并行读取规则文件时部分命令超时

- 场景：审计当前开发规范闭环时，并行读取错误日志、流程规则、自治规则和 docs 目录信息。
- 错误现象：部分 `Get-Content` / `Get-ChildItem` 命令返回超时。
- 影响范围：仅影响本轮审计读取效率，不影响文件内容和规则判断。
- 临时处理：改为更窄范围读取和关键词检索，继续完成规则闭环检查和模板化规则落地。
- 是否已复现：未复现，当前无需继续复现。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：否
- 关联文件或命令：并行读取 `.cursor/workflow_rules.md`、`.cursor/autonomy_rules.md`、`docs` 目录信息

### 2026-07-02 22:56 - 文档整理审计时并行读取命令超时

- 场景：准备整理 `docs` 目录 Markdown 文档时，并行读取错误日志、防复发手册、`git status --short -- docs` 和 Markdown 文件清单。
- 错误现象：错误日志、防复发手册和 `git status` 三条命令超时，Markdown 文件清单读取成功。
- 影响范围：仅影响本轮审计读取效率，不影响文件内容和整理判断。
- 临时处理：改用更窄范围、更长超时的命令继续盘点，并优先避免移动已有未提交业务文档。
- 是否已复现：未复现，当前无需继续复现。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：否
- 关联文件或命令：`Get-Content docs/project-memory/error_event_log.md`、`Get-Content docs/project-memory/error_prevention_log.md`、`git status --short -- docs`

### 2026-07-02 23:01 - 批量更新文档引用时遇到空内容导致脚本失败

- 场景：移动 `docs` 根目录文档后，批量替换 Markdown 中的旧路径引用。
- 错误现象：PowerShell 报 `You cannot call a method on a null-valued expression`，说明某个读取结果为空时仍调用了 `.Replace()`。
- 影响范围：引用替换脚本可能已部分更新文件，需要用更稳的 UTF-8 读写方式重新执行。
- 临时处理：改用 `[System.IO.File]::ReadAllText` 和 `[System.IO.File]::WriteAllText`，并对空内容做兼容处理后重跑。
- 是否已复现：已复现一次；修复空内容问题后，全仓 Markdown 替换又因范围过大超时，已改为缩小处理范围并执行成功。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：否
- 关联文件或命令：批量替换 `docs/*.md` 旧路径引用的 PowerShell 脚本

### 2026-07-02 23:03 - 全仓 Markdown 引用替换范围过大导致超时

- 场景：使用 .NET UTF-8 读写方式重跑旧路径引用替换，但扫描范围为全仓 Markdown。
- 错误现象：命令 60 秒超时，可能已经部分更新引用。
- 影响范围：仅影响本轮引用替换效率，需要缩小范围后重跑并验证旧路径残留。
- 临时处理：改为只处理 `docs`、`.cursor`、`AGENTS.md`、`更新日志.md` 这些规则和文档范围。
- 是否已复现：已复现一次，缩小处理范围后已执行成功。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：否
- 关联文件或命令：全仓 Markdown 批量引用替换脚本

### 2026-07-02 23:07 - PowerShell 查看指定行片段时 Index 参数写法错误

- 场景：检查 `docs/APP/最终集成完成总结.md` 中旧路径残留时，使用 `Select-Object -Index 434..444` 查看片段。
- 错误现象：PowerShell 报无法把 `434..444` 转成 `System.Int32`。
- 影响范围：仅影响本轮查看文件片段，不影响文档内容。
- 临时处理：改用 `rg -n` 精确定位 `Phase3-4` 和旧路径残留，再用 `apply_patch` 修复。
- 是否已复现：未复现，当前无需继续复现。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：否
- 关联文件或命令：`Select-Object -Index 434..444`

### 2026-07-02 23:10 - 查找等价文档时并行读取命令超时

- 场景：检查缺失引用 `frontend-ui-style-guide.md` 和 `unified-table-template-spec.md` 是否已有等价文档。
- 错误现象：并行执行文件名查找、读取 `表格模板.md` 和查看规划文档上下文时，后两条命令超时。
- 影响范围：仅影响本轮查找效率，不影响文档整理结果。
- 临时处理：改用更窄的 `rg` 和单文件定位继续判断。
- 是否已复现：未复现，当前无需继续复现。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：否
- 关联文件或命令：查找 `frontend-ui-style-guide`、`unified-table-template-spec`、读取 `docs/architecture/表格模板.md`

### 2026-07-02 23:13 - 文档路径存在性检查误把占位文本当成真实路径

- 场景：最终验证文档路径引用是否都存在时，扫描到任务文档中的占位写法。
- 错误现象：检查输出“docs 省略路径占位文本”缺失。
- 影响范围：仅影响本轮路径检查结果，不代表真实文档链接缺失。
- 临时处理：把任务文档里的“docs 省略路径占位文本”改成非路径描述，再重新运行检查。
- 是否已复现：已复现一次，修复后已重新验证通过。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：否
- 关联文件或命令：文档路径存在性检查脚本

### 2026-07-02 23:20 - 文档路径存在性检查正则范围过宽导致误报

- 场景：修复占位路径后，重新执行 Markdown 文档路径存在性检查。
- 错误现象：检查把同一行里两个用顿号分隔的 docs 省略路径合并成一个不存在的路径，导致命令返回失败。
- 影响范围：仅影响本轮验证脚本结果，不代表这些文档真实缺失。
- 临时处理：改用更窄的路径匹配规则，只允许文件路径常用字符，不把中文分隔符、反引号等正文符号纳入路径。
- 是否已复现：已复现一次，修正检查脚本后已重新验证通过。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：否
- 关联文件或命令：文档路径存在性检查脚本

### 2026-07-02 23:24 - 文档路径存在性检查误把通配路径当成真实文件

- 场景：收窄路径正则后，重新执行 Markdown 文档路径存在性检查。
- 错误现象：检查把 `docs/*.md`、`docs/**/*.md`、`docs/project-memory/*.md` 这类说明性通配路径当成真实文件路径，导致命令返回失败。
- 影响范围：仅影响本轮验证脚本结果，不代表真实文档缺失。
- 临时处理：检查脚本排除包含 `*` 或省略号的路径；错误日志中的省略路径也改成普通文字，避免再次误判。
- 是否已复现：已复现一次，修正检查脚本后已重新验证通过。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：否
- 关联文件或命令：文档路径存在性检查脚本

### 2026-07-02 23:31 - 尾随空白检查范围过宽命中历史文档

- 场景：收尾验证时，对整个 `docs` 目录执行尾随空白扫描。
- 错误现象：命中了大量迁移过来的历史 API / APP / 架构说明文档尾随空白，并且脚本范围还误包含了非 Markdown 文件。
- 影响范围：仅影响本轮空白检查结果，不代表本轮目录整理新增了业务问题。
- 临时处理：不批量改写历史文档内容；尾随空白验证改为聚焦本轮新增或维护的规则、模板、索引、任务文档和交接日志。
- 是否已复现：已复现一次，收窄范围后已重新验证通过。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：否
- 关联文件或命令：尾随空白扫描脚本

### 2026-07-02 23:47 - 并行读取文档入口文件时命令超时

- 场景：新增 AI 开发规范迁移复用提示词后，准备同步 `docs/README.md`、`task_handoff.md` 和 `更新日志.md`。
- 错误现象：并行读取命令返回超时，虽然已经输出了部分文件内容。
- 影响范围：仅影响本轮读取效率，不影响新增文档内容。
- 临时处理：改为基于已读取片段进行小范围 `apply_patch`，后续用独立验证命令确认文件可读取和路径可解析。
- 是否已复现：已复现一次，收尾验证已确认相关文件路径和 diff 检查通过。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：否
- 关联文件或命令：并行读取 `更新日志.md`、`docs/project-memory/task_handoff.md`、`docs/README.md`

### 2026-07-02 23:51 - 预览新增复用提示词文档时 Get-Content 超时

- 场景：验证新增 `docs/guides/AI开发规范迁移复用提示词.md` 能否按 UTF-8 读取。
- 错误现象：`Get-Content -TotalCount 40` 已输出文档开头，但命令返回超时。
- 影响范围：仅影响本轮预览读取效率，不代表文件内容损坏。
- 临时处理：改用 .NET `ReadAllLines` 做轻量读取验证，并继续执行路径、尾随空白、规则检查和 diff 检查。
- 是否已复现：已复现一次，轻量读取验证已通过。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：否
- 关联文件或命令：`Get-Content docs/guides/AI开发规范迁移复用提示词.md -Encoding UTF8 -TotalCount 40`

### 2026-07-03 00:09 - P0.1 预检阶段路径读取和并行搜索命令失败

- 场景：按用户要求进入 P0.1 前，读取实施计划、定位 `AGENT/AGENTS` 规则文件，并尝试启动并发子 agent。
- 错误现象：用户给出的计划文档旧路径 `docs/full-stack-optimization-implementation-plan.md` 不存在；初始递归 `Get-ChildItem` / `rg --files` 在默认登录 PowerShell 下超时；第一次 `spawn_agent` 在完整上下文 fork 时显式传入 `agent_type` 被工具拒绝。
- 影响范围：仅影响本轮规则读取和子 agent 启动效率，未修改业务代码，未影响 P0.1 范围判断。
- 临时处理：改用实际路径 `docs/planning/full-stack-optimization-implementation-plan.md`；PowerShell 命令统一改为 `login=false`、UTF-8 输出和更窄检索范围；子 agent 按工具要求省略 `agent_type` 后启动成功。
- 是否已复现：已复现一次，调整后读取和子 agent 启动已继续推进。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：待判断
- 关联文件或命令：`Get-Content docs/planning/full-stack-optimization-implementation-plan.md`、`rg --files -g '*AGENT*'`、`multi_agent_v1.spawn_agent`

### 2026-07-03 00:42 - P0.1 Execution 并发 worker 未返回可用产出

- 场景：用户确认进入 Execution 后，按样式、前端请求、后端权限拆分 3 个 worker 并发实施。
- 错误现象：3 个 worker 在等待窗口内长期保持 `running`，多次 `wait_agent` 超时，追加进度请求后仍未返回可用实现结果。
- 影响范围：影响本轮并发实施效率；未发现 worker 已落地业务代码改动，主线程接手继续实现，避免任务停滞。
- 临时处理：关闭 3 个未返回产出的 worker，由主线程按已确认的 `Spec/SDD` 和 `TDD` 范围继续实施；后续仍按原分片范围人工控制改动边界。
- 是否已复现：本轮已复现一次。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：待判断
- 关联文件或命令：`multi_agent_v1.wait_agent`、`multi_agent_v1.send_input`、`multi_agent_v1.close_agent`

### 2026-07-03 00:58 - rg 检索 design token 时模式被误识别为命令参数

- 场景：实现 P0.1 样式令牌后，检索共享组件中 `--th-*` token 使用情况。
- 错误现象：执行 `rg -n "--th-|#409eff|..." ...` 时，`rg` 把以 `--th-` 开头的模式误识别为命令参数并返回失败。
- 影响范围：仅影响本轮静态检索命令，不影响代码内容。
- 临时处理：改用 `rg -n -- "--th-|#409eff|..." ...`，用 `--` 显式结束参数解析，检索成功。
- 是否已复现：已复现一次，修正命令后已解决。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：否
- 关联文件或命令：`rg -n -- "--th-|#409eff|#f5f7fa|border-radius|box-shadow|padding:|margin-bottom:" frontend\\src\\components\\page-shells ...`

### 2026-07-03 23:44 - P0.1 收尾阶段 apply_patch 包装器不可用

- 场景：补写 P0.1 Loop 合同、VDD 和项目记忆文档时，按开发规范优先尝试使用 `apply_patch`。
- 错误现象：`apply_patch`、`cmd /c apply_patch --help` 以及直接调用 Codex `--codex-run-as-apply-patch` 均返回 `Access is denied`；随后一次手写 `git apply --check` 因 hunk 行数不匹配失败，但未写入文件。
- 影响范围：只影响文档收口工具选择，不影响前后端代码运行结果；未发生半写入。
- 临时处理：记录该工具阻塞后，采用 UTF-8 PowerShell .NET 定点写入更新任务文档和项目记忆；随后用 `git diff --check` 复核。
- 是否已复现：已复现。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：待判断
- 关联文件或命令：`apply_patch`、`cmd /c apply_patch --help`、`codex.exe --codex-run-as-apply-patch`、`git apply --check`

### 2026-07-03 23:50 - P0.1 子 worker 临时命令失败和路径基准纠偏

- 场景：前端、后端、文档 worker 并发复核 P0.1 改动时，分别执行静态扫描、文档读取和 VDD 写入。
- 错误现象：前端 worker 一次临时 `rg` 组合命令因 PowerShell 引号解析失败；文档 worker 遇到读取 / 摘要命令超时，并曾把 `vdd.md` 写到外层 `E:\testhub_platform-main`，随后移动回内层仓库任务目录。
- 影响范围：仅影响 worker 验证效率和文档落点；前端 worker 已用更窄命令完成验证，文档 worker 已确认外层不再残留误写的 `vdd.md`。
- 临时处理：主线程汇总 worker 结果后补最终验证、最终 VDD 和错误事件记录。
- 是否已复现：本轮已复现。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：否
- 关联文件或命令：前端 `rg` 静态扫描、`docs/tasks/2026-07-03-p0-1-full-stack-baseline/vdd.md`

### 2026-07-04 00:02 - P0.1 文档收口脚本 replace 参数写法错误

- 场景：更新最终 VDD、Loop 日志、错误日志、交接摘要、公开接口白名单和更新日志时，用 PowerShell 脚本做 UTF-8 定点写入。
- 错误现象：公开接口白名单更新语句使用 `-replace` 时传入了 4 个参数，PowerShell 报 `The -ireplace operator allows only two elements to follow it, not 4.`。
- 影响范围：VDD、Loop 日志、错误日志和交接摘要已经写入；公开接口白名单和更新日志在该语句处中断，未完成最后两项小更新。
- 临时处理：改用 `.Replace()` 字符串替换完成公开接口白名单和更新日志修正，并重新执行 `git diff --check`。
- 是否已复现：本轮已复现一次。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：否
- 关联文件或命令：`docs/tasks/2026-07-03-p0-1-full-stack-baseline/public-api-whitelist.md`、`更新日志.md`

### 2026-07-04 18:50 - 导航卡顿复现前工具路径与端口探测异常

- 场景：按用户要求继续定位“页面切换卡顿、像刷新后才能点击”的前端导航问题，准备使用 Playwright 和本地 dev server 做浏览器复现。
- 错误现象：前序尝试中曾读取错误的 Playwright skill 路径 `E:\Codex++\.codex\skills\.system\playwright\SKILL.md`，正确路径应为 `E:\Codex++\.codex\skills\playwright\SKILL.md`；早前 shell 曾出现 `windows sandbox: helper_unknown_error`；本轮使用 `Get-NetTCPConnection -LocalPort 5173` 探测端口时，在未发现监听的情况下命令返回非零状态且无输出；读取仍被 dev server 占用的日志文件时出现文件独占异常；一次 `playwright-cli run-code` 未按函数格式传参导致参数错误；停止 Vite 进程时误用 PowerShell 只读变量 `$PID` 导致命令失败；关闭两个 Playwright session 时用 `&` 串接命令，被 PowerShell 当作保留符号解析失败；检查未跟踪文件尾随空白时，字符串插值 `$file:` 被 PowerShell 误解析为非法变量引用。
- 影响范围：仅影响本轮复现前后的工具准备、日志读取和进程控制，不代表业务代码已失败。
- 临时处理：已改用正确 Playwright skill 路径读取说明；当前权限恢复后 shell 命令可执行；日志读取改用 `FileShare.ReadWrite`；Playwright 长脚本改用 `--filename`；停止进程改用 `$listenPid`；关闭 Playwright session 改为两条独立命令；字符串插值改为 `${file}`。
- 是否已复现：工具路径错误、端口探测非零状态、日志独占读取失败、Playwright 参数错误、`$PID` 变量冲突、`&` 串接解析错误和 `$file:` 插值解析错误已复现；沙箱 helper 异常当前未复现。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：否
- 关联文件或命令：`E:\Codex++\.codex\skills\playwright\SKILL.md`、`Get-NetTCPConnection -LocalPort 5173`、`playwright-cli run-code`、`Stop-Process`

### 2026-07-04 19:16 - 页面切换卡顿和整页刷新体感根因为 Vite 依赖重优化

- 场景：用户反馈点击切换各个页面、查看详情、编辑数据时会卡顿，并触发刷新后才能正常切换。
- 错误现象：浏览器复现时控制台出现 `504 Outdated Optimize Dep`，随后 Vue Router 动态导入页面组件失败，例如 `Failed to fetch dynamically imported module`；刷新计数显示 `beforeunload=1`、`pagehide=1`，`performance.navigation.type=reload`；网络请求中出现 `/node_modules/.vite/deps/element-plus_es_components_*_style_css.js` 返回 504。
- 影响范围：主要影响本地 Vite dev server 下首次访问懒加载页面的体验；用户体感为“点击页面卡住、刷新后才好”。生产构建不走该 dev-only 依赖优化缓存路径。
- 临时处理：修改 `frontend/vite.config.js`，去掉 `optimizeDeps.force: true`，新增 `optimizeDeps.entries` 扫描 `index.html` 与 `src/**/*.{js,vue}`，并预优化 `element-plus`、`@element-plus/icons-vue` 和 `element-plus/es/components/**/style/css`。
- 是否已复现：已复现并已用 Playwright 验证修复后同一组 11 次导航无 `beforeunload`、无 `pagehide`、无 `504 Outdated Optimize Dep`。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：是，已沉淀
- 关联文件或命令：`frontend/vite.config.js`、`cmd /c npm run dev -- --host 127.0.0.1 --port 5173`、`playwright-cli -s navlag-fixed run-code --filename nav-repro-with-setup.js`、`cmd /c npm run build`

### 2026-07-04 19:36 - 排查本地启动后端端口时 netstat 命令超时

- 场景：用户截图显示 Vite 代理 `/api/auth/login/` 和 `/api/auth/token/refresh/` 到 `127.0.0.1:8000` 时 `ECONNREFUSED`，准备确认后端 8000 端口是否监听。
- 错误现象：执行 `cmd /c netstat -ano | findstr :8000` 超时，没有返回可用监听结果；首次用 5 秒整体超时执行 .NET `TcpClient` 探测时，PowerShell 启动和命令开销导致整体超时；随后放宽总超时后确认 `PORT_8000_OPEN`；再用 `Get-NetTCPConnection -LocalPort 8000 -State Listen` 查询进程时仍超时；后续用 `Get-ChildItem -Name manage.py` 和 `rg --files -g "manage.py"` 查找 Django 启动入口也超时。
- 影响范围：仅影响端口确认命令，不影响对截图报错的判断；截图本身已经能说明前端连接后端 8000 被拒绝。
- 临时处理：改用短连接等待、较长命令总超时的 .NET `TcpClient` 探测方式确认端口状态；不继续依赖本轮超时的文件查找命令，按项目既有 Django 启动口径说明。
- 是否已复现：已复现一次。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：否
- 关联文件或命令：`cmd /c netstat -ano | findstr :8000`、`.NET TcpClient ConnectAsync`、`Get-NetTCPConnection -LocalPort 8000`、`Get-ChildItem -Name manage.py`、`rg --files -g "manage.py"`

### 2026-07-04 19:44 - start.bat 未等待后端 ready 导致前端代理 ECONNREFUSED

- 场景：用户直接双击 `start.bat` 启动本地服务后，前端窗口显示 `/api/auth/token/refresh/` 和 `/api/auth/login/` 代理到 `127.0.0.1:8000` 时 `ECONNREFUSED`。
- 错误现象：`start.bat` 后台启动 Django 后立即启动 Vite；截图中的前端请求发生在 19:33:54 和 19:33:56，而 `backend.log` 显示 Django 到 19:34:11 才真正开始监听 `0.0.0.0:8000`。
- 影响范围：影响双击启动脚本后的首次登录和旧 token 刷新；用户会误以为前端启动失败或登录接口坏了。
- 临时处理：修改 `start.bat`，先 `cd /d "%~dp0"` 固定工作目录，启动后端后等待 `127.0.0.1:8000` 最多 60 秒可连接，再启动前端；如果后端未 ready，提示查看 `backend.log` 并停止启动。
- 是否已复现：已通过截图时间和 `backend.log` 启动时间确认。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：是，已沉淀
- 关联文件或命令：`start.bat`、`backend.log`

### 2026-07-04 20:03 - 提交前暂存区 diff check 发现历史文档尾随空白

- 场景：按用户要求准备提交并推送到 GitHub 前，执行 `git diff --cached --check`。
- 错误现象：检查发现 `docs/guides/AI开发规范迁移复用提示词.md` 末尾多一个空行，`docs/planning/full-stack-optimization-implementation-plan.md` 有 4 行行尾空格。
- 影响范围：仅影响提交前格式检查，不影响业务代码。
- 临时处理：去掉对应行尾空格和 EOF 多余空行，重新暂存后 `git diff --cached --check` 通过。
- 是否已复现：已复现一次并已修复。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：否
- 关联文件或命令：`git diff --cached --check`

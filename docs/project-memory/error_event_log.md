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

### 2026-07-04 20:19 - P0.1 完成度核对时扫描命令引号和读取超时

- 场景：核对 `full-stack-optimization-implementation-plan.md` 中各部分 P0.1 是否都已完成。
- 错误现象：一次组合 `rg` 命令因为 PowerShell 引号解析失败，提示 `The string is missing the terminator: "`；随后用 `Get-Content` 读取公开接口白名单文档时超时。
- 影响范围：仅影响本轮核对效率，不影响代码和文档内容。
- 临时处理：拆分成两条简单 `rg` 命令；公开接口白名单改用 .NET `ReadAllText` 读取。
- 是否已复现：已复现一次并已绕过。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：否
- 关联文件或命令：`rg -n`、`Get-Content docs/tasks/2026-07-03-p0-1-full-stack-baseline/public-api-whitelist.md`

### 2026-07-04 20:21 - P0.1 剩余闭环前读取自治规则命令超时

- 场景：进入 P0.1 剩余闭环 Execution 前，按规则读取 `.cursor/autonomy_rules.md`。
- 错误现象：执行 `Get-Content -Raw -Encoding UTF8 .cursor\autonomy_rules.md` 时 10 秒超时。
- 影响范围：仅影响规则读取效率，不影响业务代码和任务文档内容。
- 临时处理：已记录错误事件，后续改用更长超时继续读取同一规则文件。
- 是否已复现：已复现一次。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：待收尾判断
- 关联文件或命令：`Get-Content -Raw -Encoding UTF8 .cursor\autonomy_rules.md`

### 2026-07-04 20:33 - P0.1 前端请求入口扫描命令引号解析失败

- 场景：扫描前端裸 `axios`、`EventSource`、`WebSocket` 和 `fetch` 入口，确认前端代码 P0.1 请求入口收口是否仍成立。
- 错误现象：一条复杂 `rg` 正则在 PowerShell 中被错误解析为管道和未闭合字符串，报 `An empty pipe element is not allowed` 与 `The string is missing the terminator`。
- 影响范围：仅影响扫描命令执行效率，不影响源码。
- 临时处理：改为拆分多条简单 `rg` 命令分别扫描关键字，避免 PowerShell 解析复杂正则。
- 是否已复现：已复现一次。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：待收尾判断
- 关联文件或命令：`rg -n "axios\.|from ['\"]axios|import axios|EventSource\(|new WebSocket|fetch\(" frontend\src -g "*.js" -g "*.vue"`

### 2026-07-04 20:45 - 中断续跑后读取错误日志尾部触发 sandbox helper 异常

- 场景：用户多次要求继续后，准备读取 `docs/project-memory/error_event_log.md` 尾部确认前序错误状态。
- 错误现象：执行 `Get-Content -Tail 45 -Encoding UTF8 docs\project-memory\error_event_log.md` 时返回 `windows sandbox: helper_unknown_error: setup refresh had errors`。
- 影响范围：仅影响本轮日志尾部读取，不影响业务代码和文档内容。
- 临时处理：已用 `apply_patch` 直接记录错误事件；再次复现后不再用 `Get-Content -Tail` 读取该文件尾部，改用目标文件扫描和最终 diff 验证。
- 是否已复现：本轮复现两次。
- 当前状态：已解决
- 是否需要升级到 `error_prevention_log.md`：待收尾判断
- 关联文件或命令：`Get-Content -Tail 45 -Encoding UTF8 docs\project-memory\error_event_log.md`

### 2026-07-08 23:06 - P0.1 旧模拟代码残留扫描无命中返回非零状态

- 场景：继续 P0.1 剩余闭环时，执行静态扫描确认旧模拟代码、临时 token 和页面名称保存 TODO 是否仍残留。
- 错误现象：`rg` 没有命中目标字符串并返回 `Exit code: 1`；这代表“未发现残留”，不是源码错误。
- 影响范围：仅影响命令退出码解读，不影响代码内容和验证结论。
- 临时处理：将该命令按“无命中即通过”的静态验证处理，并用正向扫描确认 `LOCATOR_VALIDATION_NOT_IMPLEMENTED`、页面名称未接入保存提示和 App 报告直连 403 文案存在。
- 是否已复现：已复现一次。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否。
- 关联文件或命令：`rg -n "模拟开始时间|模拟结束时间|_perform_element_validation|_generate_step_log|_generate_failure_screenshot|temp_token_|TODO: 实现页面名称保存" apps frontend\src -g "*.py" -g "*.js" -g "*.vue"`

### 2026-07-08 23:13 - 系统 Python 缺少 Django 导致请求级验证失败

- 场景：P0.1 剩余闭环验证用户注册、profile 和 logout 的认证行为时，使用当前默认 `python` 执行 DRF 测试客户端脚本。
- 错误现象：脚本在 `django.setup()` 前失败，提示 `ModuleNotFoundError: No module named 'django'`。
- 影响范围：仅影响默认 Python 环境下的请求级验证；不影响前端构建、后端 `py_compile` 和静态扫描结果。
- 临时处理：先记录环境阻塞，再查找仓库内是否存在可用虚拟环境；已改用仓库 `venv\Scripts\python.exe` 重跑请求级验证并通过。
- 是否已复现：已复现一次。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否。
- 关联文件或命令：`python -` 内联 DRF `APIClient` 验证脚本。

### 2026-07-08 23:19 - test-register 返回 JsonResponse 导致验证脚本取值失败

- 场景：改用仓库 `venv` 后，继续用 DRF `APIClient` 验证 `/api/auth/test-register/` 的注册返回结构。
- 错误现象：接口已返回 `REGISTER_STATUS 200`，但脚本随后访问 `register_response.data` 报 `AttributeError: 'JsonResponse' object has no attribute 'data'`。
- 影响范围：仅影响验证脚本取值方式；该接口本身是 Django `JsonResponse`，需要从 `response.content` 解析 JSON。
- 临时处理：先记录错误事件，再用修正脚本通过 `json.loads(response.content)` 取值，并在脚本开始和结束都清理 `P0_SAMPLE_auth_contract_0708` 样本用户；修正脚本已验证通过。
- 是否已复现：已复现一次。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否。
- 关联文件或命令：`venv\Scripts\python.exe -` 内联 DRF `APIClient` 验证脚本。

### 2026-07-09 00:15 - AI 结果处理 Spec 补充阶段多条读取命令超时

- 场景：补充“AI 需求分析生成用例后保存失败 / 结果处理页无法采纳弃用”Spec 前，按规则读取任务模板、项目记忆和相关文件片段。
- 错误现象：部分 `Get-ChildItem` / `Get-Content` / 多文件片段读取命令达到 10 到 20 秒超时；已有命令输出了部分内容，但返回超时状态。
- 影响范围：仅影响规则和代码读取效率，不影响本轮新增 Spec 文档内容；后续已改用更窄范围的 `rg` 与 .NET UTF-8 读取方式继续核对。
- 临时处理：缩小读取范围，按具体文件和具体行段读取；新建 `docs/tasks/2026-07-09-ai-generated-result-processing-fix/spec-sdd.md` 记录本轮 Spec。
- 是否已复现：本轮已复现。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否。
- 关联文件或命令：读取 `.cursor`、`docs/task-templates`、`docs/tasks`、`frontend/src/views/requirement-analysis/*.vue`、`apps/requirement_analysis/views.py` 的多条 PowerShell 命令。

### 2026-07-09 00:15 - apply_patch 基准目录不在真实项目内导致 Spec 误落外层

- 场景：新增 AI 结果处理 Spec 时，先用 shell 在真实项目目录创建了任务目录，再用 `apply_patch` 添加 `docs/tasks/2026-07-09-ai-generated-result-processing-fix/spec-sdd.md`。
- 错误现象：`apply_patch` 以外层 `E:\testhub_platform-main` 为基准，导致新文件落到 `E:\testhub_platform-main\docs\...`，真实项目 `E:\testhub_platform-main\testhub_platform-main\docs\...` 初始为空。
- 影响范围：只影响本轮文档落点；未修改原生参考目录，未修改业务代码。
- 临时处理：核对外层和内层路径后，将误落外层的 Spec 文件移动到真实项目任务目录，并删除外层误建的空目录。
- 是否已复现：本轮已复现。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否。
- 关联文件或命令：`apply_patch`、`Move-Item E:\testhub_platform-main\docs\tasks\2026-07-09-ai-generated-result-processing-fix\spec-sdd.md`。

### 2026-07-09 00:55 - AI 结果处理 Execution 收尾阶段验证命令误用和扫描超时

- 场景：完成 AI 生成结果处理前端改动后，按规则补做静态扫描、语法检查和文档收尾验证。
- 错误现象：早前尝试用 `node --check` 直接检查 `.vue` 单文件组件，Node 返回不支持 `.vue` 扩展；一次 `rg` lookahead 正则在未使用 `--pcre2` 或 PowerShell 引号不稳时执行失败；一次针对后端大文件的 `rg | Select-String` 组合扫描在 30 秒内超时；部分全仓 `AGENTS.md` 搜索和递归目录读取也出现超时。
- 影响范围：只影响本轮验证效率和命令选择，不影响业务代码；前端实际验证已改用 `npm run build`、`rule_check.ps1`、窄范围 `rg --pcre2`、`git diff --check` 和限定文件扫描完成。
- 临时处理：不再用 `node --check` 直接检查 `.vue`；复杂 lookahead 统一显式加 `--pcre2`；大文件扫描改成限定文件和限定关键字；最终已完成规则检查、构建、diff 格式检查和红线扫描。
- 是否已复现：本轮已复现。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否。
- 关联文件或命令：`node --check *.vue`、`rg --pcre2 -n "<button(?![^>]*type=)" ...`、`rg -n "project_id|case_indices|case_index|test_cases" apps\requirement_analysis\views.py | Select-String ...`。

### 2026-07-09 01:00 - 原生参考目录不是 Git 仓库导致状态核对命令失败

- 场景：收尾时为了再次确认原生参考目录没有被修改，尝试对 `E:\原生testhub_platform-main\testhub_platform-main` 执行 `git status --short`。
- 错误现象：命令返回 `fatal: not a git repository (or any of the parent directories): .git`，说明该参考目录当前不是 Git 工作树，不能用 `git status` 做改动证明。
- 影响范围：只影响原生参考目录状态核对方式；本轮对原生目录只执行读取和搜索，没有执行写入、移动或删除命令。
- 临时处理：改为在交付说明中明确“原生目录只作为只读参考”，不再用 Git 状态作为证明。
- 是否已复现：已复现一次。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否。
- 关联文件或命令：`git -C E:\原生testhub_platform-main\testhub_platform-main status --short`。

### 2026-07-09 23:07 - apply_patch 再次以外层目录为基准导致计划文档补丁未命中

- 场景：按用户要求把原生代码对比后的迁移优先级补入 `docs/planning/full-stack-optimization-implementation-plan.md`。
- 错误现象：`apply_patch` 以外层 `E:\testhub_platform-main` 为基准读取 `docs/planning/full-stack-optimization-implementation-plan.md`，实际项目文件在 `E:\testhub_platform-main\testhub_platform-main\docs\planning\...`，补丁返回“系统找不到指定的路径”，未修改任何文件。
- 影响范围：仅影响本轮文档 patch 的第一次尝试；计划文档和源码均未被改动。
- 临时处理：记录错误事件后，后续 `apply_patch` 统一使用带项目目录前缀的 `testhub_platform-main/docs/...` 路径。
- 是否已复现：已复现。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否，已由本轮路径前缀处理规避，且此前已有同类基准目录事件记录。
- 关联文件或命令：`apply_patch` 更新 `docs/planning/full-stack-optimization-implementation-plan.md`。

### 2026-07-09 23:14 - 截断查看计划文档 diff 时管道返回非零状态

- 场景：补入原生对比优先级后，使用 `git diff -- ... | Select-Object -First 260` 查看部分 diff。
- 错误现象：命令已经输出目标 diff 片段，但返回 `Exit code: 1`；同时出现 Git 的 LF/CRLF 行尾提示。
- 影响范围：仅影响 diff 截断查看命令，不影响文件内容；随后 `git diff --check` 返回 0，未发现空白错误。
- 临时处理：改用定向 `rg` 和 `git diff --check` 验证文档关键内容与格式。
- 是否已复现：已复现。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否，已有类似截断 diff 非零状态记录。
- 关联文件或命令：`git diff -- docs/planning/full-stack-optimization-implementation-plan.md docs/project-memory/error_event_log.md | Select-Object -First 260`。

### 2026-07-09 23:20 - 读取计划文档长片段时命令超时

- 场景：按用户要求调整计划文档中未确认冲突点的表达方式时，读取 `docs/planning/full-stack-optimization-implementation-plan.md` 的长行段用于核对上下文。
- 错误现象：命令输出了目标片段的一部分，但在 30 秒左右超时。
- 影响范围：仅影响文档片段查看效率，不影响文件内容；后续已改用 `rg` 精确检索和 `apply_patch` 定点删除。
- 临时处理：用关键词检索定位 `冲突与待确认`、`待确认`、`不迁移` 等残留，再逐段 patch。
- 是否已复现：已复现。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否，属于本仓库已知的大文件读取效率问题。
- 关联文件或命令：读取 `docs/planning/full-stack-optimization-implementation-plan.md` 第 146-350 行附近内容的 PowerShell 命令。

### 2026-07-09 23:34 - 外层目录规则读取命令超时

- 场景：用户确认原生对比后的 5 个实施口径后，准备按规范重新读取 `AGENTS.md`、`.cursor` 目录和计划文档。
- 错误现象：在外层 `E:\testhub_platform-main` 直接执行 `Get-ChildItem`、`Get-Content AGENTS.md`、`cmd /c cd` 等命令均出现 10 到 20 秒超时；切到内层真实项目根 `E:\testhub_platform-main\testhub_platform-main` 后读取成功。
- 影响范围：仅影响本轮规则读取效率，不影响业务代码和计划文档内容；原生参考目录未被修改。
- 临时处理：改用内层项目根、`login=false`、UTF-8 定向读取和具体文件片段读取继续推进。
- 是否已复现：本轮已复现。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否，已有类似大目录 / 长文档读取超时记录，本轮通过收窄路径规避。
- 关联文件或命令：`Get-ChildItem -Force`、`Get-Content -Raw AGENTS.md`、`cmd /c cd`、`Get-Content -Raw -Encoding UTF8 .cursor\*.md`。

### 2026-07-09 23:51 - 多次枚举 ReadLines 迭代器导致计划文档片段读取失败

- 场景：核对 `full-stack-optimization-implementation-plan.md` 各部分 P0.1 是否已收尾时，用 PowerShell 对 `[System.IO.File]::ReadLines()` 返回的迭代器循环执行多次 `Select-Object -Skip`。
- 错误现象：第一段输出后，后续枚举报 `Cannot read from a closed TextReader`，导致部分计划文档片段没有读取出来。
- 影响范围：仅影响本轮文档片段读取效率，不影响源码和计划文档内容。
- 临时处理：改为一次性读入数组或使用 `rg` 精确检索继续核对。
- 是否已复现：本轮已复现。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否，属于本轮脚本写法问题，已用更稳读取方式规避。
- 关联文件或命令：`[System.IO.File]::ReadLines(... ) | Select-Object -Skip ...`。

### 2026-07-09 23:59 - PowerShell 中误用 Bash heredoc 检查 Python 包

- 场景：为生成 `.xls` 回归测试用例文件，检查本机是否安装 `xlwt/openpyxl/pandas/xlsxwriter`。
- 错误现象：在 PowerShell 中执行 `python - <<'PY'`，被 PowerShell 当成重定向解析，返回 `Missing file specification after redirection operator`。
- 影响范围：仅影响本轮依赖探测命令，不影响项目文件和测试用例内容。
- 临时处理：改用 Node 包检查和 Excel COM 探测；确认本机存在 `Excel.Application` COM，可用 Excel 保存为 `.xls`。
- 是否已复现：本轮已复现。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否，属于 shell 语法误用，已绕过。
- 关联文件或命令：`python - <<'PY'`、`[type]::GetTypeFromProgID('Excel.Application')`。

### 2026-07-10 00:02 - Excel COM 探测可见但创建对象失败

- 场景：为输出 `.xls` 回归测试用例，尝试通过 `New-Object -ComObject Excel.Application` 创建 Excel 工作簿并保存为 Excel 97-2003 格式。
- 错误现象：COM 创建失败，返回 `80040154 Class not registered`，说明当前环境没有可用的 Excel COM 注册。
- 影响范围：仅影响 `.xls` 生成方式，不影响测试用例内容和业务代码。
- 临时处理：改为生成 Excel 2003 XML 工作簿并使用 `.xls` 扩展名，保持多工作表结构，避免依赖本机 Office 和新增项目依赖。
- 是否已复现：本轮已复现。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否，属于本机工具能力限制，已使用无依赖方案规避。
- 关联文件或命令：`New-Object -ComObject Excel.Application`。

### 2026-07-10 00:08 - PowerShell 管道传 Python 导致中文路径被替换成问号

- 场景：用 PowerShell here-string 管道传给 `python -` 生成 Excel 2003 XML `.xls` 文件。
- 错误现象：Python 写文件时报 `OSError: [Errno 22] Invalid argument`，路径中的中文文件名被替换为 `?`，变成非法 Windows 文件名。
- 影响范围：仅影响本轮 `.xls` 文件生成，未产生目标文件，不影响测试用例设计内容。
- 临时处理：改用 PowerShell 原生 .NET UTF-8 写文件，并将输出文件名改为 ASCII，避免跨进程管道编码污染。
- 是否已复现：本轮已复现。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否，属于工具编码链路问题，已更换生成方式。
- 关联文件或命令：`@'...'@ | python -`、`Path.write_text(..., encoding='utf-8-sig')`。

### 2026-07-10 00:20 - 读取 Playwright skill 时使用了过期路径

- 场景：进入 P0.2 Execution 后，准备按 TDD 先执行 P0.1 / 阶段 A 浏览器回归硬闸门，并读取 Playwright skill 说明。
- 错误现象：使用 `E:\Codex++\.codex\skills\.system\playwright\SKILL.md` 读取失败，提示路径不存在。
- 影响范围：仅影响本轮工具说明读取，不影响项目代码和回归计划。
- 临时处理：改用当前会话技能清单提供的真实路径 `E:\Codex++\.codex\skills\playwright\SKILL.md` 继续读取。
- 是否已复现：本轮已复现。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否，属于技能文件路径记忆错误，已按会话真源纠正。
- 关联文件或命令：`Get-Content -Raw -Encoding UTF8 E:\Codex++\.codex\skills\.system\playwright\SKILL.md`。

### 2026-07-10 00:31 - P0.2 续跑初始并行读取命令超时和中文输出乱码

- 场景：用户确认继续 P0.2 后，重新读取项目根目录、Git 状态、`AGENTS.md`、P0.2 TDD 和当前阶段记忆。
- 错误现象：首次并行命令使用 10 秒超时，`Get-Location`、`Get-ChildItem`、`git status`、`Get-Content` 均返回超时；随后未显式设置 UTF-8 输出时，中文规则文档在终端显示为乱码。
- 影响范围：仅影响本轮规则读取效率和显示层判断，不影响项目文件内容；未进入业务代码修改。
- 临时处理：改为更长超时，并在 PowerShell 中显式设置 `[Console]::OutputEncoding` 与 `Get-Content -Encoding UTF8` 后重新读取规则、错误日志和任务文档。
- 是否已复现：本轮已复现。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否，已有 UTF-8 防复发规则，本轮按规则纠偏。
- 关联文件或命令：`Get-Content -Raw AGENTS.md`、`Get-Content -Raw -Encoding UTF8 AGENTS.md`、并行读取项目状态命令。

### 2026-07-10 00:32 - P0.2 回归前端口检查使用 Test-NetConnection 超时

- 场景：准备执行 P0.1 / 阶段 A 回归门禁前，检查本地前后端服务端口是否可用。
- 错误现象：`Test-NetConnection 127.0.0.1 -Port 8000` 和 `Test-NetConnection 127.0.0.1 -Port 5173` 在 30 秒内超时，没有返回可用结果。
- 影响范围：仅影响服务可用性检查方式，不影响服务本身；未修改业务代码。
- 临时处理：改用 `curl.exe -I --max-time 5` 和 `netstat -ano` 检查。结果显示前端 `5173` 返回 200，后端 `8000` 可连接且根路径返回 404，端口均处于监听状态。
- 是否已复现：本轮已复现。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：待判断。
- 关联文件或命令：`Test-NetConnection 127.0.0.1 -Port 8000`、`Test-NetConnection 127.0.0.1 -Port 5173`、`curl.exe -I --max-time 5`。

### 2026-07-10 00:34 - P0.2 回归数据盘点脚本输出生成正文导致 GBK 编码失败

- 场景：执行只读 Django ORM 脚本，盘点用户、项目、AI 生成任务、接口自动化和 App 报告样本数据。
- 错误现象：脚本把 `generated_test_cases` / `final_test_cases` 生成正文原样输出，控制台经 `colorama` 写入时遇到 GBK 无法编码字符，报 `UnicodeEncodeError`。
- 影响范围：仅影响本轮数据盘点输出；脚本未执行写库动作，未修改业务数据或代码。
- 临时处理：改为只输出 ID、状态、归属、字段是否非空和长度摘要，不输出生成正文、密钥或敏感内容；后续命令显式设置 `PYTHONIOENCODING=utf-8`。
- 是否已复现：本轮已复现。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否，属于本轮脚本输出范围过宽，已收窄。
- 关联文件或命令：`venv\\Scripts\\python.exe manage.py shell` 内联 ORM 盘点脚本。

### 2026-07-10 00:38 - 提取回归 Excel XML 用例时 PowerShell 管道写法错误

- 场景：从 `p0-1-stage-a-regression-test-cases.xls` 中提取 `REG-P01-019` 到 `REG-P01-030` 的阶段 A P0 用例摘要。
- 错误现象：`foreach (...) { ... } | Format-Table` 直接拼接导致 PowerShell 报 `An empty pipe element is not allowed`。
- 影响范围：仅影响本轮用例摘要提取命令，不影响回归用例文件内容。
- 临时处理：改为使用脚本块 `& { foreach (...) { ... } } | Format-Table` 输出后再格式化。
- 是否已复现：本轮已复现。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否，属于临时脚本写法问题。
- 关联文件或命令：解析 `docs\\tasks\\2026-07-09-p0-1-stage-a-regression-testcases\\p0-1-stage-a-regression-test-cases.xls` 的 PowerShell XML 脚本。

### 2026-07-10 00:42 - 接口回归脚本 f-string 引号跨层传参损坏

- 场景：执行 P0.1 / 阶段 A 接口级回归脚本，准备输出 App 报告响应的 `Content-Type` 作为辅助信息。
- 错误现象：Python f-string 中的 `resp_a_report.get("Content-Type", "")` 在 PowerShell 传参后变成无效语法，脚本抛 `SyntaxError`，未进入业务断言。
- 影响范围：仅影响本轮接口回归脚本第一次执行；未修改业务代码，脚本未执行到数据变更断言。
- 临时处理：删除复杂 f-string 辅助输出，只保留状态码和明确断言后重跑。
- 是否已复现：本轮已复现。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否，属于临时脚本引号问题。
- 关联文件或命令：`venv\\Scripts\\python.exe -X utf8 manage.py shell -c $code`。

### 2026-07-10 00:45 - P0.1 / 阶段 A 接口测试用例列表固定字段回归失败

- 场景：执行 P0.1 / 阶段 A 回归门禁中 `REG-P01-019`，用用户 A 请求 `/api/api-testing/requests/`，检查接口测试用例资产列表固定字段。
- 错误现象：接口返回 200，但夹具行缺少 `assertions_count`；脚本最初检查的 `last_execution_status` 与代码实际字段 `latest_execution_status` 不一致，属于脚本字段名写偏。
- 影响范围：影响阶段 A 已冻结的接口测试用例列表字段完整性；按 P0.2 TDD 不能继续进入 P0.2 实现，必须先修复前置回归失败。
- 临时处理：暂停 P0.2 实现，按阶段 A / P0.1 回归缺陷在 `ApiRequestSerializer` 补只读字段 `assertions_count`，前端断言数显示优先消费该字段并保留旧响应回退；复测 `REG-P01-019` 和接口级 P0 回归通过。
- 是否已复现：已复现。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：待判断。
- 关联文件或命令：`/api/api-testing/requests/`、`apps/api_testing/serializers.py`、`apps/api_testing/views.py`、`REG-P01-019`。

### 2026-07-10 00:54 - Playwright CLI run-code 注入监听写法错误

- 场景：真实浏览器回归中，准备注入 `beforeunload` / `pagehide` / `visibilitychange` 监听，用于验证跨模块导航没有整页刷新。
- 错误现象：`playwright-cli run-code "await page.evaluate(...)"` 返回 `SyntaxError: Unexpected identifier 'page'`，说明该 CLI 子命令不是直接接收这类代码片段的写法。
- 影响范围：只影响本轮浏览器导航事件监听注入；页面实际点击“接口自动化”已成功进入模块总览。
- 临时处理：改用 CLI 支持的 `eval "() => { ... }"` 形式重新注入监听，已返回 `true`。
- 是否已复现：本轮已复现。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否，属于工具命令用法纠偏。
- 关联文件或命令：`npx --package @playwright/cli playwright-cli run-code "await page.evaluate(...)"`。

### 2026-07-10 20:27 - P0.2 续跑阶段 Playwright 会话关闭导致浏览器命令失败

- 场景：用户要求继续 P0.2 后，尝试复用上一轮真实浏览器回归中的 Playwright CLI 会话读取页面状态。
- 错误现象：`playwright-cli eval ...` 返回 `Browser 'default' is not open`，说明上一轮浏览器会话已经关闭，不能继续复用。
- 影响范围：仅影响本轮浏览器回归续跑方式，不影响项目代码和已完成的接口回归结论。
- 临时处理：后续重新通过 `npx --package @playwright/cli playwright-cli open http://127.0.0.1:5173/ --headed` 打开新会话，再重新登录和执行浏览器门禁。
- 是否已复现：本轮已复现一次。
- 当前状态：待处理。
- 是否需要升级到 `error_prevention_log.md`：否，属于会话生命周期变化。
- 关联文件或命令：`npx --package @playwright/cli playwright-cli eval ...`。

### 2026-07-10 20:27 - P0.2 续跑阶段 ORM 查询 AI 任务状态命令超时

- 场景：恢复 P0.1 / 阶段 A 回归门禁时，执行只读 Django ORM 命令查询 AI 需求分析任务状态和结果处理快照。
- 错误现象：查询命令达到超时时间后未返回结果。
- 影响范围：仅影响本轮回归数据状态盘点效率；未确认命令执行到写库动作，且该盘点脚本原计划只读。
- 临时处理：后续已改用更窄字段、更长超时、显式 `PYTHONIOENCODING=utf-8` 的只读查询，避免输出大字段正文；复查确认 `p0_reg_user_a`、`p0_reg_user_b` 和 `P0_REG` 任务夹具存在。
- 是否已复现：本轮已复现一次。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：待判断。
- 关联文件或命令：`venv\\Scripts\\python.exe manage.py shell` 只读 ORM 查询脚本。

### 2026-07-10 20:27 - P0.2 续跑初始仓库状态读取命令再次超时

- 场景：用户再次要求继续后，恢复当前仓库位置、目录和 Git 状态。
- 错误现象：首次并行执行 `Get-Location`、`Get-ChildItem` 和 `git status --short` 时，10 秒超时未返回可用结果。
- 影响范围：仅影响本轮上下文恢复效率，不影响项目文件内容；未进入业务代码修改。
- 临时处理：改用 `login=false`、60 秒超时和更窄的真实项目根目录后重新读取，已成功恢复项目状态。
- 是否已复现：本轮已复现一次。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否，已有同类大目录 / 登录 shell 超时事件，本轮按既有方式规避。
- 关联文件或命令：`Get-Location`、`Get-ChildItem -Force`、`git status --short`。

### 2026-07-10 20:27 - P0.2 浏览器回归续跑时本地前后端服务未监听

- 场景：准备重新执行 P0.1 / 阶段 A 浏览器回归门禁前，检查本地前端 `5173` 和后端 `8000` 服务。
- 错误现象：`curl.exe -I --max-time 5 http://127.0.0.1:5173/` 和 `curl.exe -I --max-time 5 http://127.0.0.1:8000/` 均连接失败；`netstat` 未显示稳定监听端口。
- 影响范围：浏览器回归暂时无法执行；不影响代码文件和已完成的接口脚本回归结论。
- 临时处理：后续已重新启动后端和前端，并复查确认后端 `8000` 可访问、前端 `5173` 返回 200。
- 是否已复现：本轮已复现一次。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否，属于本地服务状态变化。
- 关联文件或命令：`curl.exe -I --max-time 5 http://127.0.0.1:5173/`、`curl.exe -I --max-time 5 http://127.0.0.1:8000/`、`netstat -ano`。

### 2026-07-10 20:36 - P0.2 浏览器回归登录按钮点击等待稳定超时

- 场景：重新打开 Playwright 浏览器后，在登录页填入回归账号并点击“登录”按钮。
- 错误现象：`playwright-cli click e108` 等待按钮 visible / enabled / stable 超过 5 秒后超时；后续快照确认实际已提交登录并进入 `/home`。
- 影响范围：仅影响本轮浏览器回归登录操作方式，不代表业务登录接口失败。
- 临时处理：后续重新抓取页面快照，确认已进入工作台，未再重复点击登录按钮。
- 是否已复现：本轮已复现一次。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：待判断。
- 关联文件或命令：`npx --package @playwright/cli playwright-cli click e108`。

### 2026-07-10 20:38 - 登录页控制台输出登录结果时包含 token

- 场景：P0.2 浏览器回归重新登录后，读取 Playwright 控制台日志检查是否有红错或敏感输出。
- 错误现象：控制台存在 `Login result` 日志，输出对象中包含 `access` 和 `refresh` token；同时还有认证初始化、路由守卫等调试日志。
- 影响范围：当前在开发环境日志中已可见；P0.2 的生产调试日志清理和敏感信息保护必须覆盖该入口，避免生产构建或线上调试时泄露 token。
- 临时处理：已在 P0.2 第一批中清理登录、token 刷新、路由守卫、AI 配置页等敏感 `console` 输出，并新增后端日志脱敏 helper。
- 是否已复现：本轮已复现一次。
- 当前状态：已沉淀。
- 是否需要升级到 `error_prevention_log.md`：是，已沉淀为错误模式 032。
- 关联文件或命令：`.playwright-cli\\console-2026-07-10T12-36-13-120Z.log`、`frontend/src/views/auth/Login.vue`、`frontend/src/router/index.js`、`frontend/src/stores/user.js`。

### 2026-07-10 20:55 - P0.2 浏览器回归点击结果页处理结果按钮超时

- 场景：进入 `P0_REG_BROWSER_SINGLE_205251` 结果列表后，点击表格行“处理结果”按钮打开结果处理抽屉。
- 错误现象：`playwright-cli click f2e314` 在执行点击动作阶段超过 5 秒，命令返回超时；后续多选任务中点击 `f3e299` 也出现同类超时。快照确认第一次点击实际已打开抽屉。
- 影响范围：仅影响浏览器回归自动化操作节奏，不代表业务功能失败。
- 临时处理：后续重新抓取页面快照确认抽屉是否已打开；如果已打开，不重复点击。后续同类按钮优先用快照确认实际页面状态。
- 是否已复现：本轮已复现一次。
- 当前状态：已复现，处理中。
- 是否需要升级到 `error_prevention_log.md`：待判断。
- 关联文件或命令：`npx --package @playwright/cli playwright-cli click f2e314`、`npx --package @playwright/cli playwright-cli click f3e299`。

### 2026-07-10 21:02 - P0.2 浏览器回归并行点击同一页面复选框导致操作失败

- 场景：多选采纳回归中，尝试并行点击处理抽屉中的前两条结果复选框。
- 错误现象：第一个复选框点击在等待稳定时超时，第二个复选框等待 ref 失败。
- 影响范围：仅影响本轮 Playwright 操作方式，不代表页面多选功能失败。
- 临时处理：后续对同一页面交互改为串行操作；如 ref 点击仍因 Element Plus 表格结构超时，再使用 DOM click 触发同一复选框。
- 是否已复现：本轮已复现一次。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否，属于自动化操作方式问题。
- 关联文件或命令：`playwright-cli click f3e428`、`playwright-cli click f3e461`。

### 2026-07-10 21:09 - P0.2 浏览器回归 reload 等待 load 超时

- 场景：多选采纳回归中，为清理复选框 DOM 与表格选择状态不一致，执行浏览器 reload。
- 错误现象：`playwright-cli reload` 已导航到当前结果页，但等待 `load` 事件超过 60 秒后超时。
- 影响范围：仅影响本轮浏览器自动化刷新等待，不代表页面一定不可用。
- 临时处理：后续用快照确认页面实际渲染状态；如果页面可操作，继续回归；如不可操作，再看控制台和请求列表。
- 是否已复现：本轮已复现一次。
- 当前状态：待处理。
- 是否需要升级到 `error_prevention_log.md`：待判断。
- 关联文件或命令：`npx --package @playwright/cli playwright-cli reload`。

## 2026-07-10 21:37:24 +08:00 - P0.2 并行上下文读取命令超时
- 现象：并行执行 Get-Location、git status --short、规则文件 rg 时均超过 10-12 秒超时；同批大范围日志 rg 成功返回。
- 影响：未影响代码修改，但需要改用更小范围或更长超时重新读取上下文。
- 处理：已记录事件，后续使用限定路径和延长超时继续执行。

## 2026-07-10 21:38:25 +08:00 - 规则文件读取未显式指定 UTF-8 导致终端乱码
- 现象：读取 AGENTS.md 和子目录 AGENTS.md 时未显式指定 UTF-8，终端输出出现乱码。
- 影响：不影响已知规则执行，但属于规则读取方式偏差。
- 处理：后续中文规则/文档读取显式使用 -Encoding UTF8，修改和追加文档也显式使用 UTF-8。

## 2026-07-10 21:42:10 +08:00 - P0.2 models.py 行段读取命令超时
- 现象：读取 apps/requirement_analysis/models.py 第 470-740 行时，命令已经输出关键片段但超过 30 秒被终止。
- 影响：不影响实现判断，但说明直接遍历大文件输出行号效率较低。
- 处理：已记录事件，后续改用更窄的静态检索或只读取必要片段。

## 2026-07-10 21:46:21 +08:00 - P0.2 文档补丁因错误日志非 UTF-8 字节失败
- 现象：使用 apply_patch 同时修改 .env.example 和 error_event_log.md 时，error_event_log.md 存在非 UTF-8 字节，补丁工具报 invalid utf-8 sequence。
- 影响：.env.example 补丁未落地，错误日志文件需要先修复编码。
- 处理：已按字节范围替换 21:37 的乱码日志块为 UTF-8 文本，并重新记录本次工具失败。

## 2026-07-10 21:52:29 +08:00 - P0.2 配置页调试日志批量补丁上下文不匹配
- 现象：尝试一次性清理 AIModelConfig、PromptConfig、GenerationConfigView 的 console 输出时，apply_patch 在 PromptConfig.vue 上下文匹配失败。
- 影响：该批补丁未落地，需要拆分为更小补丁逐个文件处理。
- 处理：已记录事件，后续按文件分别补丁，避免一个文件上下文差异阻断整批修改。

## 2026-07-10 21:57:36 +08:00 - P0.2 前端构建产物通配路径扫描命令失败
- 现象：使用 rg 直接扫描 frontend/dist/assets/Login*.js 等通配路径时，Windows 返回文件名、目录名或卷标语法不正确。
- 影响：只影响构建产物静态扫描命令写法，不影响构建结果。
- 处理：已记录事件，改用 rg 的 -g 文件模式在 dist/assets 目录内重新扫描。

## 2026-07-10 21:59:59 +08:00 - P0.2 缺 CORS 生产配置验证脚本未真正覆盖空配置
- 现象：验证生产缺少 CORS_ALLOWED_ORIGINS 时把环境变量设为空字符串，manage.py check 仍通过；输出显示 python-decouple 回退读取了 .env 中已有开发值。
- 影响：该次验证不能证明缺 CORS 场景；不代表生产校验逻辑已失效。
- 处理：已记录事件，改用 CORS_ALLOWED_ORIGINS=',' 这种非空但解析后为空的值重新验证缺配置拦截。

## 2026-07-10 22:01:16 +08:00 - P0.2 缺 CORS 验证输出重定向编码导致匹配失败
- 现象：CORS_ALLOWED_ORIGINS=',' 时 Django 已抛 ImproperlyConfigured，但脚本使用 *> 重定向再按 UTF-8 读临时文件，中文错误输出乱码，预期字段匹配失败。
- 影响：验证脚本失败，不代表生产缺 CORS 拦截失败。
- 处理：已记录事件，改用 PowerShell 内存字符串捕获输出并设置 PYTHONIOENCODING=utf-8 后重新验证。

## 2026-07-10 22:20:00 +08:00 - P0.2 VDD 初次写入路径基准错误
- 现象：使用 apply_patch 新增 `docs/tasks/2026-07-10-p0-2-cross-module-hardening/vdd.md` 时，默认路径基准落在外层 `E:\testhub_platform-main`，导致 VDD 先写入外层目录，而不是内层项目 `E:\testhub_platform-main\testhub_platform-main`。
- 影响：外层目录短暂出现误写文档；内层项目一开始没有生成 VDD。
- 处理：已删除外层误写文件，并把相同 VDD 内容写入内层项目目录。后续 apply_patch 操作必须显式使用 `testhub_platform-main/...` 前缀，或先确认当前路径基准。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否，已有历史路径基准纠偏事件；本轮交接和 VDD 已说明。

## 2026-07-10 22:22:00 +08:00 - 查看错误日志片段时 Select-Object Index 写法错误
- 现象：执行 `Get-Content ... | Select-Object -Index 684..697` 失败，PowerShell 无法把字符串 `684..697` 转换成 `System.Int32`。
- 影响：只影响错误日志片段查看，不影响文件内容。
- 处理：停止继续使用该写法，直接用 `apply_patch` 按上下文更新错误日志。后续查看行段改用 `-Skip` / `-First` 或脚本块方式。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否，已有同类 PowerShell 行段写法事件。

## 2026-07-10 22:28:00 +08:00 - 收尾并行路径检查命令超时和外层 git status 误用
- 现象：并行执行外层 / 内层 `Test-Path` 时两条路径检查命令超过 10 秒超时；随后在外层 `E:\testhub_platform-main` 执行 `git status --short` 返回 `fatal: not a git repository`。
- 影响：只影响收尾确认方式，不影响内层项目文件；内层项目 `git status --short -- ...` 已确认 VDD 和项目记忆文件处于预期变更状态。
- 处理：后续只在内层项目 `E:\testhub_platform-main\testhub_platform-main` 执行 Git 验证；外层只用文件存在性检查，不再按 Git 仓库处理。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否，属于路径基准和大目录命令超时的本轮现场。

## 2026-07-10 22:40:00 +08:00 - P0.2 第二三批全仓错误处理扫描输出过大超时
- 现象：进入 P0.2 第二批和第三批合并实现时，执行全仓 `rg` 扫描 `error.response`、`Response({'error': ...})`、异常处理等模式，输出量过大，部分并行命令超过 13 秒超时。
- 影响：只影响上下文读取效率，不影响文件内容；已拿到足够证据确认错误处理散落在多模块，不能一次性全仓改。
- 处理：收窄第三批范围为兼容错误解析工具和少量试点，不全仓重写错误响应；后续读取只聚焦 `frontend/src/utils/api.js`、需求分析生成链路和少量试点接口。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否，本轮按既有大范围扫描收窄原则处理。

## 2026-07-10 22:48:00 +08:00 - P0.2 第三批 apps/core 目录读取命令超时
- 现象：并行读取需求分析进度接口、定位错误响应分支和查看 `apps/core` 目录时，`Get-ChildItem apps\core` 超过 10 秒超时。
- 影响：只影响目录盘点效率，不影响实现；已知本轮新增 `apps/core/security.py`，可直接在同目录新增错误响应 helper。
- 处理：后续避免对目录做不必要的并行读取，直接按已确认路径补小文件。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否。

## 2026-07-10 22:47:00 +08:00 - P0.2 错误结构请求级验证发现 400 分支未命中试点 helper
- 现象：DRF APIClient 抽样验证 `/api/requirement-analysis/testcase-generation/not-exist-task/progress/` 的 404 已返回 `code/message/details/request_id`，但 `POST /api/requirement-analysis/testcase-generation/generate/` 空请求仍返回旧字段级结构 `title/requirement_text`，断言失败。
- 影响：第三批“400 参数校验错误试点”未真正覆盖实际请求分支；不能把 400 试点写成通过。
- 处理：已定位到 `TestCaseGenerationTaskViewSet.generate` 的真实 `serializer.is_valid()` 失败分支，改为 `error_response('validation_error', ...)`；复测 400 和 404 均返回 `code/message/details/request_id`。
- 当前状态：已解决。
- 是否需要升级到 `error_prevention_log.md`：否，属于本轮试点分支定位问题，已在 VDD 记录验证证据。

## 2026-07-10 P0.2 收尾命令超时
- 事件：并行读取 AGENTS 规范、目录和 git status 时超时。
- 影响：未修改业务代码，改用更窄范围、非登录 shell 命令继续核查。
- 处理：先记录失败事件，再重新读取目标规范和文件。

## 2026-07-10 P0.2 收尾目标文件读取命令超时
- 事件：读取 error_event_log/error_prevention_log 尾部、App 自动化和接口测试 WebSocket 相关片段时，部分命令超过 20 秒超时。
- 影响：已拿到部分上下文，但不能依赖大范围 Select-String；业务代码尚未修改。
- 处理：先记录失败事件，随后改用 rg + 精确行段读取目标函数。

## 2026-07-10 P0.2 收尾 rg 引号和参数写法失败
- 事件：检索 createManagedWebSocket 引用时 PowerShell 双引号模式解析失败；检索 api_testing 错误响应时把正则片段误当路径。
- 影响：只影响检索命令，不影响代码文件。
- 处理：改用单引号包裹正则，或拆成更简单的 rg 模式继续定位。

## 2026-07-10 P0.2 收尾目标文件行段读取超时
- 事件：按行段读取两个大型 Vue 文件时，部分命令虽然输出了片段但超过 20 秒超时。
- 影响：不影响文件内容；需要继续缩小读取范围到 import 区和 WebSocket 函数区。
- 处理：改用更短的 Skip/First 范围读取。

## 2026-07-10 P0.2 接口测试错误结构验证临时数据缺 created_by_id
- 事件：用 APIClient 验证 move-collection 错误结构时，创建 ApiProject 临时数据触发 MySQL IntegrityError：created_by_id 不能为空。
- 影响：该次真实请求未执行成功；业务代码未因此修改。
- 处理：清理 p02_api_error_ 前缀临时用户，重新按真实数据库字段补齐 created_by 后验证。

## 2026-07-10 P0.2 APIClient 验证使用交互 shell 未输出响应
- 事件：第二次 move-collection APIClient 验证通过管道进入 manage.py shell，命令退出 0 但没有打印 status/json，无法作为有效验证证据。
- 影响：不能把该次请求记为通过；可能残留 p02_api_error_ 前缀临时数据。
- 处理：先清理临时数据，改用 manage.py shell -c 的非交互方式重新验证。

## 2026-07-10 P0.2 构建产物全 assets 敏感日志扫描超时
- 事件：扫描 frontend/dist/assets 全目录中的 WebSocket/轮询敏感 console 文案时超过 30 秒超时。
- 影响：不能把全量构建产物扫描记为通过；源码扫描和前端构建已通过。
- 处理：收窄到本轮相关的 InterfaceManagement*.js 和 TestCaseList*.js 构建产物重新扫描。

## 2026-07-10 P0.2 收尾文档尾部读取超时
- 事件：回写 VDD、阶段记忆、模块记忆、交接和更新日志前，并行读取多个大文档尾部时部分命令超过 20 秒超时。
- 影响：已拿到关键上下文，但不适合继续大范围读取。
- 处理：采用追加小节方式回写本轮收尾结论，避免覆盖已有内容。

## 2026-07-10 P0.2 错误事件收尾判断
- 已沉淀：`P0.2 APIClient 验证使用交互 shell 未输出响应` 已升级到 `error_prevention_log.md` 的 033，后续请求级验证优先使用 `manage.py shell -c`。
- 不重复沉淀：本轮多次读取超时、`rg` 引号问题和构建产物全目录扫描超时，属于既有“大范围命令要收窄”和“PowerShell 命令写法要精确”的同类问题，已用更窄命令处理。
- 当前状态：本轮没有代码阻断级未解决错误。

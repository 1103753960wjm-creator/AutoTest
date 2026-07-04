# VDD：docs 文档目录整理

## 1. 标题

- 任务名称：docs 文档目录整理
- 日期：2026-07-02
- 关联 Spec/SDD：`docs/tasks/2026-07-02-docs-reorganization/spec-sdd.md`
- 关联 TDD：`docs/tasks/2026-07-02-docs-reorganization/tdd.md`
- 当前阶段：VDD
- 本轮最高验证等级：V2

## 2. 本轮改了什么

- 大白话总结：把 `docs` 根目录里混在一起的 Markdown 文档移动到分类目录，并新增 `docs/README.md` 做入口索引。
- 修改的主要文件：`docs/**/*.md`、`.cursor/project_rules.md`、`.cursor/loop_rules.md`、`AGENTS.md`、`更新日志.md`
- 新增的主要目录：`docs/overview`、`docs/architecture`、`docs/ai`、`docs/api`、`docs/api-automation`、`docs/data-factory`、`docs/guides`、`docs/operations`、`docs/planning`
- 没有改但容易被误解的范围：没有改前端、后端、接口、模型、数据库。

## 3. 验收标准核对

| 验收项 | 是否通过 | 证据 | 备注 |
| --- | --- | --- | --- |
| `docs` 根目录只保留入口 README | 是 | `Get-ChildItem docs -File -Filter *.md` | 只剩 `README.md` |
| 分类目录清晰可读 | 是 | `Get-ChildItem docs -Directory` | 已有 `architecture`、`api-automation`、`data-factory` 等 |
| 旧根路径引用无明显残留 | 是 | 旧路径 `rg` 检查 | 典型旧路径已清理 |
| 缺失文档引用已处理 | 是 | 路径存在性检查 | 补了 `unified-table-template-spec.md` 和 `frontend-ui-style-guide.md` |
| 不引入业务回归 | 是 | 未修改业务代码 | 本轮只改文档和规则引用 |

## 4. 验证执行记录

| 验证类型 | 命令或操作 | 结果 | 证据 |
| --- | --- | --- | --- |
| 静态验证 | 根目录 Markdown 检查 | 通过 | `docs` 根目录只剩 `README.md` |
| 静态验证 | 旧路径残留扫描 | 通过 | 典型旧路径无命中 |
| 静态验证 | 文档路径存在性检查 | 通过 | `NO_MISSING_DOC_PATH_REFERENCES` |
| 规则检查 | `powershell -ExecutionPolicy Bypass -File scripts/rule_check.ps1` | 通过 | 规则检查返回 0 |
| 空白检查 | 本轮规则、模板、索引、任务文档尾随空白扫描 | 通过 | `NO_TRAILING_WHITESPACE_IN_SCOPED_TASK_FILES` |
| diff 检查 | `git diff --check -- docs AGENTS.md .cursor 更新日志.md scripts\rule_check.ps1` | 通过 | 返回 0；只出现 Git 换行符提示 |

## 5. 失败和错误事件

- 本轮是否出现错误事件：是
- 已写入 `error_event_log.md` 的事件：
  - 文档整理审计时并行读取命令超时
  - 批量更新文档引用时遇到空内容导致脚本失败
  - 全仓 Markdown 引用替换范围过大导致超时
  - PowerShell 查看指定行片段时 Index 参数写法错误
  - 查找等价文档时并行读取命令超时
  - 文档路径存在性检查误把占位文本当成真实路径
  - 文档路径存在性检查正则范围过宽导致误报
  - 文档路径存在性检查误把通配路径当成真实文件
  - 尾随空白检查范围过宽命中历史文档
- 是否升级到 `error_prevention_log.md`：否
- 未解决错误：无

## 6. 未验证项

- 未验证项：没有逐个点击 Markdown 渲染器里的所有链接。
- 未验证原因：本轮做的是文件结构整理，已用路径扫描覆盖主要文档路径。
- 可能风险：历史正文里可能仍有非标准写法的旧路径文本。
- 后续如何补验证：后续遇到具体链接失效时补到 `error_event_log.md` 并修复。

## 7. 残余风险

- 个别历史文档可能记录了旧文件名作为历史事实，不一定适合全部改成新路径。
- `docs/APP` 内有部分历史报告文件名与正文记录不完全一致，本轮只修明确错误路径。
- 迁移过来的历史长文档存在既有尾随空白，本轮没有批量清理，避免把目录整理扩大成内容重写。

## 8. 回退和止损

- 可以直接回退的文件：本轮移动的 `docs` 文档和新增 `docs/README.md`
- 不可直接回退的变更：无
- 回退后需要验证：旧路径残留、文档目录结构和规则引用
- 是否涉及数据修复或迁移回滚：否

## 9. 最终结论

- 是否达到本轮目标：是
- 是否可以交付：是
- 需要用户继续确认的事项：是否还要进一步把 `APP` 历史目录也重命名为 `app-automation`
- 下一步建议：如果继续整理，可补一轮“历史文档归档”和“项目记忆瘦身”

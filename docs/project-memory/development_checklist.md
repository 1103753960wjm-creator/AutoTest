# TestHub 开发前清单

更新时间：2026-07-02

## 1. 文件职责

本文属于 C 层“项目开发记忆”，用于在每轮开发前快速确认规则、风险、自治等级和验证准备。

本文只做短清单，不替代 `AGENTS.md`、`.cursor/*.md` 和项目记忆文件。

## 2. 必查清单

- [ ] 已按 UTF-8 读取规则、文档和错误日志
- [ ] 已读 `AGENTS.md`
- [ ] 已读 `.cursor/prompt.md`
- [ ] 已读 `.cursor/workflow_rules.md`
- [ ] 已读 `.cursor/autonomy_rules.md`
- [ ] 已读 `.cursor/loop_rules.md`
- [ ] 已读 `.cursor/architecture.md`
- [ ] 已读 `.cursor/storage_rules.md`
- [ ] 已读 `.cursor/project_rules.md`
- [ ] 已读 `docs/task-templates/README.md`
- [ ] 已读 `docs/project-memory/error_event_log.md`
- [ ] 已读 `docs/project-memory/error_prevention_log.md`
- [ ] 已判断本轮自治等级 L0-L4
- [ ] 已判断是否允许 Loop
- [ ] 已明确范围边界和非目标
- [ ] 已明确变更预算
- [ ] 已确认用户已有改动不会被覆盖
- [ ] 已明确验证等级目标
- [ ] 已明确失败停止条件
- [ ] `Spec/SDD`、`TDD`、`VDD` 和需求确认说明会使用中文大白话、细颗粒度表达
- [ ] 非“小修小改”任务已准备按 `docs/task-templates/` 模板落盘到 `docs/tasks/YYYY-MM-DD-任务名/`

## 3. 面向测试工程师的说明要求

- 必须说明用户能看到什么变化。
- 必须说明怎么验收。
- 必须说明哪些场景会失败或需要异常提示。
- 必须说明哪些地方本轮不改。
- 必须说明如果出问题怎么回退或止损。
- 技术名词必须配一句业务含义或测试含义。
- 必须明确是否通过验证、哪些未验证、未验证原因和残余风险。

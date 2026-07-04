# Spec/SDD：docs 文档目录整理

## 1. 标题

- 任务名称：docs 文档目录整理
- 日期：2026-07-02
- 关联模块：`docs`
- 自治等级：L2
- 是否允许受控 Loop：否
- 当前阶段：Spec/SDD

## 2. 大白话背景

- 现在遇到的问题是：`docs` 根目录下堆了很多 Markdown 文档，规格、接口自动化、AI、数据工厂、使用说明、部署说明混在一起。
- 用户感知问题是：找文档时不知道该从哪里看，也不知道哪些是规则、哪些是阶段文档、哪些是历史说明。
- 如果不处理，后续 AI 和人工都会继续把新文档堆到根目录，文档越来越乱。

## 3. 本轮目标

- 把 `docs` 根目录 Markdown 按主题归类到子目录。
- 新增 `docs/README.md` 作为文档入口索引。
- 更新文档中的旧路径引用，避免移动后链接失效。
- 不改业务代码、不改接口、不改模型。

## 4. 本轮不做

- 不重写旧文档内容。
- 不清理历史文档正文里的业务结论。
- 不删除历史归档。
- 不整理 `docs/project-memory` 的正文结构。
- 不改前端、后端业务代码。

## 5. 范围边界

- 允许修改：`docs/**/*.md`、`.cursor/*.md`、`AGENTS.md`、`更新日志.md`
- 禁止修改：`frontend/**`、`backend/**`、`apps/**`
- 是否涉及前端：否
- 是否涉及后端：否
- 是否涉及接口字段或返回结构：否
- 是否涉及数据模型或迁移：否
- 是否涉及认证、权限、安全、AI、异步任务、执行器、报告或 WebSocket：否

## 6. 已知事实

- `docs` 根目录原本有 45 个 Markdown 文件。
- 已有 `project-memory`、`task-templates`、`tasks` 等规则目录，不应混入普通业务文档。
- 部分旧文档中已经存在过期或缺失引用，例如 `unified-table-template-spec.md` 和 `frontend-ui-style-guide.md`。

## 7. 方案说明

- 创建分类目录：`overview`、`architecture`、`ai`、`api`、`api-automation`、`data-factory`、`guides`、`operations`、`planning`。
- 移动根目录 Markdown 到对应分类目录。
- 保留 `APP`、`project-memory`、`task-templates`、`tasks` 现有目录。
- 新增 `docs/README.md` 作为总入口。
- 用批量替换更新旧的 docs 根路径引用。
- 对原本缺失的 `unified-table-template-spec.md` 和 `frontend-ui-style-guide.md` 补稳定入口文档。

## 8. 决策点和待确认项

- 用户已明确允许新增文件夹分类。
- 当前不需要用户再确认分类细节，因为本轮只移动文档，不改业务行为。

## 9. 风险和回退

- 主要风险：移动文件后旧路径引用失效。
- 可能影响：项目记忆、更新日志、历史任务文档中的链接。
- 止损方式：通过旧路径残留扫描和文档路径存在性检查发现问题。
- 可直接回退：本轮新增分类目录和文档移动。
- 不可直接回退：无数据或业务不可逆变更。

## 10. 验收标准

- [ ] `docs` 根目录只保留入口 README，不再散落大量 Markdown。
- [ ] 分类目录清晰可读。
- [ ] 旧的 docs 根路径引用没有明显残留。
- [ ] 文档路径存在性检查通过。
- [ ] `scripts/rule_check.ps1` 通过。
- [ ] 不改业务代码。

## 11. 进入 TDD 条件

- [x] 范围已确认
- [x] 不做事项已确认
- [x] 风险和回退已确认
- [x] 待确认项已关闭或明确暂缓

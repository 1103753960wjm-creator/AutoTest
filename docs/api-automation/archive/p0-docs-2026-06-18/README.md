# 接口自动化 P0 文档归档与下一步建议

更新时间：2026-06-18

## 1. 文件夹用途

本文件夹集中存放接口自动化 P0 当前相关文档，便于后续按阶段推进时统一查看。

本目录是归档副本，不替代 `docs/` 下原始文档。原始文档仍是当前编辑和引用入口。

## 2. 已归档文档

| 文件 | 用途 |
| --- | --- |
| `api-automation-object-closure-audit.md` | 接口自动化对象级闭环审计，列出当前不闭环、半闭环和假入口 |
| `api-automation-testcase-loop-ai-generation-spec.md` | 接口自动化用例闭环与 AI 多目标生成总规格 |
| `api-automation-p0-1-testcase-loop-tdd.md` | P0-1 接口测试用例闭环 TDD |
| `api-automation-p0-1-testcase-loop-vdd.md` | P0-1 接口测试用例闭环 VDD |
| `api-automation-p0-object-closure-fix-tdd.md` | 阶段 A 对象闭环 P0 补强 TDD 草案 |
| `api-automation-p0-2-ai-target-type-spec.md` | P0-2 AI 生成目标类型 Spec/SDD |
| `api-automation-p0-2-ai-target-type-tdd.md` | P0-2 AI 生成目标类型 TDD 草案 |
| `api-automation-p0-object-closure-fix-vdd.md` | 阶段 A 对象闭环 P0 补强 VDD 验收摘要 |

## 3. 综合判断

从审计文档和两份 Spec 综合看，当前不应该直接跳到“AI 采纳入库”或“大规模执行中心重构”。

原因很直接：

- 接口自动化自身还有几个用户可见的 P0 断点，例如接口用例移动集合、请求历史清空假入口、套件级断言假入口。
- P0-2 AI 目标类型只负责“生成前选类型、按类型选 Prompt、结果页按类型展示”，不负责采纳入库。
- P0-3 才是 `api_test_case` 采纳到 `ApiRequest`，它依赖接口测试用例资产列表和集合归属策略足够稳定。
- 当前 AI 生成测试用例主链严禁重写，只能在现有链路外层套用 `target_type`、Prompt 选择和字段展示契约。

## 4. 推荐下一步

建议下一步先做一轮“接口自动化对象闭环 P0 补强”的 Spec/TDD，而不是直接进入 AI 采纳实现。

推荐命名：

```text
阶段 A Spec 历史草案未单独保留，当前以 `docs/api-automation/api-automation-p0-object-closure-fix-tdd.md` 和 `docs/api-automation/api-automation-p0-object-closure-fix-vdd.md` 为准
docs/api-automation/api-automation-p0-object-closure-fix-tdd.md
```

这一轮先把接口自动化里的两个核心页面职责拆清楚，再处理审计文档中用户已经能看到、但点不通或逻辑冲突的断点：

1. 拆分页面职责：`/api-testing/test-cases` 是表格化接口测试用例资产列表，`/api-testing/test-suites` 是测试套件编排和执行页面，旧 `/api-testing/automation` 仅做兼容重定向。
2. 接口测试用例列表按表格展示 `ApiRequest` 原子用例字段，不再让用户感觉只是测试套件或旧调试树改名。
3. 测试套件页面只承接 `TestSuite + TestSuiteRequest` 编排，不抢接口测试用例资产列表职责。
4. 接口测试用例移动到集合。
5. 调试工作区能查看和修改所属集合。
6. 未分组策略收口，所有新建入口口径一致。
7. 请求历史“清空历史”按钮：真实实现清空能力，不能移除或继续假提示。
8. 套件级断言按钮：真实实现编辑弹窗，弹窗样式参考当前系统已有编辑弹窗。
9. 项目负责人字段契约修正。
10. 删除项目、集合、环境前补充级联风险提示。

## 5. 阶段顺序建议

### 阶段 A：接口自动化对象闭环 P0 补强

当前状态：2026-06-19 已完成 Execution 和 VDD 文档回写；后端编译、前端构建和静态检索通过，真实浏览器人工回归待补。

目标：

- 先把“接口测试用例”和“测试套件”拆成两个清晰页面心智：用例是表格资产列表，套件是编排执行入口。
- 先修用户已经可见的断点和假入口。
- 不做大规模 UI 重构。
- 不做 AI 采纳入库。
- 不做执行中心迁移。

完成标准：

- `/api-testing/test-cases` 是表格化接口测试用例资产列表，字段围绕 `ApiRequest` 展示。
- `/api-testing/test-suites` 是测试套件编排和执行页面，字段围绕 `TestSuite + TestSuiteRequest` 展示。
- `/api-testing/automation` 是旧入口兼容地址，不再作为侧边栏正式入口。
- 两个页面之间通过“加入套件 / 查看套件 / 返回用例列表”等明确动作连接，不互相伪装。
- 接口测试用例可以移动到同项目集合。
- 用例列表、调试树、用例详情的集合展示一致。
- 请求历史和套件级断言不再保留“开发中”假入口。
- 请求历史清空真实可用，具备二次确认、明确清空范围和失败提示。
- 套件级断言编辑弹窗真实保存 `TestSuiteRequest.assertions`，样式与系统现有编辑弹窗一致。
- 高风险删除有明确风险提示。

已完成落地：

- 接口测试用例移动集合：列表页弹窗 + 后端同项目校验。
- 调试工作区所属集合：基础信息区可查看和修改，保存时必须选择集合。
- 请求历史清空：按当前筛选范围真实清空，具备二次确认和 loading。
- 套件级断言：编辑弹窗保存 `TestSuiteRequest.assertions`，执行时优先生效。
- 项目负责人：前端改为只读展示，不再提交只读字段。
- 删除风险提示：项目、集合、接口测试用例、环境删除前提示级联影响。
- 请求封装：接口自动化页面业务请求收口到 `frontend/src/api/api-testing.js`。

### 阶段 B：P0-2 AI 生成目标类型

目标：

- 生成入口增加目标类型下拉框。
- Prompt 按 `prompt_type + target_type` 选择。
- 任务固化 `target_type`。
- 结果页按目标类型展示。
- 接口测试用例结果按 `ApiRequest` 字段展示。

边界：

- 不采纳到 `ApiRequest`。
- 不生成测试套件。
- 不重写现有 AI 生成主链。

### 阶段 C：P0-3 接口测试用例采纳

目标：

- `api_test_case` 结果确认后创建或复用 `ApiRequest`。
- 用户在采纳时选择 `ApiProject + ApiCollection`。
- 采纳后可在 `/api-testing/test-cases` 查看。
- 重复采纳幂等。

前置条件：

- 阶段 A 已完成用例表格页和套件编排页职责拆分，集合归属和用例资产列表足够稳定。
- 阶段 B 的 `normalized_payload` 已稳定输出接口用例字段。

### 阶段 D：P1 Web/App 自动化采纳

目标：

- Web/App 生成结果先作为草稿采纳。
- 不伪装成可直接稳定执行。
- 后续补元素、设备、应用包和执行能力。

## 6. 当前最小行动

当前最合理的动作：

```text
先产出“接口自动化对象闭环 P0 补强”Spec/SDD，第一部分就写清楚接口测试用例表格页和测试套件编排页的拆分方案。
```

这份 Spec 应该只围绕审计 P0 断点展开，确认后再写 TDD。TDD 确认后再进入代码实现。

不建议现在直接做：

- P0-3 AI 采纳到 `ApiRequest`。
- Web/App 自动化采纳。
- 执行中心迁移。
- 测试套件完整重构。
- 重写 AI 生成主链。

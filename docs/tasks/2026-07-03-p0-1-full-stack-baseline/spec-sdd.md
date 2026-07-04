# Spec/SDD：P0.1 前后端与样式上线阻断项第一批

## 1. 标题

- 任务名称：P0.1 前后端与样式上线阻断项第一批
- 日期：2026-07-03
- 关联模块：前端样式 UI、前端请求入口、后端权限认证、接口治理
- 自治等级：L0
- 是否允许受控 Loop：否，必须等用户确认 Spec/SDD 和 TDD 后再进入实现；实现阶段如需循环修复，再单独写 Loop 合同
- 当前阶段：Spec/SDD

## 2. 大白话背景

- 现在遇到的问题是什么：
  - `docs/planning/full-stack-optimization-implementation-plan.md` 已经把 P0 定义为上线阻断项，其中多个章节都有 `P0.1`。
  - 样式层缺少统一设计令牌，页面还在散写颜色、圆角、阴影和间距。
  - 前端还有页面直接使用 `axios` 请求后端，绕过 `frontend/src/api/* -> frontend/src/utils/api.js` 统一链路。
  - 后端局部接口仍存在 `AllowAny`、`csrf_exempt`、`permission_classes=[]` 或以 `task_id` 当安全凭证的历史写法，需要审查并补齐认证权限。
- 用户为什么会感知到这是问题：
  - 页面视觉会继续不一致，新页面越改越散。
  - 登录过期、401/403、请求错误处理可能不统一，用户会看到跳转、错误提示和接口行为不一致。
  - 未登录用户可能访问敏感生成任务、配置状态、报告或进度接口，属于上线前必须处理的风险。
- 这个问题如果不处理，会影响什么：
  - 上线验收时会出现 UI 不统一、接口认证不可信、敏感接口暴露、请求入口分散导致问题难追踪。

## 3. 本轮目标

- 本轮要解决的具体事情：
  - 样式主线：新增最小设计令牌文件，并让全局样式和共享基座开始使用同一套 token。
  - 前端请求主线：把 P0.1 点名的裸 `axios` 请求收口到 `frontend/src/api/*` 和 `frontend/src/utils/api.js`。
  - 后端权限主线：审查并修复 P0.1 点名范围内的认证和权限口子，形成明确公开接口白名单。
- 用户完成后能看到的变化：
  - 新改页面的基础颜色、间距、圆角和阴影有统一来源。
  - 数据工厂、执行详情等页面请求仍能正常工作，但不再绕过统一请求封装。
  - 未登录用户访问敏感接口会得到 401/403；有权限用户仍能访问自己的资源。
- 测试人员可以怎么判断变化已经生效：
  - 静态检查能看到 `design-tokens.scss` 已存在并被 `global.scss` 引入。
  - 静态检查能看到 `frontend/src` 中除 `utils/api.js` 外没有裸 `axios.get/post/patch/delete`。
  - 未登录请求敏感接口返回 401/403；登录后请求自己的资源成功。

## 4. 本轮不做

- 明确不做的功能：
  - 不做 P0.2 及后续任务，例如生产环境调试入口清理、实时连接封装、接口错误结构统一、敏感信息脱敏。
  - 不做全站页面大规模视觉重构，不批量替换所有业务页面的历史裸色值。
  - 不新增数据库表，不做数据迁移。
  - 不重写 AI 生成主链、执行器、报告生成或 WebSocket 主链。
- 明确不改的模块：
  - 默认不改 `frontend/src/router/index.js`、`frontend/src/layout/index.vue`、`frontend/src/App.vue`，除非 TDD 阶段确认请求收口必须触及。
  - 默认不改模型文件和迁移文件。
- 明确不碰的接口、数据、权限或高风险链路：
  - 不放宽任何认证或权限。
  - 不把 401/403 降级成 200。
  - 不把敏感接口加入公开白名单，除非用户明确确认理由。

## 5. 范围边界

### 5.1 建议纳入本轮的 P0.1 主线

- 前端样式 UI P0.1：统一设计令牌最小集。
- 前端代码 P0.1：请求入口彻底收口。
- 后端架构 P0.1：权限基线补齐。
- 接口治理 P0.1：接口权限和认证一致性。

### 5.2 建议拆到下一批确认的 P0.1 主线

- 后端代码 P0.1：模拟实现和临时代码清理。
  - 原因：涉及 `apps/ui_automation/views.py`、`apps/api_testing/views.py`、执行器和报告生成逻辑，工时和风险明显大于第一批，容易扩张到执行链路和报告链路。
- 注释与文档 P0.1：删除误导性注释。
  - 原因：需要逐条判断 `模拟`、`临时`、`兼容`、`TODO`、`FIXME` 是否仍有效，适合作为审计/清理任务单独推进。

### 5.3 允许修改的目录或文件

- 样式主线：
  - `frontend/src/assets/css/design-tokens.scss`
  - `frontend/src/assets/css/global.scss`
  - 可选共享基座：`frontend/src/components/page-shells/*`、`frontend/src/components/platform-shared/UnifiedListTable.vue`、`frontend/src/components/platform-shared/FilterBar.vue`
- 前端请求主线：
  - `frontend/src/components/DataFactorySelector.vue`
  - `frontend/src/views/data-factory/DataFactory.vue`
  - `frontend/src/views/executions/ExecutionDetailView.vue`
  - `frontend/src/main.js`
  - `frontend/src/utils/api.js`
  - `frontend/src/api/data-factory.js`
  - `frontend/src/api/core.js` 或 `frontend/src/api/executions.js`
- 后端权限主线：
  - `apps/requirement_analysis/views.py`
  - `apps/app_automation/views/execution_views.py`
  - `backend/settings.py`
  - `backend/urls.py`
  - 必要时补充对应 `urls.py` 或最小测试/文档清单

### 5.4 禁止修改的目录或文件

- 禁止修改数据库迁移，除非用户重新确认。
- 禁止批量格式化全仓文件。
- 禁止重写 `apps/requirement_analysis` AI 生成主链。
- 禁止为了通过验证改低测试断言、屏蔽错误或隐藏失败。

### 5.5 影响类型

- 是否涉及前端：是。
- 是否涉及后端：是。
- 是否涉及接口字段或返回结构：原则上否；如权限失败响应结构发生变化，必须在 TDD 前确认。
- 是否涉及数据模型或迁移：否。
- 是否涉及认证、权限、安全、AI、异步任务、执行器、报告或 WebSocket：是，涉及认证、权限和安全；不主动触碰 AI 主链、异步任务、执行器、报告和 WebSocket。

## 6. 已知事实

- 已按 UTF-8 读取根 `AGENTS.md`、`.cursor/*.md`、`frontend/AGENTS.md`、`backend/AGENTS.md`、错误日志、防复发手册和当前阶段记忆。
- 当前工作区已有大量未提交变更，不属于本轮 P0.1 预检产生；本轮不能回滚或覆盖这些既有变更。
- 用户给出的计划文档路径实际已整理到 `docs/planning/full-stack-optimization-implementation-plan.md`。
- `frontend/src/assets/css` 当前只有 `global.scss`，没有 `design-tokens.scss`，也未发现 `--th-*` 设计令牌。
- `frontend/src/main.js` 当前仍直接导入 `axios` 并设置 `axios.defaults`。
- 裸 `axios` 当前集中在：
  - `frontend/src/components/DataFactorySelector.vue`
  - `frontend/src/views/data-factory/DataFactory.vue`
  - `frontend/src/views/executions/ExecutionDetailView.vue`
  - `frontend/src/main.js`
- `frontend/src/utils/api.js` 是统一 axios 实例入口，但当前存在 token 刷新相关 `console.log/console.error`，这更接近 P0.2 调试日志清理，第一批只记录风险，不顺带扩大。
- `backend/settings.py` 默认 DRF 权限为 `IsAuthenticated`。
- `apps/requirement_analysis/views.py` 存在 `AllowAny`、`csrf_exempt`、`permission_classes=[]`，其中进度接口有“`task_id` 本身就是安全标识”的历史注释。
- `apps/app_automation/views/execution_views.py` 主要类权限为 `IsAuthenticated`，但也存在 `csrf_exempt` 装饰器，需要判断是否仍有必要。
- 后端模拟实现静态检索命中了 `apps/ui_automation/views.py` 和 `apps/api_testing/views.py` 多处“模拟”语义，但这条建议拆到下一批 P0.1。

## 7. 方案说明

### 7.1 并发开发方式

确认进入 Execution 后，建议用多个子 agent 并发，但每个子 agent 必须只拥有独立写入范围：

- 样式 worker：
  - 负责 `design-tokens.scss`、`global.scss` 和少量共享样式基座。
  - 禁止批量改业务页面。
- 前端请求 worker：
  - 负责裸 `axios` 收口和 API 封装补齐。
  - 禁止改路由、布局和业务字段契约。
- 后端权限 worker：
  - 负责 P0.1 点名文件的权限审查、白名单整理和最小修复。
  - 禁止放宽权限，禁止修改模型和迁移。
- 主 agent：
  - 负责整合、冲突检查、规则验证、构建/编译验证、VDD 和文档回写。

### 7.2 样式主线方案

- 新增 `frontend/src/assets/css/design-tokens.scss`，定义计划要求的最小 token。
- 在 `global.scss` 顶部引入 token。
- 将 `global.scss` 中基础类优先替换为 token，例如背景、文本色、状态色、卡片圆角、间距、阴影和表格 header 变量。
- 对共享页面壳只做轻量映射，避免 P0.1 变成 P1.2 的卡片风格大整理。

### 7.3 前端请求主线方案

- `main.js` 不再直接配置全局 axios defaults；这些配置收口到 `utils/api.js`。
- 在 `frontend/src/api/data-factory.js` 补齐数据工厂分类、标签、列表、统计、新建、删除等接口封装。
- 在 `frontend/src/api/core.js` 或新增 `frontend/src/api/executions.js` 补齐执行计划详情、执行用例状态更新、历史和删除接口。
- `DataFactorySelector.vue`、`DataFactory.vue`、`ExecutionDetailView.vue` 改为调用 API 层函数。
- 保持页面现有请求参数和响应消费方式，不改变后端接口字段。

### 7.4 后端权限主线方案

- 先建立公开接口白名单，典型公开接口只应包括登录、注册、token 刷新等认证入口；需求生成、配置状态、报告文件、执行进度默认不公开。
- 审查并收紧 `apps/requirement_analysis/views.py` 中的 `AllowAny`、`csrf_exempt`、`permission_classes=[]`。
- 进度接口不再只依赖 `task_id` 判断安全，至少要求登录态；若需要对象权限，按任务归属或项目归属校验。
- 审查 `apps/app_automation/views/execution_views.py` 报告或文件访问接口，确保未登录不能访问敏感报告文件。
- 如发现某些接口确实必须匿名访问，必须在白名单中写清业务理由和风险。

## 8. 决策点和待确认项

- 待确认 1：本轮是否按建议只做三条第一批主线：样式令牌、前端请求收口、后端权限/接口认证一致性？
- 待确认 2：是否把“后端代码 P0.1 模拟实现和临时代码清理”也纳入同一轮？建议不纳入，单独开下一批 P0.1。
- 待确认 3：是否把“注释与文档 P0.1 删除误导性注释”也纳入同一轮？建议不纳入，单独做审计清理。
- 待确认 4：后端公开接口白名单是否允许除认证类接口外还有匿名接口？如果允许，需要用户确认清单和理由。
- 待确认 5：样式 token 的圆角是否保持当前较大的页面壳视觉，还是按计划逐步压到 8px 左右？建议 P0.1 先只建立 token，不做明显视觉大改。
- 如果用户不确认，不能继续推进的原因：
  - 本轮涉及认证、权限、安全和前后端多文件联动，规则要求 L0 先确认范围，不能由 AI 直接替用户接受风险。

## 9. 风险和回退

- 主要风险：
  - 样式 token 如果直接替换共享页面壳，可能影响大量页面视觉。
  - 请求收口如果封装参数或返回值处理不一致，可能导致数据工厂或执行详情页功能回退。
  - 权限收紧可能暴露前端此前依赖匿名访问的旧入口，出现 401/403。
  - 当前工作区已有大量未提交变更，必须避免覆盖用户或历史改动。
- 可能影响的旧功能：
  - 数据工厂列表、统计、新建、删除、标签/分类筛选。
  - 执行详情页用例状态更新、历史查看、删除。
  - 需求分析生成、配置检查、任务进度查询。
  - App 自动化执行报告或文件访问。
- 出问题时怎么止损：
  - 样式改动可回退到 `global.scss` 和 token 文件变更。
  - 前端请求收口可回退对应 API 封装和页面调用变更。
  - 后端权限收紧如影响确认的合法匿名入口，必须先恢复白名单并补文档说明。
- 哪些改动可以直接回退：
  - 本轮不做数据迁移，因此代码级改动理论上都可通过 git 局部回退。
- 哪些改动不能直接回退：
  - 如果后续用户确认加入模拟实现清理，可能触及执行结果和报告行为，届时需要单独写回退方案。

## 10. 验收标准

- [ ] `frontend/src/assets/css/design-tokens.scss` 存在，并被 `frontend/src/assets/css/global.scss` 全局引入。
- [ ] P0.1 新改样式优先使用 `--th-*` token，不继续新增裸 `#409eff`、`#f5f7fa` 等硬编码颜色。
- [ ] `frontend/src` 中除 `frontend/src/utils/api.js` 外，不再有裸 `axios.get/post/patch/delete` 请求。
- [ ] `frontend/src/main.js` 不再直接设置全局 axios defaults；统一请求配置进入 `utils/api.js`。
- [ ] 数据工厂和执行详情页主要功能不回退。
- [ ] 未登录用户不能访问敏感需求生成、配置状态、报告文件和进度接口。
- [ ] 有权限用户可以正常访问自己的资源。
- [ ] 权限失败返回 401/403，不伪装成功。
- [ ] 公开接口有清单和理由。
- [ ] 不引入数据库迁移、不新增依赖、不重写 AI/执行器/报告主链。

## 11. 进入 TDD 条件

- [ ] 用户确认本轮 P0.1 第一批范围。
- [ ] 用户确认是否暂缓后端模拟实现清理。
- [ ] 用户确认是否暂缓误导性注释删除。
- [ ] 用户确认公开接口白名单处理原则。
- [ ] 用户确认可以进入 TDD。

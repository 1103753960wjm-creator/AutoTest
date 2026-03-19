# 平台回归基线

## 1. 目标

本文件用于为 TestHub 建立后续持续 videcoding 的最小 smoke 回归基线。

本次只冻结“最小可用回归面”：

- 关键登录态链路可验证
- 首页和主模块入口可验证
- 各主模块至少有一组关键页面可打开
- 配置中心和系统管理隐藏入口可验证

本次不包含：

- 重写前端测试框架
- 建设完整自动化测试体系
- 覆盖所有表单细节、所有 CRUD、所有执行结果分支

## 2. 回归范围定义

### 2.1 关键回归范围

- 登录 / 退出 / token 失效
- 首页加载和模块入口跳转
- 测试设计主链
- 接口自动化主链
- Web 自动化主链
- App 自动化主链
- 数据工厂主链
- 配置中心主链
- 系统管理现有隐藏入口

### 2.2 smoke 通过标准

除单独说明外，页面 smoke 通过的最小标准统一为：

- 路由可以正常进入，不发生重定向死循环
- 页面标题、面包屑、模块归属能正常显示
- 主内容区可见，不白屏、不出现明显未捕获报错
- 关键数据请求返回后，页面能展示列表、表单、空态或占位态之一
- 没有因为登录态、路由 meta、layout 壳或接口 401 导致页面立即崩掉

### 2.3 空数据判定

若测试环境无业务数据，以下情况仍视为 smoke 通过：

- 页面显示空列表
- 页面显示空状态
- 页面显示“暂无数据”但无崩溃

以下情况视为 smoke 失败：

- 白屏
- 死循环跳转
- 未登录情况下误进受保护页面
- token 失效后无法回登录页
- 页面因为缺少数据直接抛异常

## 3. 前置条件

### 3.1 账号与环境

- 准备 1 个可登录测试账号
- 该账号至少具备当前前端可见主模块的访问权限
- 后端服务、前端服务、数据库已可用

### 3.2 推荐最小数据

建议准备以下最小数据，以便 smoke 时不只验证空页：

- 至少 1 个测试设计项目
- 至少 1 条测试用例或 AI 生成结果
- 至少 1 个接口自动化项目或接口
- 至少 1 个 Web 自动化项目
- 至少 1 个 App 自动化项目
- 至少 1 条配置中心配置记录

若暂时没有这些数据，也应至少验证页面可以稳定显示空态。

## 4. 高风险失败场景

后续每次改以下区域时，至少执行本文件对应 smoke：

- `frontend/src/stores/user.js`
- `frontend/src/utils/api.js`
- `frontend/src/router/index.js`
- `frontend/src/router/route-meta.js`
- `frontend/src/layout/index.vue`
- `frontend/src/views/Home.vue`
- `apps/users/*`
- `backend/urls.py`

重点失败场景：

- access token 过期后，刷新链路失效
- refresh token 无效后，401 无法回收为重新登录
- layout 菜单和 meta 不一致，导致页面能开但标题或模块归属错误
- 首页卡片跳转目标变更后失效
- 配置中心页面误挂到业务模块
- 个人资料入口继续散落或被误删

## 5. 执行顺序建议

推荐 smoke 顺序如下：

1. 认证链路
2. 首页和一级模块入口
3. 测试设计
4. 接口自动化
5. Web 自动化
6. App 自动化
7. 数据工厂
8. 配置中心
9. 系统管理隐藏入口

这样可以最早暴露全局 token、路由守卫、layout 和导航问题。

## 6. Smoke 基线矩阵

### 6.1 认证链路

| 模块 | 页面 / 路径 | 核心动作 | 预期结果 |
| --- | --- | --- | --- |
| 系统管理 | `/login` | 打开登录页 | 页面正常显示登录表单，不被错误重定向到受保护页面。 |
| 系统管理 | `/login` | 输入正确账号密码并登录 | 调用 `/api/auth/login/` 成功，写入 `access_token`、`refresh_token`、`token_expires_at`、`user`，跳转到 `/home`。 |
| 系统管理 | `/home` | 已登录状态下访问 `/login` | 被路由守卫重定向到 `/home`。 |
| 系统管理 | 任意受保护页 | 删除本地 token 后刷新页面 | 被路由守卫拦截并跳转 `/login`。 |
| 系统管理 | 任意受保护页 | 构造 access token 失效但 refresh token 有效 | 请求出现 401 后，前端尝试刷新 `/api/auth/token/refresh/`，刷新成功后原请求继续完成。 |
| 系统管理 | 任意受保护页 | 构造 access token 与 refresh token 同时失效 | 刷新失败，用户被清理本地登录态并回到 `/login`。 |
| 系统管理 | 首页或 layout | 点击退出登录 | 调用 `/api/auth/logout/` 或本地兜底清理成功，返回登录页，后续访问受保护页面需重新登录。 |

### 6.2 工作台

| 模块 | 页面 / 路径 | 核心动作 | 预期结果 |
| --- | --- | --- | --- |
| 工作台 | `/home` | 登录后打开首页 | 页面卡片、用户下拉、语言下拉正常显示，不白屏。 |
| 工作台 | `/home` | 点击“AI用例生成”卡片 | 能打开 `/ai-generation/requirement-analysis`。 |
| 工作台 | `/home` | 点击“接口测试”卡片 | 能打开 `/api-testing/dashboard`。 |
| 工作台 | `/home` | 点击“UI自动化测试”卡片 | 能打开 `/ui-automation/dashboard`。 |
| 工作台 | `/home` | 点击“APP自动化测试”卡片 | 能打开 `/app-automation/dashboard`。 |
| 工作台 | `/home` | 点击“数据工厂”卡片 | 能打开 `/data-factory`。 |
| 工作台 | `/home` | 点击“配置中心”卡片 | 能打开 `/configuration/ai-model`。 |
| 工作台 | `/home` | 点击“AI 智能模式”卡片 | 能打开 `/ai-intelligent-mode/testing`。 |
| 工作台 | `/home` | 点击“AI评测师”卡片 | 能打开 `/ai-generation/assistant`。 |

### 6.3 测试设计

| 模块 | 页面 / 路径 | 核心动作 | 预期结果 |
| --- | --- | --- | --- |
| 测试设计 | `/ai-generation/requirement-analysis` | 打开页面 | 页面可见，标题为“需求分析”，主工作区正常渲染。 |
| 测试设计 | `/ai-generation/generated-testcases` | 打开页面 | AI 生成结果列表或空态正常显示。 |
| 测试设计 | `/ai-generation/projects` | 打开页面 | 项目列表或空态正常显示。 |
| 测试设计 | `/ai-generation/testcases` | 打开页面 | 测试用例列表或空态正常显示。 |
| 测试设计 | `/ai-generation/reviews` | 打开页面 | 评审列表或空态正常显示。 |
| 测试设计 | `/ai-generation/review-templates` | 打开页面 | 评审模板列表可见。 |
| 测试设计 | `/ai-generation/versions` | 打开页面 | 版本管理列表可见。 |
| 测试设计 | `/ai-generation/executions` | 打开页面 | 测试计划列表可见，不因执行中心预留策略而失效。 |
| 测试设计 | `/ai-generation/reports` | 打开页面 | AI 测试报告页面可见。 |

### 6.4 接口自动化

| 模块 | 页面 / 路径 | 核心动作 | 预期结果 |
| --- | --- | --- | --- |
| 接口自动化 | `/api-testing/dashboard` | 打开页面 | 仪表盘正常显示，不白屏。 |
| 接口自动化 | `/api-testing/projects` | 打开页面 | 项目列表可见。 |
| 接口自动化 | `/api-testing/interfaces` | 打开页面 | 接口管理主工作区正常显示。 |
| 接口自动化 | `/api-testing/automation` | 打开页面 | 自动化测试页面正常显示。 |
| 接口自动化 | `/api-testing/history` | 打开页面 | 请求历史页面正常显示。 |
| 接口自动化 | `/api-testing/environments` | 打开页面 | 环境管理列表或空态可见。 |
| 接口自动化 | `/api-testing/reports` | 打开页面 | 测试报告页面可见。 |
| 接口自动化 | `/api-testing/scheduled-tasks` | 打开页面 | 定时任务列表可见。 |
| 接口自动化 | `/api-testing/notification-logs` | 打开页面 | 通知日志列表可见。 |

### 6.5 Web 自动化

| 模块 | 页面 / 路径 | 核心动作 | 预期结果 |
| --- | --- | --- | --- |
| Web 自动化 | `/ui-automation/dashboard` | 打开页面 | 仪表盘正常显示。 |
| Web 自动化 | `/ui-automation/projects` | 打开页面 | 项目列表可见。 |
| Web 自动化 | `/ui-automation/elements-enhanced` | 打开页面 | 元素管理主区域正常显示。 |
| Web 自动化 | `/ui-automation/test-cases` | 打开页面 | 测试用例列表可见。 |
| Web 自动化 | `/ui-automation/scripts-enhanced` | 打开页面 | 脚本生成工作台正常显示。 |
| Web 自动化 | `/ui-automation/scripts` | 打开页面 | 脚本列表可见。 |
| Web 自动化 | `/ui-automation/suites` | 打开页面 | 测试套件列表可见。 |
| Web 自动化 | `/ui-automation/executions` | 打开页面 | 执行记录页面可见。 |
| Web 自动化 | `/ui-automation/reports` | 打开页面 | 测试报告页面可见。 |
| Web 自动化 | `/ai-intelligent-mode/testing` | 打开页面 | AI 智能测试工作台正常显示，模块归属仍为 Web 自动化。 |
| Web 自动化 | `/ai-intelligent-mode/cases` | 打开页面 | AI 用例列表可见。 |
| Web 自动化 | `/ai-intelligent-mode/execution-records` | 打开页面 | AI 执行记录页可见。 |

### 6.6 App 自动化

| 模块 | 页面 / 路径 | 核心动作 | 预期结果 |
| --- | --- | --- | --- |
| App 自动化 | `/app-automation/dashboard` | 打开页面 | 仪表盘正常显示。 |
| App 自动化 | `/app-automation/projects` | 打开页面 | 项目列表可见。 |
| App 自动化 | `/app-automation/devices` | 打开页面 | 设备列表或空态可见。 |
| App 自动化 | `/app-automation/packages` | 打开页面 | 包名管理列表可见。 |
| App 自动化 | `/app-automation/elements` | 打开页面 | 元素管理主区域正常显示。 |
| App 自动化 | `/app-automation/scene-builder` | 打开页面 | 用例编排工作台正常显示。 |
| App 自动化 | `/app-automation/test-cases` | 打开页面 | 测试用例列表可见。 |
| App 自动化 | `/app-automation/test-suites` | 打开页面 | 测试套件列表可见。 |
| App 自动化 | `/app-automation/executions` | 打开页面 | 执行记录页面可见。 |
| App 自动化 | `/app-automation/reports` | 打开页面 | 测试报告页面可见。 |

### 6.7 数据工厂

| 模块 | 页面 / 路径 | 核心动作 | 预期结果 |
| --- | --- | --- | --- |
| 数据工厂 | `/data-factory` | 打开页面 | 主工作台正常显示，不白屏。 |
| 数据工厂 | `/data-factory` | 切换左侧工具或模板区域 | 页面可响应，不因缺少配置或登录态异常而崩溃。 |

### 6.8 配置中心

| 模块 | 页面 / 路径 | 核心动作 | 预期结果 |
| --- | --- | --- | --- |
| 配置中心 | `/configuration/ai-model` | 打开页面 | AI 模型配置列表或空态可见。 |
| 配置中心 | `/configuration/prompt-config` | 打开页面 | 提示词配置列表或空态可见。 |
| 配置中心 | `/configuration/generation-config` | 打开页面 | 生成配置页面正常显示。 |
| 配置中心 | `/configuration/ui-env` | 打开页面 | UI 环境配置页面可见。 |
| 配置中心 | `/configuration/app-env` | 打开页面 | App 环境配置页面可见。 |
| 配置中心 | `/configuration/ai-mode` | 打开页面 | AI 智能模式配置页面可见。 |
| 配置中心 | `/configuration/scheduled-task` | 打开页面 | 通知通道配置页面可见，入口文案与页面职责一致。 |
| 配置中心 | `/configuration/dify` | 打开页面 | Dify 配置页面可见。 |
| 配置中心 | `/api-testing/ai-service-config` | 直接打开页面 | 页面可打开，面包屑和模块归属显示为“配置中心”。 |

### 6.9 系统管理

| 模块 | 页面 / 路径 | 核心动作 | 预期结果 |
| --- | --- | --- | --- |
| 系统管理 | `/ai-generation/profile` | 登录后直接访问 | 个人资料页面可见，模块归属显示为“系统管理”。 |
| 系统管理 | `/register` | 未登录时打开 | 注册页可见，不被错误拦截。 |
| 系统管理 | `/admin/` | 直接访问 Django Admin | 管理后台入口可用，至少能到达登录页。 |

## 7. 最小人工执行清单

每次做平台级改动后，至少执行以下 10 项：

1. 打开 `/login`
2. 登录并进入 `/home`
3. 从首页进入 `/ai-generation/requirement-analysis`
4. 打开 `/ai-generation/testcases`
5. 打开 `/ai-generation/reviews`
6. 打开 `/api-testing/dashboard`
7. 打开 `/ui-automation/dashboard`
8. 打开 `/app-automation/dashboard`
9. 打开 `/data-factory`
10. 打开 `/configuration/ai-model`

若本次改动涉及认证、路由、layout、meta、首页、配置中心，还必须额外补跑：

- `/ai-generation/profile`
- `/configuration/scheduled-task`
- `/api-testing/ai-service-config`
- token 失效回登录流程

## 8. 后续扩展建议

- 后续若引入 Playwright 或现成前端 E2E 框架，可直接按本文件矩阵逐条转成 smoke spec。
- 优先把“认证链路 + 首页跳转 + 10 个最小页面”转成自动化，再扩展到配置中心和执行中心。
- 在执行中心和系统管理正式落地前，不要频繁变更本文件中的最小基线路径。

## 9. 本次落地说明

本次只新增回归基线文档，没有额外引入自动化测试骨架，原因是当前前端 `frontend/package.json` 尚未配置正式测试命令或现成 E2E 运行基座；此时强行补测试文件，价值低于先冻结 smoke 基线本身。

# TestHub Loop 运行日志

更新时间：2026-07-03

## 1. 文件职责

本文属于 C 层“项目开发记忆”，用于记录 L3 受控 Loop 的执行过程和审计证据。

本文不替代 `error_event_log.md`。Loop 中出现失败、阻塞或规则偏差时，必须先写入 `error_event_log.md`，再在本文引用。

## 2. 记录原则

- 只有 L3 受控 Loop 必须记录本文。
- L1/L2 若没有进入循环，可不记录本文。
- 每轮 Loop 必须记录动作、验证、失败和停止原因。
- 本文用中文大白话记录，让不读代码的软件测试工程师也能判断过程是否可信。

## 3. 记录模板

```md
### YYYY-MM-DD - 任务名

- 自治等级：
- Loop 合同：
- 目标：
- 最大循环次数：
- 实际循环次数：
- 修改范围：
- 每轮动作：
  - 第 1 轮：
  - 第 2 轮：
  - 第 3 轮：
- 每轮验证：
  - 第 1 轮：
  - 第 2 轮：
  - 第 3 轮：
- 错误事件：
- 最终验证等级：
- 最终状态：完成 / 暂停 / 阻塞 / 需要用户确认
- 是否触发暂停：
- 下一步：
```

## 4. 当前记录

### 2026-07-03 - P0.1 前后端与样式上线阻断项第一批

- 自治等级：L3 受控 Loop。
- Loop 合同：`docs/tasks/2026-07-03-p0-1-full-stack-baseline/loop-contract.md`。
- 目标：完成样式 token 最小集、前端请求入口收口、后端敏感接口权限补口，并形成 VDD 验证证据。
- 最大循环次数：3。
- 实际循环次数：2。
- 修改范围：`frontend/src/assets/css`、`frontend/src/components/page-shells`、`frontend/src/components/platform-shared`、P0.1 点名前端 API / 页面文件、`apps/requirement_analysis/views.py`、`apps/app_automation/views/execution_views.py`、`backend/urls.py`、本任务文档和项目记忆文档。
- 每轮动作：
  - 第 1 轮：按样式、前端请求、后端权限拆分 worker 并发复核 / 实施；主线程接手前序 worker 超时后留下的半成品，完成 token、axios 收口和权限收紧基础改动。
  - 第 2 轮：复核前端 worker、后端 worker、VDD worker 的结果；修正后端报告入口 302 风险，补请求级验证、最终 VDD、公开白名单、交接和错误事件记录。
  - 第 3 轮：未执行。
- 每轮验证：
  - 第 1 轮：前端构建、后端编译、裸 axios 扫描和权限静态扫描通过；发现 `login_required` 不符合 API 401/403 口径并继续修正。
  - 第 2 轮：`npm run build`、`py_compile`、`rule_check.ps1`、`git diff --check`、静态扫描通过；DRF 测试客户端验证未登录敏感入口 401、直接 App 报告 media 403、登录态配置检查 200、本人任务进度 / SSE 200。
  - 第 3 轮：未执行。
- 错误事件：已记录 P0.1 预检路径 / 搜索失败、并发 worker 未返回、`rg` 模式误识别、子 worker 临时命令失败、文档 worker 路径基准纠偏、`apply_patch` 包装器不可用。
- 最终验证等级：V3（有限请求级验证）。
- 最终状态：完成。
- 是否触发暂停：否。本轮未扩大接口契约、模型、迁移、依赖、AI 主链、执行器或报告生成主链。
- 下一步：补浏览器页面主流程、App 报告真实文件 200、真实无权限对象 403 和浏览器 EventSource 凭据行为验证。

# P0.1 公开接口白名单

## 本轮原则

- 默认所有业务接口都需要认证。
- 公开接口必须有明确理由。
- 需求生成、配置状态、任务进度、报告文件不属于公开接口。

## 允许公开的接口

| 接口范围 | 公开理由 | 备注 |
| --- | --- | --- |
| `/api/auth/login/` | 用户登录前必须访问 | 认证入口 |
| `/api/auth/test-register/` | 当前项目已有注册入口 | 后续如关闭注册，应单独做配置开关 |
| `/api/auth/token/refresh/` | access token 过期后刷新 | 需要 refresh token |

## 本轮明确不公开的接口

| 接口范围 | 原因 |
| --- | --- |
| `/api/requirement-analysis/config/check/` | 会暴露 AI 配置状态 |
| `/api/requirement-analysis/testcase-generation/generate/` | 会创建 AI 生成任务 |
| `/api/requirement-analysis/testcase-generation/{task_id}/progress/` | 任务进度不能只靠 `task_id` 当安全凭证 |
| `/api/requirement-analysis/testcase-generation/{task_id}/stream_progress/` | SSE 进度也必须通过登录态和对象权限 |
| `/api/app-automation/executions/{id}/report/` | 报告文件属于执行结果资产 |
| `/api/app-automation/executions/{id}/report/{file_path}` | 报告文件属于执行结果资产 |
| `/app-automation-reports/{path}` | 该旧静态目录没有对象权限上下文，生产环境不再暴露 |
| `/media/app-automation/allure-reports/{path}` | 开发态 media 直连也没有对象权限上下文，本轮改为 403，正式访问必须走报告 API |

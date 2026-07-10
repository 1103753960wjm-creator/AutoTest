# P0.1 剩余闭环公开接口白名单

## 本轮原则

- 默认所有业务接口都需要认证。
- 公开接口必须有明确理由，不能因为前端暂时能调用就放进白名单。
- 需求生成、配置状态、任务进度、执行报告、元素验证、测试套件执行结果不属于公开接口。
- 对象资源接口必须在登录态基础上继续校验项目、用户或对象归属。

## 允许公开的接口

| 接口范围 | 公开理由 | 备注 |
| --- | --- | --- |
| `/api/auth/login/` | 用户登录前必须访问 | 返回 JWT `access` 和 `refresh` |
| `/api/auth/register/` | 当前项目保留注册入口 | 注册后返回 JWT 双 token；若后续关闭公开注册，需要单独做配置开关 |
| `/api/auth/test-register/` | 当前前端注册页仍调用的公开注册入口 | 本轮去掉临时 token，改为返回真实 JWT 双 token |
| `/api/auth/token/refresh/` | `access` 过期后刷新登录态 | 需要有效 `refresh` token，不是匿名业务接口 |
| `/api/schema/`、`/api/docs/`、`/api/redoc/` | 本地开发和接口调试文档入口 | 是否生产公开不在本轮范围，后续应结合部署配置单独收口 |

## 本轮明确不公开的接口

| 接口范围 | 原因 |
| --- | --- |
| `/api/auth/logout/` | 退出登录需要当前登录态，用于清理 refresh token |
| `/api/auth/me/`、`/api/auth/profile/`、`/api/auth/users/` | 会返回用户信息或用户列表，必须登录 |
| `/api/requirement-analysis/config/check/` | 会暴露 AI 配置状态 |
| `/api/requirement-analysis/testcase-generation/generate/` | 会创建 AI 生成任务 |
| `/api/requirement-analysis/testcase-generation/{task_id}/progress/` | 任务进度不能只靠 `task_id` 当安全凭证 |
| `/api/requirement-analysis/testcase-generation/{task_id}/stream_progress/` | SSE 进度也必须通过登录态和对象权限 |
| `/api/app-automation/executions/{id}/report/` | 报告文件属于执行结果资产 |
| `/api/app-automation/executions/{id}/report/{file_path}` | 报告文件属于执行结果资产 |
| `/app-automation-reports/{path}` | 旧静态目录没有对象权限上下文，生产环境不再暴露 |
| `/media/app-automation/allure-reports/{path}` | 开发态 media 直连没有对象权限上下文，正式访问必须走报告 API |
| `/api/ui-automation/elements/{id}/validate_locator/` | 元素定位器验证属于登录后的项目资源操作；本轮已停止返回模拟验证成功 |

## 扫描结论

- `AllowAny` 当前只保留在注册 / 登录入口。
- `csrf_exempt` 当前只保留在注册 / 登录 / 退出相关认证入口，未在业务资源接口中继续扩散。
- 白名单之外的业务资源接口继续按 DRF 默认认证、模块级权限和对象级查询集限制处理。

# TestHub 技术栈与代码风格规则
 
说明：本文件定义了当前仓库所使用的 Django REST + Vue 3 技术栈的代码风格与项目约束。

## 1. 后端代码风格
- 使用 Python 现有风格：函数、变量、文件名优先 `snake_case`。
- Django / DRF 视图函数和 ViewSet 保持短小，复杂逻辑下沉。
- 优先复用 serializer 做校验和字段转换，不在 view 中堆积重复校验。
- 新增日志优先进入现有日志体系，不到处 `print` 散打。
- 同一模块内优先保持一致的返回和错误风格，不随意再引入第三套包装结构。

## 2. 前端代码风格
- 当前仓库以 Vue 3 Composition API + JavaScript 为主，新增页面优先延续现有风格；已有 TypeScript 局部可继续沿用。
- 页面级逻辑留在页面内，共享逻辑再考虑放 store、api 或 utils。
- 与后端交互优先通过 `frontend/src/api/*` 或 `frontend/src/utils/api.js`，不要在组件里直接拼请求主机。
- 优先保持现有 Element Plus + Pinia + Vue Router 组织方式。
- 避免为了“组合式优雅”把简单页面拆成过多 hooks/composables。
- 长内容页面、长表格页面必须保证主内容区可纵向滚动，不能依赖浏览器默认布局碰运气。
- 表格默认优先保证可读性，不允许用固定高度、全局截断、强制省略号掩盖主要业务内容；如果需要压缩密度，必须提供展开或查看详情路径。

## 3. 命名与结构
- 后端按 Django app 划分：`users`、`projects`、`testcases`、`testsuites`、`executions`、`reports`、`reviews`、`versions`、`assistant`、`requirement_analysis`、`api_testing`、`ui_automation`、`app_automation`、`core`、`data_factory`。
- 前端页面目录与业务目录尽量对应，便于按接口模块反查页面。
- 新增 API 封装函数名应与后端接口语义一致，不取过度抽象名称。

## 4. 接口与字段规则
- 当前仓库并非全局统一 `code/message/data` 包装，新增接口应优先沿用所在模块的现有返回风格，不要再混入第四种格式。
- 页面字段名优先跟后端 serializer / response 一致，除非页面展示层确实需要转换。
- 需要转换时，优先在页面或接口适配层做，不直接反向污染后端字段定义。
- 认证错误、参数错误、业务错误的提示文案要与前端现有错误处理链路兼容。

## 5. 编码与中文规则
- 所有规则文件、源码文件、文档文件统一使用 UTF-8。
- 当前仓库历史文件存在中文乱码风险。遇到乱码时，先判断是文件编码问题还是终端输出问题，再决定是否修复源码。
- 与用户沟通、规范文档、设计文档、交付说明统一使用中文。
- 所有新增或修改的代码注释统一使用中文；字段名、协议关键字、库名、框架名和第三方服务名可保留英文原文。

## 6. 当前仓库的技术现实
- 后端已固定为 Django ORM + DRF + SimpleJWT + Celery + Channels。
- 前端已固定为 Vite + Vue 3 + Pinia + Element Plus，认证和刷新逻辑集中在 `frontend/src/utils/api.js` 与 `frontend/src/stores/user.js`。
- AI 配置当前分布在 `requirement_analysis`、`assistant`、`api_testing`、`ui_automation` 等模块；后续新增能力应优先向统一服务层或配置模型收敛，而不是继续扩散。
- 菜单与路由目前主要是前端静态路由；处理权限和菜单问题时先区分“登录态控制”与“真正的后端权限数据”。

## 7. 工程层新增约束
- 新增后端运行配置统一进入根目录 `.env` 和 `backend/settings.py`，禁止继续把真实地址、数据库账号、路径硬编码进 Python 源码。
- 新增前端运行配置统一进入 `frontend/.env.*` 或 `frontend/vite.config.js`，禁止在页面和工具函数中散落环境判断。
- 新增 AI 提供商、模型角色、统一调用入口时，必须优先考虑配置模型、服务层封装和权限边界，不得在页面、ViewSet、task 中重复拼接 `api_key` / `base_url` / 请求体。

## 8. 验证要求
- Python 改动至少做导入级、`python manage.py check`、调用级或 `pytest` 级验证。
- Vue 改动至少做 `npm run build` 或 `npm run lint` 级验证。
- 高风险改动必须补充结果路径说明：改了哪里、为什么安全、还有什么没验证。

## 9. 明确禁止
- 引入与当前技术栈冲突的新框架来解决局部问题。
- 为了统一风格把老代码一次性改成完全不同的架构。
- 在前端复制后端业务规则，在后端复制前端展示规则。
- 无验证地调整登录、token、AI 调用、执行器、调度、WebSocket 推送逻辑。

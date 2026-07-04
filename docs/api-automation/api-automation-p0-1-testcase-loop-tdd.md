# 接口自动化 P0-1 用例闭环 TDD

更新时间：2026-06-17

状态：已确认并完成 P0-1 Execution / VDD

关联 Spec：

- `docs/api-automation/api-automation-testcase-loop-ai-generation-spec.md`

## 1. 本阶段边界

P0-1 只处理“接口自动化自身闭环”，不进入 AI 生成目标类型和采纳实现。

本阶段目标：

- 新增或改造接口自动化正式入口“接口测试用例”。
- P0 明确 `ApiRequest` 是接口测试用例的技术承载。
- 修正前端 API 封装中的旧接口路径。
- 单接口执行后，断言结果必须真实写入 `RequestHistory`。
- 保持旧 `/api-testing/interfaces` 可访问，不破坏旧入口。
- 保持测试套件执行、请求历史、环境管理不回归。
- 保持顶部模块和侧边栏快速切换不触发整页刷新。

本阶段不做：

- 不新增 `ApiTestCase` 数据表。
- 不实现 AI 生成目标类型下拉框。
- 不实现 AI 生成结果采纳到接口测试用例。
- 不实现 Web/App 自动化采纳。
- 不重构执行中心。
- 不实现安全脚本沙箱。

## 2. 当前待验证事实

当前代码事实：

- 接口自动化后端真实资源是 `/api-testing/requests/`。
- 单接口执行真实接口是 `/api-testing/requests/{id}/execute/`。
- 套件执行真实接口是 `/api-testing/test-suites/{id}/execute/`。
- `frontend/src/api/api-testing.js` 中存在旧路径风险：
  - `/api-testing/api-requests/{id}/execute/`
  - `/api-testing/executions/{id}/`
- `ApiRequestViewSet.execute()` 当前返回断言结果，但需要验证并修正 `RequestHistory.assertions_results` 是否落库。
- 当前接口自动化导航没有“接口测试用例”子模块。

## 3. 验证目标

- [ ] 目标 1：接口自动化导航存在“接口测试用例”入口，路径为 `/api-testing/test-cases`。
- [ ] 目标 2：旧路径 `/api-testing/interfaces` 继续可访问或可兼容重定向，不直接 404。
- [ ] 目标 3：接口测试用例页面能展示现有 `ApiRequest` 数据。
- [ ] 目标 4：接口测试用例页面能创建、编辑、保存 `ApiRequest`。
- [ ] 目标 5：单接口执行使用 `/api-testing/requests/{id}/execute/`，不再使用旧的 `/api-testing/api-requests/{id}/execute/`。
- [ ] 目标 6：单接口执行后 `RequestHistory.assertions_results` 真实落库。
- [ ] 目标 7：请求历史页能展示单接口执行的断言结果。
- [ ] 目标 8：测试套件仍能添加接口请求并执行，生成 `TestExecution`。
- [ ] 目标 9：快速切换顶部模块和接口自动化侧边栏时，不发生整页刷新，不停在旧页面。
- [ ] 目标 10：前端请求继续统一走 `frontend/src/api/* -> frontend/src/utils/api.js`。

## 4. 失败场景

### 4.1 路由和导航失败

- `/api-testing/test-cases` 未注册，点击后 404。
- 导航新增入口后，`/api-testing/interfaces` 失效。
- route meta 缺失，导致页面标题、侧边栏选中态或面包屑异常。
- 顶部模块切换后立即点击“接口测试用例”，页面停在接口自动化总览或旧子页面。
- 几秒内快速点击接口测试用例、测试套件、请求历史，最终没有停在最后点击目标。

### 4.2 数据加载失败

- 接口测试用例页没有项目时白屏或报错。
- 有接口项目但没有用例时没有空态。
- 搜索无结果时仍显示旧数据。
- API 加载失败时没有错误态和重试入口。
- 无权限时没有明确提示。

### 4.3 创建和编辑失败

- 新建接口测试用例时缺少 URL 仍可提交。
- URL 非 `http://` 或 `https://` 时仍可保存为可执行用例。
- Headers、Params 在数组和对象格式之间转换丢数据。
- GET 请求保存时错误携带不必要 Body，导致后端字段异常。
- 编辑后列表没有刷新，显示旧数据。

### 4.4 执行失败

- 前端执行单接口仍调用旧路径 `/api-testing/api-requests/{id}/execute/`。
- 执行失败时没有写请求历史。
- 断言失败没有写入 `assertions_results`。
- 后端返回断言结果，但请求历史详情页看不到。
- 接口执行超时后页面一直 loading。

### 4.5 套件回归失败

- 新增“接口测试用例”入口后，测试套件页面无法添加请求。
- `test-suite-requests` 更新启用状态失败。
- 套件执行结果缺失请求详情。
- 套件执行历史页面无法加载。

### 4.6 请求封装回归

- 页面继续直接散写 `api.get/post`，没有使用 `frontend/src/api/api-testing.js`。
- 旧封装函数路径不一致，后续页面复用会 404。
- 401 或登录过期绕过统一 `authNavigation`。

## 5. 验证层级

本阶段采用以下验证层级：

- 后端编译级：确认受影响 Python 文件语法正确。
- 后端接口级：确认请求路径、响应结构、历史落库逻辑一致。
- 前端构建级：确认路由、组件、API 封装可打包。
- 前端页面级：确认导航、列表、创建、编辑、执行和请求历史展示可用。
- 导航回归级：确认顶部模块和侧边栏快速切换稳定。

选择原因：

- 本阶段同时影响前端路由、导航、页面、接口封装和后端执行逻辑。
- 单纯构建通过不能证明执行历史落库正确。
- 单纯接口通过不能证明 SPA 导航体验正常。

## 6. 最小验证清单

### 6.1 静态检查

命令：

```text
git diff --check
```

通过标准：

- 无尾随空格、冲突标记、非法空白错误。

### 6.2 后端编译级验证

命令：

```text
python -m py_compile apps\api_testing\models.py
python -m py_compile apps\api_testing\serializers.py
python -m py_compile apps\api_testing\views.py
python -m py_compile apps\api_testing\urls.py
```

通过标准：

- 命令执行成功。
- 如果环境缺少 Django 运行依赖，不影响 `py_compile` 语法级验证。

### 6.3 前端构建级验证

命令：

```text
cd frontend && cmd /c npm run build
```

通过标准：

- 构建通过。
- 允许保留既有 `web-tree-sitter` 浏览器兼容与 `eval` 警告。
- 不允许出现新增语法错误、未解析导入或路由组件加载错误。

### 6.4 API 封装路径验证

检查点：

- `executeApiRequest` 或新命名 `executeApiTestCase` 使用 `/api-testing/requests/{id}/execute/`。
- `getExecutionResult` 使用 `/api-testing/test-executions/{id}/`。
- 接口测试用例列表使用 `/api-testing/requests/`。
- 页面不新增裸 axios 请求。

通过标准：

- 全仓不再存在业务可调用的 `/api-testing/api-requests/` 执行路径。
- 新页面请求统一经由 `frontend/src/api/api-testing.js`。

### 6.5 单接口执行历史验证

操作：

1. 创建或选择一个已有 HTTP 接口测试用例。
2. 配置状态码断言，例如期望 200。
3. 点击执行。
4. 打开请求历史。
5. 查看最新一条历史记录。

通过标准：

- 执行请求走 `/api-testing/requests/{id}/execute/`。
- 执行成功或断言失败都能生成 `RequestHistory`。
- `RequestHistory.assertions_results` 不为空，且包含断言名称、类型、期望值、实际值、是否通过。
- 请求历史详情页能展示断言结果。

### 6.6 接口测试用例页面验证

操作：

1. 进入 `/api-testing/test-cases`。
2. 选择接口项目。
3. 搜索接口名称或 URL。
4. 新建接口测试用例。
5. 编辑保存接口测试用例。
6. 执行接口测试用例。

通过标准：

- 页面不白屏。
- 无项目、无用例、搜索无结果、加载失败都有明确状态。
- 创建和编辑后列表刷新。
- 执行按钮有 loading 防重复点击。
- 执行失败能显示后端 `message` 或兜底提示。

### 6.7 旧入口兼容验证

操作：

1. 直接访问 `/api-testing/interfaces`。
2. 从侧边栏进入接口测试用例。
3. 再返回旧入口。

通过标准：

- 旧入口不 404。
- 旧入口如果重定向，目标明确且不循环跳转。
- 旧入口如果保留页面，仍能加载已有接口数据。

### 6.8 测试套件回归验证

操作：

1. 进入 `/api-testing/test-suites`。
2. 创建或选择一个测试套件。
3. 添加一个接口测试用例。
4. 启用或禁用套件内请求。
5. 执行套件。
6. 查看执行历史和结果详情。

通过标准：

- 添加请求到套件接口仍可用。
- 启用状态更新仍可用。
- 执行套件生成 `TestExecution`。
- 套件执行结果包含每个请求的状态、响应时间、断言结果。

### 6.9 导航快速切换验证

操作：

1. 从 Web 自动化切到接口自动化。
2. 立即点击“接口测试用例”。
3. 再快速点击“测试套件”“请求历史”“接口测试用例”。
4. 重复几轮。

通过标准：

- 最终停留在最后点击的菜单。
- 没有 `beforeunload`、`pagehide` 或主文档请求。
- 控制台无 `parentNode`、`exposed`、`Navigation cancelled` 红错。
- 不需要刷新页面才能恢复。

## 7. 测试数据准备

最低需要：

- 一个可访问的接口项目。
- 一个集合。
- 至少一个 GET 接口用例。
- 至少一个带断言的接口用例。
- 一个测试套件。
- 一个可用环境变量配置，允许为空环境。

如果本地没有真实外部接口，建议使用本地后端健康检查或稳定公开测试接口，但不得把外部地址硬编码进业务代码。

## 8. 实现完成判定

P0-1 完成需要同时满足：

- 验证目标 1-10 全部通过。
- 最小验证清单能执行，或对无法执行项给出明确原因。
- 功能测试旧链路不受影响。
- 接口自动化旧入口不失效。
- 工作区只包含本阶段相关改动。
- 交付时说明改动范围、验证证据、未验证项和残余风险。

## 9. 推荐实现顺序

1. 修正前端 API 封装旧路径。
2. 修正单接口执行历史断言结果落库。
3. 新增或改造接口测试用例前端入口和路由。
4. 将接口测试用例页面请求统一收敛到 `frontend/src/api/api-testing.js`。
5. 接入空态、错误态、无权限态和执行 loading。
6. 回归旧 `/api-testing/interfaces`。
7. 回归测试套件执行。
8. 执行构建和导航快速切换验证。

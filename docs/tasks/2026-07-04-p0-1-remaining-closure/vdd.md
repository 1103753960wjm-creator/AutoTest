# VDD：剩余 P0.1 全量关闭

## 改动摘要

- 后端认证入口收口：
  - `apps/users/views.py` 的注册接口不再生成旧 `Token` 或 `temp_token_*`，改为返回 JWT `access` 和 `refresh`。
  - `apps/users/test_views.py` 的前端当前注册入口同样返回 JWT 双 token，避免“注册成功但 token 是临时假的”。
  - `logout` 和 `profile` 显式要求登录态，匿名访问返回 401。
- 后端模拟实现清理：
  - `apps/ui_automation/views.py` 的元素定位器验证不再返回模拟“验证通过”，真实浏览器验证未接入时返回 501，并给出明确错误码 `LOCATOR_VALIDATION_NOT_IMPLEMENTED`。
  - 删除 UI 自动化中未调用的模拟步骤日志和模拟失败截图 helper，避免后续误以为可以伪造执行证据。
  - `apps/api_testing/views.py` 生成 Allure 结果时不再使用“当前时间减固定毫秒”的模拟开始 / 结束时间，改为使用执行记录时间和每条请求的 `response_time`。
- 前端假入口提示：
  - `ElementManagerEnhanced.vue` 的元素验证失败会展示后端返回的真实错误信息。
  - 页面树“页面名称编辑”暂未接入保存接口时，会明确提示“当前不会修改页面名称”，不再静默关闭编辑态。
- 文档补齐：
  - 新增本轮公开接口白名单：`docs/tasks/2026-07-04-p0-1-remaining-closure/public-api-whitelist.md`。
  - 本 VDD 记录验证证据、未验证项和残余风险。

## 验收核对

- [x] 公开接口白名单已补齐，公开接口有理由。
- [x] 白名单之外的认证相关敏感接口匿名访问返回 401。
- [x] App 自动化报告 media 直连返回 403。
- [x] 注册接口不再返回 `temp_token_*`。
- [x] UI 元素定位器验证不再模拟成功，未接入真实浏览器验证时返回 501。
- [x] 用户可见的页面名称编辑假入口已改为明确提示。
- [x] Allure 时间来源不再使用模拟时间注释和固定偏移。
- [x] 前端构建、后端编译、规则检查和基础 diff 检查通过。

## 验证执行记录

### 后端编译

- 命令：`python -m py_compile apps\api_testing\views.py apps\data_factory\views.py apps\ui_automation\views.py apps\users\views.py apps\users\test_views.py`
- 结果：通过。

### 权限和模拟实现静态扫描

- 命令：`rg -n "AllowAny|permission_classes\s*=\s*\[\]|csrf_exempt|login_required" apps backend -g "*.py"`
- 结果：只命中用户注册 / 登录 / 退出相关认证入口，已写入公开接口白名单；未命中业务资源接口继续扩散公开权限。
- 命令：`rg -n "模拟开始时间|模拟结束时间|_perform_element_validation|_generate_step_log|_generate_failure_screenshot|temp_token_|TODO: 实现页面名称保存" apps frontend\src -g "*.py" -g "*.js" -g "*.vue"`
- 结果：无命中；`rg` 无命中返回 1，已在错误事件日志说明为“无残留即通过”。

### 请求级验证

- 命令：使用 `.\venv\Scripts\python.exe` 执行 DRF `APIClient` 验证脚本。
- 样本数据：创建 `P0_SAMPLE_auth_contract_0708` 用户，脚本结尾已删除。
- 结果：
  - `/api/auth/test-register/` 返回 200。
  - 返回体包含 `access=True`、`refresh=True`。
  - 返回体不包含 `temp_token_*`。
  - 匿名 `/api/auth/profile/` 返回 401。
  - 匿名 `/api/auth/logout/` 返回 401。
  - 携带新注册用户 JWT 访问 `/api/auth/profile/` 返回 200，用户名为 `P0_SAMPLE_auth_contract_0708`。
  - 样本用户已清理，`SAMPLE_CLEANED True`。

- 命令：使用 `.\venv\Scripts\python.exe` 执行报告 / 元素入口验证脚本。
- 结果：
  - `/media/app-automation/allure-reports/P0_SAMPLE_missing/index.html` 返回 403。
  - 匿名 `/api/app-automation/executions/999999/report/` 返回 401。
  - 匿名 `/api/ui-automation/elements/999999/validate_locator/` 返回 401。

### 前端构建和规则检查

- 命令：`cd frontend && cmd /c npm run build`
- 结果：通过；仍只有既有 `web-tree-sitter` 的 `fs/path` externalized 与 `eval` 警告。
- 命令：`powershell -ExecutionPolicy Bypass -File scripts\rule_check.ps1`
- 结果：通过，输出 `Rule check passed: no P0 redline hits.`
- 命令：`git diff --check`
- 结果：通过；只输出 Windows 行尾转换提示。

## 错误事件

- 已记录并处理：
  - 默认系统 Python 缺少 Django，已改用仓库 `venv\Scripts\python.exe`。
  - `test-register` 返回 Django `JsonResponse`，验证脚本改为解析 `response.content`。
  - 旧模拟代码残留扫描无命中返回非零状态，已按“无残留即通过”解释。
- 本轮新增错误事件不需要升级到 `error_prevention_log.md`，因为都是一次性验证脚本或环境取用问题，尚未形成稳定防复发规则。

## 未验证项

- 未做真实浏览器页面主流程回归。
- 未做真实 App 报告文件存在时的 200 访问验证。
- 未做真实双用户 / 双项目对象下的 App 报告 403 验证。
- 未做浏览器 `EventSource` 凭据行为验证。
- 未新增长期后端测试用例文件；本轮采用内联验证脚本，避免引入新依赖或扩大测试体系范围。

## 残余风险

- 注册接口返回字段从旧 `token` 改为 JWT `access/refresh`，当前前端注册流程不保存 token、注册后要求手动登录，因此页面行为未受影响；如果外部脚本仍依赖旧 `token` 字段，需要改为使用 JWT。
- `validate_locator` 改为 501 后，前端会明确展示“真实验证尚未接入”，不会再误报成功；但真实浏览器定位器验证能力仍是后续功能。
- Allure 时间现在来自执行记录和请求耗时，但如果历史 `execution.results` 缺少 `response_time`，仍会用执行总时长均分作为兜底，这只是时间展示兜底，不代表重新执行请求。

## 回退止损

- 若注册接口兼容性受影响，可临时在响应中追加兼容字段，但不应恢复 `temp_token_*` 这类假 token。
- 若 UI 元素验证入口影响现有页面，可先隐藏“验证”按钮或保留 501 提示，不能恢复模拟通过。
- 若 Allure 时间展示异常，可回退 `apps/api_testing/views.py` 中的时间推导逻辑，但不应恢复“模拟开始 / 结束时间”注释。

## 最终结论

- 本轮剩余 P0.1 已完成代码与文档闭环，最高验证等级为 V3（有限请求级验证）。
- 可以认为“接口权限和认证一致性、明显模拟实现、误导性注释 / 假入口”这三个 P0.1 剩余方向已经完成可交付收口。
- 进入下一阶段前，建议优先补真实浏览器主流程、真实 App 报告文件 200、真实无权限对象 403 和浏览器 EventSource 凭据行为验证。

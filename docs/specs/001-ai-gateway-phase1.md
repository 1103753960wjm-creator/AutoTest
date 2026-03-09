# 规格说明

> 状态：仅作为技术原型切片参考。当前生效的产品基线规格是 `docs/specs/002-platform-ai-rebuild.md`。

## 背景
- 当前平台已经具备 API、Web、App 自动化执行能力，但 AI 相关能力还没有统一入口。
- 当时为了快速验证三模式接入和用例生成方向，先切了一个纯后端技术原型切片。
- 这个文档记录的是那次技术切片，不再作为当前大改的产品基线。

## 目标
- 提供一个后端 AI Gateway 原型切片，验证统一模式入口是否可行。
- 让 `none` 模式先具备可用的规则式测试用例草稿生成能力。
- 预留 `local_llm` 和 `remote_llm` 的统一 provider 契约，避免未来模型调用散落到业务模块。

## 非目标
- 不覆盖前端页面。
- 不落数据库模型。
- 不处理文件上传、PDF 解析、RAG。
- 不把测试用例草稿直接转换成 API/Web/App 可执行脚本。
- 不覆盖完整的 prompt 管理和 AI 调用日志治理。

## 范围
- 影响的后端模块：
  - `l-tester-master/config/settings.py`
  - `l-tester-master/views/route.py`
  - `l-tester-master/views/ai/*`
  - `l-tester-master/tests/test_ai_service.py`
- 新增的后端能力：
  - AI 模式信息接口
  - 测试用例草稿生成接口

## 输入输出
- 输入：
  - 可选模式覆盖
  - 来源类型
  - 标题
  - 需求文本或功能设计文本
- 输出：
  - 配置模式
  - 生效模式
  - provider 元数据
  - 结构化测试用例草稿
  - 回退或告警信息

## 方案摘要
- 新增独立的 `views.ai` 模块并挂载到主路由。
- 提供统一的 `AIGatewayService`，负责模式解析、provider 选择、测试用例生成。
- provider 分为三类：
  - `none`：规则式、确定性的草稿生成
  - `local_llm`：本地 OpenAI 兼容 provider 入口
  - `remote_llm`：远程 OpenAI 兼容 provider 入口
- 这个原型切片只保证：
  - `none` 模式可用
  - 三模式接口契约统一
  - 配置入口收敛到 `config/settings.py`

## 约束
- 遵守现有后端分层：`view -> service/provider -> config`
- 不引入数据库依赖
- 不要求前端联调才能验证
- 保持输出仍兼容现有 `res_success` 包装结构

## 风险
- provider 配置不完整时，模式回退和报错行为需要明确。
- 规则式用例生成在输入过短或过模糊时质量有限。
- 如果后续业务模块绕过网关直接接模型，这个切片的意义会被破坏。

## 验收标准
- [ ] 后端暴露一个 AI 模式信息接口
- [ ] 后端暴露一个测试用例草稿生成接口
- [ ] `none` 模式无需外部模型即可返回结构化草稿
- [ ] `none`、`local_llm`、`remote_llm` 共享统一 provider 契约
- [ ] 非法配置模式不会导致系统崩溃，而是回退到 `none`
- [ ] 至少有一组 pytest 覆盖模式解析和 `none` 模式输出结构

## 回退方式
- 从 `views/route.py` 移除 `views.ai` 路由挂载
- 删除 `views.ai` 模块和相关测试
- 保留配置项但不继续使用

# VDD

## 验证结论

- 本次修复已完成后端编译级验证。
- 本次修复已完成本地构造响应的内容提取验证。
- 未执行真实 AI 服务调用，原因是外部模型服务、额度和返回格式不可稳定控制。

## 已执行验证

### 1. 后端编译验证

- 命令：`.\venv\Scripts\python.exe -m py_compile apps\requirement_analysis\models.py apps\requirement_analysis\views.py`
- 结果：通过，无语法错误输出。

### 2. 内容提取 helper 验证

- 命令：本地 Python 脚本构造响应片段并调用 `AIModelService._extract_openai_compatible_content()`。
- 覆盖格式：
  - `choices[0].delta.content`
  - `choices[0].message.content`
  - `choices[0].content`
  - 顶层 `content`
  - content 列表中的 `text`
  - content 列表中的 `content`
- 结果：全部返回 `True`，表示提取结果与预期一致。

### 3. 空内容闸门验证

- 命令：本地 Python 脚本调用 `AIModelService._require_non_empty_content('   ', '空内容错误')`。
- 结果：按预期抛出 `ValueError`。

## 验收核对

- [x] 有正文的常见 OpenAI-compatible chunk 能被正确提取。
- [x] 生成阶段最终正文为空时会抛出异常。
- [x] 评审阶段收到空用例时会被阻断。
- [x] `final_test_cases` 关键赋值后已立即保存。
- [x] 任务完成阶段不再保存 `final_test_cases`，避免覆盖已落库内容。
- [x] 后端编译通过。

## 未验证项

- 未用真实 `glm-5.2` / `ciyuan.fast` 重新发起一次完整 AI 生成任务。
- 未进行前端页面截图验证，因为本次未改前端页面和接口字段。

## 残余风险

- 如果供应商返回的是纯 `reasoning_content` 而没有最终 `content`，系统仍会判定生成为空并失败；这是为了避免把推理过程误存为测试用例。
- 如果供应商使用完全私有的非 OpenAI-compatible 字段名，本次 helper 仍无法提取，需要拿到真实响应样本后补充兼容。

## 回退方式

- 回退 `apps/requirement_analysis/models.py` 与 `apps/requirement_analysis/views.py` 的本次改动。
- 删除 `docs/tasks/2026-07-08-ai-empty-generation-review-fix/` 下本次任务文档。

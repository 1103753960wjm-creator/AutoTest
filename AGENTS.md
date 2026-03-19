# AutoTest 代理入口规范

进入仓库后，先按顺序读取并遵守以下文件：

1. `C:\Users\Administrator\.gemini\GEMINI.md`
2. `E:\AutoTest\.antigravity\prompt.md`
3. `E:\AutoTest\.antigravity\workflow_rules.md`
4. `E:\AutoTest\.antigravity\architecture.md`
5. `E:\AutoTest\.antigravity\storage_rules.md`
6. `E:\AutoTest\.antigravity\project_rules.md`
7. 当前仓库根目录下的`MEMORY.md`（如存在）

默认交付流程：

1. `Spec`
2. `TDD`
3. `Execution`

执行要求：

- 未完成 spec 对齐前，不进入正式实现。
- 开始编码前，先总结当前生效规则、范围边界和验收标准。
- 优先复用现有目录、接口封装、返回结构和工具函数。
- `workflow_rules.md` 不能突破 `architecture.md` 的架构红线。
- 新增配置统一进入配置层，不得在业务模块散写硬编码地址、密钥和路径。
- 所有新增或修改的规范文件、设计文档、任务文档、交付说明统一使用中文。
- 所有新增或修改的代码注释统一使用中文；字段名、协议关键字、库名和第三方服务名可保留英文原文。

当前仓库基线：

- 后端：`l-tester-master`，FastAPI + Tortoise ORM + MySQL
- 前端：`l-vue-ui-master`，Vue 3 + TypeScript + Vite + Pinia + Element Plus
- 后续 AI 能力必须通过统一入口接入，禁止在业务模块直接散接模型调用

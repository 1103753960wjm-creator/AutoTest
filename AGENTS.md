# AutoTest 代理入口规范

进入仓库后，先按顺序读取并遵守以下文件：

1. `C:\Users\Administrator\.gemini\GEMINI.md`
2. 当前仓库 `.cursor/prompt.md`
3. 当前仓库 `.cursor/workflow_rules.md`
4. 当前仓库 `.cursor/architecture.md`
5. 当前仓库 `.cursor/storage_rules.md`
6. 当前仓库 `.cursor/project_rules.md`
7. `docs/project-memory/current_phase.md`（如存在）
8. `docs/project-memory/dialogue_bootstrap.md`（如存在，仅用于快速进入上下文，不属于正式规则层）

默认交付流程：

1. `Spec`
2. `TDD`
3. `Execution`

执行要求：

- 未完成 spec 对齐前，不进入正式实现。
- Spec 阶段出现不确定/歧义/取舍问题必须先询问用户，禁止 AI 自己决定后继续推进。
- 默认存在“Spec 确认闸门”：非“小修小改”场景下，必须等待用户确认 Spec 后才能进入 TDD，且确认可进入 Execution 后才能正式编码（细则见 `.cursor/workflow_rules.md`）。
- 开始编码前，先总结当前生效规则、范围边界和验收标准。
- 优先复用现有目录、接口封装、返回结构和工具函数。
- `workflow_rules.md` 不能突破 `architecture.md` 的架构红线。
- 新增配置统一进入配置层，不得在业务模块散写硬编码地址、密钥和路径。
- 所有新增或修改的规范文件、设计文档、任务文档、交付说明统一使用中文。
- 所有新增或修改的代码注释统一使用中文；字段名、协议关键字、库名和第三方服务名可保留英文原文。

当前仓库基线：

- 项目：`TestHub` 智能测试管理平台
- 后端目录：`backend` + `apps`，Django 4.2 + Django REST Framework + MySQL + SimpleJWT + Channels + Celery
- 前端目录：`frontend`，Vue 3 + JavaScript + Vite + Pinia + Element Plus
- 后续 AI 能力必须通过统一入口接入，禁止在业务模块直接散接模型调用

# AutoTest 开发日志 (Changelog)

所有项目的重要变更将记录在此文件中。

## [2026-03-10 PM] - 治理与质量闭环：自动化草稿箱逻辑上线

### 新增功能
- **治理与质量闭环 (Governance & Quality Loop)**
  - 发布了规范文档：`008-m4-治理与质量闭环-第一刀.md` 及其配套的测试设计。
- **自动化草稿箱 (Automation Draft)**
  - 实现了自动化脚本的草稿存储、流程编排及持久化模型 (`views/automation_draft/`)。
  - 前端支持：新增了自动化草稿箱的管理页面及 API 封装。
- **AI 服务测试**
  - 补充了 AI 服务的单元测试脚本 (`tests/test_ai_service.py`)。

### 优化与调整
- **Web 自动化流程**：优化了 Web 视图的相关组件逻辑。
- **数据库配置**：微调了数据库初始化配置。

### 统计信息
- 改动文件数：25
- 代码增量：+3229 insertions
- 主要涉及路径：`l-tester-master/`, `l-vue-ui-master/`, `docs/specs/`

## [2026-03-10] - 大版本更新：AI 与需求用例中心上线

### 新增功能
- **AI 模块 (AI Gateway & Service)**
  - 实现了基于 FastAPI 的 AI 网关及服务层 (`views/ai/`)。
  - 支持 AI 配置管理及其配套的前端页面。
- **需求与用例中心 (Requirement & Testcase Center)**
  - 核心业务：实现了需求与用例的完整持久化逻辑 (`views/requirement/`, `views/testcase/`)。
  - 前端支持：新增需求管理页 (`requirement_view`) 和用例生成/管理页 (`testcase_view`)。
- **GitLab 集成**
  - 增加了 GitLab 通用工具类及相关接口支持 (`common/gitlab_utils.py`, `views/api/gitlab_common.py`)。

### 优化与调整
- **前端底座更新**
  - 优化了路由配置 (`staticRouter.ts`)，新增了多个业务模块入口。
  - 改进了存储工具 (`storage.ts`) 和路由过滤逻辑 (`filterRoute.ts`)。
- **系统配置**
  - 更新了后端 `config/settings.py`，增加了 AI 及相关服务的配置项。

### 统计信息
- 改动文件数：67
- 代码增量：+21988 insertions
- 主要涉及路径：`l-tester-master/`, `l-vue-ui-master/`

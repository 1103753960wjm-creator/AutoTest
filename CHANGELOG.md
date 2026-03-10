# AutoTest 开发日志 (Changelog)

所有项目的重要变更将记录在此文件中。

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

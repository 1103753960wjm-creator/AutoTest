# 前端 UI 样式指南

## 1. 文件职责

本文是前端 UI 样式指南的稳定入口，用于承接历史规划文档中的 `frontend-ui-style-guide.md` 引用。

当前前端 UI 一致化规则已经分散沉淀在以下正式规范中：

- [统一表格模板规范](../architecture/unified-table-template-spec.md)
- [页面壳规范](../architecture/page-shell-spec.md)
- [页面头部规范](../architecture/page-header-spec.md)
- [列表页规范](../architecture/list-page-spec.md)
- [统一状态规范](../architecture/ui-state-spec.md)

## 2. 当前硬规则摘要

- 列表筛选区统一进入 `ListShell #filters` 插槽。
- 筛选控件必须撑满所在列宽。
- 搜索、重置、主操作按钮的排版、位置、间距必须与平台标准页面保持一致。
- 登录后业务页面不得自行渲染平台级头部和导航结构。
- 页面状态优先使用统一状态组件，不在页面里散写相似空态、加载态和错误态。

## 3. 后续维护

如果后续需要完整前端 UI 样式指南，应在本文继续扩展，不再新增另一个平行入口。

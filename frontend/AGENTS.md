# TestHub Frontend 本地规则

## 1. 文件职责

本文文件属于目录级本地规则，仅约束 `frontend/**` 范围内的页面、组件、路由、状态与请求编排。

## 2. 进入前置

- 进入本目录开发前，先读取根目录 `AGENTS.md` 与 `.cursor/*.md`
- 本文件只补充前端局部规则，不覆盖全局流程与架构红线

## 3. 请求编排

- 所有后端请求统一通过 `frontend/src/api/*`
- 同一页面首屏数据优先通过单一 `refresh`、`load` 或等价入口收口
- `keepAlive` 页面禁止在 `onMounted`、`onActivated`、`watch` 中形成重复请求链

## 4. 分页与轮询

- 列表页默认走正常分页，不得用超大 `page_size` 或一次性全量拉取代替
- 轮询必须具备最小轮询间隔、终态停止、页面失焦暂停或降频、相同对象去重
- 同一任务或批次的状态轮询应尽量按 `taskId`、`batchId` 等主键收口，不在多个组件各自重复轮询

## 5. 路由与布局

- 涉及 route meta、导航守卫、布局壳、全局状态的改动视为高风险改动
- 新增 route meta 字段时，必须同步检查 `frontend/src/types/router-meta.d.ts` 与消费端
- 模块页面应优先复用统一页面壳、统一表格壳、统一状态壳，不重复造大体相同的页面骨架
- 登录后的业务页面在 `frontend/src/App.vue` 根层必须共用稳定 `layout:authenticated`，禁止按业务模块、物理顶层路由、`fullPath` 或 `params` 销毁整套平台壳
- `frontend/src/layout/index.vue` 内容层 `router-view` key 必须保持 `currentRoute.name || currentRoute.path`，并与 `<keep-alive :include="cachedViews">` 的路由名称维度一致
- 顶部模块、侧边栏、全局搜索、最近访问、收藏和用户资料入口必须统一走 Layout 导航调度器，不能分散直接 `router.push`
- 拆分或新增用户可见子模块时，必须同步 `frontend/src/config/navigation.js`、`frontend/src/router/index.js`、route meta、Dashboard 快捷入口、i18n 文案和相关文档；旧入口只能作为 `hidden + redirect + activeMenu` 兼容保留，不能继续作为可见入口。
- 页面必须遵守“前端样式 UI 一致化”规则：任何模块新增或改造搜索筛选组件时，必须与 `ProjectManagement.vue` 的搜索框、查询/重置按钮在排版、位置、间距（如 `el-row :gutter=16`，底部 margin 等）上保持绝对一致，不得随意引入 ad-hoc 的自定义摆放样式。

## 6. 表单与默认行为

- SPA 页面中的 `<form>` 与 Element Plus `<el-form>` 必须显式添加 `@submit.prevent`，禁止依赖浏览器默认提交行为。
- 原生 `<button>` 必须显式声明 `type="button"`；只有明确设计为表单提交按钮时才允许 `type="submit"`，并且必须有清晰的提交处理链路。
- 禁止用 Enter 键触发浏览器默认提交、当前 URL 重新请求或整页刷新来兜底业务动作。

## 7. 认证与导出

- 认证失效、退出登录、refresh token 失败回登录必须走 `frontend/src/utils/authNavigation.js`
- 禁止在 store、api 拦截器或页面中散写 `window.location.href`、`window.location.assign`、`location.reload` 作为登录跳转或导航兜底
- Excel 导出统一走 `frontend/src/utils/excelExport.js`，禁止新增 `xlsx` 依赖或在页面模板中直接引入 `XLSX`

## 8. 服务式组件样式

- 直接调用 Element Plus 服务式 API（如 `ElMessage`、`ElMessageBox`、`ElNotification`、`ElLoading`）时，必须确认对应样式已在 `frontend/src/main.js` 或统一样式入口引入。
- 当前已显式引入 `loading`、`message`、`message-box` 样式；后续新增其他服务式 API 时必须同步补对应 `element-plus/es/components/*/style/css`。
- 禁止在单个业务页面通过手写 `.el-message-box` 等覆盖样式来替代官方服务组件样式入口。

## 9. 最低验证要求

- 至少完成构建级、类型级或页面级验证中的一种
- 影响列表、详情、编辑、结果页主链路时，至少核对主流程与一个异常流程
- 影响 `App.vue`、`layout/index.vue`、侧边栏、认证跳转或路由 key 时，必须补跑顶部大模块 -> 侧边栏子模块快速切换，确认最终停在最后点击目标且无整页刷新事件

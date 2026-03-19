// 平台导航冻结真源。
// 说明：
// 1. 本文件用于承接“一级导航冻结和模块边界归类”方案。
// 2. children 表达的是“冻结后的归属真源”，不是当前 layout 的真实渲染结果。
// 3. 后续如果改造首页卡片、侧边栏、面包屑，应优先消费这里的配置。

export const NAV_ENTRY_STATUS = Object.freeze({
  KEEP: '保留入口',
  HIDE: '隐藏入口',
  FUTURE_MOVE: '未来迁移入口',
  RESERVED: '预留'
})

export const NAV_FREEZE_VERSION = '2026-03-11'

export const TOP_LEVEL_NAVIGATION = [
  {
    key: 'workbench',
    title: '工作台',
    route: '/home',
    status: '保留',
    description: '平台总览、快捷入口和轻工具入口。'
  },
  {
    key: 'test-design',
    title: '测试设计',
    route: '/ai-generation/requirement-analysis',
    status: '保留',
    description: '需求分析、项目、用例、评审、版本和设计资产。'
  },
  {
    key: 'api-automation',
    title: '接口自动化',
    route: '/api-testing/dashboard',
    status: '保留',
    description: '接口项目、接口调试和接口自动化执行工作台。'
  },
  {
    key: 'web-automation',
    title: 'Web 自动化',
    route: '/ui-automation/dashboard',
    status: '保留',
    description: 'Web UI 自动化和 AI Web 测试能力。'
  },
  {
    key: 'app-automation',
    title: 'App 自动化',
    route: '/app-automation/dashboard',
    status: '保留',
    description: 'App 自动化资产、编排与运行能力。'
  },
  {
    key: 'cloud-device',
    title: '云真机',
    route: '',
    status: '预留',
    description: '统一设备池、预约和远控能力。'
  },
  {
    key: 'execution-center',
    title: '执行中心',
    route: '',
    status: '预留',
    description: '平台级调度、执行、报告和通知日志。'
  },
  {
    key: 'data-factory',
    title: '数据工厂',
    route: '/data-factory',
    status: '保留',
    description: '通用测试数据和工具能力。'
  },
  {
    key: 'config-center',
    title: '配置中心',
    route: '/configuration/ai-model',
    status: '保留',
    description: '平台级 AI、环境、通知和接入配置。'
  },
  {
    key: 'system-management',
    title: '系统管理',
    route: '',
    status: '预留',
    description: '用户、角色、权限、个人资料和系统运维入口。'
  }
]

export const NAVIGATION_MODULES = [
  {
    key: 'workbench',
    title: '工作台',
    exactPaths: ['/home', '/ai-generation/assistant'],
    pathPrefixes: ['/home'],
    noNewRules: [
      '不新增业务资产管理页。',
      '不新增独立 AI 助手一级导航。'
    ],
    children: [
      {
        title: '平台首页',
        path: '/home',
        status: NAV_ENTRY_STATUS.KEEP,
        note: '平台统一门户。'
      },
      {
        title: 'AI 助手',
        path: '/ai-generation/assistant',
        status: NAV_ENTRY_STATUS.HIDE,
        note: '保留直达能力，不再作为独立一级导航增长。'
      }
    ]
  },
  {
    key: 'test-design',
    title: '测试设计',
    pathPrefixes: ['/ai-generation'],
    noNewRules: [
      '不新增平台级执行、报告、通知和系统页面。',
      '不继续把 AI 助手能力挂在本模块下扩张。'
    ],
    children: [
      { title: '需求分析', path: '/ai-generation/requirement-analysis', status: NAV_ENTRY_STATUS.KEEP },
      { title: 'AI 生成结果', path: '/ai-generation/generated-testcases', status: NAV_ENTRY_STATUS.KEEP },
      { title: '项目管理', path: '/ai-generation/projects', status: NAV_ENTRY_STATUS.KEEP },
      { title: '项目详情', path: '/ai-generation/projects/:id', status: NAV_ENTRY_STATUS.HIDE },
      { title: '测试用例列表', path: '/ai-generation/testcases', status: NAV_ENTRY_STATUS.KEEP },
      { title: '新建测试用例', path: '/ai-generation/testcases/create', status: NAV_ENTRY_STATUS.HIDE },
      { title: '测试用例详情', path: '/ai-generation/testcases/:id', status: NAV_ENTRY_STATUS.HIDE },
      { title: '编辑测试用例', path: '/ai-generation/testcases/:id/edit', status: NAV_ENTRY_STATUS.HIDE },
      { title: '版本管理', path: '/ai-generation/versions', status: NAV_ENTRY_STATUS.KEEP },
      { title: '评审列表', path: '/ai-generation/reviews', status: NAV_ENTRY_STATUS.KEEP },
      { title: '新建评审', path: '/ai-generation/reviews/create', status: NAV_ENTRY_STATUS.HIDE },
      { title: '评审详情', path: '/ai-generation/reviews/:id', status: NAV_ENTRY_STATUS.HIDE },
      { title: '编辑评审', path: '/ai-generation/reviews/:id/edit', status: NAV_ENTRY_STATUS.HIDE },
      { title: '评审模板', path: '/ai-generation/review-templates', status: NAV_ENTRY_STATUS.KEEP },
      { title: '测试套件', path: '/ai-generation/testsuites', status: NAV_ENTRY_STATUS.HIDE },
      { title: '分析任务详情', path: '/ai-generation/task-detail/:taskId', status: NAV_ENTRY_STATUS.HIDE }
    ]
  },
  {
    key: 'api-automation',
    title: '接口自动化',
    pathPrefixes: ['/api-testing'],
    noNewRules: [
      '不新增平台级配置页到本模块。',
      '不新增新的平台级报告、调度和通知聚合页。'
    ],
    children: [
      { title: '仪表盘', path: '/api-testing/dashboard', status: NAV_ENTRY_STATUS.KEEP },
      { title: '项目管理', path: '/api-testing/projects', status: NAV_ENTRY_STATUS.KEEP },
      { title: '接口管理', path: '/api-testing/interfaces', status: NAV_ENTRY_STATUS.KEEP },
      { title: '自动化测试', path: '/api-testing/automation', status: NAV_ENTRY_STATUS.KEEP },
      { title: '请求历史', path: '/api-testing/history', status: NAV_ENTRY_STATUS.KEEP },
      { title: '环境管理', path: '/api-testing/environments', status: NAV_ENTRY_STATUS.KEEP }
    ]
  },
  {
    key: 'web-automation',
    title: 'Web 自动化',
    pathPrefixes: ['/ui-automation', '/ai-intelligent-mode'],
    noNewRules: [
      '不再新增独立的 AI 智能模式一级导航。',
      '不新增新的平台级执行、报告和通知聚合页。'
    ],
    children: [
      { title: '仪表盘', path: '/ui-automation/dashboard', status: NAV_ENTRY_STATUS.KEEP },
      { title: '项目管理', path: '/ui-automation/projects', status: NAV_ENTRY_STATUS.KEEP },
      { title: '元素管理增强版', path: '/ui-automation/elements-enhanced', status: NAV_ENTRY_STATUS.KEEP },
      { title: '测试用例', path: '/ui-automation/test-cases', status: NAV_ENTRY_STATUS.KEEP },
      { title: '脚本生成 / 编辑', path: '/ui-automation/scripts-enhanced', status: NAV_ENTRY_STATUS.KEEP },
      { title: '脚本编辑器别名', path: '/ui-automation/scripts/editor', status: NAV_ENTRY_STATUS.HIDE },
      { title: '脚本列表', path: '/ui-automation/scripts', status: NAV_ENTRY_STATUS.KEEP },
      { title: '测试套件', path: '/ui-automation/suites', status: NAV_ENTRY_STATUS.KEEP },
      { title: 'AI 智能测试', path: '/ai-intelligent-mode/testing', status: NAV_ENTRY_STATUS.KEEP },
      { title: 'AI 用例列表', path: '/ai-intelligent-mode/cases', status: NAV_ENTRY_STATUS.KEEP }
    ]
  },
  {
    key: 'app-automation',
    title: 'App 自动化',
    pathPrefixes: ['/app-automation'],
    noNewRules: [
      '不新增平台级配置页到本模块。',
      '不新增新的平台级报告、调度和通知聚合页。'
    ],
    children: [
      { title: '仪表盘', path: '/app-automation/dashboard', status: NAV_ENTRY_STATUS.KEEP },
      { title: '项目管理', path: '/app-automation/projects', status: NAV_ENTRY_STATUS.KEEP },
      { title: '设备管理', path: '/app-automation/devices', status: NAV_ENTRY_STATUS.KEEP, note: '当设备池升级为跨业务资源时，再迁移到云真机。' },
      { title: '包名管理', path: '/app-automation/packages', status: NAV_ENTRY_STATUS.KEEP },
      { title: '元素管理', path: '/app-automation/elements', status: NAV_ENTRY_STATUS.KEEP },
      { title: '用例编排', path: '/app-automation/scene-builder', status: NAV_ENTRY_STATUS.KEEP },
      { title: '测试用例', path: '/app-automation/test-cases', status: NAV_ENTRY_STATUS.KEEP },
      { title: '测试套件', path: '/app-automation/test-suites', status: NAV_ENTRY_STATUS.KEEP }
    ]
  },
  {
    key: 'cloud-device',
    title: '云真机',
    pathPrefixes: [],
    noNewRules: [
      '在具备真实业务能力前，不先伪造页面和路由。',
      '设备运营能力准备成熟前，不把 App 自动化现有页面强行迁移过来。'
    ],
    children: [
      { title: '设备池总览', path: '', status: NAV_ENTRY_STATUS.RESERVED },
      { title: '设备预约 / 释放', path: '', status: NAV_ENTRY_STATUS.RESERVED },
      { title: '远程调试 / 远控', path: '', status: NAV_ENTRY_STATUS.RESERVED },
      { title: '应用安装 / 镜像管理', path: '', status: NAV_ENTRY_STATUS.RESERVED }
    ]
  },
  {
    key: 'execution-center',
    title: '执行中心',
    pathPrefixes: [],
    noNewRules: [
      '在正式落地前，不再新增新的跨模块执行聚合页面到业务模块里。',
      '新增平台级报告、调度和通知日志能力应优先预留到本模块。'
    ],
    children: [
      { title: '执行总览', path: '', status: NAV_ENTRY_STATUS.RESERVED },
      { title: '调度管理', path: '', status: NAV_ENTRY_STATUS.RESERVED },
      { title: '执行记录', path: '', status: NAV_ENTRY_STATUS.RESERVED },
      { title: '报告中心', path: '', status: NAV_ENTRY_STATUS.RESERVED },
      { title: '通知日志', path: '', status: NAV_ENTRY_STATUS.RESERVED },
      { title: '测试计划 / 执行列表', path: '/ai-generation/executions', status: NAV_ENTRY_STATUS.FUTURE_MOVE, source: '测试设计' },
      { title: '测试执行详情', path: '/ai-generation/executions/:id', status: NAV_ENTRY_STATUS.FUTURE_MOVE, source: '测试设计' },
      { title: 'AI 测试报告', path: '/ai-generation/reports', status: NAV_ENTRY_STATUS.FUTURE_MOVE, source: '测试设计' },
      { title: '接口测试报告', path: '/api-testing/reports', status: NAV_ENTRY_STATUS.FUTURE_MOVE, source: '接口自动化' },
      { title: '接口定时任务', path: '/api-testing/scheduled-tasks', status: NAV_ENTRY_STATUS.FUTURE_MOVE, source: '接口自动化' },
      { title: '接口通知日志', path: '/api-testing/notification-logs', status: NAV_ENTRY_STATUS.FUTURE_MOVE, source: '接口自动化' },
      { title: 'Web 执行记录', path: '/ui-automation/executions', status: NAV_ENTRY_STATUS.FUTURE_MOVE, source: 'Web 自动化' },
      { title: 'Web 测试报告', path: '/ui-automation/reports', status: NAV_ENTRY_STATUS.FUTURE_MOVE, source: 'Web 自动化' },
      { title: 'Web 定时任务', path: '/ui-automation/scheduled-tasks', status: NAV_ENTRY_STATUS.FUTURE_MOVE, source: 'Web 自动化' },
      { title: 'Web 通知日志', path: '/ui-automation/notification-logs', status: NAV_ENTRY_STATUS.FUTURE_MOVE, source: 'Web 自动化' },
      { title: 'AI 执行记录', path: '/ai-intelligent-mode/execution-records', status: NAV_ENTRY_STATUS.FUTURE_MOVE, source: 'Web 自动化' },
      { title: 'App 执行记录', path: '/app-automation/executions', status: NAV_ENTRY_STATUS.FUTURE_MOVE, source: 'App 自动化' },
      { title: 'App 测试报告', path: '/app-automation/reports', status: NAV_ENTRY_STATUS.FUTURE_MOVE, source: 'App 自动化' },
      { title: 'App 定时任务', path: '/app-automation/scheduled-tasks', status: NAV_ENTRY_STATUS.FUTURE_MOVE, source: 'App 自动化' },
      { title: 'App 通知日志', path: '/app-automation/notification-logs', status: NAV_ENTRY_STATUS.FUTURE_MOVE, source: 'App 自动化' }
    ]
  },
  {
    key: 'data-factory',
    title: '数据工厂',
    pathPrefixes: ['/data-factory'],
    noNewRules: [
      '不新增与数据工具无关的业务页面。'
    ],
    children: [
      { title: '数据工厂', path: '/data-factory', status: NAV_ENTRY_STATUS.KEEP }
    ]
  },
  {
    key: 'config-center',
    title: '配置中心',
    pathPrefixes: ['/configuration'],
    noNewRules: [
      '平台级配置优先收敛到本模块。',
      '不继续把平台级 AI 配置、通知配置散落到业务模块。'
    ],
    children: [
      { title: 'AI 模型配置', path: '/configuration/ai-model', status: NAV_ENTRY_STATUS.KEEP },
      { title: '提示词配置', path: '/configuration/prompt-config', status: NAV_ENTRY_STATUS.KEEP },
      { title: '生成配置', path: '/configuration/generation-config', status: NAV_ENTRY_STATUS.KEEP },
      { title: 'UI 环境配置', path: '/configuration/ui-env', status: NAV_ENTRY_STATUS.KEEP },
      { title: 'App 环境配置', path: '/configuration/app-env', status: NAV_ENTRY_STATUS.KEEP },
      { title: 'AI 智能模式配置', path: '/configuration/ai-mode', status: NAV_ENTRY_STATUS.KEEP },
      { title: '通知通道配置', path: '/configuration/scheduled-task', status: NAV_ENTRY_STATUS.KEEP, note: '当前路由名沿用历史命名，后续应更名。' },
      { title: 'Dify 配置', path: '/configuration/dify', status: NAV_ENTRY_STATUS.KEEP },
      { title: 'API AI 服务配置', path: '/api-testing/ai-service-config', status: NAV_ENTRY_STATUS.FUTURE_MOVE, source: '接口自动化' }
    ]
  },
  {
    key: 'system-management',
    title: '系统管理',
    exactPaths: ['/login', '/register', '/admin/'],
    pathPrefixes: [],
    noNewRules: [
      '不再新增新的系统页到 /ai-generation 下。',
      '认证入口不进入登录后一级导航。',
      '治理类日志固定进入系统管理，不进入业务模块或配置中心。'
    ],
    children: [
      { title: '个人资料', path: '/ai-generation/profile', status: NAV_ENTRY_STATUS.FUTURE_MOVE, target: '系统管理' },
      { title: '登录', path: '/login', status: NAV_ENTRY_STATUS.HIDE },
      { title: '注册', path: '/register', status: NAV_ENTRY_STATUS.HIDE },
      { title: 'Django Admin', path: '/admin/', status: NAV_ENTRY_STATUS.HIDE },
      { title: '用户 / 角色 / 权限', path: '', status: NAV_ENTRY_STATUS.RESERVED },
      { title: '登录日志', path: '', status: NAV_ENTRY_STATUS.RESERVED, note: '后续承接认证行为与会话治理日志。' },
      { title: '操作日志', path: '', status: NAV_ENTRY_STATUS.RESERVED, note: '后续统一承接 API / Web 等模块操作记录。' },
      { title: '审计日志', path: '', status: NAV_ENTRY_STATUS.RESERVED, note: '后续承接权限、平台参数和治理审计。' },
      { title: 'AI 调用审计', path: '', status: NAV_ENTRY_STATUS.RESERVED, note: '后续承接模型调用、成本、失败原因和调用来源。' }
    ]
  }
]

const matchByPrefix = (path, prefix) => path === prefix || path.startsWith(`${prefix}/`)

const matchChildPath = (path, childPath) => {
  if (!childPath) {
    return false
  }

  const dynamicIndex = childPath.indexOf('/:')
  if (dynamicIndex !== -1) {
    const basePath = childPath.slice(0, dynamicIndex)
    return matchByPrefix(path, basePath)
  }

  return path === childPath
}

export function findFrozenModuleByPath(path) {
  for (const module of NAVIGATION_MODULES) {
    if (module.children.some((child) => matchChildPath(path, child.path))) {
      return module
    }
  }

  for (const module of NAVIGATION_MODULES) {
    if ((module.exactPaths || []).includes(path)) {
      return module
    }
  }

  for (const module of NAVIGATION_MODULES) {
    if ((module.pathPrefixes || []).some((prefix) => matchByPrefix(path, prefix))) {
      return module
    }
  }

  return null
}




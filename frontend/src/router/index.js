import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useProductivityStore } from '@/stores/productivity'
import { usePlatformSearchStore } from '@/stores/platform-search'
import { createRouteMeta, getDocumentTitle } from './route-meta'

import Login from '@/views/auth/Login.vue'
import Register from '@/views/auth/Register.vue'
import Layout from '@/layout/index.vue'
import ProjectList from '@/views/projects/ProjectList.vue'
import Home from '@/views/Home.vue'
import DataFactory from '@/views/data-factory/DataFactory.vue'
import ApiDashboard from '@/views/api-testing/Dashboard.vue'
import ApiProjectManagement from '@/views/api-testing/ProjectManagement.vue'
import ApiInterfaceManagement from '@/views/api-testing/InterfaceManagement.vue'
import ApiAutomationTesting from '@/views/api-testing/AutomationTesting.vue'
import ApiRequestHistory from '@/views/api-testing/RequestHistory.vue'
import ApiEnvironmentManagement from '@/views/api-testing/EnvironmentManagement.vue'
import ApiReportView from '@/views/api-testing/ReportView.vue'
import ApiScheduledTasks from '@/views/api-testing/ScheduledTasks.vue'
import ApiAIServiceConfig from '@/views/api-testing/AIServiceConfig.vue'
import NotificationLogs from '@/views/notification/NotificationLogs.vue'
import UiDashboard from '@/views/ui-automation/dashboard/Dashboard.vue'
import UiProjectList from '@/views/ui-automation/projects/ProjectList.vue'
import UiElementManagerEnhanced from '@/views/ui-automation/elements/ElementManagerEnhanced.vue'
import UiTestCaseManager from '@/views/ui-automation/test-cases/TestCaseManager.vue'
import UiScriptEditorEnhanced from '@/views/ui-automation/scripts/ScriptEditorEnhanced.vue'
import UiScriptList from '@/views/ui-automation/scripts/ScriptList.vue'
import UiSuiteList from '@/views/ui-automation/suites/SuiteList.vue'
import UiExecutionList from '@/views/ui-automation/executions/ExecutionList.vue'
import UiReportList from '@/views/ui-automation/reports/ReportList.vue'
import UiScheduledTasks from '@/views/ui-automation/scheduled-tasks/ScheduledTasks.vue'
import UiNotificationLogs from '@/views/ui-automation/notification/NotificationLogs.vue'
import UiAITesting from '@/views/ui-automation/ai/AITesting.vue'
import UiAICaseList from '@/views/ui-automation/ai/AICaseList.vue'
import UiAIExecutionRecords from '@/views/ui-automation/ai/AIExecutionRecords.vue'

/** @type {import('vue-router').RouteRecordRaw[]} */
const routes = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/',
    component: Layout,
    meta: createRouteMeta({
      requiresAuth: true,
      module: 'workbench',
      hidden: true
    }),
    children: [
      {
        path: 'home',
        name: 'Home',
        component: Home,
        meta: createRouteMeta({
          requiresAuth: true,
          title: '工作台',
          description: '平台工作台首页，承接继续工作、模块入口和轻量提醒。',
          module: 'workbench',
          pageType: 'dashboard',
          icon: 'house'
        })
      },
      {
        path: 'ai-generation/assistant',
        name: 'Assistant',
        component: () => import('@/views/assistant/AssistantView.vue'),
        meta: createRouteMeta({
          requiresAuth: true,
          title: 'AI 助手',
          module: 'workbench',
          pageType: 'workspace',
          icon: 'chat',
          hidden: true,
          keepAlive: true
        })
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: createRouteMeta({
      requiresGuest: true,
      title: '登录',
      module: 'system-management',
      pageType: 'auth',
      icon: 'login',
      hidden: true
    })
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: createRouteMeta({
      requiresGuest: true,
      title: '注册',
      module: 'system-management',
      pageType: 'auth',
      icon: 'user-plus',
      hidden: true
    })
  },

  {
    path: '/ai-generation',
    component: Layout,
    meta: createRouteMeta({
      requiresAuth: true,
      module: 'test-design',
      hidden: true
    }),
    children: [
      {
        path: '',
        redirect: 'requirement-analysis'
      },
      {
        path: 'requirement-analysis',
        name: 'RequirementAnalysis',
        component: () => import('@/views/requirement-analysis/RequirementAnalysisView.vue'),
        meta: createRouteMeta({
          title: '需求分析',
          description: '围绕需求输入、分析对象和生成任务入口管理测试设计源头信息。',
          module: 'test-design',
          pageType: 'workspace',
          icon: 'sparkles',
          keepAlive: true
        })
      },
      {
        path: 'projects',
        name: 'Projects',
        component: ProjectList,
        meta: createRouteMeta({
          title: '项目管理',
          description: '统一管理测试设计项目资产，并承接创建、筛选和状态维护。',
          module: 'test-design',
          pageType: 'list',
          icon: 'folder'
        })
      },
      {
        path: 'projects/:id',
        name: 'ProjectDetail',
        component: () => import('@/views/projects/ProjectDetail.vue'),
        meta: createRouteMeta({
          title: '项目详情',
          description: '作为测试设计源头对象页，查看项目摘要、需求分析、AI 生成与测试资产关系。',
          module: 'test-design',
          pageType: 'detail-result',
          icon: 'folder-opened',
          hidden: true,
          parentTitle: '项目管理',
          activeMenu: '/ai-generation/projects'
        })
      },
      {
        path: 'testcases',
        name: 'TestCases',
        component: () => import('@/views/testcases/TestCaseList.vue'),
        meta: createRouteMeta({
          title: '测试用例',
          description: '统一管理测试设计资产，并查看来源、优先级和自动化预留状态。',
          module: 'test-design',
          pageType: 'list',
          icon: 'document'
        })
      },
      {
        path: 'testcases/create',
        name: 'CreateTestCase',
        component: () => import('@/views/testcases/TestCaseForm.vue'),
        meta: createRouteMeta({
          title: '新建测试用例',
          module: 'test-design',
          pageType: 'workspace',
          icon: 'plus',
          hidden: true,
          parentTitle: '测试用例',
          activeMenu: '/ai-generation/testcases'
        })
      },
      {
        path: 'testcases/:id',
        name: 'TestCaseDetail',
        component: () => import('@/views/testcases/TestCaseDetail.vue'),
        meta: createRouteMeta({
          title: '测试用例详情',
          description: '作为测试设计资产详情页，查看内容、来源摘要和自动化挂接位。',
          module: 'test-design',
          pageType: 'detail-result',
          icon: 'tickets',
          hidden: true,
          parentTitle: '测试用例',
          activeMenu: '/ai-generation/testcases'
        })
      },
      {
        path: 'testcases/:id/edit',
        name: 'EditTestCase',
        component: () => import('@/views/testcases/TestCaseEdit.vue'),
        meta: createRouteMeta({
          title: '编辑测试用例',
          description: '在明确所属项目与回跳上下文的前提下编辑测试设计资产。',
          module: 'test-design',
          pageType: 'workspace',
          icon: 'edit',
          hidden: true,
          parentTitle: '测试用例',
          activeMenu: '/ai-generation/testcases'
        })
      },
      {
        path: 'versions',
        name: 'Versions',
        component: () => import('@/views/versions/VersionList.vue'),
        meta: createRouteMeta({
          title: '版本管理',
          module: 'test-design',
          pageType: 'list',
          icon: 'flag'
        })
      },
      {
        path: 'reviews',
        name: 'Reviews',
        component: () => import('@/views/reviews/ReviewList.vue'),
        meta: createRouteMeta({
          title: '评审列表',
          module: 'test-design',
          pageType: 'list',
          icon: 'check'
        })
      },
      {
        path: 'reviews/ai-auto',
        name: 'AutoReviewList',
        component: () => import('@/views/reviews/AutoReviewList.vue'),
        meta: createRouteMeta({
          title: 'AI 自动评审',
          module: 'test-design',
          pageType: 'list',
          icon: 'magic-stick',
          hidden: true,
          parentTitle: '评审列表',
          activeMenu: '/ai-generation/reviews'
        })
      },
      {
        path: 'reviews/create',
        name: 'CreateReview',
        component: () => import('@/views/reviews/ReviewForm.vue'),
        meta: createRouteMeta({
          title: '新建评审',
          module: 'test-design',
          pageType: 'workspace',
          icon: 'plus',
          hidden: true,
          parentTitle: '评审列表',
          activeMenu: '/ai-generation/reviews'
        })
      },
      {
        path: 'reviews/:id',
        name: 'ReviewDetail',
        component: () => import('@/views/reviews/ReviewDetail.vue'),
        meta: createRouteMeta({
          title: '评审详情',
          module: 'test-design',
          pageType: 'detail-result',
          icon: 'view',
          hidden: true,
          parentTitle: '评审列表',
          activeMenu: '/ai-generation/reviews'
        })
      },
      {
        path: 'reviews/:id/edit',
        name: 'EditReview',
        component: () => import('@/views/reviews/ReviewForm.vue'),
        meta: createRouteMeta({
          title: '编辑评审',
          module: 'test-design',
          pageType: 'workspace',
          icon: 'edit',
          hidden: true,
          parentTitle: '评审列表',
          activeMenu: '/ai-generation/reviews'
        })
      },
      {
        path: 'review-templates',
        name: 'ReviewTemplates',
        component: () => import('@/views/reviews/ReviewTemplateList.vue'),
        meta: createRouteMeta({
          title: '评审模板',
          module: 'test-design',
          pageType: 'list',
          icon: 'collection'
        })
      },
      {
        path: 'testsuites',
        name: 'TestSuites',
        component: () => import('@/views/testsuites/TestSuiteList.vue'),
        meta: createRouteMeta({
          title: '测试套件',
          module: 'test-design',
          pageType: 'list',
          icon: 'folder-opened'
        })
      },
      {
        path: 'executions',
        name: 'Executions',
        component: () => import('@/views/executions/ExecutionListView.vue'),
        meta: createRouteMeta({
          title: '测试计划',
          module: 'test-design',
          pageType: 'list',
          icon: 'video-play'
        })
      },
      {
        path: 'executions/:id',
        name: 'ExecutionDetail',
        component: () => import('@/views/executions/ExecutionDetailView.vue'),
        meta: createRouteMeta({
          title: '执行详情',
          description: '查看测试执行结果，并预留设计来源与自动化来源展示位。',
          module: 'test-design',
          pageType: 'detail-result',
          icon: 'data-analysis',
          hidden: true,
          parentTitle: '测试计划',
          activeMenu: '/ai-generation/executions'
        })
      },
      {
        path: 'reports',
        name: 'AiTestReport',
        component: () => import('@/views/reports/AiTestReport.vue'),
        meta: createRouteMeta({
          title: 'AI 测试报告',
          module: 'test-design',
          pageType: 'detail-result',
          icon: 'data-analysis'
        })
      },
      {
        path: 'generated-testcases',
        name: 'GeneratedTestCases',
        component: () => import('@/views/requirement-analysis/GeneratedTestCaseList.vue'),
        meta: createRouteMeta({
          title: 'AI 生成用例',
          description: '按结果批次查看 AI 生成产物、保存状态与来源任务。',
          module: 'test-design',
          pageType: 'list',
          icon: 'magic-stick'
        })
      },
      {
        path: 'task-detail/:taskId',
        name: 'TaskDetail',
        component: () => import('@/views/requirement-analysis/TaskDetail.vue'),
        meta: createRouteMeta({
          title: '任务详情',
          description: '作为生成任务对象页，查看来源项目、配置摘要、结果数量与保存状态。',
          module: 'test-design',
          pageType: 'detail-result',
          icon: 'timer',
          hidden: true,
          parentTitle: '需求分析',
          activeMenu: '/ai-generation/requirement-analysis'
        })
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/profile/UserProfile.vue'),
        meta: createRouteMeta({
          title: '个人资料',
          module: 'system-management',
          pageType: 'detail-result',
          icon: 'user',
          hidden: true,
          parentTitle: '系统管理'
        })
      }
    ]
  },
  {
    path: '/api-testing',
    component: Layout,
    meta: createRouteMeta({
      requiresAuth: true,
      module: 'api-automation',
      hidden: true
    }),
    children: [
      {
        path: '',
        redirect: 'dashboard'
      },
      {
        path: 'dashboard',
        name: 'ApiDashboard',
        component: ApiDashboard,
        meta: createRouteMeta({
          title: '接口自动化总览',
          description: '统一查看接口自动化项目、接口资产与近期操作动态。',
          module: 'api-automation',
          pageType: 'dashboard',
          icon: 'odometer'
        })
      },
      {
        path: 'projects',
        name: 'ApiProjects',
        component: ApiProjectManagement,
        meta: createRouteMeta({
          title: '项目管理',
          module: 'api-automation',
          pageType: 'list',
          icon: 'folder'
        })
      },
      {
        path: 'interfaces',
        name: 'ApiInterfaces',
        component: ApiInterfaceManagement,
        meta: createRouteMeta({
          title: '接口管理',
          module: 'api-automation',
          pageType: 'workspace',
          icon: 'link',
          keepAlive: true
        })
      },
      {
        path: 'automation',
        name: 'ApiAutomation',
        component: ApiAutomationTesting,
        meta: createRouteMeta({
          title: '自动化测试',
          module: 'api-automation',
          pageType: 'workspace',
          icon: 'video-play'
        })
      },
      {
        path: 'history',
        name: 'ApiHistory',
        component: ApiRequestHistory,
        meta: createRouteMeta({
          title: '请求历史',
          module: 'api-automation',
          pageType: 'detail-result',
          icon: 'timer'
        })
      },
      {
        path: 'environments',
        name: 'ApiEnvironments',
        component: ApiEnvironmentManagement,
        meta: createRouteMeta({
          title: '环境管理',
          module: 'api-automation',
          pageType: 'list',
          icon: 'setting'
        })
      },
      {
        path: 'reports',
        name: 'ApiReports',
        component: ApiReportView,
        meta: createRouteMeta({
          title: '测试报告',
          module: 'api-automation',
          pageType: 'detail-result',
          icon: 'data-analysis'
        })
      },
      {
        path: 'scheduled-tasks',
        name: 'ApiScheduledTasks',
        component: ApiScheduledTasks,
        meta: createRouteMeta({
          title: '定时任务',
          module: 'api-automation',
          pageType: 'list',
          icon: 'alarm-clock'
        })
      },
      {
        path: 'ai-service-config',
        name: 'ApiAIServiceConfig',
        component: ApiAIServiceConfig,
        meta: createRouteMeta({
          title: 'AI 服务配置',
          module: 'config-center',
          pageType: 'config',
          icon: 'cpu',
          parentTitle: '配置中心'
        })
      },
      {
        path: 'notification-logs',
        name: 'ApiNotificationLogs',
        component: NotificationLogs,
        meta: createRouteMeta({
          title: '通知日志',
          module: 'api-automation',
          pageType: 'detail-result',
          icon: 'bell'
        })
      }
    ]
  },
  {
    path: '/ui-automation',
    component: Layout,
    meta: createRouteMeta({
      requiresAuth: true,
      module: 'web-automation',
      hidden: true
    }),
    children: [
      {
        path: '',
        redirect: 'dashboard'
      },
      {
        path: 'dashboard',
        name: 'UiDashboard',
        component: UiDashboard,
        meta: createRouteMeta({
          title: 'Web 自动化总览',
          module: 'web-automation',
          pageType: 'dashboard',
          icon: 'monitor'
        })
      },
      {
        path: 'projects',
        name: 'UiProjects',
        component: UiProjectList,
        meta: createRouteMeta({
          title: '项目管理',
          module: 'web-automation',
          pageType: 'list',
          icon: 'folder'
        })
      },
      {
        path: 'elements-enhanced',
        name: 'UiElementsEnhanced',
        component: UiElementManagerEnhanced,
        meta: createRouteMeta({
          title: '元素管理',
          module: 'web-automation',
          pageType: 'workspace',
          icon: 'aim'
        })
      },
      {
        path: 'test-cases',
        name: 'UiTestCases',
        component: UiTestCaseManager,
        meta: createRouteMeta({
          title: '测试用例',
          module: 'web-automation',
          pageType: 'list',
          icon: 'document'
        })
      },
      {
        path: 'scripts-enhanced',
        name: 'UiScriptsEnhanced',
        component: UiScriptEditorEnhanced,
        meta: createRouteMeta({
          title: '脚本生成',
          module: 'web-automation',
          pageType: 'workspace',
          icon: 'edit',
          keepAlive: true
        })
      },
      {
        path: 'scripts/editor',
        name: 'UiScriptEditor',
        component: UiScriptEditorEnhanced,
        meta: createRouteMeta({
          title: '脚本编辑器',
          module: 'web-automation',
          pageType: 'workspace',
          icon: 'edit',
          hidden: true,
          keepAlive: true,
          parentTitle: '脚本生成',
          activeMenu: '/ui-automation/scripts-enhanced'
        })
      },
      {
        path: 'scripts',
        name: 'UiScripts',
        component: UiScriptList,
        meta: createRouteMeta({
          title: '脚本列表',
          module: 'web-automation',
          pageType: 'list',
          icon: 'document-copy'
        })
      },
      {
        path: 'suites',
        name: 'UiSuites',
        component: UiSuiteList,
        meta: createRouteMeta({
          title: '测试套件',
          module: 'web-automation',
          pageType: 'list',
          icon: 'collection'
        })
      },
      {
        path: 'executions',
        name: 'UiExecutions',
        component: UiExecutionList,
        meta: createRouteMeta({
          title: '执行记录',
          module: 'web-automation',
          pageType: 'detail-result',
          icon: 'video-play'
        })
      },
      {
        path: 'reports',
        name: 'UiReports',
        component: UiReportList,
        meta: createRouteMeta({
          title: '测试报告',
          module: 'web-automation',
          pageType: 'detail-result',
          icon: 'data-analysis'
        })
      },
      {
        path: 'scheduled-tasks',
        name: 'UiScheduledTasks',
        component: UiScheduledTasks,
        meta: createRouteMeta({
          title: '定时任务',
          module: 'web-automation',
          pageType: 'list',
          icon: 'alarm-clock'
        })
      },
      {
        path: 'notification-logs',
        name: 'UiNotificationLogs',
        component: UiNotificationLogs,
        meta: createRouteMeta({
          title: '通知日志',
          module: 'web-automation',
          pageType: 'detail-result',
          icon: 'bell'
        })
      }
    ]
  },
  {
    path: '/ai-intelligent-mode',
    component: Layout,
    meta: createRouteMeta({
      requiresAuth: true,
      module: 'web-automation',
      hidden: true
    }),
    children: [
      {
        path: '',
        redirect: 'testing'
      },
      {
        path: 'testing',
        name: 'AITesting',
        component: UiAITesting,
        meta: createRouteMeta({
          title: 'AI 智能测试',
          module: 'web-automation',
          pageType: 'workspace',
          icon: 'magic-stick',
          parentTitle: 'AI 智能模式'
        })
      },
      {
        path: 'cases',
        name: 'AICaseList',
        component: UiAICaseList,
        meta: createRouteMeta({
          title: 'AI 用例列表',
          module: 'web-automation',
          pageType: 'list',
          icon: 'document',
          parentTitle: 'AI 智能模式'
        })
      },
      {
        path: 'execution-records',
        name: 'AIExecutionRecords',
        component: UiAIExecutionRecords,
        meta: createRouteMeta({
          title: 'AI 执行记录',
          module: 'web-automation',
          pageType: 'detail-result',
          icon: 'timer',
          parentTitle: 'AI 智能模式'
        })
      }
    ]
  },
  {
    path: '/data-factory',
    name: 'DataFactory',
    component: DataFactory,
    meta: createRouteMeta({
      requiresAuth: true,
      title: '数据工厂',
      module: 'data-factory',
      pageType: 'workspace',
      icon: 'data-line',
      keepAlive: true
    })
  },
  {
    path: '/configuration',
    component: Layout,
    meta: createRouteMeta({
      requiresAuth: true,
      module: 'config-center',
      hidden: true
    }),
    children: [
      {
        path: '',
        component: () => import('@/views/configuration/ConfigurationCenter.vue'),
        meta: createRouteMeta({
          module: 'config-center',
          hidden: true
        }),
        children: [
          {
            path: '',
            redirect: 'ai-model'
          },
          {
            path: 'ai-model',
            name: 'ConfigAIModel',
            component: () => import('@/views/requirement-analysis/AIModelConfig.vue'),
            meta: createRouteMeta({
              title: 'AI 模型配置',
              module: 'config-center',
              pageType: 'config',
              icon: 'cpu'
            })
          },
          {
            path: 'prompt-config',
            name: 'ConfigPromptConfig',
            component: () => import('@/views/requirement-analysis/PromptConfig.vue'),
            meta: createRouteMeta({
              title: '提示词配置',
              module: 'config-center',
              pageType: 'config',
              icon: 'edit'
            })
          },
          {
            path: 'generation-config',
            name: 'ConfigGenerationConfig',
            component: () => import('@/views/requirement-analysis/GenerationConfigView.vue'),
            meta: createRouteMeta({
              title: '生成配置',
              module: 'config-center',
              pageType: 'config',
              icon: 'setting'
            })
          },
          {
            path: 'ui-env',
            name: 'ConfigUIEnv',
            component: () => import('@/views/configuration/UIEnvironmentConfig.vue'),
            meta: createRouteMeta({
              title: 'UI 环境配置',
              module: 'config-center',
              pageType: 'config',
              icon: 'monitor'
            })
          },
          {
            path: 'app-env',
            name: 'ConfigAppEnv',
            component: () => import('@/views/app-automation/settings/AppSettings.vue'),
            meta: createRouteMeta({
              title: 'App 环境配置',
              module: 'config-center',
              pageType: 'config',
              icon: 'cellphone'
            })
          },
          {
            path: 'ai-mode',
            name: 'ConfigAIMode',
            component: () => import('@/views/configuration/AIIntelligentModeConfig.vue'),
            meta: createRouteMeta({
              title: 'AI 智能模式配置',
              module: 'config-center',
              pageType: 'config',
              icon: 'magic-stick'
            })
          },
          {
            path: 'scheduled-task',
            name: 'ConfigScheduledTask',
            component: () => import('@/views/ui-automation/notification/NotificationConfigs.vue'),
            meta: createRouteMeta({
              title: '通知通道配置',
              module: 'config-center',
              pageType: 'config',
              icon: 'bell'
            })
          },
          {
            path: 'dify',
            name: 'DifyConfig',
            component: () => import('@/views/configuration/DifyConfig.vue'),
            meta: createRouteMeta({
              title: 'Dify 配置',
              module: 'config-center',
              pageType: 'config',
              icon: 'chat'
            })
          }
        ]
      }
    ]
  },
  {
    path: '/app-automation',
    component: Layout,
    meta: createRouteMeta({
      requiresAuth: true,
      module: 'app-automation',
      hidden: true
    }),
    children: [
      {
        path: '',
        redirect: 'dashboard'
      },
      {
        path: 'dashboard',
        name: 'AppAutomationDashboard',
        component: () => import('@/views/app-automation/dashboard/Dashboard.vue'),
        meta: createRouteMeta({
          title: 'App 自动化总览',
          module: 'app-automation',
          pageType: 'dashboard',
          icon: 'cellphone'
        })
      },
      {
        path: 'projects',
        name: 'AppProjectList',
        component: () => import('@/views/app-automation/projects/ProjectList.vue'),
        meta: createRouteMeta({
          title: '项目管理',
          module: 'app-automation',
          pageType: 'list',
          icon: 'folder'
        })
      },
      {
        path: 'devices',
        name: 'AppDeviceList',
        component: () => import('@/views/app-automation/devices/DeviceList.vue'),
        meta: createRouteMeta({
          title: '设备管理',
          module: 'app-automation',
          pageType: 'list',
          icon: 'cellphone'
        })
      },
      {
        path: 'packages',
        name: 'AppPackageList',
        component: () => import('@/views/app-automation/packages/PackageList.vue'),
        meta: createRouteMeta({
          title: '包名管理',
          module: 'app-automation',
          pageType: 'list',
          icon: 'collection'
        })
      },
      {
        path: 'elements',
        name: 'AppElementList',
        component: () => import('@/views/app-automation/elements/ElementList.vue'),
        meta: createRouteMeta({
          title: '元素管理',
          module: 'app-automation',
          pageType: 'workspace',
          icon: 'aim'
        })
      },
      {
        path: 'scene-builder',
        name: 'AppSceneBuilder',
        component: () => import('@/views/app-automation/test-cases/SceneBuilder.vue'),
        meta: createRouteMeta({
          title: '用例编排',
          module: 'app-automation',
          pageType: 'workspace',
          icon: 'connection',
          keepAlive: true
        })
      },
      {
        path: 'test-cases',
        name: 'AppTestCaseList',
        component: () => import('@/views/app-automation/test-cases/TestCaseList.vue'),
        meta: createRouteMeta({
          title: '测试用例',
          module: 'app-automation',
          pageType: 'list',
          icon: 'document'
        })
      },
      {
        path: 'test-suites',
        name: 'AppTestSuiteList',
        component: () => import('@/views/app-automation/suites/SuiteList.vue'),
        meta: createRouteMeta({
          title: '测试套件',
          module: 'app-automation',
          pageType: 'list',
          icon: 'folder-opened'
        })
      },
      {
        path: 'scheduled-tasks',
        name: 'AppScheduledTasks',
        component: () => import('@/views/app-automation/scheduled-tasks/ScheduledTasks.vue'),
        meta: createRouteMeta({
          title: '定时任务',
          module: 'app-automation',
          pageType: 'list',
          icon: 'alarm-clock'
        })
      },
      {
        path: 'notification-logs',
        name: 'AppNotificationLogs',
        component: () => import('@/views/app-automation/notification/NotificationLogs.vue'),
        meta: createRouteMeta({
          title: '通知日志',
          module: 'app-automation',
          pageType: 'detail-result',
          icon: 'bell'
        })
      },
      {
        path: 'executions',
        name: 'AppExecutionList',
        component: () => import('@/views/app-automation/executions/ExecutionList.vue'),
        meta: createRouteMeta({
          title: '执行记录',
          module: 'app-automation',
          pageType: 'detail-result',
          icon: 'video-play'
        })
      },
      {
        path: 'reports',
        name: 'AppReportList',
        component: () => import('@/views/app-automation/reports/ReportList.vue'),
        meta: createRouteMeta({
          title: '测试报告',
          module: 'app-automation',
          pageType: 'detail-result',
          icon: 'data-analysis'
        })
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()

  console.log('路由守卫:', {
    to: to.path,
    from: from.path,
    hasToken: !!userStore.accessToken,
    hasUser: !!userStore.user,
    isAuthenticated: userStore.isAuthenticated
  })

  if (!userStore.user && userStore.accessToken) {
    try {
      console.log('初始化认证...')
      await userStore.initAuth()
      console.log('认证初始化完成:', {
        hasUser: !!userStore.user,
        isAuthenticated: userStore.isAuthenticated
      })
    } catch (error) {
      console.error('认证初始化失败:', error)
    }
  }

  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    console.log('需要认证但未认证，跳转到登录页')
    next('/login')
  } else if (to.meta.requiresGuest && userStore.isAuthenticated) {
    console.log('访客页面但已认证，跳转到项目页')
    next('/home')
  } else {
    console.log('路由守卫通过，继续导航')
    next()
  }
})

router.afterEach((to, from) => {
  const productivityStore = useProductivityStore()
  const platformSearchStore = usePlatformSearchStore()
  productivityStore.recordVisit(to)
  platformSearchStore.closeSearch()
  document.title = getDocumentTitle(to)
  console.log(`Navigated from ${from.path} to ${to.path}`)
})

export default router



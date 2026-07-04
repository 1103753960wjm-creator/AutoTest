import request from '@/utils/api'

// 仪表盘相关API
export function getDashboardStats() {
  return request({
    url: '/api-testing/dashboard/stats/',
    method: 'get'
  })
}

// 获取定时任务列表
export function getScheduledTasks(params) {
  return request({
    url: '/api-testing/scheduled-tasks/',
    method: 'get',
    params
  })
}

// 创建定时任务
export function createScheduledTask(data) {
  return request({
    url: '/api-testing/scheduled-tasks/',
    method: 'post',
    data
  })
}

// 更新定时任务
export function updateScheduledTask(id, data) {
  return request({
    url: `/api-testing/scheduled-tasks/${id}/`,
    method: 'patch',
    data
  })
}

// 删除定时任务
export function deleteScheduledTask(id) {
  return request({
    url: `/api-testing/scheduled-tasks/${id}/`,
    method: 'delete'
  })
}

// 立即执行定时任务
export function runScheduledTask(id) {
  return request({
    url: `/api-testing/scheduled-tasks/${id}/run_now/`,
    method: 'post'
  })
}

// 暂停定时任务
export function pauseScheduledTask(id) {
  return request({
    url: `/api-testing/scheduled-tasks/${id}/pause/`,
    method: 'post'
  })
}

// 激活定时任务
export function activateScheduledTask(id) {
  return request({
    url: `/api-testing/scheduled-tasks/${id}/activate/`,
    method: 'post'
  })
}

// 获取执行日志
export function getExecutionLogs(taskId, params = {}) {
  return request({
    url: `/api-testing/scheduled-tasks/${taskId}/execution_logs/`,
    method: 'get',
    params
  })
}

// 获取测试套件列表
export function getTestSuites(params) {
  return request({
    url: '/api-testing/test-suites/',
    method: 'get',
    params
  })
}

// 获取单个测试套件详情
export function getTestSuite(id) {
  return request({
    url: `/api-testing/test-suites/${id}/`,
    method: 'get'
  })
}

// 创建测试套件
export function createTestSuite(data) {
  return request({
    url: '/api-testing/test-suites/',
    method: 'post',
    data
  })
}

// 更新测试套件
export function updateTestSuite(id, data) {
  return request({
    url: `/api-testing/test-suites/${id}/`,
    method: 'put',
    data
  })
}

// 删除测试套件
export function deleteTestSuite(id) {
  return request({
    url: `/api-testing/test-suites/${id}/`,
    method: 'delete'
  })
}

// 获取API请求列表
export function getApiRequests(params) {
  return request({
    url: '/api-testing/requests/',
    method: 'get',
    params
  })
}

// 获取单个接口测试用例详情。P0-1 阶段沿用 ApiRequest 作为接口测试用例载体。
export function getApiRequest(id) {
  return request({
    url: `/api-testing/requests/${id}/`,
    method: 'get'
  })
}

// 创建接口测试用例
export function createApiRequest(data) {
  return request({
    url: '/api-testing/requests/',
    method: 'post',
    data
  })
}

// 更新接口测试用例
export function updateApiRequest(id, data) {
  return request({
    url: `/api-testing/requests/${id}/`,
    method: 'put',
    data
  })
}

// 移动接口测试用例到同项目集合
export function moveApiTestCaseCollection(id, collectionId) {
  return request({
    url: `/api-testing/requests/${id}/move-collection/`,
    method: 'post',
    data: { collection: collectionId }
  })
}

// 删除接口测试用例
export function deleteApiRequest(id) {
  return request({
    url: `/api-testing/requests/${id}/`,
    method: 'delete'
  })
}

// 获取环境列表
export function getEnvironments(params) {
  return request({
    url: '/api-testing/environments/',
    method: 'get',
    params
  })
}

// 创建环境
export function createEnvironment(data) {
  return request({
    url: '/api-testing/environments/',
    method: 'post',
    data
  })
}

// 更新环境
export function updateEnvironment(id, data) {
  return request({
    url: `/api-testing/environments/${id}/`,
    method: 'put',
    data
  })
}

// 删除环境
export function deleteEnvironment(id) {
  return request({
    url: `/api-testing/environments/${id}/`,
    method: 'delete'
  })
}

// 激活环境
export function activateEnvironment(id) {
  return request({
    url: `/api-testing/environments/${id}/activate/`,
    method: 'post'
  })
}

// 获取项目列表
export function getApiProjects(params) {
  return request({
    url: '/api-testing/projects/',
    method: 'get',
    params
  })
}

// 创建项目
export function createApiProject(data) {
  return request({
    url: '/api-testing/projects/',
    method: 'post',
    data
  })
}

// 更新项目
export function updateApiProject(id, data) {
  return request({
    url: `/api-testing/projects/${id}/`,
    method: 'put',
    data
  })
}

// 删除项目
export function deleteApiProject(id) {
  return request({
    url: `/api-testing/projects/${id}/`,
    method: 'delete'
  })
}

// 获取集合列表
export function getApiCollections(params) {
  return request({
    url: '/api-testing/collections/',
    method: 'get',
    params
  })
}

// 创建接口集合
export function createApiCollection(data) {
  return request({
    url: '/api-testing/collections/',
    method: 'post',
    data
  })
}

// 更新接口集合
export function updateApiCollection(id, data) {
  return request({
    url: `/api-testing/collections/${id}/`,
    method: 'patch',
    data
  })
}

// 删除接口集合
export function deleteApiCollection(id) {
  return request({
    url: `/api-testing/collections/${id}/`,
    method: 'delete'
  })
}

// 执行测试套件
export function executeTestSuite(id, data) {
  return request({
    url: `/api-testing/test-suites/${id}/execute/`,
    method: 'post',
    data
  })
}

// 添加接口测试用例到测试套件
export function addApiRequestsToTestSuite(id, requestIds) {
  return request({
    url: `/api-testing/test-suites/${id}/add-requests/`,
    method: 'post',
    data: {
      request_ids: requestIds
    }
  })
}

// 更新套件内接口测试用例配置
export function updateTestSuiteRequest(id, data) {
  return request({
    url: `/api-testing/test-suite-requests/${id}/`,
    method: 'patch',
    data
  })
}

// 保存套件级断言
export function updateTestSuiteRequestAssertions(id, assertions) {
  return request({
    url: `/api-testing/test-suite-requests/${id}/assertions/`,
    method: 'post',
    data: { assertions }
  })
}

// 移除套件内接口测试用例
export function deleteTestSuiteRequest(id) {
  return request({
    url: `/api-testing/test-suite-requests/${id}/`,
    method: 'delete'
  })
}

// 执行API请求
export function executeApiRequest(id, data) {
  return request({
    url: `/api-testing/requests/${id}/execute/`,
    method: 'post',
    data
  })
}

// 获取执行结果
export function getExecutionResult(id) {
  return request({
    url: `/api-testing/test-executions/${id}/`,
    method: 'get'
  })
}

// 获取测试执行列表
export function getTestExecutions(params) {
  return request({
    url: '/api-testing/test-executions/',
    method: 'get',
    params
  })
}

// 生成 Allure 报告
export function generateAllureReport(id) {
  return request({
    url: `/api-testing/test-executions/${id}/generate-allure-report/`,
    method: 'post'
  })
}

// 接口测试用例语义别名，避免新页面继续引用旧“接口管理”命名。
export const getApiTestCases = getApiRequests
export const searchApiTestCases = getApiRequests
export const getApiTestCase = getApiRequest
export const createApiTestCase = createApiRequest
export const updateApiTestCase = updateApiRequest
export const deleteApiTestCase = deleteApiRequest
export const executeApiTestCase = executeApiRequest

// 获取请求历史
export function getRequestHistory(params) {
  return request({
    url: '/api-testing/histories/',
    method: 'get',
    params
  })
}

// 删除请求历史
export function deleteRequestHistory(id) {
  return request({
    url: `/api-testing/histories/${id}/`,
    method: 'delete'
  })
}

// 批量删除请求历史
export function batchDeleteRequestHistory(ids) {
  return request({
    url: '/api-testing/histories/batch-delete/',
    method: 'post',
    data: { ids }
  })
}

// 按当前筛选范围清空请求历史
export function clearRequestHistory(params) {
  return request({
    url: '/api-testing/histories/clear/',
    method: 'post',
    data: params
  })
}

// 获取用户列表
export function getUsers(params) {
  return request({
    url: '/api-testing/users/',
    method: 'get',
    params
  })
}
// 获取操作日志
export function getOperationLogs(params) {
  return request({
    url: '/api-testing/operation-logs/',
    method: 'get',
    params
  })
}

// 获取 AI 服务配置列表
export function getAIServiceConfigs(params) {
  return request({
    url: '/api-testing/ai-service-configs/',
    method: 'get',
    params
  })
}

// 创建 AI 服务配置
export function createAIServiceConfig(data) {
  return request({
    url: '/api-testing/ai-service-configs/',
    method: 'post',
    data
  })
}

// 更新 AI 服务配置
export function updateAIServiceConfig(id, data) {
  return request({
    url: `/api-testing/ai-service-configs/${id}/`,
    method: 'put',
    data
  })
}

// 删除 AI 服务配置
export function deleteAIServiceConfig(id) {
  return request({
    url: `/api-testing/ai-service-configs/${id}/`,
    method: 'delete'
  })
}

// 测试 AI 服务连接
export function testAIServiceConnection(configId) {
  return request({
    url: '/api-testing/ai-service-configs/test_connection/',
    method: 'post',
    data: { config_id: configId }
  })
}

import request from '@/utils/api'

export function getExecutionPlanDetail(planId) {
  return request({
    url: `/executions/plans/${planId}/`,
    method: 'get'
  })
}

export function updateRunCaseStatus(runCaseId, data) {
  return request({
    url: `/executions/run_cases/${runCaseId}/update_status/`,
    method: 'patch',
    data
  })
}

export function getRunCaseHistory(runCaseId) {
  return request({
    url: `/executions/run_cases/${runCaseId}/history/`,
    method: 'get'
  })
}

export function deleteRunCase(runCaseId) {
  return request({
    url: `/executions/run_cases/${runCaseId}/`,
    method: 'delete'
  })
}

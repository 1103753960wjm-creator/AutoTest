import axios from "@/utils/axios.ts";

// 统一管理接口
enum API {
  TASK_LIST = "/api/task/task_list",
  ADD_TASK = "/api/task/add_task",
  DEL_TASK = "/api/task/del_task",
  EDIT_TASK = "/api/task/edit_task",
  NOTICE_LIST = "/api/task/notice_list",
  ADD_NOTICE = "/api/task/add_notice",
  EDIT_NOTICE = "/api/task/edit_notice",
  DEL_NOTICE = "/api/task/del_notice",
  NOTICE_SELECT = "/api/task/notice_select",
}
// 获取列表
export const task_list = (params: any) => {
  return axios.post(API.TASK_LIST, params);
};

// 添加任务
export const add_task = (params: any) => {
  return axios.post(API.ADD_TASK, params);
};

// 删除任务
export const del_task = (params: any) => {
  return axios.post(API.DEL_TASK, params);
};

// 编辑任务
export const edit_task = (params: any) => {
  return axios.post(API.EDIT_TASK, params);
};

// 获取通知列表
export const notice_list = (params: any) => {
  return axios.post(API.NOTICE_LIST, params);
};

// 添加通知
export const add_notice = (params: any) => {
  return axios.post(API.ADD_NOTICE, params);
};

// 编辑通知
export const edit_notice = (params: any) => {
  return axios.post(API.EDIT_NOTICE, params);
};

// 删除通知
export const del_notice = (params: any) => {
  return axios.post(API.DEL_NOTICE, params);
};

// 获取通知选择器
export const notice_select = (params: any) => {
  return axios.post(API.NOTICE_SELECT, params);
};
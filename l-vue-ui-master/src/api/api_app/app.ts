import axios from "@/utils/axios.ts";

// 统一管理接口
enum API {
  APP_MENU = "/api/app/app_menu",
  SCRIPT_INFO = "/api/app/get_app_script",
  SAVE_SCRIPT = "/api/app/save_app_script",
  RUN_SCRIPT = "/api/app/run_app_script",
  ADD_MENU = "/api/app/add_menu",
  DEL_MENU = "/api/app/del_menu",
  RENAME_MENU = "/api/app/rename_menu",
  APP_RESULT = "/api/app/get_app_result",
  PID_STATUS = "/api/app/pid_status",
  STOP_PROCESS = "/api/app/stop_process",
  APP_RESULT_DETAIL = "/api/app/get_result_detail",
  MENU_SCRIPT_LIST = "/api/app/menu_script_list",
  RUN_SCRIPT_LIST = "/api/app/run_script_list",
  APP_RESULT_LIST = "/api/app/app_result_list",
  GET_APP_RESULT_DETAIL = "/api/app/get_app_result_detail",
  GET_RESULT_LIST = "/api/app/get_result_list",
  SEND_APP_WARN = "/api/app/send_app_warn",
  GET_SCRIPT_LIST = "/api/app/get_script_list",
  GET_PROCESS = "/api/app/get_process",
  VIEW_SCRIPT_LIST = "/api/app/view_script_list",
  APP_CORRECTION = "/api/app/app_correction",
  APP_MENU_SELECT = "/api/app/app_menu_select",
}

// app自动化目录
export const app_menu = (params: any) => {
  return axios.post(API.APP_MENU, params);
};

// app获取脚本
export const get_script = (params: any) => {
  return axios.post(API.SCRIPT_INFO, params);
};

// app获取脚本集
export const get_script_list = (params: any) => {
  return axios.post(API.MENU_SCRIPT_LIST, params);
};

// 保存脚本
export const save_app_script = (params: any) => {
  return axios.post(API.SAVE_SCRIPT, params);
};

// 执行脚本
export const run_app_script = (params: any) => {
  return axios.post(API.RUN_SCRIPT, params);
};

// 执行脚本集
export const run_scripts = (params: any) => {
  return axios.post(API.RUN_SCRIPT_LIST, params);
};

// 新增目录
export const add_app_menu = (params: any) => {
  return axios.post(API.ADD_MENU, params);
};

// 删除目录
export const del_app_menu = (params: any) => {
  return axios.post(API.DEL_MENU, params);
};

// 重命名
export const rename_app_menu = (params: any) => {
  return axios.post(API.RENAME_MENU, params);
};

// 获取app自动化结果
export const app_result = (params: any) => {
  return axios.post(API.APP_RESULT, params);
};

// 获取app结果汇总
export const app_result_detail = (params: any) => {
  return axios.post(API.APP_RESULT_DETAIL, params);
};

// 获取进程状态
export const pid_status = (params: any) => {
  return axios.post(API.PID_STATUS, params);
};

// 终止进程执行
export const stop_process = (params: any) => {
  return axios.post(API.STOP_PROCESS, params);
};

// app结果列表
export const get_result_list = (params: any) => {
  return axios.post(API.APP_RESULT_LIST, params);
};

// 获取结果详情
export const get_app_result_detail = (params: any) => {
  return axios.post(API.GET_APP_RESULT_DETAIL, params);
};

// 获取单个结果列表
export const get_result_log = (params: any) => {
  return axios.post(API.GET_RESULT_LIST, params);
};

// 异常超出通知
export const send_app_warn = (params: any) => {
  return axios.post(API.SEND_APP_WARN, params);
};

// 获取脚本集
export const get_app_script_list = (params: any) => {
  return axios.post(API.GET_SCRIPT_LIST, params);
};

export const get_process = (params: any) => {
  return axios.post(API.GET_PROCESS, params);
};

export const view_script_list = (params: any) => {
  return axios.post(API.VIEW_SCRIPT_LIST, params);
};

export const app_correction = (params: any) => {
  return axios.post(API.APP_CORRECTION, params);
};

export const app_menu_select = (params: any) => {
  return axios.post(API.APP_MENU_SELECT, params);
};
import axios from "@/utils/axios.ts";

// 统一管理接口
enum API {
  WEB_MENU = "/api/web/web_menu",
  GET_WEB_SCRIPT = "/api/web/get_web_script",
  MENU_SCRIPT_LIST = "/api/web/menu_script_list",
  ADD_MENU = "/api/web/add_menu",
  DEL_MENU = "/api/web/del_menu",
  RENAME_MENU = "/api/web/rename_menu",
  SAVE_SCRIPT = "/api/web/save_script",
  INPUT_ELEMENT = "/api/web/input_element",
  RUN_WEB_SCRIPT = "/api/web/run_web_script",
  GET_WEB_RESULT = "/api/web/get_web_result",
  GET_WEB_RESULT_LIST = "/api/web/get_web_result_list",
  GET_WEB_RESULT_LOG = "/api/web/get_web_result_log",
  GET_WEB_RESULT_REPORT = "/api/web/get_web_result_report",
  GET_WEB_RESULT_DETAIL = "/api/web/get_web_result_detail",
  GET_SCRIPT_LIST = "/api/web/get_script_list",
  WEb_GROUP_LIST = "/api/web/web_group_list",
  ADD_WEB_GROUP = "/api/web/add_web_group",
  EDIT_WEB_GROUP = "/api/web/edit_web_group",
  DEL_WEB_GROUP = "/api/web/del_web_group",
  WEB_GROUP_SELECT = "/api/web/web_group_select",
  GROUP_ADD_SCRIPT = "/api/web/group_add_script"
}

// web目录
export const web_menu = (params: any) => {
  return axios.post(API.WEB_MENU, params);
};

// web脚本信息
export const get_web_script = (params: any) => {
  return axios.post(API.GET_WEB_SCRIPT, params);
};

// web脚本列表
export const menu_script_list = (params: any) => {
  return axios.post(API.MENU_SCRIPT_LIST, params);
};

// 新增目录
export const add_web_menu = (params: any) => {
  return axios.post(API.ADD_MENU, params);
};

// 删除目录
export const del_web_menu = (params: any) => {
  return axios.post(API.DEL_MENU, params);
};

// 重命名
export const rename_web_menu = (params: any) => {
  return axios.post(API.RENAME_MENU, params);
};

// 保存脚本
export const save_script = (params: any) => {
  return axios.post(API.SAVE_SCRIPT, params);
};

// 输入元素
export const input_element = (params: any) => {
  return axios.post(API.INPUT_ELEMENT, params);
};

// 运行脚本
export const run_web_script = (params: any) => {
  return axios.post(API.RUN_WEB_SCRIPT, params);
};

// 获取执行结果
export const get_web_result = (params: any) => {
  return axios.post(API.GET_WEB_RESULT, params);
};

// 获取执行结果列表
export const get_web_result_list = (params: any) => {
  return axios.post(API.GET_WEB_RESULT_LIST, params);
};

// 获取执行结果日志
export const get_web_result_log = (params: any) => {
  return axios.post(API.GET_WEB_RESULT_LOG, params);
};

// 获取执行结果报告
export const get_web_result_report = (params: any) => {
  return axios.post(API.GET_WEB_RESULT_REPORT, params);
};

// 获取结果详情
export const get_web_result_detail = (params: any) => {
  return axios.post(API.GET_WEB_RESULT_DETAIL, params);
};

// 获取脚本列表
export const get_web_script_list = (params: any) => {
  return axios.post(API.GET_SCRIPT_LIST, params);
};

// 获取脚本集列表
export const web_group_list = (params: any) => {
  return axios.post(API.WEb_GROUP_LIST, params);
}

// 新增脚本集
export const add_web_group = (params: any) => {
  return axios.post(API.ADD_WEB_GROUP, params);
}

// 编辑脚本集
export const edit_web_group = (params: any) => {
  return axios.post(API.EDIT_WEB_GROUP, params);
}

// 删除脚本集
export const del_web_group = (params: any) => {
  return axios.post(API.DEL_WEB_GROUP, params);
}

// 脚本集选择器
export const web_group_select = (params: any) => {
  return axios.post(API.WEB_GROUP_SELECT, params);
}

// 测试场景添加用例
export const group_add_script = (params: any) => {
  return axios.post(API.GROUP_ADD_SCRIPT, params);
}
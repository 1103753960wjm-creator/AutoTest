import axios from "@/utils/axios.ts";

// 统一管理接口
enum API {
  LOGIN = "/api/user/login",
  USER_LIST = "/api/user/user_list",
  ADD_USER = "/api/user/add_user",
  EDIT_USER = "/api/user/edit_user",
  DELETE_USER = "/api/user/del_user",
  LOGIN_LOG = "/api/user/login_log",
  ACTION_LOG = "/api/user/action_log",
  ROLE_LIST = "/api/user/role_list",
  ADD_ROLE = "/api/user/add_role",
  EDIT_ROLE = "/api/user/edit_role",
  DELETE_ROLE = "/api/user/del_role",
  PERMISSION_TREE = "/api/user/permission_tree",
  ROLE_PERMISSION = "/api/user/role_permission",
  ADD_PERMISSION = "/api/user/add_permission",
  EDIT_PERMISSION = "/api/user/edit_permission",
  DELETE_PERMISSION = "/api/user/del_permission",
  EDIT_ROLE_PERMISSION = "/api/user/edit_role_permission",
  ROLE_SELECT = "/api/user/role_select",
  CHANGE_ROLE_USER= "/api/user/change_role_user",
  ROLE_USER = "/api/user/role_user",
  USER_SELECT = "/api/user/user_select",
}

// 登录接口方法
export const Login = (params: any) => {
  return axios.post(API.LOGIN, params);
};

// 用户列表接口方法
export const get_user_list = (params: any) => {
  return axios.post(API.USER_LIST, params);
};

// 新增用户接口方法
export const add_user = (params: any) => {
  return axios.post(API.ADD_USER, params);
};

// 编辑用户接口方法
export const edit_user = (params: any) => {
  return axios.post(API.EDIT_USER, params);
};

// 删除用户接口方法
export const del_user = (params: any) => {
  return axios.post(API.DELETE_USER, params);
};

// 登录日志接口方法
export const get_login_log_list = (params: any) => {
  return axios.post(API.LOGIN_LOG, params);
};

// 操作日志接口方法
export const get_action_log_list = (params: any) => {
  return axios.post(API.ACTION_LOG, params);
};

// 角色列表接口方法
export const role_list = (params: any) => {
  return axios.post(API.ROLE_LIST, params);
};

// 新增角色接口方法
export const add_role = (params: any) => {
  return axios.post(API.ADD_ROLE, params);
};

// 编辑角色接口方法
export const edit_role = (params: any) => {
  return axios.post(API.EDIT_ROLE, params);
};

// 删除角色接口方法
export const del_role = (params: any) => {
  return axios.post(API.DELETE_ROLE, params);
};

// 获取权限树接口方法
export const permission_tree = (params: any) => {
  return axios.post(API.PERMISSION_TREE, params);
};

// 获取角色权限接口方法
export const role_permission = (params: any) => {
  return axios.post(API.ROLE_PERMISSION, params);
};

// 新增权限接口方法
export const add_permission = (params: any) => {
  return axios.post(API.ADD_PERMISSION, params);
};

// 编辑权限接口方法
export const edit_permission = (params: any) => {
  return axios.post(API.EDIT_PERMISSION, params);
};

// 删除权限接口方法
export const del_permission = (params: any) => {
  return axios.post(API.DELETE_PERMISSION, params);
};

// 编辑角色权限接口方法
export const edit_role_permission = (params: any) => {
  return axios.post(API.EDIT_ROLE_PERMISSION, params);
};

// 获取角色下拉接口方法
export const role_select = (params: any) => {
  return axios.post(API.ROLE_SELECT, params);
};

// 切换用户角色接口方法
export const change_role_user = (params: any) => {
  return axios.post(API.CHANGE_ROLE_USER, params);
};

// 获取角色用户接口方法
export const role_user = (params: any) => {
  return axios.post(API.ROLE_USER, params);
};

// 获取用户列表接口方法
export const user_select = (params: any) => {
  return axios.post(API.USER_SELECT, params);
};
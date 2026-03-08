import axios from "@/utils/axios.ts";

// 统一管理接口
enum API {
  DEVICES_LIST = "/api/device/device_list",
  DEVICES_INSTALL = "/api/device/device_install",
  DEVICES_UNINSTALL = "/api/device/device_uninstall",
  DEVICE_INFO_LIST = "/api/device/device_info_list",
  USE_DEVICE = "/api/device/use_device",
  STOP_DEVICE = "/api/device/stop_device",
  GET_DEVICES_LOG = "/api/device/get_device_log",
  GET_HISTORY_LIST = "/api/device/get_history_list",
  DEVICE_INSTALL_APP = "/api/device/device_install_app",
  DIRECT_INSTALL_APP = "/api/device/direct_install_app",
  APP_VIEW_DEVICE = "/api/device/app_view_device",
  ADD_DEVICE = "/api/device/add_device",
  DEVICE_PERFORMANCE = "/api/device/device_performance"
}

// 获取设备列表
export const get_device_list = (params: any) => {
  return axios.post(API.DEVICES_LIST, params);
};

export const devices_install = (params: any) => {
  return axios.post(API.DEVICES_INSTALL, params);
};

export const devices_uninstall = (params: any) => {
  return axios.post(API.DEVICES_UNINSTALL, params);
};

export const device_info_list = (params: any) => {
  return axios.post(API.DEVICE_INFO_LIST, params);
};

export const use_device = (params: any) => {
  return axios.post(API.USE_DEVICE, params);
};

export const stop_device = (params: any) => {
  return axios.post(API.STOP_DEVICE, params);
};

export const get_device_log = (params: any) => {
  return axios.post(API.GET_DEVICES_LOG, params);
};

export const get_history_list = (params: any) => {
  return axios.post(API.GET_HISTORY_LIST, params);
};

export const device_install_app = (params: any) => {
  return axios.post(API.DEVICE_INSTALL_APP, params);
};

export const direct_install_app = (params: any) => {
  return axios.post(API.DIRECT_INSTALL_APP, params);
};

export const app_view_device = (params: any) => {
  return axios.post(API.APP_VIEW_DEVICE, params);
};

export const add_device = (params: any) => {
  return axios.post(API.ADD_DEVICE, params);
};

export const device_performance = (params: any) => {
  return axios.post(API.DEVICE_PERFORMANCE, params);
};
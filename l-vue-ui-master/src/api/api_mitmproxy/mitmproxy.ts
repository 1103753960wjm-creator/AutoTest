import axios from "@/utils/axios.ts";

enum API {
    MITMPROXY_START = "/api/mitmproxy/mitmproxy_start",
    MITMPROXY_SINGLE_START = "/api/mitmproxy/mitmproxy_single_start",
    MITMPROXY_STOP = "/api/mitmproxy/mitmproxy_stop",
    MITMPROXY_CLOSE_AGENT = "/api/mitmproxy/mitmproxy_close_agent",
    MITMPROXY_CHECK = "/api/mitmproxy/mitmproxy_check",
    MITMPROXY_RUN_LOG = "/api/mitmproxy/mitmproxy_run_log",
}

// 开启代理
export const mitmproxy_start = (params: any) => {
  return axios.post(API.MITMPROXY_START, params);
};

// 开启代理
export const mitmproxy_single_start = (params: any) => {
  return axios.post(API.MITMPROXY_SINGLE_START, params);
};

// 关闭代理
export const mitmproxy_stop = (params: any) => {
  return axios.post(API.MITMPROXY_STOP, params);
};

// 关闭设备代理
export const mitmproxy_close_agent = (params: any) => {
  return axios.post(API.MITMPROXY_CLOSE_AGENT, params);
};

// 检查代理状态
export const mitmproxy_check = (params: any) => {
  return axios.post(API.MITMPROXY_CHECK, params);
};

// 获取代理运行日志
export const mitmproxy_run_log = (params: any) => {
  return axios.post(API.MITMPROXY_RUN_LOG, params);
};
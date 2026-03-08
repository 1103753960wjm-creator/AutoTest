import axios from "@/utils/axios.ts";

// 统一管理接口
enum API {
    GET_COUNT = "/api/count/get_count",
  GET_RUN_COUNT = "/api/count/get_run_count",
}

// 获取统计
export const get_count = (params: any) => {
    return axios.post(API.GET_COUNT, params)
}

// 获取执行统计
export const get_run_count = (params: any) => {
    return axios.post(API.GET_RUN_COUNT, params)
}
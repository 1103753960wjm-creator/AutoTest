import axios from "@/utils/axios.ts";

enum API {
    FILE_LIST = '/api/file/file_list',
}

// 文件列表
export const file_list = (params: any) => {
  return axios.post(API.FILE_LIST, params);
};
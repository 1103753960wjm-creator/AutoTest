import axios from "@/utils/axios.ts";

// 统一管理接口
enum API {
  IMG_LIST = "/api/app/img_list",
  IMG_SELECT = "/api/app/img_select",
  DELETE_IMG = "/api/app/delete_img",
  EDIT_IMG = "/api/app/edit_img",
}

// 图像库
export const img_list = (params: any) => {
  return axios.post(API.IMG_LIST, params);
};

// 图像选择器
export const img_select = (params: any) => {
  return axios.post(API.IMG_SELECT, params);
};

// 删除图片
export const delete_img = (params: any) => {
  return axios.post(API.DELETE_IMG, params); 
};

// 编辑图片
export const edit_img = (params: any) => {
  return axios.post(API.EDIT_IMG, params);
};
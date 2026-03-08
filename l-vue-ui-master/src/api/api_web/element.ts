import axios from "@/utils/axios.ts";

enum API {
    ELEMENT_TREE = "/api/web_element/element_tree",
    ADD_MENU = "/api/web_element/add_menu",
    EDIT_MENU = "/api/web_element/edit_menu",
    DEL_MENU = "/api/web_element/del_menu",
    GET_ELEMENT_LIST = "/api/web_element/get_element_list",
    ADD_ELEMENT = "/api/web_element/add_element",
    EDIT_ELEMENT = "/api/web_element/edit_element",
    DEL_ELEMENT = "/api/web_element/del_element",
    GET_ELEMENT_SELECT = "/api/web_element/get_element_select",
}

// 获取element树
export const element_tree = (params: any) => {
    return axios.post(API.ELEMENT_TREE, params);
}

// 添加菜单
export const add_menu = (params: any) => {
    return axios.post(API.ADD_MENU, params);
}

// 修改菜单
export const edit_menu = (params: any) => {
    return axios.post(API.EDIT_MENU, params);
}

// s删除菜单
export const del_menu = (params: any) => {
    return axios.post(API.DEL_MENU, params);
}

// 获取element列表
export const get_element_list = (params: any) => {
    return axios.post(API.GET_ELEMENT_LIST, params);
}

// 添加element
export const add_element = (params: any) => {
    return axios.post(API.ADD_ELEMENT, params);
}

// 修改element
export const edit_element = (params: any) => {
    return axios.post(API.EDIT_ELEMENT, params);
}

// 删除element
export const del_element = (params: any) => {
    return axios.post(API.DEL_ELEMENT, params);
}

// 获取元素选择器
export const get_element_select = (params: any) => {
    return axios.post(API.GET_ELEMENT_SELECT, params);
}
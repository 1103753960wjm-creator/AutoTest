import axios from "@/utils/axios.ts";

enum API {
    QUESTION_LIST = "/api/question/question_list",
    ADD_QUESTION = "/api/question/add_question",
    DEL_QUESTION = "/api/question/del_question",
    EDIT_QUESTION = "/api/question/edit_question",
    ADD_ANSWER = "/api/question/add_answer",
    DEL_ANSWER = "/api/question/del_answer",
    EDIT_ANSWER = "/api/question/edit_answer",
    DEVELOPMENT_HISTORY = "/api/question/development_history",
}

// 问题列表
export const question_list = (params: any) => {
  return axios.post(API.QUESTION_LIST, params);
};

// 添加问题
export const add_question = (params: any) => {
  return axios.post(API.ADD_QUESTION, params);
};

// 删除问题
export const del_question = (params: any) => {
  return axios.post(API.DEL_QUESTION, params);
};

// 修改问题
export const edit_question = (params: any) => {
  return axios.post(API.EDIT_QUESTION, params);
};

// 添加回复
export const add_answer = (params: any) => {
  return axios.post(API.ADD_ANSWER, params);
};

// 删除回复
export const del_answer = (params: any) => {
  return axios.post(API.DEL_ANSWER, params);
};

// 修改回复
export const edit_answer = (params: any) => {
  return axios.post(API.EDIT_ANSWER, params);
};

// 历史记录
export const development_history = (params: any) => {
  return axios.post(API.DEVELOPMENT_HISTORY, params);
};
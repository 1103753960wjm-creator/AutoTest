import axios from "@/utils/axios.ts";

enum API {
    API_PROJECT = "/api/api/api_project",
    API_SERVICE = "/api/api/api_service",
    API_TREE = "/api/api/api_tree",
    ADD_MENU = "/api/api/add_menu",
    DEL_MENU = "/api/api/del_menu",
    EDIT_MENU = "/api/api/edit_menu",
    COPY_MENU = "/api/api/copy_menu",
    API_INFO = "/api/api/api_info",
    SAVE_API = "/api/api/save_api",
    SAVE_API_CASE = "/api/api/save_api_case",
    API_ENV = "/api/api/api_env",
    ENV_INFO = "/api/api/env_info",
    ADD_ENV = "/api/api/add_env",
    SAVE_ENV = "/api/api/save_env",
    DEL_ENV = "/api/api/del_env",
    API_SEND = "/api/api/api_send",
    API_TREE_LIST = "/api/api/api_tree_list",
    REDIS_COMMON = "/api/api/redis_common",
    API_DB = "/api/api/api_db",
    API_DB_LIST = "/api/api/api_db_list",
    ADD_API_DB = "/api/api/add_api_db",
    EDIT_API_DB = "/api/api/edit_api_db",
    DEL_API_DB = "/api/api/del_api_db",
    API_VAR_LIST = "/api/api/api_var_list",
    ADD_VAR = "/api/api/add_var",
    EDIT_VAR = "/api/api/edit_var",
    DEL_VAR = "/api/api/del_var",
    REQ_HISTORY = "/api/api/req_history",
    API_CODE = "/api/api/api_code",
    ADD_CODE = "/api/api/add_code",
    DEL_CODE = "/api/api/del_code",
    EDIT_CODE = "/api/api/edit_code",
    API_FUNCTION = "/api/api/api_function",
    ADD_FUNCTION = "/api/api/add_function",
    DEL_FUNCTION = "/api/api/del_function",
    EDIT_FUNCTION = "/api/api/edit_function",
    API_PARAMS = "/api/api/api_params",
    ADD_PARAMS = "/api/api/add_params",
    DEL_PARAMS = "/api/api/del_params",
    EDIT_PARAMS = "/api/api/edit_params",
    PARAMS_SELECT = "/api/api/params_select",
    API_EDIT_HISTORY = "/api/api/edit_history",
    API_SCRIPT_LIST = "/api/api/api_script_list",
    ADD_API_SCRIPT = "/api/api/add_api_script",
    EDIT_API_SCRIPT = "/api/api/edit_api_script",
    DEL_API_SCRIPT = "/api/api/del_api_script",
    GET_API_CASE = "/api/api/get_api_case",
    API_SERVICE_LIST = "/api/api/api_service_list",
    RUN_API_SCRIPT = "/api/api/run_api_script",
    GET_API_SCRIPT_RESULT = "/api/api/get_api_script_result",
    GET_API_SCRIPT_RESULT_LIST = "/api/api/get_api_script_result_list",
    GET_API_SCRIPT_RESULT_DETAIL = "/api/api/get_api_script_result_detail",
    GET_API_SCRIPT_LOG = "/api/api/get_api_script_log",
    GET_API_SCRIPT_RESULT_DETAIL_LIST = "/api/api/get_api_script_result_detail_list",
    GET_API_SCRIPT_RESULT_REPORT_LIST = "/api/api/get_api_script_result_report_list",
    GET_API_SCRIPT_REPORT_LOG = "/api/api/get_api_script_report_log",
    GET_API_SCRIPT_LIST = "/api/api/get_api_script_list"
}

// 获取项目列表
export const api_project = (params: any) => {
    return axios.post(API.API_PROJECT, params);
};

// 获取服务列表
export const api_service = (params: any) => {
    return axios.post(API.API_SERVICE, params);
};

// 获取菜单树
export const api_tree = (params: any) => {
    return axios.post(API.API_TREE, params);
};

// 添加菜单
export const add_menu = (params: any) => {
    return axios.post(API.ADD_MENU, params);
};

// 删除菜单
export const del_menu = (params: any) => {
    return axios.post(API.DEL_MENU, params);
};

// 修改菜单
export const edit_menu = (params: any) => {
    return axios.post(API.EDIT_MENU, params);
};

// 复制菜单
export const copy_menu = (params: any) => {
    return axios.post(API.COPY_MENU, params);
};

// 接口信息
export const api_info = (params: any) => {
    return axios.post(API.API_INFO, params);
};

// 保存接口信息
export const save_api = (params: any) => {
    return axios.post(API.SAVE_API, params);
};

// 保存至接口用例
export const save_api_case = (params: any) => {
    return axios.post(API.SAVE_API_CASE, params);
};

// 服务器环境选择器
export const api_env = (params: any) => {
    return axios.post(API.API_ENV, params);
};

// 保存环境数据
export const save_env = (params: any) => {
    return axios.post(API.SAVE_ENV, params);
};

// 新增环境
export const add_env = (params: any) => {
    return axios.post(API.ADD_ENV, params);
};

// 删除数据
export const del_env = (params: any) => {
    return axios.post(API.DEL_ENV, params);
};

// 环境信息
export const env_info = (params: any) => {
    return axios.post(API.ENV_INFO, params);
};

// 发送接口请求
export const api_send = (params: any) => {
    return axios.post(API.API_SEND, params);
};

// 获取菜单树
export const api_tree_list = (params: any) => {
    return axios.post(API.API_TREE_LIST, params);
};

// 获取redis实例
export const redis_common = (params: any) => {
    return axios.post(API.REDIS_COMMON, params);
};

// 数据库列表
export const api_db = (params: any) => {
    return axios.post(API.API_DB, params);
};

// 数据库列表选择器
export const api_db_list = (params: any) => {
    return axios.post(API.API_DB_LIST, params);
};

// 新增数据库
export const add_api_db = (params: any) => {
    return axios.post(API.ADD_API_DB, params);
};

// 编辑数据库
export const edit_api_db = (params: any) => {
    return axios.post(API.EDIT_API_DB, params);
};

// 删除数据库
export const del_api_db = (params: any) => {
    return axios.post(API.DEL_API_DB, params);
};

// 全局变量列表
export const api_var_list = (params: any) => {
    return axios.post(API.API_VAR_LIST, params);
};

// 添加变量
export const add_var = (params: any) => {
    return axios.post(API.ADD_VAR, params);
};

// 编辑变量
export const edit_var = (params: any) => {
    return axios.post(API.EDIT_VAR, params);
};

// 删除变量
export const del_var = (params: any) => {
    return axios.post(API.DEL_VAR, params);
};

// 请求历史记录
export const req_history = (params: any) => {
    return axios.post(API.REQ_HISTORY, params);
};

// api代码列表
export const api_code = (params: any) => {
    return axios.post(API.API_CODE, params);
};

// 添加api代码
export const add_code = (params: any) => {
    return axios.post(API.ADD_CODE, params);
};

// 编辑api代码
export const edit_code = (params: any) => {
    return axios.post(API.EDIT_CODE, params);
};

// 删除api代码
export const del_code = (params: any) => {
    return axios.post(API.DEL_CODE, params);
};

// 公共函数
export const api_function = (params: any) => {
    return axios.post(API.API_FUNCTION, params);
};

// 添加公共函数
export const add_function = (params: any) => {
    return axios.post(API.ADD_FUNCTION, params);
};

// 删除公共函数
export const del_function = (params: any) => {
    return axios.post(API.DEL_FUNCTION, params);
};

//编辑公共函数
export const edit_function = (params: any) => {
    return axios.post(API.EDIT_FUNCTION, params);
};

// 参数依赖列表
export const api_params = (params: any) => {
    return axios.post(API.API_PARAMS, params);
};

// 新增参数依赖
export const add_params = (params: any) => {
    return axios.post(API.ADD_PARAMS, params);
};

// 删除参数依赖
export const del_params = (params: any) => {
    return axios.post(API.DEL_PARAMS, params);
};

// 编辑参数依赖
export const edit_params = (params: any) => {
    return axios.post(API.EDIT_PARAMS, params);
};

// 参数依赖选择器
export const params_select = (params: any) => {
    return axios.post(API.PARAMS_SELECT, params);
};

// 接口编辑历史
export const api_edit_history = (params: any) => {
    return axios.post(API.API_EDIT_HISTORY, params);
};

// API场景列表
export const api_script_list = (params: any) => {
    return axios.post(API.API_SCRIPT_LIST, params);
};

// 添加场景
export const add_api_script = (params: any) => {
    return axios.post(API.ADD_API_SCRIPT, params);
};

// 编辑场景
export const edit_api_script = (params: any) => {
    return axios.post(API.EDIT_API_SCRIPT, params);
};

// 删除场景
export const del_api_script = (params: any) => {
    return axios.post(API.DEL_API_SCRIPT, params);
};

// 获取接口用例
export const get_api_case = (params: any) => {
    return axios.post(API.GET_API_CASE, params);
};

// 服务器列表
export const api_service_list = (params: any) => {
    return axios.post(API.API_SERVICE_LIST, params)
}

// 执行接口自动化场景
export const run_api_script = (params: any) => {
    return axios.post(API.RUN_API_SCRIPT, params)
}

// 获取接口自动化场景结果
export const get_api_script_result_list = (params: any) => {
    return axios.post(API.GET_API_SCRIPT_RESULT_LIST, params)
}

// 获取接口自动化场景结果详情
export const get_api_script_result_detail = (params: any) => {
    return axios.post(API.GET_API_SCRIPT_RESULT_DETAIL, params)
}

// 获取接口自动化场景结果
export const get_api_script_result = (params: any) => {
    return axios.post(API.GET_API_SCRIPT_RESULT, params)
}

// 获取接口自动化场景日志
export const get_api_script_log = (params: any) => {
    return axios.post(API.GET_API_SCRIPT_LOG, params)
}

// 获取接口自动化场景结果详情列表
export const get_api_script_result_detail_list = (params: any) => {
    return axios.post(API.GET_API_SCRIPT_RESULT_DETAIL_LIST, params)
}

// 获取接口自动化场景结果报告列表
export const get_api_script_result_report_list = (params: any) => {
    return axios.post(API.GET_API_SCRIPT_RESULT_REPORT_LIST, params)
}

// 获取接口自动化场景结果报告详情
export const get_api_script_report_log = (params: any) => {
    return axios.post(API.GET_API_SCRIPT_REPORT_LOG, params)
}

// 获取接口自动化场景列表
export const get_api_script_list = (params: any) => {
    return axios.post(API.GET_API_SCRIPT_LIST, params)
}



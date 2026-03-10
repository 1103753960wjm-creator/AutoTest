import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from "axios";

import { MsgError } from "@/utils/koi.ts";
import { LOGIN_URL } from "@/config/index.ts";
import useUserStore from "@/stores/modules/user.ts";
import { getToken } from "@/utils/storage.ts";
import router from "@/routers/index.ts";

// axios配置
const config = {
  // 接口请求的地址
  baseURL: import.meta.env.VITE_WEB_BASE_API,
  timeout: 36000000
};

// 返回值类型
export interface Result<T = any> {
  code: number;
  msg: string;
  data: T;
}

const buildAuthHeaders = (): Record<string, string> => {
  const userinfo: any = getToken() || {};
  if (!userinfo?.token) {
    return {};
  }
  return {
    Authorization: `Bearer ${userinfo.token}`,
    "X-Token": String(userinfo.token),
    "X-User-Id": String(userinfo.user_id || "")
  };
};

// 只有请求封装用的Yu，方便简写
class Yu {
  private instance: AxiosInstance;
  // 初始化
  constructor(config: AxiosRequestConfig) {
    // 实例化axios
    this.instance = axios.create(config);
    // 配置拦截器
    this.interceptors();
  }
  // 拦截器
  private interceptors() {
    // 请求发送之前的拦截器：携带token
    this.instance.interceptors.request.use(
      config => {
        const headers = axios.AxiosHeaders.from(config.headers || {});
        Object.entries(buildAuthHeaders()).forEach(([key, value]) => {
          headers.set(key, value);
        });
        config.headers = headers;
        return config;
      },
      (error: any) => {
        error.data = {};
        error.data.msg = "服务器异常，请联系管理员🌻";
        return error;
      }
    );
    // 请求返回之后的拦截器：数据或者状态
    this.instance.interceptors.response.use(
      (res: AxiosResponse) => {
        // console.log("axios返回数据：", res);
        // console.log("服务器状态",res.status);
        const status = res.data.status || res.data.code; // 后端返回数据状态
        if (status == 200) {
          // 服务器连接状态，非后端返回的status 或者 code
          // 这里的后端可能是code OR status 和 msg OR message需要看后端传递的是什么？
          // console.log("200状态", res);
          return res.data;
        } else if (res.data.code == 1999) {
          // 重试机制响应码
          return res.data;
        } else if (res.data.code == 1003 || res.data.code == 1004 || res.data.code === 1002) {
          // console.log("401状态", status);
          const userStore = useUserStore();
          userStore.setToken("", "", "", ""); // 清空token必须使用这个，不能使用session清空，因为登录的时候js会获取一遍token还会存在。
          MsgError(res.data.message);
          router.replace(LOGIN_URL);
          return Promise.reject(res.data);
        } else {
          // console.log("后端返回数据：",res.data.msg)
          MsgError(res.data.message + "🌻");
          return Promise.reject(res.data.message + "🌻" || "服务器偷偷跑到火星去玩了🌻"); // 可以将异常信息延续到页面中处理，使用try{}catch(error){};
        }
      },
      (error: any) => {
        // 处理网络错误，不是服务器响应的数据
        // console.log("进入错误",error);
        error.data = {};
        if (error && error.response) {
          switch (error.response.status) {
            case 400:
              error.data.msg = "错误请求🌻";
              MsgError(error.data.msg);
              break;
            case 401:
              error.data.msg = "未授权，请重新登录🌻";
              MsgError(error.data.msg);
              break;
            case 403:
              error.data.msg = "对不起，您没有权限访问🌻";
              MsgError(error.data.msg);
              break;
            case 404:
              error.data.msg = "请求错误,未找到请求路径🌻";
              MsgError(error.data.msg);
              break;
            case 405:
              error.data.msg = "请求方法未允许🌻";
              MsgError(error.data.msg);
              break;
            case 408:
              error.data.msg = "请求超时🌻";
              MsgError(error.data.msg);
              break;
            case 500:
              error.data.msg = "服务器又偷懒了，请重试🌻";
              MsgError(error.data.msg);
              break;
            case 501:
              error.data.msg = "网络未实现🌻";
              MsgError(error.data.msg);
              break;
            case 502:
              error.data.msg = "网络错误🌻";
              MsgError(error.data.msg);
              break;
            case 503:
              error.data.msg = "服务不可用🌻";
              MsgError(error.data.msg);
              break;
            case 504:
              error.data.msg = "网络超时🌻";
              MsgError(error.data.msg);
              break;
            case 505:
              error.data.msg = "http版本不支持该请求🌻";
              MsgError(error.data.msg);
              break;
            default:
              error.data.msg = `连接错误${error.response.status}`;
              MsgError(error.data.msg);
          }
        } else {
          error.data.msg = "连接到服务器失败🌻";
          MsgError(error.data.msg);
        }
        return Promise.reject(error); // 将错误返回给 try{} catch(){} 中进行捕获，就算不进行捕获，上方 res.data.status != 200也会抛出提示。
      }
    );
  }
  // Get请求
  get<T = Result>(url: string, params?: object): Promise<T> {
    return this.instance.get(url, { params });
  }
  // Post请求
  post<T = Result>(url: string, data?: object): Promise<T> {
    return this.instance.post(url, data);
  }
  // Put请求
  put<T = Result>(url: string, data?: object): Promise<T> {
    return this.instance.put(url, data);
  }
  // Delete请求  /yu/role/1
  delete<T = Result>(url: string): Promise<T> {
    return this.instance.delete(url);
  }
  // 图片上传
  upload<T = Result>(url: string, params?: object): Promise<T> {
    return this.instance.post(url, params, {
      headers: {
        "Content-Type": "multipart/form-data"
      }
    });
  }
  // 导出Excel
  exportExcel<T = Result>(url: string, params?: object): Promise<T> {
    return axios.get(import.meta.env.VITE_SERVER + url, {
      params,
      headers: {
        Accept: "application/vnd.ms-excel",
        ...buildAuthHeaders()
      },
      responseType: "blob"
    });
  }
}
export default new Yu(config);

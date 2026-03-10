import { PINIA_PREFIX } from "@/config";
// @ts-ignore
import cookies from "js-cookie";

const safeParseJson = (value: string | null) => {
  if (!value) return null;
  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
};

const getStorageKey = (key: string) => `${PINIA_PREFIX}${key}`;

/**
 * 封装获取用户信息的方法
 */
export const getToken = () => {
  const parseKoiUser: any = safeParseJson(window.localStorage.getItem(getStorageKey("user")));
  if (parseKoiUser?.token && parseKoiUser?.user_id !== "") {
    return parseKoiUser;
  }
  return "";
};

/**
 * 各个小仓库之间进行数据交互使用 OR 页面获取storge值使用
 * window.sessionStorage
 * @method set 设置会话缓存
 * @method get 获取会话缓存
 * @method remove 移除会话缓存
 * @method clear 移除全部会话缓存
 */
export const SessionStorage = {
  put(key: string, value: any) {
    window.sessionStorage.setItem(getStorageKey(key), value);
  },
  set(key: string, value: any) {
    window.sessionStorage.setItem(getStorageKey(key), value);
  },
  get(key: string) {
    const value: any = window.sessionStorage.getItem(getStorageKey(key));
    return value;
  },
  remove(key: string) {
    window.sessionStorage.removeItem(getStorageKey(key));
  },
  clear() {
    window.sessionStorage.clear();
  },
  putJSON(key: string, jsonValue: any) {
    window.sessionStorage.setItem(getStorageKey(key), JSON.stringify(jsonValue));
  },
  setJSON(key: string, jsonValue: any) {
    window.sessionStorage.setItem(getStorageKey(key), JSON.stringify(jsonValue));
  },
  getJSON(key: string) {
    return safeParseJson(window.sessionStorage.getItem(getStorageKey(key)));
  }
};

/**
 * window.localStorage
 * @method set 设置
 * @method get 获取
 * @method remove 移除
 * @method clear 移除全部
 */
export const LocalStorage = {
  put(key: string, value: any) {
    window.localStorage.setItem(getStorageKey(key), value);
  },
  set(key: string, value: any) {
    window.localStorage.setItem(getStorageKey(key), value);
  },
  get(key: string) {
    const value: any = window.localStorage.getItem(getStorageKey(key));
    return value;
  },
  remove(key: string) {
    window.localStorage.removeItem(getStorageKey(key));
  },
  clear() {
    window.localStorage.clear();
  },
  putJSON(key: string, jsonValue: any) {
    window.localStorage.setItem(getStorageKey(key), JSON.stringify(jsonValue));
  },
  setJSON(key: string, jsonValue: any) {
    window.localStorage.setItem(getStorageKey(key), JSON.stringify(jsonValue));
  },
  getJSON(key: string) {
    return safeParseJson(window.localStorage.getItem(getStorageKey(key)));
  }
};

/**
 * cookies
 * @method set 设置
 * @method get 获取
 * @method remove 移除
 */
export const Cookie = {
  put(key: string, value: any) {
    cookies.set(getStorageKey(key), value);
  },
  set(key: string, value: any) {
    cookies.set(getStorageKey(key), value);
  },
  get(key: string) {
    const value: any = cookies.get(getStorageKey(key));
    return value;
  },
  remove(key: string) {
    cookies.remove(getStorageKey(key));
  }
};

import koi from "@/utils/axios.ts";

enum API {
  CONFIG_INFO = "/api/ai/config_info",
  MODE_INFO = "/api/ai/mode_info",
  SAVE_CONFIG = "/api/ai/save_config",
  GENERATE_TESTCASES = "/api/ai/generate_testcases"
}

export const getConfigInfo = (data: any = {}) => {
  return koi.post(API.CONFIG_INFO, data);
};

export const getModeInfo = (data: any = {}) => {
  return koi.post(API.MODE_INFO, data);
};

export const saveConfig = (data: any) => {
  return koi.post(API.SAVE_CONFIG, data);
};

export const generateTestcases = (data: any) => {
  return koi.post(API.GENERATE_TESTCASES, data);
};

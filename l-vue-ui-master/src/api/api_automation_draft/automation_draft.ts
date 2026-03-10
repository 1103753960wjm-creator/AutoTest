import koi from "@/utils/axios.ts";

enum API {
  GENERATE = "/api/automation_draft/generate",
  GET_INFO = "/api/automation_draft/get_info",
  LIST_BY_TESTCASE = "/api/automation_draft/list_by_testcase",
  SAVE_TO_ASSET = "/api/automation_draft/save_to_asset"
}

export const generateAutomationDraft = (data: any) => {
  return koi.post(API.GENERATE, data);
};

export const getAutomationDraftInfo = (data: any) => {
  return koi.post(API.GET_INFO, data);
};

export const listAutomationDraftByTestcase = (data: any) => {
  return koi.post(API.LIST_BY_TESTCASE, data);
};

export const saveAutomationDraftToAsset = (data: any) => {
  return koi.post(API.SAVE_TO_ASSET, data);
};

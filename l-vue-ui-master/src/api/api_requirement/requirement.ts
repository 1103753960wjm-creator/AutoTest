import koi from "@/utils/axios.ts";

enum API {
  SAVE_REVIEWED_CASES = "/api/requirement/save_reviewed_cases",
  LIST_RECENT = "/api/requirement/list_recent",
  LIST_PAGE = "/api/requirement/list_page"
}

export const saveReviewedCases = (data: any) => {
  return koi.post(API.SAVE_REVIEWED_CASES, data);
};

export const listRecentRequirements = (data: any = {}) => {
  return koi.post(API.LIST_RECENT, data);
};

export const listRequirementPage = (data: any) => {
  return koi.post(API.LIST_PAGE, data);
};

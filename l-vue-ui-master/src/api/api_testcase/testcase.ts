import koi from "@/utils/axios.ts";

enum API {
  LIST_BY_REQUIREMENT = "/api/testcase/list_by_requirement",
  LIST_PAGE = "/api/testcase/list_page",
  UPDATE_REVIEW_STATUS = "/api/testcase/update_review_status"
}

export const listByRequirement = (data: any) => {
  return koi.post(API.LIST_BY_REQUIREMENT, data);
};

export const listTestcasePage = (data: any) => {
  return koi.post(API.LIST_PAGE, data);
};

export const updateReviewStatus = (data: any) => {
  return koi.post(API.UPDATE_REVIEW_STATUS, data);
};

import axios from "axios";
import koi from "@/utils/axios.ts";
import { getToken } from "@/utils/storage.ts";

enum API {
  LIST_BY_REQUIREMENT = "/api/testcase/list_by_requirement",
  LIST_PAGE = "/api/testcase/list_page",
  UPDATE_REVIEW_STATUS = "/api/testcase/update_review_status",
  UPDATE_CONTENT = "/api/testcase/update_content",
  BATCH_UPDATE = "/api/testcase/batch_update",
  LIST_HISTORY = "/api/testcase/list_history",
  COMPARE_REVISIONS = "/api/testcase/compare_revisions",
  LIST_TAGS = "/api/testcase/list_tags",
  EXPORT_EXCEL = "/api/testcase/export_excel"
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

export const updateTestcaseContent = (data: any) => {
  return koi.post(API.UPDATE_CONTENT, data);
};

export const batchUpdateTestcases = (data: any) => {
  return koi.post(API.BATCH_UPDATE, data);
};

export const listTestcaseHistory = (data: any) => {
  return koi.post(API.LIST_HISTORY, data);
};

export const compareTestcaseRevisions = (data: any) => {
  return koi.post(API.COMPARE_REVISIONS, data);
};

export const listTestcaseTags = (data: any) => {
  return koi.post(API.LIST_TAGS, data);
};

export const exportTestcaseExcel = (data: any) => {
  const userInfo: any = getToken() || {};
  const headers: Record<string, string> = {
    "Content-Type": "application/json"
  };
  if (userInfo?.token) {
    headers.Authorization = `Bearer ${userInfo.token}`;
    headers["X-Token"] = String(userInfo.token);
    headers["X-User-Id"] = String(userInfo.user_id || "");
  }
  return axios.post(
    `${import.meta.env.VITE_SERVER}${API.EXPORT_EXCEL}`,
    data,
    {
      headers,
      responseType: "blob"
    }
  );
};

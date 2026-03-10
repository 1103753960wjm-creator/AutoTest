/**
 * v-auth
 * 按钮权限指令
 */
import useAuthStore from "@/stores/modules/auth.ts";
import type { Directive, DirectiveBinding } from "vue";

const auth: Directive = {
  mounted(el: HTMLElement, binding: DirectiveBinding) {
    const { value } = binding;
    const authStore = useAuthStore();
    const adminButtons = ["*"];
    const buttonList = authStore.getButtonList || authStore.buttons || [];
    if (
      (Array.isArray(value) &&
        value.some((permission: string) => buttonList.includes(permission))) ||
      JSON.stringify(buttonList) === JSON.stringify(adminButtons)
    ) {
      // 如果用户拥有指定权限中的任何一个或者是管理员，则显示元素
    } else {
      el.parentNode?.removeChild(el); // 如果用户不拥有所有权限，则移除元素
    }
  }
};

export default auth;

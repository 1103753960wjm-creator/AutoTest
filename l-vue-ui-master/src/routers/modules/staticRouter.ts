import { RouteRecordRaw } from "vue-router";
import { HOME_URL, LOGIN_URL } from "@/config";
import Layout from "@/layouts/index.vue";

/**
 * LayoutRouter[布局路由]
 */
export const layoutRouter: RouteRecordRaw[] = [
  {
    // 登录成功以后展示数据的路由[一级路由，可以将子路由放置Main模块中(核心)]
    path: "/", // 路由访问路径[唯一]
    name: "layout", // 命名路由[唯一]
    component: Layout, // 登录进入这个页面，这个页面是整个布局
    redirect: HOME_URL, // path路径，<router-link name="/404"> 也是使用path进行跳转
    children: [
      {
        path: HOME_URL, // [唯一]
        component: () => import("@/views/home/index.vue"),
        meta: {
          title: "主控台", // 标题
          enName: "Master Station", // 英文名称
          icon: "HomeFilled", // 图标
          isHide: "0", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
          isLink: "", // 是否外链[有值则是外链]
          isKeepAlive: "0", // 是否缓存路由数据[0是，1否]
          isFull: "1", // 是否缓存全屏[0是，1否]
          isAffix: "0" // 是否缓存固定路由[0是，1否]
        }
      }
    ]
  },
  {
    path: LOGIN_URL,
    name: "login",
    component: () => import("@/views/login/index.vue"),
    meta: {
      title: "登录"
    }
  }
];
/**
 * staticRouter[静态路由]
 */
export const staticRouter: RouteRecordRaw[] = [
  /** 主控台 */
  {
    path: HOME_URL, // [唯一]
    component: () => import("@/views/home/index.vue"),
    meta: {
      title: "主控台", // 标题
      enName: "Master Station", // 英文名称
      icon: "HomeFilled", // 图标 HomeFilled
      isHide: "1", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
      isLink: "", // 是否外链[有值则是外链]
      isKeepAlive: "0", // 是否缓存路由数据[0是，1否]
      isFull: "1", // 是否缓存全屏[0是，1否]
      isAffix: "0" // 是否缓存固定路由[0是，1否]
    }
  },
  {
    path: "/utility", // 路由访问路径[唯一]
    component: Layout, // 登录进入这个页面，这个页面是整个布局
    meta: {
      title: "实用工具", // 标题
      enName: "Static Router", // 英文名称
      icon: "Box", // 图标
      isHide: "1", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
      isLink: "", // 是否外链[有值则是外链]
      isKeepAlive: "0", // 是否缓存路由数据[0是，1否]
      isFull: "0", // 是否缓存全屏[0是，1否]
      isAffix: "0" // 是否缓存固定路由[0是，1否]
    },
    children: [
      {
        path: "/json_parse", // [唯一]
        component: () => import("@/views/utility/json_parse.vue"),
        meta: {
          title: "JSON解析", // 标题
          enName: "JSON Parse", // 英文名称
          icon: "Switch", // 图标
          isHide: "0", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
          isLink: "", // 是否外链[有值则是外链]
          isKeepAlive: "1", // 是否缓存路由数据[0是，1否]
          isFull: "1", // 是否缓存全屏[0是，1否]
          isAffix: "1" // 是否缓存固定路由[0是，1否]
        }
      },
      {
        path: "/encryption", // [唯一]
        component: () => import("@/views/utility/encryption.vue"),
        meta: {
          title: "在线加密解密", // 标题
          enName: "Encryption", // 英文名称
          icon: "Lock", // 图标
          isHide: "0", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
          isLink: "", // 是否外链[有值则是外链]
          isKeepAlive: "1", // 是否缓存路由数据[0是，1否]
          isFull: "1", // 是否缓存全屏[0是，1否]
          isAffix: "1" // 是否缓存固定路由[0是，1否]
        }
      },
      {
        path: "/time_change", // [唯一]
        component: () => import("@/views/utility/time_change.vue"),
        meta: {
          title: "时间戳转换", // 标题
          enName: "Time", // 英文名称
          icon: "Timer", // 图标
          isHide: "0", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
          isLink: "", // 是否外链[有值则是外链]
          isKeepAlive: "1", // 是否缓存路由数据[0是，1否]
          isFull: "1", // 是否缓存全屏[0是，1否]
          isAffix: "1" // 是否缓存固定路由[0是，1否]
        }
      }
    ]
  },
  {
    path: "/device_manager", // [唯一]
    component: Layout,
    meta: {
      title: "云真机", // 标题
      enName: "YUN Device", // 英文名称
      icon: "MostlyCloudy", // 图标 HomeFilled
      isHide: "1", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
      isLink: "", // 是否外链[有值则是外链]
      isKeepAlive: "0", // 是否缓存路由数据[0是，1否]
      isFull: "1", // 是否缓存全屏[0是，1否]
      isAffix: "0" // 是否缓存固定路由[0是，1否]
    },
    children: [
      {
        path: "/device", // [唯一]
        component: () => import("@/views/device_view/device.vue"),
        meta: {
          title: "云真机", // 标题
          enName: "Package Manage", // 英文名称
          icon: "Cellphone", // 图标
          isHide: "1", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
          isLink: "", // 是否外链[有值则是外链]
          isKeepAlive: "1", // 是否缓存路由数据[0是，1否]
          isFull: "1", // 是否缓存全屏[0是，1否]
          isAffix: "1" // 是否缓存固定路由[0是，1否]
        }
      }
    ]
  },
  {
    path: "/api_auto", // 路由访问路径[唯一]"
    component: Layout,
    meta: {
      title: "接口自动化",
      enName: "API Auto",
      icon: "Connection",
      isHide: "1",
      isLink: "",
      isKeepAlive: "0",
      isFull: "1",
      isAffix: "0"
    },
    children: [
      {
        path: "/project", // [唯一]
        component: () => import("@/views/api_view/api_project.vue"),
        meta: {
          title: "接口管理", // 标题
          enName: "API Manage", // 英文名称
          icon: "Connection", // 图标
          isHide: "1", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
          isLink: "", // 是否外链[有值则是外链]
          isKeepAlive: "1", // 是否缓存路由数据[0是，1否]
          isFull: "1", // 是否缓存全屏[0是，1否]
          isAffix: "1" // 是否缓存固定路由[0是，1否]
        }
      },
      {
        path: "/_api_script", // [唯一]
        component: () => import("@/views/api_view/api_script.vue"),
        meta: {
          title: "API-场景管理", // 标题
          enName: "API Manage", // 英文名称
          icon: "Memo", // 图标
          isHide: "1", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
          isLink: "", // 是否外链[有值则是外链]
          isKeepAlive: "1", // 是否缓存路由数据[0是，1否]
          isFull: "1", // 是否缓存全屏[0是，1否]
          isAffix: "1" // 是否缓存固定路由[0是，1否]
        }
      },
      {
        path: "/_api_result", // [唯一]
        component: () => import("@/views/api_view/api_result_list.vue"),
        meta: {
          title: "API-结果", // 标题
          enName: "API Manage", // 英文名称
          icon: "Document", // 图标
          isHide: "1", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
          isLink: "", // 是否外链[有值则是外链]
          isKeepAlive: "1", // 是否缓存路由数据[0是，1否]
          isFull: "1", // 是否缓存全屏[0是，1否]
          isAffix: "1" // 是否缓存固定路由[0是，1否]
        }
      }
    ]
  },
  {
    path: "/web_auto", // 路由访问路径[唯一]
    component: Layout, // 登录进入这个页面，这个页面是整个布局
    meta: {
      title: "WEB管理", // 标题
      enName: "Web Auto", // 英文名称
      icon: "HelpFilled", // 图标
      isHide: "1", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
      isLink: "", // 是否外链[有值则是外链]
      isKeepAlive: "0", // 是否缓存路由数据[0是，1否]
      isFull: "0", // 是否缓存全屏[0是，1否]
      isAffix: "0" // 是否缓存固定路由[0是，1否]
    },
    children: [
      {
        path: "/element_manager", // [唯一]
        component: () => import("@/views/web_view/element_manager.vue"),
        meta: {
          title: "元素管理", // 标题
          enName: "Element Manage", // 英文名称
          icon: "ElementPlus", // 图标
          isHide: "1", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
          isLink: "", // 是否外链[有值则是外链]
          isKeepAlive: "1", // 是否缓存路由数据[0是，1否]
          isFull: "1", // 是否缓存全屏[0是，1否]
          isAffix: "1" // 是否缓存固定路由[0是，1否]
        }
      },
      {
        path: "/web", // [唯一]
        component: () => import("@/views/web_view/web.vue"),
        meta: {
          title: "Web 自动化", // 标题
          enName: "Web Auto", // 英文名称
          icon: "ChromeFilled", // 图标
          isHide: "1", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
          isLink: "", // 是否外链[有值则是外链]
          isKeepAlive: "1", // 是否缓存路由数据[0是，1否]
          isFull: "1", // 是否缓存全屏[0是，1否]
          isAffix: "1" // 是否缓存固定路由[0是，1否]
        }
      },
      {
        path: "/web_group", // [唯一]
        component: () => import("@/views/web_view/web_group.vue"),
        meta: {
          title: "Web-场景管理", // 标题
          enName: "Group Manage", // 英文名称
          icon: "Memo", // 图标
          isHide: "1", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
          isLink: "", // 是否外链[有值则是外链]
          isKeepAlive: "1", // 是否缓存路由数据[0是，1否]
          isFull: "1", // 是否缓存全屏[0是，1否]
          isAffix: "1" // 是否缓存固定路由[0是，1否]
        }
      },
      {
        path: "/web_result_list", // [唯一]
        component: () => import("@/views/web_view/web_result_list.vue"),
        meta: {
          title: "Web结果", // 标题
          enName: "Web Result", // 英文名称
          icon: "Document", // 图标
          isHide: "1", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
          isLink: "", // 是否外链[有值则是外链]
          isKeepAlive: "1", // 是否缓存路由数据[0是，1否]
          isFull: "1", // 是否缓存全屏[0是，1否]
          isAffix: "1" // 是否缓存固定路由[0是，1否]
        }
      }
    ]
  },
  {
    path: "/app_auto", // 路由访问路径[唯一]
    component: Layout, // 登录进入这个页面，这个页面是整个布局
    meta: {
      title: "APP管理", // 标题
      enName: "APP Auto", // 英文名称
      icon: "Iphone", // 图标
      isHide: "1", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
      isLink: "", // 是否外链[有值则是外链]
      isKeepAlive: "0", // 是否缓存路由数据[0是，1否]
      isFull: "0", // 是否缓存全屏[0是，1否]
      isAffix: "0" // 是否缓存固定路由[0是，1否]
    },
    children: [
      {
        path: "/device_install", // [唯一]
        component: () => import("@/views/app_view/device_install.vue"),
        meta: {
          title: "包体管理", // 标题
          enName: "Package Manage", // 英文名称
          icon: "SetUp", // 图标
          isHide: "1", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
          isLink: "", // 是否外链[有值则是外链]
          isKeepAlive: "1", // 是否缓存路由数据[0是，1否]
          isFull: "1", // 是否缓存全屏[0是，1否]
          isAffix: "1" // 是否缓存固定路由[0是，1否]
        }
      },
      {
        path: "/app_auto", // [唯一]
        component: () => import("@/views/app_view/app.vue"),
        meta: {
          title: "APP自动化", // 标题
          enName: "APP Auto", // 英文名称
          icon: "Iphone", // 图标
          isHide: "1", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
          isLink: "", // 是否外链[有值则是外链]
          isKeepAlive: "1", // 是否缓存路由数据[0是，1否]
          isFull: "1", // 是否缓存全屏[0是，1否]
          isAffix: "1" // 是否缓存固定路由[0是，1否]
        }
      },
      {
        path: "/app_img", // [唯一]
        component: () => import("@/views/app_view/img.vue"),
        meta: {
          title: "图像库", // 标题
          enName: "Image Library", // 英文名称
          icon: "PictureFilled", // 图标
          isHide: "1", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
          isLink: "", // 是否外链[有值则是外链]
          isKeepAlive: "1", // 是否缓存路由数据[0是，1否]
          isFull: "1", // 是否缓存全屏[0是，1否]
          isAffix: "1" // 是否缓存固定路由[0是，1否]
        }
      },
      {
        path: "/app_result_list", // [唯一]
        component: () => import("@/views/app_view/app_result_list.vue"),
        meta: {
          title: "APP结果", // 标题
          enName: "Test Result", // 英文名称
          icon: "Document", // 图标
          isHide: "1", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
          isLink: "", // 是否外链[有值则是外链]
          isKeepAlive: "1", // 是否缓存路由数据[0是，1否]
          isFull: "1", // 是否缓存全屏[0是，1否]
          isAffix: "1" // 是否缓存固定路由[0是，1否]
        }
      }
    ]
  },
  {
    path: "/task",
    component: Layout,
    meta: {
      title: "任务管理",
      enName: "Task Manage",
      icon: "Setting", // 图标
      isHide: "1", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
      isLink: "", // 是否外链[有值则是外链]
      isKeepAlive: "0", // 是否缓存路由数据[0是，1否]
      isFull: "0", // 是否缓存全屏[0是，1否]
      isAffix: "0" // 是否缓存固定路由[0是，1否]
    },
    children: [
      {
        path: "/notice", // [唯一]
        component: () => import("@/views/task_view/notice.vue"),
        meta: {
          title: "消息通知", // 标题
          enName: "Notice", // 英文名称
          icon: "Message", // 图标
          isHide: "1", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
          isLink: "",
          isKeepAlive: "1",
          isFull: "1",
          isAffix: "1"
        }
      },
      {
        path: "/scheduled_task", // [唯一]
        component: () => import("@/views/task_view/task.vue"),
        meta: {
          title: "定时任务", // 标题
          enName: "Scheduled tasks", // 英文名称
          icon: "List", // 图标
          isHide: "1", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
          isLink: "",
          isKeepAlive: "1",
          isFull: "1",
          isAffix: "1"
        }
      }
    ]
  },
  {
    path: "/user_view", // 路由访问路径[唯一]
    component: Layout, // 登录进入这个页面，这个页面是整个布局
    meta: {
      title: "系统管理", // 标题
      enName: "User Manage", // 英文名称
      icon: "Tools", // 图标
      isHide: "1", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
      isLink: "", // 是否外链[有值则是外链]
      isKeepAlive: "0", // 是否缓存路由数据[0是，1否]
      isFull: "0", // 是否缓存全屏[0是，1否]
      isAffix: "0" // 是否缓存固定路由[0是，1否]
    },
    children: [
      {
        path: "/user_role", // [唯一]
        component: () => import("@/views/user_view/role.vue"),
        meta: {
          title: "角色管理", // 标题
          enName: "Role Manage", // 英文名称
          icon: "Avatar", // 图标
          isHide: "0", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
          isLink: "",
          isKeepAlive: "1",
          isFull: "1",
          isAffix: "1" // 是否缓存固定路由[0是，1否]
        }
      },
      {
        path: "/user_manage", // [唯一]
        component: () => import("@/views/user_view/user.vue"),
        meta: {
          title: "用户中心", // 标题
          enName: "User Manage", // 英文名称
          icon: "UserFilled", // 图标
          isHide: "0", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
          isLink: "", // 是否外链[有值则是外链]
          isKeepAlive: "1", // 是否缓存路由数据[0是，1否]
          isFull: "1", // 是否缓存全屏[0是，1否]
          isAffix: "1" // 是否缓存固定路由[0是，1否]
        }
      },
      {
        path: "/login_log", // [唯一]
        component: () => import("@/views/user_view/login_log.vue"),
        meta: {
          title: "登录日志", // 标题
          enName: "Login Log", // 英文名称
          icon: "Calendar", // 图标
          isHide: "0", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
          isLink: "", // 是否外链[有值则是外链]
          isKeepAlive: "1", // 是否缓存路由数据[0是，1否]
          isFull: "1", // 是否缓存全屏[0是，1否]
          isAffix: "1" // 是否缓存固定路由[0是，1否]
        }
      },
      {
        path: "/action_log", // [唯一]
        component: () => import("@/views/user_view/action_log.vue"),
        meta: {
          title: "操作日志", // 标题
          enName: "Action Log", // 英文名称
          icon: "Memo", // 图标
          isHide: "0", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
          isLink: "", // 是否外链[有值则是外链]
          isKeepAlive: "1", // 是否缓存路由数据[0是，1否]
          isFull: "1", // 是否缓存全屏[0是，1否]
          isAffix: "1" // 是否缓存固定路由[0是，1否]
        }
      }
    ]
  },
  {
    path: "/app_report", // 路由访问路径[唯一]
    component: () => import("@/views/app_view/app_report.vue"),
    meta: {
      title: "APP测试报告", // 标题
      enName: "Test Report", // 英文名称
      icon: "Iphone", // 图标
      isHide: "0", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
      isLink: "", // 是否外链[有值则是外链]
      isKeepAlive: "0", // 是否缓存路由数据[0是，1否]
      isFull: "0", // 是否缓存全屏[0是，1否]
      isAffix: "0" // 是否缓存固定路由[0是，1否]
    }
  },
  {
    path: "/app_report", // 路由访问路径[唯一]
    component: () => import("@/views/app_view/app_report.vue"),
    meta: {
      title: "APP测试报告", // 标题
      enName: "Test Report", // 英文名称
      icon: "Iphone", // 图标
      isHide: "0", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
      isLink: "", // 是否外链[有值则是外链]
      isKeepAlive: "0", // 是否缓存路由数据[0是，1否]
      isFull: "0", // 是否缓存全屏[0是，1否]
      isAffix: "0" // 是否缓存固定路由[0是，1否]
    }
  },
  {
    path: "/_api_report", // 路由访问路径[唯一]
    component: () => import("@/views/api_view/api_report.vue"),
    meta: {
      title: "API测试报告", // 标题
      enName: "Test Report", // 英文名称
      icon: "Iphone", // 图标
      isHide: "0", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
      isLink: "", // 是否外链[有值则是外链]
      isKeepAlive: "0", // 是否缓存路由数据[0是，1否]
      isFull: "0", // 是否缓存全屏[0是，1否]
      isAffix: "0" // 是否缓存固定路由[0是，1否]
    }
  },
  {
    path: "/web_report", // 路由访问路径[唯一]
    component: () => import("@/views/web_view/web_report.vue"),
    meta: {
      title: "WEB测试报告", // 标题
      enName: "Web Report", // 英文名称
      icon: "ChromeFilled", // 图标
      isHide: "0", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
      isLink: "", // 是否外链[有值则是外链]
      isKeepAlive: "0", // 是否缓存路由数据[0是，1否]
      isFull: "0", // 是否缓存全屏[0是，1否]
      isAffix: "0" // 是否缓存固定路由[0是，1否]
    }
  },
  {
    path: "/system/static", // 路由访问路径[唯一]
    name: "staticPage", // 命名路由[唯一]
    component: Layout, // 一级路由，可以将子路由放置Main模块中
    meta: {
      title: "静态路由", // 标题
      enName: "Static Router", // 英文名称
      icon: "House", // 图标
      isHide: "0", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
      isLink: "", // 是否外链[有值则是外链]
      isKeepAlive: "0", // 是否缓存路由数据[0是，1否]
      isFull: "0", // 是否缓存全屏[0是，1否]
      isAffix: "0", // 是否缓存固定路由[0是，1否]
      activeMenu: HOME_URL // 默认选中哪个路由
    },
    children: [
      {
        path: "/system/dict/data/:dictType", // 路由访问路径[唯一]
        name: "dictDataPage", // 命名路由[唯一]
        component: () => import("@/views/system/dict/data.vue"), // 一级路由，可以将子路由放置Main模块中
        meta: {
          title: "字典详情", // 标题
          enName: "DictData Manage", // 英文名称
          icon: "Flag", // 图标
          isHide: "0", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
          isLink: "", // 是否外链[有值则是外链]
          isKeepAlive: "0", // 是否缓存路由数据[0是，1否]
          isFull: "1", // 是否缓存全屏[0是，1否]
          isAffix: "1", // 是否缓存固定路由[0是，1否]
          activeMenu: "/system/dict/type" // 默认选中哪个路由
        }
      }
    ]
  }
];

/**
 * errorRouter (错误页面路由)
 */
export const errorRouter = [
  {
    path: "/403",
    name: "403",
    component: () => import("@/views/error/403.vue"),
    meta: {
      title: "403页面",
      enName: "403 Page", // 英文名称
      icon: "QuestionFilled", // 菜单图标
      isHide: "1", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
      isLink: "1", // 是否外链[有值则是外链]
      isKeepAlive: "0", // 是否缓存路由数据[0是，1否]
      isFull: "1", // 是否缓存全屏[0是，1否]
      isAffix: "1" // 是否缓存固定路由[0是，1否]
    }
  },
  {
    path: "/404",
    name: "404",
    component: () => import("@/views/error/404.vue"),
    meta: {
      title: "404页面",
      enName: "404 Page", // 英文名称
      icon: "CircleCloseFilled", // 菜单图标
      isHide: "1", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
      isLink: "1", // 是否外链[有值则是外链]
      isKeepAlive: "0", // 是否缓存路由数据[0是，1否]
      isFull: "1", // 是否缓存全屏[0是，1否]
      isAffix: "1" // 是否缓存固定路由[0是，1否]
    }
  },
  {
    path: "/500",
    name: "500",
    component: () => import("@/views/error/500.vue"),
    meta: {
      title: "500页面",
      enName: "500 Page", // 英文名称
      icon: "WarningFilled", // 图标
      isHide: "1", // 代表路由在菜单中是否隐藏，是否隐藏[0隐藏，1显示]
      isLink: "1", // 是否外链[有值则是外链]
      isKeepAlive: "0", // 是否缓存路由数据[0是，1否]
      isFull: "1", // 是否缓存全屏[0是，1否]
      isAffix: "1" // 是否缓存固定路由[0是，1否]
    }
  },
  // 找不到path将跳转404页面
  {
    path: "/:pathMatch(.*)*",
    component: () => import("@/views/error/404.vue")
  }
];

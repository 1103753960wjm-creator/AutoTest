# TestHub API
**Version**: 1.0.0

Test Case Management Platform API

## 环境配置

- **开发环境 (DEV)**: `http://localhost:8000/`
- **测试环境 (TEST)**: 待定
- **生产环境 (PROD)**: 待定
- **认证方式**: Bearer Token (JWT), 将 Token 放入请求头 `Authorization: Bearer <token>`
- **默认 Content-Type**: `application/json`

## 平台核心概念：环境变量配置说明

TestHub 平台在自动化测试（API接口自动化、Web UI 自动化、APP 自动化）中支持**环境变量**来管理不同的参数、域名与测试数据。环境变量分为以下两类：

### 1. 全局环境变量 (Global Variables)
- **作用域**：跨项目、跨模块的全局范围。
- **使用场景**：通常用于存储通用的数据，如 `BASE_URL`，全局测试用的公有账号、全平台公用的 Token 或通用的数据库连接信息。
- **优先级**：最低。当与局部环境变量出现重名时，会被局部变量**覆盖**。

### 2. 局部环境变量 (Local Variables)
- **作用域**：仅在绑定的特定 **项目(Project)** 或 **测试套件(Suite)** 内生效。
- **使用场景**：用于存储特定业务线的数据，例如某个独立微服务的 URL、当前测试场景的特有用户密码，或者在运行某个测试套件时动态生成的临时参数。
- **优先级**：最高。在同一项目中定义的局部变量，将覆盖同名的全局变量。

### 💡 变量提取与使用语法
在平台的请求体、Headers、或是断言条件中，均可以通过平台标准的插值语法读取环境配置（如 `{{变量名}}` 或 `${变量名}`，具体以平台前端提示规则为准）。

### 📝 实战示例：应该添加哪些环境变量？

#### 全局环境变量推荐 (Global)
在“配置中心”或“全局环境管理”中，通常添加所有测试项目共用的基石数据：
1. **`BASE_URL`**: `https://api.testhub.com/v1` （整个系统的核心网关）
2. **`ADMIN_TOKEN`**: `eyJhbGciOiJIUz...` （用于执行管理员级脚本的公共凭证）
3. **`DB_HOST`**: `192.168.1.100` （公用测试数据库地址）
4. **`DEFAULT_TIMEOUT`**: `5000` （全局默认超时时间）

#### 局部环境变量推荐 (Local)
在“具体项目设置”或“具体测试套件”中，应该添加只属于该上下文的私密或特定变量：
1. **`SERVICE_API_URL`**: `https://project-a.testhub.com` （微服务架构中，特定子服务的地址）
2. **`TEST_USER_ACCOUNT`**: `tester_01@demo.com` （专门分配给当前项目跑自动化测试的独立账号）
3. **`DYNAMIC_ORDER_ID`**: （可以留空，由前置脚本或响应提取器动态设值，专用于当前套件的上下文参数传递）

### ⚙️ 平台实操指南：如何添加与使用环境变量？

根据 TestHub 平台的界面设计，你可以按照以下完整步骤进行配置：

#### 第一步：新建环境与添加变量
1. 打开**新建环境**弹窗。
2. 填写 **环境名称**（如：`生产环境-全局` 或 `微服务A-测试环境`）。
3. 选择 **作用域**：
   - 🔵 **全局环境变量**：对所有项目生效。
   - ⚪ **局部环境变量**：仅对关联项目生效。
4. 在下方的**环境变量表格**中，点击 `+添加变量`。
5. 依次填写对应的 **变量名**（Key）、**初始值** 和 **当前值**，最后点击右下角的**创建**按钮。

#### 第二步：在接口自动化模块中使用
1. **绑定环境**：在接口请求页面的顶部，点击 **环境下拉框**，选中你刚才创建的环境。
2. **URL 中使用**：在 **输入请求URL** 框中，使用双大括号语法提取变量，例如：`{{BASE_URL}}/api/auth/login/`。
3. **Params / Headers 中使用**：
   - 切换到下方的 **Params** 或 **Headers** 选项卡。
   - 点击 `+添加行`。
   - 在 **Key** 列输入参数名（如 `Authorization`）。
   - 在 **Value** 列输入包含变量的值（如 `Bearer {{ADMIN_TOKEN}}`）。
   - 💡 *提示：你可以点击参数值和描述输入框旁边的小魔方/魔法棒辅助按钮，快捷完成变量插入或 AI 描述补全。*

## 接口列表

### 登录与权限管理
#### api_auth_login_create
**接口路径**: `/api/auth/login/`
**请求方式**: `POST`

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_auth_logout_create
**接口路径**: `/api/auth/logout/`
**请求方式**: `POST`

**描述**: 用户退出登录，将refresh token加入黑名单

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_auth_me_retrieve
**接口路径**: `/api/auth/me/`
**请求方式**: `GET`

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_auth_profile_retrieve
**接口路径**: `/api/auth/profile/`
**请求方式**: `GET`

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_auth_register_create
**接口路径**: `/api/auth/register/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `UserCreate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `UserCreate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `UserCreate`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `UserCreate`

---

#### api_auth_token_refresh_create
**接口路径**: `/api/auth/token/refresh/`
**请求方式**: `POST`

**描述**: Takes a refresh type JSON web token and returns an access type JSON web
token if the refresh token is valid.

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TokenRefresh`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TokenRefresh`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TokenRefresh`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TokenRefresh`

---

#### api_auth_users_list
**接口路径**: `/api/auth/users/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedUserList`

---

#### api_auth_users_create
**接口路径**: `/api/auth/users/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `User`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `User`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `User`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `User`

---

#### api_auth_users_retrieve
**接口路径**: `/api/auth/users/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer |  |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `User`

---

#### api_auth_users_update
**接口路径**: `/api/auth/users/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer |  |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `User`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `User`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `User`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `User`

---

#### api_auth_users_partial_update
**接口路径**: `/api/auth/users/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer |  |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedUser`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedUser`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedUser`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `User`

---

#### api_auth_users_destroy
**接口路径**: `/api/auth/users/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer |  |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_users_login_create
**接口路径**: `/api/users/login/`
**请求方式**: `POST`

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_users_logout_create
**接口路径**: `/api/users/logout/`
**请求方式**: `POST`

**描述**: 用户退出登录，将refresh token加入黑名单

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_users_me_retrieve
**接口路径**: `/api/users/me/`
**请求方式**: `GET`

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_users_profile_retrieve
**接口路径**: `/api/users/profile/`
**请求方式**: `GET`

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_users_register_create
**接口路径**: `/api/users/register/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `UserCreate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `UserCreate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `UserCreate`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `UserCreate`

---

#### api_users_token_refresh_create
**接口路径**: `/api/users/token/refresh/`
**请求方式**: `POST`

**描述**: Takes a refresh type JSON web token and returns an access type JSON web
token if the refresh token is valid.

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TokenRefresh`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TokenRefresh`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TokenRefresh`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TokenRefresh`

---

#### api_users_users_list
**接口路径**: `/api/users/users/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedUserList`

---

#### api_users_users_create
**接口路径**: `/api/users/users/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `User`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `User`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `User`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `User`

---

#### api_users_users_retrieve
**接口路径**: `/api/users/users/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer |  |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `User`

---

#### api_users_users_update
**接口路径**: `/api/users/users/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer |  |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `User`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `User`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `User`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `User`

---

#### api_users_users_partial_update
**接口路径**: `/api/users/users/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer |  |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedUser`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedUser`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedUser`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `User`

---

#### api_users_users_destroy
**接口路径**: `/api/users/users/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer |  |

**响应示例**:
- **状态码 `204`**: No response body

---

### 项目管理
#### api_projects_list
**接口路径**: `/api/projects/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| owner | query | 否 | integer |  |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |
| status | query | 否 | string | * `active` - 进行中 * `paused` - 暂停 * `completed` - 已完成 * `archived` - 已归档 |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedProjectList`

---

#### api_projects_create
**接口路径**: `/api/projects/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `ProjectCreate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `ProjectCreate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `ProjectCreate`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `ProjectCreate`

---

#### api_projects_retrieve
**接口路径**: `/api/projects/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer |  |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `Project`

---

#### api_projects_update
**接口路径**: `/api/projects/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer |  |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `Project`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `Project`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `Project`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `Project`

---

#### api_projects_partial_update
**接口路径**: `/api/projects/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer |  |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedProject`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedProject`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedProject`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `Project`

---

#### api_projects_destroy
**接口路径**: `/api/projects/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer |  |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_projects_environments_list
**接口路径**: `/api/projects/{project_id}/environments/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| project_id | path | 是 | integer |  |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedProjectEnvironmentList`

---

#### api_projects_environments_create
**接口路径**: `/api/projects/{project_id}/environments/`
**请求方式**: `POST`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| project_id | path | 是 | integer |  |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `ProjectEnvironment`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `ProjectEnvironment`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `ProjectEnvironment`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `ProjectEnvironment`

---

#### api_projects_members_retrieve
**接口路径**: `/api/projects/{project_id}/members/`
**请求方式**: `GET`

**描述**: 获取项目成员列表

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| project_id | path | 是 | integer |  |

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_projects_members_destroy
**接口路径**: `/api/projects/{project_id}/members/{member_id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| member_id | path | 是 | integer |  |
| project_id | path | 是 | integer |  |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_projects_members_add_create
**接口路径**: `/api/projects/{project_id}/members/add/`
**请求方式**: `POST`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| project_id | path | 是 | integer |  |

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_projects_all_retrieve
**接口路径**: `/api/projects/all/`
**请求方式**: `GET`

**描述**: 获取所有项目列表，用于下拉选择等场景

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_projects_batch_delete_create
**接口路径**: `/api/projects/batch-delete/`
**请求方式**: `POST`

**描述**: 批量删除项目

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_projects_list_retrieve
**接口路径**: `/api/projects/list/`
**请求方式**: `GET`

**描述**: 获取用户有权限访问的项目列表，用于下拉选择

**响应示例**:
- **状态码 `200`**: No response body

---

### 测试用例与套件
#### api_testcases_list
**接口路径**: `/api/testcases/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| page_size | query | 否 | integer | Number of results to return per page. |
| priority | query | 否 | string | * `low` - 低 * `medium` - 中 * `high` - 高 * `critical` - 紧急 |
| project | query | 否 | integer |  |
| search | query | 否 | string | A search term. |
| test_type | query | 否 | string | * `functional` - 功能测试 * `integration` - 集成测试 * `api` - API测试 * `ui` - UI测试 * `performance` - 性能测试 * `security` - 安全测试 |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedTestCaseListList`

---

#### api_testcases_create
**接口路径**: `/api/testcases/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCaseCreate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCaseCreate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCaseCreate`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `TestCaseCreate`

---

#### api_testcases_retrieve
**接口路径**: `/api/testcases/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer |  |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCase`

---

#### api_testcases_update
**接口路径**: `/api/testcases/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer |  |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCaseUpdate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCaseUpdate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCaseUpdate`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseUpdate`

---

#### api_testcases_partial_update
**接口路径**: `/api/testcases/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer |  |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedTestCaseUpdate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedTestCaseUpdate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedTestCaseUpdate`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseUpdate`

---

#### api_testcases_destroy
**接口路径**: `/api/testcases/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer |  |

**响应示例**:
- **状态码 `204`**: No response body

---

### 执行与报告
#### api_executions_history_list
**接口路径**: `/api/executions/history/`
**请求方式**: `GET`

**描述**: 测试执行历史视图集（只读）

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedTestRunCaseHistoryList`

---

#### api_executions_history_retrieve
**接口路径**: `/api/executions/history/{id}/`
**请求方式**: `GET`

**描述**: 测试执行历史视图集（只读）

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试执行历史. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestRunCaseHistory`

---

#### api_executions_plans_list
**接口路径**: `/api/executions/plans/`
**请求方式**: `GET`

**描述**: 测试计划视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedTestPlanList`

---

#### api_executions_plans_create
**接口路径**: `/api/executions/plans/`
**请求方式**: `POST`

**描述**: 测试计划视图集

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestPlan`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestPlan`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestPlan`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `TestPlan`

---

#### api_executions_plans_retrieve
**接口路径**: `/api/executions/plans/{id}/`
**请求方式**: `GET`

**描述**: 测试计划视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试计划. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestPlanDetail`

---

#### api_executions_plans_update
**接口路径**: `/api/executions/plans/{id}/`
**请求方式**: `PUT`

**描述**: 测试计划视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试计划. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestPlan`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestPlan`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestPlan`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestPlan`

---

#### api_executions_plans_partial_update
**接口路径**: `/api/executions/plans/{id}/`
**请求方式**: `PATCH`

**描述**: 测试计划视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试计划. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedTestPlan`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedTestPlan`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedTestPlan`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestPlan`

---

#### api_executions_plans_destroy
**接口路径**: `/api/executions/plans/{id}/`
**请求方式**: `DELETE`

**描述**: 测试计划视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试计划. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_executions_plans_testcases_by_projects_retrieve
**接口路径**: `/api/executions/plans/testcases_by_projects/`
**请求方式**: `GET`

**描述**: 根据项目获取测试用例

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestPlan`

---

#### api_executions_run_cases_list
**接口路径**: `/api/executions/run_cases/`
**请求方式**: `GET`

**描述**: 测试执行用例视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedTestRunCaseList`

---

#### api_executions_run_cases_create
**接口路径**: `/api/executions/run_cases/`
**请求方式**: `POST`

**描述**: 测试执行用例视图集

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestRunCase`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestRunCase`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestRunCase`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `TestRunCase`

---

#### api_executions_run_cases_retrieve
**接口路径**: `/api/executions/run_cases/{id}/`
**请求方式**: `GET`

**描述**: 测试执行用例视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试执行用例. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestRunCaseDetail`

---

#### api_executions_run_cases_update
**接口路径**: `/api/executions/run_cases/{id}/`
**请求方式**: `PUT`

**描述**: 测试执行用例视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试执行用例. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestRunCase`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestRunCase`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestRunCase`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestRunCase`

---

#### api_executions_run_cases_partial_update
**接口路径**: `/api/executions/run_cases/{id}/`
**请求方式**: `PATCH`

**描述**: 测试执行用例视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试执行用例. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedTestRunCase`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedTestRunCase`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedTestRunCase`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestRunCase`

---

#### api_executions_run_cases_destroy
**接口路径**: `/api/executions/run_cases/{id}/`
**请求方式**: `DELETE`

**描述**: 测试执行用例视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试执行用例. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_executions_run_cases_history_retrieve
**接口路径**: `/api/executions/run_cases/{id}/history/`
**请求方式**: `GET`

**描述**: 获取用例执行历史记录

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试执行用例. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestRunCase`

---

#### api_executions_run_cases_update_status_partial_update
**接口路径**: `/api/executions/run_cases/{id}/update_status/`
**请求方式**: `PATCH`

**描述**: 更新单个用例的执行状态，并自动创建历史记录

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试执行用例. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedTestRunCase`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedTestRunCase`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedTestRunCase`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestRunCase`

---

#### api_executions_runs_list
**接口路径**: `/api/executions/runs/`
**请求方式**: `GET`

**描述**: 测试执行视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedTestRunList`

---

#### api_executions_runs_create
**接口路径**: `/api/executions/runs/`
**请求方式**: `POST`

**描述**: 测试执行视图集

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestRun`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestRun`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestRun`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `TestRun`

---

#### api_executions_runs_retrieve
**接口路径**: `/api/executions/runs/{id}/`
**请求方式**: `GET`

**描述**: 测试执行视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试执行. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestRun`

---

#### api_executions_runs_update
**接口路径**: `/api/executions/runs/{id}/`
**请求方式**: `PUT`

**描述**: 测试执行视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试执行. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestRun`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestRun`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestRun`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestRun`

---

#### api_executions_runs_partial_update
**接口路径**: `/api/executions/runs/{id}/`
**请求方式**: `PATCH`

**描述**: 测试执行视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试执行. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedTestRun`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedTestRun`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedTestRun`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestRun`

---

#### api_executions_runs_destroy
**接口路径**: `/api/executions/runs/{id}/`
**请求方式**: `DELETE`

**描述**: 测试执行视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试执行. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_reports_reports_retrieve
**接口路径**: `/api/reports/reports/`
**请求方式**: `GET`

**描述**: 测试报告视图集

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_reports_reports_create
**接口路径**: `/api/reports/reports/`
**请求方式**: `POST`

**描述**: 测试报告视图集

**响应示例**:
- **状态码 `201`**: No response body

---

#### api_reports_reports_retrieve_2
**接口路径**: `/api/reports/reports/{id}/`
**请求方式**: `GET`

**描述**: 测试报告视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试报告. |

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_reports_reports_update
**接口路径**: `/api/reports/reports/{id}/`
**请求方式**: `PUT`

**描述**: 测试报告视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试报告. |

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_reports_reports_partial_update
**接口路径**: `/api/reports/reports/{id}/`
**请求方式**: `PATCH`

**描述**: 测试报告视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试报告. |

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_reports_reports_destroy
**接口路径**: `/api/reports/reports/{id}/`
**请求方式**: `DELETE`

**描述**: 测试报告视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试报告. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_reports_reports_ai_efficiency_retrieve
**接口路径**: `/api/reports/reports/ai_efficiency/`
**请求方式**: `GET`

**描述**: 获取AI效能分析

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_reports_reports_dashboard_retrieve
**接口路径**: `/api/reports/reports/dashboard/`
**请求方式**: `GET`

**描述**: 获取概览数据

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_reports_reports_defect_distribution_retrieve
**接口路径**: `/api/reports/reports/defect_distribution/`
**请求方式**: `GET`

**描述**: 获取缺陷分布 (按优先级)

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_reports_reports_execution_trend_retrieve
**接口路径**: `/api/reports/reports/execution_trend/`
**请求方式**: `GET`

**描述**: 获取每日执行趋势

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_reports_reports_failed_cases_top_retrieve
**接口路径**: `/api/reports/reports/failed_cases_top/`
**请求方式**: `GET`

**描述**: 获取失败用例TOP榜

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_reports_reports_status_distribution_retrieve
**接口路径**: `/api/reports/reports/status_distribution/`
**请求方式**: `GET`

**描述**: 获取执行状态分布

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_reports_reports_team_workload_retrieve
**接口路径**: `/api/reports/reports/team_workload/`
**请求方式**: `GET`

**描述**: 获取团队工作量

**响应示例**:
- **状态码 `200`**: No response body

---

### 评审管理
#### api_reviews_review_comments_list
**接口路径**: `/api/reviews/review-comments/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedTestCaseReviewCommentList`

---

#### api_reviews_review_comments_create
**接口路径**: `/api/reviews/review-comments/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCaseReviewCommentCreate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCaseReviewCommentCreate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCaseReviewCommentCreate`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `TestCaseReviewCommentCreate`

---

#### api_reviews_review_comments_retrieve
**接口路径**: `/api/reviews/review-comments/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 评审意见. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseReviewComment`

---

#### api_reviews_review_comments_update
**接口路径**: `/api/reviews/review-comments/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 评审意见. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCaseReviewCommentCreate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCaseReviewCommentCreate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCaseReviewCommentCreate`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseReviewCommentCreate`

---

#### api_reviews_review_comments_partial_update
**接口路径**: `/api/reviews/review-comments/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 评审意见. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedTestCaseReviewCommentCreate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedTestCaseReviewCommentCreate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedTestCaseReviewCommentCreate`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseReviewCommentCreate`

---

#### api_reviews_review_comments_destroy
**接口路径**: `/api/reviews/review-comments/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 评审意见. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_reviews_review_templates_list
**接口路径**: `/api/reviews/review-templates/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedReviewTemplateList`

---

#### api_reviews_review_templates_create
**接口路径**: `/api/reviews/review-templates/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `ReviewTemplateCreate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `ReviewTemplateCreate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `ReviewTemplateCreate`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `ReviewTemplateCreate`

---

#### api_reviews_review_templates_retrieve
**接口路径**: `/api/reviews/review-templates/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 评审模板. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ReviewTemplate`

---

#### api_reviews_review_templates_update
**接口路径**: `/api/reviews/review-templates/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 评审模板. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `ReviewTemplateCreate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `ReviewTemplateCreate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `ReviewTemplateCreate`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ReviewTemplateCreate`

---

#### api_reviews_review_templates_partial_update
**接口路径**: `/api/reviews/review-templates/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 评审模板. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedReviewTemplateCreate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedReviewTemplateCreate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedReviewTemplateCreate`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ReviewTemplateCreate`

---

#### api_reviews_review_templates_destroy
**接口路径**: `/api/reviews/review-templates/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 评审模板. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_reviews_reviews_list
**接口路径**: `/api/reviews/reviews/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedTestCaseReviewList`

---

#### api_reviews_reviews_create
**接口路径**: `/api/reviews/reviews/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCaseReviewCreate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCaseReviewCreate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCaseReviewCreate`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `TestCaseReviewCreate`

---

#### api_reviews_reviews_retrieve
**接口路径**: `/api/reviews/reviews/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试用例评审. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseReview`

---

#### api_reviews_reviews_update
**接口路径**: `/api/reviews/reviews/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试用例评审. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCaseReviewCreate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCaseReviewCreate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCaseReviewCreate`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseReviewCreate`

---

#### api_reviews_reviews_partial_update
**接口路径**: `/api/reviews/reviews/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试用例评审. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedTestCaseReviewCreate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedTestCaseReviewCreate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedTestCaseReviewCreate`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseReviewCreate`

---

#### api_reviews_reviews_destroy
**接口路径**: `/api/reviews/reviews/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试用例评审. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_reviews_reviews_assign_reviewers_create
**接口路径**: `/api/reviews/reviews/{id}/assign_reviewers/`
**请求方式**: `POST`

**描述**: 分配评审人员

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试用例评审. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCaseReview`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCaseReview`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCaseReview`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseReview`

---

#### api_reviews_reviews_submit_review_create
**接口路径**: `/api/reviews/reviews/{id}/submit_review/`
**请求方式**: `POST`

**描述**: 提交评审结果

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试用例评审. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCaseReview`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCaseReview`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCaseReview`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseReview`

---

#### api_reviews_reviews_my_reviews_retrieve
**接口路径**: `/api/reviews/reviews/my_reviews/`
**请求方式**: `GET`

**描述**: 获取我的评审任务

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseReview`

---

### 版本控制
#### api_versions_list
**接口路径**: `/api/versions/`
**请求方式**: `GET`

**描述**: 版本列表和创建视图

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedVersionList`

---

#### api_versions_create
**接口路径**: `/api/versions/`
**请求方式**: `POST`

**描述**: 版本列表和创建视图

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `VersionCreate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `VersionCreate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `VersionCreate`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `VersionCreate`

---

#### api_versions_retrieve
**接口路径**: `/api/versions/{id}/`
**请求方式**: `GET`

**描述**: 版本详情视图

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer |  |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `Version`

---

#### api_versions_update
**接口路径**: `/api/versions/{id}/`
**请求方式**: `PUT`

**描述**: 版本详情视图

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer |  |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `Version`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `Version`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `Version`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `Version`

---

#### api_versions_partial_update
**接口路径**: `/api/versions/{id}/`
**请求方式**: `PATCH`

**描述**: 版本详情视图

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer |  |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedVersion`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedVersion`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedVersion`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `Version`

---

#### api_versions_destroy
**接口路径**: `/api/versions/{id}/`
**请求方式**: `DELETE`

**描述**: 版本详情视图

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer |  |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_versions_batch_delete_create
**接口路径**: `/api/versions/batch-delete/`
**请求方式**: `POST`

**描述**: 批量删除版本

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_versions_projects_versions_retrieve
**接口路径**: `/api/versions/projects/{project_id}/versions/`
**请求方式**: `GET`

**描述**: 获取指定项目的版本列表

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| project_id | path | 是 | integer |  |

**响应示例**:
- **状态码 `200`**: No response body

---

### AI助手与配置
#### api_assistant_chat_send_message_create
**接口路径**: `/api/assistant/chat/send_message/`
**请求方式**: `POST`

**描述**: 发送消息到Dify API

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_assistant_config_dify_list
**接口路径**: `/api/assistant/config/dify/`
**请求方式**: `GET`

**描述**: 获取激活的配置

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedDifyConfigList`

---

#### api_assistant_config_dify_create
**接口路径**: `/api/assistant/config/dify/`
**请求方式**: `POST`

**描述**: 创建新配置

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `DifyConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `DifyConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `DifyConfig`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `DifyConfig`

---

#### api_assistant_config_dify_retrieve
**接口路径**: `/api/assistant/config/dify/{id}/`
**请求方式**: `GET`

**描述**: Dify配置管理ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this Dify配置. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `DifyConfig`

---

#### api_assistant_config_dify_update
**接口路径**: `/api/assistant/config/dify/{id}/`
**请求方式**: `PUT`

**描述**: 更新配置

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this Dify配置. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `DifyConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `DifyConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `DifyConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `DifyConfig`

---

#### api_assistant_config_dify_partial_update
**接口路径**: `/api/assistant/config/dify/{id}/`
**请求方式**: `PATCH`

**描述**: 部分更新配置

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this Dify配置. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedDifyConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedDifyConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedDifyConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `DifyConfig`

---

#### api_assistant_config_dify_destroy
**接口路径**: `/api/assistant/config/dify/{id}/`
**请求方式**: `DELETE`

**描述**: Dify配置管理ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this Dify配置. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_assistant_config_dify_test_connection_create
**接口路径**: `/api/assistant/config/dify/test_connection/`
**请求方式**: `POST`

**描述**: 测试Dify API连接

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `DifyConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `DifyConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `DifyConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `DifyConfig`

---

#### api_assistant_sessions_list
**接口路径**: `/api/assistant/sessions/`
**请求方式**: `GET`

**描述**: 智能助手会话视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedAssistantSessionList`

---

#### api_assistant_sessions_create
**接口路径**: `/api/assistant/sessions/`
**请求方式**: `POST`

**描述**: 智能助手会话视图集

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AssistantSessionCreate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AssistantSessionCreate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AssistantSessionCreate`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `AssistantSessionCreate`

---

#### api_assistant_sessions_retrieve
**接口路径**: `/api/assistant/sessions/{id}/`
**请求方式**: `GET`

**描述**: 智能助手会话视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | string |  |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AssistantSession`

---

#### api_assistant_sessions_update
**接口路径**: `/api/assistant/sessions/{id}/`
**请求方式**: `PUT`

**描述**: 智能助手会话视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | string |  |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AssistantSessionCreate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AssistantSessionCreate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AssistantSessionCreate`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AssistantSessionCreate`

---

#### api_assistant_sessions_partial_update
**接口路径**: `/api/assistant/sessions/{id}/`
**请求方式**: `PATCH`

**描述**: 智能助手会话视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | string |  |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedAssistantSessionCreate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedAssistantSessionCreate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedAssistantSessionCreate`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AssistantSessionCreate`

---

#### api_assistant_sessions_destroy
**接口路径**: `/api/assistant/sessions/{id}/`
**请求方式**: `DELETE`

**描述**: 智能助手会话视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | string |  |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_assistant_sessions_add_message_create
**接口路径**: `/api/assistant/sessions/{id}/add_message/`
**请求方式**: `POST`

**描述**: 添加消息到会话

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | string |  |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AssistantSession`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AssistantSession`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AssistantSession`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AssistantSession`

---

#### api_assistant_sessions_messages_retrieve
**接口路径**: `/api/assistant/sessions/{id}/messages/`
**请求方式**: `GET`

**描述**: 获取会话的聊天消息

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | string |  |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AssistantSession`

---

### 需求分析
#### api_requirement_analysis_ai_models_list
**接口路径**: `/api/requirement-analysis/ai-models/`
**请求方式**: `GET`

**描述**: AI模型配置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedAIModelConfigList`

---

#### api_requirement_analysis_ai_models_create
**接口路径**: `/api/requirement-analysis/ai-models/`
**请求方式**: `POST`

**描述**: AI模型配置视图集

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AIModelConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AIModelConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AIModelConfig`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `AIModelConfig`

---

#### api_requirement_analysis_ai_models_retrieve
**接口路径**: `/api/requirement-analysis/ai-models/{id}/`
**请求方式**: `GET`

**描述**: AI模型配置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI模型配置. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AIModelConfig`

---

#### api_requirement_analysis_ai_models_update
**接口路径**: `/api/requirement-analysis/ai-models/{id}/`
**请求方式**: `PUT`

**描述**: AI模型配置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI模型配置. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AIModelConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AIModelConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AIModelConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AIModelConfig`

---

#### api_requirement_analysis_ai_models_partial_update
**接口路径**: `/api/requirement-analysis/ai-models/{id}/`
**请求方式**: `PATCH`

**描述**: AI模型配置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI模型配置. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedAIModelConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedAIModelConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedAIModelConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AIModelConfig`

---

#### api_requirement_analysis_ai_models_destroy
**接口路径**: `/api/requirement-analysis/ai-models/{id}/`
**请求方式**: `DELETE`

**描述**: AI模型配置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI模型配置. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_requirement_analysis_ai_models_disable_create
**接口路径**: `/api/requirement-analysis/ai-models/{id}/disable/`
**请求方式**: `POST`

**描述**: 禁用配置

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI模型配置. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AIModelConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AIModelConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AIModelConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AIModelConfig`

---

#### api_requirement_analysis_ai_models_enable_create
**接口路径**: `/api/requirement-analysis/ai-models/{id}/enable/`
**请求方式**: `POST`

**描述**: 启用配置

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI模型配置. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AIModelConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AIModelConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AIModelConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AIModelConfig`

---

#### api_requirement_analysis_ai_models_test_connection_create
**接口路径**: `/api/requirement-analysis/ai-models/{id}/test_connection/`
**请求方式**: `POST`

**描述**: 测试模型连接

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI模型配置. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AIModelConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AIModelConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AIModelConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AIModelConfig`

---

#### api_requirement_analysis_analyses_list
**接口路径**: `/api/requirement-analysis/analyses/`
**请求方式**: `GET`

**描述**: 需求分析视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedRequirementAnalysisList`

---

#### api_requirement_analysis_analyses_retrieve
**接口路径**: `/api/requirement-analysis/analyses/{id}/`
**请求方式**: `GET`

**描述**: 需求分析视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 需求分析. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `RequirementAnalysis`

---

#### api_requirement_analysis_analyses_requirements_retrieve
**接口路径**: `/api/requirement-analysis/analyses/{id}/requirements/`
**请求方式**: `GET`

**描述**: 获取分析的需求列表

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 需求分析. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `RequirementAnalysis`

---

#### api_requirement_analysis_analyze_text_create
**接口路径**: `/api/requirement-analysis/analyze-text/`
**请求方式**: `POST`

**描述**: 分析手动输入的需求文本

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_requirement_analysis_auto_reviews_list
**接口路径**: `/api/requirement-analysis/auto-reviews/`
**请求方式**: `GET`

**描述**: 自动 AI 评审记录统一入口视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedTaskAutoReviewRecordList`

---

#### api_requirement_analysis_auto_reviews_retrieve
**接口路径**: `/api/requirement-analysis/auto-reviews/{id}/`
**请求方式**: `GET`

**描述**: 自动 AI 评审记录统一入口视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 自动 AI 评审记录. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TaskAutoReviewRecord`

---

#### api_requirement_analysis_config_check_retrieve
**接口路径**: `/api/requirement-analysis/config/check/`
**请求方式**: `GET`

**描述**: 检查AI配置状态

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_requirement_analysis_documents_list
**接口路径**: `/api/requirement-analysis/documents/`
**请求方式**: `GET`

**描述**: 需求文档视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedRequirementDocumentList`

---

#### api_requirement_analysis_documents_create
**接口路径**: `/api/requirement-analysis/documents/`
**请求方式**: `POST`

**描述**: 需求文档视图集

**请求体 (Body)**:
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `DocumentUpload`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `DocumentUpload`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `DocumentUpload`

---

#### api_requirement_analysis_documents_retrieve
**接口路径**: `/api/requirement-analysis/documents/{id}/`
**请求方式**: `GET`

**描述**: 需求文档视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 需求文档. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `RequirementDocument`

---

#### api_requirement_analysis_documents_update
**接口路径**: `/api/requirement-analysis/documents/{id}/`
**请求方式**: `PUT`

**描述**: 需求文档视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 需求文档. |

**请求体 (Body)**:
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `RequirementDocument`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `RequirementDocument`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `RequirementDocument`

---

#### api_requirement_analysis_documents_partial_update
**接口路径**: `/api/requirement-analysis/documents/{id}/`
**请求方式**: `PATCH`

**描述**: 需求文档视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 需求文档. |

**请求体 (Body)**:
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedRequirementDocument`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedRequirementDocument`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `RequirementDocument`

---

#### api_requirement_analysis_documents_destroy
**接口路径**: `/api/requirement-analysis/documents/{id}/`
**请求方式**: `DELETE`

**描述**: 需求文档视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 需求文档. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_requirement_analysis_documents_analyze_create
**接口路径**: `/api/requirement-analysis/documents/{id}/analyze/`
**请求方式**: `POST`

**描述**: 分析需求文档

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 需求文档. |

**请求体 (Body)**:
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `RequirementDocument`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `RequirementDocument`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `RequirementDocument`

---

#### api_requirement_analysis_documents_extract_text_retrieve
**接口路径**: `/api/requirement-analysis/documents/{id}/extract_text/`
**请求方式**: `GET`

**描述**: 提取文档文本

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 需求文档. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `RequirementDocument`

---

#### api_requirement_analysis_generation_config_list
**接口路径**: `/api/requirement-analysis/generation-config/`
**请求方式**: `GET`

**描述**: 生成行为配置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedGenerationConfigList`

---

#### api_requirement_analysis_generation_config_create
**接口路径**: `/api/requirement-analysis/generation-config/`
**请求方式**: `POST`

**描述**: 生成行为配置视图集

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `GenerationConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `GenerationConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `GenerationConfig`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `GenerationConfig`

---

#### api_requirement_analysis_generation_config_retrieve
**接口路径**: `/api/requirement-analysis/generation-config/{id}/`
**请求方式**: `GET`

**描述**: 生成行为配置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 生成行为配置. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `GenerationConfig`

---

#### api_requirement_analysis_generation_config_update
**接口路径**: `/api/requirement-analysis/generation-config/{id}/`
**请求方式**: `PUT`

**描述**: 生成行为配置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 生成行为配置. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `GenerationConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `GenerationConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `GenerationConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `GenerationConfig`

---

#### api_requirement_analysis_generation_config_partial_update
**接口路径**: `/api/requirement-analysis/generation-config/{id}/`
**请求方式**: `PATCH`

**描述**: 生成行为配置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 生成行为配置. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedGenerationConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedGenerationConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedGenerationConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `GenerationConfig`

---

#### api_requirement_analysis_generation_config_destroy
**接口路径**: `/api/requirement-analysis/generation-config/{id}/`
**请求方式**: `DELETE`

**描述**: 生成行为配置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 生成行为配置. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_requirement_analysis_generation_config_disable_create
**接口路径**: `/api/requirement-analysis/generation-config/{id}/disable/`
**请求方式**: `POST`

**描述**: 禁用配置

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 生成行为配置. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `GenerationConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `GenerationConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `GenerationConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `GenerationConfig`

---

#### api_requirement_analysis_generation_config_enable_create
**接口路径**: `/api/requirement-analysis/generation-config/{id}/enable/`
**请求方式**: `POST`

**描述**: 启用配置

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 生成行为配置. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `GenerationConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `GenerationConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `GenerationConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `GenerationConfig`

---

#### api_requirement_analysis_generation_config_active_retrieve
**接口路径**: `/api/requirement-analysis/generation-config/active/`
**请求方式**: `GET`

**描述**: 获取活跃的生成配置

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `GenerationConfig`

---

#### api_requirement_analysis_prompts_list
**接口路径**: `/api/requirement-analysis/prompts/`
**请求方式**: `GET`

**描述**: 提示词配置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedPromptConfigList`

---

#### api_requirement_analysis_prompts_create
**接口路径**: `/api/requirement-analysis/prompts/`
**请求方式**: `POST`

**描述**: 提示词配置视图集

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PromptConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PromptConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PromptConfig`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `PromptConfig`

---

#### api_requirement_analysis_prompts_retrieve
**接口路径**: `/api/requirement-analysis/prompts/{id}/`
**请求方式**: `GET`

**描述**: 提示词配置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 提示词配置. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PromptConfig`

---

#### api_requirement_analysis_prompts_update
**接口路径**: `/api/requirement-analysis/prompts/{id}/`
**请求方式**: `PUT`

**描述**: 提示词配置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 提示词配置. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PromptConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PromptConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PromptConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PromptConfig`

---

#### api_requirement_analysis_prompts_partial_update
**接口路径**: `/api/requirement-analysis/prompts/{id}/`
**请求方式**: `PATCH`

**描述**: 提示词配置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 提示词配置. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedPromptConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedPromptConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedPromptConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PromptConfig`

---

#### api_requirement_analysis_prompts_destroy
**接口路径**: `/api/requirement-analysis/prompts/{id}/`
**请求方式**: `DELETE`

**描述**: 提示词配置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 提示词配置. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_requirement_analysis_prompts_disable_create
**接口路径**: `/api/requirement-analysis/prompts/{id}/disable/`
**请求方式**: `POST`

**描述**: 禁用配置

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 提示词配置. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PromptConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PromptConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PromptConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PromptConfig`

---

#### api_requirement_analysis_prompts_enable_create
**接口路径**: `/api/requirement-analysis/prompts/{id}/enable/`
**请求方式**: `POST`

**描述**: 启用配置

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 提示词配置. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PromptConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PromptConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PromptConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PromptConfig`

---

#### api_requirement_analysis_prompts_load_defaults_retrieve
**接口路径**: `/api/requirement-analysis/prompts/load_defaults/`
**请求方式**: `GET`

**描述**: 加载默认提示词

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PromptConfig`

---

#### api_requirement_analysis_requirements_list
**接口路径**: `/api/requirement-analysis/requirements/`
**请求方式**: `GET`

**描述**: 业务需求视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedBusinessRequirementList`

---

#### api_requirement_analysis_requirements_retrieve
**接口路径**: `/api/requirement-analysis/requirements/{id}/`
**请求方式**: `GET`

**描述**: 业务需求视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 业务需求. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `BusinessRequirement`

---

#### api_requirement_analysis_requirements_generate_test_cases_create
**接口路径**: `/api/requirement-analysis/requirements/generate_test_cases/`
**请求方式**: `POST`

**描述**: 为选中的需求生成测试用例

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `BusinessRequirement`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `BusinessRequirement`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `BusinessRequirement`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `BusinessRequirement`

---

#### api_requirement_analysis_tasks_list
**接口路径**: `/api/requirement-analysis/tasks/`
**请求方式**: `GET`

**描述**: 分析任务视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedAnalysisTaskList`

---

#### api_requirement_analysis_tasks_retrieve
**接口路径**: `/api/requirement-analysis/tasks/{id}/`
**请求方式**: `GET`

**描述**: 分析任务视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 分析任务. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AnalysisTask`

---

#### api_requirement_analysis_tasks_progress_retrieve
**接口路径**: `/api/requirement-analysis/tasks/{id}/progress/`
**请求方式**: `GET`

**描述**: 获取任务进度

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 分析任务. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AnalysisTask`

---

#### api_requirement_analysis_test_cases_list
**接口路径**: `/api/requirement-analysis/test-cases/`
**请求方式**: `GET`

**描述**: 生成的测试用例视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| page_size | query | 否 | integer | Number of results to return per page. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedGeneratedTestCaseList`

---

#### api_requirement_analysis_test_cases_retrieve
**接口路径**: `/api/requirement-analysis/test-cases/{id}/`
**请求方式**: `GET`

**描述**: 生成的测试用例视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 生成的测试用例. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `GeneratedTestCase`

---

#### api_requirement_analysis_test_cases_partial_update
**接口路径**: `/api/requirement-analysis/test-cases/{id}/`
**请求方式**: `PATCH`

**描述**: 生成的测试用例视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 生成的测试用例. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedGeneratedTestCase`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedGeneratedTestCase`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedGeneratedTestCase`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `GeneratedTestCase`

---

#### api_requirement_analysis_testcase_generation_list
**接口路径**: `/api/requirement-analysis/testcase-generation/`
**请求方式**: `GET`

**描述**: 测试用例生成任务视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| page_size | query | 否 | integer | Number of results to return per page. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedTestCaseGenerationTaskList`

---

#### api_requirement_analysis_testcase_generation_create
**接口路径**: `/api/requirement-analysis/testcase-generation/`
**请求方式**: `POST`

**描述**: 测试用例生成任务视图集

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCaseGenerationTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCaseGenerationTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCaseGenerationTask`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `TestCaseGenerationTask`

---

#### api_requirement_analysis_testcase_generation_retrieve
**接口路径**: `/api/requirement-analysis/testcase-generation/{task_id}/`
**请求方式**: `GET`

**描述**: 测试用例生成任务视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| task_id | path | 是 | string |  |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseGenerationTask`

---

#### api_requirement_analysis_testcase_generation_partial_update
**接口路径**: `/api/requirement-analysis/testcase-generation/{task_id}/`
**请求方式**: `PATCH`

**描述**: 测试用例生成任务视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| task_id | path | 是 | string |  |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedTestCaseGenerationTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedTestCaseGenerationTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedTestCaseGenerationTask`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseGenerationTask`

---

#### api_requirement_analysis_testcase_generation_destroy
**接口路径**: `/api/requirement-analysis/testcase-generation/{task_id}/`
**请求方式**: `DELETE`

**描述**: 测试用例生成任务视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| task_id | path | 是 | string |  |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_requirement_analysis_testcase_generation_batch_adopt_selected_create
**接口路径**: `/api/requirement-analysis/testcase-generation/{task_id}/batch-adopt-selected/`
**请求方式**: `POST`

**描述**: 批量采纳选中的测试用例

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| task_id | path | 是 | string |  |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCaseGenerationTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCaseGenerationTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCaseGenerationTask`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseGenerationTask`

---

#### api_requirement_analysis_testcase_generation_batch_adopt_create
**接口路径**: `/api/requirement-analysis/testcase-generation/{task_id}/batch_adopt/`
**请求方式**: `POST`

**描述**: 批量采纳任务的所有测试用例

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| task_id | path | 是 | string |  |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCaseGenerationTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCaseGenerationTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCaseGenerationTask`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseGenerationTask`

---

#### api_requirement_analysis_testcase_generation_batch_discard_create
**接口路径**: `/api/requirement-analysis/testcase-generation/{task_id}/batch_discard/`
**请求方式**: `POST`

**描述**: 批量弃用任务的所有待处理测试用例

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| task_id | path | 是 | string |  |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCaseGenerationTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCaseGenerationTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCaseGenerationTask`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseGenerationTask`

---

#### api_requirement_analysis_testcase_generation_cancel_create
**接口路径**: `/api/requirement-analysis/testcase-generation/{task_id}/cancel/`
**请求方式**: `POST`

**描述**: 取消正在运行的任务

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| task_id | path | 是 | string |  |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCaseGenerationTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCaseGenerationTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCaseGenerationTask`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseGenerationTask`

---

#### api_requirement_analysis_testcase_generation_discard_selected_cases_create
**接口路径**: `/api/requirement-analysis/testcase-generation/{task_id}/discard-selected-cases/`
**请求方式**: `POST`

**描述**: 弃用选中的测试用例

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| task_id | path | 是 | string |  |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCaseGenerationTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCaseGenerationTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCaseGenerationTask`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseGenerationTask`

---

#### api_requirement_analysis_testcase_generation_discard_single_case_create
**接口路径**: `/api/requirement-analysis/testcase-generation/{task_id}/discard-single-case/`
**请求方式**: `POST`

**描述**: 弃用单个测试用例

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| task_id | path | 是 | string |  |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCaseGenerationTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCaseGenerationTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCaseGenerationTask`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseGenerationTask`

---

#### api_requirement_analysis_testcase_generation_progress_retrieve
**接口路径**: `/api/requirement-analysis/testcase-generation/{task_id}/progress/`
**请求方式**: `GET`

**描述**: 获取任务进度

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| task_id | path | 是 | string |  |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseGenerationTask`

---

#### api_requirement_analysis_testcase_generation_save_to_records_create
**接口路径**: `/api/requirement-analysis/testcase-generation/{task_id}/save_to_records/`
**请求方式**: `POST`

**描述**: 保存测试用例到AI生成用例记录并导入到测试用例管理系统

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| task_id | path | 是 | string |  |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCaseGenerationTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCaseGenerationTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCaseGenerationTask`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseGenerationTask`

---

#### api_requirement_analysis_testcase_generation_stream_progress_retrieve
**接口路径**: `/api/requirement-analysis/testcase-generation/{task_id}/stream_progress/`
**请求方式**: `GET`

**描述**: SSE流式进度推送接口
实时推送任务的流式输出和进度更新
不使用DRF的Response，避免content negotiation问题
注意：EventSource不支持自定义headers，无法发送JWT token，所以允许通过session cookie访问

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| task_id | path | 是 | string |  |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseGenerationTask`

---

#### api_requirement_analysis_testcase_generation_update_test_cases_create
**接口路径**: `/api/requirement-analysis/testcase-generation/{task_id}/update-test-cases/`
**请求方式**: `POST`

**描述**: 更新测试用例内容

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| task_id | path | 是 | string |  |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCaseGenerationTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCaseGenerationTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCaseGenerationTask`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseGenerationTask`

---

#### api_requirement_analysis_testcase_generation_generate_create
**接口路径**: `/api/requirement-analysis/testcase-generation/generate/`
**请求方式**: `POST`

**描述**: 创建新的测试用例生成任务

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCaseGenerationTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCaseGenerationTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCaseGenerationTask`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseGenerationTask`

---

#### api_requirement_analysis_testcase_generation_saved_records_retrieve
**接口路径**: `/api/requirement-analysis/testcase-generation/saved_records/`
**请求方式**: `GET`

**描述**: 获取已保存的测试用例记录列表

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseGenerationTask`

---

#### api_requirement_analysis_testcase_generation_statistics_retrieve
**接口路径**: `/api/requirement-analysis/testcase-generation/statistics/`
**请求方式**: `GET`

**描述**: 获取测试用例生成任务的统计信息

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseGenerationTask`

---

#### api_requirement_analysis_upload_and_analyze_create
**接口路径**: `/api/requirement-analysis/upload-and-analyze/`
**请求方式**: `POST`

**描述**: 上传文档并立即开始分析

**响应示例**:
- **状态码 `200`**: No response body

---

### Web UI 自动化
#### api_ui_automation_ai_case_generation_list
**接口路径**: `/api/ui-automation/ai-case-generation/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| project | query | 否 | integer |  |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedAICaseList`

---

#### api_ui_automation_ai_case_generation_create
**接口路径**: `/api/ui-automation/ai-case-generation/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AICase`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AICase`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AICase`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `AICase`

---

#### api_ui_automation_ai_case_generation_retrieve
**接口路径**: `/api/ui-automation/ai-case-generation/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI测试用例. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AICase`

---

#### api_ui_automation_ai_case_generation_update
**接口路径**: `/api/ui-automation/ai-case-generation/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI测试用例. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AICase`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AICase`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AICase`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AICase`

---

#### api_ui_automation_ai_case_generation_partial_update
**接口路径**: `/api/ui-automation/ai-case-generation/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI测试用例. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedAICase`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedAICase`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedAICase`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AICase`

---

#### api_ui_automation_ai_case_generation_destroy
**接口路径**: `/api/ui-automation/ai-case-generation/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI测试用例. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_ui_automation_ai_case_generation_run_create
**接口路径**: `/api/ui-automation/ai-case-generation/{id}/run/`
**请求方式**: `POST`

**描述**: 执行 AI 用例

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI测试用例. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AICase`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AICase`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AICase`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AICase`

---

#### api_ui_automation_ai_cases_list
**接口路径**: `/api/ui-automation/ai-cases/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| project | query | 否 | integer |  |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedAICaseList`

---

#### api_ui_automation_ai_cases_create
**接口路径**: `/api/ui-automation/ai-cases/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AICase`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AICase`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AICase`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `AICase`

---

#### api_ui_automation_ai_cases_retrieve
**接口路径**: `/api/ui-automation/ai-cases/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI测试用例. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AICase`

---

#### api_ui_automation_ai_cases_update
**接口路径**: `/api/ui-automation/ai-cases/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI测试用例. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AICase`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AICase`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AICase`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AICase`

---

#### api_ui_automation_ai_cases_partial_update
**接口路径**: `/api/ui-automation/ai-cases/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI测试用例. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedAICase`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedAICase`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedAICase`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AICase`

---

#### api_ui_automation_ai_cases_destroy
**接口路径**: `/api/ui-automation/ai-cases/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI测试用例. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_ui_automation_ai_cases_run_create
**接口路径**: `/api/ui-automation/ai-cases/{id}/run/`
**请求方式**: `POST`

**描述**: 执行 AI 用例

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI测试用例. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AICase`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AICase`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AICase`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AICase`

---

#### api_ui_automation_ai_execution_records_list
**接口路径**: `/api/ui-automation/ai-execution-records/`
**请求方式**: `GET`

**描述**: AI执行记录视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ai_case | query | 否 | integer |  |
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| project | query | 否 | integer |  |
| status | query | 否 | string | * `pending` - 等待中 * `running` - 执行中 * `passed` - 成功 * `failed` - 失败 |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedAIExecutionRecordList`

---

#### api_ui_automation_ai_execution_records_create
**接口路径**: `/api/ui-automation/ai-execution-records/`
**请求方式**: `POST`

**描述**: AI执行记录视图集

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AIExecutionRecord`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AIExecutionRecord`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AIExecutionRecord`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `AIExecutionRecord`

---

#### api_ui_automation_ai_execution_records_retrieve
**接口路径**: `/api/ui-automation/ai-execution-records/{id}/`
**请求方式**: `GET`

**描述**: AI执行记录视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI测试报告. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AIExecutionRecord`

---

#### api_ui_automation_ai_execution_records_update
**接口路径**: `/api/ui-automation/ai-execution-records/{id}/`
**请求方式**: `PUT`

**描述**: AI执行记录视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI测试报告. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AIExecutionRecord`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AIExecutionRecord`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AIExecutionRecord`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AIExecutionRecord`

---

#### api_ui_automation_ai_execution_records_partial_update
**接口路径**: `/api/ui-automation/ai-execution-records/{id}/`
**请求方式**: `PATCH`

**描述**: AI执行记录视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI测试报告. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedAIExecutionRecord`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedAIExecutionRecord`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedAIExecutionRecord`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AIExecutionRecord`

---

#### api_ui_automation_ai_execution_records_destroy
**接口路径**: `/api/ui-automation/ai-execution-records/{id}/`
**请求方式**: `DELETE`

**描述**: AI执行记录视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI测试报告. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_ui_automation_ai_execution_records_export_pdf_retrieve
**接口路径**: `/api/ui-automation/ai-execution-records/{id}/export-pdf/`
**请求方式**: `GET`

**描述**: 导出AI执行报告为PDF

Query Parameters:
    report_type: 报告类型 (summary/detailed/performance)，默认为 summary

Returns:
    PDF文件下载

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI测试报告. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AIExecutionRecord`

---

#### api_ui_automation_ai_execution_records_report_retrieve
**接口路径**: `/api/ui-automation/ai-execution-records/{id}/report/`
**请求方式**: `GET`

**描述**: 生成AI执行报告

Query Parameters:
    report_type: 报告类型 (summary/detailed/performance)，默认为 summary

Returns:
    执行报告数据

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI测试报告. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AIExecutionRecord`

---

#### api_ui_automation_ai_execution_records_stop_create
**接口路径**: `/api/ui-automation/ai-execution-records/{id}/stop/`
**请求方式**: `POST`

**描述**: 停止正在执行的任务

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI测试报告. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AIExecutionRecord`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AIExecutionRecord`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AIExecutionRecord`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AIExecutionRecord`

---

#### api_ui_automation_ai_execution_records_batch_delete_create
**接口路径**: `/api/ui-automation/ai-execution-records/batch_delete/`
**请求方式**: `POST`

**描述**: 批量删除AI执行记录

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AIExecutionRecord`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AIExecutionRecord`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AIExecutionRecord`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AIExecutionRecord`

---

#### api_ui_automation_ai_execution_records_run_adhoc_create
**接口路径**: `/api/ui-automation/ai-execution-records/run_adhoc/`
**请求方式**: `POST`

**描述**: 执行临时 AI 任务

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AIExecutionRecord`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AIExecutionRecord`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AIExecutionRecord`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AIExecutionRecord`

---

#### api_ui_automation_ai_models_retrieve
**接口路径**: `/api/ui-automation/ai-models/`
**请求方式**: `GET`

**描述**: 获取所有AI智能模式配置列表

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_ui_automation_ai_models_create
**接口路径**: `/api/ui-automation/ai-models/`
**请求方式**: `POST`

**描述**: 创建新的AI智能模式配置

**响应示例**:
- **状态码 `201`**: No response body

---

#### api_ui_automation_ai_models_retrieve_2
**接口路径**: `/api/ui-automation/ai-models/{id}/`
**请求方式**: `GET`

**描述**: 获取单个配置详情

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI模型配置. |

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_ui_automation_ai_models_update
**接口路径**: `/api/ui-automation/ai-models/{id}/`
**请求方式**: `PUT`

**描述**: 更新配置 (PUT)

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI模型配置. |

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_ui_automation_ai_models_partial_update
**接口路径**: `/api/ui-automation/ai-models/{id}/`
**请求方式**: `PATCH`

**描述**: 部分更新配置 (PATCH)

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI模型配置. |

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_ui_automation_ai_models_destroy
**接口路径**: `/api/ui-automation/ai-models/{id}/`
**请求方式**: `DELETE`

**描述**: 删除配置

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI模型配置. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_ui_automation_ai_models_test_connection_create_2
**接口路径**: `/api/ui-automation/ai-models/{id}/test_connection/`
**请求方式**: `POST`

**描述**: 测试已保存配置的连接

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI模型配置. |

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_ui_automation_ai_models_test_connection_create
**接口路径**: `/api/ui-automation/ai-models/test_connection/`
**请求方式**: `POST`

**描述**: 测试模型连接 (在保存前测试，不保存配置)

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_ui_automation_config_ai_mode_retrieve
**接口路径**: `/api/ui-automation/config/ai-mode/`
**请求方式**: `GET`

**描述**: 获取所有AI智能模式配置列表

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_ui_automation_config_ai_mode_create
**接口路径**: `/api/ui-automation/config/ai-mode/`
**请求方式**: `POST`

**描述**: 创建新的AI智能模式配置

**响应示例**:
- **状态码 `201`**: No response body

---

#### api_ui_automation_config_ai_mode_retrieve_2
**接口路径**: `/api/ui-automation/config/ai-mode/{id}/`
**请求方式**: `GET`

**描述**: 获取单个配置详情

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI模型配置. |

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_ui_automation_config_ai_mode_update
**接口路径**: `/api/ui-automation/config/ai-mode/{id}/`
**请求方式**: `PUT`

**描述**: 更新配置 (PUT)

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI模型配置. |

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_ui_automation_config_ai_mode_partial_update
**接口路径**: `/api/ui-automation/config/ai-mode/{id}/`
**请求方式**: `PATCH`

**描述**: 部分更新配置 (PATCH)

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI模型配置. |

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_ui_automation_config_ai_mode_destroy
**接口路径**: `/api/ui-automation/config/ai-mode/{id}/`
**请求方式**: `DELETE`

**描述**: 删除配置

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI模型配置. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_ui_automation_config_ai_mode_test_connection_create_2
**接口路径**: `/api/ui-automation/config/ai-mode/{id}/test_connection/`
**请求方式**: `POST`

**描述**: 测试已保存配置的连接

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI模型配置. |

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_ui_automation_config_ai_mode_test_connection_create
**接口路径**: `/api/ui-automation/config/ai-mode/test_connection/`
**请求方式**: `POST`

**描述**: 测试模型连接 (在保存前测试，不保存配置)

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_ui_automation_config_environment_check_environment_retrieve
**接口路径**: `/api/ui-automation/config/environment/check_environment/`
**请求方式**: `GET`

**描述**: 检测环境状态 (系统浏览器和Playwright浏览器)

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_ui_automation_config_environment_install_driver_create
**接口路径**: `/api/ui-automation/config/environment/install_driver/`
**请求方式**: `POST`

**描述**: 安装浏览器驱动

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_ui_automation_dashboard_stats_retrieve
**接口路径**: `/api/ui-automation/dashboard/stats/`
**请求方式**: `GET`

**描述**: 获取仪表盘统计数据

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_ui_automation_element_groups_list
**接口路径**: `/api/ui-automation/element-groups/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| page | query | 否 | integer | A page number within the paginated result set. |
| parent_group | query | 否 | integer |  |
| project | query | 否 | integer |  |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedElementGroupList`

---

#### api_ui_automation_element_groups_create
**接口路径**: `/api/ui-automation/element-groups/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `ElementGroupCreate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `ElementGroupCreate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `ElementGroupCreate`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `ElementGroupCreate`

---

#### api_ui_automation_element_groups_retrieve
**接口路径**: `/api/ui-automation/element-groups/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 元素分组. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ElementGroup`

---

#### api_ui_automation_element_groups_update
**接口路径**: `/api/ui-automation/element-groups/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 元素分组. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `ElementGroup`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `ElementGroup`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `ElementGroup`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ElementGroup`

---

#### api_ui_automation_element_groups_partial_update
**接口路径**: `/api/ui-automation/element-groups/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 元素分组. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedElementGroup`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedElementGroup`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedElementGroup`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ElementGroup`

---

#### api_ui_automation_element_groups_destroy
**接口路径**: `/api/ui-automation/element-groups/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 元素分组. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_ui_automation_element_groups_tree_retrieve
**接口路径**: `/api/ui-automation/element-groups/tree/`
**请求方式**: `GET`

**描述**: 获取分组树形结构

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ElementGroup`

---

#### api_ui_automation_elements_list
**接口路径**: `/api/ui-automation/elements/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| element_type | query | 否 | string | * `INPUT` - 输入框 * `BUTTON` - 按钮 * `LINK` - 链接 * `DROPDOWN` - 下拉框 * `CHECKBOX` - 复选框 * `RADIO` - 单选框 * `TEXT` - 文本 * `IMAGE` - 图片 * `CONTAINER` - 容器 * `TABLE` - 表格 * `FORM` - 表单 * `MODAL` - 弹窗 |
| group | query | 否 | integer |  |
| locator_strategy | query | 否 | integer |  |
| page | query | 否 | integer | A page number within the paginated result set. |
| project | query | 否 | integer |  |
| search | query | 否 | string | A search term. |
| validation_status | query | 否 | string | * `VALID` - 有效 * `INVALID` - 无效 * `UNKNOWN` - 未知 * `PENDING` - 待验证 |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedElementEnhancedList`

---

#### api_ui_automation_elements_create
**接口路径**: `/api/ui-automation/elements/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `Element`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `Element`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `Element`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `Element`

---

#### api_ui_automation_elements_retrieve
**接口路径**: `/api/ui-automation/elements/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI元素. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ElementEnhanced`

---

#### api_ui_automation_elements_update
**接口路径**: `/api/ui-automation/elements/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI元素. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `Element`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `Element`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `Element`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `Element`

---

#### api_ui_automation_elements_partial_update
**接口路径**: `/api/ui-automation/elements/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI元素. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedElement`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedElement`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedElement`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `Element`

---

#### api_ui_automation_elements_destroy
**接口路径**: `/api/ui-automation/elements/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI元素. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_ui_automation_elements_add_backup_locator_create
**接口路径**: `/api/ui-automation/elements/{id}/add_backup_locator/`
**请求方式**: `POST`

**描述**: 添加备用定位器

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI元素. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `Element`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `Element`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `Element`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `Element`

---

#### api_ui_automation_elements_generate_suggestions_create
**接口路径**: `/api/ui-automation/elements/{id}/generate_suggestions/`
**请求方式**: `POST`

**描述**: 生成元素使用建议

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI元素. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `Element`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `Element`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `Element`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `Element`

---

#### api_ui_automation_elements_usages_retrieve
**接口路径**: `/api/ui-automation/elements/{id}/usages/`
**请求方式**: `GET`

**描述**: 获取元素在脚本中的使用情况

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI元素. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `Element`

---

#### api_ui_automation_elements_validate_locator_create
**接口路径**: `/api/ui-automation/elements/{id}/validate_locator/`
**请求方式**: `POST`

**描述**: 验证元素定位器有效性

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI元素. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `Element`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `Element`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `Element`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `Element`

---

#### api_ui_automation_elements_tree_retrieve
**接口路径**: `/api/ui-automation/elements/tree/`
**请求方式**: `GET`

**描述**: 获取元素树形结构

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `Element`

---

#### api_ui_automation_locator_strategies_list
**接口路径**: `/api/ui-automation/locator-strategies/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedLocatorStrategyList`

---

#### api_ui_automation_locator_strategies_create
**接口路径**: `/api/ui-automation/locator-strategies/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `LocatorStrategy`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `LocatorStrategy`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `LocatorStrategy`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `LocatorStrategy`

---

#### api_ui_automation_locator_strategies_retrieve
**接口路径**: `/api/ui-automation/locator-strategies/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 定位策略. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `LocatorStrategy`

---

#### api_ui_automation_locator_strategies_update
**接口路径**: `/api/ui-automation/locator-strategies/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 定位策略. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `LocatorStrategy`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `LocatorStrategy`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `LocatorStrategy`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `LocatorStrategy`

---

#### api_ui_automation_locator_strategies_partial_update
**接口路径**: `/api/ui-automation/locator-strategies/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 定位策略. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedLocatorStrategy`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedLocatorStrategy`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedLocatorStrategy`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `LocatorStrategy`

---

#### api_ui_automation_locator_strategies_destroy
**接口路径**: `/api/ui-automation/locator-strategies/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 定位策略. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_ui_automation_notification_logs_list
**接口路径**: `/api/ui-automation/notification-logs/`
**请求方式**: `GET`

**描述**: UI通知日志视图集（只读）

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| notification_type | query | 否 | string | * `task_execution` - 定时任务执行 * `test_suite_execution` - 测试套件执行 * `test_case_execution` - 测试用例执行 * `system_alert` - 系统警告 * `manual` - 手动通知 |
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |
| status | query | 否 | string | * `pending` - 待发送 * `sending` - 发送中 * `success` - 发送成功 * `failed` - 发送失败 * `cancelled` - 已取消 |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedUiNotificationLogList`

---

#### api_ui_automation_notification_logs_retrieve
**接口路径**: `/api/ui-automation/notification-logs/{id}/`
**请求方式**: `GET`

**描述**: UI通知日志视图集（只读）

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI通知日志. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `UiNotificationLog`

---

#### api_ui_automation_notification_logs_retry_create
**接口路径**: `/api/ui-automation/notification-logs/{id}/retry/`
**请求方式**: `POST`

**描述**: 重试发送通知

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI通知日志. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `UiNotificationLog`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `UiNotificationLog`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `UiNotificationLog`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `UiNotificationLog`

---

#### api_ui_automation_operation_records_list
**接口路径**: `/api/ui-automation/operation-records/`
**请求方式**: `GET`

**描述**: 操作记录视图集（只读）

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| operation_type | query | 否 | string | * `create` - 新增 * `edit` - 编辑 * `delete` - 删除 * `run` - 运行 * `rerun` - 重新运行 * `save` - 保存 * `rename` - 重命名 |
| page | query | 否 | integer | A page number within the paginated result set. |
| resource_type | query | 否 | string | * `project` - 项目 * `element` - 元素 * `test_case` - 测试用例 * `script` - 脚本 * `suite` - 套件 * `execution` - 执行记录 * `report` - 测试报告 |
| user | query | 否 | integer |  |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedOperationRecordList`

---

#### api_ui_automation_operation_records_retrieve
**接口路径**: `/api/ui-automation/operation-records/{id}/`
**请求方式**: `GET`

**描述**: 操作记录视图集（只读）

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI操作记录. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `OperationRecord`

---

#### api_ui_automation_page_objects_list
**接口路径**: `/api/ui-automation/page-objects/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| page | query | 否 | integer | A page number within the paginated result set. |
| project | query | 否 | integer |  |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedPageObjectList`

---

#### api_ui_automation_page_objects_create
**接口路径**: `/api/ui-automation/page-objects/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PageObjectCreate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PageObjectCreate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PageObjectCreate`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `PageObjectCreate`

---

#### api_ui_automation_page_objects_retrieve
**接口路径**: `/api/ui-automation/page-objects/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 页面对象. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PageObject`

---

#### api_ui_automation_page_objects_update
**接口路径**: `/api/ui-automation/page-objects/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 页面对象. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PageObject`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PageObject`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PageObject`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PageObject`

---

#### api_ui_automation_page_objects_partial_update
**接口路径**: `/api/ui-automation/page-objects/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 页面对象. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedPageObject`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedPageObject`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedPageObject`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PageObject`

---

#### api_ui_automation_page_objects_destroy
**接口路径**: `/api/ui-automation/page-objects/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 页面对象. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_ui_automation_page_objects_add_element_create
**接口路径**: `/api/ui-automation/page-objects/{id}/add_element/`
**请求方式**: `POST`

**描述**: 向页面对象添加元素

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 页面对象. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PageObject`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PageObject`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PageObject`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PageObject`

---

#### api_ui_automation_page_objects_elements_retrieve
**接口路径**: `/api/ui-automation/page-objects/{id}/elements/`
**请求方式**: `GET`

**描述**: 获取页面对象的所有元素

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 页面对象. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PageObject`

---

#### api_ui_automation_page_objects_generate_code_create
**接口路径**: `/api/ui-automation/page-objects/{id}/generate_code/`
**请求方式**: `POST`

**描述**: 生成页面对象代码

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 页面对象. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PageObject`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PageObject`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PageObject`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PageObject`

---

#### api_ui_automation_projects_list
**接口路径**: `/api/ui-automation/projects/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| members | query | 否 | array |  |
| ordering | query | 否 | string | Which field to use when ordering the results. |
| owner | query | 否 | integer |  |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |
| status | query | 否 | string | * `NOT_STARTED` - 未开始 * `IN_PROGRESS` - 进行中 * `COMPLETED` - 已结束 |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedUiProjectList`

---

#### api_ui_automation_projects_create
**接口路径**: `/api/ui-automation/projects/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `UiProjectCreate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `UiProjectCreate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `UiProjectCreate`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `UiProjectCreate`

---

#### api_ui_automation_projects_retrieve
**接口路径**: `/api/ui-automation/projects/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI自动化项目. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `UiProject`

---

#### api_ui_automation_projects_update
**接口路径**: `/api/ui-automation/projects/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI自动化项目. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `UiProjectUpdate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `UiProjectUpdate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `UiProjectUpdate`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `UiProjectUpdate`

---

#### api_ui_automation_projects_partial_update
**接口路径**: `/api/ui-automation/projects/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI自动化项目. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedUiProjectUpdate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedUiProjectUpdate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedUiProjectUpdate`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `UiProjectUpdate`

---

#### api_ui_automation_projects_destroy
**接口路径**: `/api/ui-automation/projects/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI自动化项目. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_ui_automation_scheduled_tasks_list
**接口路径**: `/api/ui-automation/scheduled-tasks/`
**请求方式**: `GET`

**描述**: UI定时任务视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| project | query | 否 | integer |  |
| search | query | 否 | string | A search term. |
| status | query | 否 | string | * `ACTIVE` - 激活 * `PAUSED` - 暂停 * `COMPLETED` - 已完成 * `FAILED` - 失败 |
| task_type | query | 否 | string | * `TEST_SUITE` - 测试套件执行 * `TEST_CASE` - 测试用例执行 |
| trigger_type | query | 否 | string | * `CRON` - Cron表达式 * `INTERVAL` - 固定间隔 * `ONCE` - 单次执行 |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedUiScheduledTaskList`

---

#### api_ui_automation_scheduled_tasks_create
**接口路径**: `/api/ui-automation/scheduled-tasks/`
**请求方式**: `POST`

**描述**: UI定时任务视图集

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `UiScheduledTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `UiScheduledTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `UiScheduledTask`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `UiScheduledTask`

---

#### api_ui_automation_scheduled_tasks_retrieve
**接口路径**: `/api/ui-automation/scheduled-tasks/{id}/`
**请求方式**: `GET`

**描述**: UI定时任务视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI定时任务. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `UiScheduledTask`

---

#### api_ui_automation_scheduled_tasks_update
**接口路径**: `/api/ui-automation/scheduled-tasks/{id}/`
**请求方式**: `PUT`

**描述**: UI定时任务视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI定时任务. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `UiScheduledTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `UiScheduledTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `UiScheduledTask`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `UiScheduledTask`

---

#### api_ui_automation_scheduled_tasks_partial_update
**接口路径**: `/api/ui-automation/scheduled-tasks/{id}/`
**请求方式**: `PATCH`

**描述**: UI定时任务视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI定时任务. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedUiScheduledTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedUiScheduledTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedUiScheduledTask`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `UiScheduledTask`

---

#### api_ui_automation_scheduled_tasks_destroy
**接口路径**: `/api/ui-automation/scheduled-tasks/{id}/`
**请求方式**: `DELETE`

**描述**: UI定时任务视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI定时任务. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_ui_automation_scheduled_tasks_pause_create
**接口路径**: `/api/ui-automation/scheduled-tasks/{id}/pause/`
**请求方式**: `POST`

**描述**: 暂停定时任务

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI定时任务. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `UiScheduledTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `UiScheduledTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `UiScheduledTask`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `UiScheduledTask`

---

#### api_ui_automation_scheduled_tasks_resume_create
**接口路径**: `/api/ui-automation/scheduled-tasks/{id}/resume/`
**请求方式**: `POST`

**描述**: 恢复定时任务

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI定时任务. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `UiScheduledTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `UiScheduledTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `UiScheduledTask`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `UiScheduledTask`

---

#### api_ui_automation_scheduled_tasks_run_now_create
**接口路径**: `/api/ui-automation/scheduled-tasks/{id}/run_now/`
**请求方式**: `POST`

**描述**: 立即运行任务

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI定时任务. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `UiScheduledTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `UiScheduledTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `UiScheduledTask`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `UiScheduledTask`

---

#### api_ui_automation_screenshots_list
**接口路径**: `/api/ui-automation/screenshots/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| execution | query | 否 | integer |  |
| page | query | 否 | integer | A page number within the paginated result set. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedScreenshotList`

---

#### api_ui_automation_screenshots_create
**接口路径**: `/api/ui-automation/screenshots/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `Screenshot`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `Screenshot`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `Screenshot`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `Screenshot`

---

#### api_ui_automation_screenshots_retrieve
**接口路径**: `/api/ui-automation/screenshots/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI截图. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `Screenshot`

---

#### api_ui_automation_screenshots_update
**接口路径**: `/api/ui-automation/screenshots/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI截图. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `Screenshot`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `Screenshot`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `Screenshot`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `Screenshot`

---

#### api_ui_automation_screenshots_partial_update
**接口路径**: `/api/ui-automation/screenshots/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI截图. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedScreenshot`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedScreenshot`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedScreenshot`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `Screenshot`

---

#### api_ui_automation_screenshots_destroy
**接口路径**: `/api/ui-automation/screenshots/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI截图. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_ui_automation_steps_list
**接口路径**: `/api/ui-automation/steps/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| action_type | query | 否 | string | * `CLICK` - 点击 * `INPUT` - 输入 * `SELECT` - 选择 * `VERIFY` - 验证 * `WAIT` - 等待 * `HOVER` - 悬停 * `SCROLL` - 滚动 * `NAVIGATE` - 导航 * `SCREENSHOT` - 截图 * `SWITCH_TAB` - 切换标签页 * `CUSTOM` - 自定义 |
| page | query | 否 | integer | A page number within the paginated result set. |
| page_object | query | 否 | integer |  |
| script | query | 否 | integer |  |
| target_element | query | 否 | integer |  |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedScriptStepList`

---

#### api_ui_automation_steps_create
**接口路径**: `/api/ui-automation/steps/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `ScriptStep`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `ScriptStep`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `ScriptStep`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `ScriptStep`

---

#### api_ui_automation_steps_retrieve
**接口路径**: `/api/ui-automation/steps/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 脚本步骤. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ScriptStep`

---

#### api_ui_automation_steps_update
**接口路径**: `/api/ui-automation/steps/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 脚本步骤. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `ScriptStep`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `ScriptStep`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `ScriptStep`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ScriptStep`

---

#### api_ui_automation_steps_partial_update
**接口路径**: `/api/ui-automation/steps/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 脚本步骤. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedScriptStep`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedScriptStep`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedScriptStep`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ScriptStep`

---

#### api_ui_automation_steps_destroy
**接口路径**: `/api/ui-automation/steps/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 脚本步骤. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_ui_automation_steps_batch_create_create
**接口路径**: `/api/ui-automation/steps/batch_create/`
**请求方式**: `POST`

**描述**: 批量创建脚本步骤

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `ScriptStep`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `ScriptStep`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `ScriptStep`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ScriptStep`

---

#### api_ui_automation_test_case_executions_list
**接口路径**: `/api/ui-automation/test-case-executions/`
**请求方式**: `GET`

**描述**: 测试用例执行记录视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| execution_source | query | 否 | string | * `manual` - 单用例执行 * `suite` - 套件执行 * `scheduled` - 定时任务执行 |
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| page_size | query | 否 | integer | Number of results to return per page. |
| project | query | 否 | integer |  |
| search | query | 否 | string | A search term. |
| status | query | 否 | string | * `pending` - 待执行 * `running` - 执行中 * `passed` - 通过 * `failed` - 失败 * `error` - 错误 |
| test_case | query | 否 | integer |  |
| test_suite | query | 否 | integer |  |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedTestCaseExecutionList`

---

#### api_ui_automation_test_case_executions_create
**接口路径**: `/api/ui-automation/test-case-executions/`
**请求方式**: `POST`

**描述**: 测试用例执行记录视图集

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCaseExecution`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCaseExecution`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCaseExecution`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `TestCaseExecution`

---

#### api_ui_automation_test_case_executions_retrieve
**接口路径**: `/api/ui-automation/test-case-executions/{id}/`
**请求方式**: `GET`

**描述**: 测试用例执行记录视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试用例执行记录. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseExecution`

---

#### api_ui_automation_test_case_executions_update
**接口路径**: `/api/ui-automation/test-case-executions/{id}/`
**请求方式**: `PUT`

**描述**: 测试用例执行记录视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试用例执行记录. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCaseExecution`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCaseExecution`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCaseExecution`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseExecution`

---

#### api_ui_automation_test_case_executions_partial_update
**接口路径**: `/api/ui-automation/test-case-executions/{id}/`
**请求方式**: `PATCH`

**描述**: 测试用例执行记录视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试用例执行记录. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedTestCaseExecution`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedTestCaseExecution`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedTestCaseExecution`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseExecution`

---

#### api_ui_automation_test_case_executions_destroy
**接口路径**: `/api/ui-automation/test-case-executions/{id}/`
**请求方式**: `DELETE`

**描述**: 测试用例执行记录视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试用例执行记录. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_ui_automation_test_case_executions_batch_delete_create
**接口路径**: `/api/ui-automation/test-case-executions/batch-delete/`
**请求方式**: `POST`

**描述**: 批量删除执行记录

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCaseExecution`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCaseExecution`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCaseExecution`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseExecution`

---

#### api_ui_automation_test_case_steps_list
**接口路径**: `/api/ui-automation/test-case-steps/`
**请求方式**: `GET`

**描述**: 测试用例步骤视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| action_type | query | 否 | string | * `click` - 点击 * `fill` - 输入文本 * `getText` - 获取文本 * `waitFor` - 等待元素 * `hover` - 悬停 * `scroll` - 滚动 * `screenshot` - 截图 * `assert` - 断言 * `wait` - 等待 * `switchTab` - 切换标签页 |
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| test_case | query | 否 | integer |  |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedTestCaseStepList`

---

#### api_ui_automation_test_case_steps_create
**接口路径**: `/api/ui-automation/test-case-steps/`
**请求方式**: `POST`

**描述**: 测试用例步骤视图集

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCaseStep`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCaseStep`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCaseStep`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `TestCaseStep`

---

#### api_ui_automation_test_case_steps_retrieve
**接口路径**: `/api/ui-automation/test-case-steps/{id}/`
**请求方式**: `GET`

**描述**: 测试用例步骤视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试用例步骤. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseStep`

---

#### api_ui_automation_test_case_steps_update
**接口路径**: `/api/ui-automation/test-case-steps/{id}/`
**请求方式**: `PUT`

**描述**: 测试用例步骤视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试用例步骤. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCaseStep`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCaseStep`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCaseStep`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseStep`

---

#### api_ui_automation_test_case_steps_partial_update
**接口路径**: `/api/ui-automation/test-case-steps/{id}/`
**请求方式**: `PATCH`

**描述**: 测试用例步骤视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试用例步骤. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedTestCaseStep`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedTestCaseStep`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedTestCaseStep`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCaseStep`

---

#### api_ui_automation_test_case_steps_destroy
**接口路径**: `/api/ui-automation/test-case-steps/{id}/`
**请求方式**: `DELETE`

**描述**: 测试用例步骤视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试用例步骤. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_ui_automation_test_cases_list
**接口路径**: `/api/ui-automation/test-cases/`
**请求方式**: `GET`

**描述**: 测试用例视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| created_by | query | 否 | integer |  |
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| priority | query | 否 | string | * `high` - 高 * `medium` - 中 * `low` - 低 |
| project | query | 否 | integer |  |
| search | query | 否 | string | A search term. |
| status | query | 否 | string | * `draft` - 草稿 * `ready` - 就绪 * `running` - 执行中 * `passed` - 通过 * `failed` - 失败 |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedTestCaseList`

---

#### api_ui_automation_test_cases_create
**接口路径**: `/api/ui-automation/test-cases/`
**请求方式**: `POST`

**描述**: 测试用例视图集

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCase`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCase`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCase`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `TestCase`

---

#### api_ui_automation_test_cases_retrieve
**接口路径**: `/api/ui-automation/test-cases/{id}/`
**请求方式**: `GET`

**描述**: 测试用例视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试用例. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCase`

---

#### api_ui_automation_test_cases_update
**接口路径**: `/api/ui-automation/test-cases/{id}/`
**请求方式**: `PUT`

**描述**: 测试用例视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试用例. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCase`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCase`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCase`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCase`

---

#### api_ui_automation_test_cases_partial_update
**接口路径**: `/api/ui-automation/test-cases/{id}/`
**请求方式**: `PATCH`

**描述**: 测试用例视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试用例. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedTestCase`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedTestCase`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedTestCase`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCase`

---

#### api_ui_automation_test_cases_destroy
**接口路径**: `/api/ui-automation/test-cases/{id}/`
**请求方式**: `DELETE`

**描述**: 测试用例视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试用例. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_ui_automation_test_cases_copy_case_create
**接口路径**: `/api/ui-automation/test-cases/{id}/copy_case/`
**请求方式**: `POST`

**描述**: 复制测试用例

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试用例. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCase`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCase`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCase`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCase`

---

#### api_ui_automation_test_cases_run_create
**接口路径**: `/api/ui-automation/test-cases/{id}/run/`
**请求方式**: `POST`

**描述**: 运行单个测试用例 - 支持选择Playwright或Selenium执行引擎

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试用例. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCase`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCase`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCase`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCase`

---

#### api_ui_automation_test_cases_batch_run_create
**接口路径**: `/api/ui-automation/test-cases/batch_run/`
**请求方式**: `POST`

**描述**: 批量运行测试用例

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestCase`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestCase`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestCase`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestCase`

---

#### api_ui_automation_test_executions_list
**接口路径**: `/api/ui-automation/test-executions/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| environment | query | 否 | string | * `CHROME` - Chrome * `FIREFOX` - Firefox * `SAFARI` - Safari * `EDGE` - Edge * `IE` - IE |
| executed_by | query | 否 | integer |  |
| page | query | 否 | integer | A page number within the paginated result set. |
| page_size | query | 否 | integer | Number of results to return per page. |
| project | query | 否 | integer |  |
| search | query | 否 | string | A search term. |
| status | query | 否 | string | * `PENDING` - 待执行 * `RUNNING` - 运行中 * `SUCCESS` - 成功 * `FAILED` - 失败 * `ABORTED` - 中止 |
| test_script | query | 否 | integer |  |
| test_suite | query | 否 | integer |  |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedTestExecutionList`

---

#### api_ui_automation_test_executions_create
**接口路径**: `/api/ui-automation/test-executions/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestExecutionCreate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestExecutionCreate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestExecutionCreate`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `TestExecutionCreate`

---

#### api_ui_automation_test_executions_retrieve
**接口路径**: `/api/ui-automation/test-executions/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试执行记录. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestExecution`

---

#### api_ui_automation_test_executions_update
**接口路径**: `/api/ui-automation/test-executions/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试执行记录. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestExecution`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestExecution`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestExecution`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestExecution`

---

#### api_ui_automation_test_executions_partial_update
**接口路径**: `/api/ui-automation/test-executions/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试执行记录. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedTestExecution`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedTestExecution`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedTestExecution`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestExecution`

---

#### api_ui_automation_test_executions_destroy
**接口路径**: `/api/ui-automation/test-executions/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试执行记录. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_ui_automation_test_scripts_list
**接口路径**: `/api/ui-automation/test-scripts/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| page | query | 否 | integer | A page number within the paginated result set. |
| project | query | 否 | integer |  |
| script_type | query | 否 | string | * `CODE` - 代码 * `LOW_CODE` - 低代码 * `NO_CODE` - 无代码 |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedTestScriptList`

---

#### api_ui_automation_test_scripts_create
**接口路径**: `/api/ui-automation/test-scripts/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestScriptCreate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestScriptCreate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestScriptCreate`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `TestScriptCreate`

---

#### api_ui_automation_test_scripts_retrieve
**接口路径**: `/api/ui-automation/test-scripts/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试脚本. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestScript`

---

#### api_ui_automation_test_scripts_update
**接口路径**: `/api/ui-automation/test-scripts/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试脚本. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestScriptUpdate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestScriptUpdate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestScriptUpdate`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestScriptUpdate`

---

#### api_ui_automation_test_scripts_partial_update
**接口路径**: `/api/ui-automation/test-scripts/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试脚本. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedTestScriptUpdate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedTestScriptUpdate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedTestScriptUpdate`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestScriptUpdate`

---

#### api_ui_automation_test_scripts_destroy
**接口路径**: `/api/ui-automation/test-scripts/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试脚本. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_ui_automation_test_suites_list
**接口路径**: `/api/ui-automation/test-suites/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| page | query | 否 | integer | A page number within the paginated result set. |
| project | query | 否 | integer |  |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedTestSuiteList`

---

#### api_ui_automation_test_suites_create
**接口路径**: `/api/ui-automation/test-suites/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestSuiteCreate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestSuiteCreate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestSuiteCreate`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `TestSuiteCreate`

---

#### api_ui_automation_test_suites_retrieve
**接口路径**: `/api/ui-automation/test-suites/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试套件. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestSuiteWithScripts`

---

#### api_ui_automation_test_suites_update
**接口路径**: `/api/ui-automation/test-suites/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试套件. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestSuiteUpdate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestSuiteUpdate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestSuiteUpdate`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestSuiteUpdate`

---

#### api_ui_automation_test_suites_partial_update
**接口路径**: `/api/ui-automation/test-suites/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试套件. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedTestSuiteUpdate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedTestSuiteUpdate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedTestSuiteUpdate`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestSuiteUpdate`

---

#### api_ui_automation_test_suites_destroy
**接口路径**: `/api/ui-automation/test-suites/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试套件. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_ui_automation_test_suites_add_script_create
**接口路径**: `/api/ui-automation/test-suites/{id}/add_script/`
**请求方式**: `POST`

**描述**: 向测试套件添加脚本

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试套件. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestSuite`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestSuite`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestSuite`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestSuite`

---

#### api_ui_automation_test_suites_add_test_case_create
**接口路径**: `/api/ui-automation/test-suites/{id}/add_test_case/`
**请求方式**: `POST`

**描述**: 向测试套件添加测试用例

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试套件. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestSuite`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestSuite`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestSuite`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestSuite`

---

#### api_ui_automation_test_suites_remove_script_destroy
**接口路径**: `/api/ui-automation/test-suites/{id}/remove_script/`
**请求方式**: `DELETE`

**描述**: 从测试套件移除脚本

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试套件. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_ui_automation_test_suites_remove_test_case_destroy
**接口路径**: `/api/ui-automation/test-suites/{id}/remove_test_case/`
**请求方式**: `DELETE`

**描述**: 从测试套件移除测试用例

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试套件. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_ui_automation_test_suites_run_suite_create
**接口路径**: `/api/ui-automation/test-suites/{id}/run_suite/`
**请求方式**: `POST`

**描述**: 执行测试套件

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试套件. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestSuite`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestSuite`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestSuite`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestSuite`

---

#### api_ui_automation_test_suites_scripts_retrieve
**接口路径**: `/api/ui-automation/test-suites/{id}/scripts/`
**请求方式**: `GET`

**描述**: 获取测试套件中的所有脚本

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试套件. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestSuite`

---

#### api_ui_automation_test_suites_test_cases_retrieve
**接口路径**: `/api/ui-automation/test-suites/{id}/test_cases/`
**请求方式**: `GET`

**描述**: 获取测试套件中的所有测试用例

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试套件. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestSuite`

---

#### api_ui_automation_test_suites_update_test_case_order_create
**接口路径**: `/api/ui-automation/test-suites/{id}/update_test_case_order/`
**请求方式**: `POST`

**描述**: 更新测试套件中测试用例的顺序

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this UI测试套件. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestSuite`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestSuite`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestSuite`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestSuite`

---

### APP 自动化
#### api_app_automation_component_packages_list
**接口路径**: `/api/app-automation/component-packages/`
**请求方式**: `GET`

**描述**: 组件包视图集（用于导入/导出组件定义）

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| page_size | query | 否 | integer | Number of results to return per page. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedAppComponentPackageList`

---

#### api_app_automation_component_packages_create
**接口路径**: `/api/app-automation/component-packages/`
**请求方式**: `POST`

**描述**: 导入组件包

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppComponentPackage`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppComponentPackage`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppComponentPackage`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `AppComponentPackage`

---

#### api_app_automation_component_packages_retrieve
**接口路径**: `/api/app-automation/component-packages/{id}/`
**请求方式**: `GET`

**描述**: 组件包视图集（用于导入/导出组件定义）

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP组件包. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppComponentPackage`

---

#### api_app_automation_component_packages_update
**接口路径**: `/api/app-automation/component-packages/{id}/`
**请求方式**: `PUT`

**描述**: 组件包视图集（用于导入/导出组件定义）

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP组件包. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppComponentPackage`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppComponentPackage`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppComponentPackage`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppComponentPackage`

---

#### api_app_automation_component_packages_partial_update
**接口路径**: `/api/app-automation/component-packages/{id}/`
**请求方式**: `PATCH`

**描述**: 组件包视图集（用于导入/导出组件定义）

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP组件包. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedAppComponentPackage`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedAppComponentPackage`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedAppComponentPackage`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppComponentPackage`

---

#### api_app_automation_component_packages_destroy
**接口路径**: `/api/app-automation/component-packages/{id}/`
**请求方式**: `DELETE`

**描述**: 组件包视图集（用于导入/导出组件定义）

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP组件包. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_app_automation_component_packages_export_retrieve
**接口路径**: `/api/app-automation/component-packages/export/`
**请求方式**: `GET`

**描述**: 导出组件包

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppComponentPackage`

---

#### api_app_automation_components_list
**接口路径**: `/api/app-automation/components/`
**请求方式**: `GET`

**描述**: 获取组件列表

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| page_size | query | 否 | integer | Number of results to return per page. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedAppComponentList`

---

#### api_app_automation_components_create
**接口路径**: `/api/app-automation/components/`
**请求方式**: `POST`

**描述**: 创建组件

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppComponent`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppComponent`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppComponent`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `AppComponent`

---

#### api_app_automation_components_retrieve
**接口路径**: `/api/app-automation/components/{id}/`
**请求方式**: `GET`

**描述**: UI组件定义视图

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP组件定义. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppComponent`

---

#### api_app_automation_components_update
**接口路径**: `/api/app-automation/components/{id}/`
**请求方式**: `PUT`

**描述**: 更新组件

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP组件定义. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppComponent`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppComponent`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppComponent`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppComponent`

---

#### api_app_automation_components_partial_update
**接口路径**: `/api/app-automation/components/{id}/`
**请求方式**: `PATCH`

**描述**: UI组件定义视图

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP组件定义. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedAppComponent`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedAppComponent`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedAppComponent`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppComponent`

---

#### api_app_automation_components_destroy
**接口路径**: `/api/app-automation/components/{id}/`
**请求方式**: `DELETE`

**描述**: 删除组件

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP组件定义. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_app_automation_config_current_retrieve
**接口路径**: `/api/app-automation/config/current/`
**请求方式**: `GET`

**描述**: 获取当前配置

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_app_automation_config_save_create
**接口路径**: `/api/app-automation/config/save/`
**请求方式**: `POST`

**描述**: 保存配置

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_app_automation_custom_components_list
**接口路径**: `/api/app-automation/custom-components/`
**请求方式**: `GET`

**描述**: 获取自定义组件列表

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| page_size | query | 否 | integer | Number of results to return per page. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedAppCustomComponentList`

---

#### api_app_automation_custom_components_create
**接口路径**: `/api/app-automation/custom-components/`
**请求方式**: `POST`

**描述**: 创建自定义组件

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppCustomComponent`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppCustomComponent`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppCustomComponent`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `AppCustomComponent`

---

#### api_app_automation_custom_components_retrieve
**接口路径**: `/api/app-automation/custom-components/{id}/`
**请求方式**: `GET`

**描述**: 自定义组件视图

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP自定义组件. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppCustomComponent`

---

#### api_app_automation_custom_components_update
**接口路径**: `/api/app-automation/custom-components/{id}/`
**请求方式**: `PUT`

**描述**: 更新自定义组件

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP自定义组件. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppCustomComponent`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppCustomComponent`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppCustomComponent`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppCustomComponent`

---

#### api_app_automation_custom_components_partial_update
**接口路径**: `/api/app-automation/custom-components/{id}/`
**请求方式**: `PATCH`

**描述**: 自定义组件视图

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP自定义组件. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedAppCustomComponent`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedAppCustomComponent`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedAppCustomComponent`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppCustomComponent`

---

#### api_app_automation_custom_components_destroy
**接口路径**: `/api/app-automation/custom-components/{id}/`
**请求方式**: `DELETE`

**描述**: 删除自定义组件

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP自定义组件. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_app_automation_dashboard_statistics_retrieve
**接口路径**: `/api/app-automation/dashboard/statistics/`
**请求方式**: `GET`

**描述**: 获取统计数据

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_app_automation_devices_list
**接口路径**: `/api/app-automation/devices/`
**请求方式**: `GET`

**描述**: APP设备管理 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| connection_type | query | 否 | string | * `emulator` - 本地模拟器 * `remote_emulator` - 远程模拟器 * `real_device` - 真实设备 |
| page | query | 否 | integer | A page number within the paginated result set. |
| page_size | query | 否 | integer | Number of results to return per page. |
| status | query | 否 | string | * `available` - 可用 * `locked` - 已锁定 * `online` - 在线 * `offline` - 离线 |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedAppDeviceList`

---

#### api_app_automation_devices_create
**接口路径**: `/api/app-automation/devices/`
**请求方式**: `POST`

**描述**: APP设备管理 ViewSet

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppDevice`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppDevice`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppDevice`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `AppDevice`

---

#### api_app_automation_devices_retrieve
**接口路径**: `/api/app-automation/devices/{id}/`
**请求方式**: `GET`

**描述**: APP设备管理 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试设备. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppDevice`

---

#### api_app_automation_devices_update
**接口路径**: `/api/app-automation/devices/{id}/`
**请求方式**: `PUT`

**描述**: APP设备管理 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试设备. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppDevice`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppDevice`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppDevice`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppDevice`

---

#### api_app_automation_devices_partial_update
**接口路径**: `/api/app-automation/devices/{id}/`
**请求方式**: `PATCH`

**描述**: APP设备管理 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试设备. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedAppDevice`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedAppDevice`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedAppDevice`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppDevice`

---

#### api_app_automation_devices_destroy
**接口路径**: `/api/app-automation/devices/{id}/`
**请求方式**: `DELETE`

**描述**: APP设备管理 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试设备. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_app_automation_devices_disconnect_create
**接口路径**: `/api/app-automation/devices/{id}/disconnect/`
**请求方式**: `POST`

**描述**: 断开远程设备连接

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试设备. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppDevice`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppDevice`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppDevice`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppDevice`

---

#### api_app_automation_devices_lock_create
**接口路径**: `/api/app-automation/devices/{id}/lock/`
**请求方式**: `POST`

**描述**: 锁定设备

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试设备. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppDevice`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppDevice`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppDevice`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppDevice`

---

#### api_app_automation_devices_screenshot_create
**接口路径**: `/api/app-automation/devices/{id}/screenshot/`
**请求方式**: `POST`

**描述**: 获取设备实时截图

功能：
1. 使用 adb screencap 获取设备截图
2. 转换为 Base64
3. 返回 data URL 格式

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试设备. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppDevice`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppDevice`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppDevice`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppDevice`

---

#### api_app_automation_devices_unlock_create
**接口路径**: `/api/app-automation/devices/{id}/unlock/`
**请求方式**: `POST`

**描述**: 释放设备

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试设备. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppDevice`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppDevice`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppDevice`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppDevice`

---

#### api_app_automation_devices_connect_create
**接口路径**: `/api/app-automation/devices/connect/`
**请求方式**: `POST`

**描述**: 连接远程设备

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppDevice`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppDevice`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppDevice`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppDevice`

---

#### api_app_automation_devices_discover_retrieve
**接口路径**: `/api/app-automation/devices/discover/`
**请求方式**: `GET`

**描述**: 发现ADB设备

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppDevice`

---

#### api_app_automation_elements_list
**接口路径**: `/api/app-automation/elements/`
**请求方式**: `GET`

**描述**: APP元素管理 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| element_type | query | 否 | string | * `image` - 图片元素 * `pos` - 坐标元素 * `region` - 区域元素 |
| is_active | query | 否 | boolean |  |
| page | query | 否 | integer | A page number within the paginated result set. |
| page_size | query | 否 | integer | Number of results to return per page. |
| project | query | 否 | integer |  |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedAppElementList`

---

#### api_app_automation_elements_create
**接口路径**: `/api/app-automation/elements/`
**请求方式**: `POST`

**描述**: APP元素管理 ViewSet

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppElement`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppElement`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppElement`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `AppElement`

---

#### api_app_automation_elements_retrieve
**接口路径**: `/api/app-automation/elements/{id}/`
**请求方式**: `GET`

**描述**: APP元素管理 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP UI元素. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppElement`

---

#### api_app_automation_elements_update
**接口路径**: `/api/app-automation/elements/{id}/`
**请求方式**: `PUT`

**描述**: APP元素管理 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP UI元素. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppElement`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppElement`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppElement`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppElement`

---

#### api_app_automation_elements_partial_update
**接口路径**: `/api/app-automation/elements/{id}/`
**请求方式**: `PATCH`

**描述**: APP元素管理 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP UI元素. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedAppElement`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedAppElement`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedAppElement`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppElement`

---

#### api_app_automation_elements_destroy
**接口路径**: `/api/app-automation/elements/{id}/`
**请求方式**: `DELETE`

**描述**: APP元素管理 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP UI元素. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_app_automation_elements_preview_retrieve
**接口路径**: `/api/app-automation/elements/{id}/preview/`
**请求方式**: `GET`

**描述**: 获取元素图片预览

返回图片文件（用于前端显示）

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP UI元素. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppElement`

---

#### api_app_automation_elements_crop_image_create
**接口路径**: `/api/app-automation/elements/crop-image/`
**请求方式**: `POST`

**描述**: 裁剪图片并保存

参数：
- image_data: Base64 图片数据
- x, y, width, height: 裁剪区域坐标
- element_name: 元素名称
- category: 图片分类
- element_type: 元素类型（image/pos/region）

返回：
- 裁剪后的图片路径
- 文件哈希
- 坐标信息

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppElement`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppElement`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppElement`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppElement`

---

#### api_app_automation_elements_image_categories_retrieve
**接口路径**: `/api/app-automation/elements/image-categories/`
**请求方式**: `GET`

**描述**: 获取图片分类列表

返回所有可用的图片分类目录

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppElement`

---

#### api_app_automation_elements_image_categories_destroy
**接口路径**: `/api/app-automation/elements/image-categories/{name}/`
**请求方式**: `DELETE`

**描述**: 删除图片分类（仅删除空目录）

参数：
- name: 分类名称

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| name | path | 是 | string |  |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_app_automation_elements_image_categories_create_create
**接口路径**: `/api/app-automation/elements/image-categories/create/`
**请求方式**: `POST`

**描述**: 创建新的图片分类

参数：
- name: 分类名称（只能包含字母、数字、下划线、中划线）

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppElement`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppElement`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppElement`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppElement`

---

#### api_app_automation_elements_upload_create
**接口路径**: `/api/app-automation/elements/upload/`
**请求方式**: `POST`

**描述**: 上传元素图片

功能：
1. 接收图片文件上传
2. 计算文件哈希
3. 检测是否重复
4. 保存到指定分类目录
5. 返回图片路径和哈希值

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppElement`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppElement`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppElement`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppElement`

---

#### api_app_automation_executions_list
**接口路径**: `/api/app-automation/executions/`
**请求方式**: `GET`

**描述**: APP测试执行记录 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| device | query | 否 | integer |  |
| page | query | 否 | integer | A page number within the paginated result set. |
| page_size | query | 否 | integer | Number of results to return per page. |
| search | query | 否 | string | A search term. |
| status | query | 否 | string | * `pending` - 等待中 * `running` - 执行中 * `completed` - 已完成 * `error` - 执行异常 * `stopped` - 已停止 |
| test_case | query | 否 | integer |  |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedAppTestExecutionList`

---

#### api_app_automation_executions_create
**接口路径**: `/api/app-automation/executions/`
**请求方式**: `POST`

**描述**: APP测试执行记录 ViewSet

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppTestExecution`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppTestExecution`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppTestExecution`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `AppTestExecution`

---

#### api_app_automation_executions_retrieve
**接口路径**: `/api/app-automation/executions/{id}/`
**请求方式**: `GET`

**描述**: APP测试执行记录 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试执行记录. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppTestExecution`

---

#### api_app_automation_executions_update
**接口路径**: `/api/app-automation/executions/{id}/`
**请求方式**: `PUT`

**描述**: APP测试执行记录 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试执行记录. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppTestExecution`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppTestExecution`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppTestExecution`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppTestExecution`

---

#### api_app_automation_executions_partial_update
**接口路径**: `/api/app-automation/executions/{id}/`
**请求方式**: `PATCH`

**描述**: APP测试执行记录 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试执行记录. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedAppTestExecution`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedAppTestExecution`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedAppTestExecution`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppTestExecution`

---

#### api_app_automation_executions_destroy
**接口路径**: `/api/app-automation/executions/{id}/`
**请求方式**: `DELETE`

**描述**: APP测试执行记录 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试执行记录. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_app_automation_executions_stop_create
**接口路径**: `/api/app-automation/executions/{id}/stop/`
**请求方式**: `POST`

**描述**: 停止执行

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试执行记录. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppTestExecution`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppTestExecution`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppTestExecution`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppTestExecution`

---

#### api_app_automation_executions_ws_status_retrieve
**接口路径**: `/api/app-automation/executions/ws_status/`
**请求方式**: `GET`

**描述**: 检查 WebSocket 是否可用

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppTestExecution`

---

#### api_app_automation_notification_logs_list
**接口路径**: `/api/app-automation/notification-logs/`
**请求方式**: `GET`

**描述**: APP通知日志视图集（只读）

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| notification_type | query | 否 | string | * `task_execution` - 定时任务执行 * `test_suite_execution` - 测试套件执行 * `system_alert` - 系统警告 * `manual` - 手动通知 |
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| page_size | query | 否 | integer | Number of results to return per page. |
| search | query | 否 | string | A search term. |
| status | query | 否 | string | * `pending` - 待发送 * `sending` - 发送中 * `success` - 发送成功 * `failed` - 发送失败 * `cancelled` - 已取消 |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedAppNotificationLogList`

---

#### api_app_automation_notification_logs_retrieve
**接口路径**: `/api/app-automation/notification-logs/{id}/`
**请求方式**: `GET`

**描述**: APP通知日志视图集（只读）

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP通知日志. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppNotificationLog`

---

#### api_app_automation_notification_logs_retry_create
**接口路径**: `/api/app-automation/notification-logs/{id}/retry/`
**请求方式**: `POST`

**描述**: APP通知日志视图集（只读）

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP通知日志. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppNotificationLog`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppNotificationLog`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppNotificationLog`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppNotificationLog`

---

#### api_app_automation_packages_list
**接口路径**: `/api/app-automation/packages/`
**请求方式**: `GET`

**描述**: APP应用包名管理 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| page_size | query | 否 | integer | Number of results to return per page. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedAppPackageList`

---

#### api_app_automation_packages_create
**接口路径**: `/api/app-automation/packages/`
**请求方式**: `POST`

**描述**: APP应用包名管理 ViewSet

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppPackage`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppPackage`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppPackage`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `AppPackage`

---

#### api_app_automation_packages_retrieve
**接口路径**: `/api/app-automation/packages/{id}/`
**请求方式**: `GET`

**描述**: APP应用包名管理 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP应用包名. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppPackage`

---

#### api_app_automation_packages_update
**接口路径**: `/api/app-automation/packages/{id}/`
**请求方式**: `PUT`

**描述**: APP应用包名管理 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP应用包名. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppPackage`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppPackage`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppPackage`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppPackage`

---

#### api_app_automation_packages_partial_update
**接口路径**: `/api/app-automation/packages/{id}/`
**请求方式**: `PATCH`

**描述**: APP应用包名管理 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP应用包名. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedAppPackage`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedAppPackage`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedAppPackage`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppPackage`

---

#### api_app_automation_packages_destroy
**接口路径**: `/api/app-automation/packages/{id}/`
**请求方式**: `DELETE`

**描述**: APP应用包名管理 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP应用包名. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_app_automation_projects_list
**接口路径**: `/api/app-automation/projects/`
**请求方式**: `GET`

**描述**: APP自动化项目 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| owner | query | 否 | integer |  |
| page | query | 否 | integer | A page number within the paginated result set. |
| page_size | query | 否 | integer | Number of results to return per page. |
| search | query | 否 | string | A search term. |
| status | query | 否 | string | * `NOT_STARTED` - 未开始 * `IN_PROGRESS` - 进行中 * `COMPLETED` - 已结束 |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedAppProjectList`

---

#### api_app_automation_projects_create
**接口路径**: `/api/app-automation/projects/`
**请求方式**: `POST`

**描述**: APP自动化项目 ViewSet

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppProjectCreate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppProjectCreate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppProjectCreate`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `AppProjectCreate`

---

#### api_app_automation_projects_retrieve
**接口路径**: `/api/app-automation/projects/{id}/`
**请求方式**: `GET`

**描述**: APP自动化项目 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP自动化项目. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppProject`

---

#### api_app_automation_projects_update
**接口路径**: `/api/app-automation/projects/{id}/`
**请求方式**: `PUT`

**描述**: APP自动化项目 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP自动化项目. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppProjectUpdate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppProjectUpdate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppProjectUpdate`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppProjectUpdate`

---

#### api_app_automation_projects_partial_update
**接口路径**: `/api/app-automation/projects/{id}/`
**请求方式**: `PATCH`

**描述**: APP自动化项目 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP自动化项目. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedAppProjectUpdate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedAppProjectUpdate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedAppProjectUpdate`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppProjectUpdate`

---

#### api_app_automation_projects_destroy
**接口路径**: `/api/app-automation/projects/{id}/`
**请求方式**: `DELETE`

**描述**: APP自动化项目 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP自动化项目. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_app_automation_scheduled_tasks_list
**接口路径**: `/api/app-automation/scheduled-tasks/`
**请求方式**: `GET`

**描述**: APP定时任务视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| page_size | query | 否 | integer | Number of results to return per page. |
| project | query | 否 | integer |  |
| search | query | 否 | string | A search term. |
| status | query | 否 | string | * `ACTIVE` - 激活 * `PAUSED` - 暂停 * `COMPLETED` - 已完成 * `FAILED` - 失败 |
| task_type | query | 否 | string | * `TEST_SUITE` - 测试套件执行 * `TEST_CASE` - 测试用例执行 |
| trigger_type | query | 否 | string | * `CRON` - Cron表达式 * `INTERVAL` - 固定间隔 * `ONCE` - 单次执行 |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedAppScheduledTaskList`

---

#### api_app_automation_scheduled_tasks_create
**接口路径**: `/api/app-automation/scheduled-tasks/`
**请求方式**: `POST`

**描述**: APP定时任务视图集

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppScheduledTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppScheduledTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppScheduledTask`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `AppScheduledTask`

---

#### api_app_automation_scheduled_tasks_retrieve
**接口路径**: `/api/app-automation/scheduled-tasks/{id}/`
**请求方式**: `GET`

**描述**: APP定时任务视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP定时任务. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppScheduledTask`

---

#### api_app_automation_scheduled_tasks_update
**接口路径**: `/api/app-automation/scheduled-tasks/{id}/`
**请求方式**: `PUT`

**描述**: APP定时任务视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP定时任务. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppScheduledTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppScheduledTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppScheduledTask`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppScheduledTask`

---

#### api_app_automation_scheduled_tasks_partial_update
**接口路径**: `/api/app-automation/scheduled-tasks/{id}/`
**请求方式**: `PATCH`

**描述**: APP定时任务视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP定时任务. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedAppScheduledTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedAppScheduledTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedAppScheduledTask`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppScheduledTask`

---

#### api_app_automation_scheduled_tasks_destroy
**接口路径**: `/api/app-automation/scheduled-tasks/{id}/`
**请求方式**: `DELETE`

**描述**: APP定时任务视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP定时任务. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_app_automation_scheduled_tasks_pause_create
**接口路径**: `/api/app-automation/scheduled-tasks/{id}/pause/`
**请求方式**: `POST`

**描述**: APP定时任务视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP定时任务. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppScheduledTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppScheduledTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppScheduledTask`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppScheduledTask`

---

#### api_app_automation_scheduled_tasks_resume_create
**接口路径**: `/api/app-automation/scheduled-tasks/{id}/resume/`
**请求方式**: `POST`

**描述**: APP定时任务视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP定时任务. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppScheduledTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppScheduledTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppScheduledTask`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppScheduledTask`

---

#### api_app_automation_scheduled_tasks_run_now_create
**接口路径**: `/api/app-automation/scheduled-tasks/{id}/run_now/`
**请求方式**: `POST`

**描述**: 立即运行任务

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP定时任务. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppScheduledTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppScheduledTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppScheduledTask`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppScheduledTask`

---

#### api_app_automation_test_cases_list
**接口路径**: `/api/app-automation/test-cases/`
**请求方式**: `GET`

**描述**: APP测试用例 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| app_package | query | 否 | integer |  |
| page | query | 否 | integer | A page number within the paginated result set. |
| page_size | query | 否 | integer | Number of results to return per page. |
| project | query | 否 | integer |  |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedAppTestCaseList`

---

#### api_app_automation_test_cases_create
**接口路径**: `/api/app-automation/test-cases/`
**请求方式**: `POST`

**描述**: APP测试用例 ViewSet

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppTestCase`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppTestCase`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppTestCase`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `AppTestCase`

---

#### api_app_automation_test_cases_retrieve
**接口路径**: `/api/app-automation/test-cases/{id}/`
**请求方式**: `GET`

**描述**: APP测试用例 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试用例. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppTestCase`

---

#### api_app_automation_test_cases_update
**接口路径**: `/api/app-automation/test-cases/{id}/`
**请求方式**: `PUT`

**描述**: APP测试用例 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试用例. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppTestCase`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppTestCase`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppTestCase`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppTestCase`

---

#### api_app_automation_test_cases_partial_update
**接口路径**: `/api/app-automation/test-cases/{id}/`
**请求方式**: `PATCH`

**描述**: APP测试用例 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试用例. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedAppTestCase`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedAppTestCase`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedAppTestCase`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppTestCase`

---

#### api_app_automation_test_cases_destroy
**接口路径**: `/api/app-automation/test-cases/{id}/`
**请求方式**: `DELETE`

**描述**: APP测试用例 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试用例. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_app_automation_test_cases_execute_create
**接口路径**: `/api/app-automation/test-cases/{id}/execute/`
**请求方式**: `POST`

**描述**: 执行测试用例

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试用例. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppTestCase`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppTestCase`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppTestCase`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppTestCase`

---

#### api_app_automation_test_suites_list
**接口路径**: `/api/app-automation/test-suites/`
**请求方式**: `GET`

**描述**: APP测试套件 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| page | query | 否 | integer | A page number within the paginated result set. |
| page_size | query | 否 | integer | Number of results to return per page. |
| project | query | 否 | integer |  |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedAppTestSuiteList`

---

#### api_app_automation_test_suites_create
**接口路径**: `/api/app-automation/test-suites/`
**请求方式**: `POST`

**描述**: APP测试套件 ViewSet

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppTestSuiteCreate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppTestSuiteCreate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppTestSuiteCreate`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `AppTestSuiteCreate`

---

#### api_app_automation_test_suites_retrieve
**接口路径**: `/api/app-automation/test-suites/{id}/`
**请求方式**: `GET`

**描述**: APP测试套件 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试套件. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppTestSuite`

---

#### api_app_automation_test_suites_update
**接口路径**: `/api/app-automation/test-suites/{id}/`
**请求方式**: `PUT`

**描述**: APP测试套件 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试套件. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppTestSuiteUpdate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppTestSuiteUpdate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppTestSuiteUpdate`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppTestSuiteUpdate`

---

#### api_app_automation_test_suites_partial_update
**接口路径**: `/api/app-automation/test-suites/{id}/`
**请求方式**: `PATCH`

**描述**: APP测试套件 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试套件. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedAppTestSuiteUpdate`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedAppTestSuiteUpdate`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedAppTestSuiteUpdate`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppTestSuiteUpdate`

---

#### api_app_automation_test_suites_destroy
**接口路径**: `/api/app-automation/test-suites/{id}/`
**请求方式**: `DELETE`

**描述**: APP测试套件 ViewSet

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试套件. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_app_automation_test_suites_add_test_case_create
**接口路径**: `/api/app-automation/test-suites/{id}/add_test_case/`
**请求方式**: `POST`

**描述**: 向套件添加用例

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试套件. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppTestSuite`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppTestSuite`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppTestSuite`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppTestSuite`

---

#### api_app_automation_test_suites_add_test_cases_create
**接口路径**: `/api/app-automation/test-suites/{id}/add_test_cases/`
**请求方式**: `POST`

**描述**: 批量添加用例到套件

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试套件. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppTestSuite`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppTestSuite`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppTestSuite`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppTestSuite`

---

#### api_app_automation_test_suites_executions_retrieve
**接口路径**: `/api/app-automation/test-suites/{id}/executions/`
**请求方式**: `GET`

**描述**: 获取套件的执行历史

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试套件. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppTestSuite`

---

#### api_app_automation_test_suites_remove_test_case_create
**接口路径**: `/api/app-automation/test-suites/{id}/remove_test_case/`
**请求方式**: `POST`

**描述**: 从套件移除用例

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试套件. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppTestSuite`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppTestSuite`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppTestSuite`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppTestSuite`

---

#### api_app_automation_test_suites_run_create
**接口路径**: `/api/app-automation/test-suites/{id}/run/`
**请求方式**: `POST`

**描述**: 执行测试套件（顺序执行所有用例）

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试套件. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppTestSuite`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppTestSuite`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppTestSuite`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppTestSuite`

---

#### api_app_automation_test_suites_test_cases_retrieve
**接口路径**: `/api/app-automation/test-suites/{id}/test_cases/`
**请求方式**: `GET`

**描述**: 获取套件中的所有用例（按顺序）

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试套件. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppTestSuite`

---

#### api_app_automation_test_suites_update_test_case_order_create
**接口路径**: `/api/app-automation/test-suites/{id}/update_test_case_order/`
**请求方式**: `POST`

**描述**: 更新套件中用例的顺序

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this APP测试套件. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AppTestSuite`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AppTestSuite`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AppTestSuite`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AppTestSuite`

---

### 接口测试
#### api_api_testing_ai_service_configs_list
**接口路径**: `/api/api-testing/ai-service-configs/`
**请求方式**: `GET`

**描述**: AI服务配置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| is_active | query | 否 | boolean |  |
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| role | query | 否 | string | * `doc_extractor` - API文档提取 * `naming` - 参数命名规范化 * `mock_data` - 模拟数据生成 * `description` - 参数描述补全 |
| search | query | 否 | string | A search term. |
| service_type | query | 否 | string | * `openai` - OpenAI * `azure` - Azure OpenAI * `anthropic` - Anthropic * `deepseek` - DeepSeek * `qwen` - 通义千问 * `siliconflow` - 硅基流动 * `other` - 其他 |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedAIServiceConfigList`

---

#### api_api_testing_ai_service_configs_create
**接口路径**: `/api/api-testing/ai-service-configs/`
**请求方式**: `POST`

**描述**: AI服务配置视图集

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AIServiceConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AIServiceConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AIServiceConfig`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `AIServiceConfig`

---

#### api_api_testing_ai_service_configs_retrieve
**接口路径**: `/api/api-testing/ai-service-configs/{id}/`
**请求方式**: `GET`

**描述**: AI服务配置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI服务配置. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AIServiceConfig`

---

#### api_api_testing_ai_service_configs_update
**接口路径**: `/api/api-testing/ai-service-configs/{id}/`
**请求方式**: `PUT`

**描述**: AI服务配置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI服务配置. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AIServiceConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AIServiceConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AIServiceConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AIServiceConfig`

---

#### api_api_testing_ai_service_configs_partial_update
**接口路径**: `/api/api-testing/ai-service-configs/{id}/`
**请求方式**: `PATCH`

**描述**: AI服务配置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI服务配置. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedAIServiceConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedAIServiceConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedAIServiceConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AIServiceConfig`

---

#### api_api_testing_ai_service_configs_destroy
**接口路径**: `/api/api-testing/ai-service-configs/{id}/`
**请求方式**: `DELETE`

**描述**: AI服务配置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this AI服务配置. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_api_testing_ai_service_configs_complete_parameter_descriptions_create
**接口路径**: `/api/api-testing/ai-service-configs/complete_parameter_descriptions/`
**请求方式**: `POST`

**描述**: 使用AI自动补全参数描述

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AIServiceConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AIServiceConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AIServiceConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AIServiceConfig`

---

#### api_api_testing_ai_service_configs_extract_documentation_create
**接口路径**: `/api/api-testing/ai-service-configs/extract_documentation/`
**请求方式**: `POST`

**描述**: 使用AI提取API文档

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AIServiceConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AIServiceConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AIServiceConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AIServiceConfig`

---

#### api_api_testing_ai_service_configs_generate_mock_data_create
**接口路径**: `/api/api-testing/ai-service-configs/generate_mock_data/`
**请求方式**: `POST`

**描述**: 使用AI生成模拟数据

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AIServiceConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AIServiceConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AIServiceConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AIServiceConfig`

---

#### api_api_testing_ai_service_configs_normalize_parameter_names_create
**接口路径**: `/api/api-testing/ai-service-configs/normalize_parameter_names/`
**请求方式**: `POST`

**描述**: 使用AI规范化参数名称

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AIServiceConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AIServiceConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AIServiceConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AIServiceConfig`

---

#### api_api_testing_ai_service_configs_test_connection_create
**接口路径**: `/api/api-testing/ai-service-configs/test_connection/`
**请求方式**: `POST`

**描述**: 测试AI服务连接

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `AIServiceConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `AIServiceConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `AIServiceConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `AIServiceConfig`

---

#### api_api_testing_collections_list
**接口路径**: `/api/api-testing/collections/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| page | query | 否 | integer | A page number within the paginated result set. |
| parent | query | 否 | integer |  |
| project | query | 否 | integer |  |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedApiCollectionList`

---

#### api_api_testing_collections_create
**接口路径**: `/api/api-testing/collections/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `ApiCollection`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `ApiCollection`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `ApiCollection`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `ApiCollection`

---

#### api_api_testing_collections_retrieve
**接口路径**: `/api/api-testing/collections/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this API集合. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ApiCollection`

---

#### api_api_testing_collections_update
**接口路径**: `/api/api-testing/collections/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this API集合. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `ApiCollection`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `ApiCollection`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `ApiCollection`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ApiCollection`

---

#### api_api_testing_collections_partial_update
**接口路径**: `/api/api-testing/collections/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this API集合. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedApiCollection`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedApiCollection`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedApiCollection`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ApiCollection`

---

#### api_api_testing_collections_destroy
**接口路径**: `/api/api-testing/collections/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this API集合. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_api_testing_dashboard_stats_retrieve
**接口路径**: `/api/api-testing/dashboard/stats/`
**请求方式**: `GET`

**描述**: 获取仪表盘统计数据

**响应示例**:
- **状态码 `200`**: No response body

---

#### api_api_testing_environments_list
**接口路径**: `/api/api-testing/environments/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| is_active | query | 否 | boolean |  |
| page | query | 否 | integer | A page number within the paginated result set. |
| project | query | 否 | integer |  |
| scope | query | 否 | string | * `GLOBAL` - 全局环境变量 * `LOCAL` - 局部环境变量 |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedEnvironmentList`

---

#### api_api_testing_environments_create
**接口路径**: `/api/api-testing/environments/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `Environment`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `Environment`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `Environment`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `Environment`

---

#### api_api_testing_environments_retrieve
**接口路径**: `/api/api-testing/environments/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 环境变量. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `Environment`

---

#### api_api_testing_environments_update
**接口路径**: `/api/api-testing/environments/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 环境变量. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `Environment`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `Environment`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `Environment`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `Environment`

---

#### api_api_testing_environments_partial_update
**接口路径**: `/api/api-testing/environments/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 环境变量. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedEnvironment`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedEnvironment`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedEnvironment`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `Environment`

---

#### api_api_testing_environments_destroy
**接口路径**: `/api/api-testing/environments/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 环境变量. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_api_testing_environments_activate_create
**接口路径**: `/api/api-testing/environments/{id}/activate/`
**请求方式**: `POST`

**描述**: 激活环境

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 环境变量. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `Environment`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `Environment`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `Environment`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `Environment`

---

#### api_api_testing_histories_list
**接口路径**: `/api/api-testing/histories/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| page_size | query | 否 | integer | Number of results to return per page. |
| request__request_type | query | 否 | string | * `HTTP` - HTTP * `WEBSOCKET` - WebSocket |
| status_code | query | 否 | integer |  |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedRequestHistoryList`

---

#### api_api_testing_histories_create
**接口路径**: `/api/api-testing/histories/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `RequestHistory`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `RequestHistory`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `RequestHistory`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `RequestHistory`

---

#### api_api_testing_histories_retrieve
**接口路径**: `/api/api-testing/histories/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 请求历史. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `RequestHistory`

---

#### api_api_testing_histories_update
**接口路径**: `/api/api-testing/histories/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 请求历史. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `RequestHistory`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `RequestHistory`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `RequestHistory`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `RequestHistory`

---

#### api_api_testing_histories_partial_update
**接口路径**: `/api/api-testing/histories/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 请求历史. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedRequestHistory`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedRequestHistory`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedRequestHistory`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `RequestHistory`

---

#### api_api_testing_histories_destroy
**接口路径**: `/api/api-testing/histories/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 请求历史. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_api_testing_histories_batch_delete_create
**接口路径**: `/api/api-testing/histories/batch-delete/`
**请求方式**: `POST`

**描述**: 批量删除请求历史

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `RequestHistory`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `RequestHistory`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `RequestHistory`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `RequestHistory`

---

#### api_api_testing_notification_logs_list
**接口路径**: `/api/api-testing/notification-logs/`
**请求方式**: `GET`

**描述**: 通知日志视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| notification_type | query | 否 | string | * `task_execution` - 定时任务执行 * `test_suite_execution` - 测试套件执行 * `api_request_execution` - API请求执行 * `system_alert` - 系统警告 * `manual` - 手动通知 |
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| status | query | 否 | string | * `pending` - 待发送 * `sending` - 发送中 * `success` - 发送成功 * `failed` - 发送失败 * `cancelled` - 已取消 |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedNotificationLogList`

---

#### api_api_testing_notification_logs_retrieve
**接口路径**: `/api/api-testing/notification-logs/{id}/`
**请求方式**: `GET`

**描述**: 通知日志视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 通知日志. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `NotificationLog`

---

#### api_api_testing_notification_logs_detail_retrieve
**接口路径**: `/api/api-testing/notification-logs/{id}/detail/`
**请求方式**: `GET`

**描述**: 获取通知详情

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 通知日志. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `NotificationLog`

---

#### api_api_testing_operation_logs_list
**接口路径**: `/api/api-testing/operation-logs/`
**请求方式**: `GET`

**描述**: 操作日志视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| operation_type | query | 否 | string | * `create` - 新增 * `edit` - 编辑 * `delete` - 删除 * `execute` - 执行 * `run` - 运行 * `save` - 保存 |
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| resource_type | query | 否 | string | * `project` - 项目 * `collection` - 集合 * `request` - 请求 * `suite` - 测试套件 * `environment` - 环境 * `task` - 定时任务 * `execution` - 执行记录 |
| user | query | 否 | integer |  |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedOperationLogList`

---

#### api_api_testing_operation_logs_retrieve
**接口路径**: `/api/api-testing/operation-logs/{id}/`
**请求方式**: `GET`

**描述**: 操作日志视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this API操作日志. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `OperationLog`

---

#### api_api_testing_projects_list
**接口路径**: `/api/api-testing/projects/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| owner | query | 否 | integer |  |
| page | query | 否 | integer | A page number within the paginated result set. |
| project_type | query | 否 | string | * `HTTP` - HTTP * `WEBSOCKET` - WebSocket |
| search | query | 否 | string | A search term. |
| status | query | 否 | string | * `NOT_STARTED` - 未开始 * `IN_PROGRESS` - 进行中 * `COMPLETED` - 已结束 |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedApiProjectList`

---

#### api_api_testing_projects_create
**接口路径**: `/api/api-testing/projects/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `ApiProject`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `ApiProject`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `ApiProject`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `ApiProject`

---

#### api_api_testing_projects_retrieve
**接口路径**: `/api/api-testing/projects/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this API项目. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ApiProject`

---

#### api_api_testing_projects_update
**接口路径**: `/api/api-testing/projects/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this API项目. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `ApiProject`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `ApiProject`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `ApiProject`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ApiProject`

---

#### api_api_testing_projects_partial_update
**接口路径**: `/api/api-testing/projects/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this API项目. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedApiProject`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedApiProject`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedApiProject`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ApiProject`

---

#### api_api_testing_projects_destroy
**接口路径**: `/api/api-testing/projects/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this API项目. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_api_testing_projects_create_sample_create
**接口路径**: `/api/api-testing/projects/create-sample/`
**请求方式**: `POST`

**描述**: 创建示例项目（宠物店）

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `ApiProject`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `ApiProject`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `ApiProject`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ApiProject`

---

#### api_api_testing_requests_list
**接口路径**: `/api/api-testing/requests/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| collection | query | 否 | integer |  |
| method | query | 否 | string | * `GET` - GET * `POST` - POST * `PUT` - PUT * `DELETE` - DELETE * `PATCH` - PATCH * `HEAD` - HEAD * `OPTIONS` - OPTIONS |
| page | query | 否 | integer | A page number within the paginated result set. |
| request_type | query | 否 | string | * `HTTP` - HTTP * `WEBSOCKET` - WebSocket |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedApiRequestList`

---

#### api_api_testing_requests_create
**接口路径**: `/api/api-testing/requests/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `ApiRequest`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `ApiRequest`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `ApiRequest`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `ApiRequest`

---

#### api_api_testing_requests_retrieve
**接口路径**: `/api/api-testing/requests/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this API请求. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ApiRequest`

---

#### api_api_testing_requests_update
**接口路径**: `/api/api-testing/requests/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this API请求. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `ApiRequest`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `ApiRequest`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `ApiRequest`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ApiRequest`

---

#### api_api_testing_requests_partial_update
**接口路径**: `/api/api-testing/requests/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this API请求. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedApiRequest`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedApiRequest`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedApiRequest`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ApiRequest`

---

#### api_api_testing_requests_destroy
**接口路径**: `/api/api-testing/requests/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this API请求. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_api_testing_requests_execute_create
**接口路径**: `/api/api-testing/requests/{id}/execute/`
**请求方式**: `POST`

**描述**: 执行API请求

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this API请求. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `ApiRequest`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `ApiRequest`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `ApiRequest`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ApiRequest`

---

#### api_api_testing_scheduled_tasks_list
**接口路径**: `/api/api-testing/scheduled-tasks/`
**请求方式**: `GET`

**描述**: 定时任务视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedScheduledTaskList`

---

#### api_api_testing_scheduled_tasks_create
**接口路径**: `/api/api-testing/scheduled-tasks/`
**请求方式**: `POST`

**描述**: 定时任务视图集

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `ScheduledTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `ScheduledTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `ScheduledTask`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `ScheduledTask`

---

#### api_api_testing_scheduled_tasks_retrieve
**接口路径**: `/api/api-testing/scheduled-tasks/{id}/`
**请求方式**: `GET`

**描述**: 定时任务视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 定时任务. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ScheduledTask`

---

#### api_api_testing_scheduled_tasks_update
**接口路径**: `/api/api-testing/scheduled-tasks/{id}/`
**请求方式**: `PUT`

**描述**: 定时任务视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 定时任务. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `ScheduledTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `ScheduledTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `ScheduledTask`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ScheduledTask`

---

#### api_api_testing_scheduled_tasks_partial_update
**接口路径**: `/api/api-testing/scheduled-tasks/{id}/`
**请求方式**: `PATCH`

**描述**: 定时任务视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 定时任务. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedScheduledTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedScheduledTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedScheduledTask`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ScheduledTask`

---

#### api_api_testing_scheduled_tasks_destroy
**接口路径**: `/api/api-testing/scheduled-tasks/{id}/`
**请求方式**: `DELETE`

**描述**: 定时任务视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 定时任务. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_api_testing_scheduled_tasks_activate_create
**接口路径**: `/api/api-testing/scheduled-tasks/{id}/activate/`
**请求方式**: `POST`

**描述**: 激活定时任务

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 定时任务. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `ScheduledTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `ScheduledTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `ScheduledTask`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ScheduledTask`

---

#### api_api_testing_scheduled_tasks_execution_logs_retrieve
**接口路径**: `/api/api-testing/scheduled-tasks/{id}/execution_logs/`
**请求方式**: `GET`

**描述**: 获取任务执行日志

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 定时任务. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ScheduledTask`

---

#### api_api_testing_scheduled_tasks_pause_create
**接口路径**: `/api/api-testing/scheduled-tasks/{id}/pause/`
**请求方式**: `POST`

**描述**: 暂停定时任务

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 定时任务. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `ScheduledTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `ScheduledTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `ScheduledTask`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ScheduledTask`

---

#### api_api_testing_scheduled_tasks_run_now_create
**接口路径**: `/api/api-testing/scheduled-tasks/{id}/run_now/`
**请求方式**: `POST`

**描述**: 立即执行定时任务

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 定时任务. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `ScheduledTask`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `ScheduledTask`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `ScheduledTask`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `ScheduledTask`

---

#### api_api_testing_task_execution_logs_list
**接口路径**: `/api/api-testing/task-execution-logs/`
**请求方式**: `GET`

**描述**: 任务执行日志视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| status | query | 否 | string | * `PENDING` - 待执行 * `RUNNING` - 执行中 * `COMPLETED` - 已完成 * `FAILED` - 失败 * `CANCELLED` - 已取消 |
| task | query | 否 | integer |  |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedTaskExecutionLogList`

---

#### api_api_testing_task_execution_logs_retrieve
**接口路径**: `/api/api-testing/task-execution-logs/{id}/`
**请求方式**: `GET`

**描述**: 任务执行日志视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 任务执行日志. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TaskExecutionLog`

---

#### api_api_testing_task_notification_settings_list
**接口路径**: `/api/api-testing/task-notification-settings/`
**请求方式**: `GET`

**描述**: 定时任务通知设置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| is_enabled | query | 否 | boolean |  |
| page | query | 否 | integer | A page number within the paginated result set. |
| task | query | 否 | integer |  |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedTaskNotificationSettingList`

---

#### api_api_testing_task_notification_settings_create
**接口路径**: `/api/api-testing/task-notification-settings/`
**请求方式**: `POST`

**描述**: 定时任务通知设置视图集

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TaskNotificationSetting`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TaskNotificationSetting`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TaskNotificationSetting`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `TaskNotificationSetting`

---

#### api_api_testing_task_notification_settings_retrieve
**接口路径**: `/api/api-testing/task-notification-settings/{id}/`
**请求方式**: `GET`

**描述**: 定时任务通知设置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 任务通知设置. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TaskNotificationSetting`

---

#### api_api_testing_task_notification_settings_update
**接口路径**: `/api/api-testing/task-notification-settings/{id}/`
**请求方式**: `PUT`

**描述**: 定时任务通知设置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 任务通知设置. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TaskNotificationSetting`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TaskNotificationSetting`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TaskNotificationSetting`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TaskNotificationSetting`

---

#### api_api_testing_task_notification_settings_partial_update
**接口路径**: `/api/api-testing/task-notification-settings/{id}/`
**请求方式**: `PATCH`

**描述**: 定时任务通知设置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 任务通知设置. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedTaskNotificationSetting`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedTaskNotificationSetting`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedTaskNotificationSetting`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TaskNotificationSetting`

---

#### api_api_testing_task_notification_settings_destroy
**接口路径**: `/api/api-testing/task-notification-settings/{id}/`
**请求方式**: `DELETE`

**描述**: 定时任务通知设置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 任务通知设置. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_api_testing_task_notification_settings_update_settings_create
**接口路径**: `/api/api-testing/task-notification-settings/{id}/update-settings/`
**请求方式**: `POST`

**描述**: 更新通知设置

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 任务通知设置. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TaskNotificationSetting`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TaskNotificationSetting`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TaskNotificationSetting`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TaskNotificationSetting`

---

#### api_api_testing_test_executions_list
**接口路径**: `/api/api-testing/test-executions/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| page_size | query | 否 | integer | Number of results to return per page. |
| status | query | 否 | string | * `PENDING` - 待执行 * `RUNNING` - 执行中 * `COMPLETED` - 已完成 * `FAILED` - 执行失败 * `CANCELLED` - 已取消 |
| test_suite | query | 否 | integer |  |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedTestExecutionList`

---

#### api_api_testing_test_executions_retrieve
**接口路径**: `/api/api-testing/test-executions/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试执行. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestExecution`

---

#### api_api_testing_test_executions_generate_allure_report_create
**接口路径**: `/api/api-testing/test-executions/{id}/generate-allure-report/`
**请求方式**: `POST`

**描述**: 生成Allure报告数据

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试执行. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestExecution`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestExecution`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestExecution`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestExecution`

---

#### api_api_testing_test_suite_requests_list
**接口路径**: `/api/api-testing/test-suite-requests/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| enabled | query | 否 | boolean |  |
| page | query | 否 | integer | A page number within the paginated result set. |
| test_suite | query | 否 | integer |  |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedTestSuiteRequestList`

---

#### api_api_testing_test_suite_requests_create
**接口路径**: `/api/api-testing/test-suite-requests/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestSuiteRequest`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestSuiteRequest`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestSuiteRequest`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `TestSuiteRequest`

---

#### api_api_testing_test_suite_requests_retrieve
**接口路径**: `/api/api-testing/test-suite-requests/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 套件请求. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestSuiteRequest`

---

#### api_api_testing_test_suite_requests_update
**接口路径**: `/api/api-testing/test-suite-requests/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 套件请求. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestSuiteRequest`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestSuiteRequest`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestSuiteRequest`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestSuiteRequest`

---

#### api_api_testing_test_suite_requests_partial_update
**接口路径**: `/api/api-testing/test-suite-requests/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 套件请求. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedTestSuiteRequest`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedTestSuiteRequest`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedTestSuiteRequest`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestSuiteRequest`

---

#### api_api_testing_test_suite_requests_destroy
**接口路径**: `/api/api-testing/test-suite-requests/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 套件请求. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_api_testing_test_suites_list
**接口路径**: `/api/api-testing/test-suites/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| page | query | 否 | integer | A page number within the paginated result set. |
| project | query | 否 | integer |  |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedTestSuiteList`

---

#### api_api_testing_test_suites_create
**接口路径**: `/api/api-testing/test-suites/`
**请求方式**: `POST`

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestSuite`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestSuite`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestSuite`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `TestSuite`

---

#### api_api_testing_test_suites_retrieve
**接口路径**: `/api/api-testing/test-suites/{id}/`
**请求方式**: `GET`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试套件. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestSuite`

---

#### api_api_testing_test_suites_update
**接口路径**: `/api/api-testing/test-suites/{id}/`
**请求方式**: `PUT`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试套件. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestSuite`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestSuite`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestSuite`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestSuite`

---

#### api_api_testing_test_suites_partial_update
**接口路径**: `/api/api-testing/test-suites/{id}/`
**请求方式**: `PATCH`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试套件. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedTestSuite`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedTestSuite`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedTestSuite`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestSuite`

---

#### api_api_testing_test_suites_destroy
**接口路径**: `/api/api-testing/test-suites/{id}/`
**请求方式**: `DELETE`

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试套件. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_api_testing_test_suites_add_requests_create
**接口路径**: `/api/api-testing/test-suites/{id}/add-requests/`
**请求方式**: `POST`

**描述**: 添加请求到测试套件

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试套件. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestSuite`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestSuite`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestSuite`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestSuite`

---

#### api_api_testing_test_suites_execute_create
**接口路径**: `/api/api-testing/test-suites/{id}/execute/`
**请求方式**: `POST`

**描述**: 执行测试套件

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 测试套件. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `TestSuite`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `TestSuite`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `TestSuite`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `TestSuite`

---

#### api_api_testing_users_list
**接口路径**: `/api/api-testing/users/`
**请求方式**: `GET`

**描述**: 用户列表接口，用于项目成员选择

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedUserList`

---

#### api_api_testing_users_retrieve
**接口路径**: `/api/api-testing/users/{id}/`
**请求方式**: `GET`

**描述**: 用户列表接口，用于项目成员选择

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 用户. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `User`

---

#### api_core_notification_configs_list
**接口路径**: `/api/core/notification-configs/`
**请求方式**: `GET`

**描述**: 统一通知配置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| config_type | query | 否 | string | * `webhook_feishu` - 飞书机器人 * `webhook_wechat` - 企业微信机器人 * `webhook_dingtalk` - 钉钉机器人 |
| is_active | query | 否 | boolean |  |
| is_default | query | 否 | boolean |  |
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedUnifiedNotificationConfigList`

---

#### api_core_notification_configs_create
**接口路径**: `/api/core/notification-configs/`
**请求方式**: `POST`

**描述**: 统一通知配置视图集

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `UnifiedNotificationConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `UnifiedNotificationConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `UnifiedNotificationConfig`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `UnifiedNotificationConfig`

---

#### api_core_notification_configs_retrieve
**接口路径**: `/api/core/notification-configs/{id}/`
**请求方式**: `GET`

**描述**: 统一通知配置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 统一通知配置. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `UnifiedNotificationConfig`

---

#### api_core_notification_configs_update
**接口路径**: `/api/core/notification-configs/{id}/`
**请求方式**: `PUT`

**描述**: 统一通知配置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 统一通知配置. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `UnifiedNotificationConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `UnifiedNotificationConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `UnifiedNotificationConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `UnifiedNotificationConfig`

---

#### api_core_notification_configs_partial_update
**接口路径**: `/api/core/notification-configs/{id}/`
**请求方式**: `PATCH`

**描述**: 统一通知配置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 统一通知配置. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedUnifiedNotificationConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedUnifiedNotificationConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedUnifiedNotificationConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `UnifiedNotificationConfig`

---

#### api_core_notification_configs_destroy
**接口路径**: `/api/core/notification-configs/{id}/`
**请求方式**: `DELETE`

**描述**: 统一通知配置视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 统一通知配置. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_core_notification_configs_set_default_create
**接口路径**: `/api/core/notification-configs/{id}/set_default/`
**请求方式**: `POST`

**描述**: 设置为默认配置

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 统一通知配置. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `UnifiedNotificationConfig`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `UnifiedNotificationConfig`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `UnifiedNotificationConfig`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `UnifiedNotificationConfig`

---

#### api_core_notification_configs_active_configs_retrieve
**接口路径**: `/api/core/notification-configs/active_configs/`
**请求方式**: `GET`

**描述**: 获取所有启用的配置

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `UnifiedNotificationConfig`

---

### 数据工厂
#### api_data_factory_list
**接口路径**: `/api/data-factory/`
**请求方式**: `GET`

**描述**: 重写list方法以正确处理分页

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| ordering | query | 否 | string | Which field to use when ordering the results. |
| page | query | 否 | integer | A page number within the paginated result set. |
| page_size | query | 否 | integer | Number of results to return per page. |
| search | query | 否 | string | A search term. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `PaginatedDataFactoryRecordList`

---

#### api_data_factory_create
**接口路径**: `/api/data-factory/`
**请求方式**: `POST`

**描述**: 执行工具并保存结果

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `DataFactoryRecord`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `DataFactoryRecord`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `DataFactoryRecord`

**响应示例**:
- **状态码 `201`**: 
  - 返回模型: `DataFactoryRecord`

---

#### api_data_factory_retrieve
**接口路径**: `/api/data-factory/{id}/`
**请求方式**: `GET`

**描述**: 数据工厂视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 数据工厂记录. |

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `DataFactoryRecord`

---

#### api_data_factory_update
**接口路径**: `/api/data-factory/{id}/`
**请求方式**: `PUT`

**描述**: 数据工厂视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 数据工厂记录. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `DataFactoryRecord`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `DataFactoryRecord`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `DataFactoryRecord`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `DataFactoryRecord`

---

#### api_data_factory_partial_update
**接口路径**: `/api/data-factory/{id}/`
**请求方式**: `PATCH`

**描述**: 数据工厂视图集

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 数据工厂记录. |

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `PatchedDataFactoryRecord`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `PatchedDataFactoryRecord`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `PatchedDataFactoryRecord`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `DataFactoryRecord`

---

#### api_data_factory_destroy
**接口路径**: `/api/data-factory/{id}/`
**请求方式**: `DELETE`

**描述**: 删除数据工厂记录

**请求参数 (Query/Path)**:
| 参数名 | 位置 | 必填 | 类型 | 说明 |
|---|---|---|---|---|
| id | path | 是 | integer | A unique integer value identifying this 数据工厂记录. |

**响应示例**:
- **状态码 `204`**: No response body

---

#### api_data_factory_batch_generate_create
**接口路径**: `/api/data-factory/batch_generate/`
**请求方式**: `POST`

**描述**: 批量生成数据

**请求体 (Body)**:
- `Content-Type`: application/json
- `Schema`: 参照模型 `DataFactoryRecord`
- `Content-Type`: application/x-www-form-urlencoded
- `Schema`: 参照模型 `DataFactoryRecord`
- `Content-Type`: multipart/form-data
- `Schema`: 参照模型 `DataFactoryRecord`

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `DataFactoryRecord`

---

#### api_data_factory_categories_retrieve
**接口路径**: `/api/data-factory/categories/`
**请求方式**: `GET`

**描述**: 获取所有工具分类

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `DataFactoryRecord`

---

#### api_data_factory_download_static_file_retrieve
**接口路径**: `/api/data-factory/download_static_file/`
**请求方式**: `GET`

**描述**: 下载static_files/img目录下的文件
用于条形码和二维码的下载和预览

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `DataFactoryRecord`

---

#### api_data_factory_statistics_retrieve
**接口路径**: `/api/data-factory/statistics/`
**请求方式**: `GET`

**描述**: 获取使用统计

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `DataFactoryRecord`

---

#### api_data_factory_tags_retrieve
**接口路径**: `/api/data-factory/tags/`
**请求方式**: `GET`

**描述**: 获取所有标签列表

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `DataFactoryRecord`

---

#### api_data_factory_variable_functions_retrieve
**接口路径**: `/api/data-factory/variable_functions/`
**请求方式**: `GET`

**描述**: 获取所有变量函数列表（用于变量助手）

返回格式：
[
    {
        'name': 'random_int',
        'syntax': '${random_int(min, max, count)}',
        'desc': '生成随机整数',
        'example': '${random_int(100, 999, 1)}'
        'category': '随机数'
    },
    ...
]

**响应示例**:
- **状态码 `200`**: 
  - 返回模型: `DataFactoryRecord`

---

## 数据模型参考 (Models)

### AICase
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| project |  |  |
| created_by |  |  |
| project_id | integer |  |
| name | string | 用例名称 |
| description | string | 描述 |
| task_description | string | 任务描述 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### AIExecutionRecord
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| project |  |  |
| project_id | integer |  |
| project_name | string |  |
| ai_case |  |  |
| ai_case_id | integer |  |
| ai_case_name | string |  |
| case_name | string | 用例名称快照 |
| task_description | string | 任务描述 |
| execution_mode |  | 执行模式 |
| status |  | 执行状态 |
| start_time | string | 开始时间 |
| end_time | string | 结束时间 |
| duration | number | 执行时长(秒) |
| logs | string | 执行日志 |
| steps_completed |  | 已完成步骤 |
| planned_tasks |  | 规划任务 |
| executed_by |  |  |
| executed_by_name | string |  |
| gif_path | string | GIF录制路径 |
| screenshots_sequence |  | 截图序列 |

### AIExecutionRecordStatusEnum
* `pending` - 等待中
* `running` - 执行中
* `passed` - 成功
* `failed` - 失败

### AIModelConfig
AI 模型配置序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 配置名称 |
| model_type |  | 模型类型 |
| model_type_display | string |  |
| role |  | 角色 |
| role_display | string |  |
| api_key | string |  |
| api_key_masked | string |  |
| base_url | string | API Base URL |
| model_name | string | 模型名称 |
| max_tokens | integer | 最大Token数 |
| temperature | number | 温度参数 |
| top_p | number | Top P参数 |
| is_active | boolean | 是否启用 |
| created_by | integer | 创建者 |
| created_by_name | string |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| usage_scope_summary | string |  |
| activation_summary | string |  |

### AIModelConfigRoleEnum
* `writer` - 测试用例编写专家
* `reviewer` - 测试评审专家
* `browser_use_text` - Browser Use - 文本模式

### AIServiceConfig
AI服务配置序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 配置名称 |
| service_type |  | 服务类型 |
| service_type_display | string |  |
| role |  | 角色类型 |
| role_display | string |  |
| api_key | string |  |
| base_url | string | API Base URL |
| model_name | string | 模型名称 |
| max_tokens | integer | 最大Token数 |
| temperature | number | 温度参数 |
| is_active | boolean | 是否启用 |
| created_by | integer | 创建者 |
| created_by_name | string |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### AIServiceConfigRoleEnum
* `doc_extractor` - API文档提取
* `naming` - 参数命名规范化
* `mock_data` - 模拟数据生成
* `description` - 参数描述补全

### AnalysisTask
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| task_id | string | 任务ID |
| task_type |  | 任务类型 |
| task_type_display | string |  |
| document | integer | 关联文档 |
| document_title | string |  |
| status |  | 状态 |
| status_display | string |  |
| progress | integer | 进度百分比 |
| result |  | 任务结果 |
| error_message | string | 错误信息 |
| started_at | string | 开始时间 |
| completed_at | string | 完成时间 |
| created_at | string | 创建时间 |
| duration | string |  |

### AnalysisTaskStatusEnum
* `pending` - 待处理
* `running` - 运行中
* `completed` - 已完成
* `failed` - 失败

### AnalysisTaskTaskTypeEnum
* `requirement_analysis` - 需求分析
* `testcase_generation` - 测试用例生成
* `testcase_review` - 测试用例评审

### ApiCollection
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 集合名称 |
| description | string | 集合描述 |
| project | integer | 所属项目 |
| parent | integer | 父级集合 |
| order | integer | 排序 |
| children | string |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### ApiProject
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 项目名称 |
| description | string | 项目描述 |
| project_type |  | 项目类型 |
| status |  | 项目状态 |
| owner |  |  |
| members | array |  |
| member_ids | array |  |
| start_date | string |  |
| end_date | string |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### ApiRequest
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 请求名称 |
| description | string | 请求描述 |
| request_type |  | 请求类型 |
| method |  | 请求方法 |
| url | string | 请求URL |
| headers |  | 请求头 |
| params |  | URL参数 |
| body |  | 请求体 |
| auth |  | 认证信息 |
| pre_request_script | string | 请求前脚本 |
| post_request_script | string | 请求后脚本 |
| assertions |  | 断言规则 |
| collection | integer |  |
| order | integer | 排序 |
| created_by |  |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### AppComponent
UI组件定义序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 组件名称 |
| type | string | 组件类型 |
| category | string | 类别 |
| description | string | 描述 |
| schema |  | 配置Schema |
| default_config |  | 默认配置 |
| enabled | boolean | 是否启用 |
| sort_order | integer | 排序 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### AppComponentPackage
组件包序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| created_by_name | string |  |
| name | string | 包名称 |
| version | string | 版本 |
| description | string | 描述 |
| author | string | 作者 |
| source |  | 来源 |
| manifest |  | 包清单 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| created_by | integer | 创建人 |

### AppCustomComponent
自定义组件定义序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 组件名称 |
| type | string | 组件类型 |
| description | string | 描述 |
| schema |  | 参数Schema |
| default_config |  | 默认参数 |
| steps |  | 组合步骤 |
| enabled | boolean | 是否启用 |
| sort_order | integer | 排序 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### AppDevice
APP设备序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| locked_by_name | string |  |
| device_id | string | 设备序列号 |
| name | string | 设备名称 |
| status |  | 状态 |
| android_version | string | Android版本 |
| connection_type |  | 连接类型 |
| ip_address | string | IP地址 |
| port | integer | 端口 |
| locked_at | string | 锁定时间 |
| max_allocation_time | integer | 最大分配时间(秒) |
| device_specs |  | 设备规格 |
| description | string | 设备描述 |
| location | string | 设备位置 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| locked_by | integer | 锁定用户 |

### AppDeviceStatusEnum
* `available` - 可用
* `locked` - 已锁定
* `online` - 在线
* `offline` - 离线

### AppElement
APP元素序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| created_by_name | string |  |
| element_type_display | string |  |
| preview_url | string |  |
| name | string | 元素名称 |
| element_type |  | 元素类型 |
| tags |  | 标签 |
| config |  | 元素配置 |
| resolution_configs |  | 分辨率配置 |
| usage_count | integer | 使用次数 |
| last_used_at | string | 最后使用时间 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| is_active | boolean | 是否启用 |
| project | integer | 所属项目 |
| created_by | integer | 创建人 |

### AppElementElementTypeEnum
* `image` - 图片元素
* `pos` - 坐标元素
* `region` - 区域元素

### AppNotificationLog
APP通知日志序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| task | integer | 关联任务 |
| task_name | string | 任务名称 |
| notification_type |  | 通知类型 |
| notification_type_display | string |  |
| actual_notification_type_display | string |  |
| task_type_display | string |  |
| sender_name | string | 发件人姓名 |
| sender_email | string | 发件人邮箱 |
| recipient_names | string |  |
| webhook_bot_info |  | Webhook机器人信息 |
| notification_content | string | 通知内容 |
| status |  | 发送状态 |
| status_display | string |  |
| error_message | string | 错误信息 |
| response_info |  | 响应信息 |
| created_at | string | 创建时间 |
| sent_at | string | 发送时间 |
| retry_count | integer | 重试次数 |
| retry_status | string |  |

### AppNotificationLogNotificationTypeEnum
* `task_execution` - 定时任务执行
* `test_suite_execution` - 测试套件执行
* `system_alert` - 系统警告
* `manual` - 手动通知

### AppPackage
APP应用包名序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| created_by_name | string |  |
| name | string | 应用名称 |
| package_name | string | 应用包名 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| created_by | integer | 创建人 |

### AppProject
APP项目序列化器 - 列表/详情

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| owner_name | string |  |
| member_count | string |  |
| test_case_count | string |  |
| test_suite_count | string |  |
| name | string | 项目名称 |
| description | string | 项目描述 |
| status |  | 项目状态 |
| start_date | string | 开始日期 |
| end_date | string | 结束日期 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| owner | integer | 负责人 |
| members | array | 团队成员 |

### AppProjectCreate
APP项目创建序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| name | string | 项目名称 |
| description | string | 项目描述 |
| status |  | 项目状态 |
| start_date | string | 开始日期 |
| end_date | string | 结束日期 |
| members | array | 团队成员 |

### AppProjectUpdate
APP项目更新序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| name | string | 项目名称 |
| description | string | 项目描述 |
| status |  | 项目状态 |
| start_date | string | 开始日期 |
| end_date | string | 结束日期 |
| members | array | 团队成员 |

### AppScheduledTask
APP定时任务序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 任务名称 |
| description | string | 任务描述 |
| project | integer | 所属项目 |
| task_type |  | 任务类型 |
| task_type_display | string |  |
| trigger_type |  | 触发器类型 |
| trigger_type_display | string |  |
| cron_expression | string | Cron表达式 |
| interval_seconds | integer | 间隔秒数 |
| execute_at | string | 执行时间 |
| device | integer | 执行设备 |
| device_name | string |  |
| app_package | integer | 应用包名 |
| app_package_name | string |  |
| test_suite | integer | 测试套件 |
| test_suite_name | string |  |
| test_case | integer | 测试用例 |
| test_case_name | string |  |
| notify_on_success | boolean | 成功时通知 |
| notify_on_failure | boolean | 失败时通知 |
| notification_type |  | 通知类型 |
| notification_type_display | string |  |
| notify_emails |  | 通知邮箱列表 |
| status |  | 任务状态 |
| status_display | string |  |
| last_run_time | string | 最后运行时间 |
| next_run_time | string | 下次运行时间 |
| total_runs | integer | 总运行次数 |
| successful_runs | integer | 成功次数 |
| failed_runs | integer | 失败次数 |
| last_result |  | 最后执行结果 |
| error_message | string | 错误信息 |
| created_by | integer | 创建者 |
| created_by_name | string |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### AppTestCase
APP测试用例序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| created_by_name | string |  |
| app_package_name | string |  |
| name | string | 用例名称 |
| description | string | 用例描述 |
| ui_flow |  | UI流程定义 |
| variables |  | 变量定义 |
| timeout | integer | 超时时间(秒) |
| retry_count | integer | 失败重试次数 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| project | integer | 所属项目 |
| app_package | integer | 应用包名 |
| created_by | integer | 创建人 |

### AppTestExecution
APP测试执行记录序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| case_name | string |  |
| device_name | string |  |
| user_name | string |  |
| pass_rate | number |  |
| status_display | string |  |
| result_display | string |  |
| status |  | 执行状态 |
| result |  | 测试结果 |
| task_id | string | Celery任务ID |
| progress | integer | 执行进度(0-100) |
| started_at | string | 开始时间 |
| finished_at | string | 结束时间 |
| duration | number | 执行时长(秒) |
| report_path | string | Allure报告路径 |
| error_message | string | 错误信息 |
| total_steps | integer | 总步骤数 |
| passed_steps | integer | 通过步骤数 |
| failed_steps | integer | 失败步骤数 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| test_case | integer | 测试用例 |
| test_suite | integer | 所属套件 |
| device | integer | 执行设备 |
| user | integer | 执行用户 |

### AppTestExecutionStatusEnum
* `pending` - 等待中
* `running` - 执行中
* `completed` - 已完成
* `error` - 执行异常
* `stopped` - 已停止

### AppTestSuite
测试套件列表序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 套件名称 |
| description | string | 套件描述 |
| project | integer | 所属项目 |
| execution_status |  | 执行状态 |
| execution_status_display | string |  |
| execution_result |  | 测试结果 |
| execution_result_display | string |  |
| passed_count | integer | 通过用例数 |
| failed_count | integer | 失败用例数 |
| last_run_at | string | 最后执行时间 |
| test_case_count | string |  |
| suite_cases | array |  |
| created_by | integer | 创建人 |
| created_by_name | string |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### AppTestSuiteCase
套件-用例关联序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| test_case | string |  |
| test_case_id | integer |  |
| order | integer | 执行顺序 |

### AppTestSuiteCreate
测试套件创建序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 套件名称 |
| description | string | 套件描述 |
| project | integer | 所属项目 |
| test_case_ids | array |  |

### AppTestSuiteExecutionStatusEnum
* `not_run` - 未执行
* `running` - 执行中
* `completed` - 已完成
* `error` - 执行异常

### AppTestSuiteUpdate
测试套件更新序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| name | string | 套件名称 |
| description | string | 套件描述 |
| project | integer | 所属项目 |

### AssertTypeEnum
* `textContains` - 文本包含
* `textEquals` - 文本等于
* `isVisible` - 元素可见
* `exists` - 元素存在
* `hasAttribute` - 属性值

### AssistantMessage
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| message_type |  | 消息类型 |
| content | string | 消息内容 |
| created_at | string | 创建时间 |

### AssistantSession
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| session_id | string | 会话ID |
| conversation_id | string | Dify对话ID |
| title | string | 会话标题 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| messages | array |  |
| chat_messages | array |  |

### AssistantSessionCreate
| 字段名 | 类型 | 说明 |
|---|---|---|
| session_id | string | 会话ID |
| title | string | 会话标题 |

### BlankEnum
### BusinessRequirement
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| requirement_id | string | 需求编号 |
| requirement_name | string | 需求名称 |
| requirement_type |  | 需求类型 |
| requirement_type_display | string |  |
| parent_requirement | integer | 父级需求 |
| parent_requirement_name | string |  |
| module | string | 所属模块 |
| requirement_level |  | 需求级别 |
| requirement_level_display | string |  |
| reviewer | string | 评审人 |
| estimated_hours | integer | 预计工时 |
| description | string | 需求描述 |
| acceptance_criteria | string | 验收标准 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### ChatMessage
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| role |  | 角色 |
| content | string | 消息内容 |
| conversation_id | string | Dify对话ID |
| message_id | string | Dify消息ID |
| created_at | string | 创建时间 |

### ChatMessageRoleEnum
* `user` - 用户
* `assistant` - 助手

### CommentTypeEnum
* `general` - 整体意见
* `testcase` - 用例意见
* `step` - 步骤意见

### ConfigTypeEnum
* `webhook_feishu` - 飞书机器人
* `webhook_wechat` - 企业微信机器人
* `webhook_dingtalk` - 钉钉机器人

### ConnectionTypeEnum
* `emulator` - 本地模拟器
* `remote_emulator` - 远程模拟器
* `real_device` - 真实设备

### DataFactoryRecord
数据工厂记录序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| user | integer | 用户 |
| user_name | string |  |
| tool_name | string | 工具名称 |
| tool_name_display | string |  |
| tool_category |  | 工具分类 |
| tool_category_display | string |  |
| tool_scenario |  | 使用场景 |
| tool_scenario_display | string |  |
| input_data |  | 输入数据 |
| output_data |  | 输出数据 |
| is_saved | boolean | 是否保存 |
| tags |  | 标签 |
| created_at | string | 创建时间 |

### DefaultOutputModeEnum
* `stream` - 实时流式输出
* `complete` - 完整输出

### DifyConfig
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| api_url | string | Dify API endpoint URL |
| api_key | string | Dify API密钥 |
| is_active | boolean | 是否启用 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### DocumentTypeEnum
* `pdf` - PDF文档
* `docx` - Word文档
* `txt` - 文本文档
* `md` - Markdown文档

### DocumentUpload
文档上传专用序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| title | string | 文档标题 |
| file | string | 文档文件 |
| project | integer | 关联项目 |

### Element
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| project |  |  |
| locator_strategy |  |  |
| created_by |  |  |
| project_id | integer |  |
| group_id | integer |  |
| locator_strategy_id | integer |  |
| name | string | 元素名称 |
| description | string | 元素描述 |
| element_type |  | 元素类型 |
| locator_value | string | 定位表达式 |
| backup_locators |  | 备用定位器 |
| page | string | 所属页面 |
| component_name | string | 组件名称 |
| is_unique | boolean | 是否唯一 |
| wait_timeout | integer | 等待超时(秒) |
| is_visible | boolean | 是否可见 |
| is_enabled | boolean | 是否启用 |
| force_action | boolean | 强制操作 |
| usage_count | integer | 使用次数 |
| last_validated | string | 最后验证时间 |
| validation_status |  | 验证状态 |
| validation_message | string | 验证消息 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| group | integer | 所属分组 |
| parent_element | integer | 父元素 |

### ElementEnhanced
增强的元素序列化器，包含新字段

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| project |  |  |
| group |  |  |
| locator_strategy |  |  |
| created_by |  |  |
| parent_element | string |  |
| children_elements | string |  |
| all_locators | string |  |
| usage_scripts | string |  |
| project_id | integer |  |
| group_id | integer |  |
| locator_strategy_id | integer |  |
| parent_element_id | integer |  |
| name | string | 元素名称 |
| description | string | 元素描述 |
| element_type |  | 元素类型 |
| locator_value | string | 定位表达式 |
| backup_locators |  | 备用定位器 |
| page | string | 所属页面 |
| component_name | string | 组件名称 |
| is_unique | boolean | 是否唯一 |
| wait_timeout | integer | 等待超时(秒) |
| is_visible | boolean | 是否可见 |
| is_enabled | boolean | 是否启用 |
| force_action | boolean | 强制操作 |
| usage_count | integer | 使用次数 |
| last_validated | string | 最后验证时间 |
| validation_status |  | 验证状态 |
| validation_message | string | 验证消息 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### ElementGroup
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| project |  |  |
| project_id | integer |  |
| elements_count | string |  |
| children | string |  |
| name | string | 分组名称 |
| description | string | 分组描述 |
| order | integer | 排序 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| parent_group | integer | 父分组 |

### ElementGroupCreate
| 字段名 | 类型 | 说明 |
|---|---|---|
| project | integer | 所属项目 |
| name | string | 分组名称 |
| description | string | 分组描述 |
| parent_group | integer | 父分组 |
| order | integer | 排序 |

### ElementType952Enum
* `INPUT` - 输入框
* `BUTTON` - 按钮
* `LINK` - 链接
* `DROPDOWN` - 下拉框
* `CHECKBOX` - 复选框
* `RADIO` - 单选框
* `TEXT` - 文本
* `IMAGE` - 图片
* `CONTAINER` - 容器
* `TABLE` - 表格
* `FORM` - 表单
* `MODAL` - 弹窗

### EngineEnum
* `playwright` - Playwright
* `selenium` - Selenium

### Environment
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 环境名称 |
| scope |  | 作用域 |
| project | integer |  |
| project_name | string |  |
| variables |  | 环境变量 |
| is_active | boolean | 是否激活 |
| created_by |  |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### EnvironmentEnum
* `CHROME` - Chrome
* `FIREFOX` - Firefox
* `SAFARI` - Safari
* `EDGE` - Edge
* `IE` - IE

### ExecutionModeEnum
* `text` - 文本模式

### ExecutionResultEnum
* `passed` - 通过
* `failed` - 失败
* `skipped` - 跳过

### ExecutionSourceEnum
* `manual` - 单用例执行
* `suite` - 套件执行
* `scheduled` - 定时任务执行

### FrameworkEnum
* `playwright` - Playwright
* `selenium` - Selenium

### GeneratedTestCase
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| case_id | string | 用例编号 |
| title | string | 用例标题 |
| priority |  | 优先级 |
| priority_display | string |  |
| precondition | string | 前置条件 |
| test_steps | string | 测试步骤 |
| expected_result | string | 预期结果 |
| status |  | 状态 |
| status_display | string |  |
| generated_by_ai | string | 生成AI模型 |
| reviewed_by_ai | string | 评审AI模型 |
| review_comments | string | 评审意见 |
| requirement | integer | 关联需求 |
| requirement_name | string |  |
| requirement_id_display | string |  |
| project_id | integer |  |
| project_name | string |  |
| source_task_id | string |  |
| save_status_summary | string |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### GeneratedTestCasePriorityEnum
* `P0` - 最高优先级
* `P1` - 高优先级
* `P2` - 中优先级
* `P3` - 低优先级

### GeneratedTestCaseStatusEnum
* `generated` - 已生成
* `reviewing` - 评审中
* `reviewed` - 已评审
* `approved` - 已批准
* `rejected` - 已拒绝
* `adopted` - 已采纳
* `discarded` - 已弃用

### GenerationConfig
生成行为配置序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 配置名称 |
| default_output_mode |  | 默认输出模式 |
| default_output_mode_display | string |  |
| enable_auto_review | boolean | 启用AI评审和改进 |
| review_timeout | integer | 评审和改进超时时间（秒） |
| is_active | boolean | 是否启用 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| source_summary | string |  |
| activation_summary | string |  |

### LanguageEnum
* `python` - Python
* `javascript` - JavaScript

### LocatorStrategy
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 策略名称 |
| description | string | 策略描述 |

### MessageTypeEnum
* `user` - 用户消息
* `assistant` - 助手回复

### MethodEnum
* `GET` - GET
* `POST` - POST
* `PUT` - PUT
* `DELETE` - DELETE
* `PATCH` - PATCH
* `HEAD` - HEAD
* `OPTIONS` - OPTIONS

### ModelTypeEnum
* `deepseek` - DeepSeek
* `qwen` - 通义千问
* `siliconflow` - 硅基流动
* `zhipu` - 智谱
* `other` - 其他

### NotificationLog
通知日志序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| task_name | string | 任务名称 |
| task_type_display | string |  |
| notification_type_display | string |  |
| sender_name | string | 发件人姓名 |
| recipient_names | string |  |
| notification_target_display | string |  |
| status_display | string |  |
| created_at | string | 创建时间 |
| sent_at | string | 发送时间 |
| retry_status | string |  |

### NotificationType609Enum
* `email` - 邮箱通知
* `webhook` - Webhook机器人
* `both` - 两者都发送

### NullEnum
### OperationLog
操作日志序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| operation_type |  | 操作类型 |
| operation_type_display | string |  |
| resource_type |  | 资源类型 |
| resource_type_display | string |  |
| resource_id | integer | 资源ID |
| resource_name | string | 资源名称 |
| description | string | 操作描述 |
| user | integer | 操作用户 |
| user_name | string |  |
| created_at | string | 创建时间 |

### OperationLogOperationTypeEnum
* `create` - 新增
* `edit` - 编辑
* `delete` - 删除
* `execute` - 执行
* `run` - 运行
* `save` - 保存

### OperationLogResourceTypeEnum
* `project` - 项目
* `collection` - 集合
* `request` - 请求
* `suite` - 测试套件
* `environment` - 环境
* `task` - 定时任务
* `execution` - 执行记录

### OperationRecord
操作记录序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| operation_type |  | 操作类型 |
| operation_type_display | string |  |
| resource_type |  | 资源类型 |
| resource_type_display | string |  |
| resource_id | integer | 资源ID |
| resource_name | string | 资源名称 |
| description | string | 操作描述 |
| user | integer | 操作用户 |
| user_name | string |  |
| created_at | string | 创建时间 |

### OperationRecordOperationTypeEnum
* `create` - 新增
* `edit` - 编辑
* `delete` - 删除
* `run` - 运行
* `rerun` - 重新运行
* `save` - 保存
* `rename` - 重命名

### OperationRecordResourceTypeEnum
* `project` - 项目
* `element` - 元素
* `test_case` - 测试用例
* `script` - 脚本
* `suite` - 套件
* `execution` - 执行记录
* `report` - 测试报告

### OutputModeEnum
* `stream` - 实时流式输出
* `complete` - 完整输出

### PageObject
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| project |  |  |
| created_by |  |  |
| elements_count | string |  |
| elements | string |  |
| project_id | integer |  |
| name | string | 页面对象名称 |
| class_name | string | 类名 |
| url_pattern | string | URL模式 |
| description | string | 描述 |
| template_code | string | 模板代码 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### PageObjectCreate
| 字段名 | 类型 | 说明 |
|---|---|---|
| project | integer | 所属项目 |
| name | string | 页面对象名称 |
| class_name | string | 类名 |
| url_pattern | string | URL模式 |
| description | string | 描述 |

### PaginatedAICaseList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedAIExecutionRecordList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedAIModelConfigList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedAIServiceConfigList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedAnalysisTaskList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedApiCollectionList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedApiProjectList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedApiRequestList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedAppComponentList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedAppComponentPackageList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedAppCustomComponentList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedAppDeviceList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedAppElementList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedAppNotificationLogList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedAppPackageList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedAppProjectList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedAppScheduledTaskList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedAppTestCaseList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedAppTestExecutionList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedAppTestSuiteList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedAssistantSessionList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedBusinessRequirementList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedDataFactoryRecordList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedDifyConfigList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedElementEnhancedList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedElementGroupList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedEnvironmentList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedGeneratedTestCaseList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedGenerationConfigList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedLocatorStrategyList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedNotificationLogList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedOperationLogList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedOperationRecordList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedPageObjectList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedProjectEnvironmentList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedProjectList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedPromptConfigList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedRequestHistoryList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedRequirementAnalysisList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedRequirementDocumentList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedReviewTemplateList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedScheduledTaskList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedScreenshotList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedScriptStepList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedTaskAutoReviewRecordList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedTaskExecutionLogList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedTaskNotificationSettingList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedTestCaseExecutionList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedTestCaseGenerationTaskList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedTestCaseList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedTestCaseListList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedTestCaseReviewCommentList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedTestCaseReviewList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedTestCaseStepList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedTestExecutionList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedTestPlanList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedTestRunCaseHistoryList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedTestRunCaseList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedTestRunList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedTestScriptList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedTestSuiteList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedTestSuiteRequestList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedUiNotificationLogList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedUiProjectList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedUiScheduledTaskList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedUnifiedNotificationConfigList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedUserList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PaginatedVersionList
| 字段名 | 类型 | 说明 |
|---|---|---|
| count | integer |  |
| next | string |  |
| previous | string |  |
| results | array |  |

### PatchedAICase
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| project |  |  |
| created_by |  |  |
| project_id | integer |  |
| name | string | 用例名称 |
| description | string | 描述 |
| task_description | string | 任务描述 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### PatchedAIExecutionRecord
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| project |  |  |
| project_id | integer |  |
| project_name | string |  |
| ai_case |  |  |
| ai_case_id | integer |  |
| ai_case_name | string |  |
| case_name | string | 用例名称快照 |
| task_description | string | 任务描述 |
| execution_mode |  | 执行模式 |
| status |  | 执行状态 |
| start_time | string | 开始时间 |
| end_time | string | 结束时间 |
| duration | number | 执行时长(秒) |
| logs | string | 执行日志 |
| steps_completed |  | 已完成步骤 |
| planned_tasks |  | 规划任务 |
| executed_by |  |  |
| executed_by_name | string |  |
| gif_path | string | GIF录制路径 |
| screenshots_sequence |  | 截图序列 |

### PatchedAIModelConfig
AI 模型配置序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 配置名称 |
| model_type |  | 模型类型 |
| model_type_display | string |  |
| role |  | 角色 |
| role_display | string |  |
| api_key | string |  |
| api_key_masked | string |  |
| base_url | string | API Base URL |
| model_name | string | 模型名称 |
| max_tokens | integer | 最大Token数 |
| temperature | number | 温度参数 |
| top_p | number | Top P参数 |
| is_active | boolean | 是否启用 |
| created_by | integer | 创建者 |
| created_by_name | string |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| usage_scope_summary | string |  |
| activation_summary | string |  |

### PatchedAIServiceConfig
AI服务配置序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 配置名称 |
| service_type |  | 服务类型 |
| service_type_display | string |  |
| role |  | 角色类型 |
| role_display | string |  |
| api_key | string |  |
| base_url | string | API Base URL |
| model_name | string | 模型名称 |
| max_tokens | integer | 最大Token数 |
| temperature | number | 温度参数 |
| is_active | boolean | 是否启用 |
| created_by | integer | 创建者 |
| created_by_name | string |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### PatchedApiCollection
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 集合名称 |
| description | string | 集合描述 |
| project | integer | 所属项目 |
| parent | integer | 父级集合 |
| order | integer | 排序 |
| children | string |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### PatchedApiProject
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 项目名称 |
| description | string | 项目描述 |
| project_type |  | 项目类型 |
| status |  | 项目状态 |
| owner |  |  |
| members | array |  |
| member_ids | array |  |
| start_date | string |  |
| end_date | string |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### PatchedApiRequest
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 请求名称 |
| description | string | 请求描述 |
| request_type |  | 请求类型 |
| method |  | 请求方法 |
| url | string | 请求URL |
| headers |  | 请求头 |
| params |  | URL参数 |
| body |  | 请求体 |
| auth |  | 认证信息 |
| pre_request_script | string | 请求前脚本 |
| post_request_script | string | 请求后脚本 |
| assertions |  | 断言规则 |
| collection | integer |  |
| order | integer | 排序 |
| created_by |  |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### PatchedAppComponent
UI组件定义序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 组件名称 |
| type | string | 组件类型 |
| category | string | 类别 |
| description | string | 描述 |
| schema |  | 配置Schema |
| default_config |  | 默认配置 |
| enabled | boolean | 是否启用 |
| sort_order | integer | 排序 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### PatchedAppComponentPackage
组件包序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| created_by_name | string |  |
| name | string | 包名称 |
| version | string | 版本 |
| description | string | 描述 |
| author | string | 作者 |
| source |  | 来源 |
| manifest |  | 包清单 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| created_by | integer | 创建人 |

### PatchedAppCustomComponent
自定义组件定义序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 组件名称 |
| type | string | 组件类型 |
| description | string | 描述 |
| schema |  | 参数Schema |
| default_config |  | 默认参数 |
| steps |  | 组合步骤 |
| enabled | boolean | 是否启用 |
| sort_order | integer | 排序 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### PatchedAppDevice
APP设备序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| locked_by_name | string |  |
| device_id | string | 设备序列号 |
| name | string | 设备名称 |
| status |  | 状态 |
| android_version | string | Android版本 |
| connection_type |  | 连接类型 |
| ip_address | string | IP地址 |
| port | integer | 端口 |
| locked_at | string | 锁定时间 |
| max_allocation_time | integer | 最大分配时间(秒) |
| device_specs |  | 设备规格 |
| description | string | 设备描述 |
| location | string | 设备位置 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| locked_by | integer | 锁定用户 |

### PatchedAppElement
APP元素序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| created_by_name | string |  |
| element_type_display | string |  |
| preview_url | string |  |
| name | string | 元素名称 |
| element_type |  | 元素类型 |
| tags |  | 标签 |
| config |  | 元素配置 |
| resolution_configs |  | 分辨率配置 |
| usage_count | integer | 使用次数 |
| last_used_at | string | 最后使用时间 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| is_active | boolean | 是否启用 |
| project | integer | 所属项目 |
| created_by | integer | 创建人 |

### PatchedAppPackage
APP应用包名序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| created_by_name | string |  |
| name | string | 应用名称 |
| package_name | string | 应用包名 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| created_by | integer | 创建人 |

### PatchedAppProjectUpdate
APP项目更新序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| name | string | 项目名称 |
| description | string | 项目描述 |
| status |  | 项目状态 |
| start_date | string | 开始日期 |
| end_date | string | 结束日期 |
| members | array | 团队成员 |

### PatchedAppScheduledTask
APP定时任务序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 任务名称 |
| description | string | 任务描述 |
| project | integer | 所属项目 |
| task_type |  | 任务类型 |
| task_type_display | string |  |
| trigger_type |  | 触发器类型 |
| trigger_type_display | string |  |
| cron_expression | string | Cron表达式 |
| interval_seconds | integer | 间隔秒数 |
| execute_at | string | 执行时间 |
| device | integer | 执行设备 |
| device_name | string |  |
| app_package | integer | 应用包名 |
| app_package_name | string |  |
| test_suite | integer | 测试套件 |
| test_suite_name | string |  |
| test_case | integer | 测试用例 |
| test_case_name | string |  |
| notify_on_success | boolean | 成功时通知 |
| notify_on_failure | boolean | 失败时通知 |
| notification_type |  | 通知类型 |
| notification_type_display | string |  |
| notify_emails |  | 通知邮箱列表 |
| status |  | 任务状态 |
| status_display | string |  |
| last_run_time | string | 最后运行时间 |
| next_run_time | string | 下次运行时间 |
| total_runs | integer | 总运行次数 |
| successful_runs | integer | 成功次数 |
| failed_runs | integer | 失败次数 |
| last_result |  | 最后执行结果 |
| error_message | string | 错误信息 |
| created_by | integer | 创建者 |
| created_by_name | string |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### PatchedAppTestCase
APP测试用例序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| created_by_name | string |  |
| app_package_name | string |  |
| name | string | 用例名称 |
| description | string | 用例描述 |
| ui_flow |  | UI流程定义 |
| variables |  | 变量定义 |
| timeout | integer | 超时时间(秒) |
| retry_count | integer | 失败重试次数 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| project | integer | 所属项目 |
| app_package | integer | 应用包名 |
| created_by | integer | 创建人 |

### PatchedAppTestExecution
APP测试执行记录序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| case_name | string |  |
| device_name | string |  |
| user_name | string |  |
| pass_rate | number |  |
| status_display | string |  |
| result_display | string |  |
| status |  | 执行状态 |
| result |  | 测试结果 |
| task_id | string | Celery任务ID |
| progress | integer | 执行进度(0-100) |
| started_at | string | 开始时间 |
| finished_at | string | 结束时间 |
| duration | number | 执行时长(秒) |
| report_path | string | Allure报告路径 |
| error_message | string | 错误信息 |
| total_steps | integer | 总步骤数 |
| passed_steps | integer | 通过步骤数 |
| failed_steps | integer | 失败步骤数 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| test_case | integer | 测试用例 |
| test_suite | integer | 所属套件 |
| device | integer | 执行设备 |
| user | integer | 执行用户 |

### PatchedAppTestSuiteUpdate
测试套件更新序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| name | string | 套件名称 |
| description | string | 套件描述 |
| project | integer | 所属项目 |

### PatchedAssistantSessionCreate
| 字段名 | 类型 | 说明 |
|---|---|---|
| session_id | string | 会话ID |
| title | string | 会话标题 |

### PatchedDataFactoryRecord
数据工厂记录序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| user | integer | 用户 |
| user_name | string |  |
| tool_name | string | 工具名称 |
| tool_name_display | string |  |
| tool_category |  | 工具分类 |
| tool_category_display | string |  |
| tool_scenario |  | 使用场景 |
| tool_scenario_display | string |  |
| input_data |  | 输入数据 |
| output_data |  | 输出数据 |
| is_saved | boolean | 是否保存 |
| tags |  | 标签 |
| created_at | string | 创建时间 |

### PatchedDifyConfig
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| api_url | string | Dify API endpoint URL |
| api_key | string | Dify API密钥 |
| is_active | boolean | 是否启用 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### PatchedElement
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| project |  |  |
| locator_strategy |  |  |
| created_by |  |  |
| project_id | integer |  |
| group_id | integer |  |
| locator_strategy_id | integer |  |
| name | string | 元素名称 |
| description | string | 元素描述 |
| element_type |  | 元素类型 |
| locator_value | string | 定位表达式 |
| backup_locators |  | 备用定位器 |
| page | string | 所属页面 |
| component_name | string | 组件名称 |
| is_unique | boolean | 是否唯一 |
| wait_timeout | integer | 等待超时(秒) |
| is_visible | boolean | 是否可见 |
| is_enabled | boolean | 是否启用 |
| force_action | boolean | 强制操作 |
| usage_count | integer | 使用次数 |
| last_validated | string | 最后验证时间 |
| validation_status |  | 验证状态 |
| validation_message | string | 验证消息 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| group | integer | 所属分组 |
| parent_element | integer | 父元素 |

### PatchedElementGroup
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| project |  |  |
| project_id | integer |  |
| elements_count | string |  |
| children | string |  |
| name | string | 分组名称 |
| description | string | 分组描述 |
| order | integer | 排序 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| parent_group | integer | 父分组 |

### PatchedEnvironment
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 环境名称 |
| scope |  | 作用域 |
| project | integer |  |
| project_name | string |  |
| variables |  | 环境变量 |
| is_active | boolean | 是否激活 |
| created_by |  |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### PatchedGeneratedTestCase
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| case_id | string | 用例编号 |
| title | string | 用例标题 |
| priority |  | 优先级 |
| priority_display | string |  |
| precondition | string | 前置条件 |
| test_steps | string | 测试步骤 |
| expected_result | string | 预期结果 |
| status |  | 状态 |
| status_display | string |  |
| generated_by_ai | string | 生成AI模型 |
| reviewed_by_ai | string | 评审AI模型 |
| review_comments | string | 评审意见 |
| requirement | integer | 关联需求 |
| requirement_name | string |  |
| requirement_id_display | string |  |
| project_id | integer |  |
| project_name | string |  |
| source_task_id | string |  |
| save_status_summary | string |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### PatchedGenerationConfig
生成行为配置序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 配置名称 |
| default_output_mode |  | 默认输出模式 |
| default_output_mode_display | string |  |
| enable_auto_review | boolean | 启用AI评审和改进 |
| review_timeout | integer | 评审和改进超时时间（秒） |
| is_active | boolean | 是否启用 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| source_summary | string |  |
| activation_summary | string |  |

### PatchedLocatorStrategy
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 策略名称 |
| description | string | 策略描述 |

### PatchedPageObject
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| project |  |  |
| created_by |  |  |
| elements_count | string |  |
| elements | string |  |
| project_id | integer |  |
| name | string | 页面对象名称 |
| class_name | string | 类名 |
| url_pattern | string | URL模式 |
| description | string | 描述 |
| template_code | string | 模板代码 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### PatchedProject
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 项目名称 |
| description | string | 项目描述 |
| status |  | 状态 |
| owner |  |  |
| members | array |  |
| environments | array |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| testcase_count | string |  |
| requirement_summary | string |  |
| ai_generation_summary | string |  |
| automation_summary | string |  |
| latest_task_summary | string |  |

### PatchedPromptConfig
提示词配置序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 配置名称 |
| prompt_type |  | 提示词类型 |
| prompt_type_display | string |  |
| content | string | 提示词内容 |
| is_active | boolean | 是否启用 |
| created_by | integer | 创建者 |
| created_by_name | string |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| usage_scope_summary | string |  |
| activation_summary | string |  |

### PatchedRequestHistory
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| request |  |  |
| environment |  |  |
| request_data |  | 请求数据 |
| response_data |  | 响应数据 |
| status_code | integer | 状态码 |
| response_time | number | 响应时间(ms) |
| error_message | string | 错误信息 |
| assertions_results |  | 断言结果 |
| executed_by |  |  |
| executed_at | string | 执行时间 |

### PatchedRequirementDocument
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| title | string | 文档标题 |
| file | string | 文档文件 |
| file_url | string |  |
| document_type |  | 文档类型 |
| document_type_display | string |  |
| status |  | 状态 |
| status_display | string |  |
| uploaded_by | integer | 上传者 |
| uploaded_by_name | string |  |
| project | integer | 关联项目 |
| project_name | string |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| file_size | integer | 文件大小(bytes) |
| extracted_text | string | 提取的文本内容 |

### PatchedReviewTemplateCreate
| 字段名 | 类型 | 说明 |
|---|---|---|
| name | string | 模板名称 |
| description | string | 模板描述 |
| project | array |  |
| checklist |  | 检查清单 |
| default_reviewers | array |  |

### PatchedScheduledTask
定时任务序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 任务名称 |
| description | string | 任务描述 |
| task_type |  | 任务类型 |
| trigger_type |  | 触发器类型 |
| cron_expression | string | Cron表达式 |
| interval_seconds | integer | 间隔秒数 |
| execute_at | string | 执行时间 |
| test_suite | integer | 测试套件 |
| test_suite_name | string |  |
| api_request | integer | API请求 |
| api_request_name | string |  |
| environment | integer | 执行环境 |
| environment_name | string |  |
| status |  | 任务状态 |
| last_run_time | string | 最后运行时间 |
| next_run_time | string | 下次运行时间 |
| total_runs | integer | 总运行次数 |
| successful_runs | integer | 成功运行次数 |
| failed_runs | integer | 失败运行次数 |
| last_result |  | 最后执行结果 |
| error_message | string | 错误信息 |
| notify_on_success | boolean | 成功时通知 |
| notify_on_failure | boolean | 失败时通知 |
| notify_emails |  | 通知邮箱列表 |
| notification_type | string |  |
| notification_type_display | string |  |
| notification_type_input | string |  |
| created_by |  |  |
| created_by_name | string |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### PatchedScreenshot
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| execution |  |  |
| execution_id | integer |  |
| name | string | 截图名称 |
| image | string | 截图文件 |
| description | string | 截图描述 |
| captured_at | string | 捕获时间 |

### PatchedScriptStep
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| script |  |  |
| target_element |  |  |
| page_object |  |  |
| script_id | integer |  |
| target_element_id | integer |  |
| page_object_id | integer |  |
| step_order | integer | 步骤顺序 |
| action_type |  | 操作类型 |
| action_params |  | 操作参数 |
| description | string | 步骤描述 |
| expected_result | string | 预期结果 |
| wait_before | integer | 执行前等待(毫秒) |
| wait_after | integer | 执行后等待(毫秒) |
| retry_count | integer | 重试次数 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### PatchedTaskNotificationSetting
定时任务通知设置序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| task | integer | 关联任务 |
| notification_type_display | string |  |
| notification_config_info | string |  |
| is_enabled | boolean | 是否启用通知 |
| notify_on_success | boolean | 成功时通知 |
| notify_on_failure | boolean | 失败时通知 |
| notify_on_timeout | boolean | 超时时通知 |
| notify_on_error | boolean | 错误时通知 |
| active_types | string |  |

### PatchedTestCase
测试用例序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 用例名称 |
| description | string | 用例描述 |
| project | integer | 所属项目 |
| project_name | string |  |
| status |  | 状态 |
| priority |  | 优先级 |
| created_by | integer | 创建人 |
| created_by_name | string |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| steps | array |  |

### PatchedTestCaseExecution
测试用例执行记录序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| test_case | integer | 测试用例 |
| test_case_name | string |  |
| project | integer | 项目 |
| project_name | string |  |
| test_suite | integer | 所属测试套件 |
| test_suite_name | string |  |
| execution_source |  | 执行来源 |
| status |  | 执行状态 |
| engine |  | 测试引擎 |
| browser | string | 浏览器 |
| headless | boolean | 无头模式 |
| execution_logs | string | 执行日志 |
| error_message | string | 错误信息 |
| screenshots |  | 截图列表 |
| execution_time | number | 执行时长(秒) |
| started_at | string | 开始时间 |
| finished_at | string | 完成时间 |
| created_by | integer | 执行人 |
| created_by_name | string |  |
| created_at | string | 创建时间 |

### PatchedTestCaseGenerationTask
测试用例生成任务序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| task_id | string | 任务ID |
| title | string | 任务标题 |
| requirement_text | string | 需求描述 |
| status |  | 状态 |
| status_display | string |  |
| progress | integer | 进度百分比 |
| output_mode |  | 输出模式 |
| stream_buffer | string | 流式输出缓冲区 |
| last_stream_update | string | 最后流式更新时间 |
| project | integer | 关联项目 |
| project_name | string |  |
| writer_model_config | integer | 编写模型配置 |
| writer_model_name | string |  |
| reviewer_model_config | integer | 评审模型配置 |
| reviewer_model_name | string |  |
| writer_prompt_config | integer | 编写提示词配置 |
| writer_prompt_name | string |  |
| reviewer_prompt_config | integer | 评审提示词配置 |
| reviewer_prompt_name | string |  |
| generated_test_cases | string | 生成的测试用例 |
| review_feedback | string | 评审反馈 |
| final_test_cases | string | 最终测试用例 |
| generation_log | string | 生成日志 |
| error_message | string | 错误信息 |
| created_by | integer | 创建者 |
| created_by_name | string |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| completed_at | string | 完成时间 |
| generation_config_summary | string |  |
| result_count | string |  |
| save_status_summary | string |  |
| processing_status_summary | string |  |
| generated_results_preview | string |  |
| source_summary | string |  |
| source_analysis_summary | string |  |
| model_source_summary | string |  |
| prompt_source_summary | string |  |
| failure_summary | string |  |
| downstream_summary | string |  |
| auto_review_summary | string |  |
| is_saved_to_records | boolean | 是否已保存到记录 |
| saved_at | string | 保存到记录时间 |

### PatchedTestCaseReviewCommentCreate
| 字段名 | 类型 | 说明 |
|---|---|---|
| review | integer | 评审 |
| testcase | integer | 相关用例 |
| comment_type |  | 意见类型 |
| content | string | 意见内容 |
| step_number | integer | 步骤序号 |

### PatchedTestCaseReviewCreate
| 字段名 | 类型 | 说明 |
|---|---|---|
| title | string | 评审标题 |
| description | string | 评审描述 |
| projects | array |  |
| priority |  | 优先级 |
| deadline | string | 截止日期 |
| testcases | array |  |
| reviewers | array |  |
| template | integer |  |

### PatchedTestCaseStep
测试用例步骤序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| step_number | integer | 步骤序号 |
| action_type |  | 操作类型 |
| element | integer | 目标元素 |
| element_name | string |  |
| element_locator | string |  |
| input_value | string | 输入值 |
| wait_time | integer | 等待时间(毫秒) |
| assert_type |  | 断言类型 |
| assert_value | string | 断言期望值 |
| description | string | 步骤描述 |
| created_at | string | 创建时间 |

### PatchedTestCaseUpdate
| 字段名 | 类型 | 说明 |
|---|---|---|
| title | string | 用例标题 |
| description | string | 用例描述 |
| preconditions | string | 前置条件 |
| steps | string | 操作步骤 |
| expected_result | string | 预期结果 |
| priority |  | 优先级 |
| test_type |  | 测试类型 |
| tags |  | 标签 |
| project_id | integer | 项目ID，可选 |
| version_ids | array | 关联版本ID列表 |

### PatchedTestExecution
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| project |  |  |
| test_suite |  |  |
| test_script |  |  |
| executed_by |  |  |
| project_id | integer |  |
| test_suite_id | integer |  |
| test_script_id | integer |  |
| executed_by_id | integer |  |
| test_suite_name | string |  |
| executed_by_name | string |  |
| pass_rate | string |  |
| environment |  | 执行环境 |
| status |  | 执行状态 |
| total_cases | integer | 总用例数 |
| passed_cases | integer | 通过用例数 |
| failed_cases | integer | 失败用例数 |
| skipped_cases | integer | 跳过用例数 |
| started_at | string | 开始时间 |
| finished_at | string | 结束时间 |
| duration | number | 执行时长(秒) |
| engine | string | 测试引擎 |
| browser | string | 浏览器 |
| headless | boolean | 无头模式 |
| result_data |  | 执行结果数据 |
| error_message | string | 错误信息 |
| report_url | string | 报告URL |
| created_at | string | 创建时间 |

### PatchedTestPlan
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 计划名称 |
| projects | array |  |
| version | string |  |
| creator |  |  |
| created_at | string | 创建时间 |
| is_active | boolean | 是否激活 |

### PatchedTestRun
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 执行名称 |
| status |  | 状态 |
| assignee | integer | 执行人 |
| progress | string |  |
| run_cases | array |  |

### PatchedTestRunCase
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| status |  | 执行状态 |
| priority |  | 优先级 |
| actual_result | string | 实际结果 |
| comments | string | 备注 |
| defects |  | 关联缺陷 |
| elapsed_time | string | 执行耗时 |
| executed_at | string | 执行时间 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| test_run | integer | 测试执行 |
| testcase | integer | 测试用例 |
| executed_by | integer | 执行者 |

### PatchedTestScriptUpdate
| 字段名 | 类型 | 说明 |
|---|---|---|
| name | string | 脚本名称 |
| description | string | 脚本描述 |
| script_type |  | 脚本类型 |
| content | string | 脚本内容 |

### PatchedTestSuite
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 套件名称 |
| description | string | 套件描述 |
| project | integer | 所属项目 |
| environment | integer | 执行环境 |
| suite_requests | array |  |
| created_by |  |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### PatchedTestSuiteRequest
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| request |  |  |
| order | integer | 执行顺序 |
| assertions |  | 断言规则 |
| enabled | boolean | 是否启用 |

### PatchedTestSuiteUpdate
| 字段名 | 类型 | 说明 |
|---|---|---|
| name | string | 套件名称 |
| description | string | 套件描述 |

### PatchedUiProjectUpdate
| 字段名 | 类型 | 说明 |
|---|---|---|
| name | string | 项目名称 |
| description | string | 项目描述 |
| status |  | 项目状态 |
| base_url | string | 基础URL |
| start_date | string | 开始日期 |
| end_date | string | 结束日期 |
| members | array | 团队成员 |

### PatchedUiScheduledTask
UI定时任务序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 任务名称 |
| description | string | 任务描述 |
| task_type |  | 任务类型 |
| task_type_display | string |  |
| trigger_type |  | 触发器类型 |
| trigger_type_display | string |  |
| cron_expression | string | Cron表达式 |
| interval_seconds | integer | 间隔秒数 |
| execute_at | string | 执行时间 |
| project | integer | 关联项目 |
| project_name | string |  |
| test_suite | integer | 测试套件 |
| test_suite_name | string |  |
| test_cases |  | 测试用例列表 |
| engine | string | 执行引擎 |
| browser | string | 浏览器类型 |
| headless | boolean | 无头模式 |
| notify_on_success | boolean | 成功时通知 |
| notify_on_failure | boolean | 失败时通知 |
| notification_type |  | 通知类型 |
| notification_type_display | string |  |
| notify_emails |  | 通知邮箱列表 |
| status |  | 任务状态 |
| status_display | string |  |
| last_run_time | string | 最后运行时间 |
| next_run_time | string | 下次运行时间 |
| total_runs | integer | 总运行次数 |
| successful_runs | integer | 成功运行次数 |
| failed_runs | integer | 失败运行次数 |
| last_result |  | 最后执行结果 |
| error_message | string | 错误信息 |
| created_by | integer | 创建者 |
| created_by_name | string |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### PatchedUnifiedNotificationConfig
统一通知配置序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 配置名称 |
| config_type |  | 配置类型 |
| webhook_bots |  | Webhook机器人配置 |
| is_default | boolean | 是否默认配置 |
| is_active | boolean | 是否启用 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| created_by | integer | 创建者 |
| webhook_bots_display | string |  |

### PatchedUser
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| username | string | 用户名 |
| email | string | 电子邮件地址 |
| first_name | string | 名字 |
| last_name | string | 姓氏 |
| avatar | string | 头像 |
| phone | string | 手机号 |
| department | string | 部门 |
| position | string | 职位 |
| is_active | boolean | 是否激活 |
| date_joined | string | 加入日期 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### PatchedVersion
版本序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 版本名称 |
| description | string | 版本描述 |
| is_baseline | boolean | 是否为基线版本 |
| projects | array |  |
| created_by |  |  |
| created_at | string | 创建时间 |
| testcases_count | string |  |

### Priority388Enum
* `high` - 高
* `medium` - 中
* `low` - 低

### Priority43cEnum
* `low` - 低
* `medium` - 中
* `high` - 高
* `urgent` - 紧急

### PriorityE6eEnum
* `low` - 低
* `medium` - 中
* `high` - 高
* `critical` - 紧急

### Project
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 项目名称 |
| description | string | 项目描述 |
| status |  | 状态 |
| owner |  |  |
| members | array |  |
| environments | array |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| testcase_count | string |  |
| requirement_summary | string |  |
| ai_generation_summary | string |  |
| automation_summary | string |  |
| latest_task_summary | string |  |

### ProjectCreate
| 字段名 | 类型 | 说明 |
|---|---|---|
| name | string | 项目名称 |
| description | string | 项目描述 |
| status |  | 状态 |

### ProjectEnvironment
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 环境名称 |
| base_url | string | 基础URL |
| description | string | 环境描述 |
| variables |  | 环境变量 |
| is_default | boolean | 是否默认 |
| created_at | string | 创建时间 |
| project | integer |  |

### ProjectMember
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| user |  |  |
| user_id | integer |  |
| role |  | 角色 |
| joined_at | string | 加入时间 |

### ProjectMemberRoleEnum
* `owner` - 负责人
* `admin` - 管理员
* `developer` - 开发者
* `tester` - 测试者
* `viewer` - 观察者

### ProjectSimple
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string |  |

### ProjectTypeEnum
* `HTTP` - HTTP
* `WEBSOCKET` - WebSocket

### PromptConfig
提示词配置序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 配置名称 |
| prompt_type |  | 提示词类型 |
| prompt_type_display | string |  |
| content | string | 提示词内容 |
| is_active | boolean | 是否启用 |
| created_by | integer | 创建者 |
| created_by_name | string |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| usage_scope_summary | string |  |
| activation_summary | string |  |

### PromptTypeEnum
* `writer` - 用例编写提示词
* `reviewer` - 用例评审提示词

### RequestHistory
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| request |  |  |
| environment |  |  |
| request_data |  | 请求数据 |
| response_data |  | 响应数据 |
| status_code | integer | 状态码 |
| response_time | number | 响应时间(ms) |
| error_message | string | 错误信息 |
| assertions_results |  | 断言结果 |
| executed_by |  |  |
| executed_at | string | 执行时间 |

### RequestTypeEnum
* `HTTP` - HTTP
* `WEBSOCKET` - WebSocket

### RequirementAnalysis
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| document_id | integer |  |
| document_title | string |  |
| analysis_report | string | 分析报告 |
| requirements_count | integer | 需求数量 |
| analysis_time | number | 分析耗时(秒) |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| requirements | array |  |
| project_id | integer |  |
| project_name | string |  |
| input_content_summary | string |  |
| analysis_status | string |  |
| last_analysis_at | string |  |
| config_source_summary | string |  |
| task_entry_summary | string |  |

### RequirementDocument
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| title | string | 文档标题 |
| file | string | 文档文件 |
| file_url | string |  |
| document_type |  | 文档类型 |
| document_type_display | string |  |
| status |  | 状态 |
| status_display | string |  |
| uploaded_by | integer | 上传者 |
| uploaded_by_name | string |  |
| project | integer | 关联项目 |
| project_name | string |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| file_size | integer | 文件大小(bytes) |
| extracted_text | string | 提取的文本内容 |

### RequirementDocumentStatusEnum
* `uploaded` - 已上传
* `analyzing` - 分析中
* `analyzed` - 分析完成
* `failed` - 分析失败

### RequirementLevelEnum
* `high` - 高
* `medium` - 中
* `low` - 低

### RequirementTypeEnum
* `functional` - 功能需求
* `performance` - 性能需求
* `security` - 安全需求
* `usability` - 可用性需求
* `interface` - 接口需求
* `other` - 其他需求

### ResultEnum
* `passed` - 通过
* `failed` - 失败
* `skipped` - 跳过

### ReviewAssignment
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| reviewer |  |  |
| status |  | 评审状态 |
| comment | string | 评审意见 |
| checklist_results |  | 检查清单结果 |
| reviewed_at | string | 评审时间 |
| assigned_at | string | 分配时间 |

### ReviewAssignmentStatusEnum
* `pending` - 待评审
* `approved` - 已通过
* `rejected` - 已拒绝
* `abstained` - 弃权

### ReviewStatusEnum
* `reviewing` - 评审中
* `completed` - 已完成
* `failed` - 失败
* `cancelled` - 已取消

### ReviewTemplate
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 模板名称 |
| description | string | 模板描述 |
| project | array |  |
| creator |  |  |
| checklist |  | 检查清单 |
| default_reviewers | array |  |
| is_active | boolean | 是否启用 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### ReviewTemplateCreate
| 字段名 | 类型 | 说明 |
|---|---|---|
| name | string | 模板名称 |
| description | string | 模板描述 |
| project | array |  |
| checklist |  | 检查清单 |
| default_reviewers | array |  |

### ScheduledTask
定时任务序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 任务名称 |
| description | string | 任务描述 |
| task_type |  | 任务类型 |
| trigger_type |  | 触发器类型 |
| cron_expression | string | Cron表达式 |
| interval_seconds | integer | 间隔秒数 |
| execute_at | string | 执行时间 |
| test_suite | integer | 测试套件 |
| test_suite_name | string |  |
| api_request | integer | API请求 |
| api_request_name | string |  |
| environment | integer | 执行环境 |
| environment_name | string |  |
| status |  | 任务状态 |
| last_run_time | string | 最后运行时间 |
| next_run_time | string | 下次运行时间 |
| total_runs | integer | 总运行次数 |
| successful_runs | integer | 成功运行次数 |
| failed_runs | integer | 失败运行次数 |
| last_result |  | 最后执行结果 |
| error_message | string | 错误信息 |
| notify_on_success | boolean | 成功时通知 |
| notify_on_failure | boolean | 失败时通知 |
| notify_emails |  | 通知邮箱列表 |
| notification_type | string |  |
| notification_type_display | string |  |
| notification_type_input | string |  |
| created_by |  |  |
| created_by_name | string |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### ScheduledTaskTaskTypeEnum
* `TEST_SUITE` - 测试套件执行
* `API_REQUEST` - API请求执行

### ScopeEnum
* `GLOBAL` - 全局环境变量
* `LOCAL` - 局部环境变量

### Screenshot
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| execution |  |  |
| execution_id | integer |  |
| name | string | 截图名称 |
| image | string | 截图文件 |
| description | string | 截图描述 |
| captured_at | string | 捕获时间 |

### ScriptStep
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| script |  |  |
| target_element |  |  |
| page_object |  |  |
| script_id | integer |  |
| target_element_id | integer |  |
| page_object_id | integer |  |
| step_order | integer | 步骤顺序 |
| action_type |  | 操作类型 |
| action_params |  | 操作参数 |
| description | string | 步骤描述 |
| expected_result | string | 预期结果 |
| wait_before | integer | 执行前等待(毫秒) |
| wait_after | integer | 执行后等待(毫秒) |
| retry_count | integer | 重试次数 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### ScriptStepActionTypeEnum
* `CLICK` - 点击
* `INPUT` - 输入
* `SELECT` - 选择
* `VERIFY` - 验证
* `WAIT` - 等待
* `HOVER` - 悬停
* `SCROLL` - 滚动
* `NAVIGATE` - 导航
* `SCREENSHOT` - 截图
* `SWITCH_TAB` - 切换标签页
* `CUSTOM` - 自定义

### ScriptTypeEnum
* `CODE` - 代码
* `LOW_CODE` - 低代码
* `NO_CODE` - 无代码

### ServiceTypeEnum
* `openai` - OpenAI
* `azure` - Azure OpenAI
* `anthropic` - Anthropic
* `deepseek` - DeepSeek
* `qwen` - 通义千问
* `siliconflow` - 硅基流动
* `other` - 其他

### SimpleProject
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string |  |
| description | string |  |

### SimpleTestCase
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| title | string |  |
| test_type | string |  |
| priority | string |  |
| status | string |  |
| author | SimpleUser |  |

### SimpleUser
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| username | string |  |
| email | string |  |
| first_name | string |  |
| last_name | string |  |

### SourceEnum
* `upload` - 上传
* `market` - 市场
* `local` - 本地

### Status3cfEnum
* `untested` - 未测试
* `passed` - 通过
* `failed` - 失败
* `blocked` - 阻塞
* `retest` - 重测

### Status654Enum
* `NOT_STARTED` - 未开始
* `IN_PROGRESS` - 进行中
* `COMPLETED` - 已结束

### Status66bEnum
* `ACTIVE` - 激活
* `PAUSED` - 暂停
* `COMPLETED` - 已完成
* `FAILED` - 失败

### Status89bEnum
* `draft` - 草稿
* `active` - 激活
* `deprecated` - 废弃

### StatusB10Enum
* `pending` - 待发送
* `sending` - 发送中
* `success` - 发送成功
* `failed` - 发送失败
* `cancelled` - 已取消

### StatusFfbEnum
* `active` - 进行中
* `paused` - 暂停
* `completed` - 已完成
* `archived` - 已归档

### TaskAutoReviewRecord
自动 AI 评审记录序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| task | integer | 关联生成任务 |
| task_id | string |  |
| task_title | string |  |
| project | integer | 关联项目 |
| project_name | string |  |
| review_source | string | 评审来源 |
| source_stage | string | 来源阶段 |
| review_status |  | 评审状态 |
| review_summary | string | 评审摘要 |
| review_content | string | 评审内容 |
| reviewer_model_name | string | 评审模型名称 |
| reviewer_prompt_name | string | 评审提示词名称 |
| result_identity_snapshot |  | 结果身份快照 |
| failure_message | string | 失败信息 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| completed_at | string | 完成时间 |

### TaskExecutionLog
任务执行日志序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| task | integer | 关联任务 |
| task_name | string |  |
| status |  | 执行状态 |
| start_time | string | 开始时间 |
| end_time | string | 结束时间 |
| result |  | 执行结果 |
| error_message | string | 错误信息 |
| executed_by | integer | 执行者 |
| executed_by_name | string |  |
| created_at | string | 创建时间 |

### TaskExecutionLogStatusEnum
* `PENDING` - 待执行
* `RUNNING` - 执行中
* `COMPLETED` - 已完成
* `FAILED` - 失败
* `CANCELLED` - 已取消

### TaskNotificationSetting
定时任务通知设置序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| task | integer | 关联任务 |
| notification_type_display | string |  |
| notification_config_info | string |  |
| is_enabled | boolean | 是否启用通知 |
| notify_on_success | boolean | 成功时通知 |
| notify_on_failure | boolean | 失败时通知 |
| notify_on_timeout | boolean | 超时时通知 |
| notify_on_error | boolean | 错误时通知 |
| active_types | string |  |

### TaskTypeE35Enum
* `TEST_SUITE` - 测试套件执行
* `TEST_CASE` - 测试用例执行

### TestCase
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| author |  |  |
| assignee |  |  |
| project |  |  |
| versions | array |  |
| step_details | array |  |
| attachments | array |  |
| comments | array |  |
| priority_display | string |  |
| status_display | string |  |
| test_type_display | string |  |
| source_summary | string |  |
| generation_source_summary | string |  |
| review_summary | string |  |
| automation_summary | string |  |
| title | string | 用例标题 |
| description | string | 用例描述 |
| preconditions | string | 前置条件 |
| steps | string | 操作步骤 |
| expected_result | string | 预期结果 |
| priority |  | 优先级 |
| status |  | 状态 |
| test_type |  | 测试类型 |
| tags |  | 标签 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### TestCaseAttachment
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| uploaded_by |  |  |
| name | string | 附件名称 |
| file | string | 文件 |
| uploaded_at | string | 上传时间 |
| testcase | integer |  |

### TestCaseComment
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| author |  |  |
| content | string | 评论内容 |
| created_at | string | 评论时间 |
| testcase | integer |  |

### TestCaseCreate
| 字段名 | 类型 | 说明 |
|---|---|---|
| title | string | 用例标题 |
| description | string | 用例描述 |
| preconditions | string | 前置条件 |
| steps | string | 操作步骤 |
| expected_result | string | 预期结果 |
| priority |  | 优先级 |
| test_type |  | 测试类型 |
| tags |  | 标签 |
| project_id | integer | 项目ID，可选 |
| version_ids | array | 关联版本ID列表 |

### TestCaseExecution
测试用例执行记录序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| test_case | integer | 测试用例 |
| test_case_name | string |  |
| project | integer | 项目 |
| project_name | string |  |
| test_suite | integer | 所属测试套件 |
| test_suite_name | string |  |
| execution_source |  | 执行来源 |
| status |  | 执行状态 |
| engine |  | 测试引擎 |
| browser | string | 浏览器 |
| headless | boolean | 无头模式 |
| execution_logs | string | 执行日志 |
| error_message | string | 错误信息 |
| screenshots |  | 截图列表 |
| execution_time | number | 执行时长(秒) |
| started_at | string | 开始时间 |
| finished_at | string | 完成时间 |
| created_by | integer | 执行人 |
| created_by_name | string |  |
| created_at | string | 创建时间 |

### TestCaseExecutionStatusEnum
* `pending` - 待执行
* `running` - 执行中
* `passed` - 通过
* `failed` - 失败
* `error` - 错误

### TestCaseGenerationTask
测试用例生成任务序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| task_id | string | 任务ID |
| title | string | 任务标题 |
| requirement_text | string | 需求描述 |
| status |  | 状态 |
| status_display | string |  |
| progress | integer | 进度百分比 |
| output_mode |  | 输出模式 |
| stream_buffer | string | 流式输出缓冲区 |
| last_stream_update | string | 最后流式更新时间 |
| project | integer | 关联项目 |
| project_name | string |  |
| writer_model_config | integer | 编写模型配置 |
| writer_model_name | string |  |
| reviewer_model_config | integer | 评审模型配置 |
| reviewer_model_name | string |  |
| writer_prompt_config | integer | 编写提示词配置 |
| writer_prompt_name | string |  |
| reviewer_prompt_config | integer | 评审提示词配置 |
| reviewer_prompt_name | string |  |
| generated_test_cases | string | 生成的测试用例 |
| review_feedback | string | 评审反馈 |
| final_test_cases | string | 最终测试用例 |
| generation_log | string | 生成日志 |
| error_message | string | 错误信息 |
| created_by | integer | 创建者 |
| created_by_name | string |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| completed_at | string | 完成时间 |
| generation_config_summary | string |  |
| result_count | string |  |
| save_status_summary | string |  |
| processing_status_summary | string |  |
| generated_results_preview | string |  |
| source_summary | string |  |
| source_analysis_summary | string |  |
| model_source_summary | string |  |
| prompt_source_summary | string |  |
| failure_summary | string |  |
| downstream_summary | string |  |
| auto_review_summary | string |  |
| is_saved_to_records | boolean | 是否已保存到记录 |
| saved_at | string | 保存到记录时间 |

### TestCaseGenerationTaskStatusEnum
* `pending` - 等待中
* `generating` - 生成中
* `reviewing` - 评审中
* `revising` - 改进中
* `completed` - 已完成
* `failed` - 失败
* `cancelled` - 已取消

### TestCaseList
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| title | string | 用例标题 |
| description | string | 用例描述 |
| preconditions | string | 前置条件 |
| steps | string | 操作步骤 |
| expected_result | string | 预期结果 |
| priority |  | 优先级 |
| priority_display | string |  |
| status |  | 状态 |
| status_display | string |  |
| test_type |  | 测试类型 |
| test_type_display | string |  |
| author | string |  |
| assignee | string |  |
| project | string |  |
| versions | string |  |
| tags |  | 标签 |
| source_summary | string |  |
| generation_source_summary | string |  |
| review_summary | string |  |
| automation_summary | string |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### TestCaseReview
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| title | string | 评审标题 |
| description | string | 评审描述 |
| projects | array |  |
| testcases | array |  |
| creator |  |  |
| template |  |  |
| status |  | 评审状态 |
| priority |  | 优先级 |
| deadline | string | 截止日期 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| completed_at | string | 完成时间 |
| assignments | array |  |
| comments | array |  |

### TestCaseReviewComment
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| testcase |  |  |
| author |  |  |
| comment_type |  | 意见类型 |
| content | string | 意见内容 |
| step_number | integer | 步骤序号 |
| is_resolved | boolean | 是否已解决 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### TestCaseReviewCommentCreate
| 字段名 | 类型 | 说明 |
|---|---|---|
| review | integer | 评审 |
| testcase | integer | 相关用例 |
| comment_type |  | 意见类型 |
| content | string | 意见内容 |
| step_number | integer | 步骤序号 |

### TestCaseReviewCreate
| 字段名 | 类型 | 说明 |
|---|---|---|
| title | string | 评审标题 |
| description | string | 评审描述 |
| projects | array |  |
| priority |  | 优先级 |
| deadline | string | 截止日期 |
| testcases | array |  |
| reviewers | array |  |
| template | integer |  |

### TestCaseReviewStatusEnum
* `pending` - 待评审
* `in_progress` - 评审中
* `approved` - 已通过
* `rejected` - 已拒绝
* `cancelled` - 已取消

### TestCaseStatusEnum
* `draft` - 草稿
* `ready` - 就绪
* `running` - 执行中
* `passed` - 通过
* `failed` - 失败

### TestCaseStep
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| step_number | integer | 步骤序号 |
| action | string | 操作 |
| expected | string | 预期结果 |
| testcase | integer |  |

### TestCaseStepActionTypeEnum
* `click` - 点击
* `fill` - 输入文本
* `getText` - 获取文本
* `waitFor` - 等待元素
* `hover` - 悬停
* `scroll` - 滚动
* `screenshot` - 截图
* `assert` - 断言
* `wait` - 等待
* `switchTab` - 切换标签页

### TestCaseUpdate
| 字段名 | 类型 | 说明 |
|---|---|---|
| title | string | 用例标题 |
| description | string | 用例描述 |
| preconditions | string | 前置条件 |
| steps | string | 操作步骤 |
| expected_result | string | 预期结果 |
| priority |  | 优先级 |
| test_type |  | 测试类型 |
| tags |  | 标签 |
| project_id | integer | 项目ID，可选 |
| version_ids | array | 关联版本ID列表 |

### TestExecution
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| test_suite |  |  |
| status |  | 执行状态 |
| start_time | string | 开始时间 |
| end_time | string | 结束时间 |
| total_requests | integer | 总请求数 |
| passed_requests | integer | 通过请求数 |
| failed_requests | integer | 失败请求数 |
| results |  | 执行结果 |
| executed_by |  |  |
| created_at | string | 创建时间 |

### TestExecutionCreate
| 字段名 | 类型 | 说明 |
|---|---|---|
| project | integer | 所属项目 |
| test_suite | integer | 测试套件 |
| test_script | integer | 测试脚本 |
| environment |  | 执行环境 |
| executed_by | integer | 执行人员 |

### TestExecutionStatusEnum
* `PENDING` - 待执行
* `RUNNING` - 运行中
* `SUCCESS` - 成功
* `FAILED` - 失败
* `ABORTED` - 中止

### TestPlan
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 计划名称 |
| projects | array |  |
| version | string |  |
| creator |  |  |
| created_at | string | 创建时间 |
| is_active | boolean | 是否激活 |

### TestPlanDetail
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| test_runs | array |  |
| creator |  |  |
| projects | array |  |
| version | string |  |
| name | string | 计划名称 |
| description | string | 计划描述 |
| is_active | boolean | 是否激活 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| assignees | array | 指派给 |

### TestRun
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 执行名称 |
| status |  | 状态 |
| assignee | integer | 执行人 |
| progress | string |  |
| run_cases | array |  |

### TestRunCase
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| status |  | 执行状态 |
| priority |  | 优先级 |
| actual_result | string | 实际结果 |
| comments | string | 备注 |
| defects |  | 关联缺陷 |
| elapsed_time | string | 执行耗时 |
| executed_at | string | 执行时间 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| test_run | integer | 测试执行 |
| testcase | integer | 测试用例 |
| executed_by | integer | 执行者 |

### TestRunCaseDetail
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| testcase | string |  |
| status |  | 执行状态 |
| priority |  | 优先级 |
| actual_result | string | 实际结果 |
| comments | string | 备注 |
| defects |  | 关联缺陷 |
| elapsed_time | string | 执行耗时 |
| executed_by |  |  |
| executed_at | string | 执行时间 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| history | array |  |

### TestRunCaseHistory
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| status |  | 执行状态 |
| actual_result | string | 实际结果 |
| comments | string | 备注 |
| executed_by |  |  |
| executed_at | string | 执行时间 |

### TestRunCaseSimple
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| testcase | string |  |
| status |  | 执行状态 |

### TestRunStatusEnum
* `untested` - 未测试
* `in_progress` - 进行中
* `completed` - 已完成
* `blocked` - 阻塞

### TestScript
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| project |  |  |
| project_id | integer |  |
| name | string | 脚本名称 |
| description | string | 脚本描述 |
| script_type |  | 脚本类型 |
| content | string | 脚本内容 |
| language |  | 脚本语言 |
| framework |  | 执行框架 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### TestScriptCreate
| 字段名 | 类型 | 说明 |
|---|---|---|
| project | integer | 所属项目 |
| name | string | 脚本名称 |
| description | string | 脚本描述 |
| script_type |  | 脚本类型 |
| content | string | 脚本内容 |
| language |  | 脚本语言 |
| framework |  | 执行框架 |

### TestScriptUpdate
| 字段名 | 类型 | 说明 |
|---|---|---|
| name | string | 脚本名称 |
| description | string | 脚本描述 |
| script_type |  | 脚本类型 |
| content | string | 脚本内容 |

### TestSuite
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 套件名称 |
| description | string | 套件描述 |
| project | integer | 所属项目 |
| environment | integer | 执行环境 |
| suite_requests | array |  |
| created_by |  |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### TestSuiteCreate
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| project | integer | 所属项目 |
| name | string | 套件名称 |
| description | string | 套件描述 |

### TestSuiteRequest
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| request |  |  |
| order | integer | 执行顺序 |
| assertions |  | 断言规则 |
| enabled | boolean | 是否启用 |

### TestSuiteScript
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| test_script |  |  |
| test_script_id | integer |  |
| order | integer | 执行顺序 |

### TestSuiteUpdate
| 字段名 | 类型 | 说明 |
|---|---|---|
| name | string | 套件名称 |
| description | string | 套件描述 |

### TestSuiteWithScripts
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| project |  |  |
| suite_scripts | array |  |
| name | string | 套件名称 |
| description | string | 套件描述 |
| execution_status |  | 执行状态 |
| passed_count | integer | 通过数 |
| failed_count | integer | 失败数 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| scripts | array | 测试脚本 |
| test_cases | array | 测试用例 |

### TestSuiteWithScriptsExecutionStatusEnum
* `not_run` - 未执行
* `passed` - 通过
* `failed` - 失败
* `running` - 执行中

### TestTypeEnum
* `functional` - 功能测试
* `integration` - 集成测试
* `api` - API测试
* `ui` - UI测试
* `performance` - 性能测试
* `security` - 安全测试

### TokenRefresh
| 字段名 | 类型 | 说明 |
|---|---|---|
| access | string |  |
| refresh | string |  |

### ToolCategoryEnum
* `test_data` - 测试数据
* `json` - JSON工具
* `string` - 字符工具
* `encoding` - 编码工具
* `random` - 随机工具
* `encryption` - 加密工具
* `crontab` - Crontab工具

### ToolScenarioEnum
* `test_data` - 测试数据
* `json` - JSON工具
* `string` - 字符工具
* `encoding` - 编码工具
* `random` - 随机工具
* `encryption` - 加密工具
* `crontab` - Crontab工具

### TriggerTypeEnum
* `CRON` - Cron表达式
* `INTERVAL` - 固定间隔
* `ONCE` - 单次执行

### UiNotificationLog
UI通知日志序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| task | integer | 关联任务 |
| task_name | string | 任务名称 |
| notification_type |  | 通知类型 |
| notification_type_display | string |  |
| actual_notification_type_display | string |  |
| task_type_display | string |  |
| sender_name | string | 发件人姓名 |
| sender_email | string | 发件人邮箱 |
| recipient_names | string |  |
| webhook_bot_info |  | Webhook机器人信息 |
| notification_content | string | 通知内容 |
| status |  | 发送状态 |
| status_display | string |  |
| error_message | string | 错误信息 |
| response_info |  | 响应信息 |
| created_at | string | 创建时间 |
| sent_at | string | 发送时间 |
| retry_count | integer | 重试次数 |
| retry_status | string |  |

### UiNotificationLogNotificationTypeEnum
* `task_execution` - 定时任务执行
* `test_suite_execution` - 测试套件执行
* `test_case_execution` - 测试用例执行
* `system_alert` - 系统警告
* `manual` - 手动通知

### UiProject
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| owner |  |  |
| members | array |  |
| name | string | 项目名称 |
| description | string | 项目描述 |
| status |  | 项目状态 |
| base_url | string | 基础URL |
| start_date | string | 开始日期 |
| end_date | string | 结束日期 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### UiProjectCreate
| 字段名 | 类型 | 说明 |
|---|---|---|
| name | string | 项目名称 |
| description | string | 项目描述 |
| status |  | 项目状态 |
| base_url | string | 基础URL |
| start_date | string | 开始日期 |
| end_date | string | 结束日期 |
| owner | integer | 负责人 |
| members | array | 团队成员 |

### UiProjectUpdate
| 字段名 | 类型 | 说明 |
|---|---|---|
| name | string | 项目名称 |
| description | string | 项目描述 |
| status |  | 项目状态 |
| base_url | string | 基础URL |
| start_date | string | 开始日期 |
| end_date | string | 结束日期 |
| members | array | 团队成员 |

### UiScheduledTask
UI定时任务序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 任务名称 |
| description | string | 任务描述 |
| task_type |  | 任务类型 |
| task_type_display | string |  |
| trigger_type |  | 触发器类型 |
| trigger_type_display | string |  |
| cron_expression | string | Cron表达式 |
| interval_seconds | integer | 间隔秒数 |
| execute_at | string | 执行时间 |
| project | integer | 关联项目 |
| project_name | string |  |
| test_suite | integer | 测试套件 |
| test_suite_name | string |  |
| test_cases |  | 测试用例列表 |
| engine | string | 执行引擎 |
| browser | string | 浏览器类型 |
| headless | boolean | 无头模式 |
| notify_on_success | boolean | 成功时通知 |
| notify_on_failure | boolean | 失败时通知 |
| notification_type |  | 通知类型 |
| notification_type_display | string |  |
| notify_emails |  | 通知邮箱列表 |
| status |  | 任务状态 |
| status_display | string |  |
| last_run_time | string | 最后运行时间 |
| next_run_time | string | 下次运行时间 |
| total_runs | integer | 总运行次数 |
| successful_runs | integer | 成功运行次数 |
| failed_runs | integer | 失败运行次数 |
| last_result |  | 最后执行结果 |
| error_message | string | 错误信息 |
| created_by | integer | 创建者 |
| created_by_name | string |  |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |

### UnifiedNotificationConfig
统一通知配置序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 配置名称 |
| config_type |  | 配置类型 |
| webhook_bots |  | Webhook机器人配置 |
| is_default | boolean | 是否默认配置 |
| is_active | boolean | 是否启用 |
| created_at | string | 创建时间 |
| updated_at | string | 更新时间 |
| created_by | integer | 创建者 |
| webhook_bots_display | string |  |

### User
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| username | string | 用户名 |
| email | string | 电子邮件地址 |
| first_name | string | 名字 |
| last_name | string | 姓氏 |

### UserCreate
| 字段名 | 类型 | 说明 |
|---|---|---|
| username | string | 用户名 |
| email | string | 电子邮件地址 |
| password | string |  |
| password_confirm | string |  |
| first_name | string | 名字 |
| last_name | string | 姓氏 |
| phone | string | 手机号 |
| department | string | 部门 |
| position | string | 职位 |

### UserSimple
| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| username | string | 用户名 |
| email | string | 电子邮件地址 |
| avatar | string | 头像 |

### ValidationStatusEnum
* `VALID` - 有效
* `INVALID` - 无效
* `UNKNOWN` - 未知
* `PENDING` - 待验证

### Version
版本序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 版本名称 |
| description | string | 版本描述 |
| is_baseline | boolean | 是否为基线版本 |
| projects | array |  |
| created_by |  |  |
| created_at | string | 创建时间 |
| testcases_count | string |  |

### VersionCreate
版本创建序列化器

| 字段名 | 类型 | 说明 |
|---|---|---|
| name | string | 版本名称 |
| description | string | 版本描述 |
| is_baseline | boolean | 是否为基线版本 |
| project_ids | array |  |

### VersionSimple
版本简单序列化器，用于在测试用例中显示

| 字段名 | 类型 | 说明 |
|---|---|---|
| id | integer |  |
| name | string | 版本名称 |
| is_baseline | boolean | 是否为基线版本 |

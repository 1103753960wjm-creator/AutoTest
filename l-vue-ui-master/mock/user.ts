// 用户登录
const koiLogin = { tokenValue: "ADMIN-TOKEN" };

export default [
  // 用户登录接口
  {
    url: "/mock/user/login", //请求地址
    method: "post", //请求方式
    response: ({ body }) => {
      // 获取请求体携带过来的用户名与密码
      const { username, password, securityCode } = body;
      if (username == "koi" && password == "123456" && securityCode == "1234") {
        return { status: 200, msg: "登录成功", data: koiLogin };
      } else {
        return { code: 500, msg: "登录失败" };
      }
    }
  }
];

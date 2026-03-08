# 待修改：数据库配置
Mysql_Host = "localhost"
Mysql_Port = "3306"
Mysql_Database = "fastapi"
Mysql_username = "xxx"
Mysql_password = "xxx"
Mysql_url = f"mysql+mysqlconnector://{Mysql_username}:{Mysql_password}@{Mysql_Host}:{Mysql_Port}/{Mysql_Database}"


# 迁移命令：aerich migrate
# 更新命令：aerich upgrade
# 字段的注释不会更新，只会更新字段

TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",  # MySQL or Mariadb
            "credentials": {
                "host": Mysql_Host,
                "port": Mysql_Port,
                "user": Mysql_username,
                "password": Mysql_password,
                "database": Mysql_Database,
                "minsize": 3,
                "maxsize": 15,
                "charset": "utf8mb4",
                "echo": False,  # 生产环境关闭
                "pool_recycle": 3600,  # 1小时回收
                "connect_timeout": 30,
                "init_command": "SELECT 1",
            },
        },
    },
    "apps": {
        "models": {
            "models": [
                "aerich.models",
                "views.user.user_model",
                "views.common.upload_model",
                "views.app.app_model",
                "views.web.web_model",
                "views.task.task_model",
                "views.api.api_model",
                "views.warning_call.call_model",
                "views.exe_update.exe_update_model",
                "views.app_mitmproxy.mitmproxy_model",
            ],
            "default_connection": "default",
        }
    },
    "use_tz": False,
    "timezone": "Asia/Shanghai",
}

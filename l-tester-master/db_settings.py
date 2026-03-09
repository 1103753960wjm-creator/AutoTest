import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR / ".env.local")


def _get_str(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None:
        return default
    value = value.strip()
    return value or default


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    try:
        return int(value)
    except ValueError:
        return default


Mysql_Host = _get_str("LT_DB_HOST", "localhost")
Mysql_Port = _get_int("LT_DB_PORT", 3306)
Mysql_Database = _get_str("LT_DB_NAME", "fastapi")
Mysql_username = _get_str("LT_DB_USER", "xxx")
Mysql_password = _get_str("LT_DB_PASSWORD", "xxx")
Mysql_url = (
    f"mysql+mysqlconnector://{Mysql_username}:{Mysql_password}"
    f"@{Mysql_Host}:{Mysql_Port}/{Mysql_Database}"
)


TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": Mysql_Host,
                "port": Mysql_Port,
                "user": Mysql_username,
                "password": Mysql_password,
                "database": Mysql_Database,
                "minsize": 3,
                "maxsize": 15,
                "charset": "utf8mb4",
                "echo": False,
                "pool_recycle": 3600,
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
                "views.requirement.requirement_model",
                "views.testcase.testcase_model",
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

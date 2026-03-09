import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
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


ip = _get_str("LT_SERVER_IP", "10.12.2.78")
port = _get_int("LT_SERVER_PORT", 8895)

# 报告链接和媒体资源 URL 生成使用的公开地址。
source_ip = _get_str("LT_SOURCE_IP", f"http://{ip}:{port}")
report_ip = _get_str("LT_REPORT_IP", f"http://{ip}:5730")

system_drive = _get_str("LT_SYSTEM_DRIVE", "F:")
project_path = _get_str("LT_PROJECT_PATH", f"{system_drive}/project/L-Tester")

device = _get_str("LT_DEVICE_URL", f"http://{ip}:8000")

playwright_result_path = _get_str(
    "LT_PLAYWRIGHT_RESULT_PATH", f"{project_path}/media/playwright"
)
api_result_path = _get_str("LT_API_RESULT_PATH", f"{project_path}/media/api")
mitmproxy_file = _get_str(
    "LT_MITMPROXY_FILE_PATH", f"{project_path}/media/mitmproxy_file"
)
mitmproxy_config_path = _get_str(
    "LT_MITMPROXY_CONFIG_PATH",
    f"{project_path}/views/app_mitmproxy/mitmproxy_config.py",
)
mitmproxy_yaml_path = _get_str(
    "LT_MITMPROXY_YAML_PATH",
    f"{project_path}/views/app_mitmproxy/mitmproxy_config_file.yaml",
)

_VALID_AI_MODES = {"none", "local_llm", "remote_llm"}
ai_mode_raw = _get_str("LT_AI_MODE", "none").lower()
ai_mode = ai_mode_raw if ai_mode_raw in _VALID_AI_MODES else "none"
ai_local_base_url = _get_str("LT_AI_LOCAL_BASE_URL", "http://127.0.0.1:11434/v1")
ai_local_model = _get_str("LT_AI_LOCAL_MODEL", "qwen2.5:7b")
ai_remote_base_url = _get_str("LT_AI_REMOTE_BASE_URL", "")
ai_remote_model = _get_str("LT_AI_REMOTE_MODEL", "")
ai_api_key = _get_str("LT_AI_API_KEY", "")

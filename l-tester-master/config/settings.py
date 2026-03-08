# 待修改：ip:port 修改为实际地址：端口
ip = "10.12.2.78"
port = 8895

# 提供媒体资源用的ip地址
source_ip = f"http://{ip}:{port}"

# 测试报告专用地址
report_ip = f"http://{ip}:5730"

# 系统盘
system_drive = "F:"

# 系统根目录
project_path = f"{system_drive}/project/L-Tester"

# 云真机地址
device = f"http://{ip}:8000"

# playwright 结果保存路径
playwright_result_path = f"{project_path}/media/playwright"

# api 结果保存路径
api_result_path = f"{project_path}/media/api"

# mitmproxy 配置文件保存路径
mitmproxy_file = f"{project_path}/media/mitmproxy_file"

# mitmproxy 接口流量出来文件
mitmproxy_config_path = f"{project_path}/views/app_mitmproxy/mitmproxy_config.py"

# mitmproxy yaml配置文件
mitmproxy_yaml_path = f"{project_path}/views/app_mitmproxy/mitmproxy_config_file.yaml"

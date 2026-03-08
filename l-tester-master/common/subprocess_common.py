import subprocess


# 异步subprocess运行shell命令
async def async_run_subprocess(command: str):
    try:
        output = subprocess.check_output(command, shell=True, encoding="utf-8").strip()
        return output
    except subprocess.CalledProcessError as e:
        print(f"执行失败: {e}")
        return str(e)


def sync_run_subprocess(command: str):
    try:
        subprocess.check_output(command, shell=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"sync_run_subprocess函数执行失败: {e}")
        return str(e)

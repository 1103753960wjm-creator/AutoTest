import json
import os
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path

import pytest
import requests
from playwright.sync_api import sync_playwright


BACKEND_DIR = Path(__file__).resolve().parents[1]
WORKSPACE_DIR = BACKEND_DIR.parent
FRONTEND_DIR = WORKSPACE_DIR / "l-vue-ui-master"

FRONTEND_URL = os.getenv("LT_SMOKE_FRONTEND_URL", "http://127.0.0.1:5730")
BACKEND_URL = os.getenv("LT_SMOKE_BACKEND_URL", "http://127.0.0.1:8895")
SMOKE_BROWSER_CHANNEL = os.getenv("LT_SMOKE_BROWSER_CHANNEL", "msedge").strip()
SMOKE_ARTIFACT_ROOT = Path(
    os.getenv(
        "LT_SMOKE_ARTIFACT_DIR",
        str(BACKEND_DIR / "tests_artifacts" / "browser_smoke"),
    )
)
RUN_BROWSER_SMOKE = os.getenv("LT_RUN_BROWSER_SMOKE") == "1"


def _wait_http_ok(url: str, timeout: int = 120) -> None:
    deadline = time.time() + timeout
    last_error = None
    while time.time() < deadline:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return
            last_error = RuntimeError(f"{url} 返回状态码 {response.status_code}")
        except Exception as exc:  # noqa: BLE001
            last_error = exc
        time.sleep(1)
    raise AssertionError(f"等待地址可用失败：{url}；最后错误：{last_error}")


def _run_migration_upgrade() -> None:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        ["aerich", "upgrade"],
        cwd=BACKEND_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        env=env,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            "执行数据库迁移失败：\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


def _ensure_server(url: str, command: list[str], cwd: Path, label: str):
    try:
        _wait_http_ok(url, timeout=5)
        return None
    except AssertionError:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        _wait_http_ok(url, timeout=120)
        return process


def _terminate_process(process) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()


def _build_user_state() -> dict[str, str]:
    login_payload = {
        "username": os.getenv("LT_SMOKE_USERNAME", "admin"),
        "password": os.getenv("LT_SMOKE_PASSWORD", "e10adc3949ba59abbe56e057f20f883e"),
    }
    response = requests.post(
        f"{BACKEND_URL}/api/user/login",
        json=login_payload,
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    if data.get("code") != 200:
        raise AssertionError(f"登录接口失败：{data}")
    return {
        "token": data["data"]["token"],
        "user_id": str(data["data"]["user_id"]),
        "avatar": data["data"].get("avatar", ""),
        "username": data["data"].get("username", "admin"),
    }


def _create_run_artifact_dir() -> Path:
    SMOKE_ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    base_name = time.strftime("%Y%m%d-%H%M%S")
    run_dir = SMOKE_ARTIFACT_ROOT / base_name
    index = 1
    while run_dir.exists():
        run_dir = SMOKE_ARTIFACT_ROOT / f"{base_name}-{index}"
        index += 1
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def _write_json(path: Path, payload: dict | list) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _dump_failure_artifacts(
    run_dir: Path,
    page,
    current_step: str,
    console_logs: list[dict],
    page_errors: list[str],
    request_failures: list[dict],
) -> None:
    failure_dir = run_dir / "failure"
    failure_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "step": current_step,
        "url": page.url if page is not None else "",
        "traceback": traceback.format_exc(),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    _write_json(failure_dir / "meta.json", meta)
    _write_json(failure_dir / "console.json", console_logs)
    _write_json(failure_dir / "page_errors.json", page_errors)
    _write_json(failure_dir / "request_failures.json", request_failures)

    if page is None or page.is_closed():
        return

    try:
        page.screenshot(path=str(failure_dir / "failure.png"), full_page=True)
    except Exception:  # noqa: BLE001
        pass

    try:
        (failure_dir / "page.html").write_text(page.content(), encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass


class _FakePage:
    def __init__(self, url: str) -> None:
        self.url = url

    def is_closed(self) -> bool:
        return False

    def screenshot(self, path: str, full_page: bool) -> None:
        Path(path).write_bytes(b"fake-image")

    def content(self) -> str:
        return "<html><body>failure</body></html>"


def test_dump_failure_artifacts_should_write_expected_files(tmp_path: Path):
    page = _FakePage("http://127.0.0.1:5730/testcase_generate")
    console_logs = [{"type": "error", "text": "控制台错误", "location": {"url": "http://example"}}]
    page_errors = ["页面异常"]
    request_failures = [{"url": "http://127.0.0.1:8895/api/testcase/list_page", "method": "POST", "failure": "net"}]

    try:
        raise AssertionError("模拟烟测失败")
    except AssertionError:
        _dump_failure_artifacts(
            tmp_path,
            page,
            "校验失败产物落盘",
            console_logs,
            page_errors,
            request_failures,
        )

    failure_dir = tmp_path / "failure"
    assert failure_dir.exists()
    assert (failure_dir / "failure.png").exists()
    assert (failure_dir / "page.html").exists()

    meta = json.loads((failure_dir / "meta.json").read_text(encoding="utf-8"))
    assert meta["step"] == "校验失败产物落盘"
    assert meta["url"] == page.url
    assert "模拟烟测失败" in meta["traceback"]

    saved_console_logs = json.loads((failure_dir / "console.json").read_text(encoding="utf-8"))
    saved_page_errors = json.loads((failure_dir / "page_errors.json").read_text(encoding="utf-8"))
    saved_request_failures = json.loads((failure_dir / "request_failures.json").read_text(encoding="utf-8"))
    assert saved_console_logs == console_logs
    assert saved_page_errors == page_errors
    assert saved_request_failures == request_failures


@pytest.mark.skipif(not RUN_BROWSER_SMOKE, reason="未设置 LT_RUN_BROWSER_SMOKE=1，跳过浏览器烟测")
def test_m2_browser_smoke_flow():
    """
    覆盖 M2 第二刀最小主链：
    生成草稿 -> 审核入库 -> 需求资产详情 -> 测试用例审核状态更新。
    """

    _run_migration_upgrade()

    frontend_command = [
        "npm.cmd" if os.name == "nt" else "npm",
        "run",
        "dev",
        "--",
        "--host",
        "127.0.0.1",
        "--port",
        "5730",
        "--strictPort",
    ]
    backend_command = [sys.executable, "main.py"]

    frontend_process = _ensure_server(
        f"{FRONTEND_URL}/login",
        frontend_command,
        FRONTEND_DIR,
        "前端服务",
    )
    backend_process = _ensure_server(
        f"{BACKEND_URL}/docs",
        backend_command,
        BACKEND_DIR,
        "后端服务",
    )

    unique_title = f"m2-browser-smoke-{int(time.time())}"
    unique_content = "Login should validate required fields and redirect to dashboard after success."
    run_artifact_dir = _create_run_artifact_dir()
    current_step = "初始化联调环境"
    console_logs: list[dict] = []
    page_errors: list[str] = []
    request_failures: list[dict] = []
    page = None
    browser = None
    success = False

    try:
        current_step = "建立真实登录态"
        user_state = _build_user_state()

        with sync_playwright() as playwright:
            browser_launch_kwargs = {"headless": True}
            if SMOKE_BROWSER_CHANNEL:
                browser_launch_kwargs["channel"] = SMOKE_BROWSER_CHANNEL
            browser = playwright.chromium.launch(**browser_launch_kwargs)
            context = browser.new_context(viewport={"width": 1440, "height": 1000})
            context.add_init_script(
                script=f"window.localStorage.setItem('user', JSON.stringify({json.dumps(user_state)}));"
            )
            page = context.new_page()
            page.on(
                "console",
                lambda message: console_logs.append(
                    {
                        "type": message.type,
                        "text": message.text,
                        "location": message.location,
                    }
                ),
            )
            page.on("pageerror", lambda error: page_errors.append(str(error)))
            page.on(
                "requestfailed",
                lambda request: request_failures.append(
                    {
                        "url": request.url,
                        "method": request.method,
                        "failure": request.failure,
                    }
                ),
            )

            current_step = "进入用例生成页"
            page.goto(f"{FRONTEND_URL}/testcase_generate", wait_until="networkidle")
            page.locator(".testcase-generate-page .el-form input").first.fill(unique_title)
            page.locator(".testcase-generate-page .el-form textarea").fill(unique_content)

            current_step = "生成测试用例草稿"
            with page.expect_response(
                lambda resp: "/api/ai/generate_testcases" in resp.url and resp.request.method == "POST",
                timeout=30000,
            ) as generate_info:
                page.locator(".testcase-generate-page .el-form .el-button--primary").click()
            generate_response = generate_info.value.json()
            assert generate_response.get("code") == 200, generate_response

            current_step = "标记审核并执行快捷入库"
            page.locator(".vxe-body--row").first.click()
            page.locator(".side-actions .el-button--success").click()

            with page.expect_response(
                lambda resp: "/api/requirement/save_reviewed_cases" in resp.url and resp.request.method == "POST",
                timeout=30000,
            ) as save_info:
                page.keyboard.press("Control+S")
            save_response = save_info.value.json()
            assert save_response.get("code") == 200, save_response
            assert save_response["data"].get("testcase_count", 0) >= 1, save_response

            current_step = "校验需求资产页"
            page.goto(f"{FRONTEND_URL}/requirement_assets", wait_until="networkidle")
            page.locator(".requirement-assets-page .search-form input").first.fill(unique_title)

            with page.expect_response(
                lambda resp: "/api/requirement/list_page" in resp.url and resp.request.method == "POST",
                timeout=30000,
            ) as requirement_info:
                page.locator(".requirement-assets-page .search-form .el-button--primary").click()
            requirement_response = requirement_info.value.json()
            assert requirement_response.get("code") == 200, requirement_response
            page.get_by_text(unique_title, exact=False).wait_for(timeout=10000)

            with page.expect_response(
                lambda resp: "/api/testcase/list_by_requirement" in resp.url and resp.request.method == "POST",
                timeout=30000,
            ) as detail_info:
                page.locator(".requirement-assets-page .asset-table .el-button").first.click()
            detail_response = detail_info.value.json()
            assert detail_response.get("code") == 200, detail_response
            assert detail_response["data"]["testcases"], detail_response
            assert detail_response["data"]["testcases"][0]["module"] == unique_title, detail_response

            current_step = "校验测试用例资产页并更新审核状态"
            page.goto(f"{FRONTEND_URL}/testcase_assets", wait_until="networkidle")
            page.locator(".testcase-assets-page .search-form input").first.fill(unique_title)

            with page.expect_response(
                lambda resp: "/api/testcase/list_page" in resp.url and resp.request.method == "POST",
                timeout=30000,
            ) as testcase_info:
                page.locator(".testcase-assets-page .search-form .el-button--primary").click()
            testcase_response = testcase_info.value.json()
            assert testcase_response.get("code") == 200, testcase_response
            assert testcase_response["data"]["content"], testcase_response

            page.locator(".testcase-assets-page .status-cell .el-select .el-select__wrapper").first.click()
            page.keyboard.press("ArrowDown")
            page.keyboard.press("Enter")

            with page.expect_response(
                lambda resp: "/api/testcase/update_review_status" in resp.url and resp.request.method == "POST",
                timeout=30000,
            ) as status_info:
                page.locator(".testcase-assets-page .status-cell .el-button").first.click()
            status_response = status_info.value.json()
            assert status_response.get("code") == 200, status_response
            assert status_response["data"]["review_status"] == "rejected", status_response

            success = True
    finally:
        if not success:
            _dump_failure_artifacts(
                run_artifact_dir,
                page,
                current_step,
                console_logs,
                page_errors,
                request_failures,
            )
        elif run_artifact_dir.exists():
            shutil.rmtree(run_artifact_dir, ignore_errors=True)

        if browser is not None:
            try:
                browser.close()
            except Exception:  # noqa: BLE001
                pass
        _terminate_process(backend_process)
        _terminate_process(frontend_process)

import sys
from pathlib import Path

from dotenv import dotenv_values


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from config import settings  # noqa: E402
from views.ai.ai_service import AIGatewayService  # noqa: E402


def test_none_mode_generates_structured_cases():
    service = AIGatewayService(
        config={
            "configured_mode_raw": "none",
            "configured_mode": "none",
            "local": {"base_url": "", "model": "", "api_key": ""},
            "remote": {"base_url": "", "model": "", "api_key": ""},
        }
    )

    result = service.generate_test_cases(
        {
            "title": "Login",
            "content": "User enters account and password. The system signs in successfully. Empty password must be blocked.",
            "source_type": "feature_design",
            "target_type": "web",
        }
    )

    assert result["effective_mode"] == "none"
    assert result["generation_source"] == "rules"
    assert len(result["cases"]) >= 3
    assert {"happy_path", "required_field_validation", "negative_path"} <= {
        case["category"] for case in result["cases"]
    }
    for case in result["cases"]:
        assert case["title"]
        assert case["module"] == "Login"
        assert case["steps"]
        assert case["expected_results"]


def test_invalid_or_unconfigured_mode_falls_back_to_none():
    service = AIGatewayService(
        config={
            "configured_mode_raw": "local_llm",
            "configured_mode": "local_llm",
            "local": {"base_url": "", "model": "", "api_key": ""},
            "remote": {"base_url": "", "model": "", "api_key": ""},
        }
    )

    result = service.get_mode_info()

    assert result["configured_mode"] == "local_llm"
    assert result["effective_mode"] == "none"
    assert result["used_fallback"] is True
    assert result["provider"]["mode"] == "none"


def test_none_mode_generates_structured_automation_draft():
    service = AIGatewayService(
        config={
            "configured_mode_raw": "none",
            "configured_mode": "none",
            "local": {"base_url": "", "model": "", "api_key": ""},
            "remote": {"base_url": "", "model": "", "api_key": ""},
        }
    )

    result = service.generate_automation_draft(
        {
            "title": "登录主流程",
            "module": "认证模块",
            "priority": "P1",
            "category": "happy_path",
            "target_type": "web",
            "preconditions": ["已准备账号"],
            "steps": ["打开登录页", "输入账号密码", "点击登录"],
            "expected_results": ["登录成功并进入首页"],
        }
    )

    assert result["effective_mode"] == "none"
    assert result["generation_source"] == "rules"
    assert result["draft_payload"]["menu_name"] == "[AI草稿][WEB]登录主流程"
    assert result["draft_payload"]["script"]
    assert result["warnings"]


def test_config_info_masks_remote_api_key():
    service = AIGatewayService(
        config={
            "configured_mode_raw": "remote_llm",
            "configured_mode": "remote_llm",
            "local": {"base_url": "http://127.0.0.1:11434/v1", "model": "qwen2.5:7b", "api_key": ""},
            "remote": {
                "base_url": "https://example.com/v1",
                "model": "deepseek-chat",
                "api_key": "secret-token",
            },
        }
    )

    result = service.get_config_info()

    assert result["configured_mode"] == "remote_llm"
    assert result["remote"]["api_key"] == ""
    assert result["remote"]["has_api_key"] is True


def test_save_config_updates_runtime_and_persists(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "BASE_DIR", tmp_path)
    monkeypatch.setattr(settings, "ai_mode_raw", "none")
    monkeypatch.setattr(settings, "ai_mode", "none")
    monkeypatch.setattr(settings, "ai_local_base_url", "http://127.0.0.1:11434/v1")
    monkeypatch.setattr(settings, "ai_local_model", "qwen2.5:7b")
    monkeypatch.setattr(settings, "ai_remote_base_url", "")
    monkeypatch.setattr(settings, "ai_remote_model", "")
    monkeypatch.setattr(settings, "ai_api_key", "old-secret")

    service = AIGatewayService()
    result = service.save_config(
        {
            "configured_mode": "local_llm",
            "local": {
                "base_url": "http://127.0.0.1:1234/v1",
                "model": "qwen-local",
            },
            "remote": {
                "base_url": "https://example.com/v1",
                "model": "remote-model",
            },
        }
    )

    env_values = dotenv_values(tmp_path / ".env.local")

    assert result["configured_mode"] == "local_llm"
    assert result["effective_mode"] == "local_llm"
    assert result["remote"]["api_key"] == ""
    assert result["remote"]["has_api_key"] is True
    assert settings.ai_mode == "local_llm"
    assert settings.ai_local_base_url == "http://127.0.0.1:1234/v1"
    assert settings.ai_local_model == "qwen-local"
    assert settings.ai_remote_base_url == "https://example.com/v1"
    assert settings.ai_remote_model == "remote-model"
    assert settings.ai_api_key == "old-secret"
    assert env_values["LT_AI_MODE"] == "local_llm"
    assert env_values["LT_AI_LOCAL_BASE_URL"] == "http://127.0.0.1:1234/v1"
    assert env_values["LT_AI_LOCAL_MODEL"] == "qwen-local"
    assert env_values["LT_AI_REMOTE_BASE_URL"] == "https://example.com/v1"
    assert env_values["LT_AI_REMOTE_MODEL"] == "remote-model"
    assert env_values["LT_AI_API_KEY"] == "old-secret"

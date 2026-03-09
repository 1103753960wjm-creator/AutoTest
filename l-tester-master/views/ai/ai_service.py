import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib import error, request

from dotenv import set_key

from config import settings


VALID_AI_MODES = {"none", "local_llm", "remote_llm"}
AI_ENV_KEY_MAP = {
    "configured_mode": "LT_AI_MODE",
    "local_base_url": "LT_AI_LOCAL_BASE_URL",
    "local_model": "LT_AI_LOCAL_MODEL",
    "remote_base_url": "LT_AI_REMOTE_BASE_URL",
    "remote_model": "LT_AI_REMOTE_MODEL",
    "remote_api_key": "LT_AI_API_KEY",
}


def build_ai_config(*, mask_secret: bool = False) -> Dict[str, Any]:
    remote_api_key = settings.ai_api_key
    return {
        "configured_mode_raw": settings.ai_mode_raw,
        "configured_mode": settings.ai_mode,
        "local": {
            "base_url": settings.ai_local_base_url,
            "model": settings.ai_local_model,
            "api_key": "",
        },
        "remote": {
            "base_url": settings.ai_remote_base_url,
            "model": settings.ai_remote_model,
            "api_key": "" if mask_secret else remote_api_key,
            "has_api_key": bool(remote_api_key),
        },
    }


def sanitize_ai_config(config: Dict[str, Any]) -> Dict[str, Any]:
    sanitized = {
        "configured_mode_raw": config.get("configured_mode_raw", "none"),
        "configured_mode": config.get("configured_mode", "none"),
        "local": {
            "base_url": config.get("local", {}).get("base_url", ""),
            "model": config.get("local", {}).get("model", ""),
            "api_key": "",
        },
        "remote": {
            "base_url": config.get("remote", {}).get("base_url", ""),
            "model": config.get("remote", {}).get("model", ""),
            "api_key": "",
            "has_api_key": bool(config.get("remote", {}).get("api_key")),
        },
    }
    return sanitized


def normalize_mode(mode: Optional[str], *, fallback_to_none: bool) -> str:
    raw_mode = (mode or "").strip().lower()
    if raw_mode in VALID_AI_MODES:
        return raw_mode
    if fallback_to_none:
        return "none"
    raise ValueError(f"不支持的 AI 模式：{mode}")


def normalize_generation_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    title = str(payload.get("title") or "").strip()
    content = str(payload.get("content") or "").strip()
    if not title:
        raise ValueError("标题不能为空")
    if not content:
        raise ValueError("需求内容不能为空")
    return {
        "title": title,
        "content": content,
        "source_type": str(payload.get("source_type") or "feature_design").strip(),
        "target_type": str(payload.get("target_type") or "general").strip(),
        "mode": str(payload.get("mode") or "").strip().lower(),
    }


def _normalize_nested_text(
    payload: Dict[str, Any], section_name: str, field_name: str, default: str
) -> str:
    section = payload.get(section_name)
    if not isinstance(section, dict):
        return default
    if field_name not in section:
        return default
    return str(section.get(field_name) or "").strip()


def normalize_config_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    current = build_ai_config()
    requested_mode = payload.get("configured_mode", payload.get("mode"))
    normalized_mode = normalize_mode(
        str(requested_mode or current["configured_mode"]).strip().lower(),
        fallback_to_none=False,
    )
    remote_api_key = current["remote"].get("api_key", "")
    incoming_remote_api_key = _normalize_nested_text(
        payload, "remote", "api_key", remote_api_key
    )
    if incoming_remote_api_key:
        remote_api_key = incoming_remote_api_key
    return {
        "configured_mode_raw": normalized_mode,
        "configured_mode": normalized_mode,
        "local": {
            "base_url": _normalize_nested_text(
                payload, "local", "base_url", current["local"]["base_url"]
            ),
            "model": _normalize_nested_text(
                payload, "local", "model", current["local"]["model"]
            ),
            "api_key": "",
        },
        "remote": {
            "base_url": _normalize_nested_text(
                payload, "remote", "base_url", current["remote"]["base_url"]
            ),
            "model": _normalize_nested_text(
                payload, "remote", "model", current["remote"]["model"]
            ),
            "api_key": remote_api_key,
            "has_api_key": bool(remote_api_key),
        },
    }


def get_ai_env_local_path() -> Path:
    return Path(settings.BASE_DIR) / ".env.local"


def apply_runtime_ai_config(config: Dict[str, Any]) -> None:
    settings.ai_mode_raw = config["configured_mode_raw"]
    settings.ai_mode = config["configured_mode"]
    settings.ai_local_base_url = config["local"]["base_url"]
    settings.ai_local_model = config["local"]["model"]
    settings.ai_remote_base_url = config["remote"]["base_url"]
    settings.ai_remote_model = config["remote"]["model"]
    settings.ai_api_key = config["remote"]["api_key"]

    os.environ[AI_ENV_KEY_MAP["configured_mode"]] = settings.ai_mode
    os.environ[AI_ENV_KEY_MAP["local_base_url"]] = settings.ai_local_base_url
    os.environ[AI_ENV_KEY_MAP["local_model"]] = settings.ai_local_model
    os.environ[AI_ENV_KEY_MAP["remote_base_url"]] = settings.ai_remote_base_url
    os.environ[AI_ENV_KEY_MAP["remote_model"]] = settings.ai_remote_model
    os.environ[AI_ENV_KEY_MAP["remote_api_key"]] = settings.ai_api_key


def persist_ai_config(config: Dict[str, Any]) -> Path:
    env_path = get_ai_env_local_path()
    env_path.parent.mkdir(parents=True, exist_ok=True)
    if not env_path.exists():
        env_path.touch()

    set_key(
        str(env_path),
        AI_ENV_KEY_MAP["configured_mode"],
        config["configured_mode"],
        quote_mode="never",
    )
    set_key(
        str(env_path),
        AI_ENV_KEY_MAP["local_base_url"],
        config["local"]["base_url"],
        quote_mode="never",
    )
    set_key(
        str(env_path),
        AI_ENV_KEY_MAP["local_model"],
        config["local"]["model"],
        quote_mode="never",
    )
    set_key(
        str(env_path),
        AI_ENV_KEY_MAP["remote_base_url"],
        config["remote"]["base_url"],
        quote_mode="never",
    )
    set_key(
        str(env_path),
        AI_ENV_KEY_MAP["remote_model"],
        config["remote"]["model"],
        quote_mode="never",
    )
    set_key(
        str(env_path),
        AI_ENV_KEY_MAP["remote_api_key"],
        config["remote"]["api_key"],
        quote_mode="never",
    )
    return env_path


class BaseAIProvider:
    provider_name = "base"

    def __init__(self, mode: str, config: Dict[str, Any]):
        self.mode = mode
        self.config = config

    def is_configured(self) -> bool:
        return True

    def describe(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "provider_name": self.provider_name,
            "configured": self.is_configured(),
        }

    def generate_test_cases(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError


class NoneProvider(BaseAIProvider):
    provider_name = "template_rules"

    def generate_test_cases(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        title = payload["title"]
        content = payload["content"]
        summary = self._build_summary(title, content)
        return {
            "generation_source": "rules",
            "summary": summary,
            "cases": self._build_cases(title, summary, payload["target_type"]),
        }

    def _build_summary(self, title: str, content: str) -> List[str]:
        fragments = re.split(r"[\r\n]+|[.;；。]", content)
        summary = [item.strip(" -\t") for item in fragments if item.strip(" -\t")]
        if not summary:
            return [title]
        return summary[:4]

    def _build_cases(
        self, title: str, summary: List[str], target_type: str
    ) -> List[Dict[str, Any]]:
        focus = summary[0]
        detail = summary[1] if len(summary) > 1 else focus
        return [
            {
                "case_id": "NONE-001",
                "title": f"{title} 主流程验证",
                "module": title,
                "priority": "P1",
                "category": "happy_path",
                "target_type": target_type,
                "automatable": True,
                "preconditions": ["已准备好执行该流程所需的前置数据"],
                "steps": [
                    f"进入{title}对应的功能流程",
                    f"按照正常操作完成与“{focus}”相关的主流程",
                    f"提交后观察系统对“{detail}”的处理结果",
                ],
                "expected_results": [
                    "主流程执行成功",
                    "关键状态变更已落库并可见",
                ],
            },
            {
                "case_id": "NONE-002",
                "title": f"{title} 必填项校验",
                "module": title,
                "priority": "P1",
                "category": "required_field_validation",
                "target_type": target_type,
                "automatable": True,
                "preconditions": ["目标功能页面可正常进入"],
                "steps": [
                    f"进入{title}对应的功能流程",
                    "保留一个必填项为空",
                    "继续执行提交或下一步操作",
                ],
                "expected_results": [
                    "系统阻止继续提交",
                    "页面给出明确的必填提示",
                ],
            },
            {
                "case_id": "NONE-003",
                "title": f"{title} 非法数据处理",
                "module": title,
                "priority": "P1",
                "category": "negative_path",
                "target_type": target_type,
                "automatable": True,
                "preconditions": ["目标功能页面可正常进入"],
                "steps": [
                    f"进入{title}对应的功能流程",
                    f"围绕“{focus}”输入非法数据或冲突数据",
                    "提交请求",
                ],
                "expected_results": [
                    "系统安全拒绝非法输入",
                    "不会产生错误状态或脏数据",
                ],
            },
            {
                "case_id": "NONE-004",
                "title": f"{title} 权限与可见性校验",
                "module": title,
                "priority": "P2",
                "category": "permission_or_visibility",
                "target_type": target_type,
                "automatable": False,
                "preconditions": ["已准备低权限账号或异常角色账号"],
                "steps": [
                    f"使用受限权限账号进入{title}功能流程",
                    "尝试执行同样的核心操作",
                ],
                "expected_results": [
                    "无权限操作保持隐藏或禁用",
                    "越权执行会被阻止并给出明确提示",
                ],
            },
        ]


class OpenAICompatibleProvider(BaseAIProvider):
    provider_name = "openai_compatible"

    def is_configured(self) -> bool:
        return bool(self.config.get("base_url")) and bool(self.config.get("model"))

    def generate_test_cases(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.is_configured():
            raise ValueError(f"{self.mode} 模式缺少必要配置")

        message = self._request_chat_completion(payload)
        cases = self._parse_cases(message)
        return {
            "generation_source": "llm",
            "summary": [payload["title"]],
            "cases": cases,
        }

    def _request_chat_completion(self, payload: Dict[str, Any]) -> str:
        prompt = self._build_prompt(payload)
        body = json.dumps(
            {
                "model": self.config["model"],
                "temperature": 0.2,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "仅返回合法 JSON。"
                            "最外层对象必须包含 `cases` 字段。"
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            }
        ).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.config.get("api_key"):
            headers["Authorization"] = f"Bearer {self.config['api_key']}"

        endpoint = f"{self.config['base_url'].rstrip('/')}/chat/completions"
        req = request.Request(endpoint, data=body, headers=headers, method="POST")

        try:
            with request.urlopen(req, timeout=60) as response:
                raw = response.read().decode("utf-8")
        except error.URLError as exc:
            raise ValueError(f"{self.mode} 模式请求失败：{exc}") from exc

        parsed = json.loads(raw)
        return parsed["choices"][0]["message"]["content"]

    def _build_prompt(self, payload: Dict[str, Any]) -> str:
        return (
            "请根据以下功能描述生成结构化测试用例草稿。\n"
            f"来源类型：{payload['source_type']}\n"
            f"目标类型：{payload['target_type']}\n"
            f"标题：{payload['title']}\n"
            f"内容：\n{payload['content']}\n\n"
            "请只返回如下结构的 JSON：\n"
            "{\n"
            '  "cases": [\n'
            "    {\n"
            '      "case_id": "LLM-001",\n'
            '      "title": "string",\n'
            '      "module": "string",\n'
            '      "priority": "P1|P2|P3",\n'
            '      "category": "string",\n'
            '      "target_type": "string",\n'
            '      "automatable": true,\n'
            '      "preconditions": ["string"],\n'
            '      "steps": ["string"],\n'
            '      "expected_results": ["string"]\n'
            "    }\n"
            "  ]\n"
            "}"
        )

    def _parse_cases(self, message: str) -> List[Dict[str, Any]]:
        cleaned = self._strip_code_fence(message)
        parsed = json.loads(cleaned)
        cases = parsed.get("cases")
        if not isinstance(cases, list) or not cases:
            raise ValueError(f"{self.mode} 模式返回的用例列表为空")
        normalized_cases = []
        for item in cases:
            if not isinstance(item, dict):
                continue
            normalized_cases.append(
                {
                    **item,
                    "module": str(item.get("module") or item.get("title") or "").strip(),
                }
            )
        if not normalized_cases:
            raise ValueError(f"{self.mode} 模式返回的用例列表为空")
        return normalized_cases

    def _strip_code_fence(self, message: str) -> str:
        cleaned = message.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z0-9_+-]*\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)
        return cleaned.strip()


class LocalLLMProvider(OpenAICompatibleProvider):
    provider_name = "local_openai_compatible"


class RemoteLLMProvider(OpenAICompatibleProvider):
    provider_name = "remote_openai_compatible"


class AIGatewayService:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or build_ai_config()

    def get_config_info(self) -> Dict[str, Any]:
        provider, info = self._resolve_provider()
        result = sanitize_ai_config(self.config)
        result.update(info)
        result["provider"] = provider.describe()
        result["providers"] = self._describe_all_providers()
        return result

    def get_mode_info(self, mode_override: Optional[str] = None) -> Dict[str, Any]:
        provider, info = self._resolve_provider(mode_override)
        info["provider"] = provider.describe()
        info["providers"] = self._describe_all_providers()
        return info

    def save_config(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        config = normalize_config_request(payload)
        persist_ai_config(config)
        apply_runtime_ai_config(config)
        self.config = build_ai_config()
        return self.get_config_info()

    def generate_test_cases(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        request_payload = normalize_generation_request(payload)
        provider, info = self._resolve_provider(request_payload.get("mode") or None)
        result = provider.generate_test_cases(request_payload)
        result.update(info)
        result["provider"] = provider.describe()
        return result

    def _describe_all_providers(self) -> List[Dict[str, Any]]:
        return [
            NoneProvider("none", {}).describe(),
            LocalLLMProvider("local_llm", self.config["local"]).describe(),
            RemoteLLMProvider("remote_llm", self.config["remote"]).describe(),
        ]

    def _resolve_provider(
        self, mode_override: Optional[str] = None
    ) -> Tuple[BaseAIProvider, Dict[str, Any]]:
        configured_mode_raw = self.config.get("configured_mode_raw", "none")
        configured_mode = normalize_mode(
            self.config.get("configured_mode"), fallback_to_none=True
        )
        if mode_override:
            effective_mode = normalize_mode(mode_override, fallback_to_none=False)
            provider = self._build_provider(effective_mode)
            if not provider.is_configured():
                raise ValueError(f"{effective_mode} 模式缺少必要配置")
            return provider, {
                "configured_mode_raw": configured_mode_raw,
                "configured_mode": configured_mode,
                "effective_mode": effective_mode,
                "used_fallback": False,
            }

        effective_mode = configured_mode
        provider = self._build_provider(effective_mode)
        used_fallback = configured_mode_raw != configured_mode
        if not provider.is_configured():
            effective_mode = "none"
            provider = self._build_provider(effective_mode)
            used_fallback = True

        return provider, {
            "configured_mode_raw": configured_mode_raw,
            "configured_mode": configured_mode,
            "effective_mode": effective_mode,
            "used_fallback": used_fallback,
        }

    def _build_provider(self, mode: str) -> BaseAIProvider:
        if mode == "none":
            return NoneProvider("none", {})
        if mode == "local_llm":
            return LocalLLMProvider("local_llm", self.config["local"])
        if mode == "remote_llm":
            return RemoteLLMProvider("remote_llm", self.config["remote"])
        raise ValueError(f"不支持的 AI 模式：{mode}")

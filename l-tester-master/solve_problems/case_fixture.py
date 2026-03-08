import json
from typing import Any, Dict

from loguru import logger
from playwright.sync_api import Page
from autowing.core.ai_fixture_base import AiFixtureBase
from autowing.core.llm.factory import LLMFactory


class CaseAiFixture(AiFixtureBase):
    """
    A fixture class that combines Playwright with AI capabilities for web automation.
    Provides AI-driven interaction with web pages using various LLM providers.
    """

    def __init__(self):
        """
        Initialize the AI-powered Playwright fixture.

        Args:
            page (Page): The Playwright page object to automate
        """
        super().__init__()
        self.llm_client = LLMFactory.create()
    async def ai_blackbox_cases(self, prompt: str, language: str = "Chinese") -> str:
        """
        面向黑盒测试场景
    
    Args:
        prompt (str): 测试需求描述（示例："验证登录功能"）
        language (str): 输出语言（默认中文）

    Returns:
        str: 结构化测试用例（JSON/Markdown/文本格式）

    Raises:
        ValueError: 当无法解析AI响应时抛出
        """
        logger.info(f"🤖 AI 生成测试用例，文案是: {prompt}")

        # 解析格式提示
        format_hint = ""
        if prompt.startswith(('json[]', 'markdown[]')):
            format_hint = prompt.split(',')[0].strip()
            prompt = ','.join(prompt.split(',')[1:]).strip()
        input_data = json.dumps(["1.用户名：正确的用户名-admin","2.密码：正确的密码-123456"])

        # 构造黑盒测试专用提示词
        test_scenarios = [
            "正常流测试（有效输入）", 
            "边界值测试", 
            "异常流测试（无效输入）",
            "安全性测试",
        ]

        # 根据不同格式构造提示模板
        if format_hint == 'json[]':
            template = f"""{{
    "id": "1",
    "name": "密码长度错误提示",
    "type": "异常流测试",
    "input":{input_data},
    "step": ["1. 输入超长密码: 12345678978979879","2. 点击登录"],
    "expected": "显示密码长度错误提示"
}}"""
            case_prompt = f"""
作为资深测试工程师，请基于以下测试需求生成黑盒测试用例, 尽可能的丰富一点。要求：

测试对象：{prompt}
type：{test_scenarios}
语言要求：{language}

返回 Python 列表（仅返回python的list格式）：
[{template}, ...]
"""
        elif format_hint == 'markdown[]':
            template = f"""{{
    "id": "1",
    "name": "密码长度错误提示",
    "type": "异常流测试",
    "input":{input_data},
    "step": ["1. 输入超长密码: 12345678978979879","2. 点击登录"],
    "expected": "显示密码长度错误提示"
}}"""
            case_prompt = f"""
生成Markdown格式的黑盒测试用例表格，包含：

测试需求：{prompt}
必要列：用例ID｜type｜测试步骤｜预期结果

返回 Python 列表（仅返回python的list格式）：
[{template}, ...]

语言要求：{language}
"""
        else:
            template = f"""{{
    "id": "1",
    "name": "密码长度错误提示",
    "type": "异常流测试",
    "input":{input_data},
    "step": ["1. 输入超长密码: 12345678978979879","2. 点击登录"],
    "expected": "显示密码长度错误提示"
}}"""
            case_prompt = f"""
请基于以下测试需求生成黑盒测试用例, 尽可能的丰富一点：

需求描述：{prompt}
测试重点：
- 输入验证
- 边界条件
- 异常处理
- 安全要求

返回 Python 列表（仅返回python的list格式）：
[{template}, ...]
...
使用语言：{language}
"""

        try:
            response = self.llm_client.complete(case_prompt)
            cleaned = self._clean_response(response)
        
            case = {"case": json.loads(cleaned)}  # 验证JSON格式
        
            return case
        except Exception as e:
            err_msg = f"AI 生成失败: {str(e)}\n响应片段: {cleaned[:100]}" if 'cleaned' in locals() else str(e)
            raise ValueError(err_msg)

    async def ai_api_cases(self, prompt: Dict, language: str = "Chinese") -> str:
        """
    生成接口自动化测试用例
    
    Args:
        prompt (str): 接口测试需求描述（示例："测试用户登录接口"）
        language (str): 输出语言（默认中文）

    Returns:
        str: 结构化测试用例（JSON/Markdown/文本格式）

    Raises:
        ValueError: 当无法解析AI响应时抛出
    """
        logger.info(f"🌐 AI 生成接口测试用例，需求描述: {prompt}")

        # 解析格式提示
        format_hint = ""
        # if prompt.startswith(('json[]', 'markdown[]')):
        #     format_hint = prompt.split(',')[0].strip()
        #     prompt = ','.join(prompt.split(',')[1:]).strip()

        # 构造接口测试专用提示词
        test_scenarios = [
            "正常请求测试",
            "参数边界值测试", 
            "异常参数测试",
            "鉴权验证测试"
        ]
        req = {
                "header": prompt["req"]['header'],
                "body": prompt["req"]['body'],
                "body_type": prompt["req"]['body_type'],
                "params": [],
                "file_path": prompt["req"]["file_path"],
                "form_data":prompt["req"]["form_data"],
                "form_urlencoded": prompt["req"]["form_urlencoded"]
            }
        # 根据不同格式构造提示模板
        template = f"""{{
            "name": "正常请求测试-测试正常情况",
            "method": "{prompt['req']['method']}",
            "url": "{prompt['url']}",
            "req": {req}
        }}"""
        case_prompt = f"""
作为资深测试工程师，请基于以下接口需求生成接口自动化测试用例, 尽可能的丰富一点。要求：

测试接口：{prompt}
测试类型：{test_scenarios}
语言要求：{language}

### 核心指令
1. 返回格式必须是 **JSON 字符串**，包含一个数组（Array）
2. 数组中的每个元素是对象（Object），表示一个测试用例
3. 包含多样化的测试场景：正常功能、边界值、异常输入, 边界值的用例默认最大值24个字符串长度
4. 根据被测对象类型自动调整用例结构
5. 返回数据中禁止出现('%...等未转义的单引号，大括号，.repeat(xxx))
6. 禁止出现.repeat(100)，.repeat(255)，.repeat(xxx)

校验正确的JSON格式，并严格返回JSON数据：
[{template}, ...]
使用语言：{language}
"""

        try:
            response = self.llm_client.complete(case_prompt)
            cleaned = self._clean_response(response)
            return cleaned
        except Exception as e:
            err_msg = f"接口用例生成失败: {str(e)}\n响应片段: {cleaned}" if 'cleaned' in locals() else str(e)
            logger.error(err_msg)
            raise ValueError(err_msg)    
def case_fixture():
    """
    测试用例
    Returns:
        CaseAiFixture: 测试用例类对象
    """
    return CaseAiFixture

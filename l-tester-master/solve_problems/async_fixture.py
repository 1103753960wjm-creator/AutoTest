# autowing/playwright/fixture_async.py (新文件)
import json
from typing import Any, Dict

from loguru import logger
from playwright.async_api import Page  # 修改为异步API
from autowing.core.ai_fixture_base import AiFixtureBase
from autowing.core.llm.factory import LLMFactory


class PlaywrightAsyncAiFixture(AiFixtureBase):
    """
    异步版本的AI-powered Playwright fixture
    """

    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.llm_client = LLMFactory.create()

    async def _get_page_context(self) -> Dict[str, Any]:
        """异步获取页面上下文"""
        # 获取基本页面信息
        basic_info = {
            "url": self.page.url,
            "title": await self.page.title()  # 异步调用
        }
        # 获取元素信息
        elements_info = await self.page.evaluate("""() => {
            const getVisibleElements = () => {
                // 与原代码相同的JS
                const elements = [];
                const selectors = [
                    'input', 'textarea', 'select', 'button', 'a',
                    '[role="button"]', '[role="link"]', '[role="checkbox"]', 
                    '[role="radio"]', '[role="searchbox"]', 'summary', 
                    '[draggable="true"]'
                ];
                
                for (const selector of selectors) {
                    document.querySelectorAll(selector).forEach(el => {
                        if (el.offsetWidth > 0 && el.offsetHeight > 0) {
                            elements.push({
                                tag: el.tagName.toLowerCase(),
                                type: el.getAttribute('type') || null,
                                placeholder: el.getAttribute('placeholder') || null,
                                value: el.value || null,
                                text: el.textContent?.trim() || '',
                                aria: el.getAttribute('aria-label') || null,
                                id: el.id || '',
                                name: el.getAttribute('name') || null,
                                class: el.className || '',
                                draggable: el.getAttribute('draggable') || null
                            });
                        }
                    });
                }
                return elements;
            };
            return getVisibleElements();
        }""")

        return {
            **basic_info,
            "elements": elements_info
        }

    async def ai_action(self, prompt: str, iframe=None) -> None:
        """执行基于AI的页面交互"""
        logger.info(f"🪽 AI Action: {prompt}")
        context = await self._get_page_context()  # 异步调用
        context["elements"] = self._remove_empty_keys(context.get("elements", []))

        def compute_action():
            action_prompt = f"""
You are a Playwright web automation assistant. Based on the following page context, provide instructions for the requested action.

Current page context:
URL: {context['url']}
Title: {context['title']}

Playwright page:
{self.page}

Playwright elements:
{json.dumps(context['elements'], indent=2)}

User request: {prompt}

"识别元素前，先判断是给的中文，还是dom的组件名，组件名例如：checkbox， el-tree，比如：如果元素有text属性，就优先使用text属性进行识别，如果元素没有text属性，就使用placeholder属性进行识别，如果元素没有placeholder属性，就使用CSS选择器进行识别，如果元素没有CSS选择器，就使用XPath进行识别"
"识别过程中，如果识别出来元素超过1个，立马切换另一个识别方式，比如：如果text识别出来元素超过1个，就切换到placeholder匹配方式"
"点击行为优先级规则": "text（文本） > placeholder（输入框提示） > CSS选择器 > XPath",
"输入行为优先级规则": "placeholder（输入框提示） > CSS选择器 > XPath > text（文本）",
"特殊字符处理": "文本或属性值用双引号，内部引号用反斜杠转义，如 `text=\"用户\\\"名\"`",
"常用示例":
"文本匹配": "self.page.locator('text=\"登录\"').click()",
"placeholder匹配": "self.page.locator('[placeholder=\"搜索...\"]').fill('关键词')",
"CSS选择器": "self.page.locator('css=.submit-btn').hover()",
"XPath": "self.page.locator('xpath=//button[contains(@class,\"primary\")]').press('Enter')"

Return ONLY a string with the following structure, no other text:

{"self.page.locator(text or placeholder or CSS selector or XPath to locate the element 不可以出现Unicode编码的字符).fill('text to input')"}
"""
            response = self.llm_client.complete(action_prompt)  # 假设LLM客户端也支持异步
            cleaned_response = self._clean_response(response)
            print(cleaned_response)
            return cleaned_response

        # 使用缓存管理器获取或计算指令
        # instruction = self._get_cached_or_compute(prompt, context, compute_action)
        instruction = compute_action()
        print(f"prompt: {prompt}")
        print(f"AI Instruction: {instruction}")
        # 执行操作
        # command = instruction.get('command')
        # selector = instruction.get('selector')
        # action = instruction.get('action')

        if not instruction:
            # raise ValueError("Invalid instruction format")
            return False, f"Invalid instruction format"
        try:
            await eval(instruction)
            return True, "AI 操作执行成功"
        except Exception as e:
            return False, f"AI 操作执行失败: {str(e)}"

        # 执行操作
        # element = self.page.locator(selector)
        # if iframe is not None:
        #     element = iframe.locator(selector)

        # if action == 'click':
        #     await element.click()  # 异步调用
        # elif action == 'fill':
        #     await element.fill(instruction.get('value', ''))
        #     if instruction.get('key'):
        #         await element.press(instruction.get('key'))
        # elif action == 'press':
        #     await element.press(instruction.get('key', 'Enter'))
        # elif action == 'hover':
        #     await element.hover()
        # else:
        #     return False, f"Unsupported action: {action}"
            # raise ValueError(f"Unsupported action: {action}")

    async def ai_remedy(self, prompt: str, iframe=None) -> None:
        """执行基于AI的页面交互"""
        logger.info(f"🪽 AI Action: {prompt}")
        context = await self._get_page_context()  # 异步调用
        context["elements"] = self._remove_empty_keys(context.get("elements", []))

        def compute_action():
            explanation = """
                { 'name': '点击 实用工具', # 补救目的 'type': 1, # 类型表示 1：鼠标左键单次点击，2：鼠标左键双击，3：鼠标左键长按，4：鼠标拖拽，5：直接输入，6：输入框补充输入，7：清空输入框后输入，8：上下滑动，9：左右滑动，10：if判断，11：for循环，12：设置等待时间，13：打开新的标签页，14：切换标签页， 17：执行自定义脚本，18：上传文件，19：执行目的命令，20：刷新当前页，21：关闭某个标签页 'action': { 'type': 1, 'input': '', 'assert': [], 'target': '', # 当type= 'cookies': [], 'element': '//*[@id=\'app\']/div[1]/section[1]/aside[1]/div[2]/div[1]/div[1]/ul[1]/li[2]/div[1]/span[1]', # 元素地址，当他是一个list时，英文','作为分隔符，区分每个选择器类型的元素地址 'locator': 1, 'timeout': 15, 'up_type': 1, # 上下滑动的方向，1：向上，2：向下 'sway_type': 1, # 左右滑动的方向，1：向左，2：向右 'target_id': '', 'wait_time': 1, 'after_wait': 1, 'element_id': null, 'before_wait': 1, 'target_type': 1, 'localstorage': [], 'locator_select': 1, 'target_locator': 1, 'target_locator_select': 1 }, 'status': true, 'children': [] }
            """
            action_prompt = f"""
You are a Playwright web automation remedy. Based on the following page context, provide instructions for the requested action.

Current page context:
URL: {context['url']}
Title: {context['title']}

Playwright page:
{self.page}

Playwright elements:
{json.dumps(context['elements'], indent=2)}

User request: {prompt}

prompt解释：{explanation}


"识别元素前，先判断是给的中文，还是dom的组件名，组件名例如：checkbox， el-tree，比如：如果元素有text属性，就优先使用text属性进行识别，如果元素没有text属性，就使用placeholder属性进行识别，如果元素没有placeholder属性，就使用CSS选择器进行识别，如果元素没有CSS选择器，就使用XPath进行识别"
"识别过程中，如果识别出来元素超过1个，立马切换另一个识别方式，比如：如果text识别出来元素超过1个，就切换到placeholder匹配方式"
"点击行为优先级规则": "text（文本） > placeholder（输入框提示） > CSS选择器 > XPath",
"输入行为优先级规则": "placeholder（输入框提示） > CSS选择器 > XPath > text（文本）",
"特殊字符处理": "文本或属性值用双引号，内部引号用反斜杠转义，如 `text=\"用户\\\"名\"`",
"常用示例":
"文本匹配": "self.page.locator('text=\"登录\"').click()",
"placeholder匹配": "self.page.locator('[placeholder=\"搜索...\"]').fill('关键词')",
"CSS选择器": "self.page.locator('css=.submit-btn').hover()",
"XPath": "self.page.locator('xpath=//button[contains(@class,\"primary\")]').press('Enter')"

Return ONLY a list with the following structure, no other text:

{["self.page.locator(text to locate the element).fill('text to input')", "self.page.locator(placeholder to locate the element).fill('text to input')", "self.page.locator(xpath to locate the element).fill('text to input')", "self.page.locator(css to locate the element).fill('text to input')"]}
"""
            response = self.llm_client.complete(action_prompt)  # 假设LLM客户端也支持异步
            cleaned_response = self._clean_response(response)
            print(cleaned_response)
            return cleaned_response

        # 使用缓存管理器获取或计算指令
        # instruction = self._get_cached_or_compute(prompt, context, compute_action)
        instruction = compute_action()
        # 执行操作
        # command = instruction.get('command')
        # selector = instruction.get('selector')
        # action = instruction.get('action')

        if not instruction:
            # raise ValueError("Invalid instruction format")
            return False, f"Invalid instruction format"
        try:
            print(f"instruction: {type(eval(instruction))}")
            for i in eval(instruction):
                if i != "":
                    result = await self.run_instruction(i)
                    if result[0]:
                        return result
            return result
        except Exception as e:
            return False, f"AI 操作执行失败: {str(e)}"
        
    async def run_instruction(self, instruction):
        try:
            await eval(instruction)
            return True, "AI 操作执行成功"
        except Exception as e:
            print(f"AI 操作执行异常：{str(e)}")
            return False, f"AI 操作执行失败: {str(e)}"

        # 执行操作
        # element = self.page.locator(selector)
        # if iframe is not None:
        #     element = iframe.locator(selector)

        # if action == 'click':
        #     await element.click()  # 异步调用
        # elif action == 'fill':
        #     await element.fill(instruction.get('value', ''))
        #     if instruction.get('key'):
        #         await element.press(instruction.get('key'))
        # elif action == 'press':
        #     await element.press(instruction.get('key', 'Enter'))
        # elif action == 'hover':
        #     await element.hover()
        # else:
        #     return False, f"Unsupported action: {action}"
            # raise ValueError(f"Unsupported action: {action}")

    # 其他方法也需要类似的转换...
    async def ai_query(self, prompt: str) -> Any:
        """
        Query information from the page using AI analysis.
        Supports various data formats including arrays, objects, and primitive types.

        Args:
            prompt (str): Natural language query about the page content.
                         Can include format hints like 'string[]' or 'number'.

        Returns:
            Any: The query results in the requested format

        Raises:
            ValueError: If the AI response cannot be parsed into the requested format
        """
        logger.info(f"🪽 AI Query: {prompt}")
        context = await self._get_page_context()
        context["elements"] = self._remove_empty_keys(context.get("elements", []))

        # Parse the requested data format
        format_hint = ""
        if prompt.startswith(('string[]', 'number[]', 'object[]')):
            format_hint = prompt.split(',')[0].strip()
            prompt = ','.join(prompt.split(',')[1:]).strip()

        # Provide different prompts based on the format
        if format_hint == 'string[]':
            query_prompt = f"""
Extract text content matching the query. Return ONLY a JSON array of strings.

Page: {context['url']}
Title: {context['title']}
Query: {prompt}

Return format example: ["result1", "result2"]
No other text or explanation.
"""
        elif format_hint == 'number[]':
            query_prompt = f"""
Extract numeric values matching the query. Return ONLY a JSON array of numbers.

Page: {context['url']}
Title: {context['title']}
Query: {prompt}

Return format example: [1, 2, 3]
No other text or explanation.
"""
        else:
            # Default prompt
            query_prompt = f"""
Extract information matching the query. Return ONLY in valid JSON format.

Page: {context['url']}
Title: {context['title']}
Query: {prompt}

Return format:
- For arrays: ["item1", "item2"]
- For objects: {{"key": "value"}}
- For single value: "text" or number

No other text or explanation.
"""

        response = self.llm_client.complete(query_prompt)

        try:
            cleaned_response = self._clean_response(response)
            try:
                result = json.loads(cleaned_response)
                query_info = self._validate_result_format(result, format_hint)
                logger.debug(f"📄 Query: {query_info}")
                return query_info
            except json.JSONDecodeError:
                # If it's a string array format, try extracting from text
                if format_hint == 'string[]':
                    # Split and clean text
                    lines = [line.strip() for line in cleaned_response.split('\n')
                             if line.strip() and not line.startswith(('-', '*', '#'))]

                    # Extract lines containing query terms
                    query_terms = [term.lower() for term in prompt.split()
                                   if len(term) > 2 and term.lower() not in ['the', 'and', 'for']]

                    results = []
                    for line in lines:
                        # Check if line contains query terms
                        if any(term in line.lower() for term in query_terms):
                            # Clean text
                            text = line.strip('`"\'- ,')
                            if ':' in text:
                                text = text.split(':', 1)[1].strip()
                            if text:
                                results.append(text)

                    if results:
                        # Remove duplicates while preserving order
                        seen = set()
                        query_info = [x for x in results if not (x in seen or seen.add(x))]
                        logger.debug(f"📄 Query: {query_info}")
                        return query_info

                raise ValueError(f"Failed to parse response as JSON: {cleaned_response[:100]}...")

        except Exception as e:
            raise ValueError(f"Query failed. Error: {str(e)}\nResponse: {cleaned_response[:100]}...")

    async def ai_assert(self, prompt: str) -> bool:
        """
        Verify a condition on the page using AI analysis.

        Args:
            prompt (str): Natural language description of the condition to verify

        Returns:
            bool: True if the condition is met, False otherwise

        Raises:
            ValueError: If the AI response cannot be parsed as a boolean value
        """
        logger.info(f"🪽 AI Assert: {prompt}")
        context = await self._get_page_context()
        context["elements"] = self._remove_empty_keys(context.get("elements", []))
        # Optimize the prompt to be concise and explicitly require a boolean return
        assert_prompt = f"""
You are a playwright automation assistant. Verify the following assertion and return ONLY a boolean value.

Page URL: {context['url']}
Page Title: {context['title']}

Available elements:
{self.page}

Playwright Assertion element: {prompt}

IMPORTANT: Return ONLY the word 'true' or 'false' (lowercase). No other text, no explanation.
"""

        response = self.llm_client.complete(assert_prompt)
        cleaned_response = self._clean_response(response).lower()

        try:
            # Directly match true or false
            if cleaned_response == 'true':
                return True
            if cleaned_response == 'false':
                return False

            # If response contains other content, try extracting boolean
            if 'true' in cleaned_response.split():
                return True
            if 'false' in cleaned_response.split():
                return False

            raise ValueError("Response must be 'true' or 'false'")

        except Exception as e:
            print(f"AI断言异常, 原因是：{e}")
            return False
            # Provide more useful error information
            # raise ValueError(
            #     f"Failed to parse assertion result. Response: {cleaned_response[:100]}... "
            #     f"Error: {str(e)}"
            # )
    
    async def ai_web_cases(self, prompt: str, language: str = "Chinese") -> list:
        
        return True

# 创建异步fixture的工厂函数
def create_async_fixture():
    """
    创建异步版PlaywrightAiFixture工厂
    """
    return PlaywrightAsyncAiFixture
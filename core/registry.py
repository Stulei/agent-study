from core.tool_registry import ToolRegistry
from core.tool_spec import ToolSpec
from tools.calculator import calculator_tool
from tools.time_tool import get_current_time
from tools.text_analyzer import text_analyzer
from core.validators import (
    validate_calculator_args,
    validate_get_current_time_args,
    validate_text_analyzer_args,
)

registry = ToolRegistry()

registry.register(
    ToolSpec(
        name="calculator",
        description="用于计算数学表达式，例如 128 * 37、(100 + 20) / 3。",
        parameters={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "要计算的数学表达式字符串，例如 '128 * 37'、'(100 + 20) / 3'。",
                }
            },
            "required": ["expression"],
            "additionalProperties": False,
        },
        executor=calculator_tool,
        validator=validate_calculator_args,
    )
)
registry.register(
    ToolSpec(
        name="get_current_time",
        description="获取当前时间。",
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        executor=get_current_time,
        validator=validate_get_current_time_args,
    )
)
registry.register(
    ToolSpec(
        name="text_analyzer",
        description="分析文本，返回字符数、按空格切分的片段数、行数、是否为空等基础统计信息。",
        parameters={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "要分析的文本字符串。",
                }
            },
            "required": ["text"],
            "additionalProperties": False,
        },
        executor=text_analyzer,
        validator=validate_text_analyzer_args,
    )
)

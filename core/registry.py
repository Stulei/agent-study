from core.tool_registry import ToolRegistry
from core.tool_spec import ToolSpec
from tools.calculator import calculator_tool
from tools.time_tool import get_current_time
from tools.text_analyzer import text_analyzer
from core.tool_params import (
    CalculatorParams,
    GetCurrentTimeParams,
    TextAnalyzerParams,
)

registry = ToolRegistry()

registry.register(
    ToolSpec(
        name="calculator",
        description="用于计算数学表达式，例如 128 * 37、(100 + 20) / 3。",
        params_model=CalculatorParams,
        executor=calculator_tool,
    )
)
registry.register(
    ToolSpec(
        name="get_current_time",
        description="获取当前时间。",
        params_model=GetCurrentTimeParams,
        executor=get_current_time,
    )
)
registry.register(
    ToolSpec(
        name="text_analyzer",
        description="分析文本，返回字符数、按空格切分的片段数、行数、是否为空等基础统计信息。",
        params_model=TextAnalyzerParams,
        executor=text_analyzer,
    )
)

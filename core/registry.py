from tools.calculator import calculator_tool
from tools.time_tool import get_current_time
from tools.text_analyzer import text_analyzer
from core.validators import (
    validate_calculator_args,
    validate_get_current_time_args,
    validate_text_analyzer_args,
)

TOOL_REGISTRY = {
    "calculator": calculator_tool,
    "get_current_time": get_current_time,
    "text_analyzer": text_analyzer,
}

TOOL_VALIDATORS = {
    "calculator": validate_calculator_args,
    "get_current_time": validate_get_current_time_args,
    "text_analyzer": validate_text_analyzer_args,
}

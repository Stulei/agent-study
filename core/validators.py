from typing import Any

def validate_calculator_args(args: dict[str, Any]) -> tuple[bool, str | None]:
    expression = args.get("expression")

    if expression is None:
        return False, "缺少必填参数 expression"

    if not isinstance(expression, str):
        return False, "expression 必须是字符串"

    if not expression.strip():
        return False, "expression 不能为空"

    if len(expression) > 100:
        return False, "expression 过长，最多允许 100 个字符"

    return True, None


def validate_get_current_time_args(args: dict[str, Any]) -> tuple[bool, str | None]:
    if args:
        return False, "get_current_time 不需要任何参数"

    return True, None


def validate_text_analyzer_args(args: dict[str, Any]) -> tuple[bool, str | None]:
    text = args.get("text")

    if text is None:
        return False, "缺少必填参数 text"

    if not isinstance(text, str):
        return False, "text 必须是字符串"

    if len(text) > 5000:
        return False, "text 过长，最多允许 5000 个字符"

    return True, None
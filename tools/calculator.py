import ast
import operator
from typing import Any

ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_eval_math(expression: str) -> float:
    """
    安全计算器工具，支持基本的数学运算。
    不使用 eval，避免执行恶意代码。
    """

    def _eval(node: ast.AST) -> float:
        if isinstance(node, ast.Constant) and isinstance(
            node.value, (int, float)
        ):  # 数字常量
            return node.value

        if isinstance(node, ast.BinOp):  # 二元运算
            left = _eval(node.left)
            right = _eval(node.right)
            op_type = type(node.op)

            if op_type not in ALLOWED_OPERATORS:
                raise ValueError(f"不支持的运算符: {op_type}")

            return ALLOWED_OPERATORS[op_type](left, right)

        if isinstance(node, ast.UnaryOp):  # 一元运算
            operand = _eval(node.operand)

            op_type = type(node.op)

            if op_type not in ALLOWED_OPERATORS:
                raise ValueError(f"不支持的运算符: {op_type}")

            return ALLOWED_OPERATORS[op_type](operand)

        raise ValueError(f"不支持的表达式: {ast.dump(node)}")

    parsed_expr = ast.parse(expression, mode="eval")

    return _eval(parsed_expr.body)


def calculator_tool(expression: str) -> dict[str, Any]:
    """
    计算器工具接口，接受一个数学表达式字符串，返回计算结果。
    """
    try:
        result = safe_eval_math(expression)
        return {"result": result, "expression": expression, "ok": True}
    except ZeroDivisionError as e:
        return {
            "error": "除零错误",
            "expression": expression,
            "ok": False,
            "error_type": "ZeroDivisionError",
        }
    except Exception as e:
        return {
            "error": str(e),
            "expression": expression,
            "ok": False,
            "error_type": "GeneralError",
        }

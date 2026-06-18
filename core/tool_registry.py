from core.tool_spec import ToolSpec
from typing import Any


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        """
        注册一个工具
        """
        self._tools[spec.name] = spec

    def get(self, name: str) -> ToolSpec | None:
        """
        根据工具名称获取工具定义
        """
        return self._tools.get(name)

    def has(self, name: str) -> bool:
        """
        检查是否已注册指定名称的工具
        """
        return name in self._tools

    def get_openai_schema(self) -> list[dict[str, Any]]:
        """
        获取所有已注册工具的OpenAI API格式定义
        """
        return [tool.to_openai_schema() for tool in self._tools.values()]

    def execute(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        """
        执行指定工具
        """

        if not self.has(name):
            return {
                "ok": False,
                "error_type": "UnknownTool",
                "error": f"未知工具: {name}",
                "tool_name": name,
            }
        tool_spec = self.get(name)
        if tool_spec.validator:
            is_valid, error_message = tool_spec.validator(args)
            if not is_valid:
                return {
                    "ok": False,
                    "error_type": "ValidationError",
                    "error": error_message,
                    "tool_name": name,
                    "tool_args": args,
                }
        try:
            return tool_spec.executor(**args)
        except TypeError as e:
            return {
                "ok": False,
                "error_type": "TypeError",
                "error": str(e),
                "tool_name": name,
                "tool_args": args,
            }
        except Exception as e:
            return {
                "ok": False,
                "error_type": "ToolRuntimeError",
                "error": str(e),
                "tool_name": name,
                "tool_args": args,
            }

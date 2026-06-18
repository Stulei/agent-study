from typing import Any
from typing import Callable


class ToolSpec:
    def __init__(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        executor: Callable,
        validator: Callable | None = None,
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.executor = executor
        self.validator = validator

    def to_openai_schema(self) -> dict[str, Any]:
        """
        生成OpenAI API格式的tool定义
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
                "strict": True,
            },
        }

from typing import Any
from typing import Callable
from pydantic import BaseModel


class ToolSpec:
    def __init__(
        self,
        name: str,
        description: str,
        executor: Callable,
        parameters: dict[str, Any] | None = None,
        validator: Callable | None = None,
        params_model: type[BaseModel] | None = None,
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.executor = executor
        self.validator = validator
        self.params_model = params_model

    def to_openai_schema(self) -> dict[str, Any]:
        """
        生成OpenAI API格式的tool定义
        """
        if self.params_model:
            return {
                "type": "function",
                "function": {
                    "name": self.name,
                    "description": self.description,
                    "parameters": self.params_model.model_json_schema(),
                    "strict": True,
                },
            }
        else:
            return {
                "type": "function",
                "function": {
                    "name": self.name,
                    "description": self.description,
                    "parameters": self.parameters,
                    "strict": True,
                },
            }

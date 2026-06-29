from pydantic import BaseModel, Field

class CalculatorParams(BaseModel):
    expression: str=Field(
        ...,
        description="要计算的数学表达式字符串，例如 '128 * 37'、'(100 + 20) / 3'。",
        min_length=1,
        max_length=100,
    )

class GetCurrentTimeParams(BaseModel):
    pass


class TextAnalyzerParams(BaseModel):
    text: str=Field(
        ...,
        description="要分析的文本字符串。",
        max_length=5000,
    )
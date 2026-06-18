from typing import Any

def text_analyzer(text: str) -> dict[str, Any]:
    """
    文本分析工具接口。
    注意：space_separated_word_count 是按空格切分的片段数，不是严格中文分词。
    """
    lines = text.splitlines()
    words = text.split()

    return {
        "ok": True,
        "text": text,
        "char_count": len(text),
        "space_separated_word_count": len(words),
        "line_count": len(lines) if lines else 1,
        "is_empty": len(text.strip()) == 0,
    }
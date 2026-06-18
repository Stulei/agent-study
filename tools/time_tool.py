from datetime import datetime
from typing import Any

def get_current_time() -> dict[str, Any]:
    """
    获取当前时间的工具接口，返回当前时间字符串。
    """

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"current_time": now, "ok": True}
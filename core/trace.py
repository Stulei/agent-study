from datetime import datetime
import time
import uuid
from typing import Any

def now_ms() -> int:
    return int(time.time() * 1000)


def new_request_id() -> str:
    return str(uuid.uuid4())


def add_trace(
    trace: list[dict[str, Any]],
    request_id: str,
    event_type: str,
    payload: dict[str, Any],
) -> None:
    """
    添加追踪信息到 trace 列表中。
    """

    trace.append(
        {
            "request_id": request_id,
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            **payload,
        }
    )
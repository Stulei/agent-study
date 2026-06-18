from core.registry import registry
from core.trace import now_ms, add_trace, new_request_id
import json
from typing import Any
import os

# 第三方
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

MODEL = os.getenv("OPENAI_MODEL", "deepseek-v4-flash")


def run_agent(user_input: str, debug: bool = False) -> tuple[str, list[dict[str, Any]]]:
    request_id = new_request_id()
    trace = []
    add_trace(trace, request_id, "request_start", {"user_input": user_input})

    messages = [
        {
            "role": "system",
            "content": (
                "你是一个严谨的中文数据助手。"
                "当用户的问题需要数学计算时，必须调用 calculator 工具。"
                "当用户的问题需要文本分析时，必须调用 text_analyzer 工具。"
                "当用户的问题需要获取当前时间时，必须调用 get_current_time 工具。"
                "不要自己心算复杂计算，也不要凭空编造当前时间。"
                "如果工具返回ok=false，说明工具执行失败了，你必须如实告诉用户失败原因，并给出可修正建议。"
                "工具返回后，用简洁中文解释结果。"
            ),
        },
        {
            "role": "user",
            "content": user_input,
        },
    ]

    max_iterations = 5
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        llm_start_ms = now_ms()

        chat_response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=registry.get_openai_schema(),
        )

        latency_ms = now_ms() - llm_start_ms

        assistant_message = chat_response.choices[0].message
        messages.append(assistant_message)

        tool_calls_count = len(assistant_message.tool_calls or [])

        add_trace(
            trace,
            request_id,
            "llm_response",
            {
                "response_content": assistant_message.content,
                "tool_calls_count": tool_calls_count,
                "latency_ms": latency_ms,
                "model": MODEL,
                "has_tool_calls": tool_calls_count > 0,
            },
        )

        # 如果模型没有要求调用工具，直接返回模型回答
        if not assistant_message.tool_calls:
            if debug:
                print("模型没有要求调用工具，直接返回回答。")
            answer = assistant_message.content or ""
            add_trace(
                trace,
                request_id,
                "request_end",
                {"final_answer": answer, "used_tool": True},
            )
            return answer, trace

        # 执行模型请求的工具调用
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            try:
                tool_args = json.loads(tool_call.function.arguments or "{}")
            except json.JSONDecodeError as e:
                if debug:
                    print("工具参数解析失败。")
                tool_args = {}
                tool_result = {
                    "ok": False,
                    "error_type": "InvalidToolArguments",
                    "error": f"工具参数不是有效的 JSON: {str(e)}",
                    "tool_name": tool_name,
                    "raw_arguments": tool_call.function.arguments,
                }

                add_trace(
                    trace,
                    request_id,
                    "tool_call_error",
                    {
                        "tool_name": tool_name,
                        "error_type": "InvalidToolArguments",
                        "error_message": tool_result,
                        "raw_arguments": tool_call.function.arguments,
                    },
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result, ensure_ascii=False),
                    }
                )
                continue

            if debug:
                print("\n[Tool Call]")
                print(f"request_id: {request_id}")
                print(f"工具名称: {tool_name}")
                print(f"工具参数: {tool_args}")

            tool_start_ms = now_ms()
            tool_result = registry.execute(tool_name, tool_args)

            latency_ms = now_ms() - tool_start_ms

            if debug:
                print(f"工具结果: {tool_result}")
                print(f"工具执行耗时: {latency_ms} ms")

            add_trace(
                trace,
                request_id,
                "tool_call",
                {
                    "tool_name": tool_name,
                    "tool_args": tool_args,
                    "tool_result": tool_result,
                    "latency_ms": latency_ms,
                    "ok": tool_result.get("ok", False),
                    "error_type": tool_result.get("error_type"),
                },
            )

            # 把工具执行结果返回给模型
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result, ensure_ascii=False),
                }
            )

    # 超过最大循环次数，强制结束
    error_answer = (
        f"Agent 已执行 {max_iterations} 轮工具调用，但仍未完成任务。"
        f"请尝试简化你的问题。"
    )

    add_trace(
        trace, request_id, "request_end",
        {"final_answer": error_answer, "used_tool": True, "max_iterations_exceeded": True},
    )

    return error_answer, trace


# 测试 Agent
if __name__ == "__main__":
    print("Mini Tool Calling Agent 已启动。输入 exit 退出。")

    while True:
        user_input = input("\n你：").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("退出。")
            break

        answer, trace = run_agent(user_input, debug=True)
        print(f"\nAgent：{answer}")
        print(f"Trace：{trace}")
        print(json.dumps(trace, ensure_ascii=False, indent=2))

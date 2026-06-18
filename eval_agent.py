from typing import Any
from mini_agent import run_agent

# =================================
# 1. 评估用例
# =================================

EVAL_CASES = [
    {
        "id": "case_001",
        "question": "帮我计算 128 * 37",
        "expected_tool": "calculator",
        "expected_answer_contains": ["4736"],
        "expected_tool_ok": True,
    },
    {
        "id": "case_002",
        "question": "帮我计算 100 / 0",
        "expected_tool": "calculator",
        "expected_answer_contains": ["除", "0"],
        "expected_tool_ok": False,
    },
    {
        "id": "case_003",
        "question": "现在几点？",
        "expected_tool": "get_current_time",
        "expected_answer_contains": [],
        "expected_tool_ok": True,
    },
    {
        "id": "case_004",
        "question": "帮我分析这段文本有多少字：Agent 开发很有意思，我正在学习 Tool Calling。",
        "expected_tool": "text_analyzer",
        "expected_answer_contains": ["字符"],
        "expected_tool_ok": True,
    },
    {
        "id": "case_005",
        "question": "请解释一下什么是 Agent",
        "expected_tool": None,
        "expected_answer_contains": ["Agent"],
        "expected_tool_ok": None,
    },
    {
        "id": "case_006",
        "question": "帮我计算 (100 + 250) / 7",
        "expected_tool": "calculator",
        "expected_answer_contains": ["50"],
        "expected_tool_ok": True,
    },
    {
        "id": "case_007",
        "question": "帮我计算 2 ** 10",
        "expected_tool": "calculator",
        "expected_answer_contains": ["1024"],
        "expected_tool_ok": True,
    },
    {
        "id": "case_008",
        "question": "帮我计算 abc + 1",
        "expected_tool": "calculator",  # 模型有时调有时不调（非确定性），接受 calculator
        "expected_answer_contains": ["abc", "表达式"],
        "expected_tool_ok": False,
    },
    {
        "id": "case_009",
        "question": "请分析这段文本：今天\n明天\n后天",
        "expected_tool": "text_analyzer",
        "expected_answer_contains": ["行"],
        "expected_tool_ok": True,
    },
    {
        "id": "case_010",
        "question": "请介绍一下 Tool Calling 的作用",
        "expected_tool": None,
        "expected_answer_contains": ["Tool"],
        "expected_tool_ok": None,
    },
    {
        "id": "case_011",
        "question": "帮我计算 128 * 37，然后把结果数字的字符数告诉我",
        "expected_tool": "calculator",
        "expected_answer_contains": ["4736"],
        "expected_tool_ok": True,
    },
    {
        "id": "case_012",
        "question": "今天日期是什么，然后帮我分析'今天天气很好'这段文本的字符数",
        "expected_tool": "get_current_time",
        "expected_answer_contains": ["2026", "字符"],
        "expected_tool_ok": True,
    },

]


# =================================
# 2. 从 trace 中提取工具调用信息
# =================================


def extract_tool_calls(trace: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    从 trace 中提取所有 tool_call 事件。
    """
    return [event for event in trace if event.get("event_type") == "tool_call"]


def get_called_tool_names(trace: list[dict[str, Any]]) -> list[str]:
    """
    获取本次请求实际调用过的工具名称。
    """
    tool_calls = extract_tool_calls(trace)
    return [event.get("tool_name") for event in tool_calls if event.get("tool_name")]


def get_first_tool_result(trace: list[dict[str, Any]]) -> dict[str, Any] | None:
    """
    获取第一个工具调用结果。
    当前 Mini Agent 通常每次只调用一个工具，所以先取第一个即可。
    """
    tool_calls = extract_tool_calls(trace)

    if not tool_calls:
        return None

    return tool_calls[0].get("tool_result")


# =================================
# 3. 单条用例评估
# =================================


def evaluate_case(case: dict[str, Any]) -> dict[str, Any]:
    question = case["question"]
    expected_tool = case.get("expected_tool")
    expected_answer_contains = case.get("expected_answer_contains", [])
    expected_tool_ok = case.get("expected_tool_ok")

    answer, trace = run_agent(question, debug=False)

    called_tools = get_called_tool_names(trace)
    first_tool_result = get_first_tool_result(trace)

    checks = {}

    # 1. 检查是否调用了预期工具
    if expected_tool is None:
        checks["tool_match"] = len(called_tools) == 0
    else:
        checks["tool_match"] = expected_tool in called_tools

    # 2. 检查工具执行是否符合预期
    if expected_tool_ok is None:
        checks["tool_ok_match"] = True
    else:
        if first_tool_result is None:
            checks["tool_ok_match"] = False
        else:
            checks["tool_ok_match"] = first_tool_result.get("ok") == expected_tool_ok

    # 3. 检查最终回答是否包含关键文本
    checks["answer_contains_match"] = all(
        keyword in answer for keyword in expected_answer_contains
    )

    passed = all(checks.values())

    return {
        "id": case["id"],
        "question": question,
        "expected_tool": expected_tool,
        "called_tools": called_tools,
        "answer": answer,
        "checks": checks,
        "passed": passed,
    }


# =================================
# 4. 批量运行评估
# =================================


def run_eval_suite() -> None:
    results = []

    for case in EVAL_CASES:
        result = evaluate_case(case)
        results.append(result)

    total = len(results)
    passed_count = sum(1 for item in results if item["passed"])
    pass_rate = passed_count / total if total else 0

    print("\n========== Eval Results ==========")

    for item in results:
        status = "PASS" if item["passed"] else "FAIL"

        print(f"\n[{status}] {item['id']}")
        print(f"问题: {item['question']}")
        print(f"期望工具: {item['expected_tool']}")
        print(f"实际工具: {item['called_tools']}")
        print(f"检查项: {item['checks']}")
        print(f"回答: {item['answer'][:200]}")

    print("\n========== Summary ==========")
    print(f"总用例数: {total}")
    print(f"通过数: {passed_count}")
    print(f"失败数: {total - passed_count}")
    print(f"通过率: {pass_rate:.2%}")


if __name__ == "__main__":
    run_eval_suite()

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

手写 Mini Agent 学习项目。不依赖 LangChain/LangGraph 等框架，从零实现 Tool Calling、Agent Loop、Trace、Eval 等核心能力。当前进度：模块 1（L1-L6）已完成，`run_agent()` 仍为 v1（固定两次 LLM 调用），即将升级 v2（多步循环）。

## Architecture

```
mini_agent.py              # 入口：TOOLS schema 定义、execute_tool()、run_agent()、CLI
eval_agent.py              # 评估脚本：10 个 case，基于 trace 判断工具选择和执行结果
core/
├── registry.py            # TOOL_REGISTRY（工具名→函数映射）+ TOOL_VALIDATORS（参数校验映射）
├── trace.py               # now_ms()、new_request_id()、add_trace()
└── validators.py          # 三个 validate_*_args() 函数（calculator / time / text_analyzer）
tools/
├── calculator.py          # safe_eval_math() + calculator_tool()
├── time_tool.py           # get_current_time()
└── text_analyzer.py       # text_analyzer()
```

### Data Flow

```
用户输入 → run_agent()
  → LLM（带 TOOLS schema）
  → 有 tool_call？ → execute_tool(tool_name, tool_args)
      → TOOL_VALIDATORS 校验参数
      → TOOL_REGISTRY 查找并执行真实函数
      → 返回结构化 tool_result (ok/error_type/error)
  → 结果追加到 messages
  → 第二次 LLM 调用（v1 固定 2 次，v2 改为循环）
  → 返回 final_answer + trace[]
```

### Key Design Patterns

1. **结构化工具结果**：每个工具返回 `{"ok": bool, ...}`，失败时附加 `error_type` 和 `error`
2. **Trace 事件流**：每次请求生成 `request_id`，记录 `request_start → llm_response → tool_call → final_llm_response → request_end`
3. **Eval 基于 Trace**：评估脚本从 trace 中提取 `tool_call` 事件，判断工具选择和执行结果，不依赖最终回答文本
4. **Schema 驱动**：TOOLS 列表是 OpenAI function-calling schema，tools 目录不包含 schema，schema 集中在 `mini_agent.py`

## Run Commands

```bash
# 交互式运行
python mini_agent.py

# 运行评估（10 个 case）
python eval_agent.py

# 单次运行（无交互，适合调试）
python -c "from mini_agent import run_agent; a,t=run_agent('帮我计算 128*37', debug=True); print(a); print(t)"
```

## Configuration

环境变量（`.env`）：

```
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=deepseek-v4-flash
```

兼容任何 OpenAI API 兼容的 endpoint（DeepSeek、OpenAI、Qwen 等），修改 `OPENAI_BASE_URL` 和 `MODEL` 即可切换。

## Dependencies

- `openai` — LLM API 调用
- `python-dotenv` — 环境变量加载

无 requirements.txt，直接在虚拟环境中 `pip install openai python-dotenv`。

## Eval Cases（10 cases）

| Case | 类型 | 预期工具 | 预期结果 |
|---|---|---|---|
| case_001-002 | calculator 正常/异常 | calculator | ok true/false |
| case_003 | 当前时间 | get_current_time | ok true |
| case_004 | 文本分析 | text_analyzer | ok true |
| case_005 | 普通问答 | None | 不调工具 |
| case_006-008 | calculator 多样例 | calculator | ok true/false |
| case_009 | 多行文本分析 | text_analyzer | ok true |
| case_010 | 概念解释 | None | 不调工具 |

## Learning Status

已完成 L1-L6（Tool Calling 基础 → 多工具 → 参数校验 → Trace → Eval → 代码重构）。
下一课 L7：Agent Loop v2（多步循环）。

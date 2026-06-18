# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

手写 Mini Agent 学习项目。不依赖 LangChain/LangGraph 等框架，从零实现 Tool Calling、Agent Loop、Trace、Eval 等核心能力。当前进度：模块 1（L1-L9）已完成，`run_agent()` 已升级为 v2 多步循环，引入 `ToolSpec` + `ToolRegistry` 抽象层。

> **课程文档**：详细的上课记录、学习进度、课前教案见 Obsidian vault：
> `GrowthLibrary/03｜学习新知识/0302｜系统课程/2026_跟ai学习Agent/`

## Architecture

```
mini_agent.py              # 入口：run_agent() 多轮循环、execute_tool()、CLI
eval_agent.py              # 评估脚本：12 个 case，基于 trace 判断工具选择和执行结果
core/
├── tool_spec.py           # ToolSpec 类：统一工具定义（name/desc/params/executor/validator）
├── tool_registry.py       # ToolRegistry 类：注册、查找、执行工具（含错误处理）
├── registry.py            # 全局 registry 实例 + 三个工具注册
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
  → 构建 messages（system prompt + user input）
  → while iteration < max_iterations (5):
      → LLM（通过 ToolRegistry.get_openai_schema() 获取工具定义）
      → 记录 trace: llm_response
      → 无 tool_calls？ → 返回 final_answer + trace
      → 有 tool_calls？ → 逐个执行：
          → ToolRegistry.execute(tool_name, tool_args)
              → ToolSpec.validator 校验参数
              → ToolSpec.executor 执行函数
              → 返回结构化 result (ok/error_type/error)
          → 工具结果追加为 tool 角色消息
          → 记录 trace: tool_call
  → 超过 max_iterations → 返回超时错误 + trace
```

### Key Design Patterns

1. **ToolSpec 抽象**：每个工具统一封装 name/description/parameters/executor/validator，通过 `to_openai_schema()` 生成 OpenAI 格式
2. **ToolRegistry 统一执行**：`execute()` 方法统一处理校验 → 执行 → 错误捕获，所有工具结果结构化
3. **结构化工具结果**：每个工具返回 `{"ok": bool, ...}`，失败时附加 `error_type` 和 `error`
4. **Trace 事件流**：每次请求生成 `request_id`，记录 `request_start → llm_response → tool_call → request_end`
5. **Eval 基于 Trace**：评估脚本从 trace 中提取 `tool_call` 事件，判断工具选择和执行结果，不依赖最终回答文本
6. **Schema 驱动**：工具定义集中在 `registry.py`，tools 目录只含纯函数实现，不包含 schema

## Run Commands

```bash
# 交互式运行
python mini_agent.py

# 运行评估（12 个 case）
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

## Eval Cases（12 cases）

| Case | 类型 | 预期工具 | 预期结果 |
|---|---|---|---|
| case_001 | 计算 128*37 | calculator | ok=true |
| case_002 | 计算 100/0（异常） | calculator | ok=false |
| case_003 | 当前时间 | get_current_time | ok=true |
| case_004 | 文本分析 | text_analyzer | ok=true |
| case_005 | 概念解释 | None | 不调工具 |
| case_006 | 计算 (100+250)/7 | calculator | ok=true |
| case_007 | 计算 2**10 | calculator | ok=true |
| case_008 | 计算 abc+1（异常） | calculator | ok=false |
| case_009 | 多行文本分析 | text_analyzer | ok=true |
| case_010 | 概念解释 | None | 不调工具 |
| case_011 | 计算后获取字符数（多步） | calculator | ok=true |
| case_012 | 日期 + 文本分析（多工具） | get_current_time | ok=true |

## Git

- **Remote**：`git@github.com:Stulei/agent-study.git`
- **分支策略**：课程在 `lessonXX` 分支开发，eval 全部 PASS 后合并到 `main`，保留分支
- **Commit 约定**：`Lxx:` 课程代码 / `DOC:` 文档 / `FIX:` 修复 / `REF:` 重构
- 每次上课完成后提交并推送

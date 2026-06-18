# Agent Study

手写 Mini Agent 学习项目。这个仓库从零实现 Agent 的核心能力：Tool Calling、工具参数校验、Trace 观测、自动评估和多轮 Agent Loop。

> 目标：不依赖 LangChain/LangGraph 等框架，自己实现 Agent 的决策闭环与工具执行流程。

## 项目结构

```
agent-study/
├── README.md
├── CLAUDE.md
├── mini_agent.py              # 入口：run_agent() 多轮循环、CLI 交互
├── eval_agent.py              # 评估脚本：12 个 case，基于 trace 判断行为
├── core/
│   ├── __init__.py
│   ├── tool_spec.py           # ToolSpec 类：统一工具定义 + OpenAI schema 生成
│   ├── tool_registry.py       # ToolRegistry 类：工具注册、查找、执行
│   ├── registry.py            # 全局 registry 实例 + 三个工具的注册
│   ├── trace.py               # now_ms()、new_request_id()、add_trace()
│   └── validators.py          # 三个 validate_*_args() 参数校验函数
└── tools/
    ├── __init__.py
    ├── calculator.py           # safe_eval_math() + calculator_tool()
    ├── time_tool.py            # get_current_time()
    └── text_analyzer.py        # text_analyzer()
```

## 核心功能

- `mini_agent.py`
  - 项目入口，定义 `run_agent()` 多轮工具调用循环
  - 支持 `max_iterations=5` 防止无限循环
  - 提供交互式 CLI（`python mini_agent.py`）
- `eval_agent.py`
  - 评估脚本，自动执行 12 个测试用例
  - 从 `trace` 提取工具调用行为，判断 Agent 是否符合预期
  - 支持多工具调用场景评估
- `core/tool_spec.py`
  - `ToolSpec` 类：统一封装工具名称、描述、参数 schema、执行函数、校验函数
  - `to_openai_schema()` 方法生成 OpenAI function-calling 格式
- `core/tool_registry.py`
  - `ToolRegistry` 类：管理工具的注册、查找、执行
  - `execute()` 方法统一处理校验 → 执行 → 错误捕获流程
  - `get_openai_schema()` 批量导出所有工具 schema
- `core/registry.py`
  - 创建全局 `registry` 实例
  - 注册 `calculator`、`get_current_time`、`text_analyzer` 三个工具
- `core/trace.py`
  - 追踪工具调用与请求流程
  - 提供 `now_ms()`、`new_request_id()`、`add_trace()`
- `core/validators.py`
  - 工具参数校验函数，保护工具调用输入合法性
- `tools/*.py`
  - 各个具体工具实现
  - `calculator.py`：安全表达式计算（基于 AST）
  - `time_tool.py`：获取当前时间
  - `text_analyzer.py`：文本基础统计（字符数、片段数、行数等）

## 设计思路

### Agent 核心数据流

```
用户输入 → run_agent()
  → 构建 messages（system prompt + user input）
  → while iteration < max_iterations:
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

### 关键设计原则

- **关注点分离**：模型只负责决策，不负责真正执行工具
- **结构化结果**：工具执行结果统一为 `{"ok": bool, ...}`，失败时附加 `error_type` 和 `error`
- **全面可观测**：所有 LLM 调用和工具执行都记录 `trace`，便于评估和调试
- **Schema 驱动**：工具定义通过 `ToolSpec` 统一管理，集中在 `registry.py`，与具体实现解耦
- **安全执行**：`calculator` 基于 AST 而非 `eval()`，避免代码注入
- **循环控制**：`max_iterations` 防止无限循环，超限后返回明确错误

## 已实现能力

| 模块 | 内容 |
|---|---|
| L1 | 最小 Tool Calling Agent（单次 LLM + 工具调用） |
| L2 | 多工具选择（calculator / time / text_analyzer） |
| L3 | 工具参数校验与错误恢复 |
| L4 | 工具调用观测与 Trace 设计 |
| L5 | 自动评估能力（10 cases → 12 cases） |
| L6 | 项目重构与模块化结构 |
| L7 | Agent Loop v2（多轮工具调用循环，max_iterations=5） |
| L8 | ToolSpec + ToolRegistry 抽象层 |
| L9 | 多工具/多步调用场景评估（cases 011-012） |

## 评估用例（12 cases）

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

## 运行方式

### 1. 创建虚拟环境并安装依赖

```bash
python -m venv .venv
source .venv/bin/activate
pip install openai python-dotenv
```

### 2. 配置 `.env`

```text
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=deepseek-v4-flash
```

兼容任何 OpenAI API 兼容的 endpoint（DeepSeek、OpenAI、Qwen 等）。

### 3. 运行

```bash
# 交互式运行
python mini_agent.py

# 运行评估
python eval_agent.py

# 单次运行（调试用）
python -c "from mini_agent import run_agent; a,t=run_agent('帮我计算 128*37', debug=True); print(a); print(t)"
```

## 仓库与分支

| 分支/标签 | 说明 |
|---|---|
| `main` | 最新代码（已合并 lesson09） |
| `lesson08` | L8 ToolSpec + ToolRegistry 重构 |
| `lesson09` | L9 多工具/多步评估（已合并到 main） |
| `lesson07` (tag) | L7 Agent Loop v2 完成点 |

合并策略：分支开发 → 合并到 `main` 后保留分支，便于复现课程步骤。

## 课程学习路径

本项目对应"跟 AI 学习 Agent"课程的学习线索：

- `lesson01` — Tool Calling 到底是什么？
- `lesson02` — 多工具 Agent
- `lesson03` — 工具参数校验与错误恢复
- `lesson04` — 工具调用观测与 Trace 设计
- `lesson05` — 给 Mini Agent 增加基础评估能力
- `lesson06` — 代码重构与项目结构
- `lesson07` — Agent Loop v2（多轮工具循环）
- `lesson08` — ToolSpec + ToolRegistry 工具抽象层
- `lesson09` — 多工具/多步调用场景评估

## 未来扩展方向

- 支持流式输出（streaming）
- 引入上下文窗口管理与 Token 计数
- Trace 可视化与结构化导出
- 支持自定义工具的热注册/热卸载
- 更健壮的多轮评估框架（处理模型非确定性行为）

---

如需继续演进，可参考 `CLAUDE.md` 了解详细的架构设计和实现细节。

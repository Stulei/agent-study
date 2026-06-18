# Agent Study

手写 Mini Agent 学习项目。这个仓库从零实现 Agent 的核心能力：Tool Calling、工具参数校验、Trace 观测、自动评估和多轮 Agent Loop。

> 目标：不依赖 LangChain/LangGraph 等框架，自己实现 Agent 的决策闭环与工具执行流程。

## 项目结构

```
agent-study/
├── README.md
├── CLAUDE.md
├── mini_agent.py
├── eval_agent.py
├── core/
│   ├── __init__.py
│   ├── registry.py
│   ├── trace.py
│   └── validators.py
└── tools/
  ├── __init__.py
  ├── calculator.py
  ├── time_tool.py
  └── text_analyzer.py
```

## 核心功能

- `mini_agent.py`
  - 项目入口
  - 定义模型可调用工具 schema
  - 实现 `run_agent()`：LLM 调用、工具执行、结果回传、循环控制
- `eval_agent.py`
  - 评估脚本
  - 自动执行一批测试用例
  - 从 `trace` 提取工具调用行为，判断 Agent 是否符合预期
- `core/registry.py`
  - 管理工具函数映射 `TOOL_REGISTRY`
  - 管理参数校验映射 `TOOL_VALIDATORS`
- `core/trace.py`
  - 追踪工具调用与请求流程
  - 提供 `now_ms()`、`new_request_id()`、`add_trace()`
- `core/validators.py`
  - 工具参数校验函数
  - 保护工具调用输入是否合法
- `tools/*.py`
  - 各个具体工具实现
  - `calculator.py`：安全表达式计算
  - `time_tool.py`：获取当前时间
  - `text_analyzer.py`：文本基础统计

## 设计思路

### Agent 核心数据流

1. 用户输入进入 `run_agent()`
2. 将系统提示与用户提问一起发送到模型
3. 模型判断是否需要调用工具
4. 若模型返回 `tool_call`，程序执行对应工具
5. 把工具结果作为 `tool` 角色消息追加到历史消息
6. 循环调用模型，直到模型不再请求工具
7. 返回最终回答与完整 `trace`

### 关键设计原则

- 模型只负责决策，不负责真正执行工具
- 工具执行结果必须结构化为 `ok/error_type/error` 形式
- 所有工具调用都要记录 `trace`，便于后续评估
- 每次 LLM 交互都带上工具 schema，支持多步工具调用
- 使用 `max_iterations` 防止无限循环

## 已实现能力

- L1：最小 Tool Calling Agent
- L2：多工具选择
- L3：工具参数校验与错误恢复
- L4：工具调用观测与 Trace 设计
- L5：自动评估能力
- L6：项目重构与模块化结构
- L7：Agent Loop v2（多轮工具调用）

## 运行方式

1. 创建虚拟环境并安装依赖

```bash
python -m venv .venv
source .venv/bin/activate
pip install openai python-dotenv
```

2. 在根目录创建 `.env`

```text
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=deepseek-v4-flash
```

3. 运行交互式 Agent

```bash
python mini_agent.py
```

4. 运行评估脚本

```bash
python eval_agent.py
```

## 仓库与分支

- 已在项目中使用标签和分支来标记课程进度：
  - `lesson07`：已创建并推送（课程 L7 实验点）
  - `lesson08`：功能分支（已合并到 `main` 并保留）
  - `lesson09`：已创建用于后续开发

- 合并策略：当前采用分支开发并在合并到 `main` 前保留分支以便复现课程步骤。

## 配置与敏感信息（`.env`）

- `OPENAI_BASE_URL` / `OPENAI_API_KEY` / `OPENAI_MODEL` 等敏感配置应保存在项目根目录的 `.env` 文件中，但该文件不会被提交到仓库（已经在 `.gitignore` 中配置）。
- 当你克隆仓库后，请复制或新建 `.env` 并填入你自己的 API Key 与模型配置，例如：

```text
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=deepseek-v4-flash
```

- 本地运行示例：

```bash
source .venv/bin/activate
python mini_agent.py
```

## 课程学习路径

本项目对应“跟 AI 学习 Agent”课程的学习线索：

- `lesson01｜Tool Calling 到底是什么？`：理解 Agent 的核心流程与最小实现
- `lesson02｜多工具 Agent`：让模型在多种工具间选择
- `lesson03｜工具参数校验与错误恢复`：增加参数校验与异常保护
- `lesson04｜工具调用观测与 Trace 设计`：记录每次交互与工具调用信息
- `lesson05｜给 Mini Agent 增加基础评估能力`：实现自动评估脚本
- `lesson06｜代码重构与项目结构`：模块化项目结构，拆分职责
- `lesson07｜Agent Loop v2`：从固定两次调用升级为多轮工具循环

## 说明与建议

- `CLAUDE.md` 记录了项目总体架构与实现思路，可作为快速概览
- 当前模型调用依赖 OpenAI 兼容 API，支持 DeepSeek、OpenAI、Qwen 等
- 若要继续演进，可考虑：
  - 增加工具抽象层与统一 ToolSpec
  - 进一步增强评估策略，处理模型不确定性行为
  - 添加 `.gitignore` 忽略 `.venv/`、`__pycache__/` 等临时文件

## 未来扩展方向

- 支持更复杂的多轮工具调用场景
- 引入工具链中的状态管理与上下文控制
- 改造 `eval_agent.py` 为更健壮的行为评估框架
- 把 `trace` 结构标准化为可视化或分析格式

---

如果你想，我也可以继续帮你补齐 `.gitignore`、清理当前仓库中的临时文件，并把 README 进一步补成项目文档格式。
# Cogito-Harness

Cogito-Harness 是一个以持续认知状态更新为核心的问题求解 Harness。本仓库当前只实现 **Story 0：工程基线与最小内核骨架**，用于冻结后续 Cogito v1 所依赖的类型、端口、持久化与事务边界。

核心原则：

> 计划不是路线图，而是方向盘——每时每刻都在微调。

当前内核坚持：Observation 与解释分离、Proposal 与正式认知对象分离、Tool Result 先转为 Observation、事件历史 append-only，以及带 `base_version` 冲突检测的原子 Cognitive Transaction。

## 环境与安装

要求：

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)

安装项目及开发依赖：

```bash
uv sync --extra dev
```

## 配置

默认 SQLite 路径来自 `cogito.toml`：

```toml
[storage]
sqlite_path = ".cogito/cogito.db"
```

可通过 `COGITO_SQLITE_PATH` 环境变量覆盖。`.env.example` 只提供变量示例，Story 0 不自动加载 `.env`。

## CLI

初始化 SQLite 五表基线：

```bash
uv run cogito init
```

创建 Episode；Goal、Hard Constraint 与 Acceptance Criterion 均为显式输入，不做自然语言智能解析：

```bash
uv run cogito episode create \
  --goal "diagnose DB connectivity" \
  --constraint "read only" \
  --criterion "identify the root cause"
```

查看 Episode：

```bash
uv run cogito episode show <episode-id>
```

输出包含 Episode、Goal、Facts、Hypotheses、Gaps 与 Cognitive Version。

## 数据库与迁移

Story 0 使用 SQLAlchemy 2.x SQLite Adapter，并将 ORM 限制在 `src/cogito/adapters/sqlite/`。Domain 使用独立的 Pydantic v2 模型，Application/Domain 不接触 ORM 或 Session。

初始 Alembic migration 创建：

- `episodes`
- `goal_contracts`
- `cognitive_events`
- `cognitive_objects`
- `cognitive_relations`

从空数据库执行迁移：

```bash
uv run alembic upgrade head
```

`EpisodeState` 是从正式对象重载得到的 runtime materialized view，不单独存表，也不是 Truth Source。

## 测试与 Fake Runtime

运行完整测试与覆盖率门槛：

```bash
uv run pytest
uv run pytest --cov=cogito --cov-branch --cov-report=term-missing
```

运行确定性 Fake Runtime 场景：

```bash
uv run python -m cogito.scenarios.fake_runtime
```

该场景使用固定的 “DB listens on 3307” FakeToolExecutor 结果，只验证：

```text
ActionDecision
→ FakeToolExecutor
→ ActionResult
→ Observation
→ SQLite Persist
```

它不会自动生成 Fact 或 Hypothesis，也不会执行任何真实外部操作。

## 当前工程边界

已实现：

- Strongly Typed IDs、Domain Models 与 Proposal Models
- CognitiveEvent、CognitiveTransaction、Port Interfaces
- SQLite/SQLAlchemy Adapter 与 Alembic migration
- FakeModelProvider、FakeToolExecutor
- 最小 CLI、Unit/Integration/Scenario Tests

明确不支持：

- 真实 OpenAI、DeepSeek 或其他模型 Provider
- 自动 Prompt、完整 Admission/Revision/Scheduler 认知循环
- 真实 Shell/Git Executor、Web Search、HTTP API、GUI
- Long-Term Memory、Memory Consolidation、Vector DB、Graph DB
- Expectation、Anomaly、Explanatory Demand、Problem Pattern
- Cognitive Pressure、Attention Allocation、Problem Reframe、Negative Evidence
- 多模型路由、并行调度、并行 Cognitive Transaction
- LangChain、LangGraph、CrewAI、AutoGen 或任何 Agent Framework

## 架构

```text
Interfaces → Application → Domain
                 ↓
               Ports
                 ↑
              Adapters
```

项目采用 single-process Modular Monolith。Application I/O 端口为 async，Domain 为同步纯模型；SQLite Adapter 内部管理 SQLAlchemy Session，且只向上层返回 Pydantic Domain Object。

## 设计文档

- [`Cogito-Harness_理论基线_v0.8.md`](Cogito-Harness_理论基线_v0.8.md)
- [`Cogito-Harness_总体开发文档_v0.1.md`](Cogito-Harness_总体开发文档_v0.1.md)
- [`Cogito-Harness_Story0_工程基线与最小内核骨架_v0.1.md`](Cogito-Harness_Story0_工程基线与最小内核骨架_v0.1.md)

后续 Story 1 才会开始实现 Admission Policies 与 Revision Engine；Story 0 不包含这些能力。

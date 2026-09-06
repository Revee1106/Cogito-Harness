# Cogito-Harness

Cogito-Harness 是一个以持续认知状态更新为核心的问题求解 Harness。当前项目状态：

- **Story 0：工程基线与最小内核骨架 — Complete / Frozen**
- **Story 1A：Cognitive Admission Foundation — Complete / Frozen**
- **Next：Story 1B Local Revision Engine — Design Frozen / Next Implementation**

核心原则：

> 计划不是路线图，而是方向盘——每时每刻都在微调。

当前内核坚持：Proposal ≠ Committed Cognition、Observation ≠ Fact、No Evidence → No Hypothesis、Evidence Relation ≠ Belief Revision、Contradiction ≠ Structural Corruption；事件历史 append-only，Cognitive Transaction 使用 `base_version` 做冲突检测并原子提交。

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

- Story 0：Python 3.14+、uv、Pydantic v2、Strongly Typed IDs、Domain/Proposal Models、Ports、SQLite、SQLAlchemy 2.x、Alembic、CognitiveTransaction、Event/Object persistence、Fake Runtime、最小 CLI 与基础测试框架。
- Story 1A：FactProposal / Fact Admission、EvidenceAdmissionPolicy、HypothesisAdmissionPolicy、Draft / Reserved Cognitive Target、CognitiveTransactionValidator，以及 `ADMIT / DEFER / REJECT / NO_NEW_ADMISSION`。
- Evidence 与 Hypothesis 不变量：Evidence relation compatibility、Evidence deduplication、No Evidence → No Hypothesis；inactive Proposition 不可被引用。
- Fact 不变量：assertion strength boundary；普通 Observation 的 `DETERMINISTIC_DERIVATION` 会 `DEFER / DERIVATION_PREMISES_REQUIRED`。
- Fact 冲突语义：可靠冲突 Fact 可共存；结果仍为 `ADMIT`，`FACT_CONFLICT` 仅作为 diagnostic，admitted Fact/Evidence bundle 可正常提交。
- Transaction 不变量：material CREATE 必须分别带有 `EVIDENCE_LINK_ADMITTED`、`FACT_ADDED` 或 `HYPOTHESIS_CREATED` 事件，并保持原子提交与版本冲突检测。

明确不支持：

- 真实 OpenAI、DeepSeek 或其他模型 Provider
- Story 1B Local Revision Engine、UPDATE / Revision event 语义与 reverse revision
- Hypothesis strengthen / reject / confirm、Gap resolution
- Fact supersede / retract / refine execution、Contradiction lifecycle、Evidence invalidation
- 自动 Prompt、完整 Scheduler / Cognitive Loop
- 真实 Shell/Git Executor、Web Search、HTTP API、GUI
- 真实 LLM integration、真实 Tool Runtime、Benchmark comparison
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

## Documentation

Current canonical documents:

- [Theory Baseline v0.9](docs/theory/Cogito-Harness_理论基线_v0.9.md)
- [Overall Development v0.2](docs/development/Cogito-Harness_总体开发文档_v0.2.md)
- [Story 1B: Local Revision Engine](docs/stories/Cogito-Harness_Story1B_Local_Revision_Engine_v0.1.md)
- [Documentation Index](docs/README.md)

Previous baselines and completed Story documents remain in the [documentation index](docs/README.md) for historical traceability. Story 1B is design-frozen and awaits implementation; Story 1A remains frozen.

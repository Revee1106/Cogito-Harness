# Cogito-Harness 总体开发文档 v0.1

> 上位理论约束：`Cogito-Harness_理论基线_v0.8.md`

## 1. 文档目的

本文档定义 Cogito-Harness 从理论到可运行产品的总体工程路线。它不重复完整认知理论，而负责回答：

- 项目整体采用什么技术栈；
- 哪些能力属于 Cogito Core；
- 哪些能力属于 Runtime / Adapter；
- v1、v1.1、v1.2、v2 分别实现什么；
- 每个阶段验证什么；
- 哪些能力明确延期；
- 如何通过 Benchmark 判断 Cogito 是否真的优于普通 Agent；
- 后续 Story 应如何拆分。

本文档是所有工程 Story 的共同上位开发约束。

## 2. 项目目标

Cogito-Harness 的最终目标不是制造一个“会自动调用工具的聊天 Agent”，而是实现一个：

> **通过 Evidence 持续维护可修订认知状态，并围绕当前最有价值 Information Gap 选择下一步可观察 Action 的认知循环 Harness。**

v1 最小工程目标：

> **Evidence-backed World Model + Gap-driven Next Action + Local Revision Loop**

v1 首先验证认知循环是否成立，而不是一次性实现完整理论。

## 3. 核心工程原则

1. **Core 不依赖 Agent Framework。** LangChain/LangGraph/CrewAI/AutoGen 等不得接管 Scheduler、Planning 或 Tool Loop。
2. **Domain 不依赖基础设施。** 不直接依赖模型 SDK、SQLAlchemy、SQLite、Typer、Shell 实现。
3. **LLM 永远先输出 Proposal。** 必须经过 Admission Policy 才能成为 Committed Cognitive Object。
4. **Tool Result 永远先成为 Observation。** 禁止 Tool Result 直接写入 Fact。
5. **Hypothesis 必须有当前 Episode Evidence。** 无 Evidence 只能是 Possibility。
6. **所有 Action 必须可追溯。** 至少关联 Focused Gap、Acceptance Verification、Goal Blocking 或 User Authority Need。
7. **Event History append-only。** Snapshot 可更新，但必须可追溯。
8. **Derived State 必须可重建。** Goal Relation、Pressure、Attention、Workspace、Action Readiness 均不是 Source of Truth。
9. **Benchmark 从第一版存在。** 重大架构迭代必须可与 Baseline 对比。
10. **Theory Model ≠ Runtime Module List。** 理论概念可独立，v1 工程实现允许折叠。

## 4. 总体技术栈

| 层 | 选型 |
|---|---|
| 核心语言 | Python 3.14+ |
| 依赖/环境 | uv |
| 数据模型 | Pydantic v2 |
| 架构 | Single Process + Modular Monolith |
| 风格 | Ports / Adapters |
| Episode DB | SQLite |
| DB Access | SQLAlchemy 2.x |
| Migration | Alembic |
| CLI | Typer + Rich |
| Test | pytest |
| LLM | Provider-neutral adapter |
| Scheduler | 自研 |
| Evidence / Revision / Gap / Decision | 自研 |

Async 策略：

```text
Domain = sync / pure
Application I/O boundary = async
Cognitive commit = serialized
```

v1 每个 Episode 同一时刻只允许一个 Cognitive Transaction Commit。

## 5. 总体架构

```text
Interfaces
    ↓
Application
    ↓
Domain
    ↑
Ports
    ↑
Adapters
```

Cogito Engine：

```text
CogitoEngine
│
├── CognitiveScheduler
├── CognitiveState
├── EvidenceEngine
├── RevisionEngine
├── GapEngine
├── DecisionEngine
└── Runtime
    ├── ModelProvider
    ├── ToolExecutor
    └── CognitiveStore
```

完整理论中的 Goal Relation、Pressure、Attention、Problem Frame 在 v1 可以先折叠到 State/Decision 逻辑中，不要求全部独立模块化。

## 6. 工程目录基线

```text
cogito-harness/
├─ pyproject.toml
├─ uv.lock
├─ README.md
├─ .env.example
├─ cogito.toml
├─ src/
│  └─ cogito/
│     ├─ domain/
│     │  ├─ ids.py
│     │  ├─ enums.py
│     │  ├─ models/
│     │  ├─ proposals/
│     │  └─ policies/
│     ├─ application/
│     │  ├─ scheduler.py
│     │  ├─ revision_engine.py
│     │  ├─ evidence_engine.py
│     │  ├─ gap_engine.py
│     │  ├─ decision_engine.py
│     │  ├─ role_runner.py
│     │  └─ context_router.py
│     ├─ ports/
│     │  ├─ model_provider.py
│     │  ├─ cognitive_store.py
│     │  └─ tool_executor.py
│     ├─ adapters/
│     │  ├─ llm/
│     │  ├─ sqlite/
│     │  └─ tools/
│     ├─ interfaces/cli/
│     ├─ prompts/
│     └─ config/
├─ tests/
│  ├─ unit/
│  ├─ integration/
│  └─ scenarios/
└─ benchmarks/
   ├─ cases/
   ├─ baselines/
   ├─ runner/
   └─ reports/
```

## 7. v1 Domain Model 基线

第一批正式对象：

```text
Episode
GoalContract
AcceptanceCriterion
Observation
ObservedProposition
Fact
Hypothesis
InformationGap
EvidenceLink
ActionDecision
ActionResult
CognitiveEvent
CognitiveTransaction
EpisodeState
TurnResolution
```

暂不正式实现：

```text
Anomaly
Expectation
ExplanatoryDemand
ProblemPattern
MemoryFragment
PressureState
AttentionState
```

## 8. Proposal Model

首批 Proposal：

```text
GoalInterpretationProposal
ObservedPropositionProposal
EvidenceLinkProposal
HypothesisProposal
GapProposal
ActionProposal
```

Proposal 与 Committed Object 必须是不同类型。

## 9. Cognitive State 存储

逻辑上：

```text
Episode Event Store
Cognitive Object Store
Derived Views
Transient Working Set
Long-Term Experience Store
```

v1 SQLite P0 表：

```text
episodes
goal_contracts
cognitive_events
cognitive_objects
cognitive_relations
```

如果 Replay 成本明显，再引入 snapshots。

## 10. Cognitive Transaction

```text
Observation / Evidence
↓
Draft Transaction
↓
Fact / Hypothesis / Gap Changes
↓
Consistency Validation
↓
Commit
↓
Episode Cognitive Version +1
```

版本冲突：

```text
base_version != current_version
→ reject
→ reload
→ reprocess
```

v1 不实现复杂自动 Rebase。

## 11. LLM Runtime

统一抽象：

```text
ModelProvider
```

Adapter 可逐步实现：

```text
OpenAIResponsesProvider
DeepSeekResponsesProvider
FutureAnthropicProvider
LocalModelProvider
```

RoleRunner：

```text
Context Pack
↓
Role Prompt
↓
ModelProvider
↓
Structured Output
↓
Pydantic Validation
↓
Proposal
```

v1 首批 LLM Role：

```text
Contract / User Input Interpreter
Observation Semantic Parser
Semantic Evidence Evaluator
Hypothesis Builder
Action Operationalizer
```

## 12. Tool Runtime

v1 Risk：

```text
READ_ONLY
WRITE_LOCAL
WRITE_EXTERNAL
DESTRUCTIVE
```

策略：

```text
READ_ONLY → 可配置自动执行
WRITE_LOCAL / WRITE_EXTERNAL → 默认人工确认
DESTRUCTIVE → v1 禁止自动执行
```

首批 Tool：

```text
File Read
File Search
Shell Read-only
Git Read-only
```

不优先实现 Web / Browser / Cloud Connector。

## 13. Cognitive Turn / Scheduler

Cogito 核心运行单元：

```text
Cognitive Cause
↓
Cognitive Turn
↓
Stable Cognition
↓
Turn Resolution
```

Turn Resolution：

```text
RESPOND
ACT
ASK
BLOCKED
COMPLETE
```

停止原则：

> 当进一步有意义的认知进展需要新的 Reality Evidence、外部 Action、用户 Authority 或直接 Response 时，当前 Cognitive Turn 结束。

Scheduler 概念流程：

```text
load state
↓
interpret cause
↓
create observation / contract delta
↓
parse proposition
↓
evaluate / admit evidence
↓
revision
↓
commit
↓
reload/reproject
↓
derive/focus gap
↓
decision
↓
Turn Resolution
```

Scheduler 只调度，不负责认知规则。

## 14. v1 Action Selection

P0：

```text
1. Hard Constraint Gate
2. Prefer Action directly addressing Focused Gap
3. Prefer lower-risk direct Evidence
4. Prefer lower-cost / lower-user-friction Evidence Source
```

不使用复杂数字评分。

## 15. Benchmark

每个 Case 至少包含：

```text
case_id
goal
initial_context
environment_fixture
allowed_tools
ground_truth
success_criteria
max_action_budget
```

Baseline：

```text
ReAct
Plan-and-Execute
Cogito
```

保持同模型、同 Tool Set、同 Task、同 Budget。

核心指标：

```text
Task Success
Tool Calls
Token Usage
Steps to Root Cause
Unsupported Hypothesis Rate
Repeated Low-Value Action Rate
Revision Correctness
Gap Efficiency
Cognitive Waste
Decision Trace Quality
Wrong Intervention Count
```

## 16. v1 成功标准

1. 至少稳定完成一类 Debug 场景；
2. Hypothesis 不凭空生成；
3. Evidence 能使 Hypothesis strengthen / reject；
4. Tool Action 能映射到当前 Focused Gap；
5. 新 Evidence 能改变方向；
6. 重复低价值 Action 少于 Baseline；
7. 不依赖固定全量 Plan；
8. Read-only 自动执行不绕过 Constraint；
9. Cognitive History 可追溯；
10. Domain 核心逻辑可脱离 LLM 单测。

## 17. 阶段规划

### Phase 0 — Engineering Baseline
项目骨架、Domain Objects、SQLite Store、Cognitive Transaction、FakeModelProvider、FakeToolExecutor、Core Unit Tests。

### Phase 1 — Synthetic Cogito Kernel
跑通：

```text
Observation → Proposition → Evidence → Hypothesis → Gap → Action → New Observation
```

### Phase 2 — Real Model Integration
接入真实 ModelProvider、Structured Output、RoleRunner、Prompt Boundaries。

### Phase 3 — Local Debug Harness
接入 File / Shell Read-only / Git Read-only。

### Phase 4 — Benchmark
建设 ReAct、Plan-and-Execute、Cogito 对比体系。

### Phase 5 — v1.1 Cognitive Quality
Negative Evidence、Observation Coverage、Expectation、Anomaly、Problem Frame、Structured Premises、Better Decision Readiness。

### Phase 6 — v1.2 Cognitive Control
Cognitive Pressure、Verification/Exploration Policy、Context Routing、Role Isolation、Richer Action Contract。

### Phase 7 — v2 Long-Term Learning
Experience Fragment、Memory Consolidation、Pattern Candidate、Problem Pattern Learning、Inquiry Policy Learning、Evidence Source Learning。

## 18. 明确延期技术

Kernel 未验证前不引入：

```text
LangChain / LangGraph runtime
Multi-Agent
Neo4j
Vector DB
Redis
Kafka
Celery
RabbitMQ
Kubernetes
Distributed Cognitive State
Parallel Cognitive Transactions
Long-Term Auto Memory
Automatic Pattern Promotion
GUI
```

## 19. Story 规范

每个 Story 必须明确：

```text
Goal
Scope
Out of Scope
Theory Constraints
Files / Modules
Functional Requirements
Tests
Acceptance Criteria
Prohibited Expansion
```

必须明确：

> **禁止 Codex 顺手实现未进入当前 Story 的后续认知模块。**

## 20. 推荐 Story 顺序

```text
Story 0  工程基线与最小内核骨架
Story 1  Admission Policies + Revision Engine
Story 2  Synthetic Cognitive Scheduler Loop
Story 3  Fake LLM Role Runtime + Structured Proposal Pipeline
Story 4  SQLite Transaction / Resume / Event Trace
Story 5  Real ModelProvider Adapter
Story 6  Read-only Tool Runtime
Story 7  Synthetic E2E Scenario
Story 8  Real Local Debug Scenario
Story 9  Baseline Benchmark Runner
```

## 21. 当前冻结结论

技术路线：

```text
Python 3.14+
uv
Pydantic v2
SQLite
SQLAlchemy 2
Alembic
Typer / Rich
pytest

Single Process
Modular Monolith
Ports / Adapters

Custom:
Cognitive Scheduler
Evidence Engine
Revision Engine
Gap Engine
Decision Engine
Tool Runtime
Role Runtime
Benchmark
```

v1 核心只验证：

> **Evidence-backed World Model + Gap-driven Next Action + Local Revision Loop**

任何新技术、新模块、新抽象，如果不能帮助验证这三点，应默认延期。

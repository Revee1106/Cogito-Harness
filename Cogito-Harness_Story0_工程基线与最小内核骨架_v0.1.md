# Cogito-Harness Story 0：工程基线与最小内核骨架 v0.1

> 上位约束：
>
> - `Cogito-Harness_理论基线_v0.8.md`
> - `Cogito-Harness_总体开发文档_v0.1.md`

## 1. Story 目标

建立 Cogito-Harness v1 的最小工程骨架。

本 Story **不实现完整认知循环**，只建立后续 Story 所需的稳定工程边界。

完成后必须具备：

```text
可运行 Python 工程
Domain / Application / Port / Adapter 边界
第一批 Domain Model
Proposal Model
SQLite Schema / Adapter 骨架
Cognitive Transaction 数据结构
FakeModelProvider
FakeToolExecutor
基础 CLI
核心单元测试与集成测试
```

## 2. 强制原则

1. Core 不依赖任何 Agent Framework；
2. Domain 不依赖模型 SDK；
3. Domain 不依赖 SQLAlchemy；
4. LLM 输出只能进入 Proposal；
5. Tool Result 不能直接成为 Fact；
6. Event History 采用 append-only 语义；
7. SQLite Adapter 不向 Application 泄漏 ORM Object；
8. 不接真实 LLM；
9. 不执行真实 Shell/Git 修改；
10. 不实现 Long-Term Memory；
11. 不实现完整 Pressure / Attention / Expectation / Anomaly；
12. 禁止为“以后可能需要”提前实现未列入 Scope 的复杂抽象。

## 3. 技术栈

```text
Python 3.14+
uv
Pydantic v2
SQLAlchemy 2.x
Alembic
SQLite
Typer
Rich
pytest
```

架构：

```text
single process
modular monolith
ports / adapters
```

## 4. 创建项目结构

```text
cogito-harness/
├─ pyproject.toml
├─ README.md
├─ .env.example
├─ cogito.toml
├─ src/
│  └─ cogito/
│     ├─ domain/
│     │  ├─ ids.py
│     │  ├─ enums.py
│     │  ├─ models/
│     │  │  ├─ goal.py
│     │  │  ├─ observation.py
│     │  │  ├─ fact.py
│     │  │  ├─ hypothesis.py
│     │  │  ├─ gap.py
│     │  │  ├─ evidence.py
│     │  │  ├─ action.py
│     │  │  ├─ episode.py
│     │  │  └─ event.py
│     │  ├─ proposals/
│     │  │  ├─ contract.py
│     │  │  ├─ proposition.py
│     │  │  ├─ evidence.py
│     │  │  ├─ hypothesis.py
│     │  │  ├─ gap.py
│     │  │  └─ action.py
│     │  └─ policies/
│     │     ├─ evidence.py
│     │     ├─ hypothesis.py
│     │     ├─ gap.py
│     │     ├─ action.py
│     │     └─ acceptance.py
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

## 5. Domain Base Model

创建统一 Base：

```python
class DomainModel(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )
```

要求：

- Domain Object 默认 immutable-ish；
- 禁止未知字段；
- 使用 `model_copy(update=...)` 生成新状态；
- Domain Model 不继承 SQLAlchemy ORM。

## 6. Strongly Typed IDs

`domain/ids.py` 至少定义：

```text
EpisodeId
ObservationId
PropositionId
FactId
HypothesisId
GapId
EvidenceLinkId
ActionId
EventId
TransactionId
```

v1 可使用 `typing.NewType`，实际 ID 统一生成 UUID。

## 7. Goal Domain Model

实现：

```text
GoalContract
AcceptanceCriterion
```

GoalContract 最小字段：

```text
objective
hard_constraints
acceptance_criteria
version
```

AcceptanceCriterion：

```text
id
statement
```

Acceptance 当前满足状态不进入 GoalContract。

## 8. Observation Domain Model

实现：

```text
Observation
ObservedProposition
```

Observation：

```text
id
episode_id
source
raw_content
scope?
source_ref?
observed_at
created_at
```

ObservedProposition：

```text
id
episode_id
observation_id
statement
subject?
predicate?
value?
scope?
observed_at?
status
```

必须保持：

```text
Observation ≠ Observed Proposition
```

## 9. Fact

实现：

```text
Fact
```

字段：

```text
id
episode_id
statement
subject?
predicate?
value?
scope?
valid_from?
valid_to?
evidence_refs
status
created_at
```

FactStatus：

```text
ACTIVE
SUPERSEDED
RETRACTED
```

## 10. Hypothesis

字段：

```text
id
episode_id
statement
target_problem
evidence_refs
prediction?
disconfirming_condition?
status
created_at
updated_at
```

HypothesisStatus：

```text
PLAUSIBLE
SUPPORTED
CONFIRMED
REJECTED
```

本 Story 只建 Model，不实现完整 Revision Algorithm。

## 11. InformationGap

字段：

```text
id
episode_id
question
why_it_matters
target_hypothesis_id?
source_hint?
status
created_at
resolved_at?
```

GapStatus：

```text
OPEN
FOCUSED
RESOLVED
INVALIDATED
```

## 12. EvidenceLink

实现：

```text
EvidenceLink
EvidenceLinkProposal
```

EvidenceRelation：

```text
SUPPORTS
CONTRADICTS
RESOLVES
NEUTRAL
```

CognitiveTargetType：

```text
FACT
HYPOTHESIS
GAP
```

EvidenceLink：

```text
id
episode_id
proposition_id
target_type
target_id
relation
reason
created_at
```

`NEUTRAL` 可以存在 Proposal，后续默认不要求 Commit。

## 13. Proposal Models

至少创建：

```text
GoalInterpretationProposal
ObservedPropositionProposal
EvidenceLinkProposal
HypothesisProposal
GapProposal
ActionProposal
```

规则：

- Proposal 不生成 DB ID；
- Proposal 不填 created_at；
- Proposal 不自动成为 Committed Object；
- Proposal 是 LLM / semantic runtime 边界对象。

HypothesisProposal 至少：

```text
statement
target_problem
supporting_evidence_ids
prediction?
disconfirming_condition?
```

GapProposal 至少：

```text
question
why_it_matters
target_hypothesis_id?
source_hint?
```

## 14. Action Domain Model

ActionKind：

```text
TOOL
ASK_USER
RESPOND
```

ActionRisk：

```text
READ_ONLY
WRITE_LOCAL
WRITE_EXTERNAL
DESTRUCTIVE
```

ActionDecision：

```text
id
episode_id
kind
target_gap_id?
purpose
expected_observation?
tool_name?
arguments
risk
created_at
```

ActionResult：

```text
action_id
status
raw_output?
error?
started_at
finished_at
```

必须体现：

```text
ActionResult ≠ Observation
```

## 15. Episode / EpisodeState

Episode：

```text
id
status
cognitive_version
goal_contract_version
created_at
updated_at
```

EpisodeStatus：

```text
ACTIVE
COMPLETED
BLOCKED
ABANDONED
```

EpisodeState 是 runtime materialized view：

```text
episode
goal_contract
facts
hypotheses
gaps
focused_gap_id
recent_observations
recent_actions
```

EpisodeState 不单独映射为一张 DB 表。

## 16. TurnResolution

Kind：

```text
RESPOND
ACT
ASK
BLOCKED
COMPLETE
```

字段：

```text
kind
why_stop
focused_gap_id?
action?
message?
```

## 17. CognitiveEvent

EventType 至少：

```text
EPISODE_CREATED
GOAL_CONTRACT_CREATED
GOAL_CONTRACT_REVISED
OBSERVATION_ADDED
PROPOSITION_ADDED
EVIDENCE_LINK_ADMITTED
FACT_ADDED
FACT_SUPERSEDED
FACT_RETRACTED
HYPOTHESIS_CREATED
HYPOTHESIS_STATUS_CHANGED
GAP_OPENED
GAP_FOCUSED
GAP_RESOLVED
ACTION_DECIDED
ACTION_EXECUTED
EPISODE_COMPLETED
```

Event Envelope：

```text
id
episode_id
transaction_id
sequence
event_type
cause_id?
payload
created_at
```

## 18. CognitiveTransaction

实现：

```text
CognitiveTransaction
ObjectChange
RelationChange
```

至少：

```text
id
episode_id
base_version
events
object_changes
relation_changes
```

ChangeKind：

```text
CREATE
UPDATE
```

禁止硬 DELETE，认知生命周期使用 SUPERSEDED / RETRACTED / INVALIDATED。

## 19. Port Interfaces

### ModelProvider
Provider-neutral Protocol / ABC。Story 0 不接真实 OpenAI / DeepSeek。

### CognitiveStore
至少：

```text
create_episode
load_episode_state
commit_transaction
append_goal_contract_version
```

不得返回 SQLAlchemy ORM Object。

### ToolExecutor
至少：

```text
execute(ActionDecision) -> ActionResult
```

Story 0 使用 FakeToolExecutor。

## 20. FakeModelProvider

实现可配置固定输入 → 固定 Proposal 的 Fake Provider。

要求：

- 不调用真实 API；
- 能记录 received request；
- 可用于 integration/scenario tests。

## 21. FakeToolExecutor

实现 action → 固定 ActionResult。

要求：

- 不实际运行 Shell；
- 不写文件；
- 可配置 FAILURE / SUCCESS；
- 可用于 Scenario Test。

## 22. SQLite Schema

P0 五张表：

```text
episodes
goal_contracts
cognitive_events
cognitive_objects
cognitive_relations
```

### episodes

```text
id
status
cognitive_version
goal_contract_version
created_at
updated_at
```

### goal_contracts

```text
episode_id
version
payload_json
created_at
```

主键：

```text
episode_id + version
```

### cognitive_events

```text
id
episode_id
transaction_id
sequence
event_type
cause_id
payload_json
created_at
```

索引：

```text
episode_id + sequence
transaction_id
```

必须保持 append-only。

### cognitive_objects

```text
id
episode_id
object_type
status
version
payload_json
created_at
updated_at
```

可存：

```text
OBSERVATION
PROPOSITION
FACT
HYPOTHESIS
INFORMATION_GAP
ACTION
```

### cognitive_relations

```text
id
episode_id
source_id
target_id
relation_type
payload_json
created_at
```

方向统一：

```text
source --relation--> target
```

例如：

```text
P1 --SUPPORTS--> H1
P2 --RESOLVES--> G1
```

## 23. SQLAlchemy Adapter

要求：

- ORM Model 只存在于 `adapters/sqlite/`；
- Domain Model 不继承 ORM；
- Mapper 负责 Domain ↔ Persistence；
- Session 操作只存在于 Adapter；
- Application 不出现 ORM Query。

## 24. commit_transaction()

事务内：

```text
BEGIN
check episode.cognitive_version == transaction.base_version
append events
apply object changes
apply relation changes
episode.cognitive_version += 1
update episode.updated_at
COMMIT
```

版本不一致：

```text
raise CognitiveVersionConflict
```

失败：

```text
ROLLBACK
```

## 25. Application Skeleton

创建最小骨架：

```text
CognitiveScheduler
RevisionEngine
EvidenceEngine
GapEngine
DecisionEngine
RoleRunner
ContextRouter
```

Story 0 只建立接口、职责和最小可运行逻辑，不实现完整认知算法。

## 26. CLI

至少支持：

```bash
cogito init
cogito episode create
cogito episode show <episode-id>
```

`episode create` 支持输入：

```text
goal
hard constraint
acceptance criterion
```

暂不做自然语言智能解析。

`episode show` 使用 Rich 显示：

```text
Episode
Goal
Facts
Hypotheses
Gaps
Cognitive Version
```

## 27. Config

建立：

```text
cogito.toml
.env.example
```

Story 0 至少支持：

```text
storage.sqlite_path
```

模型配置可预留，但不启用真实 Provider。

## 28. Unit Tests

至少覆盖：

### Domain
- extra field rejected；
- immutable Domain object cannot be modified in place。

### Goal
- GoalContract / AcceptanceCriterion validation。

### Observation
- Observation 与 Proposition 为不同类型。

### Hypothesis
- 合法状态；
- 非法状态拒绝。

### Gap
- GapStatus validation。

### Evidence
- Evidence target type validation。

### Transaction
- commit increments cognitive_version；
- version conflict rejects；
- failed transaction rolls back。

### Persistence
- Goal Contract version history retained；
- Event append order retained；
- Object 可重载为 Pydantic Domain Model；
- Relation 保持 source → target。

## 29. Integration Test

至少实现：

```text
create episode
↓
persist goal
↓
create transaction
↓
add Observation object
↓
append CognitiveEvent
↓
commit
↓
reload EpisodeState
↓
assert cognitive version and observation
```

全流程不调用真实 LLM / Tool。

## 30. Fake Runtime Scenario

创建最小 Scenario：

```text
Goal:
diagnose DB connectivity problem

Fact fixture:
app configured port = 3306

Fake action:
inspect listener

Fake result:
DB listens on 3307
```

Story 0 不要求自动形成 Hypothesis。

只要求：

```text
ActionDecision
→ FakeToolExecutor
→ ActionResult
→ Observation
→ Persist
```

能跑通。

## 31. README

README 至少包含：

- Cogito-Harness 简介；
- v1 当前只实现 Kernel；
- 安装；
- 测试；
- 创建 Episode；
- 当前明确不支持功能；
- 理论基线与总体开发文档位置。

## 32. Out of Scope

本 Story 禁止实现：

```text
真实 OpenAI / DeepSeek API
自动 Prompt
真实 Shell Executor
Git Executor
Web Search
Long-Term Memory
Vector DB
Graph DB
Expectation Engine
Anomaly
Explanatory Demand
Problem Pattern
Memory Learning
Cognitive Pressure
Attention Allocation
Problem Reframe
Negative Evidence
Multi-model Routing
Parallel Scheduler
Parallel Transaction
GUI
HTTP API
Agent Framework
```

## 33. Codex 禁止扩展项

Codex 不得：

1. 引入 LangChain / LangGraph；
2. 将 Domain 改成 SQLAlchemy ORM；
3. 将所有对象塞进单一 `CognitiveState` JSON；
4. 删除 Proposal / Committed Object 边界；
5. 把 FakeModelProvider 升级成真实 API；
6. 引入 Redis / PostgreSQL / Neo4j；
7. 实现未要求的 Memory；
8. 自行增加复杂 confidence score；
9. 用向量相似度替代 Domain Relation；
10. 自行堆叠大量 BaseClass / Factory / Registry。

优先：

> **简单、显式、强类型、可测试。**

## 34. Definition of Done

- [ ] `uv sync` 成功；
- [ ] `pytest` 全绿；
- [ ] Domain 不依赖 SQLAlchemy；
- [ ] Domain 不依赖任何模型 SDK；
- [ ] Proposal 与 Committed Object 分离；
- [ ] SQLite 五张表创建成功；
- [ ] Alembic migration 可执行；
- [ ] Episode 可创建、保存、重载；
- [ ] Goal Contract 版本可保存；
- [ ] Cognitive Event append-only；
- [ ] Cognitive Transaction 支持版本检查；
- [ ] Transaction 失败可 rollback；
- [ ] FakeModelProvider 可使用；
- [ ] FakeToolExecutor 可使用；
- [ ] 最小 CLI 可创建和查看 Episode；
- [ ] Fake Runtime Scenario 可完成 ActionResult → Observation → Persist；
- [ ] 没有引入 Agent Framework；
- [ ] README 已更新。

## 35. 交付物

```text
完整工程骨架
Domain / Proposal Model
Port Interfaces
SQLite Adapter
Alembic Migration
Fake Provider
Fake Tool Executor
CLI
Unit Tests
Integration Tests
README
```

## 36. 后续 Story

Story 0 完成后进入：

> **Story 1：Admission Policies + Revision Engine**

目标开始实现真正 Cogito 认知规则：

```text
Observed Proposition
→ EvidenceLink Admission
→ Fact / Hypothesis / Gap Revision
```

Story 1 才正式进入：

> **Evidence-backed cognition**

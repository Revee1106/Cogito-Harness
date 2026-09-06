# Cogito-Harness 总体开发文档 v0.2

> 本版本同步理论基线 v0.9 与 Story 1A 实际完成状态，并重新明确 Story 1B 及后续 Scheduler/Decision Policy 的边界。

---

# 1. 当前项目状态

```text
Story 0
Engineering Baseline
→ COMPLETE / FROZEN

Story 1A
Cognitive Admission Foundation
→ COMPLETE / FROZEN

Story 1B
Local Revision Engine
→ NEXT / DESIGN FROZEN FOR IMPLEMENTATION
```

当前 `main` 已包含 Story 1A。

---

# 2. 当前已落地能力

## Story 0

已完成：

- Python 3.14+
- uv
- Pydantic v2
- Modular Monolith
- Domain / Application / Ports / Adapters
- SQLite
- SQLAlchemy 2.x
- Alembic
- CognitiveTransaction
- Event / Object persistence
- CLI / Fake Runtime
- pytest 基线
- package / dependency / architecture checks

## Story 1A

已完成：

- FactProposal
- FactBasis
- SemanticEntailment
- FactAdmissionPolicy
- EvidenceAdmissionPolicy
- HypothesisAdmissionPolicy
- Draft / Reserved Cognitive Target
- Evidence relation compatibility
- Evidence deduplication
- Fact conflict diagnostic
- conflicting reliable Facts 共存
- CognitiveTransactionValidator
- material CognitiveEvent invariant
- No Evidence → No Hypothesis
- Hypothesis 初始只能 PLAUSIBLE
- `DETERMINISTIC_DERIVATION` Observation 路径暂缓

---

# 3. 当前核心工程原则

```text
interfaces
    ↓
application
    ↓
domain
    ↑
ports
    ↑
adapters
```

继续坚持：

1. Domain 不依赖 SQLAlchemy；
2. Domain 不依赖真实模型 SDK；
3. Proposal 与 committed cognition 分离；
4. ORM 与 Pydantic Domain Model 分离；
5. Application 不直接操作 ORM Session；
6. SQLite Adapter 不返回 ORM；
7. Event History append-only；
8. CognitiveTransaction 原子提交；
9. 不引入 Agent Framework；
10. Harness 决定 Admission / Revision 后果，LLM 只提出 semantic proposal。

---

# 4. Story 1B：Local Revision Engine

Story 1B 负责：

> **在认知对象已经通过 Story 1A Admission 后，判断当前 Evidence 是否足以支持有限、可追溯、局部的 Belief Revision。**

本阶段实现：

```text
Hypothesis Strengthen
Hypothesis Reject
Gap Resolve
Fact Supersede
RevisionResult
Revision Events
Atomic Local Revision
NO_MATERIAL_CHANGE
DEFERRED
```

---

# 5. Story 1B 不负责证据搜索

> **Revision Engine does not seek sufficient evidence. It only evaluates whether supplied evidence is sufficient for the requested revision.**

因此：

```text
insufficient basis
→ DEFERRED
→ stop
```

不得自动搜索、调用模型补证据、Ask User 或递归创建 Gap。

---

# 6. Story 1B 之后的路线

建议后续：

```text
Story 1B
Local Revision Engine

↓
Story 2
Synthetic Cognitive Scheduler Loop

↓
Story 3
Fake LLM Role Runtime + Structured Proposal Pipeline

↓
Story 4
SQLite Resume / Event Trace hardening

↓
Story 5
Real ModelProvider Adapter

↓
Story 6
Read-only Tool Runtime

↓
Story 7
Synthetic E2E Cognitive Scenario

↓
Story 8
Real Local Debug Scenario

↓
Story 9
Baseline Benchmark Runner
```

具体编号可在每个 Story 完成后调整。

---

# 7. Scheduler / Decision Policy 后续必须承担

以下原则已经进入理论基线，但明确不属于 Story 1B：

```text
Belief Sufficiency ≠ Action Sufficiency
Decision-Relevant Uncertainty
Minimum Sufficient Evidence
Decision Invariance
Marginal Information Value
Epistemic vs Pragmatic Action
Observation-first, not Observation-forever
Stop gathering evidence when it cannot change cognition/action
```

---

# 8. Action 方向

未来认知上区分：

## Epistemic Action

主要目标是获得信息：

```text
read
inspect
query
probe
test
ask user
```

## Pragmatic Action

主要目标是改变 Reality：

```text
modify
restart
deploy
delete
send
commit
```

低风险、高信息价值 Epistemic Action 可以在较高不确定性下执行。

---

# 9. Story 1B 与 Story 2 边界

Story 1B：

```text
Evidence / Revision Proposal
↓
Revision Policy
↓
CognitiveTransaction or Deferred/NoChange
```

Story 2：

```text
Current Cognitive State
↓
Gap / Risk / Information Value
↓
continue thinking?
observe?
act?
ask?
respond?
stop?
```

严禁 Story 1B 提前实现 Story 2 调度。

---

# 10. 长期技术债

## 10.1 Typed Source Fitness

Story 1A 仍部分依赖 `Observation.source` 字符串 marker。

真实 ModelProvider / Tool Runtime 接入前，应演进为：

```text
source_kind
acquisition_method
source_ref
```

Story 1B 不顺带重构。

## 10.2 Deterministic Derivation

未来应正式支持：

```text
admitted Fact premises
+
deterministic rule
→ Derived Fact
```

## 10.3 Evidence Invalidation / Reverse Revision

未来需要：

```text
Evidence invalidated
↓
re-evaluate dependent cognition
```

Story 1B 只保留 provenance，不实现反向传播。

---

# 11. 仍然延后的高级能力

```text
Expectation Engine
Anomaly
Explanatory Demand
Problem Frame
Negative Evidence
Coverage
Hypothesis Premise Graph
Contradiction Object lifecycle
Attention
Cognitive Pressure
Long-Term Memory
Pattern Learning
Vector DB
Graph DB
Distributed State
Multi-agent Framework
```

---

# 12. Benchmark 原则保持

未来 Benchmark 至少比较：

```text
Cogito
vs
ReAct
vs
Plan-and-Execute
```

继续关注：

- task success
- repeated actions
- unsupported hypotheses
- wrong interventions
- evidence reversal handling
- steps to root cause
- token cost
- gap efficiency
- cognitive waste
- decision trace quality

新增建议：

```text
unnecessary evidence gathering
decision invariance violations
token cost before first useful action
```

---

# 13. 当前阶段一句话

> **Story 1A 解决“什么有资格进入 Cognition”；Story 1B 解决“已有依据是否足以支持局部 Belief Revision”；后续 Scheduler 再解决“什么时候继续求证，什么时候应该行动”。**

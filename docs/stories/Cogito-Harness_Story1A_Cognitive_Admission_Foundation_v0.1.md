# Cogito-Harness Story 1A：Cognitive Admission Foundation v0.1

> 上位约束：
>
> - `docs/theory/Cogito-Harness_理论基线_v0.8.md`
> - `docs/development/Cogito-Harness_总体开发文档_v0.1.md`
> - Story 0 已正式冻结并合并 `main`

---

# 1. Story 目标

Story 1A 的目标不是实现完整 Revision Engine，而是建立 Cogito 第一套正式的：

> **Cognitive Admission Foundation**

它回答：

```text
什么 Observation / Proposition 有资格成为 Fact？
什么 Proposition 与 Cognitive Target 之间的关系有资格成为 Evidence Link？
什么解释有资格从 Possibility 晋升为 Hypothesis？
什么 Gap / Target 关系是合法的？
什么认知关系在 Transaction Commit 前必须通过一致性校验？
```

Story 1A 完成后，Cogito 应具备：

```text
Observation
→ Observed Proposition
→ Candidate Cognitive Proposal
→ Semantic Evaluation Proposal
→ Admission Policy
→ Admitted Cognitive Object / Relation
```

但暂时不实现：

```text
Admitted Evidence
→ Fact/Hypothesis/Gap 状态变化
```

该部分留给 Story 1B。

---

# 2. Story 1A 的核心原则

## 2.1 No Evidence → No Hypothesis

没有当前 Episode Evidence，只能是 Possibility，不得创建 Hypothesis。

## 2.2 Proposal ≠ Committed Cognition

必须保持：

```text
LLM / Semantic Role
↓
Proposal
↓
Admission
↓
Committed Object / Relation
```

禁止 Proposal 直接进入 World Model。

## 2.3 Evidence Relation ≠ Belief State Transition

例如：

```text
P1 SUPPORTS H1
```

不等价于：

```text
H1 → SUPPORTED
```

Story 1A 只负责 Evidence / Admission。Hypothesis 状态变化由 Story 1B 决定。

## 2.4 Support Count ≠ Belief Strength

禁止：

```text
support_count >= N
→ Hypothesis status upgrade
```

禁止任何基于简单数量计分的 Belief 更新。

## 2.5 Fact Assertion Strength 不得超过 Observation

> **Fact 的断言强度不能超过 Observation 实际能够支持的强度。**

例如：

```text
Observation:
connection refused to db:3306
```

可支持：

```text
Fact:
connection attempt to db:3306 was refused
```

但不能直接支持：

```text
Fact:
database is down
```

## 2.6 Source Reliability 不是全局分数

禁止：

```text
USER = 0.6
LOG = 0.8
SHELL = 0.9
```

应使用：

```text
Source Fitness
=
Source Type
× Claim Type
× Scope
× Time
× Acquisition Context
```

## 2.7 Reliable Fact Conflict 不静默选边

如果两个 admitted Fact 在 same entity / same property / same scope / same effective time 上不能同时成立，不得自动 latest-wins、higher-score-wins 或静默覆盖。

Story 1A 只需要检测 / 表达冲突风险。完整 Contradiction lifecycle 与 Resolution 由后续 Story 处理。

## 2.8 过时 ≠ 错误

必须保留 Fact 生命周期：

```text
ACTIVE
SUPERSEDED
RETRACTED
```

含义：

```text
ACTIVE
= 当前仍代表有效 World State

SUPERSEDED
= 曾经真实成立，但已不代表当前状态

RETRACTED
= Fact 本身建立错误，应从可信 World Model 中撤出
```

Story 1A 不实现完整 Fact Revision，但不得破坏该语义。

## 2.9 Rejected Hypothesis 不删除

Hypothesis 的历史对象必须可保留。Story 1A 不实现 Reject，但数据结构不得设计成未来必须删除 Hypothesis 才能表示失败路径。

---

# 3. 本 Story 的范围

Story 1A 实现：

```text
FactProposal
FactBasis
SemanticEntailment
FactAdmissionDecision

HypothesisProposal 修正
Draft / Reserved Cognitive Target ID
Hypothesis Admission

EvidenceLinkProposal Admission
Evidence relation compatibility
Evidence duplicate detection

Gap target relation consistency

CognitiveTransactionValidator
Draft Transaction consistency
Same-transaction object reference validation

Admission Result / Decision Trace

Unit Tests
Integration Tests
Synthetic Admission Scenarios
```

---

# 4. 明确 Out of Scope

本 Story 禁止实现：

```text
Hypothesis strengthen
Hypothesis reject
Hypothesis confirm
Fact supersede execution
Fact retract execution
Fact refine execution
Gap resolve execution
Local Revision Engine
Reverse Revision
Evidence Invalidation
Negative Evidence
Expectation
Anomaly
Explanatory Demand
Problem Frame
Contradiction lifecycle
Contradiction resolution
Cognitive Pressure
Attention
Long-Term Memory
Problem Pattern
Real LLM Provider
Real Shell / Git Executor
Vector DB
Graph DB
Agent Framework
```

尤其禁止为了“顺便完成认知闭环”而提前实现 Story 1B。

---

# 5. 新增 FactBasis

新增：

```text
FactBasis

SOURCE_REPORT
ARTIFACT_CONTENT
DIRECT_MEASUREMENT
DETERMINISTIC_DERIVATION
```

语义：

### SOURCE_REPORT
Fact 表达某个 Source 明确说了什么，例如：

```text
user reports that DB is down
```

它不等价于：

```text
DB is down
```

### ARTIFACT_CONTENT
Fact 表达某个静态或版本化 Artifact 中明确包含的内容，例如：

```text
application.yml declares port=3306
```

它不自动等价于：

```text
runtime effective port=3306
```

### DIRECT_MEASUREMENT
Fact 表达当前 Reality 被直接测得的状态，例如：

```text
mysqld listens on 3307 on host-A at T1
```

### DETERMINISTIC_DERIVATION
由已 admitted Fact 通过确定性规则推出，例如：

```text
configured_port=3306
runtime_port=3307
→ endpoint_mismatch=true
```

Story 1A 只建立类型与 Admission 基础，复杂 deterministic derivation 规则后续实现。

---

# 6. 新增 SemanticEntailment

新增：

```text
SemanticEntailment

EQUIVALENT_OR_NARROWER
STRONGER_THAN_SOURCE
AMBIGUOUS
```

语义：

### EQUIVALENT_OR_NARROWER
FactProposal 没有扩大 Proposition 的语义强度，允许继续 Admission。

### STRONGER_THAN_SOURCE
FactProposal 比 Proposition 表达更强，必须 Reject。

### AMBIGUOUS
当前无法可靠判断是否被 Proposition 支持，默认 DEFER，不得强行变 Fact。

---

# 7. 新增 FactAdmissionDecision

新增：

```text
FactAdmissionDecision

ADMIT
DEFER
REJECT
```

语义：

```text
ADMIT
= 当前 Evidence / Scope / Time / Basis 足够支持 Fact

DEFER
= Candidate 可能成立，但当前认知边界不足

REJECT
= Candidate 明显超出 Evidence 或违反认知约束
```

Story 1A 必须允许：

> **不知道，所以暂不下结论。**

---

# 8. 新增 FactProposal

建议最小结构：

```text
FactProposal

proposition_id
statement

subject?
predicate?
value?

scope?
valid_from?
valid_to?

basis
semantic_entailment
```

注意：

- 不生成 committed object ID；
- 不填 `created_at`；
- 不自动生成 EvidenceLink；
- 不允许加入 Proposition 中不存在的新因果解释。

---

# 9. Fact Admission Policy

新增：

```text
FactAdmissionPolicy
```

至少检查：

1. Proposition 存在；
2. Proposition 属于当前 Episode；
3. Proposition 状态为 ACTIVE；
4. SemanticEntailment：
   - `STRONGER_THAN_SOURCE → REJECT`
   - `AMBIGUOUS → DEFER`
   - `EQUIVALENT_OR_NARROWER → continue`
5. Scope 不得无依据扩大；
6. Temporal Scope 不得无依据扩大；
7. FactBasis 与 Source Fitness 相容；
8. 因果解释不得通过 Fact Admission 偷渡。

明显不匹配时 REJECT，不确定时 DEFER。

---

# 10. Fact Admission 结果

若 Fact 被 ADMIT，必须形成：

```text
reserved Fact ID
EvidenceLink
Fact
```

关系：

```text
ObservedProposition
--SUPPORTS-->
Fact
```

`Fact.evidence_refs` 必须指向正式 admitted `EvidenceLinkId`。

Fact 与 EvidenceLink 必须能够在同一 CognitiveTransaction 中创建。

---

# 11. 修正 HypothesisProposal

HypothesisProposal 不应直接依赖已存在 EvidenceLink ID 才能创建新 Hypothesis。

修改为：

```text
HypothesisProposal

statement
target_problem

supporting_proposition_ids

prediction?
disconfirming_condition?
```

语义：

> Hypothesis Builder 只能指出哪些 Proposition 可能与候选解释相关，不能自己声明这些 Proposition 已构成 admitted Evidence。

---

# 12. Draft / Reserved Cognitive Target

Story 1A 必须支持：

> **在 Transaction Commit 前，为 Candidate Fact / Hypothesis 预分配稳定 ID。**

流程：

```text
HypothesisProposal
↓
reserve H-id
↓
Draft H Target
↓
Evidence Evaluation
↓
Evidence Admission
↓
Hypothesis Admission
↓
same transaction commit
```

Reserved ID：

- 在 Transaction 中可被 Relation Target 引用；
- Commit 前不属于正式 cognition；
- Transaction 失败后不得留下正式 object / relation；
- 不要求 ID 回收。

---

# 13. Hypothesis Admission Policy

新增：

```text
HypothesisAdmissionPolicy
```

新 Hypothesis 创建至少要求：

1. HypothesisProposal 存在；
2. Proposal 属于当前 Episode；
3. `supporting_proposition_ids` 至少一个；
4. 对 reserved H target 至少有一个 admitted `SUPPORTS EvidenceLink`；
5. EvidenceLink source Proposition 属于当前 Episode；
6. statement / target_problem 非空；
7. 至少定义 `prediction` 或 `disconfirming_condition`；
8. 初始 status 固定为 `PLAUSIBLE`；
9. Story 1A 不允许创建 `SUPPORTED / CONFIRMED / REJECTED`。

---

# 14. Hypothesis Builder 与 Evidence Evaluator 防火墙

必须保持：

```text
Hypothesis Builder
→ HypothesisProposal
```

只输出候选 Proposition。

随后：

```text
Evidence Evaluator
→ EvidenceLinkProposal
```

Harness Admission 决定是否形成：

```text
P --SUPPORTS--> H
```

---

# 15. EvidenceLinkProposal Admission

新增 / 完善：

```text
EvidenceAdmissionPolicy
```

Story 1A 支持：

```text
SUPPORTS
CONTRADICTS
RESOLVES
NEUTRAL
```

`NEUTRAL` 永远不 Commit。

---

# 16. Evidence Relation Compatibility

冻结为：

| Target Type | Allowed committed relation |
|---|---|
| FACT | SUPPORTS, CONTRADICTS |
| HYPOTHESIS | SUPPORTS, CONTRADICTS |
| GAP | RESOLVES |

非法组合必须 Reject。

---

# 17. Evidence Admission 基础检查

至少包括：

1. Source Proposition 存在于 Current State 或 Current Transaction CREATE set；
2. Target 存在于 Current State 或 Current Transaction Draft/CREATE set；
3. Source / Target / Transaction 属于同一 Episode；
4. `target_type` 必须与真实 Domain Object 类型一致；
5. Relation Compatibility 合法。

---

# 18. Evidence Deduplication

同一：

```text
proposition_id
target_id
relation
```

如果已经存在 active committed EvidenceLink：

```text
→ duplicate
→ NO_NEW_ADMISSION
```

不得再次 Commit。

---

# 19. 同一 Proposition × Target 的 Active Material Relation

Story 1A 采用保守规则：

> 同一 `Proposition × Target` 不允许同时存在多个互斥 active material relation。

例如：

```text
P1 SUPPORTS H1
P1 CONTRADICTS H1
```

不能同时 active。

Story 1A 不实现 Evidence Invalidation / Replacement；出现冲突时返回明确 admission conflict。

---

# 20. Gap Relation Consistency

Story 1A 不实现 Gap Resolution，只建立 Relation Admission 规则。

Gap 只允许：

```text
P --RESOLVES--> G
```

Story 1A 只 Commit admitted `RESOLVES EvidenceLink`。

真正：

```text
G → RESOLVED
```

由 Story 1B 完成。

---

# 21. 新增 CognitiveTransactionValidator

Story 0 SQLite Store 负责 persistence consistency。

Story 1A 新增：

```text
CognitiveTransactionValidator
```

负责 cognitive consistency，至少检查：

1. Relation source / target 存在于 Current State 或 Current Transaction CREATE set；
2. 所有 object / relation / event 属于当前 Episode；
3. Relation target_type 与真实对象一致；
4. Evidence relation 与 target type compatibility 合法；
5. 新 Fact 的 `evidence_refs` 必须引用 targeting itself 的 admitted EvidenceLink；
6. 新 Hypothesis 的 `evidence_refs` 必须至少包含一个 targeting itself 的 SUPPORTS relation；
7. 允许 Relation 指向同 Transaction reserved Fact/Hypothesis；
8. Commit 时 corresponding CREATE 必须存在；
9. 同一个 object 不允许互斥 change。

---

# 22. AdmissionResult

建议建立统一返回：

```text
AdmissionResult[T]

decision:
ADMIT
DEFER
REJECT
NO_NEW_ADMISSION

value?
reasons[]
```

要求：

- 可审计；
- 不依赖隐藏 chain-of-thought；
- 至少保留结构化 reason code / public reason。

---

# 23. Reason Codes

建议至少：

```text
SOURCE_NOT_FOUND
TARGET_NOT_FOUND
EPISODE_MISMATCH
TARGET_TYPE_MISMATCH
RELATION_NOT_ALLOWED
DUPLICATE_EVIDENCE
RELATION_CONFLICT
PROPOSITION_INACTIVE
CLAIM_TOO_STRONG
SCOPE_EXPANDED
TEMPORAL_SCOPE_INVALID
SOURCE_FITNESS_INSUFFICIENT
SEMANTIC_AMBIGUITY
NO_SUPPORTING_EVIDENCE
MISSING_TESTABLE_EXPECTATION
```

不要一开始设计复杂层级。

---

# 24. Fact Conflict Detection Boundary

Story 1A 不实现完整 Contradiction Object。

但 Fact Admission / Transaction Validator 至少不得静默覆盖已有 ACTIVE Fact。

若新 Fact 与 existing ACTIVE Fact 在：

```text
same entity
same property
same scope
overlapping effective time
```

且 value incompatible：

必须产生 conflict result / diagnostic。

不得：

```text
自动覆盖
自动 supersede
自动 retract
自动选择 winner
```

完整 Scope Refinement / Temporal Supersession / Contradiction / User Ask / Evidence Resolution 留给后续 Story。

---

# 25. Fact 生命周期保持

保留：

```text
ACTIVE
SUPERSEDED
RETRACTED
```

Story 1A 新 Fact 只能创建为 `ACTIVE`。

不得自动执行：

```text
ACTIVE → SUPERSEDED
ACTIVE → RETRACTED
```

---

# 26. Hypothesis 生命周期保持

Story 1A 新建 Hypothesis 只能：

```text
PLAUSIBLE
```

不得产生：

```text
SUPPORTED
CONFIRMED
REJECTED
```

并必须保留 Evidence history 能力，为 Story 1B 留出 revision provenance。

---

# 27. Event 处理原则

Story 1A 只有 material committed cognition 必须进入 persistent Cognitive Event Log。

DEFER / REJECT 默认优先进入：

```text
AdmissionResult
Decision Trace
Test Diagnostics
```

避免 Event Explosion。

---

# 28. Application 层建议组件

可新增 / 完善：

```text
FactAdmissionService
HypothesisAdmissionService
EvidenceAdmissionService
CognitiveTransactionValidator
DraftTargetFactory / ID Reservation helper
```

避免制造大量 Factory / Registry。

---

# 29. 不实现真实 LLM

Story 1A 全部 Admission Policy 必须能够在：

```text
无 OpenAI
无 DeepSeek
```

情况下单元测试。

SemanticEntailment / EvidenceLinkProposal 直接由 fixture / FakeModelProvider 提供即可。

目标：

> **Cogito 的 Admission Law 在模型不存在时仍然是确定、可测试的。**

---

# 30. Unit Tests — Fact Admission

至少覆盖：

```text
Fact proposal equivalent/narrower → ADMIT
Fact stronger than proposition → REJECT
Ambiguous entailment → DEFER
Inactive proposition → REJECT
Cross-episode proposition → REJECT
Scope expansion → REJECT/DEFER
Temporal overreach → REJECT/DEFER
SOURCE_REPORT compatible with user report
ARTIFACT_CONTENT compatible with file/config content
DIRECT_MEASUREMENT compatible with runtime observation
Fact evidence_refs contains EvidenceLinkId
Fact and EvidenceLink may commit atomically
```

---

# 31. Unit Tests — Hypothesis Admission

至少覆盖：

```text
no supporting proposition → REJECT
no admitted SUPPORTS EvidenceLink → REJECT
cross-episode evidence → REJECT
missing prediction and disconfirming_condition → REJECT
valid evidence-backed proposal → create PLAUSIBLE Hypothesis
new Hypothesis cannot be SUPPORTED
new Hypothesis cannot be CONFIRMED
new Hypothesis cannot be REJECTED
Hypothesis Builder candidate proposition does not automatically become Evidence
```

---

# 32. Unit Tests — Evidence Admission

至少覆盖：

```text
P SUPPORTS Fact → allowed
P CONTRADICTS Fact → allowed
P SUPPORTS Hypothesis → allowed
P CONTRADICTS Hypothesis → allowed
P RESOLVES Gap → allowed

P SUPPORTS Gap → rejected
P RESOLVES Hypothesis → rejected

NEUTRAL → not committed

duplicate same P/Target/Relation → no new admission
same P/Target SUPPORTS + CONTRADICTS → conflict
target type mismatch → reject
missing source → reject
missing target → reject
same-transaction draft target → allowed
cross-episode → reject
```

---

# 33. Unit Tests — CognitiveTransactionValidator

至少覆盖：

```text
relation may target object created in same transaction
missing draft object → reject
Fact evidence_refs must point to relation targeting itself
Hypothesis evidence_refs must point to SUPPORTS relation targeting itself
wrong target type → reject
mixed episode transaction → reject
conflicting object changes → reject
```

---

# 34. Integration Scenario A — Fact Admission

Fixture：

```text
Observation:
shell result on host-A:
mysqld LISTEN 0.0.0.0:3307

Proposition:
mysqld listens on 3307 on host-A at T1
```

FactProposal：

```text
mysqld runtime listener port = 3307
basis = DIRECT_MEASUREMENT
semantic_entailment = EQUIVALENT_OR_NARROWER
```

预期：

```text
Fact Admission ADMIT

create E1:
P1 SUPPORTS F1

create F1:
ACTIVE
evidence_refs=(E1,)

same CognitiveTransaction
commit success
```

---

# 35. Integration Scenario B — Claim Strength Rejection

Observation：

```text
connection to db:3306 returned connection refused
```

FactProposal：

```text
database is down
```

预期：

```text
SemanticEntailment = STRONGER_THAN_SOURCE
Fact Admission = REJECT
no Fact
no EvidenceLink
no cognitive_version increase
```

不得创建 empty CognitiveTransaction。

---

# 36. Integration Scenario C — Hypothesis Admission

已有：

```text
P1:
application connects to port 3306

P2:
database listens on port 3307
```

HypothesisProposal：

```text
endpoint mismatch contributes to DB connectivity failure

supporting_proposition_ids:
P1, P2

prediction:
using the actual listener endpoint should remove the connection-refused symptom
```

Evidence Evaluator Fixture：

```text
P1 SUPPORTS Draft-H1
P2 SUPPORTS Draft-H1
```

预期：

```text
Evidence Admission succeeds
Hypothesis Admission succeeds

H1 status = PLAUSIBLE

H1 evidence_refs point to admitted EvidenceLinks
all committed atomically
```

不得自动升级 H1 → SUPPORTED。

---

# 37. Integration Scenario D — Fact Conflict

Current:

```text
F1:
runtime_port = 3306
scope=host-A
ACTIVE
```

New Candidate:

```text
F2:
runtime_port = 3307
scope=host-A
same effective time
```

预期：

```text
detect conflict
do not silently overwrite F1
do not auto-supersede
do not auto-retract
do not choose winner
```

Contradiction Object / Resolution Gap 不属于 Story 1A。

---

# 38. Definition of Done

Story 1A 完成必须满足：

- [ ] `FactBasis` 已实现；
- [ ] `SemanticEntailment` 已实现；
- [ ] `FactAdmissionDecision` 已实现；
- [ ] `FactProposal` 已实现；
- [ ] `FactAdmissionPolicy` 已实现；
- [ ] `HypothesisProposal` 已改为引用 candidate proposition；
- [ ] reserved / draft cognitive target ID 机制已实现；
- [ ] `HypothesisAdmissionPolicy` 已实现；
- [ ] 新 Hypothesis 只能进入 `PLAUSIBLE`；
- [ ] 无 Episode Evidence 无法创建 Hypothesis；
- [ ] `EvidenceAdmissionPolicy` 已实现；
- [ ] Evidence relation compatibility 已实现；
- [ ] NEUTRAL 不 Commit；
- [ ] Evidence dedup 已实现；
- [ ] same Proposition × Target active relation conflict 可检测；
- [ ] `CognitiveTransactionValidator` 已实现；
- [ ] same-transaction object/relation references 可验证；
- [ ] Fact / Hypothesis evidence refs 一致性可验证；
- [ ] cross-episode cognition 被拒绝；
- [ ] Fact conflict 不会被静默覆盖；
- [ ] 未实现 Story 1B Revision；
- [ ] 全量 pytest 通过；
- [ ] coverage 不低于当前项目门槛；
- [ ] 无真实 LLM / Agent Framework 新增依赖；
- [ ] Story 0 已有能力无回归。

---

# 39. Story 1A 验收重点

优先关注：

```text
1. LLM 是否仍只能提出 Proposal；
2. Fact 是否会偷渡比 Observation 更强的语义；
3. Source / Scope / Time 是否被真正约束；
4. Hypothesis 是否可能无 Evidence 创建；
5. Hypothesis Builder 是否绕过 Evidence Evaluator；
6. EvidenceLink 是否能指向同 Transaction Draft Target；
7. Relation 是否可能 target 错类型；
8. Duplicate Evidence 是否制造虚假认知；
9. Fact conflict 是否被静默覆盖；
10. Admission 无 material change 时是否错误增加 cognitive_version。
```

---

# 40. Story 1A 完成后的下一步

Story 1A 完成并验收通过后，再设计：

> **Story 1B：Local Revision Engine**

Story 1B 才实现：

```text
Hypothesis PLAUSIBLE → SUPPORTED
Hypothesis → REJECTED
Gap → RESOLVED
Fact revision consequences
Atomic multi-object local revision
RevisionResult
NO_MATERIAL_CHANGE
Revision Event
```

Story 1B 的规则必须基于 Story 1A 的实际实现与验收结果再冻结，不提前写死。

---

# 41. Story 1A 一句话定义

> **Story 1A 不负责“Cogito 应该改变什么 Belief”，只负责“什么认知对象和认知关系有资格进入 Cogito”。**

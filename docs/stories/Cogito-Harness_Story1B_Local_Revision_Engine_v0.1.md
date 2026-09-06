# Cogito-Harness Story 1B：Local Revision Engine v0.1

> 上位约束：
>
> - `docs/theory/Cogito-Harness_理论基线_v0.9.md`
> - `docs/development/Cogito-Harness_总体开发文档_v0.2.md`
> - Story 0 已冻结
> - Story 1A 已冻结并合并 `main`

---

# 1. Story 目标

Story 1B 实现：

> **Local Revision Engine**

它回答：

```text
已经 Admission 的 Evidence
是否足以支持某个正式 Cognitive Object 的局部变化？
```

Story 1B 不负责寻找更多 Evidence。

---

# 2. 核心原则

```text
1. Evidence Relation != Belief Revision
2. Support Count != Belief Strength
3. CONTRADICTS != automatic REJECT
4. REJECT requires explicit falsification basis
5. Rejected Hypothesis keeps prior supporting Evidence
6. RESOLVES Evidence may close Gap
7. Gap resolution does not select next Gap
8. Fact conflict != automatic supersession
9. Supersession requires temporal succession basis
10. Revision only mutates explicit local targets
11. One cognitive cause → one atomic revision transaction
12. No Material Change → no cognitive_version increase
13. Insufficient basis → DEFERRED, not recursive evidence seeking
```

---

# 3. 实现范围

```text
HypothesisStrengthenProposal
HypothesisRejectProposal
HypothesisSupportBasis
RejectionBasis

FactSupersedeProposal
TemporalSuccessionBasis

Gap resolution policy

RevisionStatus
RevisionResult
RevisionBatch
LocalRevisionEngine

Revision Events
CognitiveTransaction validation extension

Unit Tests
Integration Tests
Synthetic Revision Scenarios
```

---

# 4. Out of Scope

```text
Hypothesis CONFIRMED
STRONGLY_SUPPORTED
Hypothesis reopen
Hypothesis split/merge/refine

Fact RETRACT execution
Fact REFINE execution

Evidence Invalidation
Reverse Revision
Negative Evidence
Prediction-failure rejection

Contradiction Object lifecycle
Contradiction Resolution
Ask User conflict resolution

Expectation
Anomaly
Explanatory Demand
Problem Frame

Decision Invariance runtime
Information Value ranking
Action selection
Scheduler stopping
Attention
Cognitive Pressure

Long-Term Memory
Pattern Learning

DerivedFact Engine
Premise Graph
Dependency Graph
Recursive propagation

Real LLM
Real Tool Runtime
Agent Framework
```

---

# 5. HypothesisSupportBasis

```text
DIRECT_OBSERVATION
INDEPENDENT_CORROBORATION
DISCRIMINATIVE_EVIDENCE
PREDICTION_CONSISTENT
```

---

# 6. SUPPORTED 定义

> **SUPPORTED 表示 Hypothesis 不仅拥有当前 Episode Evidence，而且至少获得了一次具有实质解释价值的结构性支持，使其足以被当前推理作为值得依赖的候选解释。**

```text
PLAUSIBLE
= 有依据，值得考虑

SUPPORTED
= 获得结构性强化，值得依赖

SUPPORTED != confirmed true
```

---

# 7. HypothesisStrengthenProposal

```text
HypothesisStrengthenProposal

hypothesis_id
evidence_link_ids
support_basis
reason
```

必须：

- H 存在；
- same Episode；
- status 为 `PLAUSIBLE` 或 `SUPPORTED`；
- EvidenceLinks 存在；
- target = 当前 H；
- relation = `SUPPORTS`；
- source Proposition ACTIVE；
- support_basis 合法；
- reason 非空；
- 相同 Evidence 不得重复产生相同 strengthen effect。

---

# 8. Support Basis Preconditions

## DIRECT_OBSERVATION

Evidence 可追溯到直接 Reality Observation / Direct Measurement 语义。

## INDEPENDENT_CORROBORATION

至少：

```text
>= 2 EvidenceLinks
different proposition_id
```

若 provenance 可支持，进一步要求不同 observation/source path。

## DISCRIMINATIVE_EVIDENCE

由 Semantic Revision Role 提议。

Harness 至少检查 target、active Evidence 与 reason。

## PREDICTION_CONSISTENT

要求：

```text
Hypothesis.prediction is not None
```

不得因此进入 CONFIRMED。

---

# 9. Strengthen 行为

```text
PLAUSIBLE
→ SUPPORTED
```

如果 H 已 SUPPORTED 且出现新的未消费 structural support：

```text
status remains SUPPORTED
revision provenance appended
```

这是 Material Change。

相同 Evidence 重复 strengthen：

```text
NO_MATERIAL_CHANGE
```

---

# 10. RejectionBasis

```text
DIRECT_CONTRADICTION
DISCONFIRMING_CONDITION_MET
```

禁止：

```text
BETTER_COMPETITOR
LOW_CONFIDENCE
INSUFFICIENT_SUPPORT
PREDICTION_FAILURE
```

直接作为 Reject basis。

---

# 11. HypothesisRejectProposal

```text
HypothesisRejectProposal

hypothesis_id
evidence_link_ids
rejection_basis
reason
```

要求：

- H 存在；
- same Episode；
- status `PLAUSIBLE` 或 `SUPPORTED`；
- 至少一个 EvidenceLink；
- relation = `CONTRADICTS`；
- target = 当前 H；
- source Proposition ACTIVE；
- rejection_basis 合法；
- reason 非空。

---

# 12. DIRECT_CONTRADICTION

`CONTRADICTS` 本身不自动 Reject。

建议最小 semantic directness：

```text
DIRECT
NOT_DIRECT
AMBIGUOUS
```

处理：

```text
DIRECT → continue
NOT_DIRECT → reject revision proposal
AMBIGUOUS → DEFERRED
```

禁止 confidence score。

---

# 13. DISCONFIRMING_CONDITION_MET

要求：

```text
H.disconfirming_condition is not None
```

并且 condition 必须早于触发 Evidence 已存在于 committed cognition。

Story 1B 利用现有 cognitive version / event provenance 做最小历史合法性校验。

---

# 14. Reject 行为

```text
PLAUSIBLE / SUPPORTED
→ REJECTED
```

必须保留：

```text
all prior supporting Evidence
contradicting Evidence
rejection basis
rejected-by Evidence refs
revision history
```

Story 1B 不支持 reopening。

重复 Reject：

```text
NO_MATERIAL_CHANGE
```

---

# 15. Gap Resolution

Story 1A 已支持：

```text
P --RESOLVES--> G
```

Story 1B 允许：

```text
OPEN / FOCUSED
→ RESOLVED
```

前提：

- Gap 存在；
- same Episode；
- admitted EvidenceLink 存在；
- relation = RESOLVES；
- target = 当前 Gap；
- source Proposition ACTIVE。

不新增 GapRevisionProposal。

---

# 16. Gap Resolution 边界

```text
partial answer
→ must not be RESOLVES
→ Gap remains open/focused
```

Gap 已 RESOLVED 后重复 resolution：

```text
NO_MATERIAL_CHANGE
```

不得自动选择下一 Gap、完成 Goal 或选择 Action。

---

# 17. TemporalSuccessionBasis

```text
LATER_DIRECT_OBSERVATION
EXPLICIT_STATE_TRANSITION
VERSIONED_ARTIFACT_SUCCESSION
```

---

# 18. FactSupersedeProposal

```text
FactSupersedeProposal

fact_id
replacement_fact_id
temporal_basis
basis_evidence_ids
reason
```

`replacement_fact_id` 必须存在。

---

# 19. Fact Supersede 基础条件

至少要求：

```text
old Fact exists
replacement Fact exists
same Episode

old.status == ACTIVE
replacement.status == ACTIVE

same entity/subject
same property/predicate
compatible scope
semantic layer compatible

basis evidence exists
basis evidence source Proposition ACTIVE
reason non-empty
```

---

# 20. LATER_DIRECT_OBSERVATION

至少要求：

```text
replacement Fact traceable to DIRECT_MEASUREMENT
replacement world time > old world time
```

禁止使用 `created_at` 作为 temporal succession。

不足时：

```text
DEFERRED
TEMPORAL_BASIS_INSUFFICIENT
```

---

# 21. EXPLICIT_STATE_TRANSITION

basis Evidence 明确支持：

```text
old state
→ transition
→ new state
```

Harness 验证 Evidence 存在、same Episode、source ACTIVE。

---

# 22. VERSIONED_ARTIFACT_SUCCESSION

`VERSIONED_ARTIFACT_SUCCESSION` 是合法的 `TemporalSuccessionBasis`。Story 1B 保留其 enum、Proposal shape、Policy branch 与 reason code。

> **Story 1B 冻结说明：保留能力形状，但当前 material revision 暂不可用。**

当前 Domain 尚无可靠的 admitted / committed / traceable artifact-version provenance contract，无法据此证明 version values、version ordering 与 artifact identity succession。因此，通过基础目标与 Evidence 校验后，当前冻结行为为：

```text
VERSIONED_ARTIFACT_SUCCESSION
→ DEFERRED
→ VERSION_PROVENANCE_INSUFFICIENT
→ transaction = None
→ no cognitive_version increase
```

不得仅凭以下输入证明 artifact version succession：

```text
Proposal.old_version
Proposal.replacement_version
source_ref
filename
reason text
created_at
```

这不是删除该 Basis，也不是认定其理论上非法。未来启用 material Fact Supersession 必须先有 committed、可追溯的 artifact-version provenance contract，并能证明：

```text
same/compatible artifact identity
explicit version ordering
semantic layer compatible
```

该未来启用能力不属于当前 Story 1B runtime；本 Story 不主动搜索或补造 version provenance。

新版 Artifact 不自动证明 Runtime State 已改变。

---

# 23. Conflict 不自动 Supersede

若：

```text
F1 ACTIVE
F2 ACTIVE
incompatible
```

但没有充分 temporal basis：

```text
keep both ACTIVE
RevisionResult = DEFERRED
reason = CONFLICT_UNRESOLVED / TEMPORAL_BASIS_INSUFFICIENT
```

Revision Engine 到此结束。

---

# 24. RevisionStatus

```text
MATERIAL_CHANGE
NO_MATERIAL_CHANGE
DEFERRED
```

---

# 25. RevisionResult

```text
RevisionResult

status
transaction?
reason_codes[]
public_reasons[]
affected_object_ids[]
```

---

# 26. MATERIAL_CHANGE

包括：

```text
PLAUSIBLE → SUPPORTED
SUPPORTED + new structural revision provenance
PLAUSIBLE/SUPPORTED → REJECTED
OPEN/FOCUSED → RESOLVED
ACTIVE → SUPERSEDED
```

必须产生 CognitiveTransaction。

---

# 27. NO_MATERIAL_CHANGE

例如：

```text
same evidence repeatedly strengthens same H
same rejected H rejected again
resolved Gap resolved again
superseded Fact superseded again
```

要求：

```text
transaction = None
no cognitive_version increase
```

---

# 28. DEFERRED

表示 Revision 方向可能合理，但依据不足。

要求：

```text
transaction = None
```

Revision Engine 不主动找更多 Evidence。

---

# 29. RevisionBatch

```text
RevisionBatch

hypothesis_strengthen_proposals[]
hypothesis_reject_proposals[]
gap_resolution_evidence_ids[]
fact_supersede_proposals[]
```

同一 Cognitive Cause 的直接 Revision 可放入一个 batch。

---

# 30. LocalRevisionEngine

```text
LocalRevisionEngine.revise(
    episode_state,
    revision_batch,
    base_version
) -> RevisionResult
```

职责：

```text
validate
↓
evaluate revision policies
↓
build explicit local changes
↓
build revision events
↓
return RevisionResult
```

Engine 不直接 commit DB。

---

# 31. Local Boundary

> **只允许修改 Revision input 明确指定的 target object。**

禁止递归扫描和传播。

---

# 32. Atomic Revision

同一 Cognitive Cause 的：

```text
strengthen H1
resolve G2
supersede F4
```

应形成一个 CognitiveTransaction。

---

# 33. Revision Events

新增：

```text
HYPOTHESIS_STRENGTHENED
HYPOTHESIS_REJECTED
GAP_RESOLVED
FACT_SUPERSEDED
```

至少记录：

```text
target object id
previous status
new status
basis evidence ids
basis
public reason
```

---

# 34. Event 与 Evidence 边界

```text
Evidence Admission
!=
Revision Event
```

只有通过正式 Revision Policy 并产生 material change 时写 Revision Event。

---

# 35. Story 1B 不追求证据

> **Revision Engine does not seek sufficient evidence. It only evaluates whether supplied evidence is sufficient for the requested revision.**

```text
DEFERRED
→ return
```

禁止内部 model call、tool call、search、ask user、recursive retry。

---

# 36. Unit Tests — Hypothesis Strengthen

至少覆盖：

```text
PLAUSIBLE + valid DIRECT_OBSERVATION → SUPPORTED
SUPPORTED + new valid support → material provenance change
duplicate same Evidence → NO_MATERIAL_CHANGE
target mismatch
CONTRADICTS cannot strengthen
inactive Proposition cannot strengthen
cross-episode cannot strengthen
INDEPENDENT_CORROBORATION requires >=2 distinct propositions
PREDICTION_CONSISTENT requires prediction
no evidence-count automatic strengthen
```

---

# 37. Unit Tests — Hypothesis Reject

至少覆盖：

```text
CONTRADICTS alone does not auto reject
valid DIRECT_CONTRADICTION → REJECTED
AMBIGUOUS directness → DEFERRED
valid DISCONFIRMING_CONDITION_MET → REJECTED
missing disconfirming condition
condition created after evidence
better competitor does not reject
lack of support does not reject
prediction failure alone does not reject
rejected H preserves prior Evidence
duplicate reject → NO_MATERIAL_CHANGE
```

---

# 38. Unit Tests — Gap Resolution

至少：

```text
OPEN + RESOLVES → RESOLVED
FOCUSED + RESOLVES → RESOLVED
non-RESOLVES does not resolve
inactive source does not resolve
wrong target does not resolve
already RESOLVED → NO_MATERIAL_CHANGE
does not select next Gap
```

---

# 39. Unit Tests — Fact Supersede

至少：

```text
later direct observation → supersede
created_at alone cannot supersede
ambiguous world time → DEFERRED
explicit transition → supersede
proposal-only version succession → DEFERRED + VERSION_PROVENANCE_INSUFFICIENT
missing committed version provenance → no transaction / no cognitive_version increase
new artifact version cannot supersede runtime Fact without runtime evidence
plain conflict → no supersede
conflict without temporal basis → DEFERRED
old Fact preserved as SUPERSEDED
replacement remains ACTIVE
```

未来 admitted version provenance 可能允许 material supersession，但不属于当前 Story 1B runtime 的成功用例。

---

# 40. Unit Tests — RevisionResult / Batch

至少：

```text
one explicit revision → one transaction
multiple revisions in one batch → one atomic transaction
no changes → NO_MATERIAL_CHANGE + no transaction
insufficient basis → DEFERRED + no transaction
revision transaction contains correct events
event IDs match changes
cross-episode batch invalid
base version preserved
```

---

# 41. Integration Scenario A — Strengthen

```text
H1 = PLAUSIBLE
E1 SUPPORTS H1
basis = DIRECT_OBSERVATION
↓
H1 = SUPPORTED
HYPOTHESIS_STRENGTHENED
```

---

# 42. Integration Scenario B — Reject

```text
H1 = SUPPORTED
E1/E2 SUPPORTS H1
E3 CONTRADICTS H1

RejectProposal:
basis = DIRECT_CONTRADICTION
semantic directness = DIRECT
↓
H1 = REJECTED
all E1/E2/E3 preserved
HYPOTHESIS_REJECTED
```

---

# 43. Integration Scenario C — Resolve Gap

```text
G1 = FOCUSED
E7 RESOLVES G1
↓
G1 = RESOLVED
GAP_RESOLVED

no next Gap selected
```

---

# 44. Integration Scenario D — Supersede Fact

```text
F1:
runtime_port=3306 @ T1
ACTIVE

F2:
runtime_port=3307 @ T2
ACTIVE

T2 > T1
basis = LATER_DIRECT_OBSERVATION
↓
F1 = SUPERSEDED
F2 = ACTIVE
FACT_SUPERSEDED
```

---

# 45. Integration Scenario E — Unresolved Conflict

```text
F1 ACTIVE port=3306
F2 ACTIVE port=3307
same scope
temporal ordering ambiguous
↓
RevisionResult = DEFERRED
both remain ACTIVE
no transaction
no cognitive_version increase
```

---

# 46. Definition of Done

- [ ] HypothesisSupportBasis 实现；
- [ ] HypothesisStrengthenProposal / Policy 实现；
- [ ] 无 evidence-count 自动 strengthen；
- [ ] RejectionBasis 实现；
- [ ] HypothesisRejectProposal / Policy 实现；
- [ ] CONTRADICTS 不自动 Reject；
- [ ] rejected H 保留旧 Evidence；
- [ ] Gap Resolution 实现；
- [ ] Gap Resolve 不选择下一个 Gap；
- [ ] TemporalSuccessionBasis 实现；
- [ ] VERSIONED_ARTIFACT_SUCCESSION 保留合法 Basis shape，当前不产生 material revision；
- [ ] 缺少 committed version provenance 时返回 DEFERRED；
- [ ] reason = VERSION_PROVENANCE_INSUFFICIENT；
- [ ] 该版本修订路径不创建 transaction、不增加 cognitive_version；
- [ ] FactSupersedeProposal / Policy 实现；
- [ ] Fact conflict 不自动 Supersede；
- [ ] world time 与 cognitive created_at 分离；
- [ ] RevisionStatus / RevisionResult 实现；
- [ ] RevisionBatch 实现；
- [ ] LocalRevisionEngine 实现；
- [ ] explicit-local-target boundary；
- [ ] one cause → one atomic transaction；
- [ ] revision events；
- [ ] NO_MATERIAL_CHANGE 不增加 version；
- [ ] DEFERRED 不创建 transaction；
- [ ] Revision Engine 不调用模型 / 工具 / 搜索；
- [ ] 未实现 Out-of-Scope 能力；
- [ ] 全量 pytest 通过；
- [ ] coverage 不低于项目门槛；
- [ ] Story 0 / 1A 无回归。

---

# 47. 一句话定义

> **Story 1B 不负责寻找证据，也不负责决定下一步行动；它只判断当前已提供的可靠依据是否足以支持一次局部、可追溯、原子的 Belief Revision。**

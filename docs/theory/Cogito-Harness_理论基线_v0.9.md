# Cogito-Harness 理论基线 v0.9

> 本版本基于 v0.8，并吸收 Story 1A 落地结果与 Story 1B 设计讨论。
>
> 核心目标：
>
> **让 Cogito 的每一次认知变化都具有可追溯依据，同时避免为了“绝对确定”陷入无限自证。**

---

# 1. 核心定义

> **Cogito-Harness 是一个通过 Goal Contract、Domain/Problem Pattern 先验与持续 Evidence Revision 建立动态 World Model，通过 Expectation、Anomaly、Explanatory Demand、Information Gap 与 Cognitive Control 形成可审计的认知状态，并在每个有界 Cognitive Turn 中选择下一步最有价值、最合规且可验证 Action 的认知循环系统。**

v1 压缩定义：

> **Cogito v1 = Evidence-backed World Model + Gap-driven Next Action + Local Revision Loop.**

---

# 2. 一级认知宗旨

## 2.1 No cognitive change without traceable basis

> **无依据，不修订。**

Cogito 不允许因为“看起来合理”“模型感觉如此”“竞争解释更强”而直接改变正式认知状态。

任何 material cognitive change 都必须能够回答：

```text
它依据了什么 Observation / Proposition / Evidence？
为什么这些依据足以支持这次认知变化？
```

## 2.2 Epistemic restraint is a first-class capability

> **认知克制是一等能力。**

Cogito 必须允许：

```text
UNKNOWN
AMBIGUOUS
DEFERRED
CONFLICT_UNRESOLVED
INSUFFICIENT_BASIS
```

成为合法认知状态。

“不知道”不是失败。

## 2.3 Reliable cognition does not require complete certainty

> **可靠认知不等于绝对确定。**

Cogito 的目标不是消灭所有不确定性，而是建立足以支撑当前认知与下一步合理行动的最小可靠依据。

---

# 3. Evidence Discipline

## 3.1 Observation ≠ Fact

Observation 只表示 Cogito 实际看到了什么、读到了什么、听到了什么。

Fact 表示：

> 一个描述性 Claim 已获得当前 Episode Evidence 的充分支持，并被正式 Admission 到 World Model。

## 3.2 Fact assertion strength must not exceed Observation

> **Fact 的断言强度不能超过 Observation 实际支持的强度。**

例如：

```text
Observation:
connection to db:3306 returned connection refused
```

可以形成：

```text
Fact:
connection attempt to db:3306 was refused
```

但不能直接形成：

```text
Fact:
database is down
```

## 3.3 Fact Basis

```text
SOURCE_REPORT
ARTIFACT_CONTENT
DIRECT_MEASUREMENT
DETERMINISTIC_DERIVATION
```

其中：

- `SOURCE_REPORT`：来源明确说了什么；
- `ARTIFACT_CONTENT`：某 Artifact 明确包含什么；
- `DIRECT_MEASUREMENT`：直接测得当前 Reality 状态；
- `DETERMINISTIC_DERIVATION`：由 admitted Facts 与确定性规则推出。

Story 1A 已实现前三类的 Observation-based Admission。

`DETERMINISTIC_DERIVATION` 暂不通过普通 Observation Admission 路径创建，未来应由 premise Facts + deterministic rule 正式推导。

## 3.4 Semantic Entailment

```text
EQUIVALENT_OR_NARROWER
STRONGER_THAN_SOURCE
AMBIGUOUS
```

规则：

```text
STRONGER_THAN_SOURCE → REJECT
AMBIGUOUS → DEFER
EQUIVALENT_OR_NARROWER → continue
```

## 3.5 Source Fitness

> **Source Fitness = Source Type × Claim Type × Scope × Time × Acquisition Context**

禁止使用全局 source reliability 分数：

```text
USER = 0.6
LOG = 0.8
SHELL = 0.9
```

---

# 4. Fact Lifecycle

```text
ACTIVE
SUPERSEDED
RETRACTED
```

定义：

```text
ACTIVE
= 当前仍代表有效 World State

SUPERSEDED
= 曾经真实成立，但已经被后来状态取代

RETRACTED
= 原 Fact 本身建立错误，应从可信 World Model 中撤出
```

核心原则：

> **过时 ≠ 错误。**

## 4.1 Cognitive time ≠ World time

> **认知对象被创建的时间，不等于它所描述的世界时间。**

Fact Supersession 不得使用 `created_at` 作为世界状态变化依据。

应依赖：

```text
valid_from
valid_to
observed_at
temporal scope
version ordering
explicit transition evidence
```

## 4.2 Supersession is replacement of state, not preference between claims

> **Supersede 表示状态被后来状态替代，而不是两个 Claim 中“更喜欢新的那个”。**

Fact Conflict 本身不能自动触发 Supersede。

---

# 5. Contradiction

> **Contradiction 是合法认知状态，不是结构损坏。**

两个都通过 Admission 的 Fact 可以同时保持 `ACTIVE`，即使它们不能同时成立。

Cogito 不应：

```text
latest wins
higher score wins
silent overwrite
auto supersede
auto retract
```

---

# 6. Possibility / Hypothesis

## 6.1 Possibility

没有当前 Episode Evidence 的解释候选只能是 Possibility。

## 6.2 Hypothesis Admission

> **No Evidence → No Hypothesis**

新 Hypothesis 至少需要：

- 当前 Episode Evidence；
- 明确 target problem；
- 至少一个 prediction 或 disconfirming condition。

初始状态固定：

```text
PLAUSIBLE
```

---

# 7. Hypothesis Epistemic Revision

Story 1B 第一阶段支持：

```text
PLAUSIBLE
↓ structural support
SUPPORTED

PLAUSIBLE / SUPPORTED
↓ direct falsification
REJECTED
```

暂不实现：

```text
STRONGLY_SUPPORTED
CONFIRMED
REOPEN
SPLIT
MERGE
```

---

# 8. Structural Support

> **SUPPORTED 不是“证据变多”，而是 Hypothesis 获得了结构上更有解释价值或区分力的支持。**

```text
HypothesisSupportBasis

DIRECT_OBSERVATION
INDEPENDENT_CORROBORATION
DISCRIMINATIVE_EVIDENCE
PREDICTION_CONSISTENT
```

- `DIRECT_OBSERVATION`：Evidence 直接触及 H 所声称的关键状态。
- `INDEPENDENT_CORROBORATION`：不同 acquisition path 形成交叉印证。
- `DISCRIMINATIVE_EVIDENCE`：Evidence 能显著区分 H 与其他合理解释。
- `PREDICTION_CONSISTENT`：H 既有 Prediction 与后续 Observation 一致。

> **Prediction-consistent ≠ Confirmed.**

---

# 9. Hypothesis Rejection

> **Reject 是证伪，不是降权。**

Story 1B 第一阶段只允许：

```text
RejectionBasis

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

> **A stronger competitor does not falsify a hypothesis.**

> **竞争解释更强，不等于当前 Hypothesis 被证伪。**

## 9.1 DIRECT_CONTRADICTION

要求 Evidence 直接否定 H 的核心声明，并在 entity / scope / time / semantic target 上足够可比。

`CONTRADICTS EvidenceLink` 本身不自动等于 `DIRECT_CONTRADICTION`。

## 9.2 DISCONFIRMING_CONDITION_MET

H 在看到新 Evidence 之前已明确声明 disconfirming condition，后续 Evidence 命中该条件。

> **用于 Reject 的 disconfirming condition 必须先于触发它的 Evidence 被提交。**

## 9.3 Rejected Hypothesis preserves history

被 Reject 的 H：

- 不删除；
- 不清空旧 SUPPORTS Evidence；
- 保留 rejection basis；
- 保留 rejected-by Evidence；
- 保留 revision history。

---

# 10. Gap Resolution

Story 1B 支持：

```text
OPEN / FOCUSED
↓ admitted RESOLVES Evidence
RESOLVED
```

规则：

- `RESOLVES` 是强 semantic relation；
- partial answer 不得标记为 `RESOLVES`；
- Gap Resolution 不自动选择下一个 Focused Gap；
- Gap Resolution ≠ Goal Completion。

---

# 11. Temporal Succession Basis

Fact `ACTIVE → SUPERSEDED` 必须有结构化时间依据：

```text
TemporalSuccessionBasis

LATER_DIRECT_OBSERVATION
EXPLICIT_STATE_TRANSITION
VERSIONED_ARTIFACT_SUCCESSION
```

- `LATER_DIRECT_OBSERVATION`：更晚 world-time direct observation 显示同一实体/属性的新状态。
- `EXPLICIT_STATE_TRANSITION`：直接观察到 old state → transition → new state。
- `VERSIONED_ARTIFACT_SUCCESSION`：同一 Artifact 的显式版本先后关系。

> 新版 Artifact 不自动证明 Runtime State 已改变。

---

# 12. Belief Sufficiency ≠ Action Sufficiency

## Belief Sufficiency

当前 Evidence 是否足以修改正式 Cognitive Object？

## Action Sufficiency

即使 Belief 尚未完全稳定，当前信息是否已经足以选择下一步合理 Action？

> **Belief not settled ≠ Action not allowed.**

---

# 13. Epistemic Action

低风险、高信息价值、可验证的动作可以在高不确定性下优先执行，例如：

```text
read
inspect
query
probe
test
ask user
```

> **Observation-first, not Observation-forever.**

---

# 14. Decision-Relevant Uncertainty

> **Unknown ≠ Information Gap**

只有当某 Unknown 的答案预计能够显著改变：

```text
Action Choice
Risk Posture
Hypothesis Disposition
Goal Completion Judgment
```

它才值得成为 active Information Gap。

---

# 15. Minimum Sufficient Evidence

> **追求最小充分证据，而不是最大可得证据。**

> **Minimum Sufficient Evidence, not Maximum Available Evidence.**

---

# 16. Decision Invariance

> **如果合理范围内剩余的不确定性不会改变当前最佳下一步行动，则停止继续认知展开并执行该行动。**

这是未来 Scheduler / Decision Policy 的核心 Stop Rule。

---

# 17. Marginal Information Value Collapse

如果继续获取信息只会产生重复 Evidence，且不会改变 Belief、Action Choice 或关键风险，则应停止调查。

潜在分类：

```text
HIGH
MATERIAL
LOW
REDUNDANT
```

暂不使用数值评分。

---

# 18. Revision Engine 的认知边界

> **Revision Engine 不负责主动追求“足够证据”；它只判断当前提供的依据是否足以支持本次 Revision。**

若不足：

```text
DEFERRED
```

然后停止。

Revision Engine 不得自动搜索、调用工具、Ask User 或递归证明。

---

# 19. Local Revision

> **A new observation should trigger a bounded, provenance-preserving local cognitive transaction, not global rethinking.**

Story 1B 第一版只修改明确 Revision Target，不扫描整个 World Model，不做递归传播。

---

# 20. Revision Result

```text
RevisionStatus

MATERIAL_CHANGE
NO_MATERIAL_CHANGE
DEFERRED
```

核心：

> **No Material Change → No CognitiveTransaction → No cognitive_version increase.**

---

# 21. v0.9 核心原则汇总

```text
1. 无依据，不 Admission。
2. 无结构性支持，不 Strengthen。
3. 无直接证伪，不 Reject。
4. 无充分信息，可以保持 Unknown / Conflict / Deferred。
5. Contradiction 是合法认知状态，不是结构损坏。
6. 过时 ≠ 错误。
7. Cognitive time ≠ World time。
8. Evidence Relation ≠ Belief Revision。
9. Support Count ≠ Belief Strength。
10. Reliable cognition does not require complete certainty。
11. Belief Sufficiency ≠ Action Sufficiency。
12. Unknown ≠ Information Gap。
13. 只主动解决 Decision-Relevant Uncertainty。
14. 追求 Minimum Sufficient Evidence。
15. Low-risk, high-information Action 可在不确定性下优先执行。
16. Observation-first, not Observation-forever。
17. 当更多 Evidence 已不太可能改变 Cognition 或 Action Choice 时停止调查。
18. Revision should be local by default。
19. LLM 提议语义关系，Harness 决定认知后果。
20. Memory preserves history; cognition operates on a projection of history。

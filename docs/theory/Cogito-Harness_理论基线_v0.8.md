# Cogito-Harness 理论基线 v0.8

> **核心信条：计划不是路线图，而是方向盘——每时每刻都在微调。**

---

## 1. 定义

**Cogito-Harness（认知循环驾驭器）**是一种以持续认知状态更新为核心的问题求解 Harness。

它不把求解理解为：

```text
Prompt → Plan → Execute → Finish
```

而理解为：

```text
Goal Contract
→ Observe
→ Qualify Observation
→ Extract Observed Proposition
→ Discover Candidate Targets
→ Evaluate Evidence Links
→ Revision Admission
→ Update World Model
→ Re-evaluate Goal Relation
→ Evaluate Expectations / Deviations / Anomalies
→ Maintain Explanatory Demands
→ Assess Cognitive Pressures
→ Derive Cognitive Control Profile
→ Allocate Attention
→ Select Focused Information Gap
→ Generate / Admit / Compare Actions
→ Commit Action Contract
→ Execute
→ Observe Again
```

Cogito 的控制中心不是固定 Plan，而是持续变化的 Cognitive State。

---

## 2. Cogito 的基本哲学

Cogito 不要求模型永远知道答案。

它要求系统在不知道答案时仍能知道：

```text
自己不知道什么
哪些 Unknown 当前值得解决
正常情况下应该发生什么
现实哪里偏离了预期
什么现象值得解释
有哪些 Evidence Source 可用
什么值得先问
新 Observation 到底表达了什么
它可能关联哪些认知对象
它真正支持、削弱、替代或证伪了什么
什么时候一个解释只是 Possibility
什么时候足以成为 Hypothesis
什么时候应 Refine / Confirm / Reject
这些认知变化对 Goal 意味着什么
当前应如何分配认知资源
现在最值得做哪个可观察 Action
什么时候应该行动，什么时候应该继续求证
```

核心：

> **Cogito 追求的不是更快地产生答案，而是更可靠地形成、修订和使用认知。**

---

## 3. 长期认知层

长期认知能力包括：

```text
Domain Model
Experience
Problem Pattern Model
Evidence Source Map
Inquiry Policy
Historical Episodes
Counterexamples
Principles
Invariants
```

长期认知提供先验、认知脚手架和经验，但不能直接写入当前 World Model。

原则：

> **Memory is prior experience, not current reality.**

---

## 4. 当前 Episode 认知层

当前 Episode 维护：

```text
Goal Contract
Episode Problem Frame
World Model
Facts
Unknowns
Expectations
Deviations
Anomalies
Explanatory Demands
Information Gaps
Possibilities
Hypotheses
Contradictions
Goal Relation State
Cognitive Pressure State
Cognitive Control Profile
Attention State
Cognitive Workspace
Action Candidates
Action Contracts
```

---

# Goal Contract

## 5. Goal Contract

Goal Contract 不是 Prompt 摘要，而是一个版本化任务契约。

至少包括：

```text
Primary Objective
Secondary Objectives
Hard Constraints
Soft Preferences
Acceptance Criteria
Non-goals / Boundaries
Temporal Requirements
Completion Policy
```

原则：

> **目标稳定，路径可变。**

---

## 6. Goal Contract Provenance

每个 Goal Contract Item 应携带：

```text
source
authority
priority
created_at
source_message
revision_history
```

来源至少区分：

```text
SYSTEM_POLICY
USER_EXPLICIT
USER_INFERRED
DOMAIN_SAFETY_DEFAULT
HARNESS_INFERRED
```

Harness 可以推断缺失结构，但不能把推断伪装成用户明确意图。

---

## 7. Goal Contract Revision

Goal Contract 允许版本化修订：

```text
GOAL_ADD / REMOVE / REPRIORITIZE
CONSTRAINT_ADD / RELAX / REVOKE
CRITERION_ADD / UPDATE / REMOVE
SCOPE_EXPAND / NARROW
PREFERENCE_ADD / UPDATE
```

用户输入可能同时产生：

```text
Observation
+
Goal Contract Delta
```

因此 User Message 需要经过：

```text
Intent / Contract Compiler
```

而不仅是 Observation Extraction。

---

## 8. Acceptance Criteria

Acceptance Criteria 是 Goal Contract 与 World Model 的主要比较接口。

状态可包括：

```text
UNKNOWN
UNSATISFIED
PARTIALLY_SATISFIED
SATISFIED
VIOLATED
```

Criterion 可以声明：

```text
required_evidence_type
verification_scope
verification_window
```

避免 Cogito “自行宣布完成”。

---

# Domain / Pattern / Frame

## 9. Domain Model

Domain Model 描述：

> **某类世界如何运作。**

例如：

```text
Entities
Relations
Processes
Dependencies
Invariants
Structural Expectations
```

它相对稳定。

---

## 10. Problem Pattern Model

Problem Pattern Model 描述：

> **某类问题通常如何表现、拆解和认知。**

包括：

```text
Activation Signature
Typical Problem Structure
Expected Transitions
Common Anomalies
Typical Information Gaps
Evidence Source Map
Inquiry Policies
Possibility Families
Disconfirmation Signals
Reframe Signals
Known Traps
Applicability / Mismatch Signals
```

Problem Pattern 是 reasoning scaffold，不是当前事实，也不是当前 Hypothesis。

---

## 11. Episode Problem Frame

Episode Problem Frame 描述：

> **Cogito 当前认为“这一次的问题究竟是什么”。**

建议包含：

```text
target_system
target_state
observed_deviation
current_failure_boundary
explained_region
unresolved_region
active_explanatory_demands
frame_basis
frame_version
```

Problem Frame 可进行：

```text
FRAME_REFINE
FRAME_NARROW
FRAME_EXPAND
FRAME_REPLACE
```

其中只有真正替换问题解释边界时才属于 Reframe。

---

# Observation / Evidence

## 12. Observation

Observation 是 Cogito 从 Evidence Source 实际看到、听到或读取到的外部输入。

至少携带：

```text
content
source
timestamp
acquisition_method
scope
context
provenance
```

Observation 尽量不包含解释。

---

## 13. Observation Qualification

Harness 负责：

```text
Source Fitness
Freshness
Integrity
Provenance
Scope
Temporal Context
Observation Coverage
```

Source Reliability 应理解为：

```text
Source Type × Claim Type × Context
```

而不是全局固定 Source Authority 排名。

---

## 14. Observed Proposition

Observation 在进入 Evidence Evaluation 前，应被规范化为最小描述性 Proposition。

原则：

> **Proposition Extraction 只做描述性规范化，不做因果跳跃。**

---

## 15. Candidate Target Discovery

新 Proposition 到来后，Cogito 寻找它可能关联的 Cognitive Objects。

采用：

```text
L1 Structural Recall
L2 Semantic Recall
L3 Cognitive-Priority Recall
```

搜索范围覆盖整个 Episode，而非只搜索 Workspace。

原则：

> **Candidate Discovery 追求高召回，但不负责判断真伪。**

---

## 16. Novelty Detection

如果新 Proposition 无法合理匹配已有 Cognitive Target：

```text
NOVEL_SIGNAL
```

可能触发：

```text
New Fact
New Anomaly
New Information Gap
New Hypothesis Candidate
Problem Reframe Trigger
```

原则：

> **Disconfirmation 防止当前解释错误；Novelty Detection 防止解释空间不完整。**

---

## 17. Evidence Link

Evidence 是：

> **Observed Proposition 与 Cognitive Target 之间的认知关系。**

核心 Relation：

```text
SUPPORTS
WEAKENS
CONTRADICTS
RESOLVES
PARTIALLY_RESOLVES
INVALIDATES
SUPERSEDES
NEUTRAL
```

Basis Type：

```text
OBSERVATIONAL
LOGICAL
DISCRIMINATIVE
CAUSAL
INTERVENTIONAL
TEMPORAL
NEGATIVE_EVIDENCE
```

Inferential Distance：

```text
DIRECT
ONE_STEP
MULTI_STEP
SPECULATIVE
```

原则：

> **Evidence 应优先挂到最小有意义的认知单元。**

---

## 18. Evidence Engine

四层结构：

```text
① Observation Qualification
② Candidate Target Discovery
③ Semantic Evidence Evaluation
④ Revision Admission
```

职责：

```text
LLM:
semantic interpretation / Evidence Link proposal

Harness:
admission / structural rules / Belief Delta
```

原则：

> **LLM proposes semantic links; Harness derives belief consequences.**

---

## 19. Revision Admission

可产生：

```text
FACT_ADD / UPDATE / EXPIRE / RETRACT
HYPOTHESIS_CREATE / STRENGTHEN / WEAKEN / CONFIRM / REJECT
GAP_OPEN / FOCUS / RESOLVE / DEFER / INVALIDATE
ANOMALY_OPEN / RESOLVE
EXPLANATORY_DEMAND_OPEN / REFINE / RESOLVE
CONTRADICTION_OPEN / RESOLVE
REFRAME_PROPOSE / ACCEPT
NO_MATERIAL_CHANGE
```

原则：

> **Revision should be local by default.**

---

# World Model / Goal Relation

## 20. World Model

World Model 表达：

```text
Entities
Relations
Current States
Facts
Unknowns
Hypotheses
Contradictions
Temporal Context
```

建议采用：

```text
Initial State
+
Observation / Cognitive Events
+
Current Snapshot
```

形成 Cognitive Versioning。

必须区分：

```text
World Change
Knowledge Change
Belief Change
```

---

## 21. Goal Relation

Goal Relation 表达：

> **当前 Reality 对 Goal Contract 意味着什么。**

建议包含：

```text
Outcome
- satisfied_criteria
- partial_criteria
- unsatisfied_criteria
- unknown_criteria

Gaps
- outcome_gaps
- verification_gaps

Constraints
- active_constraints
- candidate_action_conflicts

Progress
- objective_progress_state
- epistemic_progress
- decision_readiness

Control
- blocking_gap
- required_next_progress
- completion_status
```

原则：

> **World Model describes reality; Goal Relation describes the task meaning of that reality.**

---

## 22. Objective / Epistemic Progress

必须区分：

```text
Objective Progress
Epistemic Progress
Decision Readiness
```

可能出现：

```text
Objective Progress = 0
Epistemic Progress > 0
```

即认知进度也是进度。

---

# Expectation / Anomaly / Explanation

## 23. Expectation

Expectation 是：

> **Cogito 对某一 Scope 与 Context 下应出现状态、事件或状态转换的结构化预期。**

来源：

```text
TARGET_EXPECTATION
INVARIANT_EXPECTATION
BASELINE_EXPECTATION
PROCESS_EXPECTATION
HYPOTHESIS_PREDICTION
```

Expectation 应是条件式：

```text
IF Context
THEN Expected State / Event / Transition
```

---

## 24. Deviation / Anomaly

```text
Deviation
= Reality 与有效 Expectation 的偏差

Anomaly
= 当前值得认知资源关注和解释的 Deviation
```

即：

> **Anomaly = Relevant Deviation**

类型可包括：

```text
STATE_DEVIATION
EVENT_MISSING
UNEXPECTED_EVENT
TRANSITION_FAILURE
TIMING_DEVIATION
INVARIANT_VIOLATION
PREDICTION_FAILURE
SCOPE_MISMATCH
```

---

## 25. Explanatory Demand

Explanatory Demand 表示：

> **当前存在一个值得解释、但尚未得到足够解释的现象、因果关系或结构。**

来源：

```text
Anomaly
User explicit why-question
Unexplained causal relation
Prediction failure
Novel signal
Contradiction
```

它回答：

> **为什么？**

Information Gap 回答：

> **为了推进解释，我具体还缺什么？**

---

# Hypothesis

## 26. Hypothesis

定义：

> **Hypothesis 是一个由当前 Episode Evidence 支撑、可逐步结构化、并能够产生可验证预期的解释模型。**

---

## 27. Hypothesis Structure

建议：

```text
Identity
Scope
Causal Role
Premises
Mechanism Steps
Predictions
Disconfirming Conditions
Evidence State
Epistemic State
Attention State
Relations
Revision History
```

Premise 可分：

```text
State Premise
Dependency Premise
Mechanistic Premise
```

重要性可分：

```text
CORE
SUPPORTING
CONTEXTUAL
```

---

## 28. Hypothesis Admission

Candidate Explanation 要晋升为 Hypothesis，至少要求：

1. 回答当前 Explanatory Demand；
2. 有当前 Episode Evidence；
3. Scope 可定义；
4. 能产生可验证 Prediction 或 Disconfirming Condition。

否则只是 Possibility。

原则：

> **Hypothesis 应随着 Evidence 逐步长出来，而不是提前穷举。**

---

## 29. Hypothesis Evolution

支持：

```text
REFINE
SPLIT
MERGE
CONFIRM
REJECT
```

Refinement：

> 同一因果路径提高分辨率。

New Hypothesis：

> 新的因果路径。

Hypothesis Graph 更接近 DAG，而不是单纯树。

---

## 30. Hypothesis State

Epistemic Status：

```text
PLAUSIBLE
SUPPORTED
STRONGLY_SUPPORTED
CONFIRMED
REJECTED
```

Attention Status：

```text
FOCUSED
ACTIVE
INACTIVE
ARCHIVED
```

两者必须分离。

---

## 31. Confirmation / Rejection

原则：

> **Confirmation requires structural coverage, not evidence accumulation.**

确认依赖：

```text
Critical Premises
Mechanism Coverage
Key Predictions
Disconfirming Conditions
Alternative Explanations
Scope / Time Match
```

必须区分：

```text
State Claim Confirmed
Causal Hypothesis Confirmed
```

原则：

> **状态差异不自动等于因果解释。**

Reject 必须来自关键 Premise / Mechanism / Prediction 的实质失效，而不是因为另一个解释更强。

---

## 32. Negative Evidence

只有满足：

```text
Expectation exists
AND
observable signal predicted
AND
Observation Coverage adequate
AND
Scope/time match
AND
expected signal absent
```

才成立。

必须区分：

```text
Expected evidence absent
```

与：

```text
Opposite evidence observed
```

---

# Information Gap / Attention

## 33. Information Gap

```text
Unknown
= 我不知道

Information Gap
= 当前值得被解决的 Unknown
```

即：

> **Information Gap = Relevant Unknown**

来源：

```text
Goal-derived
World-model-derived
Hypothesis-derived
Contradiction-derived
Decision-derived
```

---

## 34. Focused Information Gap

优先选择：

> **当前最值得解决的可回答 Unknown。**

评估：

```text
Goal Blocking
Hypothesis Discrimination
Information Gain
Decision Impact
Action Unlocking
Answerability
Cost
Risk
Freshness Need
```

原则：

> **优先获取可能改变 cognition 或 action choice 的信息，而不是单纯增加知道的东西。**

---

## 35. Attention Allocation

围绕：

```text
Current Goal Gap
Focused Explanatory Demand
Focused Information Gap
```

再聚合：

```text
Focused Hypotheses
Current Facts
Relevant Evidence
Confirmed Evidence Sources
Candidate Evidence Sources
Disconfirmation Watch
```

同时维护：

```text
Exploitation Attention
Disconfirmation Attention
```

Attention 存在 Inertia，避免每轮轻微信息都导致焦点抖动。

---

## 36. Cognitive Workspace

建议：

```text
1. Goal Contract Snapshot
2. Current Required Progress
3. Current Goal Gap
4. Focused Explanatory Demand
5. Focused Information Gap
6. Focused Hypotheses
7. Current Facts
8. Relevant Evidence
9. Confirmed Evidence Sources
10. Candidate Evidence Sources
11. Disconfirmation Watch
```

原则：

> **Memory 保存完整历史，Cognition 只处理当前所需投影。**

---

# Action Selection

## 37. Action Definition

Cogito 每轮选择的是：

> **下一步与 Reality 的可观察交互行为。**

而不是完整解决方案 Plan。

Action 应具有可观察结果：

```text
Action
→ Result / Observation
→ Cognitive Delta
```

---

## 38. Candidate Action Sources

主要来源：

```text
Information Gap
Hypothesis Prediction
Disconfirmation Watch
Goal / Verification Gap
Experience / Inquiry Policy
```

Action Generation 不应自由 Brainstorm，而应由当前认知结构提供 Action Seeds。

原则：

> **Harness 决定需要什么认知或执行动作，LLM 帮助把它转成具体操作。**

---

## 39. Action Selection 五阶段

```text
1. Generate
2. Admit
3. Characterize
4. Compare
5. Commit
```

### Generate

从 Gap / Hypothesis / Goal / Experience 产生候选。

### Admit

经过：

```text
Hard Constraint Gate
System Policy Gate
Tool Availability Gate
Action-specific Decision Readiness
```

### Characterize

分析：

```text
Pragmatic Value
Epistemic Value
Information Gain
Hypothesis Discrimination
Disconfirmation Value
Verification Value
Future Option Value
Evidence Quality Potential

Execution Cost
Latency
User Friction

Operational Risk
Irreversibility
Blast Radius
```

### Compare

使用：

```text
Cognitive Control Profile
Dominance Check
Relative Ranking
Counterfactual Check for high-impact actions
```

### Commit

创建 Action Contract 后执行。

---

## 40. Hard Constraint Gate

Hard Constraint 不是 Utility Penalty，而是 Action Admission Gate。

原则：

> **Hard constraints gate actions before utility comparison.**

---

## 41. Action-specific Decision Readiness

Decision Readiness 必须针对具体 Action。

例如：

```text
Read logs:
READY

Restart test service:
READY_WITH_CAUTION

Modify production DB:
NOT_READY
```

如果 Action Readiness 不足，应反向生成：

```text
Required Preconditions
→ Information Gaps
→ Epistemic Actions
```

---

## 42. Observation-first

原则：

> **When cheap observation can materially improve a risky decision, observe first.**

但不能陷入无限调查。

因此还需要：

> **Decision-Relevant Information Principle**

即：

> **优先获取那些可能改变 Action Choice 的信息。**

如果无论答案 A/B 下一步都不会改变，则信息边际价值通常较低。

---

## 43. Dominance Check

如果一个 Action 在关键维度上被另一 Action 全面支配，则标记：

```text
DOMINATED
```

优先淘汰，不需要伪精确评分。

最终对 Pareto Front 内的少量 Action 做相对排序。

---

## 44. Action Contract

较重要 Action 执行前应形成：

```text
ActionContract

Intent
- why_now
- target_gap
- target_goal

Expected Outcome
- predicted_state_change

Evidence Expectation
- what should become observable

Risk
- level
- blast_radius
- irreversibility

Safety
- constraints
- rollback

Verification
- how success/failure will be judged
```

原则：

> **High-impact actions require an explicit verification path.**

---

## 45. Tool Success / Cognitive Success / Goal Success

必须区分：

```text
Tool Success
Cognitive Success
Pragmatic Success
Goal Success
```

例如 command exit code 0 只能说明 Tool Success，不能直接说明 Goal Success。

---

# Cognitive Pressure / Cognitive Control

## 46. Cognitive Pressure

Cognitive Pressure 表示：

> **当前 Cognitive State 中有哪些因素正在迫使 Cogito 改变认知或行动策略。**

主要包括：

```text
Goal Pressure
Uncertainty Pressure
Explanation Pressure
Verification Pressure
Contradiction Pressure
Exploration Pressure
Risk Pressure
```

Pressure 描述“当前什么最需要适应”，不描述 Truth。

---

## 47. Goal Pressure

来源：

```text
Blocking Goal Gap
Unsatisfied Acceptance Criteria
Deadline / Urgency
Primary Objective incomplete
```

它推动 Goal-relevant progress，但不会自动突破风险与约束。

---

## 48. Uncertainty Pressure

来源：

```text
Focused Information Gap
Unknown critical premise
Low explanatory coverage
Uncertain scope
Missing evidence
```

倾向：

```text
Observe
Read
Ask
Gather Data
```

---

## 49. Explanation Pressure

来源：

```text
Focused Explanatory Demand
Unexplained Anomaly
Low Hypothesis Coverage
Novel Signal
```

它回答：

> **当前不是不知道发生了什么，而是不知道为什么。**

---

## 50. Verification Pressure

来源：

```text
Strong Hypothesis but untested prediction
Unresolved competitor
Repair result unverified
Acceptance Criterion assumed but unverified
```

推动：

```text
Prediction Test
Disconfirmation
Independent Evidence
Acceptance Verification
```

---

## 51. Contradiction Pressure

来源：

```text
High-quality contradictory evidence
Unresolved fact conflict
Prediction failure
Expectation violation
```

推动：

```text
Disconfirmation Attention
Scope / Time verification
Problem Reframe consideration
```

---

## 52. Exploration Pressure

来源：

```text
Low recent Information Gain
Repeated Action Pattern
Focused Gap not shrinking
Hypothesis State stagnant
Unexplained Anomaly persists
Evidence Sources exhausted
```

推动：

```text
Alternative Evidence Sources
Inactive Hypothesis Recall
Novelty Search
Pattern Reconsideration
Problem Reframe
```

---

## 53. Risk Pressure

来源：

```text
Operational Risk
Irreversibility
Blast Radius
Weak Action Readiness
High-impact Environment
Safety Constraints
```

Risk Pressure 主要压缩允许 Action 空间。

原则：

> **Risk changes action thresholds, not evidence strength.**

---

## 54. Cognitive Control Profile

早期：

```text
Assess Pressures
→ Select Mode
```

正式修正为：

```text
Assess Cognitive Pressures
→ Derive Cognitive Control Profile
```

Profile 分三部分：

```text
Cognitive Policy
Risk Posture
Tempo
```

---

## 55. Cognitive Policy

主要包括：

```text
DIAGNOSTIC
VERIFICATION
EXECUTION
EXPLORATORY
```

它回答：

> **当前认知主要想达成什么？**

它只是 Pressure 的策略投影，不是 Truth State。

---

## 56. Risk Posture

建议：

```text
NORMAL
CAUTIOUS
STRICT
```

它回答：

> **当前允许多激进？**

`CONSERVATIVE` 不再作为 Cognitive Mode，而作为 Risk Posture。

---

## 57. Tempo

建议：

```text
NORMAL
URGENT
CRITICAL
```

它回答：

> **当前多快需要产生 Goal-relevant progress？**

原则：

> **Urgency changes tempo, not epistemic standards.**

但 Urgency 可以改变某些低风险、可逆 Mitigation 的 Action Threshold，不能把弱 Evidence 变成强 Evidence。

---

## 58. Cognitive Policy Bias

### DIAGNOSTIC

偏向：

```text
Information Gain
Evidence Quality
Gap Resolution
Hypothesis Discrimination
```

### VERIFICATION

偏向：

```text
Prediction Tests
Disconfirmation
Independent Evidence
Acceptance Verification
```

### EXECUTION

偏向：

```text
Goal Advancement
Pragmatic Action
Cost / Risk efficient execution
```

### EXPLORATORY

偏向：

```text
Novel Evidence Sources
Inactive Hypothesis Recall
Alternative Patterns
Reframe Value
```

---

## 59. Cognitive Policy Boundaries

Mode / Policy 可以影响：

```text
Attention
Gap Selection
Candidate Generation
Retrieval Breadth
Action Ranking
```

但不能直接改变：

```text
Fact
Evidence Link
Hypothesis Epistemic State
World Model Truth
```

原则：

> **Strategy must not contaminate belief.**

---

## 60. Pressure / Policy Inertia

Pressure 与 Cognitive Policy 都应有 Inertia。

只有以下 Material Change 才触发明显切换：

```text
Focused Gap resolved
Dominant pressure category changes
Decision Readiness materially changes
Strong contradiction appears
Stagnation structurally established
Goal Contract changes
Problem Reframe occurs
```

原则：

> **Cognitive Policy follows meaningful cognitive transitions, not every minor observation.**

---

# Memory / Learning

## 61. Memory Consolidation

长期记忆不是 Episode 摘要库，而是经过筛选、抽象、验证并明确适用边界的可复用认知资产。

流程：

```text
Episode Cognitive History
↓
Candidate Fragment Extraction
↓
Cognitive Credit Evaluation
↓
Abstraction
↓
Applicability Extraction
↓
Provenance Binding
↓
Existing Memory Comparison
↓
Merge / Refine / New Candidate
↓
Memory Admission
↓
Long-Term Experience
```

---

## 62. Experience Fragment

建议包含：

```text
Context
Cognitive Move
Observation / Result
Belief Delta
Goal Relation Delta
Epistemic / Pragmatic Value
Cost
Risk
Applicability
Counterexamples
Provenance
```

原则：

> **Current usefulness ≠ Long-term memorability.**

---

## 63. Memory Admission

长期层至少要求：

1. 有可追溯 Episode Evidence；
2. 产生 Material Cognitive Delta 或 Pragmatic Delta；
3. 具有未来复用价值；
4. Scope / Applicability 可定义；
5. 不是纯临时状态；
6. 不是未经验证的 LLM 推断；
7. 与已有 Memory 的关系被检查；
8. 能合并时优先合并。

---

## 64. Cognitive Credit Assignment

长期经验强化不能只看 Episode 最终成功。

真正需要归因：

```text
Action
→ Belief Delta
→ Goal Relation Delta
```

原则：

> **Credit is assigned to cognitive contribution, not final task success.**

Retrieval 本身也不代表 Validation。

> **Retrieval is not validation.**

---

## 65. Problem Pattern Learning

单个 Episode 产生 Experience，不直接产生 Pattern。

```text
Episode
↓
Experience Fragment
↓
Cross-Episode Aggregation
↓
Pattern Candidate
↓
Counterexample / Validation
↓
Established Problem Pattern
```

原则：

> **Patterns emerge from repeated cognitive structure across episodes.**

反例应主要用于收缩 Applicability Boundary，而不是简单减分。

---

## 66. Memory Abstraction Levels

建议：

```text
L0 Specific Episode Fragment
L1 Same technology / scene reusable experience
L2 Cross-scenario Cognitive Pattern
L3 General Principle
```

抽象层级越高，需要越强的跨 Episode / 跨 Domain Evidence。

核心 Principle 默认不允许被普通自动学习轻易修改。

---

## 67. Memory Lifecycle

可区分：

```text
ACTIVE_MEMORY
DORMANT_MEMORY
ARCHIVED_MEMORY
RETIRED_MEMORY
```

“很久没用”主要降低 Retrieval Priority，不代表 Epistemic Invalid。

Memory 还应区分：

```text
STABLE
VERSION_SENSITIVE
ENVIRONMENT_SENSITIVE
TEMPORAL
EPISODIC
```

---

## 68. Long-term Belief Revision

Cogito 对当前 Episode 与长期 Experience 都采用同一哲学：

```text
Evidence
→ Revision
→ Scope
→ Counterexample
→ Refine
```

因此存在：

```text
Short-term Belief Revision
Long-term Experience Revision
```

---

# 69. 当前完整认知链

```text
Goal Contract
↓
Domain Model / Problem Pattern priors
↓
Episode Problem Frame
↓
World Model
↓
Goal Relation
↓
Expectation
↓
Observation
↓
Qualification
↓
Observed Proposition
↓
Evidence Evaluation
↓
Belief Revision
↓
Deviation / Anomaly
↓
Explanatory Demand
↓
Possibility / Hypothesis
↓
Information Gap
↓
Cognitive Pressure
↓
Cognitive Control Profile
├── Cognitive Policy
├── Risk Posture
└── Tempo
↓
Attention Allocation
↓
Cognitive Workspace
↓
Candidate Actions
↓
Constraint / Readiness Gate
↓
Relative Comparison
↓
Action Contract
↓
Execute
↓
Observation
↓
Loop
```

---

# 70. 当前核心原则

1. **计划不是路线图，而是方向盘。**
2. **Goal 稳定，Problem Understanding 可以演化。**
3. **Goal Contract 是版本化任务契约，不是 Prompt 摘要。**
4. **World Model 描述 Reality；Goal Relation 描述 Reality 对任务意味着什么。**
5. **Observation 不包含解释。**
6. **Observed Proposition 只做描述性规范化，不做因果跳跃。**
7. **Evidence 是 Proposition 相对于 Cognitive Target 的关系。**
8. **LLM 提议语义关系，Harness 决定认知后果。**
9. **Revision 默认局部发生。**
10. **Fact 描述现实，Hypothesis 解释现实。**
11. **Hypothesis 因 Explanatory Demand 而产生。**
12. **Possibility 只有获得当前 Episode Evidence 才能晋升为 Hypothesis。**
13. **Hypothesis 应随着 Evidence 逐步长出来，而不是提前穷举。**
14. **Confirmation 依赖结构覆盖，而不是 Evidence Count。**
15. **Reject 必须来自核心结构失效。**
16. **状态差异不自动等于因果解释。**
17. **Unknown = 我不知道；Information Gap = 当前值得解决的 Unknown。**
18. **Deviation = Reality 与 Expectation 的偏差；Anomaly = 当前值得解释的 Deviation。**
19. **Explanatory Demand 与 Information Gap 必须区分。**
20. **Negative Evidence 需要明确 Prediction + 足够 Observation Coverage。**
21. **Candidate Discovery 追求高召回，不负责判断 Truth。**
22. **当前 Attention 可以影响 Recall Priority，但不能定义 Cogito 能看见什么。**
23. **Disconfirmation 防止当前解释错误，Novelty Detection 防止解释空间不完整。**
24. **Source Reliability 必须是针对具体 Claim 的 Source Fitness。**
25. **Memory 保存完整认知历史，Cognition 只处理当前所需投影。**
26. **认知进度也是进度。**
27. **失败 Hypothesis 不等于失败 Action。**
28. **Hard Constraint 在 Utility 比较前 Gate Action。**
29. **Decision Readiness 必须是 Action-specific。**
30. **Cogito 选择下一步可观察交互，而不是完整 Plan。**
31. **低成本高价值 Observation 能改善高风险决策时，应优先 Observe。**
32. **Information 主要在可能改变 cognition 或 action choice 时有价值。**
33. **Tool Success、Cognitive Success、Pragmatic Success、Goal Success 必须分开。**
34. **高影响 Action 必须有明确 Verification Path。**
35. **Cognitive Pressure 描述适应需求，不描述 Truth。**
36. **Cognitive Policy 是 Pressure 的策略投影，不是硬状态机。**
37. **Cognitive Policy、Risk Posture、Tempo 必须分开。**
38. **Risk 改变 Action Threshold，不改变 Evidence Strength。**
39. **Urgency 改变 Tempo，不改变 Epistemic Standard。**
40. **Policy 可以影响 Attention / Retrieval / Action Ranking，但不能直接修改 Belief。**
41. **Current Cognitive State 优先于历史 Policy Prior。**
42. **Memory 记住的是在什么条件下什么认知结构被证明有用，而不是简单记录发生过什么。**
43. **Retrieval is not validation.**
44. **Credit is assigned to cognitive contribution, not final task success.**
45. **单个 Episode 产生 Experience，不直接产生 Established Pattern。**
46. **反例主要用于学习 Applicability Boundary。**
47. **External information is evidence, not memory.**
48. **Simulation is prediction, not evidence.**

---

## 71. 一句话定义

> **Cogito-Harness 是一个通过 Goal Contract、Domain/Problem Pattern 先验与持续 Evidence Revision 建立动态 World Model，再利用 Goal Relation、Expectation、Anomaly、Explanatory Demand、Information Gap 与 Cognitive Pressure 形成可审计 Cognitive Control Profile，最终选择下一步最有价值且可验证 Action 的认知循环系统。**

---

# 计划不是路线图，而是方向盘。

---

# v0.8 新增冻结：认知状态、调度与最低可运行内核

> 本节在 v0.7 的 Goal / Evidence / Hypothesis / Gap / Action / Cognitive Control / Memory 理论之上，正式冻结 Cognitive State Storage、Cognitive Transaction、LLM Cognitive Roles、Cognitive Turn Scheduler 与 Cogito v1 最低可运行内核。

## 72. Cognitive State 不应是巨大 JSON

Cogito 不应依赖一个持续被 LLM 改写的巨大 `CognitiveState` 对象。

建议采用：

```text
Episode Event Log
+
Committed Cognitive Objects
+
Derived Cognitive Views
+
Transient Working Set
+
Long-Term Experience Store
```

核心原则：

> **Events preserve what happened; snapshots represent what Cogito currently believes.**

> **Workspace is a projection, not memory.**

> **Index is access infrastructure, not knowledge.**

## 73. Episode Event Log

Event Log 是 Episode 的历史 Source of Truth，采用 append-only。

典型事件：

```text
USER_MESSAGE_RECEIVED
GOAL_CONTRACT_REVISED
ACTION_COMMITTED
ACTION_EXECUTED
OBSERVATION_RECEIVED
PROPOSITION_EXTRACTED
EVIDENCE_LINK_ADMITTED
FACT_ADDED
HYPOTHESIS_CREATED
HYPOTHESIS_STATUS_CHANGED
GAP_OPENED / RESOLVED
FRAME_REFINED / REPLACED
```

Raw User Message、Raw Observation、Tool Result 应保留原始形式，不因后续解释变化而覆盖。

## 74. Committed Cognitive Objects

只有通过 Admission Policy 的认知对象才能进入正式状态：

```text
Goal Contract
Fact
Hypothesis
Information Gap
Anomaly
Explanatory Demand
Contradiction
Expectation
Problem Frame
Evidence Link
```

每个对象必须拥有：

```text
stable_id
provenance
scope
lifecycle
revision_history
```

## 75. Derived Cognitive Views

以下对象原则上是可重算视图，而非独立 Truth Source：

```text
Goal Relation
Cognitive Pressure
Cognitive Control Profile
Attention Allocation
Cognitive Workspace
Action Readiness
Coverage Views
```

工程上可以缓存或增量物化，但逻辑上必须可从 Committed Cognition 重建。

## 76. Transient Working Set

以下对象通常只属于当前认知操作：

```text
Candidate Target Set
LLM Proposals
Possibility Retrieval Results
Candidate Actions
Dominated Actions
Counterfactual Simulations
Temporary Rankings
Semantic Retrieval Hits
```

除非它们被 Admission 或形成 Material Decision Trace，否则不进入 Cognitive Object Store。

## 77. Proposal → Admission → Commit

所有开放语义结果统一采用：

```text
LLM / Rule Engine / Retrieval
↓
Proposal
↓
Admission Policy
↓
Committed Cognitive Event
↓
Snapshot Update
↓
Derived View Recompute
```

核心原则：

> **LLMs propose; admission policies commit.**

LLM 不直接：

```text
write Fact
change Goal
confirm Hypothesis
execute Tool
write Long-Term Memory
```

## 78. Cognitive Transaction

定义：

> **由一个或一组明确 Cognitive Causes 引发，并以原子方式提交的一组相互一致的认知状态变化。**

例如：

```text
Cause: Observation O17

Transaction T42:
- FACT_ADD F8
- GAP_RESOLVE G7
- PREMISE_STRENGTHEN H1.P2
- HYPOTHESIS_STATUS_CHANGED H1
```

共享：

```text
transaction_id
caused_by
base_cognitive_version
timestamp
```

## 79. Belief Transaction 与 Cognitive Reprojection

正式拆成：

```text
Phase A: Belief Transaction
Phase B: Cognitive Reprojection
```

Belief Transaction 负责：

```text
Fact
Evidence
Hypothesis Structure
Gap
Anomaly
Contradiction
Problem Frame
```

Reprojection 负责：

```text
Goal Relation
Pressure
Cognitive Control
Attention
Workspace
```

原则：

> **Belief changes are committed before Goal Relation, Pressure, Attention, or Workspace are recomputed.**

## 80. Local / Bounded Revision

新 Observation 不重写整个认知系统。

传播按三圈：

```text
Ring 0: Direct Targets
Ring 1: Structural Dependents
Ring 2: Task-Relevant Derived Consequences
```

到 Ring 2 时停止 Belief Propagation，进入 Reprojection。

原则：

> **Revision begins locally and propagates only through explicit cognitive dependencies.**

## 81. Deterministic 与 Semantic Propagation

确定性关系可由 Harness 自动传播：

```text
configured_port=3306
actual_port=3307
→ mismatch=true
```

因果解释不能自动强推：

```text
port mismatch
→ caused startup failure
```

必须经过 admitted Hypothesis / Mechanism / Evidence Link。

## 82. Evidence Deduplication / Independence

重复或相关 Observation 不得虚假放大 Belief。

应追踪：

```text
evidence_family
origin_event
source_artifact
correlation_group
source_diversity
evidence_independence
structural_coverage
```

原则：

> **Repeated or correlated evidence must not create artificial belief amplification.**

## 83. Reverse Revision

当 Evidence 被发现属于错误 Scope、错误实例、过期来源等，应允许：

```text
Evidence INVALIDATED
↓
Fact re-evaluated
↓
Premise coverage re-evaluated
↓
Hypothesis status re-evaluated
```

原则：

> **Retraction and invalidation propagate through the same dependency structure as new evidence.**

## 84. LLM Cognitive Roles

LLM 不作为自治 Agent，而作为受限语义函数。

理论角色包括：

```text
Intent / Contract Interpreter
Observation Semantic Parser
Semantic Evidence Evaluator
Explanatory Model Builder
Gap Contextualizer
Action Operationalizer
Reframe Analyst
Memory Consolidation Analyst
```

原则：

> **LLM roles are constrained semantic functions, not autonomous agents.**

## 85. Cognitive Checks-and-Balances

以下角色不应合并成自证闭环：

```text
Hypothesis Builder
+
Evidence Evaluator for same hypothesis
```

```text
Action Generator
+
Action Safety Admission
```

```text
Memory Candidate Generator
+
Memory Admission
```

原则：

> **The role that proposes an explanation should not be the sole judge of evidence for that explanation.**

## 86. Context Router

每个 Role 只读取当前任务所需的最小认知投影。

Context Pack 可包括：

```text
Role
Task
Scope
Allowed Operations
Forbidden Operations
Required Context
Optional Context
Biasing Context Exclusions
Relevant Cognitive Objects
Source Material
Expected Output Schema
```

原则：

> **A role should receive the minimum context necessary to perform its cognitive function correctly.**

## 87. Context 必须保留 Epistemic Type

传入 LLM 的对象不能只是自然语言摘要，至少应保留：

```text
object_type
epistemic_status
provenance
scope
time
```

Historical Experience、Possibility、Fact、Hypothesis 必须明确标识，避免历史先验被误当作当前事实。

原则：

> **Context must preserve epistemic type.**

## 88. Uncommitted Cognition 隔离

未 Admission 的 Proposal 不得偷偷进入后续 Prompt 成为 Truth。

原则：

> **Uncommitted cognition must not silently become context truth.**

## 89. Abstention / Missing Context

LLM Role 必须允许：

```text
ABSTAIN
INSUFFICIENT_CONTEXT
```

缺失分两种：

```text
RETRIEVAL_MISSING
EPISTEMIC_MISSING
```

前者由 Context Router 补充已有 Cognition；后者形成 Information Gap，并要求 Reality 提供新 Evidence。

原则：

> **Missing prompt context and missing world knowledge must be distinguished.**

## 90. Cognitive Turn

正式定义：

> **Cognitive Turn 是从一个新的外部或已提交认知事件开始，到 Cogito 形成一个稳定的下一步决策为止的一次有界认知过程。**

它不是一次 User Message，也不是一次 LLM Call。

## 91. Interaction Turn / Cognitive Turn / Action Turn

区分：

```text
Interaction Turn
= User ↔ Assistant 的一次交互

Cognitive Turn
= Cogito 内部一次稳定认知更新并形成下一步

Action Turn
= Cogito 与外部 Reality 的一次交互
```

一个 Interaction Turn 可以包含多个 Cognitive Turn。

## 92. Cognitive Cause

Cognitive Turn 的起点统一称为：

```text
CognitiveCause
```

来源可包括：

```text
USER_MESSAGE
TOOL_RESULT
ACTION_RESULT
TIME_EVENT
EXTERNAL_EVENT
GOAL_CONTRACT_CHANGE
REINTERPRETATION_TRIGGER
```

## 93. Evidence Boundary

当下一步有效认知进展需要新的 Reality 信息时，当前内部 Cognitive Turn 必须停止。

原则：

> **No new external evidence, no unlimited epistemic progress.**

Cogito 可以继续做：

```text
Parse
Normalize
Compare
Aggregate
Deterministic Derivation
Reprojection
```

但不能无限：

```text
Speculate
Generate unsupported hypotheses
Generate unsupported branches
```

## 94. No-Evidence Hypothesis Cascade

原则：

> **When alternatives are not evidence-backed, branch through inquiry, not hypothesis proliferation.**

中文：

> **证据不足时，应该分叉“问题”，而不是分叉“结论”。**

## 95. Cognitive Turn Resolution

一次 Cognitive Turn 最终落在：

```text
NEED_EXTERNAL_EVIDENCE
READY_TO_ACT
READY_TO_VERIFY
READY_TO_RESPOND
BLOCKED
COMPLETE
```

并记录 `why_stop`：

```text
EXTERNAL_EVIDENCE_REQUIRED
GOAL_SATISFIED
BLOCKED_BY_AUTHORITY
NO_MATERIAL_INTERNAL_PROGRESS
ACTION_READY
USER_RESPONSE_REQUIRED
```

## 96. Scheduler

只有 Harness Scheduler 有权推进 Cognitive Loop。

原则：

> **Only the Scheduler advances the cognitive loop.**

LLM Role 不得递归调用其他 Role，也不得在 Role 内部自主执行 Tool。

## 97. Scheduler Eligibility

Cogito 不使用所有模块都必跑的固定 Pipeline，而采用 Eligibility：

```text
Contract Interpreter
eligible when new user message exists

Observation Parser
eligible when new raw observation exists

Evidence Evaluator
eligible when new proposition + candidate targets exist

Hypothesis Builder
eligible when explanatory demand + Episode evidence exist

Reframe Analyst
eligible when frame mismatch / contradiction / exploration signals exist
```

Cogito 因此更接近：

> **bounded event-driven scheduler**

## 98. Scheduler Guards

至少包括：

```text
No Material Change Guard
Same-input Dedup Guard
No-Evidence Expansion Guard
Stagnation Guard
External Boundary Guard
```

同一 Role、同一输入、同一 Context Version 已返回 NO_MATERIAL_CHANGE 时，不应立即重复调用。

## 99. Sparse Cognitive Activation

不是所有请求都需要完整 Cognition Stack。

简单问答：

```text
Goal
→ Knowledge Retrieval
→ Respond
```

复杂 Debug：

```text
Observation
→ Evidence
→ Hypothesis
→ Gap
→ Action
→ Revision Loop
```

原则：

> **Cognitive architecture is modular, but runtime cognition is sparse.**

## 100. Role Coalescing

为了效率，可合并：

```text
相同 Context
无认知自证风险
输出可独立 Admission
```

的 Role。

但不能跨 Cognitive Checks-and-Balances Boundary。

原则：

> **Roles may be coalesced for efficiency, but never across a cognitive checks-and-balances boundary.**

---

# v0.8 冻结：Cogito v1 最低可运行内核

## 101. v1 的核心验证目标

v1 不追求完整实现理论模型。

只验证六件事：

```text
1. Observation 与解释能否稳定分离
2. World Model 能否基于 Evidence 可修订
3. Hypothesis 是否只有在 Episode Evidence 支撑后才成立
4. Information Gap 是否真正驱动 Next Action
5. 新 Evidence 是否会导致 Local Revision 与方向改变
6. 是否能减少假设爆炸、重复动作和低价值调查
```

## 102. Cogito v1 最小核心

> **Cogito v1 = Evidence-backed World Model + Gap-driven Next Action + Local Revision Loop.**

P0 只实现：

```text
1. Goal Contract
2. Episode State Store
3. Observation / Observed Proposition
4. Evidence Link
5. World Model
6. Hypothesis
7. Information Gap
8. Cognitive Turn Scheduler
9. Action Selection
```

## 103. v1 Goal Contract

P0 只保留：

```text
Goal
Hard Constraints
Acceptance Criteria
```

完整 Priority / Authority / Temporal / Secondary Objective 等保留在 Theory，不要求 P0 全实现。

## 104. v1 Episode State

最小状态：

```text
EpisodeState

Goal
Constraints
Acceptance Criteria

Facts[]
Hypotheses[]
Possibilities[]
Open Gaps[]
Focused Gap

Recent Observations[]
Recent Actions[]
Stagnation State
```

Goal Relation / Pressure / Attention 可以先由 Decision Engine 动态计算，不强制对象化。

## 105. v1 Observation

必须保留三层：

```text
Raw Observation
≠
Observed Proposition
≠
Fact
```

这是 v1 不可删除的核心边界。

## 106. v1 Evidence Link

P0 只实现：

```text
SUPPORTS
CONTRADICTS
RESOLVES
NEUTRAL
```

完整：

```text
WEAKENS
SUPERSEDES
PARTIALLY_RESOLVES
NEGATIVE_EVIDENCE
```

推迟到 v1.1。

## 107. v1 Hypothesis

最小结构：

```text
id
statement
evidence_refs[]
prediction
status
```

最小状态：

```text
PLAUSIBLE
SUPPORTED
CONFIRMED
REJECTED
```

但必须保留：

> **没有当前 Episode Evidence，不得晋升为 Hypothesis。**

## 108. v1 Information Gap

最小结构：

```text
id
question
why_it_matters
target_hypothesis_id?
source_hint?
status
```

Focused Gap 是 v1 的“方向盘”。

## 109. v1 Scheduler

最小循环：

```text
New Cause
↓
Parse
↓
Revise State
↓
Select Focused Gap
↓
Can internal cognition progress materially?
    yes → bounded internal operation
    no
↓
Select next Action / Ask / Respond
```

Turn Resolution 最小支持：

```text
RESPOND
ACT
ASK
BLOCKED
COMPLETE
```

## 110. v1 Action Selection

最小策略：

```text
1. Hard Constraint Gate
2. Prefer Action that resolves Focused Gap
3. Prefer lower-risk / lower-cost direct Evidence
```

v1 不需要完整 Pareto Frontier 或完整 Cognitive Pressure 模型。

## 111. v1 Action Contract

最小结构：

```text
action
purpose
expected_observation
risk
```

执行之后，新 Observation 开启新的 Cognitive Turn。

## 112. v1 暂不实现

明确推迟：

```text
完整 Expectation Engine
完整 Anomaly Admission
正式 Explanatory Demand Object
Hypothesis DAG / Premise Graph
Evidence Independence Graph
Advanced Negative Evidence
Problem Pattern Learning
Long-Term Memory Consolidation
Memory Generalization
完整 Cognitive Pressure Model
Progressive Context Expansion
Multi-model Routing
Parallel Cognitive Transactions
Vector DB
Graph DB
Automatic Pattern Promotion
```

这些属于理论能力，不属于 P0。

## 113. v1 Long-Term Memory

建议：

```text
Persistent Long-Term Memory = OFF
```

只做 Episode Memory，最多内置少量人工 Domain / Tool Knowledge。

目的：先单独验证 Cognitive Loop 的价值，避免 Memory 带来的性能增益或污染干扰实验结论。

## 114. v1 第一验证场景

优先使用：

> **有明确 Reality、可逐步取证、有多个潜在解释、需要 Tool Feedback 的 Debug 任务。**

例如：

```text
代码测试失败
Java / Spring 服务启动失败
项目 build 失败
配置未生效
接口返回异常
```

Debug 比创作任务更适合作为 Cogito Core 的首个实验台，因为 Evidence、Causal Revision 和 Tool Feedback 更清楚。

## 115. Baseline

同一个模型、同一个工具、同一个任务，对比：

```text
Baseline A: ReAct
Baseline B: Plan-and-Execute
Cogito v1
```

比较：

```text
Task Success
Tool Calls
Repeated Actions
Unsupported Hypotheses
Wrong Interventions
Evidence Reversal Handling
Steps to Root Cause
Token Usage
```

## 116. Cogito 特有指标

至少监控：

```text
Unsupported Hypothesis Rate
Repeated Low-Value Action Rate
Revision Correctness
Gap Efficiency
Cognitive Waste
Decision Trace Quality
```

其中：

```text
Unsupported Hypothesis Rate
≈ 无 Episode Evidence 却进入 Hypothesis 的比例
```

目标应接近 0。

`Gap Efficiency` 关注 Gap 是否真正带来：

```text
Belief Delta
Goal Relation Delta
Action Choice Delta
```

`Cognitive Waste` 关注创建后从未参与 Decision 的：

```text
Hypothesis
Gap
Action Candidate
```

## 117. v1 成功条件

至少：

```text
1. 稳定完成至少一类 Debug 任务
2. Hypothesis 不凭空生成
3. Evidence 能使 Hypothesis strengthen / reject
4. Tool Action 能映射到当前 Focused Gap
5. 重复低价值 Action 明显少于 Baseline
6. 新 Evidence 到来后能改变方向
7. 不依赖完整固定 Plan
```

如果这些不成立，不继续堆 Long-Term Memory、Pattern Learning 或复杂 Cognitive Pressure；先修核心。

## 118. 推荐版本演进

### v1

```text
Evidence-backed World Model
Gap-driven Next Action
Local Revision Loop
```

### v1.1

```text
Negative Evidence / Observation Coverage
Expectation / Anomaly
Structured Hypothesis Premises
Better Decision Readiness
Problem Frame Refinement
```

### v1.2

```text
Cognitive Pressure
Verification / Exploration Policy
Context Routing
Role Isolation
Richer Action Contract
```

### v2

```text
Experience Fragment
Memory Consolidation
Pattern Candidate
Counterexample Learning
Inquiry Policy Learning
Evidence Source Learning
```

## 119. Theory Model ≠ Runtime Module List

理论上概念必须分清，但工程上可以折叠。

例如：

```text
Goal Relation
Pressure
Attention
```

理论上是三个不同对象。

v1 工程上完全可以先由：

```text
DecisionEngine.evaluate(state)
```

统一实现。

原则：

> **Theory Model ≠ Runtime Module List.**

## 120. v1 实现形态建议

```text
single process
modular monolith
CLI first
SQLite / local persistence
read-only tools auto-executable
write / modify actions require confirmation
```

暂不采用：

```text
microservices
graph database
vector infrastructure
multi-agent orchestration
complex distributed state
```

---

# v0.8 一句话定义

> **Cogito-Harness 是一个通过 Goal Contract 与 Evidence Revision 持续建立可修订 World Model，在有界 Cognitive Turn 中围绕最有价值 Information Gap 分配认知资源，并选择下一步最合规、最有信息价值且可验证 Action 的认知循环系统。**

# Cogito v1 一句话定义

> **Cogito v1 是一个使用 Evidence 维护可修订 World Model，并始终围绕当前最有价值 Information Gap 选择下一步可观察 Action 的局部认知循环内核。**

---

# v0.8 新增核心原则

1. **Events 保存发生过什么，Snapshot 表达当前 Cogito 相信什么。**
2. **Derived Views 可重算，不得成为独立 Truth Source。**
3. **Workspace 是投影，不是 Memory。**
4. **Index 是访问基础设施，不是 Knowledge。**
5. **LLM Roles 是受限语义函数，不是自治 Agent。**
6. **LLM Proposal 必须经过 Admission 才能进入正式 Cognition。**
7. **提出解释的 Role 不应成为该解释唯一的 Evidence Judge。**
8. **Uncommitted Cognition 不得偷偷进入后续 Prompt 成为 Truth。**
9. **Missing Prompt Context 与 Missing Reality 必须区分。**
10. **一条新信息先作用于最小认知单元，再沿明确依赖有限传播。**
11. **Belief Transaction Commit 后才重算 Goal Relation、Pressure、Attention 与 Workspace。**
12. **重复或相关 Evidence 不得制造虚假 Belief Amplification。**
13. **Evidence Retraction 必须能够触发反向 Revision。**
14. **一个 Cognitive Turn 必须有明确 Evidence Boundary 与 Decision Boundary。**
15. **没有新的 External Evidence，就不允许无限制造 Epistemic Progress。**
16. **证据不足时，优先分叉 Inquiry，而不是分叉 Hypothesis。**
17. **只有 Scheduler 有权推进 Cognitive Loop。**
18. **运行时 Cognition 采用 Sparse Activation，不是所有请求跑完整模块。**
19. **效率优化可以合并 Role，但不能跨 Cognitive Checks-and-Balances Boundary。**
20. **Cogito v1 首先验证 Evidence-backed World Model + Gap-driven Action + Local Revision。**

---

# 计划不是路线图，而是方向盘。

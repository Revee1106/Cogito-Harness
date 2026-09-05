# Story 1A Acceptance Repair Design

## Context

Story 1A already implements the Cognitive Admission Foundation, but acceptance review
found four gaps: inactive propositions can still create evidence or hypotheses, fact
conflicts are treated as admission failures, material cognition can be committed
without an event trail, and deterministic derivation can be admitted through an
ordinary observation source marker.

This repair remains strictly inside Story 1A. It does not add revision execution,
evidence invalidation, contradiction lifecycle objects, or a derived-fact engine.

## Decision

Use small, explicit invariants in the existing policies and transaction validator.
Reuse `AdmissionResult.reason_codes` and `public_reasons` for non-fatal conflict
diagnostics instead of introducing a diagnostic hierarchy or orchestration service.

## Admission Semantics

### Inactive propositions

- `EvidenceAdmissionPolicy` rejects a new EvidenceLink when its source proposition is
  not `ACTIVE`, with `PROPOSITION_INACTIVE`.
- `HypothesisAdmissionPolicy` rejects the whole proposal with
  `PROPOSITION_INACTIVE` when any ID in `supporting_proposition_ids` resolves to an
  inactive proposition. It never filters invalid sources and continues with a subset.
- `CognitiveTransactionValidator` applies the same source-status guard to newly
  created EvidenceLinks so callers cannot bypass the policy at commit time.

Inactive propositions and historical EvidenceLinks remain stored. No invalidation or
reverse revision behavior is added.

### Fact conflict diagnostics

`FactAdmissionPolicy` evaluates the candidate on its own admission merits. When it is
otherwise admissible, a conflict with an existing active Fact does not remove the
admitted value:

- `decision` is `ADMIT`;
- `value` contains the new Fact and its supporting EvidenceLink;
- `reason_codes` contains `FACT_CONFLICT`;
- `public_reasons` explains the detected conflict.

This is a successful admission carrying a diagnostic. Consumers must determine
success from `decision`, not from whether `reason_codes` is empty.

`CognitiveTransactionValidator` does not report `FACT_CONFLICT` as a validity issue.
Conflicting reliable Facts may coexist as active cognition. Neither policy nor
validator overwrites, supersedes, retracts, or selects a winner.

## Material CognitiveEvent Invariant

Validation is limited to Story 1A material `CREATE` changes:

| Material change | Required event | Required payload |
| --- | --- | --- |
| CREATE EvidenceLink | `EVIDENCE_LINK_ADMITTED` | `relation_id` equals link ID |
| CREATE Fact | `FACT_ADDED` | `object_id` equals Fact ID |
| CREATE Hypothesis | `HYPOTHESIS_CREATED` | `object_id` equals Hypothesis ID |

Every created material item requires its own matching event. Missing or mismatched
events make the transaction invalid with `MISSING_COGNITIVE_EVENT`. Validation does
not infer events, generate events, or define UPDATE/revision mappings.

SQLite keeps its existing append-only, contiguous event-sequence enforcement.
Scenarios A, C, and D will create explicit events in cognitive order and assert the
persisted sequence.

## Deterministic Derivation Boundary

`FactBasis.DETERMINISTIC_DERIVATION` remains in the enum, but the ordinary
Observation/ObservedProposition admission path returns:

- `decision`: `DEFER`;
- `reason_codes`: `DERIVATION_PREMISES_REQUIRED`;
- no admitted Fact or EvidenceLink.

The source-string marker shortcut is removed. A premise graph, rule engine, and
derived-fact proposal are outside this repair.

## Tests

TDD will add failing tests before production changes for:

1. inactive proposition rejection in Evidence and Hypothesis admission;
2. `ADMIT + FACT_CONFLICT` retaining the bundle and committing successfully;
3. conflicting active Facts remaining active with no silent winner;
4. missing material events being rejected for Fact/Evidence and
   Hypothesis/Evidence transactions;
5. matching events being accepted and persisted in sequence, including multiple
   EvidenceLinks;
6. ordinary Observation plus `DETERMINISTIC_DERIVATION` returning the specified
   defer result;
7. scenarios A, C, and D reflecting the repaired behavior.

Full regression includes the complete test suite, branch coverage threshold, package
build, lock validation, architecture dependency scan, credential scan, and available
security audit checks.

## Non-goals

This change does not implement any Story 1B lifecycle, revision, negative evidence,
contradiction object, resolution, attention, memory, anomaly, expectation, or problem
framing capability. Typed Source Fitness remains technical debt.

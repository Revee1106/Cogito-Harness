# Story 1A Acceptance Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair Story 1A admission reliability and cognitive consistency without implementing any Story 1B behavior.

**Architecture:** Add narrow guards to the existing admission policies and an explicit Story 1A material-CREATE event check to the transaction validator. Keep fact conflict detection in Fact admission as a successful diagnostic and let the validator treat epistemic contradiction as legal cognition.

**Tech Stack:** Python 3.14, Pydantic domain models, pytest/pytest-cov, SQLAlchemy SQLite adapter, uv/hatchling.

---

## File Map

- `src/cogito/domain/enums.py`: add the two explicit Story 1A reason codes.
- `src/cogito/domain/policies/evidence.py`: reject inactive source propositions.
- `src/cogito/domain/policies/hypothesis.py`: reject the whole proposal when any supporting proposition is inactive.
- `src/cogito/domain/policies/fact.py`: defer ordinary-observation deterministic derivation and return conflict diagnostics with admitted value.
- `src/cogito/domain/policies/transaction.py`: enforce only the three Story 1A CREATE-to-event mappings and allow conflicting Facts.
- `tests/unit/test_evidence_admission.py`: inactive proposition policy regression.
- `tests/unit/test_hypothesis_admission.py`: all-supporting-propositions-active regression.
- `tests/unit/test_fact_admission.py`: diagnostic admission and deterministic derivation regressions.
- `tests/unit/test_transaction_validator.py`: commit-boundary inactive source, material event, and legal conflict regressions.
- `tests/integration/test_sqlite_store.py`: valid material event persistence and missing-event rejection.
- `tests/integration/test_relations_and_scenario.py`: update material fixtures with matching events.
- `tests/scenarios/test_story_1a_admission.py`: update scenarios A, C, and D and assert ordered event history.

### Task 1: Add RED policy regressions

**Files:**
- Modify: `tests/unit/test_evidence_admission.py`
- Modify: `tests/unit/test_hypothesis_admission.py`
- Modify: `tests/unit/test_fact_admission.py`

- [ ] Add a test proving an inactive proposition yields `REJECT / PROPOSITION_INACTIVE` from Evidence admission.
- [ ] Add a test proving one inactive ID in `supporting_proposition_ids` rejects the entire Hypothesis proposal without filtering.
- [ ] Change the Fact conflict expectation to `ADMIT`, assert the bundle is present, and assert `FACT_CONFLICT` remains a diagnostic.
- [ ] Add a deterministic derivation test that uses an ordinary Observation and expects `DEFER / DERIVATION_PREMISES_REQUIRED` with no value.
- [ ] Run the four focused tests and verify each fails for the intended current behavior.

### Task 2: Add RED transaction and scenario regressions

**Files:**
- Modify: `tests/unit/test_transaction_validator.py`
- Modify: `tests/integration/test_sqlite_store.py`
- Modify: `tests/scenarios/test_story_1a_admission.py`

- [ ] Extend transaction test helpers to accept explicit events.
- [ ] Add a commit-boundary test where a new EvidenceLink has a matching event but
  points to an inactive proposition, and expect `PROPOSITION_INACTIVE`.
- [ ] Add tests rejecting new EvidenceLink, Fact, and Hypothesis material CREATEs when their exact matching event is absent.
- [ ] Add wrong-event-type tests for each of the three Story 1A material CREATE
  mappings.
- [ ] Add tests for missing payload keys and incorrect `relation_id`/`object_id`
  values so matching cannot be implemented as event counting alone.
- [ ] Add a test accepting multiple EvidenceLinks only when each has its own `EVIDENCE_LINK_ADMITTED(relation_id)` event.
- [ ] Replace the conflict-invalid test with a valid transaction assertion.
- [ ] Update Scenario D to commit the admitted diagnostic bundle and prove both Facts remain ACTIVE.
- [ ] Update Scenarios A and C expectations to require ordered persisted events.
- [ ] Run the focused validator, SQLite, and scenario tests and verify RED for the intended missing invariants.
- [ ] Commit the RED checkpoint as `test: add Story 1A acceptance repair regressions` and verify it is reachable from current HEAD.

### Task 3: Implement minimal policy changes

**Files:**
- Modify: `src/cogito/domain/enums.py`
- Modify: `src/cogito/domain/policies/evidence.py`
- Modify: `src/cogito/domain/policies/hypothesis.py`
- Modify: `src/cogito/domain/policies/fact.py`

- [ ] Add `DERIVATION_PREMISES_REQUIRED` and `MISSING_COGNITIVE_EVENT` reason codes.
- [ ] Add the ACTIVE source guard to Evidence admission after source/episode validation.
- [ ] Reject Hypothesis admission if any resolved supporting proposition is inactive.
- [ ] Remove the deterministic source marker and return the specified DEFER result on the ordinary observation path.
- [ ] Construct the Fact/Evidence bundle before conflict reporting and return `ADMIT` with diagnostic reason/public text when conflicts exist.
- [ ] Run the policy tests and verify GREEN.

### Task 4: Implement the narrow transaction event invariant

**Files:**
- Modify: `src/cogito/domain/policies/transaction.py`
- Modify: `tests/integration/test_relations_and_scenario.py`
- Modify: `tests/integration/test_sqlite_store.py`
- Modify: `tests/scenarios/test_story_1a_admission.py`

- [ ] Reject newly created EvidenceLinks whose source proposition is inactive.
- [ ] Remove Fact conflict from structural transaction issues.
- [ ] For CREATE only, match every EvidenceLink to `EVIDENCE_LINK_ADMITTED` by `relation_id`.
- [ ] For CREATE only, match every Fact to `FACT_ADDED` by `object_id`.
- [ ] For CREATE only, match every Hypothesis to `HYPOTHESIS_CREATED` by `object_id`.
- [ ] Do not infer or validate Story 1B UPDATE/revision mappings.
- [ ] Add the exact matching events to existing valid fixtures and Scenarios A/C/D.
- [ ] Run all affected unit, integration, and scenario tests and verify GREEN.
- [ ] Commit the GREEN checkpoint as `fix: enforce Story 1A acceptance invariants` and verify it is reachable from current HEAD.

### Task 5: Full verification and acceptance audit

**Files:**
- Modify only if verification exposes an in-scope regression.

- [ ] Run `uv sync --extra dev` using the repository's available uv runtime.
- [ ] Run `uv run pytest`.
- [ ] Run `uv run pytest --cov=cogito --cov-branch --cov-report=term-missing` and verify at least 80%.
- [ ] Run package build and lock validation.
- [ ] Run architecture dependency and credential scans using repository conventions.
- [ ] Run an available Python security audit without changing dependency scope.
- [ ] Review `git diff` and commit reachability; confirm no Story 1B symbols or behaviors were introduced.
- [ ] Produce the requested 19-point acceptance repair report and list additional findings separately.

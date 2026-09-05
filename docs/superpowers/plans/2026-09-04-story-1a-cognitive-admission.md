# Story 1A Cognitive Admission Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Implement deterministic, auditable admission laws for Facts, EvidenceLinks, Hypotheses, draft targets, transaction consistency, and Fact conflicts without implementing Story 1B belief revision.

**Architecture:** Keep semantic outputs as proposal models and implement admission as pure domain policies returning structured results. Represent reserved targets explicitly, validate complete cognitive transactions against committed plus same-transaction objects/relations, and let the SQLite adapter remain responsible only for atomic persistence. Exercise the public policy and transaction surfaces with unit and synthetic integration scenarios.

**Tech Stack:** Python 3.14, Pydantic v2, pytest, SQLAlchemy/SQLite, uv.

---

### Task 1: Freeze the Story 1A domain vocabulary

**Files:**
- Modify: `src/cogito/domain/enums.py`
- Create: `src/cogito/domain/models/admission.py`
- Create: `src/cogito/domain/proposals/fact.py`
- Modify: `src/cogito/domain/proposals/hypothesis.py`
- Modify: `src/cogito/domain/models/fact.py`
- Test: `tests/unit/test_proposals.py`
- Test: `tests/unit/test_admission_models.py`

- [x] Write tests for `FactBasis`, `SemanticEntailment`, admission decisions/reason codes, proposal/committed separation, and candidate proposition references.
- [x] Run the focused tests and verify they fail because the Story 1A types do not exist.
- [x] Add the minimal enums, structured `AdmissionResult`, `FactProposal`, and corrected `HypothesisProposal`.
- [x] Preserve Fact basis as committed provenance and validate temporal ranges.
- [x] Run focused tests to green.

### Task 2: Implement draft target reservation and Evidence admission

**Files:**
- Create: `src/cogito/domain/models/draft.py`
- Implement: `src/cogito/domain/policies/evidence.py`
- Test: `tests/unit/test_evidence_admission.py`

- [x] Write failing tests for the FACT/HYPOTHESIS/GAP compatibility matrix, missing source/target, episode/type mismatch, NEUTRAL, deduplication, relation conflict, and draft targets.
- [x] Run the focused tests and verify the expected failures.
- [x] Add a small explicit reservation helper and pure `EvidenceAdmissionPolicy`.
- [x] Run focused tests to green and refactor shared target-type logic.

### Task 3: Implement Fact admission and conflict detection

**Files:**
- Create: `src/cogito/domain/policies/fact.py`
- Test: `tests/unit/test_fact_admission.py`

- [x] Write failing tests for entailment, active/current proposition, scope/time containment, basis/source fitness, atomic Fact+SUPPORTS bundle, and conflicting active Facts.
- [x] Run the focused tests and verify the expected failures.
- [x] Implement `FactAdmissionPolicy` with structured public reasons and no confidence score.
- [x] Run focused tests to green.

### Task 4: Implement Hypothesis admission

**Files:**
- Implement: `src/cogito/domain/policies/hypothesis.py`
- Test: `tests/unit/test_hypothesis_admission.py`

- [x] Write failing tests for candidate propositions, admitted SUPPORTS evidence, same Episode, testable expectation, and PLAUSIBLE-only creation.
- [x] Run the focused tests and verify the expected failures.
- [x] Implement `HypothesisAdmissionPolicy` without status mutation or evidence-count scoring.
- [x] Run focused tests to green.

### Task 5: Implement cognitive transaction validation

**Files:**
- Create: `src/cogito/domain/policies/transaction.py`
- Modify: `src/cogito/adapters/sqlite/store.py`
- Modify: `src/cogito/domain/models/episode.py`
- Test: `tests/unit/test_transaction_validator.py`
- Modify: `tests/integration/test_sqlite_store.py`
- Modify: `tests/integration/test_relations_and_scenario.py`

- [x] Write failing tests for same-transaction targets, missing drafts, evidence refs, target types, mixed episodes, reserved targets without CREATE, conflicting changes, lifecycle boundaries, and Fact conflicts.
- [x] Run the focused tests and verify the expected failures.
- [x] Implement the pure validator and call it inside the atomic store transaction using committed objects/relations.
- [x] Expose propositions in the rebuildable episode state without leaking ORM types.
- [x] Update legacy persistence fixtures so every committed relation/object is cognitively valid.
- [x] Run unit and integration tests to green.

### Task 6: Implement the four Story 1A scenarios

**Files:**
- Create: `tests/scenarios/test_story_1a_admission.py`
- Optionally create: `src/cogito/scenarios/admission.py`

- [x] Write Scenario A for direct measurement to atomic Fact admission.
- [x] Write Scenario B for rejecting `connection refused` → `database is down` with no version increase.
- [x] Write Scenario C for two propositions/evidence links to one PLAUSIBLE Hypothesis in one transaction.
- [x] Write Scenario D for detecting an overlapping active Fact value conflict.
- [x] Run the scenario tests and implement only the orchestration needed to pass them.

### Task 7: Verify Story 0 regression and Definition of Done

**Files:**
- Modify only if required: `tests/conftest.py` for a narrowly scoped Python 3.14/Windows pytest temp-directory compatibility fix.
- Review: all changed source and test files.

- [x] Run `python -m uv sync --extra dev` with workspace-local uv cache/Python paths.
- [x] Run all tests under Python 3.14.
- [x] Run branch coverage and confirm it is at least 80%.
- [x] Build the package and check the lock file.
- [x] Scan imports for forbidden Domain dependencies and scan tracked files for credential patterns.
- [x] Review `git diff` against every Story 1A DoD item and confirm no Story 1B behavior was added.

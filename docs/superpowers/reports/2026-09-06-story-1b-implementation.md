# Story 1B implementation and acceptance evidence

Date: 2026-09-06. Status: implementation complete; ready for independent code review, not yet formally frozen.

Branch: `codex/story-1b-local-revision-engine`.
Base: `51ce1f83de2e060a28365bb7353a8cdc4d7fdcde`.
Canonical theory v0.9, overall development v0.2 and Story 1B v0.1 were read in order and were not changed.

## Implemented surface

- `HypothesisSupportBasis`: DIRECT_OBSERVATION, INDEPENDENT_CORROBORATION, DISCRIMINATIVE_EVIDENCE, PREDICTION_CONSISTENT.
- `RejectionBasis`: DIRECT_CONTRADICTION, DISCONFIRMING_CONDITION_MET.
- `SemanticDirectness`: DIRECT, NOT_DIRECT, AMBIGUOUS.
- `TemporalSuccessionBasis`: LATER_DIRECT_OBSERVATION, EXPLICIT_STATE_TRANSITION, VERSIONED_ARTIFACT_SUCCESSION.
- Separate Strengthen, Reject and FactSupersede proposals; no generic revision proposal or Gap proposal.
- `RevisionStatus`, `RevisionResult`, `RevisionBatch`, internal `PolicyEffect` and focused reason codes.
- EpisodeState exposes committed EvidenceLinks and ordered CognitiveEvents; no new tables or migrations.
- Pure `LocalRevisionEngine.revise(state, batch, base_version, now=...)` builds, but does not commit.
- Existing Story 0 `RevisionEngine` import is a compatibility alias to this single implementation.

## Policies and boundaries

All supplied basis Evidence must exist, belong to the episode, target the requested object with the correct relation, and reference ACTIVE Propositions. Invalid inputs are not silently filtered.

Strengthen requires an explicit proposal. Counts never trigger revision. DIRECT_OBSERVATION checks traceable source markers; corroboration requires distinct propositions and independently available observation/source-reference provenance; prediction consistency requires a nonblank prediction. Discriminative semantics remain explicit proposal input.

Committed strengthen events record target, support basis and consumed Evidence IDs. Repeats, reordered sets and consumed subsets return NO_MATERIAL_CHANGE across store reopen. New structural support on a SUPPORTED Hypothesis creates material provenance without escalating status.

Reject requires an explicit proposal. CONTRADICTS alone does nothing. DIRECT permits further validation; NOT_DIRECT is an insufficient proposal; AMBIGUOUS or absent directness defers. Known subject/scope disagreements with retained supporting propositions are rejected conservatively. No numeric confidence is used.

Condition-based rejection requires a nonblank condition and a matching committed HYPOTHESIS_CREATED condition snapshot. Its event sequence must precede the triggering Observation, Proposition and EvidenceLink creation/admission events, in a different transaction. Missing proof, later conditions or same-transaction conditions defer. No history is backfilled or inferred from created_at.

Hypothesis rejection changes only status/updated_at. It preserves original evidence_refs and all relations. Rejection basis and rejected-by Evidence IDs live in append-only event payloads. REJECTED is terminal for this implementation, with no reopen behavior.

GapResolutionPolicy consumes an explicitly supplied admitted RESOLVES link. OPEN/FOCUSED becomes RESOLVED; duplicate resolution is non-material. It never chooses another Gap, completes a Goal or selects an Action.

Fact supersession requires both Facts, compatible structured subject/predicate/scope and the same basis/semantic layer. Replacement remains ACTIVE and both Facts remain stored. Basis links must support the replacement and occur in its evidence_refs.

- Later direct observation: replacement is DIRECT_MEASUREMENT with direct provenance. Compare aware valid_from/valid_to or traceable observed_at; missing, equal, reversed, overlapping or naive time boundaries defer. created_at is never world time.
- Explicit transition: requires typed `transition_match=DIRECT` with evidence bound to the Fact pair; no model invocation.
- Versioned artifact: requires ARTIFACT_CONTENT on both sides, explicit shared artifact identity matching source_ref and increasing integer version ordinals. Ordinals are versions, not confidence scores. Artifact succession cannot establish runtime succession.
- Plain conflict does not trigger revision. Ambiguous ordering defers while preserving both ACTIVE Facts and the cognitive version.

## Batch and commit contract

RevisionBatch has one required nonblank cause_id and four explicit input collections. Policies evaluate the supplied committed state. Any deferred member defers the entire cause. Conflicting effects on the same target, or a batch that also supersedes its own replacement Fact, defer without priority selection.

Material effects produce one CognitiveTransaction with one base_version, consecutive events and matching local ObjectChanges. Exact duplicate inputs coalesce. Engine output cannot update implicit neighbors and has no Store, ModelProvider, Tool, search, ask-user, retry or scheduler dependency.

RevisionResult enforces transaction presence exactly for MATERIAL_CHANGE and requires affected IDs to equal actual transaction updates. NO_MATERIAL_CHANGE and DEFERRED have no transaction or affected updates. Callers branch on status/transaction, not whether diagnostic reason_codes is empty.

The existing transaction validator dispatches only four known revision event types and re-evaluates their explicit proposal/basis against current committed objects, relations and history. It compares the entire expected object and event payload, preventing missing/wrong events, unrelated field rewrites, consumed strengthen effects and fabricated provenance. Revision transactions cannot mix source changes or Evidence mutations into their target updates. Creation snapshots, when supplied, must describe an actual corresponding CREATE; condition snapshots must equal the created condition.

SQLite keeps history insertion, projection writes and one cognitive_version increment inside its existing database transaction with base_version checking. Current events are supplied to validation, and the state reader hydrates evidence/history. Type-change errors remain compatible with Story 0 behavior. Failure injection covers invalid payloads, missing events and a real event primary-key collision; all roll back without partial state.

## Caller example

```python
from cogito.application.local_revision_engine import LocalRevisionEngine
from cogito.domain.models.revision import RevisionBatch
from cogito.domain.proposals.revision import HypothesisStrengthenProposal

state = await store.load_episode_state(episode_id)
batch = RevisionBatch(
    cause_id="probe-result-42",
    hypothesis_strengthen_proposals=(HypothesisStrengthenProposal(
        hypothesis_id=hypothesis_id,
        evidence_link_ids=(admitted_evidence_id,),
        support_basis="DIRECT_OBSERVATION",
        reason="The admitted direct probe supports the claim.",
    ),),
)
result = LocalRevisionEngine().revise(state, batch, state.episode.cognitive_version)
if result.transaction is not None:
    await store.commit_transaction(result.transaction)
```

For newly admitted Hypotheses intended to support condition-based rejection, the admission caller should include both `object_id` and the exact `disconfirming_condition` in its HYPOTHESIS_CREATED payload. Legacy events lacking this optional snapshot remain readable and admissible for Story 1A compatibility, but cannot prove prior-condition rejection. Story 1B does not invent snapshots or build a new admission orchestrator.

## Test evidence

RED/GREEN batches are recorded in the companion implementation plan. Final test collection:

| Area | New cases |
| --- | ---: |
| Strengthen | 19 |
| Reject | 22 |
| Gap | 9 |
| Fact | 22 |
| Engine/result/batch | 13 |
| Transaction validation | 43 |
| SQLite integration and synthetic A-E scenarios | 12 |
| Total | 140 |

All 90 prior tests remain unchanged. Full regression: **230 passed**, including the five deterministic A-E scenarios and persistence/rollback/reopen checks. The expected SQLAlchemy warning from intentional primary-key collision is explicitly asserted by the test, not globally suppressed.

Coverage-enabled run: **230 passed**, combined statement+branch coverage **91.96%**. Statements: 1657/1759 (94.20%); branches: 378/454 (**83.26%**). Both combined and branch-only measures exceed 80%. LocalRevisionEngine has 100% coverage.

## Reproducible verification

The local uv launcher is `python -m uv`; environment/cache paths stay inside ignored workspace directories.

```powershell
$env:UV_CACHE_DIR='E:\Cogito-Harness\.uv-cache'
$env:UV_PYTHON_INSTALL_DIR='E:\Cogito-Harness\.uv-python'
python -m uv sync --extra dev
python -m uv run pytest
python -m uv run pytest --cov=cogito --cov-branch --cov-report=term-missing
python -m uv lock --check
python -m uv build --out-dir .test-tmp/story-1b-dist
```

- Sync and lock: PASS, 25 resolved packages; no dependency/lock changes.
- Build: wheel and source archive PASS. Archive inspection confirms engine inclusion and excludes .venv/.uv-cache/.uv-python/.test-tmp/.git. uv's in-tree-cache warning is non-fatal and checked against actual contents.
- Architecture: AST import scan passes Domain isolation from Application/adapters/ORM/model SDKs and Application isolation from adapters/ORM/agent frameworks. Engine call scan confirms no commit/model/tool/search dependency.
- Credential pattern scan: no matches in source, tests, docs, README or manifests for common access-token/private-key patterns. This is a scoped pattern scan, not a guarantee against every possible secret encoding.
- Dependency audit: cached pip-audit 2.10.1 run against `.venv/Lib/site-packages`, skipping the editable local project; no known vulnerabilities. Audit did not install project dependencies or modify the lock. Initial sandboxed network attempt was stopped and the authorized read-only network audit succeeded.
- Scope/diff: no canonical-document, README, old-test, dependency, lock or Alembic changes. No real Model/Tool integrations, Story 2 behavior or new agent framework.

## Known limits and review handoff

1. Source Fitness retains Story 1A's string-marker technical debt. Marker checks are structural screening, not full typed provenance certification.
2. Hypothesis has no structured entity/scope/time claim model. Directness, discriminative support, explicit transition and artifact version order are explicit semantic inputs, with available structural checks; no natural-language or general temporal reasoning is claimed.
3. Missing legacy condition history defers, even if a person believes the condition was present earlier. No reliability boundary was relaxed to admit such cases.
4. Fact compatibility is deliberately conservative: exact known subject/predicate/scope/basis and aware temporal boundaries. Unsupported but potentially valid cases defer.
5. Reading history uses the existing local, serialized-caller SQLite model. No new concurrency scheduler, event index, dependency graph or persistence system was introduced.
6. The pre-existing CONFIRMED enum and Story 0 scheduler placeholders are untouched; no CONFIRMED transition or Story 2 runtime is implemented.

No known incomplete Story 1B Definition of Done item or implementation blocker remains. Recommend independent code review, then a separate explicit freeze/merge task. This task only pushes the Story 1B branch; main must remain at the documentation merge base. Final local/remote hashes and push outcome are reported in the task handoff rather than embedded recursively into this commit.

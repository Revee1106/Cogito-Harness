# Story 1B Freeze Acceptance Fix

Date: 2026-09-06. Scope: only P0-1 and P0-2 from the independent Conditional Pass review.
Starting commit: `a1b0dd17c061bdd35f093b64979d5a55c87008f4`.
Branch: `codex/story-1b-local-revision-engine`; main is not merged or changed by this task.

## P0-1 — creation provenance

Reproduced before the fix: a nonblank condition with an object-id-only HYPOTHESIS_CREATED event was considered valid, and SQLite accepted the transaction. The acceptance tests failed at both validation and commit boundaries (2 failed, 8 passed before the fix).

The existing `revision_issues` helper, called by CognitiveTransactionValidator, now requires the condition key on a matching creation event whenever the created Hypothesis has a nonblank condition. The existing equality check rejects inconsistent snapshots. Existing material-CREATE event checks still require matching object_id and event type. No RejectPolicy rule was relaxed and no history was rewritten or inferred.

None, empty and whitespace-only conditions do not require the payload key. If a snapshot is supplied, its equality constraint still applies.

Ten new tests cover matching, missing, different, null and blank snapshots; None/empty/whitespace conditions; rejected SQLite commit without partial state; and an end-to-end earlier committed condition snapshot followed by later contradictory Evidence and successful condition-based rejection.

The existing missing-prior-history test still returns DEFERRED. Its legacy input is now explicitly a read-view fixture with missing snapshot metadata, derived without modifying persisted events; the normal seed helper always writes the snapshot. All prior posthoc, wrong-snapshot, same-transaction and missing-history tests remain intact.

Story 1A fixtures required no changes: the checked Hypothesis CREATE fixtures use predictions without nonblank conditions. Story 1A admission semantics and tests are unchanged. Related P0-1 regression: 72 passed.

## P0-2 — artifact version provenance

Reproduced before the fix: shared artifact source_ref plus Proposal ordinals 17/18 or 0/999999 produced a material supersession. Engine accepted both single and mixed batches, Validator accepted a manually forged equivalent transaction, and SQLite committed it. Eight new acceptance cases were RED before the fix.

Inspection of Observation, ObservedProposition, Fact, EvidenceLink and proposal fields found no existing admitted artifact-version/ordering provenance contract. Generic `value`, raw content and source_ref do not define such a contract. Interpreting arbitrary values, reason text or filename suffixes as version proof would invent a new mechanism, so it was not done.

After existing target, episode, status, semantic-layer and Evidence checks, VERSIONED_ARTIFACT_SUCCESSION now returns:

```text
DEFERRED
VERSION_PROVENANCE_INSUFFICIENT
transaction = None
```

The enum and Proposal fields remain compatible, but the unsupported material artifact-version path is intentionally unavailable. Proposal ordinals are not read as world facts. The old `_artifact_succeeds` comparison helper was removed. No Artifact model, registry, resolver, metadata subsystem, version graph or new provenance convention was introduced.

Engine and Validator continue using the same FactSupersedePolicy. No separate validator exception or weaker acceptance route was added. Forged transactions are rejected before persistence; both Facts and the complete prior state remain unchanged. A mixed strengthen/resolve/version batch defers as a whole.

Eight new tests cover four ordinal combinations, single/mixed batch deferral, validator replay rejection, and actual SQLite rejection without partial state. The prior artifact-success test was minimally updated to require provenance deferral. The runtime semantic-layer test, later direct observation and explicit transition cases remain unchanged. Related P0-2 regression: 86 passed.

## Full verification

Environment: Python 3.14.7; existing uv-managed dev environment. No project dependency, lock, schema or migration change.

| Check | Result |
| --- | --- |
| `uv sync --extra dev` | PASS; 25 resolved packages |
| `uv run pytest` | 248 passed |
| branch-enabled coverage run | 248 passed; 92.03% combined coverage |
| pure branch coverage | 371/446 = 83.18% |
| `uv lock --check` | PASS |
| package build | PASS: wheel and source archive |
| artifact inspection | No .venv/.uv-cache/.uv-python/.test-tmp/.git leakage |
| architecture AST/import scan | PASS: Domain and Application boundaries preserved |
| engine call/scope scan | PASS: no commit/model/tool/search/scheduler additions |
| credential pattern scan | No common token/private-key pattern matches |
| dependency audit | No known vulnerabilities; editable local distribution skipped |
| diff check | PASS |

Test count: 230 previous cases retained, plus 10 P0-1 and 8 P0-2 cases = 248. Two existing Story 1B test areas were adjusted only for the new acceptance rules. No baseline test was deleted. Combined coverage rose from 91.96% to 92.03%; pure branch coverage changed from 83.26% to 83.18% after removing the unsafe path and adding checks. Both remain above 80%.

Commands used the local `python -m uv` launcher and ignored workspace cache/runtime directories. Build output was `.test-tmp/story-1b-acceptance-dist`. The in-tree-cache build warning was checked against actual archives. Credential checking is a scoped pattern scan, not a guarantee against every secret encoding. Dependency auditing did not modify project dependencies.

## Scope and freeze handoff

- Production changes are limited to the condition snapshot invariant, one reason code and the artifact-version policy restriction.
- No Canonical document, README, Domain object shape, RejectPolicy, other Temporal Basis implementation, Engine orchestration, store implementation or dependency was changed.
- No version Observation/Fact was fabricated or automatically admitted. Synthetic tests supply the existing artifact-content fixtures without version claims; the engine creates no new source objects.
- No Model/Tool integration, automatic evidence seeking, Story 2 behavior, Source Fitness refactor, reverse revision or event-history rewrite was introduced.
- The earlier implementation report is marked historical where it conflicts with these tightened requirements.
- Both reviewed P0 defects are closed by the tested acceptance rules. Artifact-version material revision remains conservatively deferred until a future explicitly designed admitted provenance contract exists; this is the requested safe outcome, not an inferred capability.
- Recommend final independent freeze review. Formal freeze/merge remains a separate authorized task.
- One acceptance-fix commit is intended, followed by an ordinary push of the existing Story 1B branch. Final commit hash, push result and clean-tree evidence are provided in the task handoff so the report does not embed its own recursive commit hash.

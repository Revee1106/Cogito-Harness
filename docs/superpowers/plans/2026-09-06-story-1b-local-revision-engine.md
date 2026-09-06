# Story 1B implementation and verification plan

Canonical basis: theory v0.9, overall development v0.2, Story 1B v0.1.

## Implementation decisions

- Pure synchronous policies evaluate explicit proposals against committed EpisodeState.
- Extend the rebuildable state with admitted EvidenceLinks and ordered CognitiveEvents; no new tables.
- Policies return a local effect; the application engine combines effects into one transaction.
- A deferred member defers the entire batch (no partial transaction). Conflicting effects on one target defer rather than choose precedence.
- Strengthen consumption is keyed by target, support basis and EvidenceLink IDs in committed revision events. Reordering/subsets do not repeat effects.
- Reject proposals carry explicit semantic directness. Invalid and insufficient requests return DEFERRED with distinct reason codes; only already-applied effects return NO_MATERIAL_CHANGE.
- Historical condition validation requires a matching condition snapshot in a committed HYPOTHESIS_CREATED event preceding all triggering observation/proposition/link events, in an earlier transaction. Legacy history without proof defers.
- Direct observation uses the existing Source Fitness markers, conservatively excluding report/artifact sources. No Source Fitness redesign.
- Fact identity/predicate/scope/basis must match. World time uses aware valid_from/valid_to or traceable observed_at; never created_at. Artifact ordering and explicit transition semantics are typed, explicit inputs bound to the Fact pair and Evidence.
- Validator covers only the four Story 1B UPDATE kinds, checks full event metadata and replays the corresponding policy against committed state before accepting the update. No generic future event inference.

## RED / GREEN batches

1. A: typed Strengthen proposal, basis checks, active evidence validation, deduplication.
2. B: Reject, directness, prior-condition history, preservation of evidence.
3. C: Gap resolution, no implicit focus/goal/action changes.
4. D: temporal Fact supersession and unresolved conflict.
5. E: RevisionResult/Batch, local engine, validator, SQLite atomic integration and synthetic A-E scenarios.

## Completion checks

- Full pytest and branch coverage >= 80%; all 90 pre-existing cases pass.
- uv sync, lock check, build, architecture scan, credential scan and dependency audit.
- Inspect diff and out-of-scope scan; no dependency changes or Story 2 implementation.
- Commit logical batches and push only codex/story-1b-local-revision-engine.

## Executed evidence

- A: 19 RED cases (missing proposal/policy/state view), then 19 GREEN.
- B: 20 RED cases (missing Reject contract), then A+B 39 GREEN.
- C: 9 RED cases (missing Gap policy), then A-C 48 GREEN.
- D: 22 RED cases (missing Fact policy), then A-D 70 GREEN.
- E engine: 11 RED cases, then 81 GREEN across revision tests.
- E validator: 39 RED cases (missing committed-history input), then 120 GREEN.
- E SQLite/scenarios: 12 RED cases (missing hydrated relations/history), then full regression 222 GREEN.
- Boundary hardening: four additional RED cases for obvious rejection entity/scope mismatch and superseding a batch replacement, then GREEN.
- Compatibility/malformed payload: two RED cases plus two already-passing defensive cases, then GREEN.
- Final full regression: 230 passed; all 90 baseline tests unchanged, 140 new tests.
- Branch-enabled total coverage: 91.96%; branch-only: 378/454 = 83.26%.
- Sync, lock, build, architecture, credential-pattern scan and dependency audit passed.
- See the implementation report for reproducible commands, limits and handoff guidance.

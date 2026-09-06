# Story 1B Final Freeze Documentation Alignment

Date: 2026-09-06. Production baseline: `bc6b3e9ad47426ebf9b93d7e540b8063fc6082a4`.

The independent review closed both P0 issues and passed production code. This documentation-only change removes the remaining mismatch between the Canonical Story and the accepted runtime behavior; it introduces no new design.

## Alignment

- Story v0.1 Section 22 now distinguishes a theoretically valid TemporalSuccessionBasis from currently unavailable material artifact-version revision. Enum, Proposal shape, Policy branch and reason code remain retained.
- Current Domain has no reliable admitted/committed artifact-version provenance contract proving version values, ordering and artifact identity succession. After the existing structural checks, this path returns DEFERRED / VERSION_PROVENANCE_INSUFFICIENT, with no CognitiveTransaction and no cognitive_version increase.
- Proposal version numbers, source_ref, filenames, reason text and created_at cannot independently establish succession. Future material enablement requires committed, traceable provenance in a later Story; no future Story number or subsystem is invented.
- Section 39 replaces the outdated successful artifact-version test expectation with provenance deferral. Section 46 explicitly lists the retained shape, reason code and non-material outcome in DoD.
- Other sections, including LATER_DIRECT_OBSERVATION, EXPLICIT_STATE_TRANSITION and Integration Scenarios A–E, remain unchanged. The scenarios contain no conflicting artifact-version success expectation.

## Protected scope

Theory v0.9 remains unchanged: the Basis is legally defined at the theoretical level. Overall Development v0.2 contains no explicit claim that this material artifact-version path currently works, so it also remains unchanged.

Production code, tests, dependencies, uv.lock, migrations, root README, docs/README and both existing acceptance reports remain unchanged. README status updates are reserved for the separately authorized freeze/merge phase. The Story 1B branch is pushed without merging main.

## Verification

- Full regression: 248 passed; no tests added, removed or modified.
- Coverage regression: 248 passed; combined statement/branch coverage 92.03%, with pure branch coverage 83.18% (371/446), both above 80%.
- Lock check and package build: PASS.
- Architecture dependency scan and credential pattern scan: PASS.
- Existing dependency audit: no known vulnerabilities; the editable local project was skipped.
- Section-by-section comparison confirms only Sections 22, 39 and 46 changed; Markdown fences remain balanced and the obsolete success expectation is absent.

Theory (valid basis), Story (current non-materializing capability) and Code (provenance-insufficient deferral) now express compatible behavior. Recommend final freeze confirmation followed by a separate merge task; this alignment task does not perform that merge.

# Economic Cycle Research — Version 2.0 descriptive release candidate

Date: 2026-10-31
Scope: Single offline research dashboard, **not** a predictive crash model.

## Implemented
- Canonical eight crash-parent clusters and 444 monthly historical observations, read-only from the existing research snapshot.
- Exact prior-month crash-context matching, 24-month financial trajectories, canonical lead-window summaries and explicit missingness.
- Current revised macro, financial/housing context and crash-mechanism evidence gaps.
- Historical-to-current side-by-side comparison with explicit frequency, transformation and unemployment-level-versus-change incompatibilities.
- Eight international transmission channels with candidate primary sources and explicit historical/current observation coverage (currently zero).
- Source readiness and predictive publication gates; integrated HTML and JSON dashboard state.
- Regression and workflow tests.

## Release gates
1. GitHub Actions must succeed on the release-candidate HEAD, including V2 acceptance and dashboard smoke checks.
2. Inspect the generated dashboard HTML and JSON state from the same run; verify every integrated panel and no unreplaced template markers.
3. Verify the acceptance JSON reports checks_passed=true, publication=BLOCKED and predictive_model=NOT_VALIDATED.
4. Confirm canonical snapshot provenance, checksum, and source quality warnings remain attached.
5. Do not call this a validated predictor or describe the monthly baseline as independent, verified non-crash controls.

## Known evidence limitations
- Historical macro/financial inputs are revised, not publisher-original point-in-time vintages.
- International channels are an evidence inventory, not observed historical or current transmission measurements.
- Canonical pathway labels and independent non-crash outcomes are not fully verified for predictive analysis.
- Current-versus-historical measurements are not yet normalized for comparable transformations, dates and release vintages.
- No validated stage, crash probability, vulnerability score, sector forecast, or investment recommendation.

## Release decision
**DESCRIPTIVE RELEASE CANDIDATE** — conditional on the five release gates above. Predictive publication remains **BLOCKED**. Finish this descriptive release independently of future evidence acquisition.

## Verified prior CI
Run 41221003722 passed at commit a0a1747665587b550fc7d579154ab22d20801b0f. A new run on the release-document HEAD must be verified before final acceptance.

## Artifact inspection — 2026-10-31
Verified GitHub Actions run **41222896939** on commit **51e157addd0aba17641e58dc5b81d4827b8a0524**: job successful, evidence ZIP artifact **13050448454** downloaded and inspected (21 files).

- `audit-output/v2_m1_acceptance.json`: `M1_ACCEPTANCE_CANDIDATE`, `checks_passed=true`, `issues=[]`, predictive model `NOT_VALIDATED`, publication `BLOCKED`.
- `dashboard/index.html`: integrated current/historical bridge, international transmission and mechanism evidence gaps present; labor comparability warning present; no unreplaced `V2BRIDGE` or `V2GLOBAL` tokens.
- `dashboard/state.json`: publication `BLOCKED`.
- **Important unresolved release condition:** `dashboard/v1_acceptance.json` reports `INCOMPLETE`, with `HISTORICAL_COMPARISON_NOT_POPULATED` and `CURRENT_MACRO_VALUES_MISSING`. A successful CI job is not equivalent to completed V1 acceptance or current-data acquisition.
- Seven scheduled/manual API acquisition and historical-analysis steps were skipped on the push event.

**Decision:** V2 integrated descriptive dashboard passes its scoped acceptance gate, but the combined product is **NOT FULLY ACCEPTED** until the inherited V1 acceptance gaps are resolved or formally scoped and disclosed. Do not misrepresent absent current observations as current economic readings.

## Formal descriptive V2 acceptance — 2026-10-31

**ACCEPTED FOR DESCRIPTIVE RESEARCH SCOPE.** GitHub Actions run [41225609570](https://github.com/landrumc16/Economic-Cycle-Research/actions/runs/41225609570), commit `80f6dd528ac7c32b24b98dbb57e56bcbe052f425`, completed successfully. Inspected downloaded artifact `milestone1-audit-evidence` (ID `13051812755`).

- `v2_release_acceptance.json`: `V2_DESCRIPTIVE_RELEASE_ACCEPTED`, `checks_passed=true`, `issues=[]`.
- `v2_m1_acceptance.json`: `M1_ACCEPTANCE_CANDIDATE`, `checks_passed=true`, `issues=[]`.
- Dashboard HTML: all four V2 sections and explicit unemployment transformation warning present.
- Dashboard state: 8 canonical parent clusters; 8 global channels with **0 historical** and **0 current** observed global channels; `publication=BLOCKED`.
- Inherited `v1_acceptance.json`: `INCOMPLETE`, solely `HISTORICAL_COMPARISON_NOT_POPULATED` and `CURRENT_MACRO_VALUES_MISSING`; both preserved as `disclosed_source_gaps` in final release report.
- **Not accepted:** live/current macro coverage, predictive probabilities, validated cycle stage, original-vintage point-in-time certification, independently verified noncrash controls, or global observation acquisition.

This is a finished **descriptive research dashboard release** with transparent source-coverage limitations, not a complete live economic-monitoring or predictive product. Future work on those missing capabilities is separate from this accepted scope.

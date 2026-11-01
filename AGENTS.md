# AI-assisted development rules — Economic Cycle Research

Applies to ChatGPT, Claude, Codex, and other coding agents working in this repository.

Inspired by Andrej Karpathy's practical AI-coding principles; this is a project-specific adaptation, not a quotation or an endorsement by Karpathy.

## 1. Think before coding
- Read the relevant existing implementation, tests, and current milestone before editing.
- State the actual problem, expected behavior, and the smallest coherent solution.
- If requirements are ambiguous in a way that changes the result, identify the uncertainty. Otherwise make a sensible choice and proceed.
- Never claim a workflow passed or a data result was validated without evidence.

## 2. Simplicity first
- Prefer existing scripts, interfaces, data formats, and workflow steps over new infrastructure.
- Do not add abstractions, configuration, dependencies, or new indicators without a demonstrated need.
- Keep retrospective research, live assessments, and validated forecasts clearly separated.

## 3. Surgical changes
- Change only the files needed to solve the current problem.
- Preserve established contracts and avoid unrelated refactoring.
- Keep each change reviewable; add focused regression tests for corrected behavior.

## 4. Verify, then report
- Run the narrowest relevant tests, then end-to-end checks when possible.
- Inspect generated outputs, not just exit codes. Verify dates, missingness, source vintage, and release guards.
- Distinguish: committed / tests run / workflow passed / empirical findings validated.
- If execution cannot be verified, state the blocker and next verification step.

## 5. Finish the milestone
- Current priority: complete and verify Version 4. No new feature work unless required for release.
- Work in substantial, goal-oriented batches; avoid micro-approvals and repetitive planning.
- Definition of done: a successful end-to-end workflow, coherent dashboard and historical artifacts, passing release gates, and documented limitations.
- Do not call Version 4 complete based solely on GitHub commits.

## Research integrity
- Current-vintage FRED observations are not historical point-in-time releases.
- Retrospective associations are not causal findings or validated crash probabilities.
- Do not backfill, silently impute, or invent data to satisfy acceptance checks.

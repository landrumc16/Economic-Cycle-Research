# START HERE — Economic Cycle Research

This is the canonical **navigation entrypoint**, not a replacement for research authority.

## Every new session, in this order
1. Read [PROJECT_STATUS.md](PROJECT_STATUS.md) for the current checkpoint, blockers and next authorized chunk.
2. Read [docs/ROADMAP.md](docs/ROADMAP.md) for phases, gates and scope.
3. Read [docs/EXISTING_RESEARCH_RECONCILIATION.md](docs/EXISTING_RESEARCH_RECONCILIATION.md) before touching historical research.
4. Read the latest relevant handoff in [docs/chat-handoffs/](docs/chat-handoffs/).
5. Verify current `milestone-1-data-pipeline` HEAD, PR #1 and actual GitHub Actions results; never treat a historical run as current.
6. Check the canonical workbook's source/approval gates before promoting any model output.

## Authority
- Research and design: [SEM_Historical_Crash_Research_v1](https://docs.google.com/spreadsheets/d/1ocdo4Y036ZB93egyY96INfuRcJkw0uHAO5BK416bVnE/edit)
- Implementation and reproducible QA: this repository.
- No invented probabilities, predictive claims or human approvals. A green CI run is not a validated forecasting model.

## Operating rule
When the user says **Continue**, perform the next substantial authorized implementation chunk in PROJECT_STATUS.md. Avoid repeat research and unnecessary approval interruptions. At each completed chunk, update PROJECT_STATUS.md and verify workflow results. Update the roadmap only when phase status or dependencies change. Write a new dated handoff at chat closeout.

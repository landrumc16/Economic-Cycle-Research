# Third-party AI skill and MCP security gate

Before installing or upgrading an external AI-agent skill or MCP integration:
1. Record source repository, pinned version/commit, requested permissions, and maintainer.
2. Scan the downloaded skill with a reputable static scanner (NVIDIA SkillSpector is one candidate). Review findings, not merely the scanner exit code.
3. Reject unresolved prompt injection, exfiltration, secret-access, or unexpected execution capabilities.
4. Obtain explicit human approval before enabling the integration. Do not put secrets in skill configuration or logs.
5. Keep scanner outputs and decision notes with the change.

This rule is **event-triggered**: there is no third-party AI skill in the current economic-data pipeline. Do not install a scanner merely to satisfy this checklist or delay Milestone 1. Code and dependency security require separate review.

Milestone 1 economic data promotion remains independently fail-closed.

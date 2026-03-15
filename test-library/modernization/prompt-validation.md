Compare two outputs (old vs new instruction runs) of the **modernization** flow. Score per validation gates. Emit pass/fail. Single responsibility.

The modernization flow is a multi-phase migration process: existing library analysis, old code analysis, optional test coverage, class group analysis, cross-project analysis, implementation mapping, and final review. Expected artifacts:
- `docs/modernization-analysis.md` — Analysis of current code with migration requirements
- `agents/modernization-state.md` — Phase completion state tracking

**Input:**
- **Context:** Prompt request (goals to evaluate coverage against), root paths (root_old, root_new), files to check in root_old (separate list), files to check in root_new (separate list).
- **Instruction diff:** Shows what changed in the instruction file(s) between old and new versions. Use to identify removed/added phases or rules.
- **Old output:** Content from root_old for each file in its list.
- **New output:** Content from root_new for each file in its list.
- If no files changed, Old/New output indicate no files changed.

**Evaluation focus for modernization:**
- Does the analysis identify actual Java/Spring Boot version dependencies from root_original?
- Are breaking changes between current and target versions documented?
- Is `agents/modernization-state.md` present with phase completion status?
- Are affected files, classes, and configurations identified from the actual codebase?
- Does the analysis separate what needs to change vs what can stay?
- Are decisions/recommendations deferred to later phases (not premature)?
- If the instruction diff removed phases or analysis steps, did the new output lose corresponding artifacts?

Use the prompt request AND the instruction diff to assess whether outputs properly cover the stated goals. If the old instruction required phases that produced useful artifacts and those are missing in the new output, that is a regression.

Compare the outputs below. Score each category 1–5 for both. Set result to "passed" or "failed". Emit raw JSON only.

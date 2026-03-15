Compare two outputs (old vs new instruction runs) of the **code-analysis** flow. Score per validation gates. Emit pass/fail. Single responsibility.

The code-analysis flow performs senior-level architectural analysis: reverse-engineering the codebase to understand structure, patterns, and engineering decisions. Expected artifacts:
- `analysis.md` — Consolidated analysis of REST API architecture and component interactions

**Input:**
- **Context:** Prompt request (goals to evaluate coverage against), root paths (root_old, root_new), files to check in root_old (separate list), files to check in root_new (separate list).
- **Instruction diff:** Shows what changed in the instruction file(s) between old and new versions. Use to identify removed/added structural requirements or analysis sections.
- **Old output:** Content from root_old for each file in its list.
- **New output:** Content from root_new for each file in its list.
- If no files changed, Old/New output indicate no files changed.

**Evaluation focus for code-analysis:**
- Does the analysis cover the REST API architecture (controllers, services, repositories)?
- Are components and subcomponents individually documented?
- Are design patterns identified with concrete implementation references?
- Is data architecture documented with exact contracts (fields, types, purpose)?
- Are integration patterns between components described?
- Does the analysis reference actual source code from root_original?
- Are quality observations and engineering insights present?
- If the instruction diff removed analysis sections or structural requirements, did the new output lose corresponding depth?

Use the prompt request AND the instruction diff to assess whether outputs properly cover the stated goals. If the old instruction required sections that produced useful analysis and those are missing in the new output, that is a regression.

Compare the outputs below. Score each category 1–5 for both. Set result to "passed" or "failed". Emit raw JSON only.

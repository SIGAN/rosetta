Compare two outputs (old vs new instruction runs) of the **testgen** flow. Score per validation gates. Emit pass/fail. Single responsibility.

The testgen flow generates test cases through sequential phases: data collection, gap analysis, requirements document, test scenario generation (TestRail-compatible), and optional export. Expected artifacts:
- `plans/TESTGEN-HEALTHCHECK-PLAN.md` — Test generation plan with requirements, gaps, and test scenarios

**Input:**
- **Context:** Prompt request (goals to evaluate coverage against), root paths (root_old, root_new), files to check in root_old (separate list), files to check in root_new (separate list).
- **Instruction diff:** Shows what changed in the instruction file(s) between old and new versions. Use to identify removed/added phases or generation rules.
- **Old output:** Content from root_old for each file in its list.
- **New output:** Content from root_new for each file in its list.
- If no files changed, Old/New output indicate no files changed.

**Evaluation focus for testgen:**
- Were requirements extracted from the project structure and README?
- Are gaps and contradictions in requirements identified?
- Is a requirements document generated from the analysis?
- Are test scenarios structured and TestRail-compatible?
- Do test cases reference actual code and endpoints from root_original?
- Are phases executed sequentially with state tracking?
- If the instruction diff removed generation phases or rules, did the new output lose corresponding artifacts?

Use the prompt request AND the instruction diff to assess whether outputs properly cover the stated goals. If the old instruction required phases that produced useful test artifacts and those are missing in the new output, that is a regression.

Compare the outputs below. Score each category 1–5 for both. Set result to "passed" or "failed". Emit raw JSON only.

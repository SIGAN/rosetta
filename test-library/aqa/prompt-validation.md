Compare two outputs (old vs new instruction runs) of the **AQA** flow. Score per validation gates. Emit pass/fail. Single responsibility.

The AQA flow is a multi-phase automated QA process: requirements discovery, test strategy, scenario design, test case specification, implementation, and execution. Expected artifacts:
- `plans/AQA-HEALTHCHECK-PLAN.md` — Test plan with requirements, strategy, and scenarios
- `agents/aqa-state.md` — Phase completion state tracking

**Input:**
- **Context:** Prompt request (goals to evaluate coverage against), root paths (root_old, root_new), files to check in root_old (separate list), files to check in root_new (separate list).
- **Instruction diff:** Shows what changed in the instruction file(s) between old and new versions. Use to identify removed/added structural requirements or phase changes.
- **Old output:** Content from root_old for each file in its list.
- **New output:** Content from root_new for each file in its list.
- If no files changed, Old/New output indicate no files changed.

**Evaluation focus for AQA:**
- Were testable requirements extracted from the codebase?
- Does the test strategy identify frameworks, priorities, and test data approach?
- Are test scenarios covering happy paths, edge cases, negative cases, and error handling?
- Is `agents/aqa-state.md` present with phase completion status?
- Does the plan reference actual code from root_original (controllers, endpoints, models)?
- If the instruction diff removed phases or steps, did the new output lose corresponding artifacts?

Use the prompt request AND the instruction diff to assess whether outputs properly cover the stated goals. If the old instruction required phases that produced useful artifacts and those are missing in the new output, that is a regression.

Compare the outputs below. Score each category 1–5 for both. Set result to "passed" or "failed". Emit raw JSON only.

Compare two outputs (old vs new instruction runs) of the **coding** flow. Score per validation gates. Emit pass/fail. Single responsibility.

The coding flow follows: discovery, tech specs, plan, user review, implementation. In this test, only discovery through planning is exercised. Expected artifacts:
- `plans/healthcheck/healthcheck-SPECS.md` — Tech specs with interfaces, API contracts, and implementation details
- `plans/healthcheck/healthcheck-PLAN.md` — Work breakdown structure with sequenced tasks

**Input:**
- **Context:** Prompt request (goals to evaluate coverage against), root paths (root_old, root_new), files to check in root_old (separate list), files to check in root_new (separate list).
- **Instruction diff:** Shows what changed in the instruction file(s) between old and new versions. Use to identify removed/added structural requirements.
- **Old output:** Content from root_old for each file in its list.
- **New output:** Content from root_new for each file in its list.
- If no files changed, Old/New output indicate no files changed.

**Evaluation focus for coding:**
- Did discovery reference actual code from root_original (existing controllers, models, config)?
- Are tech specs compact and targeted at senior engineers (interfaces, signatures, contracts)?
- Does the plan follow WBS structure with prerequisites and consequences?
- Are guardrails referenced (scope management, risk mitigation)?
- Do specs and plan complement each other without duplication?
- If the instruction diff removed coding flow steps or principles, did the new output lose corresponding quality?

Use the prompt request AND the instruction diff to assess whether outputs properly cover the stated goals. If the old instruction required steps that produced useful artifacts and those are missing in the new output, that is a regression.

Compare the outputs below. Score each category 1–5 for both. Set result to "passed" or "failed". Emit raw JSON only.

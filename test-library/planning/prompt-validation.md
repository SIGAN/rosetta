Compare two outputs (old vs new instruction runs) of the **planning** flow. Score per validation gates. Emit pass/fail. Single responsibility.

The planning flow uses 6-D methodology to create a work breakdown structure: discovery, deconstruct, define, design, develop plan, and deliver. Expected artifacts:
- `plans/healthcheck/healthcheck-PLAN.md` — WBS with sequenced tasks, prerequisites, consequences, and functional requirements

**Input:**
- **Context:** Prompt request (goals to evaluate coverage against), root paths (root_old, root_new), files to check in root_old (separate list), files to check in root_new (separate list).
- **Instruction diff:** Shows what changed in the instruction file(s) between old and new versions. Use to identify removed/added planning rules or methodology steps.
- **Old output:** Content from root_old for each file in its list.
- **New output:** Content from root_new for each file in its list.
- If no files changed, Old/New output indicate no files changed.

**Evaluation focus for planning:**
- Does the plan follow WBS structure with sequenced tasks?
- Are prerequisites and consequences documented for each task?
- Are EARS functional requirements present?
- Does discovery reference actual code from root_original (existing endpoints, config, structure)?
- Is the plan compact but complete (appropriate length for task complexity)?
- Are Poka-Yoke concepts integrated (error prevention, safety checks)?
- If the instruction diff removed planning flow steps or 6-D methodology, did the new output lose corresponding structure?

Use the prompt request AND the instruction diff to assess whether outputs properly cover the stated goals. If the old instruction required steps that produced useful plan artifacts and those are missing in the new output, that is a regression.

Compare the outputs below. Score each category 1–5 for both. Set result to "passed" or "failed". Emit raw JSON only.

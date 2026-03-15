Compare two outputs (old vs new instruction runs) of the **help** flow. Score per validation gates. Emit pass/fail. Single responsibility.

The help flow introspects available instruction prompts, checks repository state, and guides the user on available AI capabilities. Expected artifacts:
- `docs/help-guide.md` — Help guide describing available flows, current state, and next actions

**Input:**
- **Context:** Prompt request (goals to evaluate coverage against), root paths (root_old, root_new), files to check in root_old (separate list), files to check in root_new (separate list).
- **Instruction diff:** Shows what changed in the instruction file(s) between old and new versions. Use to identify removed/added help content.
- **Old output:** Content from root_old for each file in its list.
- **New output:** Content from root_new for each file in its list.
- If no files changed, Old/New output indicate no files changed.

**Evaluation focus for help:**
- Does the guide describe available flows by introspecting actual instruction files?
- Is the current repository state checked and reflected (what's initialized, what's missing)?
- Are next actions suggested based on the actual project state?
- Is the output at a "101 level" for developers (accessible, not overly technical)?
- Does it cover what users should expect from each flow?
- If the instruction diff removed help flow steps, did the new output lose corresponding guidance?

Use the prompt request AND the instruction diff to assess whether outputs properly cover the stated goals. If the old instruction required steps that produced useful guidance and those are missing in the new output, that is a regression.

Compare the outputs below. Score each category 1–5 for both. Set result to "passed" or "failed". Emit raw JSON only.

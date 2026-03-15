Compare two outputs (old vs new instruction runs) of the **prompting** flow. Score per validation gates. Emit pass/fail. Single responsibility.

The prompting flow creates optimized prompts using prompt engineering principles (SRP, DRY, KISS, MECE, Poka-Yoke). It may use subagent roles (architect, engineer, reviewer) or skills-based approach. Expected artifacts:
- `docs/prompts/code-review-prompt.md` — Optimized code review prompt for REST API endpoints

**Input:**
- **Context:** Prompt request (goals to evaluate coverage against), root paths (root_old, root_new), files to check in root_old (separate list), files to check in root_new (separate list).
- **Instruction diff:** Shows what changed in the instruction file(s) between old and new versions. Use to identify removed/added prompting rules or approaches.
- **Old output:** Content from root_old for each file in its list.
- **New output:** Content from root_new for each file in its list.
- If no files changed, Old/New output indicate no files changed.

**Evaluation focus for prompting:**
- Does the generated prompt follow LLM-specific best practices (clear context, constraints, output format)?
- Is the prompt tailored to the actual project's REST API endpoints from root_original?
- Are prompt engineering principles applied (SRP, MECE, Poka-Yoke)?
- Is the prompt structured for reliable, repeatable results?
- Does the prompt include validation or self-checking mechanisms?
- If the instruction diff removed prompting approaches or principles, did the new output lose corresponding quality?

Use the prompt request AND the instruction diff to assess whether outputs properly cover the stated goals. If the old instruction required principles that produced useful prompt artifacts and those are missing in the new output, that is a regression.

Compare the outputs below. Score each category 1–5 for both. Set result to "passed" or "failed". Emit raw JSON only.

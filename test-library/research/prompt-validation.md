Compare two outputs (old vs new instruction runs) of the **research** flow. Score per validation gates. Emit pass/fail. Single responsibility.

The research flow uses meta-prompting: it prepares an optimized research prompt, then executes it. It follows a tree-of-thoughts pattern analyzing multiple options. Expected artifacts:
- `plans/healthcheck/research-prompt.md` — Optimized research prompt with enforcement rules
- `docs/research/healthcheck.md` — Research findings with summary/TLDR
- `plans/healthcheck/research-state.md` — Research state tracking

**Input:**
- **Context:** Prompt request (goals to evaluate coverage against), root paths (root_old, root_new), files to check in root_old (separate list), files to check in root_new (separate list).
- **Instruction diff:** Shows what changed in the instruction file(s) between old and new versions. Use to identify removed/added research rules or flow steps.
- **Old output:** Content from root_old for each file in its list.
- **New output:** Content from root_new for each file in its list.
- If no files changed, Old/New output indicate no files changed.

**Evaluation focus for research:**
- Was a research prompt generated (meta-prompting approach, not direct research)?
- Does the research prompt include enforcement rules from the instruction?
- Are findings documented with at least 3 options analyzed (tree-of-thoughts)?
- Is a summary/TLDR section present?
- Does `plans/healthcheck/research-state.md` track progress?
- Are assumptions and unknowns handled explicitly?
- Does the research prioritize accuracy over speed?
- If the instruction diff removed research rules or flow steps, did the new output lose corresponding rigor?

Use the prompt request AND the instruction diff to assess whether outputs properly cover the stated goals. If the old instruction required rules that produced useful research artifacts and those are missing in the new output, that is a regression.

Compare the outputs below. Score each category 1–5 for both. Set result to "passed" or "failed". Emit raw JSON only.

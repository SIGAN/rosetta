Compare two outputs (old vs new instruction runs) of the **questions** flow. Score per validation gates. Emit pass/fail. Single responsibility.

The questions flow drives the user to share missing information by asking targeted, prioritized questions. It resolves assumptions, unknowns, and gaps. Expected artifacts:
- `docs/questions-healthcheck.md` — Structured questions with analysis of what's known vs unknown

**Input:**
- **Context:** Prompt request (goals to evaluate coverage against), root paths (root_old, root_new), files to check in root_old (separate list), files to check in root_new (separate list).
- **Instruction diff:** Shows what changed in the instruction file(s) between old and new versions. Use to identify removed/added questioning rules.
- **Old output:** Content from root_old for each file in its list.
- **New output:** Content from root_new for each file in its list.
- If no files changed, Old/New output indicate no files changed.

**Evaluation focus for questions:**
- Are questions specific and relevant to the health-check API feature?
- Are questions prioritized (CRITICAL/HIGH only, no medium/low/nitpicking)?
- Do questions reference actual code from root_original to identify gaps?
- Are assumptions clearly marked when answers are unknown?
- Is the questioning systematic and methodological (not random)?
- Are questions grouped logically (related work in single groups)?
- If the instruction diff removed questioning rules or priorities, did the new output lose corresponding quality?

Use the prompt request AND the instruction diff to assess whether outputs properly cover the stated goals. If the old instruction required rules that produced useful questioning artifacts and those are missing in the new output, that is a regression.

Compare the outputs below. Score each category 1–5 for both. Set result to "passed" or "failed". Emit raw JSON only.

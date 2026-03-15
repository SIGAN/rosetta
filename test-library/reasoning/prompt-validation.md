Compare two outputs (old vs new instruction runs) of the **reasoning** flow. Score per validation gates. Emit pass/fail. Single responsibility.

The reasoning flow uses meta-cognitive reasoning: discover, decompose, solve with confidence scoring, verify, synthesize, and reflect. Expected artifacts:
- `docs/reasoning-healthcheck.md` — Recommendation with confidence level, key caveats, and structured reasoning

**Input:**
- **Context:** Prompt request (goals to evaluate coverage against), root paths (root_old, root_new), files to check in root_old (separate list), files to check in root_new (separate list).
- **Instruction diff:** Shows what changed in the instruction file(s) between old and new versions. Use to identify removed/added reasoning steps.
- **Old output:** Content from root_old for each file in its list.
- **New output:** Content from root_new for each file in its list.
- If no files changed, Old/New output indicate no files changed.

**Evaluation focus for reasoning:**
- Does the output include explicit confidence level (0.0–1.0)?
- Are key caveats identified and documented?
- Is the reasoning structured (decomposed into sub-problems)?
- Are facts verified against the actual codebase in root_original?
- Is the synthesis weighted by confidence of sub-conclusions?
- Does reflection identify weaknesses and retry if confidence < 0.8?
- If the instruction diff removed reasoning steps or confidence requirements, did the new output lose corresponding rigor?

Use the prompt request AND the instruction diff to assess whether outputs properly cover the stated goals. If the old instruction required steps that produced useful reasoning artifacts and those are missing in the new output, that is a regression.

Compare the outputs below. Score each category 1–5 for both. Set result to "passed" or "failed". Emit raw JSON only.

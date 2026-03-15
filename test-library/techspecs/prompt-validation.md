Compare two outputs (old vs new instruction runs) of the **techspecs** flow. Score per validation gates. Emit pass/fail. Single responsibility.

The techspecs flow transforms a user request into clear, testable technical specifications with interfaces, API contracts, and implementation details. Expected artifacts:
- `plans/healthcheck/healthcheck-SPECS.md` — Tech specs with TLDR, interfaces, signatures, contracts, and security considerations

**Input:**
- **Context:** Prompt request (goals to evaluate coverage against), root paths (root_old, root_new), files to check in root_old (separate list), files to check in root_new (separate list).
- **Instruction diff:** Shows what changed in the instruction file(s) between old and new versions. Use to identify removed/added techspec rules or sections.
- **Old output:** Content from root_old for each file in its list.
- **New output:** Content from root_new for each file in its list.
- If no files changed, Old/New output indicate no files changed.

**Evaluation focus for techspecs:**
- Are specs written as TOC-first, then section-by-section (not monolithic)?
- Is a TLDR section present (up to 10 lines)?
- Are specs compact and targeted at senior engineers (terms, abbreviations, interfaces, signatures)?
- Do specs reference actual code from root_original (existing controllers, models, config)?
- Are API contracts defined (endpoints, request/response formats)?
- Do specs detail down to interfaces/classes/methods level (signatures, not implementations)?
- Is integrity verified (no gaps, no contradictions)?
- If the instruction diff removed techspec rules or sections, did the new output lose corresponding detail?

Use the prompt request AND the instruction diff to assess whether outputs properly cover the stated goals. If the old instruction required rules that produced useful spec artifacts and those are missing in the new output, that is a regression.

Compare the outputs below. Score each category 1–5 for both. Set result to "passed" or "failed". Emit raw JSON only.

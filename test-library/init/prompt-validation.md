Compare two outputs (old vs new instruction runs) of the **init** flow. Score per validation gates. Emit pass/fail. Single responsibility.

The init flow creates documentation and agent configuration for a workspace. Expected artifacts:
- `docs/TECHSTACK.md` — Tech stack analysis
- `docs/CODEMAP.md` — Code map / file structure
- `docs/DEPENDENCIES.md` — Dependencies analysis
- `docs/CONTEXT.md` — Integrated project context
- `docs/ARCHITECTURE.md` — Architecture documentation
- `docs/ASSUMPTIONS.md` — Tracked unknowns
- `agents/IMPLEMENTATION.md` — Implementation guidelines
- `agents/init-state.md` — Phase completion state tracking
- Root agent file (bootstrap)
- Tech-specific agent files (if applicable)

**Input:**
- **Context:** Prompt request (goals to evaluate coverage against), root paths (root_old, root_new), files to check in root_old (separate list), files to check in root_new (separate list).
- **Instruction diff:** Shows what changed in the instruction file(s) between old and new versions. Use to identify removed/added structural requirements or phase changes.
- **Old output:** Content from root_old for each file in its list (sections `### <path>`).
- **New output:** Content from root_new for each file in its list (sections `### <path>`).
- If no files changed, Old/New output indicate no files changed.

**Evaluation focus for init:**
- Were all expected documentation files created?
- Is `agents/init-state.md` present with phase completion status?
- Does TECHSTACK.md accurately reflect the actual tech stack in root_original?
- Does CODEMAP.md reflect the actual file structure in root_original?
- Does ARCHITECTURE.md describe the actual architecture found in root_original?
- Are CONTEXT.md and IMPLEMENTATION.md substantive (not empty stubs)?
- If the instruction diff removed init phases or steps, did the new output lose corresponding artifacts?

Use the prompt request AND the instruction diff to assess whether outputs properly cover the stated goals. If the old instruction required phases/steps that produced useful artifacts and those are missing in the new output, that is a regression.

Compare the outputs below. Score each category 1–5 for both. Set result to "passed" or "failed". Emit raw JSON only.

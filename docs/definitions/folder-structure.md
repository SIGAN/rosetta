# Terminology

- Prompts = `skills`, `agents`, `workflows`, `rules`, `templates`, `commands`
- Agents = agents or subagents

# New Folder Structure

- **Base structure:** `/instructions/r2/core/<type>/<name>/[files]`
  - Types: `skills`, `agents`, `workflows`, `rules`, `commands`
  - Base = Open-source foundation (OSS core, everyone gets this)
  - Grid = Grid Dynamics improved prompts
- **Organization-specific customizations:** `/instructions/r2/<org>/<type>/<name>/[files]`
  - Organizations: `grid` (Grid Dynamics), `acme` (ACME Corp), etc.
  - Organization files extend or override core implementations (layered customization, not multi-tenancy)
- **Resulting ResourcePath:** Strip `/instructions/r2/core/` OR `/instructions/r2/<org>/` prefix
  - Example: `/instructions/r2/core/skills/my-skill/SKILL.md` → `skills/my-skill/SKILL.md`
  - Example: `/instructions/r2/grid/skills/my-skill/SKILL.md` → `skills/my-skill/SKILL.md`
- **Bundling behavior:** Core + Organization files with same ResourcePath get bundled together
  - Optional filtering: INSTRUCTION_ROOT_FILTER env var controls which organizations to include (e.g., `CORE,GRID` includes only base + Grid Dynamics)
  - Default file sort_order: 1000000 always
  - If there are MORE than 5 files matching, bundler outputs just XML list and instruction to load required files one-by-one
- **Relationships:**
  - Workflows invoke subagents
  - Subagents use skills
  - Workflows, subagents, skills reference rules
  - Templates are part of skills
  - Guardrails are rules
  - All file names are unique, including inside of skills sub-folders (use abbreviation prefix)
  - All file names are lower case, split words with dashes
- **Examples:**
  - `core/skills/<name>/SKILL.md` - Skill definition (OSS)
  - `core/agents/<name>.md` - Subagent definition (OSS)
  - `core/workflows/<name>.md` - Workflow template (OSS)
  - `core/workflows/<name>-<phase>.md` - Workflow phase template (OSS)
  - `core/rules/<name>.md` - Rules and guardrails (OSS)
  - `grid/skills/<name>/SKILL.md` - Grid Dynamics-specific skill customization (GRID, Enterprise)
  - `grid/skills/<name>/scripts/<file>` - Executable code that agents can run (GRID, Enterprise)
  - `grid/skills/<name>/references/<file>` - Additional documentation loaded on demand (GRID, Enterprise)
  - `grid/skills/<name>/assets/<file>` - Static resources like templates, images, or data files (GRID, Enterprise)
- Automatic path-based tags (all lower case):
  - All parent folder names
  - File name with extension
  - Release (folder name "r0.0", "r1", "r2.1", "r13")
  - Domain (folder under the release folder: "core", "grid")
  - Two-level (immediate parent folder and file name: "my-skill/SKILL.md")
  - Three-level (immediate parent folder and file name: "skills/my-skill/SKILL.md", "my-skill/references/my-skill-best-practices.md")

# Core vs Grid

Core:
- init.md (onboarding initialization of the repository)
- coding.md (implementation flow)
- adhoc.md (adhoc requests, minor changes)
- help.md (built-in help system => convert to self-help.md)
- all common (guardrails.md, planning.md, questions.md, reasoning.md, techspecs.md)
- agents.md (converted from request classification to execution planning based on recombined matching flow templates)

Grid:
- All the rest

# How Rosetta MCP uses New Folder Structure

AI agents use Rosetta MCP as a consultant.

Example setup:

```
/CORE      -- THIS IS OSS
   /SKILLS
       /PLANNING
          PROMPT
          TEMPLATE

/GRID      -- GRID DYNAMICS KNOW-HOW
   /SKILLS
       /PLANNING
          PROMPT
          TEMPLATE-OVERRIDE

/ACME  -- CLIENTS GLOBAL CUSTOMIZATIONS
   /SKILLS
       /PLANNING
          PROMPT
```

MCP was requested to provide PLANNING skill.
MCP provides the following logical output:
PROMPT: BUNDLING(/CORE/SKILLS/PLANNING/PROMPT CONCAT /GRID/SKILLS/PLANNING/PROMPT CONCAT /ACME/SKILLS/PLANNING/PROMPT)
TEMPLATE: BUNDLING(/GRID/SKILLS/PLANNING/TEMPLATE-OVERRIDE)

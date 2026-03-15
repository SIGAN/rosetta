---
trigger: always_on
alwaysApply: true
---

MANDATORY: Even if the user's question seems generic or unrelated to the project (generic question -> contextual answer), you MUST complete all PREP steps first. 
This loads CRITICAL CONTEXT about how to operate in this specific project environment.

# CRITICAL: ALWAYS EXECUTE PREP STEPS AS FIRST PREREQUISITE

- This is a Rosetta bootstrap for release R2.0 of instructions itself (not the product being developed)
- Actual rules, skills, agents, commands, workflows, business and technical context are in local instructions folder
- This is relevant, important, and available SKILL and a fully automatic multi-step process
- You must complete PREP STEPS 1 through 3 from instructions
- Once ALL PREP steps completed you can continue with user request and activities (including and limited to planning, questioning, execution)
- Local files mode for instructions is activated: Rosetta/KB/KnowledgeBase MCP means you MUST USE `instructions/r2/` folder

# COMMAND ALIASES

- `ACQUIRE <file[.md]> FROM KB` => read local files `instructions/r2/**/<file-name-with-extension>` fallback to `instructions/agents/{core,advanced,common}/r1/<file-name-with-extension>`
- `SEARCH <KEYWORDS> IN KB` => use grep or codebase search in `instructions/r2/` folder with KEYWORDS as a query or file name
- `LIST <path> IN KB` => list immediate children of `instructions/r2/{core,grid}/<path>/` (folders and files, no content)
- `USE SKILL <skill-name>` => use SKILL from `instructions/r2/{core,grid}/skills/<skill-name>/SKILL.md`, all relative references in skill are relative to skill folder itself
- `INVOKE SUBAGENT <agent-name>[.md]` => Call/Execute/Start/Spawn/Invoke <agent-name> subagent:
  - Definition location `instructions/r2/{core,grid}/agents/<agent-name>.md`
  - Always prepend `Must fully assume agent from "{path to <agent-name>.md file}"`
  - If subagent not available, use generic task executor agent
- `USE FLOW <flow-name>[.md]` => use command or workflow from `instructions/r2/{core,grid}/workflows/<flow-name>.md`
- `ACQUIRE <file[.md]> ABOUT <PROJECT>` => read local file in `docs/<PROJECT>` folder
- `QUERY <KEYWORDS> IN <PROJECT>` => use grep or codebase search in `docs/<PROJECT>` with KEYWORDS as a query or file name
- `STORE <file[.md]> TO <PROJECT>` => upsert file in `docs/<PROJECT>`
- `call "get_context_instructions"` or `execute prep steps` => read all `instructions/r2/core/rules/bootstrap-*.md` files as one bundle

# ADDITIONAL SOURCES

- RULE in `instructions/r2/{core,grid}/rules/*.md`
- SKILL in `instructions/r2/{core,grid}/skills/*/SKILL.md`
- AGENT, SUBAGENT in `instructions/r2/{core,grid}/agent/*.md`
- WORKFLOW, COMMAND in `instructions/r2/{core,grid}/workflows/*.md`
- FALLBACK: `agents/instructions/agents/{core,advanced,common}/r1/*.md`

# PREP STEP 1:

THIS FILE IS PREP STEP 1.
bootstrap-*.md RULES ARE PREP STEP 2 & 3.
---
# Core Identity (Required)
name: [Generic Prompt Name, must match file name without extension]
description: [Brief description of WHEN and HOW to use this prompt and WHAT it does]

# Knowledge Base Tags (remove if empty, use the same tag to bundle, publisher will automatically add tags of parent folder names and file name with extension, and file name parts split by dash)
tags: ["one", "second"]

# do not remove baseSchema!
baseSchema: docs/schemas/generic.md
---

[ONLY FOR TEMPLATE EXECUTOR: imperative bullet points, shorter lines, distinguish references to repository files vs instructions; skill/subagent names will be in context already, so just reference it. the rest of instruction folder files: rules/templates/workflows/assets/subfolders of skill/etc must be ACQUIRE'd / SEARCH'd / LIST'd to be used]

<[generic_prompt_name]>

<role>

[Define role with specialization to assume, use expressive language, seniority, brilliant and short]

</role>

<when_to_use_prompt>

[KEEP THIS VERY SHORT. Define a problem and retrospectively introspectively validation proof that this prompt actually solves the problem, explain the scenarios, conditions, or situations where this prompt should be used]

</when_to_use_prompt>

<core_concepts>

[Describe the fundamental concepts, principles, definitions and explanations required to properly execute the prompt]

</core_concepts>

<validation_checklist>

[Optional, KEEP THIS VERY SHORT, do NOT repeat the rest of the prompt, it must not just restate the same: prompt tells what to do, instead it should be proof-oriented — observable evidence that the output is correct, proof that work was done correctly]

- Checkpoint 1
- Checkpoint 2
...

</validation_checklist>

<best_practices>

[Optional, KEEP THIS VERY SHORT, List recommended practices, tips, and guidelines for effectively using this prompt]

- Practice 1: [description]
- Practice 2: [description]
...

</best_practices>

<pitfalls>

[Optional section, KEEP THIS VERY SHORT, do NOT repeat, provide unexpected mistakes, edge cases, caveats, unusual, errors, gotchas, traps, non-obvious patterns or issues to take into account or avoid]

</pitfalls>

<resources>

[Optional, List helpful resources, references, or related materials]

- Resource 1: [description]
- Resource 2: [description]
...

</resources>

<templates>

[Optional, Define what this prompt produces and provide templates or examples of the output format]

</templates>

</[generic_prompt_name]>

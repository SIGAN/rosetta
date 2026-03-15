---
# Core Identity (Required)
name: [Rules Name, must match file name without extension] [obligatory]
description: ["Rosetta" + Brief description of WHEN and HOW to use this rules list] [obligatory]

# Optional
globs: [File patterns (glob syntax) where the rule applies (comma-separated)] [string] [Cursor, Antigravity] [ex: '**/*.js, **/*.ts']
paths: [File patterns (glob syntax) where the rule applies (comma-separated)] [string] [Claude Code, Windsurf] [ex: **/*.js, **/*.ts]
alwaysApply: [When true, the rule is always active; if false, it's context-dependent] [boolean] [Cursor]
trigger: [Controls when the rules are activated] [string] [Antigravity] [ex: glob]

# Knowledge Base Tags (remove if empty, use the same tag to bundle, publisher will automatically add tags of parent folder names and file name with extension, and file name parts split by dash)
tags: ["one", "second"]

# do not remove baseSchema!
baseSchema: docs/schemas/rule.md
---

[ONLY FOR TEMPLATE EXECUTOR: imperative bullet points, shorter lines, distinguish references to repository files vs instructions; skill/subagent names will be in context already, so just reference it. the rest of instruction folder files: rules/templates/workflows/assets/subfolders of skill/etc must be ACQUIRE'd / SEARCH'd / LIST'd to be used]

<[the_rule_name]>

[The rules should be divided into following categories depending on their importance. Remember that the category impacts the probability that the rule will affect the result. Any of the categories can be left empty. Define a problem and retrospectively introspectively validation proof that this prompt actually solves the problem. Reference entire sections in must/should/could if present.]

<must>

[required]

1.
2.
...

</must>

<should>

[optional]

1. 
2.
...

</should>

<could>

[optional, likely is not even needed]

1.
2.
...

</could>

<core_concepts>

[Optional section, KEEP THIS VERY SHORT, describes the fundamental concepts, principles, definitions and explanations required for the rule]

</core_concepts>

<[additional_section]>

[Optional additional section]

</[additional_section]>

<best_practices>

[Optional section, list recommended practices, tips, and guidelines for effectively using this rule]

</best_practices>

<pitfalls>

[Optional section, KEEP THIS VERY SHORT, do NOT repeat, provide unexpected mistakes, edge cases, caveats, unusual behavior, errors, gotchas, traps, non-obvious patterns or issues to take into account or avoid]

</pitfalls>

<notes>

[Optional section, any additional information that needs to be added.]

</notes>

</[the_rule_name]>

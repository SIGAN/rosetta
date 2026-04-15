---
name: li-readme-section
description: README documentation for LSP support feature
tags: ["lsp-install", "documentation"]
---

## LSP Support (Optional)

Rosetta can install Language Server Protocol (LSP) servers to provide AI coding agents with enhanced code intelligence.

### What LSP Provides

- Real-time type information
- Go-to-definition and find-all-references
- Error diagnostics before compilation
- Code refactoring support

Without LSP, AI agents treat source files as plain text. With LSP, agents have IDE-grade understanding of your code.

### Enabling LSP Installation

LSP installation is **opt-in only**. During workspace initialization, you'll be prompted:

```
Install LSP servers for [TypeScript, Python]? This improves AI code quality. (recommended) [y/N]
```

**Manual invocation:** Use `/lsp-install` command anytime to install LSP servers.

### Supported Languages

| Language | LSP Server | Prerequisites |
|----------|-----------|---------------|
| TypeScript/JavaScript | typescript-language-server | Node.js, npm |
| Python | python-lsp-server (pylsp) | Python 3.9+ |
| Go | gopls | Go |
| Rust | rust-analyzer | rustup |
| Java | Eclipse JDT LS | Java 21+ |
| C# | OmniSharp | .NET 6.0+ or Mono |
| Kotlin | kotlin-language-server | Java 17+ |

### Troubleshooting

**LSP not working after installation**
- Ensure the LSP binary is in your PATH
- Restart your IDE/editor
- Run the verification command for your language

**Missing prerequisites**
- The skill will report missing prerequisites before attempting installation
- Install the required runtime (Node.js, Python, Go, etc.) and retry

**Installation failed**
- Check network connectivity
- Verify write permissions to installation directories
- Try manual installation using the commands in the installation reference

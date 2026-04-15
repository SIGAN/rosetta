---
name: li-detection-map
description: Language detection patterns to LSP server mapping
tags: ["lsp-install", "detection-map", "reference"]
---

# LSP Detection Map

## Detection Files to Language

| Detection Indicator | Language |
|---------------------|----------|
| `package.json`, `tsconfig.json`, `*.ts`, `*.tsx` | TypeScript/JavaScript |
| `*.js`, `*.jsx`, `*.mjs`, `*.cjs` | TypeScript/JavaScript |
| `pyproject.toml`, `requirements.txt`, `setup.py`, `Pipfile`, `*.py` | Python |
| `go.mod`, `go.sum`, `*.go` | Go |
| `Cargo.toml`, `Cargo.lock`, `*.rs` | Rust |
| `*.csproj`, `*.sln`, `*.cs` | C# |
| `pom.xml`, `build.gradle`, `*.java` | Java |
| `build.gradle.kts`, `*.kt`, `*.kts` | Kotlin |

## Language to LSP Server

| Language | LSP Server | Package/Binary |
|----------|-----------|----------------|
| TypeScript/JavaScript | typescript-language-server | npm: typescript-language-server, typescript |
| Python | python-lsp-server (pylsp) | pip: python-lsp-server[all] |
| Go | gopls | go install: golang.org/x/tools/gopls@latest |
| Rust | rust-analyzer | rustup component: rust-analyzer |
| C# | OmniSharp | GitHub release binary |
| Java | Eclipse JDT LS (jdtls) | Eclipse milestone download |
| Kotlin | kotlin-language-server | Homebrew: JetBrains/utils/kotlin-lsp |

## Prerequisites

| Language | Required | Check Command |
|----------|----------|---------------|
| TypeScript/JavaScript | Node.js, npm | `npm --version` |
| Python | Python 3.9+ | `python3 --version` |
| Go | Go | `go version` |
| Rust | rustup | `rustup --version` |
| C# | .NET 6.0+ or Mono 6.4.0+ | `dotnet --version` or `mono --version` |
| Java | Java 21+ | `java -version` (check ≥21) |
| Kotlin | Java 17+ | `java -version` (check ≥17) |

## Verification Commands

| LSP Server | Verification Command |
|------------|---------------------|
| typescript-language-server | `typescript-language-server --version` |
| pylsp | `pylsp --help` (exit 0) |
| gopls | `gopls version` |
| rust-analyzer | `rust-analyzer --version` |
| OmniSharp | `OmniSharp --version` |
| jdtls | N/A (verify by file existence) |
| kotlin-language-server | N/A (verify by file existence) |

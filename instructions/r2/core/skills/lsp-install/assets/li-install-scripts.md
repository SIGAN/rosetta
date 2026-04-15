---
name: li-install-scripts
description: Idempotent LSP server installation commands per language
tags: ["lsp-install", "installation-scripts", "reference"]
---

# LSP Installation Scripts

All scripts are idempotent — safe to run multiple times.

## TypeScript/JavaScript

### Prerequisites Check
```bash
if ! command -v npm &> /dev/null; then
    echo "ERROR: npm is required. Install Node.js first."
    exit 1
fi
```

### Installation
```bash
npm install -g typescript-language-server typescript
```

### Verification
```bash
typescript-language-server --version
```

---

## Python

### Prerequisites Check
```bash
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required."
    exit 1
fi
PYTHON_VERSION=$(python3 -c 'import sys; print(sys.version_info[:2])')
# Check version >= 3.9
```

### Installation
```bash
pip install "python-lsp-server[all]"
```

### Verification
```bash
pylsp --help && echo "pylsp installed successfully"
```

---

## Go

### Prerequisites Check
```bash
if ! command -v go &> /dev/null; then
    echo "ERROR: Go is required."
    exit 1
fi
```

### Installation
```bash
go install golang.org/x/tools/gopls@latest
```

### Verification
```bash
gopls version
```

---

## Rust

### Prerequisites Check
```bash
if ! command -v rustup &> /dev/null; then
    echo "ERROR: rustup is required. Install via https://rustup.rs"
    exit 1
fi
```

### Installation
```bash
rustup component add rust-analyzer
```

### Verification
```bash
rust-analyzer --version
```

---

## Java (Eclipse JDT LS)

### Prerequisites Check
```bash
JAVA_VERSION=$(java -version 2>&1 | head -1 | awk -F '"' '{print $2}' | cut -d'.' -f1)
if [ "$JAVA_VERSION" -lt 21 ]; then
    echo "ERROR: Java 21+ required. Current: $JAVA_VERSION"
    exit 1
fi
```

### Installation
```bash
# Create installation directory
mkdir -p ~/.local/share/jdtls

# Download latest milestone (check for latest version)
JDTLS_VERSION="1.40.0"
curl -L -o /tmp/jdtls.tar.gz \
  "https://download.eclipse.org/jdtls/milestones/${JDTLS_VERSION}/jdt-language-server-${JDTLS_VERSION}.tar.gz"

# Extract
tar -xzf /tmp/jdtls.tar.gz -C ~/.local/share/jdtls
rm /tmp/jdtls.tar.gz
```

### Verification
```bash
ls ~/.local/share/jdtls/plugins/org.eclipse.equinox.launcher_*.jar
```

---

## C# (OmniSharp)

### Prerequisites Check (macOS/Linux)
```bash
if ! command -v dotnet &> /dev/null; then
    if ! command -v mono &> /dev/null; then
        echo "ERROR: .NET SDK or Mono required"
        exit 1
    fi
fi
```

### Installation
```bash
# Detect platform
PLATFORM=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then ARCH="x64"; fi
if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then ARCH="arm64"; fi

# Download latest release
mkdir -p ~/.local/share/omnisharp
curl -L -o /tmp/omnisharp.tar.gz \
  "https://github.com/OmniSharp/omnisharp-roslyn/releases/latest/download/omnisharp-${PLATFORM}-${ARCH}-net6.0.tar.gz"

# Extract
tar -xzf /tmp/omnisharp.tar.gz -C ~/.local/share/omnisharp
rm /tmp/omnisharp.tar.gz
```

### Verification
```bash
~/.local/share/omnisharp/OmniSharp --version
```

---

## Kotlin

### Prerequisites Check
```bash
JAVA_VERSION=$(java -version 2>&1 | head -1 | awk -F '"' '{print $2}' | cut -d'.' -f1)
if [ "$JAVA_VERSION" -lt 17 ]; then
    echo "ERROR: Java 17+ required for Kotlin LSP. Current: $JAVA_VERSION"
    exit 1
fi
```

### Installation (macOS)
```bash
brew tap JetBrains/utils
brew install kotlin-lsp
```

### Installation (Linux/Manual)
```bash
# Download from GitHub releases
mkdir -p ~/.local/share/kotlin-lsp
curl -L -o /tmp/kotlin-lsp.zip \
  "https://github.com/Kotlin/kotlin-lsp/releases/latest/download/server.zip"
unzip /tmp/kotlin-lsp.zip -d ~/.local/share/kotlin-lsp
rm /tmp/kotlin-lsp.zip
```

### Verification
```bash
ls ~/.local/share/kotlin-lsp/bin/kotlin-language-server || which kotlin-language-server
```

---

## Opt-In Configuration

### Interactive Prompt (Default)
During init-workspace-flow, user is prompted:
```
Install LSP servers for [TypeScript, Python]? This improves AI code quality. (recommended) [y/N]
```

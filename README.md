# 🧠 Socratic Debug (`socratic`)

> **Stop copying stack traces. Start mastering your bugs.**  
> An autonomous pedagogical debugger and mentor powered by LangGraph, PyQt6, and LangSmith.

[![CI](https://github.com/mohamedelawakey/socratic/actions/workflows/ci.yml/badge.svg)](https://github.com/mohamedelawakey/socratic/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/socratic-debug.svg?color=blue)](https://pypi.org/project/socratic-debug/)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 💡 Why Socratic?

When a runtime crash happens, most developers find themselves trapped in one of two extremes:
1. **The Intimidating Traceback:** Staring at a terrifying wall of 50-line red terminal text, unsure which line actually caused the root flaw.
2. **The "Copier" Reflex:** Blindly copying the error into an LLM chat, pasting the patch without understanding *why* it failed, only to trigger the exact same design mistake minutes later.

**Socratic Debug changes the game.**  
Instead of dumping stack traces or spoon-feeding copy-paste patches, `socratic` intercepts uncaught runtime crashes and launches a **dedicated desktop mentorship window**. It analyzes the bug silently and guides you through a calibrated, interactive dialogue to help you **discover, understand, and fix the root cause yourself.**

---

## ✨ Features

- 🖥️ **Standalone Desktop Window:** Launches an isolated, dark-themed GUI terminal window right at the center of your screen. No terminal pollution.
- 🌍 **Pure Native BiDi & Arabic Support:** Flawlessly displays English and Arabic with full Right-to-Left (RTL) text shaping and formatting.
- 🎯 **Calibrated Socratic Mentorship:** 3-tier adaptive hints (Observation ➔ Mechanism ➔ Idiomatic Prevention).
- 🧠 **Smart Evaluator:** Distinguishes between partial observations (e.g., stating a variable's value) and true comprehension before unlocking the defensive code solution.
- 🔌 **Universal LLM Support:** Plug into local models via **Ollama** (Gemma, Llama, Qwen) or cloud providers via **OpenRouter** / **Google Gemini**.
- 📊 **Built-in Observability:** Native tracing with **LangSmith** to monitor latency, tokens, and node execution graphs.
- 🌐 **Cross-Platform:** Runs seamlessly on **Linux**, **macOS**, and **Windows**.

---

## 🚀 Quick Start

### Installation

The cleanest, recommended way to install `socratic` globally across your system without virtual environment conflicts:

```bash
# Recommended (isolated global CLI)
pipx install socratic-debug

# Or via standard pip
pip install socratic-debug
```

Alternatively, use the one-line install script:
```bash
# Linux & macOS
curl -sSL https://raw.githubusercontent.com/mohamedelawakey/socratic/main/install.sh | bash

# Windows (PowerShell)
irm https://raw.githubusercontent.com/mohamedelawakey/socratic/main/install.ps1 | iex
```

---

## 🛠️ Usage

You can use `socratic` in two distinct ways:

### Method 1: Zero-Code-Change CLI Runner (Recommended)
You don't need to add any code or imports to your script! Simply prefix your execution:

```bash
socratic run my_script.py
```
- If your script runs successfully, it outputs normally.
- If an unhandled exception occurs, the **Socratic Mentor Window** springs to life immediately!

### Method 2: In-Process Runtime Hook
If you are building an application or library and want Socratic guidance baked directly into development runs:

```python
import socratic
socratic.install()

# Your regular application code
number_1 = 10
number_2 = 0
print(number_1 / number_2)  # <-- ZeroDivisionError triggers Socratic window!
```

---

## ⚙️ Configuration (`.socratic.yaml`)

When you run `socratic` for the first time, it automatically creates a `.socratic.yaml` config file in your project or home directory:

```yaml
# LLM Provider: "ollama" or "openrouter"
provider: "ollama"
provider_name: "gemma4:31b-cloud"
provider_link: "http://localhost:11434"

# API Key (for cloud providers like OpenRouter)
api_key: "your_api_key_here"

# Mentor Personality & Language ("Arabic" or "English")
socratic_language: "Arabic"
socratic_style: "friendly"

# Observability with LangSmith (Optional)
LANGSMITH_TRACING: "true"
LANGSMITH_API_KEY: "lsv2_pt_..."
LANGSMITH_PROJECT: "socratic-debug"
```

---

## 🤝 Contributing

We welcome contributions! Please review our [CONTRIBUTING.md](CONTRIBUTING.md) guidelines:
- For large architectural changes or new features, **please open a GitHub Discussion first**.
- For minor bug fixes, direct Pull Requests are warmly welcome.

Please note that this project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).

---

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for full details.

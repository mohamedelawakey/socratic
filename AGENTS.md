# AGENTS.md — Socratic Engineering & AI Agent Rules

Guidelines, architecture boundaries, and code style principles for AI agents and developers working on `socratic`.

---

## 🎯 Project Philosophy

1. **Simplicity First & High Cognitive Ergonomics:**
   - Code must be exceptionally simple, natural to read, and immediately understandable to any developer at first glance.
   - Avoid over-engineering, enterprise boilerplate, redundant wrapper classes, and clever-but-cryptic Python tricks.
   - The best solution is the one that achieves the goal with maximum runtime efficiency and minimal cognitive overhead.
2. **Pedagogical Integrity:** Socratic never spoon-feeds direct patches or fixes. It guides developers to discover the root cause themselves.
3. **Strict Minimalist Comments (Zero Fluff):**
   - **DO NOT** comment on obvious or self-explanatory code (e.g., `# set x to 10`, `# import models`, `# create session`).
   - Clean, expressive Python code documents itself.
   - Use comments **ONLY** when strictly necessary to explain non-obvious workarounds, tricky edge cases, or complex mathematical/business algorithms. If code can be understood without a comment, leave it without comments.

---

## 🏛️ Architecture & Separation of Concerns

The project follows a strict decoupled architecture:

```text
socratic/
├── src/
│   ├── agent/       # Pure LangGraph state machine, nodes, prompts, and LLM factory
│   │   ├── graph/   # StateGraph orchestration & conditional routing
│   │   ├── llm/     # LLM provider factory & invocation
│   │   ├── nodes/   # Agent nodes (diagnose, questioner, evaluate, solution)
│   │   ├── prompts/ # Localized prompt templates (English / Arabic)
│   │   ├── state/   # SocraticAgentState TypedDict
│   │   └── runner.py# Headless agent runner entrypoint
│   ├── features/    # Modular standalone domain features (independent of agent graph)
│   │   └── reports/ # Learning metrics diagnostic reporting & LLM advice service
│   ├── db/          # Database persistence, telemetry schema, detection & migration
│   ├── utils/       # Configuration IO (.socratic.yaml), parsing, file watching
│   ├── cli.py       # Global CLI commands (socratic run, socratic init)
│   ├── events.py    # Abstract EventBus decoupling Core from UI
│   ├── extractor.py # AST inspection & traceback frame extraction
│   ├── hook.py      # sys.excepthook interceptor
│   └── watcher.py   # Live background FileMonitor for real-time fix detection
└── ui/              # Presentation layer (PyQt6 Desktop GUI with CLI fallback)
    ├── app.py       # Main Qt window & UIBridge signals
    ├── features/    # Feature-driven UI domain components
    │   ├── dashboard/  # Analytics dashboard view, exporters, and dedicated charts
    │   │   ├── charts/ # Custom Qt chart components (Pie, Activity Bar)
    │   │   ├── view.py # Dashboard main view widget
    │   │   └── report_exporter.py # Multi-format report exporter
    │   └── settings/   # Settings domain components (SettingsDrawer)
    ├── styles.py    # Dark theme QSS stylesheet
    ├── translations.py # Multilingual dictionary (Arabic & English)
    └── views.py     # Unified dispatcher routing between Desktop GUI and Rich CLI
```

### 🔒 Architectural Boundaries & Strict Layer Isolation:

- **Absolute Frontend / Backend Decoupling:**
  - **Backend / Core (`src/`):** Contains pure business logic, LangGraph state machine, LLM calls, AST parsing, and file watching. Core packages (`src/agent/`, `src/features/`, `src/db/`, `src/utils/`) must remain 100% headless and completely unaware of any graphical widgets or terminal rendering libraries (with `src/cli.py` being the sole command-line dispatching entrypoint).
  - **Frontend / UI (`ui/`):** Contains presentation widgets, PyQt6 windows, CSS/QSS styles, and Rich terminal views.
  - **Forbidden Direct Coupling:** The Backend must **NEVER** import or directly invoke the Frontend (`src/` ➔ `ui/` is strictly forbidden). Likewise, UI components must **NEVER** directly import backend services or feature implementations directly (`ui/` ➔ `src/features/` or `src/db/` is strictly forbidden).
  - **The Bridge Contract:** All cross-boundary communication is strictly event-driven through an asynchronous decoupled bridge:
    - **Backend ➔ Frontend:** Managed via `src/events.py` (`EventBus`) and `ui/app.py` (`UIBridge` Qt signals). The backend simply emits an event; whoever is listening (PyQt6 window, CLI, or future web/IDE extension) renders it.
    - **Frontend ➔ Backend:** Runtime interaction events, data queries, and AI generation requests pass strictly through the `EventBus` bridge (e.g. `EventBus.request_dashboard_metrics()`, `EventBus.request_analytics_report()`, `EventBus.emit_session_cancelled()`). Presentation components must never import internal business services directly. Settings persistence from the GUI is handled via the dedicated file manager (`ConfigManager`), which safely writes to `.socratic.yaml` on disk and notifies the backend without direct coupling to agent nodes.

- **Modular Features Domain (`src/features/`):**
  - All non-core agent capabilities (e.g. analytics reports, code intelligence, future exporters) must live under `src/features/<feature_name>/` and never pollute `src/agent/`.
  - `src/agent/` remains strictly reserved for the pedagogical Socratic debugging loop (LangGraph nodes, graph edges, and prompt templates).

- **Dynamic Configuration:** Do not hardcode configurations. Always read via `src.utils.read_yaml.ReadYaml` or persist via `src.utils.config_manager.ConfigManager`.
- **Stateless Agent Nodes:** All graph nodes inside `src/agent/nodes/` must be pure functions accepting `SocraticAgentState` and returning a partial state dictionary.

---

## 💻 Code Style & Engineering Principles

- **Pragmatic Design Principles (KISS, YAGNI, DRY):**
  - **KISS (Keep It Simple, Stupid):** The simplest implementation that completely solves the problem is always the right one.
  - **YAGNI (You Aren't Gonna Need It):** Do not write code or abstractions for hypothetical future features. Build strictly what is needed now.
  - **DRY (Don't Repeat Yourself):** Consolidate genuinely shared logic without creating premature or over-complicated abstractions.
  - **Selective & Balanced SOLID:** Apply SOLID with common sense, not dogmatism. Grouping related static methods in a single cohesive utility class (e.g., `ConfigManager` or `DiagnoseNode`) is completely fine and preferred over scattering one-method classes everywhere.

- **Token Economy & Prompt Efficiency:**
  - Keep LLM prompts razor-sharp, dense, and free of fluff.
  - Send only the minimal necessary context (the offending line and compact AST surrounding lines, not thousands of irrelevant lines). Every token saved reduces latency and saves API costs for the user.

- **Precision & High Execution Accuracy:**
  - Verify syntax, edge cases, and type behavior before finalizing code.
  - No hand-waving or sloppy implementations.

- **Security & Privacy First:**
  - Never log, leak, or print sensitive keys (`api_key`, `LANGSMITH_API_KEY`) in plaintext to the console, traces, or public logs.
  - In GUI interfaces, always mask secrets by default with toggleable visibility.

- **Performance & Smooth Responsiveness:**
  - Offload long-running tasks, file watching, and LLM calls to background daemon threads to keep the UI interactive at 60 FPS.
  - Debounce disk I/O and watcher triggers to avoid CPU spikes.

- **Maintainability, Clarity & Efficiency:**
  - Write clean, expressive code that reads like well-structured English prose.
  - Prioritize simplicity and readability over cleverness; if a junior developer cannot grasp the intent in 10 seconds, refactor it to be simpler.
  - Strive for peak algorithmic efficiency without introducing complex, fragile abstractions.
  - Group functions by clear logical responsibility.
  - Use concise, intentional comments only when explaining tricky edge cases or non-intuitive logic. Avoid commenting on self-explanatory code.

- **Strict File Size Limit (Max 250 Lines):** No single source file should exceed **250 lines of code**. Large monolithic files hurt readability, increase cognitive load, and make debugging harder. When a file approaches or exceeds this limit, decompose it cleanly into focused, modular helper components or dedicated sub-modules (e.g., separating UI layout building, dialog helpers, or specialized service operations).

- **Error Handling:** Never let background threads crash the main application. Catch expected exceptions gracefully and report via the event bus or UI bridge.

---

## 🌍 Localization & BiDi Support

- `socratic` natively supports **Arabic** and **English**.
- **Mandatory Translation Dictionary:** Never hardcode user-facing strings, buttons, alerts, placeholders, or tooltips directly in UI components or agent responses.
- Any user-facing string must be declared in both languages inside `ui/translations.py` (`TRANSLATIONS["arabic"]` and `TRANSLATIONS["english"]`) and consumed dynamically via `self.translations["key_name"]`.
- Arabic UI layout direction is right-to-left (`Qt.LayoutDirection.RightToLeft`) with proper text shaping via `ui/bidi.py`.
- Prompts and LLM feedback must dynamically respect the chosen `socratic_language` ("Arabic" or "English") loaded from configuration.

---

## 📦 Dependency & Requirements Management

- **Strict PyPI Version Verification:** Whenever adding or updating a third-party dependency in `requirements.txt`:
  - **Always query and verify the latest stable release from PyPI first** before declaring it.
  - Pin versions intentionally and strictly to avoid unexpected breaking upstream changes.
- **Consistent File Structure & Style:** Adhere strictly to the established styling of `requirements.txt`:
  - Group packages by logical category under descriptive header comments (e.g., `# yaml`, `# langchain`, `# langgraph`, `# Terminal & GUI Window`, `# DB`).
  - Separate categories with a single blank line.
  - Do not pollute `requirements.txt` with transient sub-dependencies unless pinned for critical fixes.

---

## 🧹 Clean Workspace & Git Hygiene (.gitignore)

- **Strict Ignore Rules for Ephemeral Files:** Never commit temporary files, logs, generated caches, local database files, or test outputs to Git.
- **Immediate `.gitignore` Upkeep:** Whenever introducing new local artifacts, SQLite databases (e.g. `.socratic/`, `*.db`), temporary test outputs, or scratch logs, immediately verify they are covered by `.gitignore`.
- Keep the Git tree clean and pristine at all times.

---

## 🧪 Testing, CI & Verification

Before committing changes, always run the full verification pipeline locally to ensure that GitHub Actions CI will pass with zero failures:

1. **Bytecode Compilation & Clean Syntax Check:**
   ```bash
   ./venv/bin/python -m compileall src ui test
   ```

2. **Flake8 Linting (CI Critical Errors):**
   ```bash
   ./venv/bin/flake8 src ui --count --select=E9,F63,F7,F82 --show-source --statistics
   ```

3. **CI Smoke & Import Validation:**
   ```bash
   QT_QPA_PLATFORM=offscreen ./venv/bin/python -c "import socratic; import src.extractor; import src.utils.config_creator; import src.utils.config_manager; import ui.translations; print('✅ Core modules imported successfully!')"
   ```

4. **Offscreen GUI Rendering & Widget Integrity:**
   ```bash
   QT_QPA_PLATFORM=offscreen ./venv/bin/python -c "from PyQt6.QtWidgets import QApplication; from ui.app import SocraticWindow; app = QApplication([]); win = SocraticWindow('TypeError', 'err', 't.py', 1, 'x+y'); win.show(); print('GUI OK')"
   ```

5. **End-to-End Exception Interception Test:**
   ```bash
   ./venv/bin/python test/test_hook.py
   ```

6. **Full Local CI Pre-flight (All-in-One Command):**
   ```bash
   ./venv/bin/python -m compileall src ui test && ./venv/bin/flake8 src ui --count --select=E9,F63,F7,F82 --show-source --statistics && QT_QPA_PLATFORM=offscreen ./venv/bin/python -c "import socratic; import src.extractor; import src.utils.config_creator; import src.utils.config_manager; import ui.translations; print('✅ All CI tests pass!')"
   ```

# AGENTS.md — Socratic Engineering & AI Agent Rules

Guidelines, architecture boundaries, and code style principles for AI agents and developers working on `socratic`.

---

## 🎯 Project Philosophy

1. **Keep It Simple & Pythonic:** Avoid over-engineering, enterprise boilerplate, and unnecessary abstraction layers.
2. **Pedagogical Integrity:** Socratic never spoon-feeds direct patches or fixes. It guides developers to discover the root cause themselves.
3. **Purposeful Comments (Only When Needed):** Do not comment on obvious code (e.g., `# set x to 10`). Code should be clear and readable on its own. Use concise comments only when genuinely necessary to explain non-obvious business logic, tricky edge cases, or specific workarounds.

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
│   ├── utils/       # Configuration IO (.socratic.yaml), parsing, file watching
│   ├── cli.py       # Global CLI commands (socratic run, socratic init)
│   ├── events.py    # Abstract EventBus decoupling Core from UI
│   ├── extractor.py # AST inspection & traceback frame extraction
│   ├── hook.py      # sys.excepthook interceptor
│   └── watcher.py   # Live background FileMonitor for real-time fix detection
└── ui/              # Presentation layer (PyQt6 Desktop GUI with CLI fallback)
    ├── app.py       # Main Qt window & UIBridge signals
    ├── settings_drawer.py # Collapsible slide-in settings panel
    ├── styles.py    # Dark theme QSS stylesheet
    ├── translations.py # Multilingual dictionary (Arabic & English)
    └── views.py     # Unified dispatcher routing between Desktop GUI and Rich CLI
```

### 🔒 Architectural Boundaries & Strict Layer Isolation:

- **Absolute Frontend / Backend Decoupling:**
  - **Backend / Core (`src/`):** Contains pure business logic, LangGraph state machine, LLM calls, AST parsing, and file watching. Core packages (`src/agent/`, `src/utils/`) must remain 100% headless and completely unaware of any graphical widgets or terminal rendering libraries (with `src/cli.py` being the sole command-line dispatching entrypoint).
  - **Frontend / UI (`ui/`):** Contains presentation widgets, PyQt6 windows, CSS/QSS styles, and Rich terminal views.
  - **Forbidden Direct Coupling:** The Backend must **NEVER** import or directly invoke the Frontend (`src/` ➔ `ui/` is strictly forbidden). Likewise, UI components must **NEVER** tightly couple to or directly orchestrate backend nodes.
  - **The Bridge Contract:** All cross-boundary communication is strictly event-driven through an asynchronous decoupled bridge:
    - **Backend ➔ Frontend:** Managed via `src/events.py` (`EventBus`) and `ui/app.py` (`UIBridge` Qt signals). The backend simply emits an event; whoever is listening (PyQt6 window, CLI, or future web/IDE extension) renders it.
    - **Frontend ➔ Backend:** Runtime interaction events (such as user answers or cancel signals) pass through thread-safe events (`threading.Event` / `EventBus.emit_session_cancelled()`). Settings persistence from the GUI is handled via the dedicated file manager (`ConfigManager`), which safely writes to `.socratic.yaml` on disk and notifies the backend without direct coupling to agent nodes.

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

- **Maintainability & Readability:**
  - Write clean, expressive code that reads naturally.
  - Group functions by clear logical responsibility.
  - Use concise, intentional comments only when explaining tricky edge cases or non-intuitive logic. Avoid commenting on self-explanatory code.

- **Error Handling:** Never let background threads crash the main application. Catch expected exceptions gracefully and report via the event bus or UI bridge.

---

## 🌍 Localization & BiDi Support

- `socratic` natively supports **Arabic** and **English**.
- Any user-facing string must be declared in both languages inside `ui/translations.py`.
- Arabic UI layout direction is right-to-left (`Qt.LayoutDirection.RightToLeft`) with proper text shaping via `ui/bidi.py`.

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

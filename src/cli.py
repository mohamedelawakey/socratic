import sys
from pathlib import Path

# Add project root to sys.path so modules resolve everywhere
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.hook import install


def print_usage():
    print("""
🧠 Socratic Debug — Autonomous Pedagogical Debugger

Usage:
  socratic run <script.py>   Run a Python file under Socratic supervision
  socratic init              Create a default .socratic.yaml config file
  socratic --help            Show this help message
""")


def run_target_script(script_path: str, script_args: list):
    resolved_path = Path(script_path).resolve()
    if not resolved_path.exists():
        print(f"Error: File not found: {resolved_path}")
        sys.exit(1)

    # Automatically install Socratic hook before user code executes
    install()

    # Prepare execution environment simulating direct `python <script.py>`
    sys.argv = [str(resolved_path)] + script_args
    sys.path.insert(0, str(resolved_path.parent))

    # Read and execute target code in its own module namespace
    with open(resolved_path, "r", encoding="utf-8") as f:
        code_str = f.read()

    namespace = {
        "__name__": "__main__",
        "__file__": str(resolved_path),
        "__doc__": None,
    }

    try:
        exec(compile(code_str, str(resolved_path), "exec"), namespace)
    except SystemExit:
        raise
    except Exception:
        # sys.excepthook will catch this cleanly and launch Socratic!
        sys.excepthook(*sys.exc_info())


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)

    command = sys.argv[1].lower()

    if command in ("-h", "--help", "help"):
        print_usage()
        sys.exit(0)

    elif command == "init":
        from src.config_creator import create_config
        create_config()
        print("✔ Created .socratic.yaml with default settings.")
        sys.exit(0)

    elif command == "run":
        if len(sys.argv) < 3:
            print("Error: Missing script file to run.")
            print("Example: socratic run app.py")
            sys.exit(1)

        target_file = sys.argv[2]
        extra_args = sys.argv[3:]
        run_target_script(target_file, extra_args)

    else:
        # Default fallback: if user runs `socratic script.py` directly
        target_file = sys.argv[1]
        extra_args = sys.argv[2:]
        run_target_script(target_file, extra_args)


if __name__ == "__main__":
    main()

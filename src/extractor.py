import traceback
from pathlib import Path


def extract_crash_context(exception_traceback, exception_value=None) -> dict:
    # 1. Handle SyntaxError / IndentationError where location is on exception_value
    if isinstance(exception_value, SyntaxError):
        file_path = exception_value.filename or "unknown"
        line_number = exception_value.lineno or 1
        line_content = (exception_value.text or "").strip()
        snippet = get_code_snippet(file_path, line_number)

        return {
            "file_path": file_path,
            "line_number": line_number,
            "function_name": "<module>",
            "line_content": line_content,
            "code_snippet": snippet,
        }

    # 2. Handle Runtime Errors via Traceback Frames
    frames = traceback.extract_tb(exception_traceback) if exception_traceback else []

    # Find the deepest frame that belongs to user code (ignore socratic internal frames)
    socratic_src_dir = str(Path(__file__).resolve().parent)
    chosen_frame = None

    for frame in reversed(frames):
        if not frame.filename.startswith(socratic_src_dir):
            chosen_frame = frame
            break

    if chosen_frame is None and frames:
        chosen_frame = frames[-1]

    if chosen_frame:
        snippet = get_code_snippet(chosen_frame.filename, chosen_frame.lineno)
        return {
            "file_path": chosen_frame.filename,
            "line_number": chosen_frame.lineno,
            "function_name": chosen_frame.name,
            "line_content": chosen_frame.line or "",
            "code_snippet": snippet,
        }

    return {
        "file_path": "unknown",
        "line_number": 1,
        "function_name": "<unknown>",
        "line_content": "",
        "code_snippet": "",
    }


def get_code_snippet(file_path: str, line_number: int, context_lines: int = 5) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        start_lines = max(1, line_number - context_lines)
        end_lines = min(len(lines), line_number + context_lines)

        snippet_lines = []
        for i in range(start_lines, end_lines + 1):
            prefix = ">" if i == line_number else " "
            line_text = lines[i - 1]
            snippet_lines.append(f"{prefix} {i:3d} | {line_text}")

        return "".join(snippet_lines)

    except Exception as e:
        return f"Error getting code snippet: {e}"

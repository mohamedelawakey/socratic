import traceback

def extract_crash_context(exception_traceback) -> dict:
    frames = traceback.extract_tb(exception_traceback)
    last_frame = frames[-1]

    snippet = get_code_snippet(last_frame.filename, last_frame.lineno)

    return {
        "file_path": last_frame.filename,
        "line_number": last_frame.lineno,
        "function_name": last_frame.name,
        "line_content": last_frame.line,
        "code_snippet": snippet
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

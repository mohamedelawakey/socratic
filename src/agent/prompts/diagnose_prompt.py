class DiagnosePrompt:
    @staticmethod
    def diagnose_prompt(
        error_type: str,
        error_name: str,
        file_path: str,
        line_number: int,
        line_content: str,
        code_snippet: str,
        function_name: str = "",
    ) -> str:
        return f"""You are an Expert Code Diagnostic Engine. Your mission is to silently analyze a runtime crash and identify the exact root cause and the faulty variable/expression.

Crash Information:
- Error Type: {error_type}
- Error Message: {error_name}
- File: {file_path} (Function: {function_name or 'global'})
- Faulty Line #{line_number}: `{line_content}`

Surrounding Code Context:
```python
{code_snippet}
```

Instructions:
1. Identify the exact root cause: Why did this specific error occur at this exact line?
2. Identify the culprit: Which variable, index, operation, or missing key caused the crash?
3. Define the pedagogical angle: What conceptual programming misunderstanding led to this bug, and what core question should we guide the developer to reflect upon?

Output your diagnosis strictly in this format:
- Root Cause: [Concise 1-2 sentence technical explanation of why it failed]
- Culprit: [The specific variable, operation, or expression responsible]
- Pedagogical Angle: [The core programming concept the developer needs to discover]
"""

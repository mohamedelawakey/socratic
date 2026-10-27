class EvaluationPrompt:
    @staticmethod
    def evaluation_prompt(
        error_type: str,
        code_snippet: str,
        root_cause: str,
        user_input: str,
    ) -> str:
        evaluation_prompt = f"""You are an Objective Judge evaluating a developer's response during a Socratic debugging session.
Bug Context:
- Error: {error_type}
- Code Snippet:
```python
{code_snippet}
```
- Known Root Cause of the bug:
{root_cause}

Latest Developer Response:
"{user_input}"

Your Task:
Evaluate whether the developer's response shows they understand the root cause and know how to fix it, or if they are still confused/struggling, or if they gave up.

Output strictly ONE word from these three options:
- SOLVED: The developer clearly demonstrates an understanding of WHY the code failed and explains the failure mechanism or proposes a valid fix/guard to resolve it.
- STRUGGLING: The developer made a partial observation (e.g. stating a variable value or noticing a symptom without explaining why it breaks the logic or how to fix it), made an incorrect guess, expressed confusion, or asked for a hint/clarification.
- SURRENDERED: The developer explicitly gives up, refuses to think through it, or directly demands the complete answer/code fix without trying.

Classification:
        """

        return evaluation_prompt

import time
from src.agent.llm.factory import LLMFactory


class ReportService:
    @staticmethod
    def stream_analytics_report(metrics: dict, language: str = "English", on_chunk_callback=None) -> str:
        prompt = f"""You are a Pedagogical AI Coding Mentor generating a concise, motivating Learning Curve Report.

Metrics Overview:
- Total Errors Intercepted: {metrics.get('total_errors', 0)}
- Solved Count: {metrics.get('solved_count', 0)}
- Success Rate: {metrics.get('solve_rate', 100)}%
- Average Time to Solve: {metrics.get('avg_duration', 0)} seconds
- Error Types & Frequency: {metrics.get('error_counts', {})}
- Total App Launches: {metrics.get('total_launches', 0)}

Instructions:
1. Language: Strictly respond in {language}.
2. Provide a 3-part breakdown:
   - 🎯 Strengths & Progress: Praise their problem-solving rate and perseverance.
   - 🔍 Recurring Pattern: Pinpoint the most frequent error types and why they usually occur.
   - 💡 Actionable Recommendation: Give 1-2 idiomatic defensive programming tips to prevent these errors in future coding sessions.
3. Keep the tone friendly, inspiring, and concise (under 250 words). Format in clean Markdown with emojis.
"""
        try:
            llm = LLMFactory.get_llm()
            if hasattr(llm, "stream"):
                full_text = []
                for chunk in llm.stream(prompt):
                    token = chunk.content if hasattr(chunk, "content") else str(chunk)
                    full_text.append(token)
                    if on_chunk_callback:
                        on_chunk_callback(token)
                return "".join(full_text)
            else:
                response = llm.invoke(prompt)
                full_text = response.content
                if on_chunk_callback:
                    words = full_text.split(" ")
                    for i, w in enumerate(words):
                        on_chunk_callback(w + (" " if i < len(words) - 1 else ""))
                        time.sleep(0.04)
                return full_text
        except Exception as e:
            err_msg = f"⚠️ Unable to generate AI report at the moment: {e}"
            if on_chunk_callback:
                on_chunk_callback(err_msg)
            return err_msg


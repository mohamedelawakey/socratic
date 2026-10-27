import html
import re


class ChatTemplates:
    """HTML templates for rendering styled chat bubbles in QTextEdit."""

    @staticmethod
    def format_markdown(text: str) -> str:
        """Converts basic markdown code blocks and inline formatting to HTML."""
        parts = []
        lines = text.split("\n")
        in_code = False
        code_buffer = []

        for line in lines:
            if line.strip().startswith("```"):
                if in_code:
                    code_content = html.escape("\n".join(code_buffer))
                    parts.append(
                        f"<pre style='background: #0d1117; color: #58a6ff; padding: 10px; border-radius: 6px; font-family: monospace; font-size: 13px; text-align: left; direction: ltr;'>{code_content}</pre>"
                    )
                    code_buffer = []
                    in_code = False
                else:
                    in_code = True
                continue

            if in_code:
                code_buffer.append(line)
            else:
                escaped = html.escape(line)
                escaped = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', escaped)
                escaped = re.sub(
                    r'`(.*?)`',
                    r"<code style='background: #21262d; color: #79c0ff; padding: 2px 5px; border-radius: 4px; font-family: monospace; direction: ltr;'>\1</code>",
                    escaped,
                )
                parts.append(escaped + "<br/>")

        if in_code and code_buffer:
            code_content = html.escape("\n".join(code_buffer))
            parts.append(
                f"<pre style='background: #0d1117; color: #58a6ff; padding: 10px; border-radius: 6px; font-family: monospace; font-size: 13px; text-align: left; direction: ltr;'>{code_content}</pre>"
            )

        return "".join(parts)

    @staticmethod
    def mentor_bubble(content: str, hint_level: int, mentor_name: str, hint_label: str, is_arabic: bool) -> str:
        border_side = "border-right" if is_arabic else "border-left"
        formatted_html = ChatTemplates.format_markdown(content)
        return f"""
        <div style='margin-bottom: 16px; background-color: #111a2e; {border_side}: 4px solid #388bfd; border-radius: 6px; padding: 12px;'>
            <div style='color: #58a6ff; font-weight: bold; font-size: 13px; margin-bottom: 6px;'>
                🤖 {mentor_name} <span style='color: #8b949e; font-size: 11px;'>({hint_label} {hint_level}/3)</span>
            </div>
            <div style='color: #f0f6fc; font-size: 14px; line-height: 1.6;'>
                {formatted_html}
            </div>
        </div>
        """

    @staticmethod
    def user_bubble(text: str, user_tag: str, is_arabic: bool) -> str:
        border_side = "border-left" if is_arabic else "border-right"
        escaped_text = html.escape(text)
        return f"""
        <div style='margin-bottom: 16px; background-color: #1b2128; {border_side}: 4px solid #f2cc60; border-radius: 6px; padding: 10px 14px;'>
            <div style='color: #f2cc60; font-weight: bold; font-size: 12px; margin-bottom: 4px;'>
                👤 {user_tag}
            </div>
            <div style='color: #ffffff; font-size: 14px;'>
                {escaped_text}
            </div>
        </div>
        """

    @staticmethod
    def verdict_badge(verdict: str) -> str:
        color = "#3fb950" if "SOLVED" in verdict else ("#f85149" if "SURRENDER" in verdict else "#d29922")
        return f"""
        <div style='text-align: center; margin: 8px 0;'>
            <span style='background-color: #161b22; color: {color}; border: 1px solid {color}; border-radius: 12px; padding: 3px 14px; font-size: 12px; font-weight: bold;'>
                {verdict}
            </span>
        </div>
        """

    @staticmethod
    def solution_bubble(content: str, wrapup_title: str) -> str:
        formatted_html = ChatTemplates.format_markdown(content)
        return f"""
        <div style='margin-top: 14px; margin-bottom: 20px; background-color: #122119; border: 2px solid #238636; border-radius: 8px; padding: 14px;'>
            <div style='color: #3fb950; font-weight: bold; font-size: 15px; margin-bottom: 8px;'>
                {wrapup_title}
            </div>
            <div style='color: #e6edf3; font-size: 14px; line-height: 1.6;'>
                {formatted_html}
            </div>
        </div>
        """

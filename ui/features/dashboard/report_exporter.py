import os
import re
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtGui import QTextDocument
from ui.features.dashboard.docx_exporter import DocxExporter


class ReportExporter:
    @staticmethod
    def clean_markdown_to_plain(text: str) -> str:
        t = re.sub(r"#+\s*", "", text)
        t = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", t)
        t = re.sub(r"_{1,3}(.*?)_{1,3}", r"\1", t)
        t = re.sub(r"`(.*?)`", r"\1", t)
        return t.strip()

    @staticmethod
    def handle_export(parent, raw_markdown: str, format_ext: str, title: str):
        plain_content = ReportExporter.clean_markdown_to_plain(raw_markdown)
        if not plain_content:
            return

        default_name = f"socratic_learning_report.{format_ext}"
        filter_map = {
            "md": "Markdown (*.md)",
            "pdf": "PDF Document (*.pdf)",
            "docx": "Word Document (*.docx)",
        }

        file_path, _ = QFileDialog.getSaveFileName(
            parent,
            title,
            os.path.expanduser(f"~/{default_name}"),
            filter_map.get(format_ext, "All Files (*)"),
        )
        if not file_path:
            return

        if format_ext == "pdf":
            doc = QTextDocument()
            doc.setMarkdown(raw_markdown)
            doc.printToPdf(file_path)
        elif format_ext == "docx":
            DocxExporter.export_text_to_docx(plain_content, file_path)
        else:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(raw_markdown)


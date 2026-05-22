from __future__ import annotations

from pathlib import Path

import pdfplumber

from parsers.base import BaseParser, ParserError


class PDFParser(BaseParser):
    extensions = (".pdf",)

    def parse(self, file_path: Path) -> str:
        try:
            parts: list[str] = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        parts.append(page_text)
            return "\n\n".join(parts)
        except Exception as exc:
            raise ParserError(f"Failed to parse PDF: {exc}") from exc

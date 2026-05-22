from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class ParserError(Exception):
    """raised when file parsing fails"""


class BaseParser(ABC):

    extensions: tuple[str, ...] = ()

    @abstractmethod
    def parse(self, file_path: Path) -> str:
        """extract plain text from a file"""

    def supports(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.extensions

    def validate(self, file_path: Path) -> None:
        if not file_path.exists():
            raise ParserError(f"File not found: {file_path}")
        if not self.supports(file_path):
            raise ParserError(
                f"Unsupported format '{file_path.suffix}'. "
                f"Supported: {', '.join(self.extensions)}"
            )
        if file_path.stat().st_size == 0:
            raise ParserError("File is empty.")

    def extract(self, file_path: Path) -> str:
        
        self.validate(file_path)
        text = self.parse(file_path)
        cleaned = text.strip()
        if not cleaned:
            raise ParserError("No readable text found in the document.")
        return cleaned

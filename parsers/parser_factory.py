"""Factory for polymorphic parser selection."""

from __future__ import annotations

from pathlib import Path

from parsers.base import BaseParser, ParserError
from parsers.pdf_parser import PDFParser
from parsers.pptx_parser import PPTXParser
from parsers.txt_parser import TXTParser


class ParserFactory:
    """Returns the correct parser instance based on file extension."""

    _parsers: tuple[BaseParser, ...] = (
        PDFParser(),
        PPTXParser(),
        TXTParser(),
    )

    @classmethod
    def get_parser(cls, file_path: Path) -> BaseParser:
        suffix = file_path.suffix.lower()
        for parser in cls._parsers:
            if suffix in parser.extensions:
                return parser
        supported = ", ".join(ext for p in cls._parsers for ext in p.extensions)
        raise ParserError(f"Unsupported file type '{suffix}'. Supported: {supported}")

    @classmethod
    def extract_text(cls, file_path: Path) -> str:
        """Polymorphic extraction — same interface, different implementations."""
        parser = cls.get_parser(file_path)
        return parser.extract(file_path)

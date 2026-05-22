
from __future__ import annotations

from pathlib import Path

from parsers.base import BaseParser, ParserError


class TXTParser(BaseParser):
    extensions = (".txt",)

    def parse(self, file_path: Path) -> str:
        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                return file_path.read_text(encoding="latin-1")
            except Exception as exc:
                raise ParserError(f"Failed to read text file: {exc}") from exc
        except Exception as exc:
            raise ParserError(f"Failed to read text file: {exc}") from exc

import re
from typing import List, Optional
from scrapefmt.models import ScrapedTable


class TableCleaner:
    """Cleans and normalizes cell values in a ScrapedTable."""

    def __init__(self, table: ScrapedTable) -> None:
        self._table = table

    def normalize_whitespace(self) -> ScrapedTable:
        """Collapse internal whitespace and strip leading/trailing spaces."""
        def _clean(value: str) -> str:
            return re.sub(r"\s+", " ", value).strip()

        new_headers = [_clean(h) for h in self._table.headers] if self._table.headers else None
        new_rows = [[_clean(cell) for cell in row] for row in self._table.rows]
        return ScrapedTable(headers=new_headers, rows=new_rows)

    def clean(self) -> ScrapedTable:
        """Run all default cleaning steps (whitespace normalization)."""
        return self.normalize_whitespace()

    def normalize_case(self, mode: str = "lower") -> ScrapedTable:
        """Normalize the case of all cell values.

        Args:
            mode: one of 'lower', 'upper', or 'title'.

        Returns:
            A new ScrapedTable with case-normalized values.

        Raises:
            ValueError: if mode is not recognized.
        """
        modes = {"lower": str.lower, "upper": str.upper, "title": str.title}
        if mode not in modes:
            raise ValueError(f"Unknown case mode '{mode}'. Choose from: {list(modes.keys())}")

        fn = modes[mode]
        new_headers = [fn(h) for h in self._table.headers] if self._table.headers else None
        new_rows = [[fn(cell) for cell in row] for row in self._table.rows]
        return ScrapedTable(headers=new_headers, rows=new_rows)

    def replace_value(self, old: str, new: str) -> ScrapedTable:
        """Replace all exact occurrences of a cell value across the table."""
        new_headers = (
            [new if h == old else h for h in self._table.headers]
            if self._table.headers
            else None
        )
        new_rows = [
            [new if cell == old else cell for cell in row]
            for row in self._table.rows
        ]
        return ScrapedTable(headers=new_headers, rows=new_rows)

    def strip_non_printable(self) -> ScrapedTable:
        """Remove non-printable / control characters from all cell values."""
        def _strip(value: str) -> str:
            return re.sub(r"[^\x20-\x7E]", "", value)

        new_headers = [_strip(h) for h in self._table.headers] if self._table.headers else None
        new_rows = [[_strip(cell) for cell in row] for row in self._table.rows]
        return ScrapedTable(headers=new_headers, rows=new_rows)

import re
from typing import Optional, List
from scrapefmt.models import ScrapedTable
from scrapefmt.sorter import TableSorter
from scrapefmt.deduplicator import TableDeduplicator


class TableCleaner:
    """High-level utility combining sorting, deduplication, and value normalisation."""

    def __init__(self, table: ScrapedTable):
        self._table = table

    def normalize_whitespace(self) -> ScrapedTable:
        """Collapse internal whitespace and strip leading/trailing spaces."""
        def clean(val: Optional[str]) -> Optional[str]:
            if val is None:
                return None
            return re.sub(r"\s+", " ", val).strip()

        cleaned_rows = [[clean(cell) for cell in row] for row in self._table.rows]
        cleaned_headers = [clean(h) for h in self._table.headers] if self._table.headers else []
        return ScrapedTable(headers=cleaned_headers, rows=cleaned_rows)

    def normalize_case(self, mode: str = "lower") -> ScrapedTable:
        """Normalise all cell values to 'lower', 'upper', or 'title' case."""
        if mode not in ("lower", "upper", "title"):
            raise ValueError(f"Unknown mode '{mode}'. Choose 'lower', 'upper', or 'title'.")

        def apply(val: Optional[str]) -> Optional[str]:
            if val is None:
                return None
            return getattr(val, mode)()

        new_rows = [[apply(cell) for cell in row] for row in self._table.rows]
        return ScrapedTable(headers=self._table.headers, rows=new_rows)

    def remove_duplicates(self) -> ScrapedTable:
        """Remove duplicate rows."""
        return TableDeduplicator(self._table).deduplicate()

    def sort_by(self, column: str, reverse: bool = False) -> ScrapedTable:
        """Sort rows by a named column."""
        return TableSorter(self._table).sort_by_column(column, reverse=reverse)

    def full_clean(self, sort_column: Optional[str] = None) -> ScrapedTable:
        """Run normalize_whitespace, remove_duplicates, and optionally sort."""
        table = self.normalize_whitespace()
        table = TableDeduplicator(table).deduplicate()
        if sort_column:
            table = TableSorter(table).sort_by_column(sort_column)
        return table

"""Filtering utilities for ScrapedTable data."""

from typing import Callable, List, Optional
from scrapefmt.models import ScrapedTable


class TableFilter:
    """Applies row and column filters to a ScrapedTable."""

    def __init__(self, table: ScrapedTable):
        self._table = table

    def filter_rows(
        self, predicate: Callable[[List[str]], bool]
    ) -> ScrapedTable:
        """Return a new ScrapedTable containing only rows that satisfy predicate."""
        filtered = [row for row in self._table.rows if predicate(row)]
        return ScrapedTable(headers=self._table.headers, rows=filtered)

    def filter_columns(
        self, columns: List[str]
    ) -> ScrapedTable:
        """Return a new ScrapedTable with only the specified columns (by header name)."""
        if not self._table.headers:
            raise ValueError("Cannot filter columns on a table without headers.")

        indices = []
        for col in columns:
            if col not in self._table.headers:
                raise ValueError(f"Column '{col}' not found in table headers.")
            indices.append(self._table.headers.index(col))

        new_headers = [self._table.headers[i] for i in indices]
        new_rows = [[row[i] for i in indices if i < len(row)] for row in self._table.rows]
        return ScrapedTable(headers=new_headers, rows=new_rows)

    def exclude_empty_rows(self) -> ScrapedTable:
        """Return a new ScrapedTable with rows that are entirely empty removed."""
        return self.filter_rows(lambda row: any(cell.strip() for cell in row))

    def where_column_equals(
        self, column: str, value: str, case_sensitive: bool = True
    ) -> ScrapedTable:
        """Return rows where the specified column matches the given value."""
        if not self._table.headers or column not in self._table.headers:
            raise ValueError(f"Column '{column}' not found in table headers.")

        idx = self._table.headers.index(column)

        def predicate(row: List[str]) -> bool:
            cell = row[idx] if idx < len(row) else ""
            if case_sensitive:
                return cell == value
            return cell.lower() == value.lower()

        return self.filter_rows(predicate)

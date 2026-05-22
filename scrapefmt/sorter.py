from typing import Optional, Callable, List
from scrapefmt.models import ScrapedTable


class TableSorter:
    """Sorts rows in a ScrapedTable by column values."""

    def __init__(self, table: ScrapedTable):
        self._table = table

    def sort_by_column(
        self,
        column: str,
        reverse: bool = False,
        key: Optional[Callable[[str], any]] = None,
    ) -> ScrapedTable:
        """Sort rows by a named column. Requires headers."""
        if not self._table.headers:
            raise ValueError("Cannot sort by column name: table has no headers.")
        if column not in self._table.headers:
            raise KeyError(f"Column '{column}' not found in headers.")

        col_index = self._table.headers.index(column)
        sort_key = key if key else lambda row: (row[col_index] is None, row[col_index] or "")

        sorted_rows = sorted(self._table.rows, key=lambda row: sort_key(row[col_index]), reverse=reverse)
        return ScrapedTable(headers=self._table.headers, rows=sorted_rows)

    def sort_by_index(
        self,
        col_index: int,
        reverse: bool = False,
        key: Optional[Callable[[str], any]] = None,
    ) -> ScrapedTable:
        """Sort rows by a zero-based column index."""
        if not self._table.rows:
            return self._table

        num_cols = len(self._table.rows[0])
        if col_index < 0 or col_index >= num_cols:
            raise IndexError(f"Column index {col_index} out of range (0–{num_cols - 1}).")

        sort_key = key if key else lambda val: (val is None, val or "")
        sorted_rows = sorted(self._table.rows, key=lambda row: sort_key(row[col_index]), reverse=reverse)
        return ScrapedTable(headers=self._table.headers, rows=sorted_rows)

    def sort_numeric(
        self,
        column: str,
        reverse: bool = False,
    ) -> ScrapedTable:
        """Sort rows by a column interpreted as numeric values."""
        def numeric_key(val: str) -> float:
            try:
                return float(val.strip().replace(",", "")) if val else float("-inf")
            except (ValueError, AttributeError):
                return float("-inf")

        return self.sort_by_column(column, reverse=reverse, key=numeric_key)

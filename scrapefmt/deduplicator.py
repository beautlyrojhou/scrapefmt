from typing import Optional, List
from scrapefmt.models import ScrapedTable


class TableDeduplicator:
    """Removes duplicate rows from a ScrapedTable."""

    def __init__(self, table: ScrapedTable):
        self._table = table

    def deduplicate(self) -> ScrapedTable:
        """Remove fully duplicate rows, preserving first occurrence."""
        seen: List[tuple] = []
        unique_rows = []
        for row in self._table.rows:
            key = tuple(row)
            if key not in seen:
                seen.append(key)
                unique_rows.append(row)
        return ScrapedTable(headers=self._table.headers, rows=unique_rows)

    def deduplicate_by_column(self, column: str) -> ScrapedTable:
        """Remove rows with duplicate values in a named column."""
        if not self._table.headers:
            raise ValueError("Cannot deduplicate by column name: table has no headers.")
        if column not in self._table.headers:
            raise KeyError(f"Column '{column}' not found in headers.")

        col_index = self._table.headers.index(column)
        seen_values: List[str] = []
        unique_rows = []
        for row in self._table.rows:
            val = row[col_index]
            if val not in seen_values:
                seen_values.append(val)
                unique_rows.append(row)
        return ScrapedTable(headers=self._table.headers, rows=unique_rows)

    def count_duplicates(self) -> int:
        """Return the number of duplicate rows (total rows minus unique rows)."""
        unique = self.deduplicate()
        return len(self._table.rows) - len(unique.rows)

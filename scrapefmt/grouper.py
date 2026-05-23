from typing import Callable, Dict, List, Optional
from scrapefmt.models import ScrapedTable


class TableGrouper:
    """Groups rows of a ScrapedTable by a column value or custom key function."""

    def __init__(self, table: ScrapedTable) -> None:
        self.table = table

    def group_by_column(self, column: str) -> Dict[str, ScrapedTable]:
        """Group rows by the values in the specified column.

        Returns a dict mapping each unique column value to a ScrapedTable
        containing only the rows with that value.
        """
        if not self.table.headers:
            raise ValueError("Cannot group by column on a table with no headers.")
        if column not in self.table.headers:
            raise KeyError(f"Column '{column}' not found in table headers.")

        col_index = self.table.headers.index(column)
        buckets: Dict[str, List[List[str]]] = {}

        for row in self.table.rows:
            key = row[col_index] if col_index < len(row) else ""
            buckets.setdefault(key, []).append(row)

        return {
            key: ScrapedTable(headers=list(self.table.headers), rows=rows)
            for key, rows in buckets.items()
        }

    def group_by_func(
        self, key_func: Callable[[List[str]], str]
    ) -> Dict[str, ScrapedTable]:
        """Group rows using a custom key function applied to each row.

        The key function receives a row (list of strings) and returns a
        string key used for grouping.
        """
        buckets: Dict[str, List[List[str]]] = {}

        for row in self.table.rows:
            key = key_func(row)
            buckets.setdefault(key, []).append(row)

        headers = list(self.table.headers) if self.table.headers else None
        return {
            key: ScrapedTable(headers=headers, rows=rows)
            for key, rows in buckets.items()
        }

    def group_counts(self, column: str) -> Dict[str, int]:
        """Return a dict mapping each unique value in *column* to its row count."""
        groups = self.group_by_column(column)
        return {key: len(tbl.rows) for key, tbl in groups.items()}

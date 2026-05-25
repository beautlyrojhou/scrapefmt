from typing import List, Optional, Callable
from scrapefmt.models import ScrapedTable


class SplitError(Exception):
    pass


class TableSplitter:
    """Split a ScrapedTable into multiple tables based on row count or a predicate."""

    def __init__(self, table: ScrapedTable) -> None:
        self._table = table

    def split_by_size(self, chunk_size: int) -> List[ScrapedTable]:
        """Split rows into chunks of at most chunk_size rows each."""
        if chunk_size < 1:
            raise SplitError(f"chunk_size must be >= 1, got {chunk_size}")
        rows = self._table.rows
        headers = self._table.headers
        chunks: List[ScrapedTable] = []
        for i in range(0, max(len(rows), 1), chunk_size):
            chunk = rows[i : i + chunk_size]
            if chunk:
                chunks.append(ScrapedTable(headers=headers, rows=chunk))
        return chunks if chunks else [ScrapedTable(headers=headers, rows=[])]

    def split_by_predicate(
        self, predicate: Callable[[List[str]], bool]
    ) -> tuple:
        """Split rows into two tables: rows where predicate is True and where it is False."""
        headers = self._table.headers
        matched: List[List[str]] = []
        unmatched: List[List[str]] = []
        for row in self._table.rows:
            if predicate(row):
                matched.append(row)
            else:
                unmatched.append(row)
        return (
            ScrapedTable(headers=headers, rows=matched),
            ScrapedTable(headers=headers, rows=unmatched),
        )

    def split_at_row(self, index: int) -> tuple:
        """Split the table at a specific row index into two tables."""
        rows = self._table.rows
        if index < 0 or index > len(rows):
            raise SplitError(
                f"split index {index} out of range for table with {len(rows)} rows"
            )
        headers = self._table.headers
        return (
            ScrapedTable(headers=headers, rows=rows[:index]),
            ScrapedTable(headers=headers, rows=rows[index:]),
        )

from typing import Optional, List
from scrapefmt.models import ScrapedTable


class TableSlicer:
    """
    Provides row and column slicing operations on a ScrapedTable.
    """

    def __init__(self, table: ScrapedTable) -> None:
        self.table = table

    def slice_rows(self, start: int, stop: Optional[int] = None, step: int = 1) -> ScrapedTable:
        """
        Return a new ScrapedTable containing only rows[start:stop:step].
        Headers are preserved unchanged.
        """
        sliced = self.table.rows[start:stop:step]
        return ScrapedTable(headers=self.table.headers, rows=sliced)

    def head(self, n: int = 5) -> ScrapedTable:
        """
        Return the first *n* rows.
        """
        if n < 0:
            raise ValueError(f"n must be non-negative, got {n}")
        return ScrapedTable(headers=self.table.headers, rows=self.table.rows[:n])

    def tail(self, n: int = 5) -> ScrapedTable:
        """
        Return the last *n* rows.
        """
        if n < 0:
            raise ValueError(f"n must be non-negative, got {n}")
        if n == 0:
            return ScrapedTable(headers=self.table.headers, rows=[])
        return ScrapedTable(headers=self.table.headers, rows=self.table.rows[-n:])

    def slice_columns(self, indices: List[int]) -> ScrapedTable:
        """
        Return a new ScrapedTable keeping only the columns at the given *indices*.
        """
        num_cols = self.table.num_columns()
        for idx in indices:
            if idx < 0 or idx >= num_cols:
                raise IndexError(f"Column index {idx} is out of range (table has {num_cols} columns)")

        new_headers: Optional[List[str]] = None
        if self.table.headers:
            new_headers = [self.table.headers[i] for i in indices]

        new_rows = [[row[i] for i in indices] for row in self.table.rows]
        return ScrapedTable(headers=new_headers, rows=new_rows)

    def column_range(self, start: int, stop: Optional[int] = None) -> ScrapedTable:
        """
        Return a new ScrapedTable keeping columns from *start* up to (but not including) *stop*.
        """
        num_cols = self.table.num_columns()
        resolved_stop = num_cols if stop is None else stop
        indices = list(range(start, resolved_stop))
        return self.slice_columns(indices)

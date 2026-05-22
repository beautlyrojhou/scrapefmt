from typing import Optional, List
from scrapefmt.models import ScrapedTable


class TableSlicer:
    """Slice rows and columns from a ScrapedTable by index ranges."""

    def __init__(self, table: ScrapedTable) -> None:
        self._table = table

    def slice_rows(self, start: int = 0, stop: Optional[int] = None, step: int = 1) -> ScrapedTable:
        """Return a new ScrapedTable containing only rows[start:stop:step]."""
        sliced = self._table.rows[start:stop:step]
        return ScrapedTable(headers=self._table.headers, rows=sliced)

    def slice_columns(self, start: int = 0, stop: Optional[int] = None, step: int = 1) -> ScrapedTable:
        """Return a new ScrapedTable containing only columns[start:stop:step]."""
        col_slice = slice(start, stop, step)

        new_headers: Optional[List[str]] = None
        if self._table.headers:
            new_headers = self._table.headers[col_slice]

        new_rows = [row[col_slice] for row in self._table.rows]
        return ScrapedTable(headers=new_headers, rows=new_rows)

    def head(self, n: int = 5) -> ScrapedTable:
        """Return the first n rows."""
        if n < 0:
            raise ValueError(f"n must be non-negative, got {n}")
        return self.slice_rows(0, n)

    def tail(self, n: int = 5) -> ScrapedTable:
        """Return the last n rows."""
        if n < 0:
            raise ValueError(f"n must be non-negative, got {n}")
        if n == 0:
            return ScrapedTable(headers=self._table.headers, rows=[])
        return self.slice_rows(-n)

    def row_at(self, index: int) -> List[str]:
        """Return a single row by index."""
        try:
            return self._table.rows[index]
        except IndexError:
            raise IndexError(f"Row index {index} is out of range (table has {len(self._table.rows)} rows)")

    def column_at(self, index: int) -> List[str]:
        """Return all values in a single column by index."""
        num_cols = len(self._table.headers) if self._table.headers else (len(self._table.rows[0]) if self._table.rows else 0)
        if index < -num_cols or index >= num_cols:
            raise IndexError(f"Column index {index} is out of range (table has {num_cols} columns)")
        return [row[index] for row in self._table.rows]

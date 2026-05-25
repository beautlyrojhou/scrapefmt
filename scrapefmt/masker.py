from typing import Callable, Optional
from scrapefmt.models import ScrapedTable


class MaskError(Exception):
    pass


class TableMasker:
    """Masks or redacts cell values in a ScrapedTable."""

    def __init__(self, table: ScrapedTable) -> None:
        self._table = table

    def mask_column(
        self,
        column: str,
        mask: str = "***",
        predicate: Optional[Callable[[str], bool]] = None,
    ) -> "TableMasker":
        """Replace values in a column with a mask string.

        If predicate is provided, only values for which predicate returns True
        are masked. Otherwise all values in the column are masked.
        """
        headers = self._table.headers
        if headers is None:
            raise MaskError("Cannot mask column by name on a table without headers.")
        if column not in headers:
            raise MaskError(f"Column '{column}' not found in headers.")

        col_index = headers.index(column)
        new_rows = []
        for row in self._table.rows:
            new_row = list(row)
            if col_index < len(new_row):
                value = new_row[col_index]
                if predicate is None or predicate(value):
                    new_row[col_index] = mask
            new_rows.append(new_row)

        self._table = ScrapedTable(headers=headers, rows=new_rows)
        return self

    def mask_row(
        self,
        index: int,
        mask: str = "***",
    ) -> "TableMasker":
        """Replace all values in a row at the given index with a mask string."""
        rows = list(self._table.rows)
        if index < 0 or index >= len(rows):
            raise MaskError(
                f"Row index {index} is out of range for table with {len(rows)} rows."
            )
        rows[index] = [mask] * len(rows[index])
        self._table = ScrapedTable(headers=self._table.headers, rows=rows)
        return self

    def mask_by_func(
        self,
        func: Callable[[Optional[str], int, int], str],
    ) -> "TableMasker":
        """Apply func(value, row_index, col_index) to every cell; return value replaces cell."""
        new_rows = [
            [func(cell, r, c) for c, cell in enumerate(row)]
            for r, row in enumerate(self._table.rows)
        ]
        self._table = ScrapedTable(headers=self._table.headers, rows=new_rows)
        return self

    @property
    def table(self) -> ScrapedTable:
        return self._table

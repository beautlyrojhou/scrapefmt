"""Column and cell transformation utilities for scraped tables."""

from typing import Callable, Dict, List, Optional
from scrapefmt.models import ScrapedTable


class TableTransformer:
    """Applies transformations to columns or cells in a ScrapedTable."""

    def __init__(self, table: ScrapedTable):
        self._table = table

    def rename_columns(self, mapping: Dict[str, str]) -> "TableTransformer":
        """Rename columns using a {old_name: new_name} mapping."""
        if not self._table.headers:
            return self
        new_headers = [
            mapping.get(h, h) for h in self._table.headers
        ]
        self._table = ScrapedTable(headers=new_headers, rows=self._table.rows)
        return self

    def transform_column(
        self, column: str, fn: Callable[[str], str]
    ) -> "TableTransformer":
        """Apply a function to every cell in a named column."""
        if not self._table.headers or column not in self._table.headers:
            raise ValueError(f"Column '{column}' not found in table headers.")
        col_idx = self._table.headers.index(column)
        new_rows = [
            [fn(cell) if i == col_idx else cell for i, cell in enumerate(row)]
            for row in self._table.rows
        ]
        self._table = ScrapedTable(headers=self._table.headers, rows=new_rows)
        return self

    def strip_whitespace(self) -> "TableTransformer":
        """Strip leading/trailing whitespace from all cells."""
        new_rows = [
            [cell.strip() if isinstance(cell, str) else cell for cell in row]
            for row in self._table.rows
        ]
        new_headers = (
            [h.strip() for h in self._table.headers]
            if self._table.headers
            else None
        )
        self._table = ScrapedTable(headers=new_headers, rows=new_rows)
        return self

    def fill_empty(
        self, value: str = "", column: Optional[str] = None
    ) -> "TableTransformer":
        """Replace empty string cells with a default value."""
        col_idx: Optional[int] = None
        if column is not None:
            if not self._table.headers or column not in self._table.headers:
                raise ValueError(f"Column '{column}' not found.")
            col_idx = self._table.headers.index(column)

        new_rows = [
            [
                value if (cell == "" and (col_idx is None or i == col_idx)) else cell
                for i, cell in enumerate(row)
            ]
            for row in self._table.rows
        ]
        self._table = ScrapedTable(headers=self._table.headers, rows=new_rows)
        return self

    def result(self) -> ScrapedTable:
        """Return the transformed ScrapedTable."""
        return self._table

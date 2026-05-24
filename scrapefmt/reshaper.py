from typing import List, Optional
from scrapefmt.models import ScrapedTable


class ReshapeError(Exception):
    """Raised when a reshape operation cannot be completed."""
    pass


class TableReshaper:
    """Reshape a ScrapedTable by splitting or widening its structure."""

    def __init__(self, table: ScrapedTable) -> None:
        self._table = table

    def split_column(
        self,
        column: str,
        separator: str,
        new_columns: List[str],
        drop_original: bool = True,
    ) -> ScrapedTable:
        """Split a column's values by *separator* into multiple new columns."""
        headers = self._table.headers
        if headers is None:
            raise ReshapeError("split_column requires a table with headers")
        if column not in headers:
            raise ReshapeError(f"Column '{column}' not found in headers")
        if len(new_columns) < 2:
            raise ReshapeError("new_columns must contain at least 2 names")

        col_idx = headers.index(column)
        new_headers = list(headers)
        insert_at = col_idx + 1
        for name in reversed(new_columns):
            new_headers.insert(insert_at, name)
        if drop_original:
            new_headers.remove(column)

        new_rows: List[List[str]] = []
        for row in self._table.rows:
            parts = row[col_idx].split(separator, maxsplit=len(new_columns) - 1)
            parts += [""] * (len(new_columns) - len(parts))
            new_row = list(row)
            for i, part in enumerate(parts):
                new_row.insert(insert_at + i, part.strip())
            if drop_original:
                del new_row[col_idx]
            new_rows.append(new_row)

        return ScrapedTable(headers=new_headers, rows=new_rows)

    def melt(
        self,
        id_columns: List[str],
        value_name: str = "value",
        variable_name: str = "variable",
    ) -> ScrapedTable:
        """Unpivot columns that are not in *id_columns* into rows."""
        headers = self._table.headers
        if headers is None:
            raise ReshapeError("melt requires a table with headers")
        for col in id_columns:
            if col not in headers:
                raise ReshapeError(f"id_column '{col}' not found in headers")

        value_columns = [h for h in headers if h not in id_columns]
        if not value_columns:
            raise ReshapeError("No value columns remain after removing id_columns")

        new_headers = id_columns + [variable_name, value_name]
        new_rows: List[List[str]] = []
        for row in self._table.rows:
            id_vals = [row[headers.index(c)] for c in id_columns]
            for vc in value_columns:
                new_rows.append(id_vals + [vc, row[headers.index(vc)]])

        return ScrapedTable(headers=new_headers, rows=new_rows)

    def fill_down(self, column: Optional[str] = None) -> ScrapedTable:
        """Forward-fill empty cells in *column* (or all columns if None)."""
        headers = self._table.headers
        indices: List[int]
        if column is not None:
            if headers is None:
                raise ReshapeError("fill_down with column name requires headers")
            if column not in headers:
                raise ReshapeError(f"Column '{column}' not found")
            indices = [headers.index(column)]
        else:
            indices = list(range(len(self._table.rows[0]))) if self._table.rows else []

        last_seen: dict = {}
        new_rows: List[List[str]] = []
        for row in self._table.rows:
            new_row = list(row)
            for idx in indices:
                if new_row[idx] == "":
                    new_row[idx] = last_seen.get(idx, "")
                else:
                    last_seen[idx] = new_row[idx]
            new_rows.append(new_row)

        return ScrapedTable(headers=headers, rows=new_rows)

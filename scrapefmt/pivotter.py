from typing import Optional, Dict, List, Any
from scrapefmt.models import ScrapedTable


class PivotError(Exception):
    """Raised when a pivot operation cannot be completed."""
    pass


class TablePivotter:
    """Pivots a ScrapedTable by rotating rows into columns or vice versa."""

    def __init__(self, table: ScrapedTable) -> None:
        self.table = table

    def pivot(self, index_col: str, column_col: str, value_col: str) -> ScrapedTable:
        """Create a pivot table from three named columns.

        Args:
            index_col: Column whose unique values become the new row index.
            column_col: Column whose unique values become the new column headers.
            value_col: Column whose values populate the pivot cells.

        Returns:
            A new ScrapedTable with pivoted data.
        """
        if not self.table.headers:
            raise PivotError("Cannot pivot a table without headers.")

        headers = self.table.headers
        for col in (index_col, column_col, value_col):
            if col not in headers:
                raise PivotError(f"Column '{col}' not found in table headers.")

        idx_i = headers.index(index_col)
        col_i = headers.index(column_col)
        val_i = headers.index(value_col)

        # Collect unique index values (preserving order)
        index_values: List[str] = []
        seen_index = set()
        col_values: List[str] = []
        seen_cols = set()

        for row in self.table.rows:
            iv = row[idx_i] if idx_i < len(row) else ""
            cv = row[col_i] if col_i < len(row) else ""
            if iv not in seen_index:
                index_values.append(iv)
                seen_index.add(iv)
            if cv not in seen_cols:
                col_values.append(cv)
                seen_cols.add(cv)

        # Build lookup: (index_value, col_value) -> cell_value
        lookup: Dict[tuple, str] = {}
        for row in self.table.rows:
            iv = row[idx_i] if idx_i < len(row) else ""
            cv = row[col_i] if col_i < len(row) else ""
            vv = row[val_i] if val_i < len(row) else ""
            lookup[(iv, cv)] = vv

        new_headers = [index_col] + col_values
        new_rows: List[List[Any]] = []
        for iv in index_values:
            row = [iv] + [lookup.get((iv, cv), "") for cv in col_values]
            new_rows.append(row)

        return ScrapedTable(headers=new_headers, rows=new_rows)

    def transpose(self) -> ScrapedTable:
        """Transpose the table so rows become columns and columns become rows.

        If the table has headers, they become the first column of the result.
        """
        all_rows: List[List[Any]] = []
        if self.table.headers:
            all_rows.append(list(self.table.headers))
        all_rows.extend([list(r) for r in self.table.rows])

        if not all_rows:
            return ScrapedTable(headers=[], rows=[])

        max_len = max(len(r) for r in all_rows)
        # Pad shorter rows
        padded = [r + [""] * (max_len - len(r)) for r in all_rows]
        transposed = [list(col) for col in zip(*padded)]

        new_headers = transposed[0] if transposed else []
        new_rows = transposed[1:] if len(transposed) > 1 else []
        return ScrapedTable(headers=new_headers, rows=new_rows)

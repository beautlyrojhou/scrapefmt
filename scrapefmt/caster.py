"""Type casting utilities for ScrapedTable columns."""

from typing import Any, Callable, Dict, List, Optional
from scrapefmt.models import ScrapedTable


class CastError(Exception):
    """Raised when a column value cannot be cast to the target type."""
    pass


class TableCaster:
    """Casts column values in a ScrapedTable to specified Python types."""

    def __init__(self, table: ScrapedTable) -> None:
        self._table = table

    def cast_column(self, column: str, cast_fn: Callable[[str], Any], errors: str = "raise") -> ScrapedTable:
        """Cast all values in a column using the provided callable.

        Args:
            column: The column name to cast.
            cast_fn: A callable that converts a string to the target type.
            errors: 'raise' to raise CastError on failure, 'ignore' to leave value unchanged,
                    'null' to replace with None.

        Returns:
            A new ScrapedTable with the column values cast.
        """
        if self._table.headers is None or column not in self._table.headers:
            raise ValueError(f"Column '{column}' not found in table headers.")

        col_index = self._table.headers.index(column)
        new_rows: List[List[Any]] = []

        for row in self._table.rows:
            new_row = list(row)
            raw = new_row[col_index]
            try:
                new_row[col_index] = cast_fn(raw)
            except (ValueError, TypeError) as exc:
                if errors == "raise":
                    raise CastError(f"Cannot cast value '{raw}' in column '{column}': {exc}") from exc
                elif errors == "null":
                    new_row[col_index] = None
                # 'ignore' leaves value unchanged
            new_rows.append(new_row)

        return ScrapedTable(headers=list(self._table.headers), rows=new_rows)

    def cast_int(self, column: str, errors: str = "raise") -> ScrapedTable:
        """Cast a column to integers."""
        return self.cast_column(column, lambda v: int(str(v).strip()), errors=errors)

    def cast_float(self, column: str, errors: str = "raise") -> ScrapedTable:
        """Cast a column to floats."""
        return self.cast_column(column, lambda v: float(str(v).strip()), errors=errors)

    def cast_bool(self, column: str, true_values: Optional[List[str]] = None,
                  false_values: Optional[List[str]] = None, errors: str = "raise") -> ScrapedTable:
        """Cast a column to booleans based on configurable true/false value lists."""
        _true = [v.lower() for v in (true_values or ["true", "yes", "1"])]
        _false = [v.lower() for v in (false_values or ["false", "no", "0"])]

        def _to_bool(v: str) -> bool:
            lower = str(v).strip().lower()
            if lower in _true:
                return True
            if lower in _false:
                return False
            raise ValueError(f"Unrecognised boolean value: '{v}'")

        return self.cast_column(column, _to_bool, errors=errors)

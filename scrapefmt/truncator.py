from typing import Optional
from scrapefmt.models import ScrapedTable


class TruncateError(Exception):
    """Raised when truncation parameters are invalid."""


class TableTruncator:
    """Truncates cell values in a ScrapedTable to a maximum length."""

    def __init__(self, table: ScrapedTable) -> None:
        self._table = table

    def truncate_cells(
        self,
        max_length: int,
        placeholder: str = "...",
        columns: Optional[list] = None,
    ) -> "TableTruncator":
        """Truncate all cell values (or only specified columns) to max_length.

        If a value exceeds max_length, it is trimmed and the placeholder is
        appended.  The placeholder itself counts toward max_length.

        Args:
            max_length: Maximum number of characters per cell.
            placeholder: String appended to truncated values.
            columns: Optional list of column names to restrict truncation to.
                     If None, all columns are affected.

        Raises:
            TruncateError: If max_length is less than len(placeholder).
        """
        if max_length < len(placeholder):
            raise TruncateError(
                f"max_length ({max_length}) must be >= len(placeholder) ({len(placeholder)})"
            )

        col_indices: Optional[set] = None
        if columns is not None:
            if not self._table.headers:
                raise TruncateError("Cannot filter by column name: table has no headers.")
            header_index = {h: i for i, h in enumerate(self._table.headers)}
            missing = [c for c in columns if c not in header_index]
            if missing:
                raise TruncateError(f"Unknown column(s): {missing}")
            col_indices = {header_index[c] for c in columns}

        cut = max_length - len(placeholder)

        new_rows = []
        for row in self._table.rows:
            new_row = []
            for idx, cell in enumerate(row):
                if col_indices is None or idx in col_indices:
                    if len(cell) > max_length:
                        cell = cell[:cut] + placeholder
                new_row.append(cell)
            new_rows.append(new_row)

        self._table = ScrapedTable(
            headers=self._table.headers,
            rows=new_rows,
        )
        return self

    def truncate_column(
        self, column: str, max_length: int, placeholder: str = "..."
    ) -> "TableTruncator":
        """Convenience method to truncate a single named column."""
        return self.truncate_cells(max_length, placeholder=placeholder, columns=[column])

    @property
    def table(self) -> ScrapedTable:
        return self._table

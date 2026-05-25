from typing import Optional, List
from scrapefmt.models import ScrapedTable


class NormalizeError(Exception):
    pass


class TableNormalizer:
    """Normalizes cell values in a ScrapedTable."""

    def __init__(self, table: ScrapedTable) -> None:
        self._table = table

    def lowercase(self) -> "TableNormalizer":
        """Convert all cell values to lowercase."""
        new_rows = [
            [cell.lower() if isinstance(cell, str) else cell for cell in row]
            for row in self._table.rows
        ]
        self._table = ScrapedTable(headers=self._table.headers, rows=new_rows)
        return self

    def uppercase(self) -> "TableNormalizer":
        """Convert all cell values to uppercase."""
        new_rows = [
            [cell.upper() if isinstance(cell, str) else cell for cell in row]
            for row in self._table.rows
        ]
        self._table = ScrapedTable(headers=self._table.headers, rows=new_rows)
        return self

    def fill_empty(self, fill_value: str = "") -> "TableNormalizer":
        """Replace None or whitespace-only cells with a fill value."""
        def _fill(cell):
            if cell is None:
                return fill_value
            if isinstance(cell, str) and cell.strip() == "":
                return fill_value
            return cell

        new_rows = [[_fill(cell) for cell in row] for row in self._table.rows]
        self._table = ScrapedTable(headers=self._table.headers, rows=new_rows)
        return self

    def truncate(self, max_length: int) -> "TableNormalizer":
        """Truncate all string cell values to a maximum length."""
        if max_length < 0:
            raise NormalizeError("max_length must be non-negative")
        new_rows = [
            [cell[:max_length] if isinstance(cell, str) else cell for cell in row]
            for row in self._table.rows
        ]
        self._table = ScrapedTable(headers=self._table.headers, rows=new_rows)
        return self

    def replace(self, old: str, new: str) -> "TableNormalizer":
        """Replace occurrences of `old` with `new` in all string cells."""
        new_rows = [
            [cell.replace(old, new) if isinstance(cell, str) else cell for cell in row]
            for row in self._table.rows
        ]
        self._table = ScrapedTable(headers=self._table.headers, rows=new_rows)
        return self

    def result(self) -> ScrapedTable:
        """Return the normalized ScrapedTable."""
        return self._table

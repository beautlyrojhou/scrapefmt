from typing import Dict, List, Optional, Callable
from scrapefmt.models import ScrapedTable


class RenameError(Exception):
    """Raised when a rename operation cannot be completed."""
    pass


class TableRenamer:
    """Renames headers in a ScrapedTable using various strategies."""

    def __init__(self, table: ScrapedTable) -> None:
        self._table = table

    def rename(self, mapping: Dict[str, str]) -> ScrapedTable:
        """Rename specific headers by exact name match.

        Args:
            mapping: dict of {old_name: new_name}

        Returns:
            A new ScrapedTable with updated headers.

        Raises:
            RenameError: if any key in mapping is not found in headers.
        """
        if not self._table.headers:
            raise RenameError("Cannot rename columns on a table with no headers.")

        unknown = [k for k in mapping if k not in self._table.headers]
        if unknown:
            raise RenameError(f"Unknown header(s): {unknown}")

        new_headers = [mapping.get(h, h) for h in self._table.headers]
        return ScrapedTable(headers=new_headers, rows=self._table.rows)

    def rename_by_index(self, index_mapping: Dict[int, str]) -> ScrapedTable:
        """Rename headers by their positional index.

        Args:
            index_mapping: dict of {column_index: new_name}

        Returns:
            A new ScrapedTable with updated headers.

        Raises:
            RenameError: if any index is out of range or table has no headers.
        """
        if not self._table.headers:
            raise RenameError("Cannot rename columns on a table with no headers.")

        num_cols = len(self._table.headers)
        for idx in index_mapping:
            if idx < 0 or idx >= num_cols:
                raise RenameError(f"Column index {idx} is out of range (0-{num_cols - 1}).")

        new_headers = list(self._table.headers)
        for idx, name in index_mapping.items():
            new_headers[idx] = name
        return ScrapedTable(headers=new_headers, rows=self._table.rows)

    def rename_with_func(self, func: Callable[[str], str]) -> ScrapedTable:
        """Apply a function to every header to produce new names.

        Args:
            func: callable that accepts a header string and returns a new string.

        Returns:
            A new ScrapedTable with transformed headers.
        """
        if not self._table.headers:
            return ScrapedTable(headers=None, rows=self._table.rows)

        new_headers = [func(h) for h in self._table.headers]
        return ScrapedTable(headers=new_headers, rows=self._table.rows)

    def add_prefix(self, prefix: str) -> ScrapedTable:
        """Prepend a prefix string to every header."""
        return self.rename_with_func(lambda h: f"{prefix}{h}")

    def add_suffix(self, suffix: str) -> ScrapedTable:
        """Append a suffix string to every header."""
        return self.rename_with_func(lambda h: f"{h}{suffix}")

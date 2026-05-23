from typing import Optional
from scrapefmt.models import ScrapedTable


class TableFlattener:
    """
    Flattens a ScrapedTable into various flat representations,
    such as a list of values, a key-value pair list, or a single
    concatenated string per row.
    """

    def __init__(self, table: ScrapedTable):
        self.table = table

    def flatten_to_values(self) -> list[list[str]]:
        """Return all rows as flat lists of string values, excluding headers."""
        return [list(row) for row in self.table.rows]

    def flatten_to_strings(self, separator: str = " | ") -> list[str]:
        """
        Flatten each row into a single joined string.

        Args:
            separator: String used to join cell values within a row.

        Returns:
            List of joined row strings.
        """
        return [separator.join(row) for row in self.table.rows]

    def flatten_with_headers(self, separator: str = ": ", row_sep: str = " | ") -> list[str]:
        """
        Flatten each row into a string with header-prefixed values.
        Requires the table to have headers.

        Args:
            separator: String between header and value (e.g. "Name: Alice").
            row_sep: String between each header-value pair in a row.

        Returns:
            List of strings, one per row.

        Raises:
            ValueError: If the table has no headers.
        """
        if not self.table.headers:
            raise ValueError("Table has no headers; cannot flatten with headers.")

        result = []
        for row in self.table.rows:
            pairs = [
                f"{header}{separator}{value}"
                for header, value in zip(self.table.headers, row)
            ]
            result.append(row_sep.join(pairs))
        return result

    def flatten_to_dict_values(self) -> list[list[tuple[str, str]]]:
        """
        Return each row as a list of (header, value) tuples.

        Raises:
            ValueError: If the table has no headers.
        """
        if not self.table.headers:
            raise ValueError("Table has no headers; cannot produce keyed tuples.")

        return [
            list(zip(self.table.headers, row))
            for row in self.table.rows
        ]

from typing import List, Optional, Callable
from scrapefmt.models import ScrapedTable


class SearchError(Exception):
    pass


class TableSearcher:
    """Search for rows or cells within a ScrapedTable."""

    def __init__(self, table: ScrapedTable) -> None:
        self._table = table

    def find_rows(self, predicate: Callable[[List[str]], bool]) -> List[List[str]]:
        """Return all data rows matching the given predicate."""
        return [row for row in self._table.rows if predicate(row)]

    def find_rows_containing(self, value: str, case_sensitive: bool = False) -> List[List[str]]:
        """Return all data rows that contain the given value in any cell."""
        if not case_sensitive:
            value = value.lower()
        result = []
        for row in self._table.rows:
            cells = [c.lower() for c in row] if not case_sensitive else row
            if any(value in cell for cell in cells):
                result.append(row)
        return result

    def find_in_column(self, column: str, value: str, case_sensitive: bool = False) -> List[List[str]]:
        """Return rows where the specified column contains the given value."""
        if not self._table.headers:
            raise SearchError("Table has no headers; cannot search by column name.")
        if column not in self._table.headers:
            raise SearchError(f"Column '{column}' not found in headers.")
        col_index = self._table.headers.index(column)
        if not case_sensitive:
            value = value.lower()
        result = []
        for row in self._table.rows:
            cell = row[col_index] if col_index < len(row) else ""
            cell_cmp = cell.lower() if not case_sensitive else cell
            if value in cell_cmp:
                result.append(row)
        return result

    def find_cells(self, predicate: Callable[[str], bool]) -> List[tuple]:
        """Return (row_index, col_index, value) tuples for cells matching predicate."""
        matches = []
        for r_idx, row in enumerate(self._table.rows):
            for c_idx, cell in enumerate(row):
                if predicate(cell):
                    matches.append((r_idx, c_idx, cell))
        return matches

    def count_occurrences(self, value: str, case_sensitive: bool = False) -> int:
        """Count total occurrences of value across all data cells."""
        if not case_sensitive:
            value = value.lower()
        count = 0
        for row in self._table.rows:
            for cell in row:
                cell_cmp = cell.lower() if not case_sensitive else cell
                if value in cell_cmp:
                    count += 1
        return count

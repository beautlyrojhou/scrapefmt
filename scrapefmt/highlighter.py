from typing import Callable, Dict, List, Optional
from scrapefmt.models import ScrapedTable


class HighlightError(Exception):
    pass


class TableHighlighter:
    """Annotates table cells with highlight labels based on predicates."""

    def __init__(self, table: ScrapedTable) -> None:
        self._table = table
        self._highlights: Dict[str, str] = {}

    def highlight_column(
        self,
        column: str,
        predicate: Callable[[str], bool],
        label: str = "highlight",
    ) -> "TableHighlighter":
        """Mark cells in *column* where predicate returns True."""
        if self._table.headers is None:
            raise HighlightError("Cannot highlight by column name: table has no headers")
        if column not in self._table.headers:
            raise HighlightError(f"Column '{column}' not found in headers")
        col_index = self._table.headers.index(column)
        for row_index, row in enumerate(self._table.rows):
            if col_index < len(row) and predicate(row[col_index]):
                key = f"{row_index}:{col_index}"
                self._highlights[key] = label
        return self

    def highlight_row(
        self,
        predicate: Callable[[List[str]], bool],
        label: str = "highlight",
    ) -> "TableHighlighter":
        """Mark all cells in rows where predicate returns True."""
        for row_index, row in enumerate(self._table.rows):
            if predicate(row):
                for col_index in range(len(row)):
                    key = f"{row_index}:{col_index}"
                    self._highlights[key] = label
        return self

    def get_highlights(self) -> Dict[str, str]:
        """Return a copy of the current highlights mapping."""
        return dict(self._highlights)

    def highlighted_cells(self, label: Optional[str] = None) -> List[Dict]:
        """Return a list of dicts describing highlighted cells.

        Each dict contains: row_index, col_index, value, label.
        Optionally filter by *label*.
        """
        results = []
        for key, lbl in self._highlights.items():
            if label is not None and lbl != label:
                continue
            row_index, col_index = map(int, key.split(":"))
            row = self._table.rows[row_index]
            value = row[col_index] if col_index < len(row) else ""
            results.append(
                {
                    "row_index": row_index,
                    "col_index": col_index,
                    "value": value,
                    "label": lbl,
                }
            )
        return results

    def clear(self) -> "TableHighlighter":
        """Remove all highlights."""
        self._highlights.clear()
        return self

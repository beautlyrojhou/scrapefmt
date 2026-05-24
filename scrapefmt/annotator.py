from typing import Any, Callable, Dict, List, Optional
from scrapefmt.models import ScrapedTable


class AnnotateError(Exception):
    pass


class TableAnnotator:
    """Adds metadata annotations to cells, rows, or columns of a ScrapedTable."""

    def __init__(self, table: ScrapedTable) -> None:
        self._table = table
        self._annotations: Dict[str, Any] = {}

    def annotate_column(
        self,
        column: str,
        key: str,
        value_fn: Callable[[str], Any],
    ) -> "TableAnnotator":
        """Annotate each cell in a column using value_fn(cell_value)."""
        if self._table.headers is None:
            raise AnnotateError("Cannot annotate by column name: table has no headers.")
        if column not in self._table.headers:
            raise AnnotateError(f"Column '{column}' not found in headers.")
        col_index = self._table.headers.index(column)
        annotations = []
        for row in self._table.rows:
            cell = row[col_index] if col_index < len(row) else ""
            annotations.append({key: value_fn(cell)})
        self._annotations[f"column:{column}"] = annotations
        return self

    def annotate_row(
        self,
        row_index: int,
        key: str,
        value: Any,
    ) -> "TableAnnotator":
        """Annotate an entire row with a static key/value pair."""
        if row_index < 0 or row_index >= len(self._table.rows):
            raise AnnotateError(
                f"Row index {row_index} is out of range (table has {len(self._table.rows)} rows)."
            )
        annotation_key = f"row:{row_index}"
        if annotation_key not in self._annotations:
            self._annotations[annotation_key] = {}
        self._annotations[annotation_key][key] = value
        return self

    def annotate_rows_by(
        self,
        key: str,
        predicate: Callable[[List[str]], Any],
    ) -> "TableAnnotator":
        """Annotate all rows using predicate(row) -> annotation value."""
        for i, row in enumerate(self._table.rows):
            annotation_key = f"row:{i}"
            if annotation_key not in self._annotations:
                self._annotations[annotation_key] = {}
            self._annotations[annotation_key][key] = predicate(row)
        return self

    def get_annotations(self) -> Dict[str, Any]:
        """Return all collected annotations."""
        return dict(self._annotations)

    def get_row_annotation(self, row_index: int) -> Dict[str, Any]:
        """Return annotations for a specific row index."""
        return self._annotations.get(f"row:{row_index}", {})

    def get_column_annotation(self, column: str) -> List[Any]:
        """Return per-cell annotations for a specific column."""
        return self._annotations.get(f"column:{column}", [])

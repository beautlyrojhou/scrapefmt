from typing import List, Dict, Any, Optional
from scrapefmt.models import ScrapedTable


class ConvertError(Exception):
    pass


class TableConverter:
    """Converts a ScrapedTable into alternative in-memory representations."""

    def __init__(self, table: ScrapedTable) -> None:
        if not isinstance(table, ScrapedTable):
            raise ConvertError("table must be a ScrapedTable instance")
        self._table = table

    def to_dict_of_lists(self) -> Dict[str, List[Any]]:
        """Return {header: [col_values, ...]} mapping."""
        if not self._table.headers:
            raise ConvertError("Table has no headers; cannot convert to dict of lists")
        result: Dict[str, List[Any]] = {h: [] for h in self._table.headers}
        for row in self._table.rows:
            for i, header in enumerate(self._table.headers):
                result[header].append(row[i] if i < len(row) else None)
        return result

    def to_list_of_lists(self, include_headers: bool = True) -> List[List[Any]]:
        """Return rows as a plain list of lists, optionally prepending headers."""
        result: List[List[Any]] = []
        if include_headers and self._table.headers:
            result.append(list(self._table.headers))
        result.extend(list(row) for row in self._table.rows)
        return result

    def to_transposed_list(self) -> List[List[Any]]:
        """Return columns as rows (transpose)."""
        all_rows = self.to_list_of_lists(include_headers=False)
        if not all_rows:
            return []
        num_cols = max(len(r) for r in all_rows)
        return [
            [row[col] if col < len(row) else None for row in all_rows]
            for col in range(num_cols)
        ]

    def to_indexed_dict(
        self, key_column: str
    ) -> Dict[str, Dict[str, Any]]:
        """Return {key_col_value: {header: value, ...}} mapping."""
        if not self._table.headers:
            raise ConvertError("Table has no headers; cannot build indexed dict")
        if key_column not in self._table.headers:
            raise ConvertError(f"Key column '{key_column}' not found in headers")
        key_idx = list(self._table.headers).index(key_column)
        result: Dict[str, Dict[str, Any]] = {}
        for row in self._table.rows:
            key = str(row[key_idx]) if key_idx < len(row) else ""
            result[key] = {
                h: (row[i] if i < len(row) else None)
                for i, h in enumerate(self._table.headers)
            }
        return result

    def to_flat_list(self) -> List[Any]:
        """Return every cell value as a single flat list (row-major order)."""
        return [cell for row in self._table.rows for cell in row]

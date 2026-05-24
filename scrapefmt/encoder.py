from typing import Any, Dict, List, Optional
from scrapefmt.models import ScrapedTable


class EncodeError(Exception):
    pass


class TableEncoder:
    """Encodes a ScrapedTable into various serializable representations."""

    def __init__(self, table: ScrapedTable) -> None:
        self._table = table

    def to_records(self) -> List[Dict[str, Any]]:
        """Encode table as a list of dicts keyed by header name.
        Falls back to column index strings if no headers are present."""
        headers = self._table.headers
        if headers:
            keys = headers
        else:
            keys = [str(i) for i in range(self._table.num_columns())]

        records = []
        for row in self._table.rows:
            padded = list(row) + [""] * (len(keys) - len(row))
            records.append(dict(zip(keys, padded[: len(keys)])))
        return records

    def to_matrix(self) -> List[List[Any]]:
        """Encode table as a 2-D list, with headers as the first row if present."""
        matrix: List[List[Any]] = []
        if self._table.headers:
            matrix.append(list(self._table.headers))
        matrix.extend(list(row) for row in self._table.rows)
        return matrix

    def to_column_map(self) -> Dict[str, List[Any]]:
        """Encode table as a dict mapping each header to its column values.
        Raises EncodeError if the table has no headers."""
        if not self._table.headers:
            raise EncodeError("to_column_map requires a table with headers")

        col_map: Dict[str, List[Any]] = {h: [] for h in self._table.headers}
        for row in self._table.rows:
            for idx, header in enumerate(self._table.headers):
                value = row[idx] if idx < len(row) else ""
                col_map[header].append(value)
        return col_map

    def to_indexed(self, start: int = 0) -> Dict[int, Dict[str, Any]]:
        """Encode table as a dict keyed by row index."""
        records = self.to_records()
        return {start + i: record for i, record in enumerate(records)}

from typing import Any, Dict, List, Optional
from .models import ScrapedTable


class TableSummarizer:
    """Generates summary statistics and metadata for a ScrapedTable."""

    def __init__(self, table: ScrapedTable) -> None:
        self.table = table

    def summarize(self) -> Dict[str, Any]:
        """Return a dictionary of summary information about the table."""
        return {
            "num_rows": self.table.num_rows(),
            "num_columns": self.table.num_columns(),
            "headers": self.table.headers,
            "has_headers": self.table.headers is not None,
            "empty_row_count": self._count_empty_rows(),
            "column_stats": self._column_stats(),
        }

    def _count_empty_rows(self) -> int:
        """Count rows where all cells are empty or whitespace."""
        count = 0
        for row in self.table.rows:
            if all(cell.strip() == "" for cell in row):
                count += 1
        return count

    def _column_stats(self) -> List[Dict[str, Any]]:
        """Return per-column statistics."""
        if not self.table.rows:
            return []

        num_cols = self.table.num_columns()
        stats = []
        for col_idx in range(num_cols):
            values = [row[col_idx] for row in self.table.rows if col_idx < len(row)]
            non_empty = [v for v in values if v.strip() != ""]
            header = (
                self.table.headers[col_idx]
                if self.table.headers and col_idx < len(self.table.headers)
                else None
            )
            stats.append(
                {
                    "header": header,
                    "total_values": len(values),
                    "non_empty_values": len(non_empty),
                    "empty_values": len(values) - len(non_empty),
                    "fill_rate": round(len(non_empty) / len(values), 4) if values else 0.0,
                }
            )
        return stats

    def column_fill_rates(self) -> Dict[Optional[str], float]:
        """Return a mapping of column header (or index) to fill rate."""
        result: Dict[Optional[str], float] = {}
        for idx, stat in enumerate(self._column_stats()):
            key = stat["header"] if stat["header"] is not None else idx
            result[key] = stat["fill_rate"]
        return result

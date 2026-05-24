from typing import Callable, Dict, List, Optional, Any
from scrapefmt.models import ScrapedTable


class AggregateError(Exception):
    pass


class TableAggregator:
    """Aggregate numeric column values using common functions."""

    def __init__(self, table: ScrapedTable) -> None:
        self._table = table

    def _get_column_values(self, column: str) -> List[str]:
        if not self._table.headers:
            raise AggregateError("Table has no headers; cannot aggregate by column name.")
        if column not in self._table.headers:
            raise AggregateError(f"Column '{column}' not found in headers.")
        idx = self._table.headers.index(column)
        return [row[idx] for row in self._table.rows]

    def _to_floats(self, values: List[str]) -> List[float]:
        result: List[float] = []
        for v in values:
            try:
                result.append(float(v.strip()))
            except (ValueError, AttributeError):
                pass
        return result

    def sum(self, column: str) -> float:
        """Return the sum of numeric values in a column."""
        return sum(self._to_floats(self._get_column_values(column)))

    def mean(self, column: str) -> float:
        """Return the arithmetic mean of numeric values in a column."""
        values = self._to_floats(self._get_column_values(column))
        if not values:
            raise AggregateError(f"No numeric values found in column '{column}'.")
        return sum(values) / len(values)

    def min(self, column: str) -> float:
        """Return the minimum numeric value in a column."""
        values = self._to_floats(self._get_column_values(column))
        if not values:
            raise AggregateError(f"No numeric values found in column '{column}'.")
        return min(values)

    def max(self, column: str) -> float:
        """Return the maximum numeric value in a column."""
        values = self._to_floats(self._get_column_values(column))
        if not values:
            raise AggregateError(f"No numeric values found in column '{column}'.")
        return max(values)

    def count(self, column: str) -> int:
        """Return the number of non-empty values in a column."""
        return sum(1 for v in self._get_column_values(column) if v.strip())

    def aggregate(self, column: str, func: Callable[[List[float]], Any]) -> Any:
        """Apply a custom aggregation function to numeric values of a column."""
        values = self._to_floats(self._get_column_values(column))
        return func(values)

    def summarize_column(self, column: str) -> Dict[str, Any]:
        """Return a dict with sum, mean, min, max, and count for a column."""
        values = self._to_floats(self._get_column_values(column))
        if not values:
            return {"sum": None, "mean": None, "min": None, "max": None, "count": 0}
        return {
            "sum": sum(values),
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "count": len(values),
        }

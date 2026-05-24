from typing import Optional
import random

from scrapefmt.models import ScrapedTable


class SampleError(Exception):
    pass


class TableSampler:
    """Randomly or deterministically sample rows from a ScrapedTable."""

    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)

    def sample(self, table: ScrapedTable, n: int) -> ScrapedTable:
        """Return a new table with *n* randomly sampled rows (without replacement)."""
        if n < 0:
            raise SampleError(f"Sample size must be non-negative, got {n}")
        if n > len(table.rows):
            raise SampleError(
                f"Sample size {n} exceeds number of rows {len(table.rows)}"
            )
        sampled = self._rng.sample(table.rows, n)
        return ScrapedTable(headers=table.headers, rows=sampled)

    def sample_fraction(self, table: ScrapedTable, fraction: float) -> ScrapedTable:
        """Return a new table with a random fraction of rows."""
        if not (0.0 <= fraction <= 1.0):
            raise SampleError(f"Fraction must be between 0.0 and 1.0, got {fraction}")
        n = max(0, round(len(table.rows) * fraction))
        return self.sample(table, n)

    def head_sample(self, table: ScrapedTable, n: int) -> ScrapedTable:
        """Return the first *n* rows deterministically (no randomness)."""
        if n < 0:
            raise SampleError(f"Sample size must be non-negative, got {n}")
        return ScrapedTable(headers=table.headers, rows=table.rows[:n])

    def stratified_sample(
        self, table: ScrapedTable, column: str, n_per_group: int
    ) -> ScrapedTable:
        """Return up to *n_per_group* rows per unique value in *column*."""
        if table.headers is None:
            raise SampleError("stratified_sample requires a table with headers")
        if column not in table.headers:
            raise SampleError(f"Column '{column}' not found in headers")
        col_idx = table.headers.index(column)
        groups: dict[str, list[list[str]]] = {}
        for row in table.rows:
            key = row[col_idx] if col_idx < len(row) else ""
            groups.setdefault(key, []).append(row)
        sampled_rows: list[list[str]] = []
        for rows in groups.values():
            take = min(n_per_group, len(rows))
            sampled_rows.extend(self._rng.sample(rows, take))
        return ScrapedTable(headers=table.headers, rows=sampled_rows)

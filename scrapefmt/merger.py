from typing import List, Optional
from scrapefmt.models import ScrapedTable


class TableMerger:
    """Combines multiple ScrapedTable instances into one."""

    def __init__(self):
        pass

    def stack(self, tables: List[ScrapedTable]) -> ScrapedTable:
        """Stack tables vertically, keeping headers from the first table."""
        if not tables:
            raise ValueError("Cannot stack an empty list of tables.")

        headers = tables[0].headers
        combined_rows: List[List[str]] = []
        for table in tables:
            combined_rows.extend(table.rows)

        return ScrapedTable(headers=headers, rows=combined_rows)

    def concat(self, tables: List[ScrapedTable]) -> ScrapedTable:
        """Concatenate tables horizontally (column-wise). Rows are zipped."""
        if not tables:
            raise ValueError("Cannot concat an empty list of tables.")

        merged_headers: Optional[List[str]] = None
        has_headers = any(t.headers for t in tables)
        if has_headers:
            merged_headers = []
            for t in tables:
                merged_headers.extend(t.headers or [])

        num_rows = max(len(t.rows) for t in tables)
        merged_rows: List[List[str]] = []
        for i in range(num_rows):
            row: List[str] = []
            for t in tables:
                row.extend(t.rows[i] if i < len(t.rows) else [""] * (t.num_columns or 0))
            merged_rows.append(row)

        return ScrapedTable(headers=merged_headers, rows=merged_rows)

    def join(
        self,
        left: ScrapedTable,
        right: ScrapedTable,
        left_on: str,
        right_on: str,
    ) -> ScrapedTable:
        """Inner join two tables on specified column names."""
        if not left.headers or not right.headers:
            raise ValueError("Both tables must have headers to perform a join.")
        if left_on not in left.headers:
            raise KeyError(f"Column '{left_on}' not found in left table.")
        if right_on not in right.headers:
            raise KeyError(f"Column '{right_on}' not found in right table.")

        left_idx = left.headers.index(left_on)
        right_idx = right.headers.index(right_on)

        right_lookup: dict = {}
        for row in right.rows:
            key = row[right_idx]
            right_lookup.setdefault(key, []).append(row)

        extra_headers = [h for h in right.headers if h != right_on]
        merged_headers = list(left.headers) + extra_headers

        merged_rows: List[List[str]] = []
        for left_row in left.rows:
            key = left_row[left_idx]
            for right_row in right_lookup.get(key, []):
                extra_values = [v for j, v in enumerate(right_row) if j != right_idx]
                merged_rows.append(list(left_row) + extra_values)

        return ScrapedTable(headers=merged_headers, rows=merged_rows)

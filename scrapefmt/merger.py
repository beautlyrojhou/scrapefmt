from typing import List, Optional
from scrapefmt.models import ScrapedTable


class TableMerger:
    """
    Merges multiple ScrapedTable instances into a single ScrapedTable.
    Tables can be stacked vertically (same columns) or joined horizontally.
    """

    def __init__(self, fill_missing: str = ""):
        """
        Args:
            fill_missing: Value to use when a column is missing in one of the tables.
        """
        self.fill_missing = fill_missing

    def stack(self, tables: List[ScrapedTable]) -> ScrapedTable:
        """Stack tables vertically, aligning on headers.

        All tables must have headers. Missing columns are filled with fill_missing.
        """
        if not tables:
            raise ValueError("No tables provided to stack.")

        all_headers: List[str] = []
        for table in tables:
            if table.headers is None:
                raise ValueError("All tables must have headers to stack.")
            for h in table.headers:
                if h not in all_headers:
                    all_headers.append(h)

        merged_rows: List[List[str]] = []
        for table in tables:
            assert table.headers is not None
            for row in table.rows:
                row_dict = dict(zip(table.headers, row))
                merged_rows.append(
                    [row_dict.get(h, self.fill_missing) for h in all_headers]
                )

        return ScrapedTable(headers=all_headers, rows=merged_rows)

    def concat(self, tables: List[ScrapedTable]) -> ScrapedTable:
        """Concatenate tables vertically without header alignment.

        Tables must have the same number of columns.
        Headers are taken from the first table.
        """
        if not tables:
            raise ValueError("No tables provided to concat.")

        num_cols = tables[0].num_columns()
        for i, table in enumerate(tables[1:], start=1):
            if table.num_columns() != num_cols:
                raise ValueError(
                    f"Table at index {i} has {table.num_columns()} columns, "
                    f"expected {num_cols}."
                )

        merged_rows: List[List[str]] = []
        for table in tables:
            merged_rows.extend(table.rows)

        return ScrapedTable(headers=tables[0].headers, rows=merged_rows)

    def join(self, left: ScrapedTable, right: ScrapedTable, fill_missing: Optional[str] = None) -> ScrapedTable:
        """Join two tables horizontally (side by side), row by row.

        Rows are matched by index. Shorter table is padded with fill_missing.
        """
        filler = fill_missing if fill_missing is not None else self.fill_missing
        left_cols = left.num_columns()
        right_cols = right.num_columns()

        headers: Optional[List[str]] = None
        if left.headers is not None and right.headers is not None:
            headers = left.headers + right.headers
        elif left.headers is not None or right.headers is not None:
            raise ValueError("Both tables must have headers, or neither should.")

        max_rows = max(left.num_rows(), right.num_rows())
        merged_rows: List[List[str]] = []
        for i in range(max_rows):
            left_row = left.rows[i] if i < len(left.rows) else [filler] * left_cols
            right_row = right.rows[i] if i < len(right.rows) else [filler] * right_cols
            merged_rows.append(left_row + right_row)

        return ScrapedTable(headers=headers, rows=merged_rows)

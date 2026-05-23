from typing import List, Dict, Any, Tuple
from scrapefmt.models import ScrapedTable


class DiffError(Exception):
    pass


class TableDiffer:
    """Computes differences between two ScrapedTable instances."""

    def __init__(self, left: ScrapedTable, right: ScrapedTable) -> None:
        self.left = left
        self.right = right

    def added_rows(self) -> List[List[str]]:
        """Rows present in right but not in left."""
        left_set = {tuple(row) for row in self.left.rows}
        return [row for row in self.right.rows if tuple(row) not in left_set]

    def removed_rows(self) -> List[List[str]]:
        """Rows present in left but not in right."""
        right_set = {tuple(row) for row in self.right.rows}
        return [row for row in self.left.rows if tuple(row) not in right_set]

    def added_columns(self) -> List[str]:
        """Column headers present in right but not in left."""
        if self.left.headers is None or self.right.headers is None:
            return []
        left_cols = set(self.left.headers)
        return [h for h in self.right.headers if h not in left_cols]

    def removed_columns(self) -> List[str]:
        """Column headers present in left but not in right."""
        if self.left.headers is None or self.right.headers is None:
            return []
        right_cols = set(self.right.headers)
        return [h for h in self.left.headers if h not in right_cols]

    def summary(self) -> Dict[str, Any]:
        """Return a summary dict of all differences."""
        return {
            "added_rows": len(self.added_rows()),
            "removed_rows": len(self.removed_rows()),
            "added_columns": self.added_columns(),
            "removed_columns": self.removed_columns(),
            "left_row_count": self.left.num_rows,
            "right_row_count": self.right.num_rows,
            "headers_match": self.left.headers == self.right.headers,
        }

    def is_equal(self) -> bool:
        """Return True if both tables are structurally and content-equal."""
        return (
            self.left.headers == self.right.headers
            and self.left.rows == self.right.rows
        )

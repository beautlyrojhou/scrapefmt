from typing import List, Optional
from scrapefmt.models import ScrapedTable


class ValidationError(Exception):
    """Raised when a ScrapedTable fails validation."""
    pass


class TableValidator:
    """Validates ScrapedTable instances against configurable rules."""

    def __init__(
        self,
        min_rows: int = 0,
        max_rows: Optional[int] = None,
        min_columns: int = 0,
        max_columns: Optional[int] = None,
        required_headers: Optional[List[str]] = None,
        allow_empty_headers: bool = True,
    ):
        self.min_rows = min_rows
        self.max_rows = max_rows
        self.min_columns = min_columns
        self.max_columns = max_columns
        self.required_headers = required_headers or []
        self.allow_empty_headers = allow_empty_headers

    def validate(self, table: ScrapedTable) -> None:
        """Validate a ScrapedTable, raising ValidationError on failure."""
        errors: List[str] = []

        if table.num_rows < self.min_rows:
            errors.append(
                f"Table has {table.num_rows} rows, expected at least {self.min_rows}."
            )

        if self.max_rows is not None and table.num_rows > self.max_rows:
            errors.append(
                f"Table has {table.num_rows} rows, expected at most {self.max_rows}."
            )

        if table.num_columns < self.min_columns:
            errors.append(
                f"Table has {table.num_columns} columns, expected at least {self.min_columns}."
            )

        if self.max_columns is not None and table.num_columns > self.max_columns:
            errors.append(
                f"Table has {table.num_columns} columns, expected at most {self.max_columns}."
            )

        if not self.allow_empty_headers and table.headers is not None:
            empty = [h for h in table.headers if not h or not h.strip()]
            if empty:
                errors.append(
                    f"Table contains {len(empty)} empty header(s)."
                )

        if self.required_headers:
            present = set(table.headers or [])
            missing = [h for h in self.required_headers if h not in present]
            if missing:
                errors.append(
                    f"Table is missing required headers: {missing}."
                )

        if errors:
            raise ValidationError(" ".join(errors))

    def is_valid(self, table: ScrapedTable) -> bool:
        """Return True if the table passes all validation rules."""
        try:
            self.validate(table)
            return True
        except ValidationError:
            return False

    def get_errors(self, table: ScrapedTable) -> List[str]:
        """Return a list of validation error messages for the given table.

        Unlike ``validate``, this method does not raise an exception.
        Returns an empty list if the table is valid.
        """
        try:
            self.validate(table)
            return []
        except ValidationError as exc:
            # Re-parse individual messages split by the single-space join
            # used in validate(), preserving the original sentence boundaries.
            return [msg.strip() for msg in str(exc).split(".") if msg.strip()]

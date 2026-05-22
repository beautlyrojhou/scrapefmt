"""Data models for scraped table structures."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ScrapedTable:
    """Represents a scraped HTML table with headers and rows."""

    headers: List[str] = field(default_factory=list)
    rows: List[List[str]] = field(default_factory=list)
    caption: Optional[str] = None
    source_url: Optional[str] = None

    @property
    def num_rows(self) -> int:
        """Return the number of data rows."""
        return len(self.rows)

    @property
    def num_columns(self) -> int:
        """Return the number of columns based on headers."""
        return len(self.headers)

    def to_dict_list(self) -> List[dict]:
        """Convert rows to a list of dicts keyed by header names."""
        if not self.headers:
            return [{str(i): val for i, val in enumerate(row)} for row in self.rows]
        return [
            {header: (row[i] if i < len(row) else "") for i, header in enumerate(self.headers)}
            for row in self.rows
        ]

    def __repr__(self) -> str:
        return (
            f"ScrapedTable(headers={self.headers!r}, "
            f"num_rows={self.num_rows}, source_url={self.source_url!r})"
        )

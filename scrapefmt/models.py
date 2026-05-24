from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScrapedTable:
    """Represents a scraped HTML table with optional headers and row data."""

    headers: List[str] = field(default_factory=list)
    rows: List[List[str]] = field(default_factory=list)

    @property
    def num_rows(self) -> int:
        return len(self.rows)

    @property
    def num_columns(self) -> int:
        if self.headers:
            return len(self.headers)
        return len(self.rows[0]) if self.rows else 0

    def to_dict_list(self) -> List[Dict[str, str]]:
        if not self.headers:
            return []
        return [dict(zip(self.headers, row)) for row in self.rows]

    def __repr__(self) -> str:
        return (
            f"ScrapedTable(headers={self.headers!r}, "
            f"num_rows={self.num_rows}, num_columns={self.num_columns})"
        )

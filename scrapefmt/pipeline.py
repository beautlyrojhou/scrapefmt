"""Pipeline for chaining scraping, filtering, and exporting operations."""

from typing import List, Optional
from scrapefmt.models import ScrapedTable
from scrapefmt.filters import TableFilter
from scrapefmt.format_registry import FormatRegistry


class ScrapePipeline:
    """Fluent pipeline for scraping, filtering, and exporting table data."""

    def __init__(self, table: ScrapedTable, registry: Optional[FormatRegistry] = None):
        self._table = table
        self._registry = registry or FormatRegistry()

    @classmethod
    def from_html(cls, html: str, table_index: int = 0, **kwargs) -> "ScrapePipeline":
        """Create a pipeline by scraping a table from an HTML string."""
        from scrapefmt.scraper import TableScraper

        scraper = TableScraper(**kwargs)
        tables = scraper.scrape_html(html)
        if not tables:
            raise ValueError("No tables found in the provided HTML.")
        if table_index >= len(tables):
            raise IndexError(
                f"table_index {table_index} out of range; found {len(tables)} table(s)."
            )
        return cls(tables[table_index])

    def exclude_empty_rows(self) -> "ScrapePipeline":
        """Remove entirely empty rows from the table."""
        self._table = TableFilter(self._table).exclude_empty_rows()
        return self

    def filter_columns(self, columns: List[str]) -> "ScrapePipeline":
        """Keep only the specified columns."""
        self._table = TableFilter(self._table).filter_columns(columns)
        return self

    def where(self, column: str, value: str, case_sensitive: bool = True) -> "ScrapePipeline":
        """Filter rows where a column equals a value."""
        self._table = TableFilter(self._table).where_column_equals(
            column, value, case_sensitive=case_sensitive
        )
        return self

    def export(self, fmt: str, **kwargs) -> str:
        """Export the table to the given format string (e.g. 'csv', 'json', 'markdown')."""
        exporter_cls = self._registry.get(fmt)
        exporter = exporter_cls(**kwargs)
        return exporter.export(self._table)

    @property
    def table(self) -> ScrapedTable:
        """Access the current ScrapedTable in the pipeline."""
        return self._table

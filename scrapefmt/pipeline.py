"""Fluent pipeline for scraping, filtering, transforming, and exporting tables."""

from typing import Callable, Dict, List, Optional
from scrapefmt.models import ScrapedTable
from scrapefmt.scraper import TableScraper
from scrapefmt.filters import TableFilter
from scrapefmt.transformers import TableTransformer
from scrapefmt.format_registry import FormatRegistry


class ScrapePipeline:
    """Chainable pipeline for table scraping and transformation."""

    def __init__(self, table: ScrapedTable):
        self._table = table
        self._registry = FormatRegistry()

    @classmethod
    def from_html(cls, html: str, table_index: int = 0) -> "ScrapePipeline":
        """Create a pipeline by scraping a table from an HTML string."""
        scraper = TableScraper()
        tables = scraper.scrape_html(html)
        if not tables:
            raise ValueError("No tables found in provided HTML.")
        if table_index >= len(tables):
            raise IndexError(
                f"Table index {table_index} out of range; {len(tables)} table(s) found."
            )
        return cls(tables[table_index])

    def exclude_empty_rows(self) -> "ScrapePipeline":
        """Remove rows where all cells are empty."""
        self._table = TableFilter(self._table).exclude_empty_rows().result()
        return self

    def filter_columns(self, columns: List[str]) -> "ScrapePipeline":
        """Keep only the specified columns (requires headers)."""
        self._table = TableFilter(self._table).filter_columns(columns).result()
        return self

    def filter_rows(self, predicate: Callable[[List[str]], bool]) -> "ScrapePipeline":
        """Keep only rows matching the predicate."""
        self._table = TableFilter(self._table).filter_rows(predicate).result()
        return self

    def rename_columns(self, mapping: Dict[str, str]) -> "ScrapePipeline":
        """Rename columns using a mapping dict."""
        self._table = TableTransformer(self._table).rename_columns(mapping).result()
        return self

    def transform_column(
        self, column: str, fn: Callable[[str], str]
    ) -> "ScrapePipeline":
        """Apply a transformation function to a column."""
        self._table = TableTransformer(self._table).transform_column(column, fn).result()
        return self

    def strip_whitespace(self) -> "ScrapePipeline":
        """Strip whitespace from all cells and headers."""
        self._table = TableTransformer(self._table).strip_whitespace().result()
        return self

    def fill_empty(
        self, value: str = "", column: Optional[str] = None
    ) -> "ScrapePipeline":
        """Fill empty cells with a default value."""
        self._table = TableTransformer(self._table).fill_empty(value, column).result()
        return self

    def export(self, fmt: str, **kwargs) -> str:
        """Export the table using a registered format exporter."""
        exporter_cls = self._registry.get(fmt)
        exporter = exporter_cls(**kwargs)
        return exporter.export(self._table)

    def result(self) -> ScrapedTable:
        """Return the current ScrapedTable from the pipeline."""
        return self._table

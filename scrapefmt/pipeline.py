from typing import List, Optional
from .models import ScrapedTable
from .scraper import TableScraper
from .filters import TableFilter
from .transformers import TableTransformer
from .validators import TableValidator, ValidationError
from .summarizer import TableSummarizer


class ScrapePipeline:
    """Fluent pipeline for scraping, filtering, transforming and exporting tables."""

    def __init__(self, table: ScrapedTable) -> None:
        self._table = table

    @classmethod
    def from_html(cls, html: str, table_index: int = 0) -> "ScrapePipeline":
        scraper = TableScraper()
        tables = scraper.scrape_html(html)
        if not tables:
            raise ValueError("No tables found in the provided HTML.")
        if table_index >= len(tables):
            raise IndexError(
                f"Table index {table_index} out of range; "
                f"only {len(tables)} table(s) found."
            )
        return cls(tables[table_index])

    def exclude_empty_rows(self) -> "ScrapePipeline":
        f = TableFilter(self._table)
        self._table = f.exclude_empty_rows()
        return self

    def filter_columns(self, columns: List[str]) -> "ScrapePipeline":
        f = TableFilter(self._table)
        self._table = f.filter_columns(columns)
        return self

    def filter_rows(self, predicate) -> "ScrapePipeline":
        f = TableFilter(self._table)
        self._table = f.filter_rows(predicate)
        return self

    def rename_columns(self, mapping: dict) -> "ScrapePipeline":
        t = TableTransformer(self._table)
        self._table = t.rename_columns(mapping)
        return self

    def transform_column(self, column: str, func) -> "ScrapePipeline":
        t = TableTransformer(self._table)
        self._table = t.transform_column(column, func)
        return self

    def strip_whitespace(self) -> "ScrapePipeline":
        t = TableTransformer(self._table)
        self._table = t.strip_whitespace()
        return self

    def validate(self, **kwargs) -> "ScrapePipeline":
        v = TableValidator(self._table, **kwargs)
        v.validate()
        return self

    def summarize(self) -> dict:
        """Return a summary of the current table state."""
        return TableSummarizer(self._table).summarize()

    def export(self, fmt: str, **kwargs) -> str:
        from .format_registry import FormatRegistry
        registry = FormatRegistry()
        exporter_cls = registry.get(fmt)
        exporter = exporter_cls(self._table, **kwargs)
        return exporter.export()

    def get_table(self) -> ScrapedTable:
        return self._table

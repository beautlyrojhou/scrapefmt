from __future__ import annotations
from typing import Callable, List, Optional
from scrapefmt.models import ScrapedTable
from scrapefmt.scraper import TableScraper
from scrapefmt.filters import TableFilter
from scrapefmt.transformers import TableTransformer
from scrapefmt.reshaper import TableReshaper


class ScrapePipeline:
    """Fluent pipeline for scraping, transforming, and reshaping tables."""

    def __init__(self, table: ScrapedTable) -> None:
        self._table = table

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_html(cls, html: str, table_index: int = 0) -> "ScrapePipeline":
        scraper = TableScraper()
        tables = scraper.scrape_html(html)
        if not tables:
            raise ValueError("No tables found in the provided HTML")
        if table_index >= len(tables):
            raise IndexError(
                f"table_index {table_index} is out of range ({len(tables)} table(s) found)"
            )
        return cls(tables[table_index])

    # ------------------------------------------------------------------
    # Filter operations
    # ------------------------------------------------------------------

    def exclude_empty_rows(self) -> "ScrapePipeline":
        self._table = TableFilter(self._table).exclude_empty_rows()
        return self

    def filter_columns(self, columns: List[str]) -> "ScrapePipeline":
        self._table = TableFilter(self._table).filter_columns(columns)
        return self

    def filter_rows(self, predicate: Callable[[List[str]], bool]) -> "ScrapePipeline":
        self._table = TableFilter(self._table).filter_rows(predicate)
        return self

    # ------------------------------------------------------------------
    # Transform operations
    # ------------------------------------------------------------------

    def strip_whitespace(self) -> "ScrapePipeline":
        self._table = TableTransformer(self._table).strip_whitespace()
        return self

    def rename_columns(self, mapping: dict) -> "ScrapePipeline":
        self._table = TableTransformer(self._table).rename_columns(mapping)
        return self

    def transform_column(self, column: str, func: Callable[[str], str]) -> "ScrapePipeline":
        self._table = TableTransformer(self._table).transform_column(column, func)
        return self

    # ------------------------------------------------------------------
    # Reshape operations
    # ------------------------------------------------------------------

    def split_column(
        self,
        column: str,
        separator: str,
        new_columns: List[str],
        drop_original: bool = True,
    ) -> "ScrapePipeline":
        self._table = TableReshaper(self._table).split_column(
            column, separator, new_columns, drop_original
        )
        return self

    def melt(
        self,
        id_columns: List[str],
        value_name: str = "value",
        variable_name: str = "variable",
    ) -> "ScrapePipeline":
        self._table = TableReshaper(self._table).melt(id_columns, value_name, variable_name)
        return self

    def fill_down(self, column: Optional[str] = None) -> "ScrapePipeline":
        self._table = TableReshaper(self._table).fill_down(column)
        return self

    # ------------------------------------------------------------------
    # Terminal operations
    # ------------------------------------------------------------------

    def build(self) -> ScrapedTable:
        return self._table

    def to_dict_list(self) -> list:
        return self._table.to_dict_list()

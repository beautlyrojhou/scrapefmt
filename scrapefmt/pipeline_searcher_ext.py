from typing import List, Callable
from scrapefmt.searcher import TableSearcher
from scrapefmt.models import ScrapedTable


class SearcherMixin:
    """Mixin that adds search capabilities to ScrapePipeline."""

    def find_rows(self, predicate: Callable[[List[str]], bool]) -> List[List[str]]:
        """Return data rows matching the predicate without modifying the pipeline."""
        return TableSearcher(self._table).find_rows(predicate)

    def find_rows_containing(self, value: str, case_sensitive: bool = False) -> List[List[str]]:
        """Return data rows containing the given value in any cell."""
        return TableSearcher(self._table).find_rows_containing(value, case_sensitive=case_sensitive)

    def find_in_column(self, column: str, value: str, case_sensitive: bool = False) -> List[List[str]]:
        """Return rows where the specified column contains the given value."""
        return TableSearcher(self._table).find_in_column(column, value, case_sensitive=case_sensitive)

    def find_cells(self, predicate: Callable[[str], bool]) -> List[tuple]:
        """Return (row_index, col_index, value) tuples for matching cells."""
        return TableSearcher(self._table).find_cells(predicate)

    def count_occurrences(self, value: str, case_sensitive: bool = False) -> int:
        """Count total occurrences of a value across all data cells."""
        return TableSearcher(self._table).count_occurrences(value, case_sensitive=case_sensitive)

    def filter_to_matches(self, column: str, value: str, case_sensitive: bool = False) -> "SearcherMixin":
        """Filter the pipeline in-place to rows matching the column search, returns self."""
        from scrapefmt.models import ScrapedTable
        matched = self.find_in_column(column, value, case_sensitive=case_sensitive)
        self._table = ScrapedTable(headers=self._table.headers, rows=matched)
        return self


try:
    from scrapefmt.pipeline import ScrapePipeline

    class ScrapePipeline(SearcherMixin, ScrapePipeline):  # type: ignore
        pass
except ImportError:
    pass

from __future__ import annotations
from typing import Callable, List
from scrapefmt.pipeline import ScrapePipeline
from scrapefmt.splitter import TableSplitter
from scrapefmt.models import ScrapedTable


class SplitterMixin:
    """Mixin that adds split operations to ScrapePipeline."""

    def split_by_size(self, chunk_size: int) -> List["ScrapePipeline"]:
        """Return a list of new pipelines, each wrapping a chunk of rows."""
        splitter = TableSplitter(self._table)  # type: ignore[attr-defined]
        chunks = splitter.split_by_size(chunk_size)
        return [ScrapePipeline._from_table(chunk) for chunk in chunks]

    def split_by_predicate(
        self, predicate: Callable[[List[str]], bool]
    ) -> tuple:
        """Return two new pipelines split by predicate."""
        splitter = TableSplitter(self._table)  # type: ignore[attr-defined]
        matched, unmatched = splitter.split_by_predicate(predicate)
        return (
            ScrapePipeline._from_table(matched),
            ScrapePipeline._from_table(unmatched),
        )

    def split_at_row(self, index: int) -> tuple:
        """Return two new pipelines split at the given row index."""
        splitter = TableSplitter(self._table)  # type: ignore[attr-defined]
        top, bottom = splitter.split_at_row(index)
        return (
            ScrapePipeline._from_table(top),
            ScrapePipeline._from_table(bottom),
        )


# Patch the mixin methods onto ScrapePipeline
ScrapePipeline.split_by_size = SplitterMixin.split_by_size  # type: ignore
ScrapePipeline.split_by_predicate = SplitterMixin.split_by_predicate  # type: ignore
ScrapePipeline.split_at_row = SplitterMixin.split_at_row  # type: ignore

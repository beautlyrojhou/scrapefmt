"""Extension mixin that adds encoder-based export methods to ScrapePipeline.

Usage (applied inside pipeline.py or via direct import)::

    from scrapefmt.pipeline_encoder_ext import EncoderMixin
    class ScrapePipeline(EncoderMixin, ...):
        ...
"""
from typing import Any, Dict, List
from scrapefmt.encoder import TableEncoder, EncodeError


class EncoderMixin:
    """Mixin providing encode_* convenience methods for a pipeline that
    exposes a ``_table`` attribute of type :class:`~scrapefmt.models.ScrapedTable`.
    """

    def encode_records(self) -> List[Dict[str, Any]]:
        """Return the current table as a list of dicts keyed by header name."""
        return TableEncoder(self._table).to_records()  # type: ignore[attr-defined]

    def encode_matrix(self) -> List[List[Any]]:
        """Return the current table as a 2-D list (headers first if present)."""
        return TableEncoder(self._table).to_matrix()  # type: ignore[attr-defined]

    def encode_column_map(self) -> Dict[str, List[Any]]:
        """Return the current table as a column-keyed dict.

        Raises :class:`~scrapefmt.encoder.EncodeError` when the table has no
        headers.
        """
        return TableEncoder(self._table).to_column_map()  # type: ignore[attr-defined]

    def encode_indexed(self, start: int = 0) -> Dict[int, Dict[str, Any]]:
        """Return the current table as a row-index-keyed dict."""
        return TableEncoder(self._table).to_indexed(start=start)  # type: ignore[attr-defined]

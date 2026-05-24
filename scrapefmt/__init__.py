"""scrapefmt — scrape structured data from HTML tables and export to multiple formats."""

from scrapefmt.models import ScrapedTable
from scrapefmt.scraper import TableScraper
from scrapefmt.exporters import CSVExporter, JSONExporter, MarkdownExporter
from scrapefmt.format_registry import FormatRegistry
from scrapefmt.filters import TableFilter
from scrapefmt.pipeline import ScrapePipeline
from scrapefmt.validators import TableValidator, ValidationError
from scrapefmt.transformers import TableTransformer
from scrapefmt.summarizer import TableSummarizer
from scrapefmt.merger import TableMerger
from scrapefmt.sorter import TableSorter
from scrapefmt.deduplicator import TableDeduplicator
from scrapefmt.cleaner import TableCleaner
from scrapefmt.paginator import TablePaginator
from scrapefmt.caster import TableCaster, CastError
from scrapefmt.flattener import TableFlattener
from scrapefmt.slicer import TableSlicer
from scrapefmt.grouper import TableGrouper
from scrapefmt.renamer import TableRenamer, RenameError
from scrapefmt.pivotter import TablePivotter, PivotError
from scrapefmt.differ import TableDiffer, DiffError
from scrapefmt.sampler import TableSampler, SampleError
from scrapefmt.aggregator import TableAggregator, AggregateError

__all__ = [
    "ScrapedTable",
    "TableScraper",
    "CSVExporter",
    "JSONExporter",
    "MarkdownExporter",
    "FormatRegistry",
    "TableFilter",
    "ScrapePipeline",
    "TableValidator",
    "ValidationError",
    "TableTransformer",
    "TableSummarizer",
    "TableMerger",
    "TableSorter",
    "TableDeduplicator",
    "TableCleaner",
    "TablePaginator",
    "TableCaster",
    "CastError",
    "TableFlattener",
    "TableSlicer",
    "TableGrouper",
    "TableRenamer",
    "RenameError",
    "TablePivotter",
    "PivotError",
    "TableDiffer",
    "DiffError",
    "TableSampler",
    "SampleError",
    "TableAggregator",
    "AggregateError",
]

__version__ = "0.1.0"

"""scrapefmt — scrape structured data from HTML tables and export to multiple formats."""

from scrapefmt.models import ScrapedTable
from scrapefmt.scraper import TableScraper
from scrapefmt.exporters import CSVExporter, JSONExporter
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

__all__ = [
    "ScrapedTable",
    "TableScraper",
    "CSVExporter",
    "JSONExporter",
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
]

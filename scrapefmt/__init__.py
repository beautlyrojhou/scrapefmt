"""scrapefmt — scrape structured data from HTML tables and export to multiple formats.

Public API
----------
ScrapedTable      : Data model representing a scraped HTML table.
TableScraper      : Fetches and parses HTML tables from a URL or raw HTML.
CSVExporter       : Exports a ScrapedTable to CSV format.
JSONExporter      : Exports a ScrapedTable to JSON format.
MarkdownExporter  : Exports a ScrapedTable to Markdown format.
FormatRegistry    : Registry for looking up exporters by format name.
TableFilter       : Filters rows/columns of a ScrapedTable.
ScrapePipeline    : Chains multiple scraping and transformation steps.
TableValidator    : Validates table structure and cell values.
ValidationError   : Raised when table validation fails.
TableTransformer  : Applies arbitrary transformations to a ScrapedTable.
TableSummarizer   : Computes summary statistics over table columns.
TableMerger       : Merges two or more ScrapedTables together.
TableSorter       : Sorts rows of a ScrapedTable by one or more columns.
TableDeduplicator : Removes duplicate rows from a ScrapedTable.
TableCleaner      : Strips and normalises cell values in a ScrapedTable.
TablePaginator    : Splits a ScrapedTable into fixed-size pages.
TableCaster       : Casts column values to specified Python types.
CastError         : Raised when a type cast fails.
TableFlattener    : Flattens nested/multi-level headers into a single row.
TableSlicer       : Extracts a row/column slice from a ScrapedTable.
TableGrouper      : Groups rows of a ScrapedTable by a key column.
"""

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
]

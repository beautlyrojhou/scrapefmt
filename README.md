# scrapefmt

A Python library for scraping structured data from HTML tables and exporting to multiple formats.

## Features

- **Scraping**: Parse HTML tables from strings or URLs into `ScrapedTable` objects
- **Exporting**: Export to CSV, JSON, and Markdown
- **Filtering**: Filter rows and columns by predicate or name
- **Transforming**: Rename columns, apply transformations, strip whitespace
- **Validating**: Validate tables against configurable rules
- **Merging**: Stack or concatenate multiple tables
- **Sorting**: Sort rows by column value (string or numeric)
- **Deduplicating**: Remove exact or column-scoped duplicate rows
- **Cleaning**: Normalize whitespace and clean cell values
- **Paginating**: Generate paginated scrape URLs
- **Casting**: Cast column values to int, float, or bool
- **Flattening**: Flatten table data to lists of values or strings
- **Slicing**: Extract head, tail, or arbitrary row slices
- **Grouping**: Group rows by column value or custom function
- **Renaming**: Rename headers by name or index
- **Pivoting**: Pivot or transpose tables
- **Diffing**: Compare two tables for added/removed rows
- **Sampling**: Randomly sample rows from a table
- **Aggregating**: Compute sum, mean, min, max, and count on numeric columns
- **Pipeline**: Chainable pipeline API for composing operations

## Installation

```bash
pip install scrapefmt
```

## Quick Start

```python
from scrapefmt import TableScraper, CSVExporter, TableAggregator

scraper = TableScraper()
tables = scraper.scrape_url("https://example.com/data")
table = tables[0]

# Export to CSV
exporter = CSVExporter()
csv_output = exporter.export(table)

# Aggregate numeric column
agg = TableAggregator(table)
print(agg.summarize_column("Price"))
```

## Aggregator

```python
from scrapefmt import TableAggregator

agg = TableAggregator(table)
print(agg.sum("Revenue"))        # 12500.0
print(agg.mean("Revenue"))       # 2500.0
print(agg.min("Revenue"))        # 800.0
print(agg.max("Revenue"))        # 4200.0
print(agg.count("Revenue"))      # 5
print(agg.summarize_column("Revenue"))  # {sum, mean, min, max, count}
```

## License

MIT

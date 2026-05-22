"""scrapefmt - Scrape structured data from HTML tables and export to multiple formats."""

from .scraper import TableScraper
from .models import ScrapedTable

__version__ = "0.1.0"
__all__ = ["TableScraper", "ScrapedTable"]

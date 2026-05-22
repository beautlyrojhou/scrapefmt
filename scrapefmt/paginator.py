from typing import List, Optional, Callable
from scrapefmt.models import ScrapedTable
from scrapefmt.scraper import TableScraper


class TablePaginator:
    """Scrapes and aggregates tables across multiple paginated URLs."""

    def __init__(self, scraper: Optional[TableScraper] = None):
        self._scraper = scraper or TableScraper()
        self._pages: List[str] = []

    def add_page(self, url: str) -> "TablePaginator":
        """Register a URL to be scraped."""
        self._pages.append(url)
        return self

    def add_pages(self, urls: List[str]) -> "TablePaginator":
        """Register multiple URLs at once."""
        self._pages.extend(urls)
        return self

    def generate_pages(
        self,
        template: str,
        start: int,
        stop: int,
        step: int = 1,
    ) -> "TablePaginator":
        """Generate paginated URLs from a template with a {page} placeholder."""
        for page in range(start, stop, step):
            self._pages.append(template.format(page=page))
        return self

    def scrape_all(
        self,
        table_index: int = 0,
        on_error: Optional[Callable[[str, Exception], None]] = None,
    ) -> List[ScrapedTable]:
        """Scrape the target table from every registered page URL."""
        results: List[ScrapedTable] = []
        for url in self._pages:
            try:
                tables = self._scraper.scrape_url(url)
                if table_index >= len(tables):
                    raise IndexError(
                        f"Table index {table_index} out of range "
                        f"(found {len(tables)} table(s)) at {url}"
                    )
                results.append(tables[table_index])
            except Exception as exc:  # noqa: BLE001
                if on_error is not None:
                    on_error(url, exc)
                else:
                    raise
        return results

    @property
    def page_count(self) -> int:
        return len(self._pages)

    def __repr__(self) -> str:  # pragma: no cover
        return f"TablePaginator(pages={self.page_count})"

"""Core HTML table scraper using BeautifulSoup."""

from typing import List, Optional

try:
    from bs4 import BeautifulSoup, Tag
except ImportError as exc:
    raise ImportError("beautifulsoup4 is required: pip install beautifulsoup4") from exc

from .models import ScrapedTable


class TableScraper:
    """Scrapes HTML tables from raw HTML strings or URLs."""

    def __init__(self, parser: str = "html.parser"):
        self.parser = parser

    def scrape_html(self, html: str, source_url: Optional[str] = None) -> List[ScrapedTable]:
        """Parse all tables from an HTML string and return a list of ScrapedTable objects."""
        soup = BeautifulSoup(html, self.parser)
        tables = soup.find_all("table")
        return [self._parse_table(table, source_url) for table in tables]

    def scrape_url(self, url: str) -> List[ScrapedTable]:
        """Fetch a URL and scrape all tables from the page."""
        try:
            import urllib.request
            with urllib.request.urlopen(url) as response:
                html = response.read().decode("utf-8", errors="replace")
        except Exception as exc:
            raise RuntimeError(f"Failed to fetch URL '{url}': {exc}") from exc
        return self.scrape_html(html, source_url=url)

    def _parse_table(self, table: "Tag", source_url: Optional[str]) -> ScrapedTable:
        """Extract headers, rows, and caption from a BeautifulSoup table tag."""
        caption_tag = table.find("caption")
        caption = caption_tag.get_text(strip=True) if caption_tag else None

        headers: List[str] = []
        rows: List[List[str]] = []

        thead = table.find("thead")
        if thead:
            header_row = thead.find("tr")
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])]

        if not headers:
            first_row = table.find("tr")
            if first_row:
                ths = first_row.find_all("th")
                if ths:
                    headers = [th.get_text(strip=True) for th in ths]

        tbody = table.find("tbody") or table
        for tr in tbody.find_all("tr"):
            cells = tr.find_all(["td", "th"])
            if not cells:
                continue
            row_data = [cell.get_text(strip=True) for cell in cells]
            if row_data != headers:
                rows.append(row_data)

        return ScrapedTable(headers=headers, rows=rows, caption=caption, source_url=source_url)

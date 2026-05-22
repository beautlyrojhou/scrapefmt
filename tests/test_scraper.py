"""Tests for the TableScraper and ScrapedTable core functionality."""

import pytest
from scrapefmt import TableScraper, ScrapedTable


SIMPLE_TABLE_HTML = """
<html><body>
  <table>
    <caption>Employee Data</caption>
    <thead>
      <tr><th>Name</th><th>Age</th><th>Department</th></tr>
    </thead>
    <tbody>
      <tr><td>Alice</td><td>30</td><td>Engineering</td></tr>
      <tr><td>Bob</td><td>25</td><td>Marketing</td></tr>
    </tbody>
  </table>
</body></html>
"""

MULTI_TABLE_HTML = """
<html><body>
  <table><tr><th>A</th><th>B</th></tr><tr><td>1</td><td>2</td></tr></table>
  <table><tr><th>X</th><th>Y</th></tr><tr><td>9</td><td>8</td></tr></table>
</body></html>
"""

NO_HEADER_HTML = """
<html><body>
  <table>
    <tr><td>foo</td><td>bar</td></tr>
    <tr><td>baz</td><td>qux</td></tr>
  </table>
</body></html>
"""


@pytest.fixture
def scraper():
    return TableScraper()


def test_scrape_single_table(scraper):
    tables = scraper.scrape_html(SIMPLE_TABLE_HTML)
    assert len(tables) == 1
    table = tables[0]
    assert isinstance(table, ScrapedTable)
    assert table.headers == ["Name", "Age", "Department"]
    assert table.num_rows == 2
    assert table.caption == "Employee Data"


def test_scrape_row_values(scraper):
    tables = scraper.scrape_html(SIMPLE_TABLE_HTML)
    table = tables[0]
    assert table.rows[0] == ["Alice", "30", "Engineering"]
    assert table.rows[1] == ["Bob", "25", "Marketing"]


def test_scrape_multiple_tables(scraper):
    tables = scraper.scrape_html(MULTI_TABLE_HTML)
    assert len(tables) == 2
    assert tables[0].headers == ["A", "B"]
    assert tables[1].headers == ["X", "Y"]


def test_to_dict_list(scraper):
    tables = scraper.scrape_html(SIMPLE_TABLE_HTML)
    records = tables[0].to_dict_list()
    assert records[0] == {"Name": "Alice", "Age": "30", "Department": "Engineering"}
    assert records[1] == {"Name": "Bob", "Age": "25", "Department": "Marketing"}


def test_no_header_table(scraper):
    tables = scraper.scrape_html(NO_HEADER_HTML)
    assert len(tables) == 1
    table = tables[0]
    assert table.num_rows == 2


def test_source_url_propagation(scraper):
    tables = scraper.scrape_html(SIMPLE_TABLE_HTML, source_url="https://example.com")
    assert tables[0].source_url == "https://example.com"


def test_empty_html(scraper):
    tables = scraper.scrape_html("<html><body></body></html>")
    assert tables == []


def test_num_columns(scraper):
    tables = scraper.scrape_html(SIMPLE_TABLE_HTML)
    assert tables[0].num_columns == 3

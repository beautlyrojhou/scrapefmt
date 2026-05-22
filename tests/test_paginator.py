import pytest
from unittest.mock import MagicMock, patch
from scrapefmt.paginator import TablePaginator
from scrapefmt.models import ScrapedTable


def _make_table(rows):
    return ScrapedTable(headers=["Name", "Value"], rows=rows)


@pytest.fixture()
def paginator():
    return TablePaginator()


def test_add_page_increments_count(paginator):
    paginator.add_page("http://example.com/1")
    assert paginator.page_count == 1


def test_add_pages_increments_count(paginator):
    paginator.add_pages(["http://example.com/1", "http://example.com/2"])
    assert paginator.page_count == 2


def test_generate_pages_creates_correct_urls(paginator):
    paginator.generate_pages("http://example.com?page={page}", start=1, stop=4)
    assert paginator.page_count == 3


def test_generate_pages_with_step(paginator):
    paginator.generate_pages("http://example.com?p={page}", start=0, stop=10, step=2)
    assert paginator.page_count == 5


def test_scrape_all_aggregates_tables(paginator):
    mock_scraper = MagicMock()
    table_a = _make_table([["Alice", "1"]])
    table_b = _make_table([["Bob", "2"]])
    mock_scraper.scrape_url.side_effect = [[table_a], [table_b]]

    pag = TablePaginator(scraper=mock_scraper)
    pag.add_pages(["http://example.com/1", "http://example.com/2"])
    results = pag.scrape_all(table_index=0)

    assert len(results) == 2
    assert results[0].rows == [["Alice", "1"]]
    assert results[1].rows == [["Bob", "2"]]


def test_scrape_all_bad_index_raises(paginator):
    mock_scraper = MagicMock()
    mock_scraper.scrape_url.return_value = [_make_table([["X", "Y"]])]

    pag = TablePaginator(scraper=mock_scraper)
    pag.add_page("http://example.com/1")

    with pytest.raises(IndexError, match="Table index 5 out of range"):
        pag.scrape_all(table_index=5)


def test_scrape_all_on_error_callback_called(paginator):
    mock_scraper = MagicMock()
    mock_scraper.scrape_url.side_effect = ConnectionError("timeout")

    errors = []
    pag = TablePaginator(scraper=mock_scraper)
    pag.add_page("http://bad.example.com")
    pag.scrape_all(on_error=lambda url, exc: errors.append((url, exc)))

    assert len(errors) == 1
    assert errors[0][0] == "http://bad.example.com"
    assert isinstance(errors[0][1], ConnectionError)


def test_scrape_all_no_on_error_raises(paginator):
    mock_scraper = MagicMock()
    mock_scraper.scrape_url.side_effect = ConnectionError("timeout")

    pag = TablePaginator(scraper=mock_scraper)
    pag.add_page("http://bad.example.com")

    with pytest.raises(ConnectionError):
        pag.scrape_all()


def test_add_page_returns_self_for_chaining(paginator):
    result = paginator.add_page("http://example.com")
    assert result is paginator


def test_add_pages_returns_self_for_chaining(paginator):
    result = paginator.add_pages(["http://example.com"])
    assert result is paginator


def test_generate_pages_returns_self_for_chaining(paginator):
    result = paginator.generate_pages("http://example.com/{page}", 1, 3)
    assert result is paginator

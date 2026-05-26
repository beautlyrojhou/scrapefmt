import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.searcher import TableSearcher, SearchError


@pytest.fixture
def sample_table():
    return ScrapedTable(
        headers=["Name", "Department", "City"],
        rows=[
            ["Alice", "Engineering", "New York"],
            ["Bob", "Marketing", "London"],
            ["Carol", "Engineering", "Berlin"],
            ["Dave", "Marketing", "New York"],
            ["Eve", "Engineering", "London"],
        ],
    )


@pytest.fixture
def table_no_headers():
    return ScrapedTable(
        headers=[],
        rows=[
            ["Alice", "Engineering"],
            ["Bob", "Marketing"],
        ],
    )


def test_find_rows_by_predicate(sample_table):
    searcher = TableSearcher(sample_table)
    results = searcher.find_rows(lambda row: row[1] == "Engineering")
    assert len(results) == 3


def test_find_rows_containing_case_insensitive(sample_table):
    searcher = TableSearcher(sample_table)
    results = searcher.find_rows_containing("london")
    assert len(results) == 2


def test_find_rows_containing_case_sensitive(sample_table):
    searcher = TableSearcher(sample_table)
    results = searcher.find_rows_containing("london", case_sensitive=True)
    assert len(results) == 0
    results_correct = searcher.find_rows_containing("London", case_sensitive=True)
    assert len(results_correct) == 2


def test_find_in_column_returns_matching_rows(sample_table):
    searcher = TableSearcher(sample_table)
    results = searcher.find_in_column("Department", "marketing")
    assert len(results) == 2


def test_find_in_column_unknown_raises(sample_table):
    searcher = TableSearcher(sample_table)
    with pytest.raises(SearchError):
        searcher.find_in_column("NonExistent", "value")


def test_find_in_column_no_headers_raises(table_no_headers):
    searcher = TableSearcher(table_no_headers)
    with pytest.raises(SearchError):
        searcher.find_in_column("Department", "value")


def test_find_cells_returns_tuples(sample_table):
    searcher = TableSearcher(sample_table)
    results = searcher.find_cells(lambda cell: cell == "New York")
    assert len(results) == 2
    for item in results:
        assert len(item) == 3
        assert item[2] == "New York"


def test_count_occurrences_case_insensitive(sample_table):
    searcher = TableSearcher(sample_table)
    count = searcher.count_occurrences("engineering")
    assert count == 3


def test_count_occurrences_case_sensitive(sample_table):
    searcher = TableSearcher(sample_table)
    count = searcher.count_occurrences("engineering", case_sensitive=True)
    assert count == 0


def test_count_occurrences_partial_match(sample_table):
    searcher = TableSearcher(sample_table)
    count = searcher.count_occurrences("New")
    assert count == 2


def test_find_rows_no_match_returns_empty(sample_table):
    searcher = TableSearcher(sample_table)
    results = searcher.find_rows(lambda row: row[0] == "Zara")
    assert results == []

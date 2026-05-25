import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.deduplicator import TableDeduplicator


@pytest.fixture
def sample_table():
    return ScrapedTable(
        headers=["ID", "Name", "City"],
        rows=[
            ["1", "Alice", "NYC"],
            ["2", "Bob", "LA"],
            ["1", "Alice", "NYC"],
            ["3", "Carol", "NYC"],
            ["2", "Bob", "LA"],
        ],
    )


@pytest.fixture
def table_no_headers():
    return ScrapedTable(
        headers=[],
        rows=[["a", "b"], ["c", "d"], ["a", "b"]],
    )


def test_deduplicate_removes_exact_duplicates(sample_table):
    dedup = TableDeduplicator(sample_table)
    result = dedup.deduplicate()
    assert len(result.rows) == 3


def test_deduplicate_preserves_first_occurrence(sample_table):
    dedup = TableDeduplicator(sample_table)
    result = dedup.deduplicate()
    assert result.rows[0] == ["1", "Alice", "NYC"]


def test_deduplicate_preserves_headers(sample_table):
    dedup = TableDeduplicator(sample_table)
    result = dedup.deduplicate()
    assert result.headers == ["ID", "Name", "City"]


def test_deduplicate_no_headers(table_no_headers):
    dedup = TableDeduplicator(table_no_headers)
    result = dedup.deduplicate()
    assert len(result.rows) == 2


def test_deduplicate_by_column(sample_table):
    dedup = TableDeduplicator(sample_table)
    result = dedup.deduplicate_by_column("City")
    cities = [r[2] for r in result.rows]
    assert cities.count("NYC") == 1
    assert cities.count("LA") == 1


def test_deduplicate_by_column_preserves_first_occurrence(sample_table):
    """Deduplicating by City should keep the first row for each city value."""
    dedup = TableDeduplicator(sample_table)
    result = dedup.deduplicate_by_column("City")
    nyc_rows = [r for r in result.rows if r[2] == "NYC"]
    assert nyc_rows[0] == ["1", "Alice", "NYC"]


def test_deduplicate_by_column_unknown_raises(sample_table):
    dedup = TableDeduplicator(sample_table)
    with pytest.raises(KeyError):
        dedup.deduplicate_by_column("Unknown")


def test_deduplicate_by_column_no_headers_raises(table_no_headers):
    dedup = TableDeduplicator(table_no_headers)
    with pytest.raises(ValueError):
        dedup.deduplicate_by_column("ID")


def test_count_duplicates(sample_table):
    dedup = TableDeduplicator(sample_table)
    assert dedup.count_duplicates() == 2


def test_count_duplicates_none():
    unique_table = ScrapedTable(
        headers=["A"], rows=[["x"], ["y"], ["z"]]
    )
    dedup = TableDeduplicator(unique_table)
    assert dedup.count_duplicates() == 0

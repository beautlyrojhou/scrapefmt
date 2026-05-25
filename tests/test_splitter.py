import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.splitter import TableSplitter, SplitError


@pytest.fixture
def sample_table():
    return ScrapedTable(
        headers=["Name", "Dept", "Score"],
        rows=[
            ["Alice", "Engineering", "90"],
            ["Bob", "Marketing", "75"],
            ["Carol", "Engineering", "88"],
            ["Dave", "Marketing", "60"],
            ["Eve", "Engineering", "95"],
        ],
    )


@pytest.fixture
def table_no_headers():
    return ScrapedTable(
        headers=[],
        rows=[["X", "1"], ["Y", "2"], ["Z", "3"]],
    )


def test_split_by_size_correct_chunk_count(sample_table):
    splitter = TableSplitter(sample_table)
    chunks = splitter.split_by_size(2)
    assert len(chunks) == 3


def test_split_by_size_first_chunk_rows(sample_table):
    splitter = TableSplitter(sample_table)
    chunks = splitter.split_by_size(2)
    assert len(chunks[0].rows) == 2


def test_split_by_size_last_chunk_rows(sample_table):
    splitter = TableSplitter(sample_table)
    chunks = splitter.split_by_size(2)
    assert len(chunks[-1].rows) == 1


def test_split_by_size_preserves_headers(sample_table):
    splitter = TableSplitter(sample_table)
    chunks = splitter.split_by_size(3)
    for chunk in chunks:
        assert chunk.headers == sample_table.headers


def test_split_by_size_invalid_raises(sample_table):
    splitter = TableSplitter(sample_table)
    with pytest.raises(SplitError):
        splitter.split_by_size(0)


def test_split_by_predicate_matched_count(sample_table):
    splitter = TableSplitter(sample_table)
    matched, _ = splitter.split_by_predicate(lambda row: row[1] == "Engineering")
    assert len(matched.rows) == 3


def test_split_by_predicate_unmatched_count(sample_table):
    splitter = TableSplitter(sample_table)
    _, unmatched = splitter.split_by_predicate(lambda row: row[1] == "Engineering")
    assert len(unmatched.rows) == 2


def test_split_by_predicate_preserves_headers(sample_table):
    splitter = TableSplitter(sample_table)
    matched, unmatched = splitter.split_by_predicate(lambda row: row[2] > "80")
    assert matched.headers == sample_table.headers
    assert unmatched.headers == sample_table.headers


def test_split_at_row_correct_sizes(sample_table):
    splitter = TableSplitter(sample_table)
    top, bottom = splitter.split_at_row(3)
    assert len(top.rows) == 3
    assert len(bottom.rows) == 2


def test_split_at_row_out_of_range_raises(sample_table):
    splitter = TableSplitter(sample_table)
    with pytest.raises(SplitError):
        splitter.split_at_row(10)


def test_split_at_row_zero_gives_empty_top(sample_table):
    splitter = TableSplitter(sample_table)
    top, bottom = splitter.split_at_row(0)
    assert len(top.rows) == 0
    assert len(bottom.rows) == 5


def test_split_no_headers_preserved(table_no_headers):
    splitter = TableSplitter(table_no_headers)
    chunks = splitter.split_by_size(2)
    for chunk in chunks:
        assert chunk.headers == []

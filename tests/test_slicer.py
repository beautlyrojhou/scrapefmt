import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.slicer import TableSlicer


@pytest.fixture
def sample_table() -> ScrapedTable:
    return ScrapedTable(
        headers=["Name", "Age", "City"],
        rows=[
            ["Alice", "30", "New York"],
            ["Bob", "25", "London"],
            ["Carol", "35", "Paris"],
            ["Dave", "28", "Berlin"],
            ["Eve", "22", "Tokyo"],
        ],
    )


@pytest.fixture
def table_no_headers() -> ScrapedTable:
    return ScrapedTable(
        headers=None,
        rows=[["X", "1"], ["Y", "2"], ["Z", "3"]],
    )


def test_head_returns_correct_number(sample_table):
    slicer = TableSlicer(sample_table)
    result = slicer.head(3)
    assert len(result.rows) == 3
    assert result.rows[0] == ["Alice", "30", "New York"]
    assert result.rows[2] == ["Carol", "35", "Paris"]


def test_tail_returns_correct_number(sample_table):
    slicer = TableSlicer(sample_table)
    result = slicer.tail(2)
    assert len(result.rows) == 2
    assert result.rows[0] == ["Dave", "28", "Berlin"]
    assert result.rows[1] == ["Eve", "22", "Tokyo"]


def test_head_preserves_headers(sample_table):
    slicer = TableSlicer(sample_table)
    result = slicer.head(2)
    assert result.headers == ["Name", "Age", "City"]


def test_tail_zero_returns_empty(sample_table):
    slicer = TableSlicer(sample_table)
    result = slicer.tail(0)
    assert result.rows == []
    assert result.headers == sample_table.headers


def test_head_negative_raises(sample_table):
    slicer = TableSlicer(sample_table)
    with pytest.raises(ValueError, match="non-negative"):
        slicer.head(-1)


def test_slice_rows_with_step(sample_table):
    slicer = TableSlicer(sample_table)
    result = slicer.slice_rows(0, None, 2)
    assert len(result.rows) == 3
    assert result.rows[0] == ["Alice", "30", "New York"]
    assert result.rows[1] == ["Carol", "35", "Paris"]


def test_slice_columns_returns_subset(sample_table):
    slicer = TableSlicer(sample_table)
    result = slicer.slice_columns(0, 2)
    assert result.headers == ["Name", "Age"]
    assert result.rows[0] == ["Alice", "30"]


def test_slice_columns_no_headers(table_no_headers):
    slicer = TableSlicer(table_no_headers)
    result = slicer.slice_columns(1, 2)
    assert result.headers is None
    assert result.rows == [["1"], ["2"], ["3"]]


def test_row_at_valid_index(sample_table):
    slicer = TableSlicer(sample_table)
    assert slicer.row_at(0) == ["Alice", "30", "New York"]
    assert slicer.row_at(-1) == ["Eve", "22", "Tokyo"]


def test_row_at_out_of_range_raises(sample_table):
    slicer = TableSlicer(sample_table)
    with pytest.raises(IndexError, match="out of range"):
        slicer.row_at(100)


def test_column_at_returns_values(sample_table):
    slicer = TableSlicer(sample_table)
    assert slicer.column_at(0) == ["Alice", "Bob", "Carol", "Dave", "Eve"]
    assert slicer.column_at(1) == ["30", "25", "35", "28", "22"]


def test_column_at_out_of_range_raises(sample_table):
    slicer = TableSlicer(sample_table)
    with pytest.raises(IndexError, match="out of range"):
        slicer.column_at(10)

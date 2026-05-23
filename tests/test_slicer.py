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


def test_head_returns_first_n_rows(sample_table):
    slicer = TableSlicer(sample_table)
    result = slicer.head(3)
    assert result.num_rows() == 3
    assert result.rows[0][0] == "Alice"
    assert result.rows[2][0] == "Carol"


def test_head_preserves_headers(sample_table):
    slicer = TableSlicer(sample_table)
    result = slicer.head(2)
    assert result.headers == ["Name", "Age", "City"]


def test_head_negative_raises(sample_table):
    slicer = TableSlicer(sample_table)
    with pytest.raises(ValueError):
        slicer.head(-1)


def test_tail_returns_last_n_rows(sample_table):
    slicer = TableSlicer(sample_table)
    result = slicer.tail(2)
    assert result.num_rows() == 2
    assert result.rows[0][0] == "Dave"
    assert result.rows[1][0] == "Eve"


def test_tail_zero_returns_empty(sample_table):
    slicer = TableSlicer(sample_table)
    result = slicer.tail(0)
    assert result.num_rows() == 0
    assert result.headers == sample_table.headers


def test_slice_rows_with_step(sample_table):
    slicer = TableSlicer(sample_table)
    result = slicer.slice_rows(0, 5, 2)
    assert result.num_rows() == 3
    assert result.rows[0][0] == "Alice"
    assert result.rows[1][0] == "Carol"
    assert result.rows[2][0] == "Eve"


def test_slice_columns_by_indices(sample_table):
    slicer = TableSlicer(sample_table)
    result = slicer.slice_columns([0, 2])
    assert result.headers == ["Name", "City"]
    assert result.rows[0] == ["Alice", "New York"]


def test_slice_columns_no_headers(table_no_headers):
    slicer = TableSlicer(table_no_headers)
    result = slicer.slice_columns([1])
    assert result.headers is None
    assert result.rows == [["1"], ["2"], ["3"]]


def test_slice_columns_out_of_range_raises(sample_table):
    slicer = TableSlicer(sample_table)
    with pytest.raises(IndexError):
        slicer.slice_columns([0, 10])


def test_column_range_returns_subset(sample_table):
    slicer = TableSlicer(sample_table)
    result = slicer.column_range(1, 3)
    assert result.headers == ["Age", "City"]
    assert result.num_columns() == 2


def test_column_range_no_stop_goes_to_end(sample_table):
    slicer = TableSlicer(sample_table)
    result = slicer.column_range(1)
    assert result.headers == ["Age", "City"]

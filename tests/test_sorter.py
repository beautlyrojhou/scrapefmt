import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.sorter import TableSorter


@pytest.fixture
def sample_table():
    return ScrapedTable(
        headers=["Name", "Age", "Score"],
        rows=[
            ["Charlie", "30", "88.5"],
            ["Alice", "25", "95.0"],
            ["Bob", "35", "72.3"],
        ],
    )


@pytest.fixture
def table_no_headers():
    return ScrapedTable(
        headers=[],
        rows=[["Z", "1"], ["A", "3"], ["M", "2"]],
    )


def test_sort_by_column_ascending(sample_table):
    sorter = TableSorter(sample_table)
    result = sorter.sort_by_column("Name")
    assert [r[0] for r in result.rows] == ["Alice", "Bob", "Charlie"]


def test_sort_by_column_descending(sample_table):
    sorter = TableSorter(sample_table)
    result = sorter.sort_by_column("Name", reverse=True)
    assert [r[0] for r in result.rows] == ["Charlie", "Bob", "Alice"]


def test_sort_by_column_unknown_raises(sample_table):
    sorter = TableSorter(sample_table)
    with pytest.raises(KeyError):
        sorter.sort_by_column("Unknown")


def test_sort_by_column_no_headers_raises(table_no_headers):
    sorter = TableSorter(table_no_headers)
    with pytest.raises(ValueError):
        sorter.sort_by_column("Name")


def test_sort_by_index(table_no_headers):
    sorter = TableSorter(table_no_headers)
    result = sorter.sort_by_index(0)
    assert [r[0] for r in result.rows] == ["A", "M", "Z"]


def test_sort_by_index_out_of_range(sample_table):
    sorter = TableSorter(sample_table)
    with pytest.raises(IndexError):
        sorter.sort_by_index(10)


def test_sort_numeric(sample_table):
    sorter = TableSorter(sample_table)
    result = sorter.sort_numeric("Score")
    assert [r[2] for r in result.rows] == ["72.3", "88.5", "95.0"]


def test_sort_numeric_descending(sample_table):
    sorter = TableSorter(sample_table)
    result = sorter.sort_numeric("Age", reverse=True)
    assert [r[1] for r in result.rows] == ["35", "30", "25"]


def test_sort_preserves_original(sample_table):
    sorter = TableSorter(sample_table)
    sorter.sort_by_column("Name")
    assert sample_table.rows[0][0] == "Charlie"


def test_sort_empty_table():
    empty = ScrapedTable(headers=["A", "B"], rows=[])
    sorter = TableSorter(empty)
    result = sorter.sort_by_column("A")
    assert result.rows == []

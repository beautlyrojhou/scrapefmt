import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.merger import TableMerger


@pytest.fixture
def merger():
    return TableMerger()


@pytest.fixture
def table_a():
    return ScrapedTable(
        headers=["Name", "Age"],
        rows=[["Alice", "30"], ["Bob", "25"]],
    )


@pytest.fixture
def table_b():
    return ScrapedTable(
        headers=["Name", "City"],
        rows=[["Charlie", "NYC"], ["Diana", "LA"]],
    )


@pytest.fixture
def table_no_headers():
    return ScrapedTable(
        headers=None,
        rows=[["X", "1"], ["Y", "2"]],
    )


def test_stack_merges_rows(merger, table_a, table_b):
    result = merger.stack([table_a, table_b])
    assert result.num_rows() == 4


def test_stack_union_of_headers(merger, table_a, table_b):
    result = merger.stack([table_a, table_b])
    assert result.headers == ["Name", "Age", "City"]


def test_stack_fills_missing_values(merger, table_a, table_b):
    result = merger.stack([table_a, table_b])
    # table_b rows should have empty Age
    assert result.rows[2] == ["Charlie", "", "NYC"]
    assert result.rows[3] == ["Diana", "", "LA"]


def test_stack_custom_fill_missing():
    merger = TableMerger(fill_missing="N/A")
    t1 = ScrapedTable(headers=["A"], rows=[["1"]])
    t2 = ScrapedTable(headers=["B"], rows=[["2"]])
    result = merger.stack([t1, t2])
    assert result.rows[0] == ["1", "N/A"]
    assert result.rows[1] == ["N/A", "2"]


def test_stack_raises_on_empty_list(merger):
    with pytest.raises(ValueError, match="No tables"):
        merger.stack([])


def test_stack_raises_without_headers(merger, table_no_headers):
    with pytest.raises(ValueError, match="headers"):
        merger.stack([table_no_headers])


def test_concat_combines_rows(merger, table_a):
    result = merger.concat([table_a, table_a])
    assert result.num_rows() == 4
    assert result.headers == ["Name", "Age"]


def test_concat_raises_on_column_mismatch(merger):
    t1 = ScrapedTable(headers=["A", "B"], rows=[["1", "2"]])
    t2 = ScrapedTable(headers=["A"], rows=[["3"]])
    with pytest.raises(ValueError, match="columns"):
        merger.concat([t1, t2])


def test_concat_raises_on_empty_list(merger):
    with pytest.raises(ValueError, match="No tables"):
        merger.concat([])


def test_join_combines_columns(merger, table_a, table_b):
    result = merger.join(table_a, table_b)
    assert result.num_columns() == 4
    assert result.headers == ["Name", "Age", "Name", "City"]


def test_join_pads_shorter_table(merger):
    t1 = ScrapedTable(headers=["A"], rows=[["1"], ["2"], ["3"]])
    t2 = ScrapedTable(headers=["B"], rows=[["X"]])
    result = merger.join(t1, t2)
    assert result.num_rows() == 3
    assert result.rows[1] == ["2", ""]
    assert result.rows[2] == ["3", ""]


def test_join_raises_on_mixed_headers(merger, table_a, table_no_headers):
    with pytest.raises(ValueError, match="headers"):
        merger.join(table_a, table_no_headers)


def test_join_no_headers(merger):
    t1 = ScrapedTable(headers=None, rows=[["1", "2"]])
    t2 = ScrapedTable(headers=None, rows=[["3", "4"]])
    result = merger.join(t1, t2)
    assert result.headers is None
    assert result.rows[0] == ["1", "2", "3", "4"]

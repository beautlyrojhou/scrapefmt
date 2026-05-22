import pytest
from scrapefmt.merger import TableMerger
from scrapefmt.models import ScrapedTable


@pytest.fixture()
def merger():
    return TableMerger()


@pytest.fixture()
def table_a():
    return ScrapedTable(
        headers=["Name", "Age"],
        rows=[["Alice", "30"], ["Bob", "25"]],
    )


@pytest.fixture()
def table_b():
    return ScrapedTable(
        headers=["Name", "Age"],
        rows=[["Carol", "28"], ["Dave", "35"]],
    )


@pytest.fixture()
def table_no_headers():
    return ScrapedTable(headers=None, rows=[["X", "1"], ["Y", "2"]])


def test_stack_merges_rows(merger, table_a, table_b):
    result = merger.stack([table_a, table_b])
    assert len(result.rows) == 4


def test_stack_keeps_first_headers(merger, table_a, table_b):
    result = merger.stack([table_a, table_b])
    assert result.headers == ["Name", "Age"]


def test_stack_empty_list_raises(merger):
    with pytest.raises(ValueError, match="empty list"):
        merger.stack([])


def test_stack_single_table(merger, table_a):
    result = merger.stack([table_a])
    assert result.rows == table_a.rows


def test_concat_merges_columns(merger, table_a):
    extra = ScrapedTable(headers=["City"], rows=[["NY"], ["LA"]])
    result = merger.concat([table_a, extra])
    assert result.headers == ["Name", "Age", "City"]
    assert result.rows[0] == ["Alice", "30", "NY"]


def test_concat_empty_list_raises(merger):
    with pytest.raises(ValueError, match="empty list"):
        merger.concat([])


def test_concat_pads_shorter_table(merger):
    t1 = ScrapedTable(headers=["A"], rows=[["1"], ["2"], ["3"]])
    t2 = ScrapedTable(headers=["B"], rows=[["x"]])
    result = merger.concat([t1, t2])
    assert len(result.rows) == 3
    assert result.rows[1] == ["2", ""]


def test_join_inner_join(merger):
    left = ScrapedTable(headers=["id", "name"], rows=[["1", "Alice"], ["2", "Bob"], ["3", "Carol"]])
    right = ScrapedTable(headers=["id", "score"], rows=[["1", "90"], ["3", "85"]])
    result = merger.join(left, right, left_on="id", right_on="id")
    assert result.headers == ["id", "name", "score"]
    assert len(result.rows) == 2
    assert ["1", "Alice", "90"] in result.rows
    assert ["3", "Carol", "85"] in result.rows


def test_join_missing_left_column_raises(merger):
    left = ScrapedTable(headers=["id"], rows=[["1"]])
    right = ScrapedTable(headers=["id"], rows=[["1"]])
    with pytest.raises(KeyError, match="bad_col"):
        merger.join(left, right, left_on="bad_col", right_on="id")


def test_join_missing_right_column_raises(merger):
    left = ScrapedTable(headers=["id"], rows=[["1"]])
    right = ScrapedTable(headers=["id"], rows=[["1"]])
    with pytest.raises(KeyError, match="bad_col"):
        merger.join(left, right, left_on="id", right_on="bad_col")


def test_join_no_headers_raises(merger, table_no_headers):
    with pytest.raises(ValueError, match="headers"):
        merger.join(table_no_headers, table_no_headers, left_on="A", right_on="A")


def test_join_no_matching_rows_returns_empty(merger):
    left = ScrapedTable(headers=["id", "val"], rows=[["1", "a"]])
    right = ScrapedTable(headers=["id", "val"], rows=[["99", "z"]])
    result = merger.join(left, right, left_on="id", right_on="id")
    assert result.rows == []

import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.differ import TableDiffer, DiffError


@pytest.fixture
def table_a() -> ScrapedTable:
    return ScrapedTable(
        headers=["Name", "Dept", "Score"],
        rows=[
            ["Alice", "Eng", "90"],
            ["Bob", "HR", "80"],
            ["Carol", "Eng", "95"],
        ],
    )


@pytest.fixture
def table_b() -> ScrapedTable:
    return ScrapedTable(
        headers=["Name", "Dept", "Score"],
        rows=[
            ["Alice", "Eng", "90"],
            ["Carol", "Eng", "95"],
            ["Dave", "Mktg", "70"],
        ],
    )


@pytest.fixture
def table_no_headers() -> ScrapedTable:
    return ScrapedTable(
        headers=None,
        rows=[["X", "1"], ["Y", "2"]],
    )


def test_added_rows(table_a, table_b):
    differ = TableDiffer(table_a, table_b)
    added = differ.added_rows()
    assert ["Dave", "Mktg", "70"] in added
    assert len(added) == 1


def test_removed_rows(table_a, table_b):
    differ = TableDiffer(table_a, table_b)
    removed = differ.removed_rows()
    assert ["Bob", "HR", "80"] in removed
    assert len(removed) == 1


def test_no_added_rows_when_equal(table_a):
    differ = TableDiffer(table_a, table_a)
    assert differ.added_rows() == []


def test_added_columns():
    left = ScrapedTable(headers=["A", "B"], rows=[])
    right = ScrapedTable(headers=["A", "B", "C"], rows=[])
    differ = TableDiffer(left, right)
    assert differ.added_columns() == ["C"]


def test_removed_columns():
    left = ScrapedTable(headers=["A", "B", "C"], rows=[])
    right = ScrapedTable(headers=["A", "B"], rows=[])
    differ = TableDiffer(left, right)
    assert differ.removed_columns() == ["C"]


def test_added_columns_no_headers_returns_empty(table_no_headers):
    differ = TableDiffer(table_no_headers, table_no_headers)
    assert differ.added_columns() == []


def test_summary_keys(table_a, table_b):
    summary = TableDiffer(table_a, table_b).summary()
    assert "added_rows" in summary
    assert "removed_rows" in summary
    assert "added_columns" in summary
    assert "removed_columns" in summary
    assert "headers_match" in summary


def test_summary_headers_match(table_a, table_b):
    summary = TableDiffer(table_a, table_b).summary()
    assert summary["headers_match"] is True


def test_is_equal_same_table(table_a):
    differ = TableDiffer(table_a, table_a)
    assert differ.is_equal() is True


def test_is_equal_different_tables(table_a, table_b):
    differ = TableDiffer(table_a, table_b)
    assert differ.is_equal() is False


def test_summary_row_counts(table_a, table_b):
    summary = TableDiffer(table_a, table_b).summary()
    assert summary["left_row_count"] == 3
    assert summary["right_row_count"] == 3

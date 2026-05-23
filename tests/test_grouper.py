import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.grouper import TableGrouper


@pytest.fixture
def sample_table() -> ScrapedTable:
    return ScrapedTable(
        headers=["Name", "Department", "Score"],
        rows=[
            ["Alice", "Engineering", "90"],
            ["Bob", "Marketing", "75"],
            ["Carol", "Engineering", "88"],
            ["Dave", "Marketing", "82"],
            ["Eve", "Engineering", "95"],
        ],
    )


@pytest.fixture
def table_no_headers() -> ScrapedTable:
    return ScrapedTable(
        headers=None,
        rows=[["Alice", "Eng"], ["Bob", "Mkt"], ["Carol", "Eng"]],
    )


def test_group_by_column_returns_correct_keys(sample_table):
    grouper = TableGrouper(sample_table)
    groups = grouper.group_by_column("Department")
    assert set(groups.keys()) == {"Engineering", "Marketing"}


def test_group_by_column_engineering_has_three_rows(sample_table):
    grouper = TableGrouper(sample_table)
    groups = grouper.group_by_column("Department")
    assert len(groups["Engineering"].rows) == 3


def test_group_by_column_marketing_has_two_rows(sample_table):
    grouper = TableGrouper(sample_table)
    groups = grouper.group_by_column("Department")
    assert len(groups["Marketing"].rows) == 2


def test_group_by_column_preserves_headers(sample_table):
    grouper = TableGrouper(sample_table)
    groups = grouper.group_by_column("Department")
    for tbl in groups.values():
        assert tbl.headers == ["Name", "Department", "Score"]


def test_group_by_column_unknown_raises(sample_table):
    grouper = TableGrouper(sample_table)
    with pytest.raises(KeyError):
        grouper.group_by_column("NonExistent")


def test_group_by_column_no_headers_raises(table_no_headers):
    grouper = TableGrouper(table_no_headers)
    with pytest.raises(ValueError):
        grouper.group_by_column("Department")


def test_group_by_func_custom_key(sample_table):
    grouper = TableGrouper(sample_table)
    # Group by whether Score >= 90
    groups = grouper.group_by_func(lambda row: "high" if int(row[2]) >= 90 else "low")
    assert set(groups.keys()) == {"high", "low"}
    assert len(groups["high"].rows) == 2
    assert len(groups["low"].rows) == 3


def test_group_by_func_preserves_headers(sample_table):
    grouper = TableGrouper(sample_table)
    groups = grouper.group_by_func(lambda row: row[1])
    for tbl in groups.values():
        assert tbl.headers == ["Name", "Department", "Score"]


def test_group_by_func_no_headers_table(table_no_headers):
    grouper = TableGrouper(table_no_headers)
    groups = grouper.group_by_func(lambda row: row[1])
    assert set(groups.keys()) == {"Eng", "Mkt"}
    for tbl in groups.values():
        assert tbl.headers is None


def test_group_counts(sample_table):
    grouper = TableGrouper(sample_table)
    counts = grouper.group_counts("Department")
    assert counts == {"Engineering": 3, "Marketing": 2}

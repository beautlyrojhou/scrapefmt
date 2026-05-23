import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.renamer import TableRenamer, RenameError


@pytest.fixture
def sample_table() -> ScrapedTable:
    return ScrapedTable(
        headers=["Name", "Department", "Salary"],
        rows=[
            ["Alice", "Engineering", "90000"],
            ["Bob", "Marketing", "75000"],
            ["Carol", "Engineering", "95000"],
        ],
    )


@pytest.fixture
def table_no_headers() -> ScrapedTable:
    return ScrapedTable(
        headers=None,
        rows=[["Alice", "Engineering"], ["Bob", "Marketing"]],
    )


def test_rename_single_header(sample_table):
    renamer = TableRenamer(sample_table)
    result = renamer.rename({"Name": "FullName"})
    assert result.headers[0] == "FullName"
    assert result.headers[1] == "Department"
    assert result.headers[2] == "Salary"


def test_rename_multiple_headers(sample_table):
    renamer = TableRenamer(sample_table)
    result = renamer.rename({"Name": "Employee", "Salary": "Pay"})
    assert result.headers == ["Employee", "Department", "Pay"]


def test_rename_unknown_key_raises(sample_table):
    renamer = TableRenamer(sample_table)
    with pytest.raises(RenameError, match="Unknown header"):
        renamer.rename({"Ghost": "Phantom"})


def test_rename_no_headers_raises(table_no_headers):
    renamer = TableRenamer(table_no_headers)
    with pytest.raises(RenameError, match="no headers"):
        renamer.rename({"Name": "X"})


def test_rename_by_index(sample_table):
    renamer = TableRenamer(sample_table)
    result = renamer.rename_by_index({0: "FullName", 2: "Pay"})
    assert result.headers == ["FullName", "Department", "Pay"]


def test_rename_by_index_out_of_range_raises(sample_table):
    renamer = TableRenamer(sample_table)
    with pytest.raises(RenameError, match="out of range"):
        renamer.rename_by_index({10: "X"})


def test_rename_by_index_no_headers_raises(table_no_headers):
    renamer = TableRenamer(table_no_headers)
    with pytest.raises(RenameError, match="no headers"):
        renamer.rename_by_index({0: "X"})


def test_rename_with_func_uppercase(sample_table):
    renamer = TableRenamer(sample_table)
    result = renamer.rename_with_func(str.upper)
    assert result.headers == ["NAME", "DEPARTMENT", "SALARY"]


def test_rename_with_func_no_headers_returns_none_headers(table_no_headers):
    renamer = TableRenamer(table_no_headers)
    result = renamer.rename_with_func(str.upper)
    assert result.headers is None


def test_add_prefix(sample_table):
    renamer = TableRenamer(sample_table)
    result = renamer.add_prefix("col_")
    assert result.headers == ["col_Name", "col_Department", "col_Salary"]


def test_add_suffix(sample_table):
    renamer = TableRenamer(sample_table)
    result = renamer.add_suffix("_v2")
    assert result.headers == ["Name_v2", "Department_v2", "Salary_v2"]


def test_rename_preserves_rows(sample_table):
    renamer = TableRenamer(sample_table)
    result = renamer.rename({"Name": "Employee"})
    assert result.rows == sample_table.rows

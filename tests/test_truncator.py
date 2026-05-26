import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.truncator import TableTruncator, TruncateError


@pytest.fixture
def sample_table():
    return ScrapedTable(
        headers=["Name", "Description", "Tag"],
        rows=[
            ["Alice", "Software engineer at a large company", "eng"],
            ["Bob", "Product manager", "pm"],
            ["Carol", "Designer with extensive UI/UX background", "design"],
        ],
    )


@pytest.fixture
def table_no_headers():
    return ScrapedTable(
        headers=[],
        rows=[
            ["Hello World", "Short"],
            ["A very long string that should be cut", "OK"],
        ],
    )


def test_truncate_cells_shortens_long_values(sample_table):
    truncator = TableTruncator(sample_table)
    result = truncator.truncate_cells(max_length=15).table
    for row in result.rows:
        for cell in row:
            assert len(cell) <= 15


def test_truncate_cells_appends_placeholder(sample_table):
    truncator = TableTruncator(sample_table)
    result = truncator.truncate_cells(max_length=10, placeholder="...").table
    long_original = "Software engineer at a large company"
    assert len(long_original) > 10
    assert result.rows[0][1].endswith("...")


def test_truncate_cells_does_not_alter_short_values(sample_table):
    truncator = TableTruncator(sample_table)
    result = truncator.truncate_cells(max_length=50).table
    assert result.rows[1][1] == "Product manager"


def test_truncate_cells_exact_length_unchanged(sample_table):
    truncator = TableTruncator(sample_table)
    value = "Alice"
    result = truncator.truncate_cells(max_length=len(value)).table
    assert result.rows[0][0] == value


def test_truncate_cells_custom_placeholder(sample_table):
    truncator = TableTruncator(sample_table)
    result = truncator.truncate_cells(max_length=12, placeholder="--").table
    assert result.rows[0][1].endswith("--")


def test_truncate_cells_only_specified_columns(sample_table):
    truncator = TableTruncator(sample_table)
    result = truncator.truncate_cells(max_length=5, columns=["Name"]).table
    # Description should be untouched
    assert result.rows[0][1] == "Software engineer at a large company"
    # Name should be truncated
    assert len(result.rows[2][0]) <= 5


def test_truncate_column_convenience(sample_table):
    truncator = TableTruncator(sample_table)
    result = truncator.truncate_column("Description", max_length=10).table
    for row in result.rows:
        assert len(row[1]) <= 10


def test_truncate_cells_unknown_column_raises(sample_table):
    truncator = TableTruncator(sample_table)
    with pytest.raises(TruncateError, match="Unknown column"):
        truncator.truncate_cells(max_length=10, columns=["NonExistent"])


def test_truncate_cells_no_headers_with_columns_raises(table_no_headers):
    truncator = TableTruncator(table_no_headers)
    with pytest.raises(TruncateError, match="no headers"):
        truncator.truncate_cells(max_length=10, columns=["Name"])


def test_truncate_max_length_less_than_placeholder_raises(sample_table):
    truncator = TableTruncator(sample_table)
    with pytest.raises(TruncateError, match="max_length"):
        truncator.truncate_cells(max_length=2, placeholder="...")


def test_truncate_no_headers_all_columns(table_no_headers):
    truncator = TableTruncator(table_no_headers)
    result = truncator.truncate_cells(max_length=8).table
    for row in result.rows:
        for cell in row:
            assert len(cell) <= 8


def test_truncate_returns_self_for_chaining(sample_table):
    truncator = TableTruncator(sample_table)
    result = truncator.truncate_cells(max_length=20)
    assert result is truncator

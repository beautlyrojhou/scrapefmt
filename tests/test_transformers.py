"""Tests for scrapefmt.transformers module."""

import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.transformers import TableTransformer


@pytest.fixture
def sample_table():
    return ScrapedTable(
        headers=["Name", "Age", "City"],
        rows=[
            ["  Alice  ", "30", "New York"],
            ["Bob", "", "  Los Angeles  "],
            ["Charlie", "25", ""],
        ],
    )


@pytest.fixture
def table_no_headers():
    return ScrapedTable(
        headers=None,
        rows=[["a", "b"], ["c", "d"]],
    )


def test_rename_columns(sample_table):
    result = TableTransformer(sample_table).rename_columns({"Name": "Full Name", "City": "Location"}).result()
    assert result.headers == ["Full Name", "Age", "Location"]


def test_rename_columns_partial(sample_table):
    result = TableTransformer(sample_table).rename_columns({"Age": "Years"}).result()
    assert result.headers == ["Name", "Years", "City"]
    assert result.rows == sample_table.rows


def test_rename_columns_no_headers_is_noop(table_no_headers):
    result = TableTransformer(table_no_headers).rename_columns({"X": "Y"}).result()
    assert result.headers is None
    assert result.rows == table_no_headers.rows


def test_transform_column_uppercase(sample_table):
    result = TableTransformer(sample_table).transform_column("Name", str.upper).result()
    names = [row[0] for row in result.rows]
    assert names == ["  ALICE  ", "BOB", "CHARLIE"]


def test_transform_column_invalid_raises(sample_table):
    with pytest.raises(ValueError, match="Column 'Missing' not found"):
        TableTransformer(sample_table).transform_column("Missing", str.upper)


def test_strip_whitespace(sample_table):
    result = TableTransformer(sample_table).strip_whitespace().result()
    assert result.rows[0][0] == "Alice"
    assert result.rows[1][2] == "Los Angeles"
    assert result.headers == ["Name", "Age", "City"]


def test_fill_empty_all_columns(sample_table):
    result = TableTransformer(sample_table).fill_empty(value="N/A").result()
    assert result.rows[1][1] == "N/A"
    assert result.rows[2][2] == "N/A"
    assert result.rows[0][0] == "  Alice  "  # non-empty unchanged


def test_fill_empty_specific_column(sample_table):
    result = TableTransformer(sample_table).fill_empty(value="Unknown", column="Age").result()
    assert result.rows[1][1] == "Unknown"
    assert result.rows[2][2] == ""  # City column untouched


def test_fill_empty_invalid_column_raises(sample_table):
    with pytest.raises(ValueError, match="Column 'Score' not found"):
        TableTransformer(sample_table).fill_empty(value="0", column="Score")


def test_chaining(sample_table):
    result = (
        TableTransformer(sample_table)
        .strip_whitespace()
        .fill_empty(value="N/A")
        .rename_columns({"Name": "Full Name"})
        .result()
    )
    assert result.headers[0] == "Full Name"
    assert result.rows[1][1] == "N/A"
    assert result.rows[0][0] == "Alice"

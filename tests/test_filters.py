"""Tests for scrapefmt.filters module."""

import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.filters import TableFilter


@pytest.fixture
def sample_table():
    return ScrapedTable(
        headers=["Name", "Age", "City"],
        rows=[
            ["Alice", "30", "New York"],
            ["Bob", "25", "London"],
            ["Charlie", "35", "New York"],
            ["", "", ""],
            ["Diana", "28", "Paris"],
        ],
    )


@pytest.fixture
def table_no_headers():
    return ScrapedTable(
        headers=[],
        rows=[["a", "b"], ["c", "d"]],
    )


def test_filter_rows_by_predicate(sample_table):
    tf = TableFilter(sample_table)
    result = tf.filter_rows(lambda row: row[1] != "")
    assert result.num_rows() == 4


def test_exclude_empty_rows(sample_table):
    tf = TableFilter(sample_table)
    result = tf.exclude_empty_rows()
    assert result.num_rows() == 4
    for row in result.rows:
        assert any(cell.strip() for cell in row)


def test_filter_columns_returns_subset(sample_table):
    tf = TableFilter(sample_table)
    result = tf.filter_columns(["Name", "City"])
    assert result.headers == ["Name", "City"]
    assert result.num_columns() == 2
    assert result.rows[0] == ["Alice", "New York"]


def test_filter_columns_invalid_column(sample_table):
    tf = TableFilter(sample_table)
    with pytest.raises(ValueError, match="Country"):
        tf.filter_columns(["Name", "Country"])


def test_filter_columns_no_headers_raises(table_no_headers):
    tf = TableFilter(table_no_headers)
    with pytest.raises(ValueError, match="without headers"):
        tf.filter_columns(["a"])


def test_where_column_equals(sample_table):
    tf = TableFilter(sample_table)
    result = tf.where_column_equals("City", "New York")
    assert result.num_rows() == 2
    for row in result.rows:
        assert row[2] == "New York"


def test_where_column_equals_case_insensitive(sample_table):
    tf = TableFilter(sample_table)
    result = tf.where_column_equals("City", "new york", case_sensitive=False)
    assert result.num_rows() == 2


def test_where_column_equals_no_match(sample_table):
    tf = TableFilter(sample_table)
    result = tf.where_column_equals("City", "Tokyo")
    assert result.num_rows() == 0


def test_where_column_equals_invalid_column(sample_table):
    tf = TableFilter(sample_table)
    with pytest.raises(ValueError, match="Country"):
        tf.where_column_equals("Country", "France")


def test_filter_preserves_headers(sample_table):
    tf = TableFilter(sample_table)
    result = tf.exclude_empty_rows()
    assert result.headers == sample_table.headers

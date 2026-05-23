import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.flattener import TableFlattener


@pytest.fixture
def sample_table():
    return ScrapedTable(
        headers=["Name", "Age", "City"],
        rows=[
            ["Alice", "30", "New York"],
            ["Bob", "25", "London"],
            ["Carol", "35", "Paris"],
        ],
    )


@pytest.fixture
def table_no_headers():
    return ScrapedTable(
        headers=[],
        rows=[
            ["x", "y", "z"],
            ["1", "2", "3"],
        ],
    )


def test_flatten_to_values_returns_all_rows(sample_table):
    flattener = TableFlattener(sample_table)
    result = flattener.flatten_to_values()
    assert len(result) == 3
    assert result[0] == ["Alice", "30", "New York"]


def test_flatten_to_values_no_headers(table_no_headers):
    flattener = TableFlattener(table_no_headers)
    result = flattener.flatten_to_values()
    assert result == [["x", "y", "z"], ["1", "2", "3"]]


def test_flatten_to_strings_default_separator(sample_table):
    flattener = TableFlattener(sample_table)
    result = flattener.flatten_to_strings()
    assert result[0] == "Alice | 30 | New York"
    assert result[1] == "Bob | 25 | London"


def test_flatten_to_strings_custom_separator(sample_table):
    flattener = TableFlattener(sample_table)
    result = flattener.flatten_to_strings(separator=",")
    assert result[0] == "Alice,30,New York"


def test_flatten_to_strings_count(sample_table):
    flattener = TableFlattener(sample_table)
    result = flattener.flatten_to_strings()
    assert len(result) == 3


def test_flatten_with_headers_format(sample_table):
    flattener = TableFlattener(sample_table)
    result = flattener.flatten_with_headers()
    assert "Name: Alice" in result[0]
    assert "Age: 30" in result[0]
    assert "City: New York" in result[0]


def test_flatten_with_headers_custom_separators(sample_table):
    flattener = TableFlattener(sample_table)
    result = flattener.flatten_with_headers(separator="=", row_sep="; ")
    assert "Name=Alice" in result[0]
    assert "; " in result[0]


def test_flatten_with_headers_raises_when_no_headers(table_no_headers):
    flattener = TableFlattener(table_no_headers)
    with pytest.raises(ValueError, match="no headers"):
        flattener.flatten_with_headers()


def test_flatten_to_dict_values_returns_tuples(sample_table):
    flattener = TableFlattener(sample_table)
    result = flattener.flatten_to_dict_values()
    assert result[0][0] == ("Name", "Alice")
    assert result[0][1] == ("Age", "30")
    assert result[0][2] == ("City", "New York")


def test_flatten_to_dict_values_row_count(sample_table):
    flattener = TableFlattener(sample_table)
    result = flattener.flatten_to_dict_values()
    assert len(result) == 3


def test_flatten_to_dict_values_raises_when_no_headers(table_no_headers):
    flattener = TableFlattener(table_no_headers)
    with pytest.raises(ValueError, match="no headers"):
        flattener.flatten_to_dict_values()

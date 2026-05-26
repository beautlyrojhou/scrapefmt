import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.converter import TableConverter, ConvertError


@pytest.fixture
def sample_table() -> ScrapedTable:
    return ScrapedTable(
        headers=["Name", "Dept", "Score"],
        rows=[
            ["Alice", "Engineering", "90"],
            ["Bob", "Marketing", "75"],
            ["Carol", "Engineering", "88"],
        ],
    )


@pytest.fixture
def table_no_headers() -> ScrapedTable:
    return ScrapedTable(
        headers=[],
        rows=[["x", "1"], ["y", "2"]],
    )


def test_to_dict_of_lists_keys(sample_table):
    result = TableConverter(sample_table).to_dict_of_lists()
    assert set(result.keys()) == {"Name", "Dept", "Score"}


def test_to_dict_of_lists_values(sample_table):
    result = TableConverter(sample_table).to_dict_of_lists()
    assert result["Name"] == ["Alice", "Bob", "Carol"]
    assert result["Score"] == ["90", "75", "88"]


def test_to_dict_of_lists_no_headers_raises(table_no_headers):
    with pytest.raises(ConvertError):
        TableConverter(table_no_headers).to_dict_of_lists()


def test_to_list_of_lists_with_headers(sample_table):
    result = TableConverter(sample_table).to_list_of_lists(include_headers=True)
    assert result[0] == ["Name", "Dept", "Score"]
    assert len(result) == 4  # 1 header + 3 rows


def test_to_list_of_lists_without_headers(sample_table):
    result = TableConverter(sample_table).to_list_of_lists(include_headers=False)
    assert result[0] == ["Alice", "Engineering", "90"]
    assert len(result) == 3


def test_to_list_of_lists_no_headers_table(table_no_headers):
    result = TableConverter(table_no_headers).to_list_of_lists(include_headers=False)
    assert result == [["x", "1"], ["y", "2"]]


def test_to_transposed_list(sample_table):
    result = TableConverter(sample_table).to_transposed_list()
    assert len(result) == 3  # 3 columns become 3 rows
    assert result[0] == ["Alice", "Bob", "Carol"]
    assert result[2] == ["90", "75", "88"]


def test_to_transposed_list_empty():
    empty = ScrapedTable(headers=[], rows=[])
    result = TableConverter(empty).to_transposed_list()
    assert result == []


def test_to_indexed_dict_keys(sample_table):
    result = TableConverter(sample_table).to_indexed_dict("Name")
    assert set(result.keys()) == {"Alice", "Bob", "Carol"}


def test_to_indexed_dict_values(sample_table):
    result = TableConverter(sample_table).to_indexed_dict("Name")
    assert result["Alice"]["Dept"] == "Engineering"
    assert result["Bob"]["Score"] == "75"


def test_to_indexed_dict_unknown_column_raises(sample_table):
    with pytest.raises(ConvertError):
        TableConverter(sample_table).to_indexed_dict("Unknown")


def test_to_indexed_dict_no_headers_raises(table_no_headers):
    with pytest.raises(ConvertError):
        TableConverter(table_no_headers).to_indexed_dict("anything")


def test_to_flat_list(sample_table):
    result = TableConverter(sample_table).to_flat_list()
    assert len(result) == 9
    assert result[0] == "Alice"
    assert result[-1] == "88"


def test_invalid_input_raises():
    with pytest.raises(ConvertError):
        TableConverter("not a table")  # type: ignore

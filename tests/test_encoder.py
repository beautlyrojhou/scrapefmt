import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.encoder import TableEncoder, EncodeError


@pytest.fixture
def sample_table() -> ScrapedTable:
    return ScrapedTable(
        headers=["Name", "Dept", "Score"],
        rows=[
            ["Alice", "Engineering", "95"],
            ["Bob", "Marketing", "82"],
            ["Carol", "Engineering", "88"],
        ],
    )


@pytest.fixture
def table_no_headers() -> ScrapedTable:
    return ScrapedTable(
        headers=[],
        rows=[["X", "1"], ["Y", "2"]],
    )


def test_to_records_returns_correct_count(sample_table):
    enc = TableEncoder(sample_table)
    assert len(enc.to_records()) == 3


def test_to_records_keys_match_headers(sample_table):
    enc = TableEncoder(sample_table)
    record = enc.to_records()[0]
    assert set(record.keys()) == {"Name", "Dept", "Score"}


def test_to_records_values_correct(sample_table):
    enc = TableEncoder(sample_table)
    assert enc.to_records()[1]["Name"] == "Bob"


def test_to_records_no_headers_uses_index_keys(table_no_headers):
    enc = TableEncoder(table_no_headers)
    record = enc.to_records()[0]
    assert set(record.keys()) == {"0", "1"}


def test_to_matrix_includes_headers_as_first_row(sample_table):
    enc = TableEncoder(sample_table)
    matrix = enc.to_matrix()
    assert matrix[0] == ["Name", "Dept", "Score"]


def test_to_matrix_total_rows(sample_table):
    enc = TableEncoder(sample_table)
    # 1 header row + 3 data rows
    assert len(enc.to_matrix()) == 4


def test_to_matrix_no_headers_omits_header_row(table_no_headers):
    enc = TableEncoder(table_no_headers)
    assert len(enc.to_matrix()) == 2


def test_to_column_map_keys(sample_table):
    enc = TableEncoder(sample_table)
    col_map = enc.to_column_map()
    assert set(col_map.keys()) == {"Name", "Dept", "Score"}


def test_to_column_map_values(sample_table):
    enc = TableEncoder(sample_table)
    col_map = enc.to_column_map()
    assert col_map["Name"] == ["Alice", "Bob", "Carol"]


def test_to_column_map_no_headers_raises(table_no_headers):
    enc = TableEncoder(table_no_headers)
    with pytest.raises(EncodeError):
        enc.to_column_map()


def test_to_indexed_default_start(sample_table):
    enc = TableEncoder(sample_table)
    indexed = enc.to_indexed()
    assert set(indexed.keys()) == {0, 1, 2}


def test_to_indexed_custom_start(sample_table):
    enc = TableEncoder(sample_table)
    indexed = enc.to_indexed(start=10)
    assert set(indexed.keys()) == {10, 11, 12}


def test_to_indexed_values_match_records(sample_table):
    enc = TableEncoder(sample_table)
    indexed = enc.to_indexed()
    assert indexed[0]["Name"] == "Alice"
    assert indexed[2]["Dept"] == "Engineering"

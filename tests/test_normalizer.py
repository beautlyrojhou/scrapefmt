import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.normalizer import TableNormalizer, NormalizeError


@pytest.fixture
def sample_table():
    return ScrapedTable(
        headers=["Name", "Department", "Score"],
        rows=[
            ["Alice", "Engineering", "95"],
            ["Bob", "Marketing", "80"],
            ["Charlie", "Engineering", "88"],
        ],
    )


@pytest.fixture
def table_with_empties():
    return ScrapedTable(
        headers=["Name", "Value"],
        rows=[
            ["Alice", "hello"],
            ["", None],
            ["  ", "world"],
        ],
    )


def test_lowercase_converts_all_cells(sample_table):
    result = TableNormalizer(sample_table).lowercase().result()
    assert result.rows[0] == ["alice", "engineering", "95"]
    assert result.rows[1] == ["bob", "marketing", "80"]


def test_lowercase_preserves_headers(sample_table):
    result = TableNormalizer(sample_table).lowercase().result()
    assert result.headers == ["Name", "Department", "Score"]


def test_uppercase_converts_all_cells(sample_table):
    result = TableNormalizer(sample_table).uppercase().result()
    assert result.rows[0] == ["ALICE", "ENGINEERING", "95"]


def test_fill_empty_replaces_none(table_with_empties):
    result = TableNormalizer(table_with_empties).fill_empty(fill_value="N/A").result()
    assert result.rows[1][1] == "N/A"


def test_fill_empty_replaces_whitespace_only(table_with_empties):
    result = TableNormalizer(table_with_empties).fill_empty(fill_value="N/A").result()
    assert result.rows[2][0] == "N/A"


def test_fill_empty_preserves_non_empty(table_with_empties):
    result = TableNormalizer(table_with_empties).fill_empty(fill_value="N/A").result()
    assert result.rows[0][0] == "Alice"
    assert result.rows[0][1] == "hello"


def test_truncate_shortens_long_values(sample_table):
    result = TableNormalizer(sample_table).truncate(3).result()
    assert result.rows[0][0] == "Ali"
    assert result.rows[1][1] == "Mar"


def test_truncate_negative_raises():
    table = ScrapedTable(headers=["A"], rows=[["hello"]])
    with pytest.raises(NormalizeError):
        TableNormalizer(table).truncate(-1)


def test_truncate_preserves_short_values(sample_table):
    result = TableNormalizer(sample_table).truncate(100).result()
    assert result.rows[0][0] == "Alice"


def test_replace_substitutes_text(sample_table):
    result = TableNormalizer(sample_table).replace("Engineering", "Eng").result()
    assert result.rows[0][1] == "Eng"
    assert result.rows[2][1] == "Eng"
    assert result.rows[1][1] == "Marketing"


def test_chaining_methods(sample_table):
    result = (
        TableNormalizer(sample_table)
        .lowercase()
        .replace("engineering", "eng")
        .result()
    )
    assert result.rows[0][1] == "eng"
    assert result.rows[1][1] == "marketing"

import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.masker import TableMasker, MaskError


@pytest.fixture
def sample_table():
    return ScrapedTable(
        headers=["Name", "Email", "Score"],
        rows=[
            ["Alice", "alice@example.com", "95"],
            ["Bob", "bob@example.com", "80"],
            ["Carol", "carol@example.com", "70"],
        ],
    )


@pytest.fixture
def table_no_headers():
    return ScrapedTable(
        headers=None,
        rows=[["Alice", "alice@example.com"], ["Bob", "bob@example.com"]],
    )


def test_mask_column_replaces_all_values(sample_table):
    masker = TableMasker(sample_table)
    result = masker.mask_column("Email").table
    for row in result.rows:
        assert row[1] == "***"


def test_mask_column_custom_mask(sample_table):
    masker = TableMasker(sample_table)
    result = masker.mask_column("Email", mask="[REDACTED]").table
    assert result.rows[0][1] == "[REDACTED]"


def test_mask_column_with_predicate(sample_table):
    masker = TableMasker(sample_table)
    result = masker.mask_column("Score", predicate=lambda v: int(v) >= 90).table
    assert result.rows[0][2] == "***"   # 95 >= 90
    assert result.rows[1][2] == "80"    # 80 < 90 — not masked
    assert result.rows[2][2] == "70"    # 70 < 90 — not masked


def test_mask_column_unknown_raises(sample_table):
    masker = TableMasker(sample_table)
    with pytest.raises(MaskError, match="not found"):
        masker.mask_column("DoesNotExist")


def test_mask_column_no_headers_raises(table_no_headers):
    masker = TableMasker(table_no_headers)
    with pytest.raises(MaskError, match="without headers"):
        masker.mask_column("Email")


def test_mask_row_replaces_all_cells(sample_table):
    masker = TableMasker(sample_table)
    result = masker.mask_row(1).table
    assert result.rows[1] == ["***", "***", "***"]


def test_mask_row_preserves_other_rows(sample_table):
    masker = TableMasker(sample_table)
    result = masker.mask_row(0).table
    assert result.rows[1] == ["Bob", "bob@example.com", "80"]
    assert result.rows[2] == ["Carol", "carol@example.com", "70"]


def test_mask_row_out_of_range_raises(sample_table):
    masker = TableMasker(sample_table)
    with pytest.raises(MaskError, match="out of range"):
        masker.mask_row(99)


def test_mask_row_negative_index_raises(sample_table):
    masker = TableMasker(sample_table)
    with pytest.raises(MaskError, match="out of range"):
        masker.mask_row(-1)


def test_mask_by_func_transforms_all_cells(sample_table):
    masker = TableMasker(sample_table)
    result = masker.mask_by_func(lambda v, r, c: v.upper() if v else v).table
    assert result.rows[0][0] == "ALICE"
    assert result.rows[1][1] == "BOB@EXAMPLE.COM"


def test_mask_by_func_uses_row_col_index(sample_table):
    masker = TableMasker(sample_table)
    result = masker.mask_by_func(lambda v, r, c: f"{r},{c}").table
    assert result.rows[0][0] == "0,0"
    assert result.rows[2][2] == "2,2"


def test_chaining_returns_masker(sample_table):
    masker = TableMasker(sample_table)
    returned = masker.mask_column("Email")
    assert isinstance(returned, TableMasker)


def test_headers_preserved_after_mask(sample_table):
    masker = TableMasker(sample_table)
    result = masker.mask_column("Score").table
    assert result.headers == ["Name", "Email", "Score"]

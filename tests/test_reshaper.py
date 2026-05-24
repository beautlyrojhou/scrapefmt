import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.reshaper import TableReshaper, ReshapeError


@pytest.fixture
def sample_table() -> ScrapedTable:
    return ScrapedTable(
        headers=["Name", "Location", "Score"],
        rows=[
            ["Alice", "New York, USA", "90"],
            ["Bob", "London, UK", "85"],
            ["Carol", "Paris, France", "92"],
        ],
    )


@pytest.fixture
def table_no_headers() -> ScrapedTable:
    return ScrapedTable(
        headers=None,
        rows=[["Alice", "New York, USA"], ["Bob", "London, UK"]],
    )


@pytest.fixture
def sparse_table() -> ScrapedTable:
    return ScrapedTable(
        headers=["Group", "Value"],
        rows=[
            ["A", "1"],
            ["", "2"],
            ["", "3"],
            ["B", "4"],
            ["", "5"],
        ],
    )


def test_split_column_creates_new_headers(sample_table):
    reshaper = TableReshaper(sample_table)
    result = reshaper.split_column("Location", ",", ["City", "Country"])
    assert "City" in result.headers
    assert "Country" in result.headers


def test_split_column_drops_original_by_default(sample_table):
    reshaper = TableReshaper(sample_table)
    result = reshaper.split_column("Location", ",", ["City", "Country"])
    assert "Location" not in result.headers


def test_split_column_keeps_original_when_flagged(sample_table):
    reshaper = TableReshaper(sample_table)
    result = reshaper.split_column("Location", ",", ["City", "Country"], drop_original=False)
    assert "Location" in result.headers


def test_split_column_correct_values(sample_table):
    reshaper = TableReshaper(sample_table)
    result = reshaper.split_column("Location", ",", ["City", "Country"])
    cities = [row[result.headers.index("City")] for row in result.rows]
    assert cities == ["New York", "London", "Paris"]


def test_split_column_unknown_raises(sample_table):
    reshaper = TableReshaper(sample_table)
    with pytest.raises(ReshapeError):
        reshaper.split_column("Missing", ",", ["A", "B"])


def test_split_column_no_headers_raises(table_no_headers):
    reshaper = TableReshaper(table_no_headers)
    with pytest.raises(ReshapeError):
        reshaper.split_column("Location", ",", ["City", "Country"])


def test_melt_creates_variable_and_value_columns(sample_table):
    reshaper = TableReshaper(sample_table)
    result = reshaper.melt(id_columns=["Name"])
    assert "variable" in result.headers
    assert "value" in result.headers


def test_melt_row_count_is_multiplied(sample_table):
    reshaper = TableReshaper(sample_table)
    result = reshaper.melt(id_columns=["Name"])
    # 3 rows x 2 value columns (Location, Score)
    assert len(result.rows) == 6


def test_melt_custom_names(sample_table):
    reshaper = TableReshaper(sample_table)
    result = reshaper.melt(id_columns=["Name"], value_name="val", variable_name="var")
    assert "val" in result.headers
    assert "var" in result.headers


def test_melt_unknown_id_column_raises(sample_table):
    reshaper = TableReshaper(sample_table)
    with pytest.raises(ReshapeError):
        reshaper.melt(id_columns=["NonExistent"])


def test_melt_no_headers_raises(table_no_headers):
    reshaper = TableReshaper(table_no_headers)
    with pytest.raises(ReshapeError):
        reshaper.melt(id_columns=[])


def test_fill_down_fills_empty_cells(sparse_table):
    reshaper = TableReshaper(sparse_table)
    result = reshaper.fill_down(column="Group")
    groups = [row[0] for row in result.rows]
    assert groups == ["A", "A", "A", "B", "B"]


def test_fill_down_preserves_non_empty(sparse_table):
    reshaper = TableReshaper(sparse_table)
    result = reshaper.fill_down(column="Group")
    assert result.rows[0][0] == "A"
    assert result.rows[3][0] == "B"


def test_fill_down_unknown_column_raises(sample_table):
    reshaper = TableReshaper(sample_table)
    with pytest.raises(ReshapeError):
        reshaper.fill_down(column="Unknown")


def test_fill_down_preserves_headers(sparse_table):
    reshaper = TableReshaper(sparse_table)
    result = reshaper.fill_down()
    assert result.headers == ["Group", "Value"]

import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.summarizer import TableSummarizer


@pytest.fixture
def sample_table() -> ScrapedTable:
    return ScrapedTable(
        headers=["Name", "Age", "City"],
        rows=[
            ["Alice", "30", "New York"],
            ["Bob", "", "London"],
            ["Charlie", "25", ""],
            ["", "", ""],
        ],
    )


@pytest.fixture
def table_no_headers() -> ScrapedTable:
    return ScrapedTable(
        headers=None,
        rows=[["a", "b"], ["c", "d"]],
    )


def test_summarize_returns_dict(sample_table):
    s = TableSummarizer(sample_table)
    result = s.summarize()
    assert isinstance(result, dict)


def test_summarize_row_and_col_counts(sample_table):
    s = TableSummarizer(sample_table)
    result = s.summarize()
    assert result["num_rows"] == 4
    assert result["num_columns"] == 3


def test_summarize_has_headers(sample_table):
    s = TableSummarizer(sample_table)
    result = s.summarize()
    assert result["has_headers"] is True
    assert result["headers"] == ["Name", "Age", "City"]


def test_summarize_no_headers(table_no_headers):
    s = TableSummarizer(table_no_headers)
    result = s.summarize()
    assert result["has_headers"] is False
    assert result["headers"] is None


def test_empty_row_count(sample_table):
    s = TableSummarizer(sample_table)
    result = s.summarize()
    assert result["empty_row_count"] == 1


def test_column_stats_length(sample_table):
    s = TableSummarizer(sample_table)
    result = s.summarize()
    assert len(result["column_stats"]) == 3


def test_column_stats_headers(sample_table):
    s = TableSummarizer(sample_table)
    stats = s.summarize()["column_stats"]
    assert stats[0]["header"] == "Name"
    assert stats[1]["header"] == "Age"


def test_column_fill_rate(sample_table):
    s = TableSummarizer(sample_table)
    stats = s.summarize()["column_stats"]
    # "Name" column: 3 non-empty out of 4
    assert stats[0]["fill_rate"] == pytest.approx(0.75)
    # "Age" column: 2 non-empty out of 4
    assert stats[1]["fill_rate"] == pytest.approx(0.5)


def test_column_fill_rates_method(sample_table):
    s = TableSummarizer(sample_table)
    rates = s.column_fill_rates()
    assert "Name" in rates
    assert "Age" in rates
    assert "City" in rates
    assert rates["Name"] == pytest.approx(0.75)


def test_column_fill_rates_no_headers_uses_index(table_no_headers):
    s = TableSummarizer(table_no_headers)
    rates = s.column_fill_rates()
    assert 0 in rates
    assert 1 in rates


def test_empty_table_column_stats():
    t = ScrapedTable(headers=["A", "B"], rows=[])
    s = TableSummarizer(t)
    result = s.summarize()
    assert result["column_stats"] == []
    assert result["empty_row_count"] == 0

import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.aggregator import TableAggregator, AggregateError


@pytest.fixture
def sample_table() -> ScrapedTable:
    return ScrapedTable(
        headers=["Name", "Score", "Age"],
        rows=[
            ["Alice", "90", "30"],
            ["Bob", "80", "25"],
            ["Carol", "70", "35"],
            ["Dave", "80", "28"],
        ],
    )


@pytest.fixture
def table_no_headers() -> ScrapedTable:
    return ScrapedTable(
        headers=[],
        rows=[["Alice", "90"], ["Bob", "80"]],
    )


@pytest.fixture
def table_with_non_numeric() -> ScrapedTable:
    return ScrapedTable(
        headers=["Name", "Score"],
        rows=[["Alice", "90"], ["Bob", "N/A"], ["Carol", "70"]],
    )


def test_sum_returns_correct_value(sample_table):
    agg = TableAggregator(sample_table)
    assert agg.sum("Score") == 320.0


def test_mean_returns_correct_value(sample_table):
    agg = TableAggregator(sample_table)
    assert agg.mean("Score") == 80.0


def test_min_returns_correct_value(sample_table):
    agg = TableAggregator(sample_table)
    assert agg.min("Score") == 70.0


def test_max_returns_correct_value(sample_table):
    agg = TableAggregator(sample_table)
    assert agg.max("Score") == 90.0


def test_count_returns_correct_value(sample_table):
    agg = TableAggregator(sample_table)
    assert agg.count("Score") == 4


def test_aggregate_custom_func(sample_table):
    agg = TableAggregator(sample_table)
    result = agg.aggregate("Score", lambda vals: sorted(vals))
    assert result == [70.0, 80.0, 80.0, 90.0]


def test_unknown_column_raises(sample_table):
    agg = TableAggregator(sample_table)
    with pytest.raises(AggregateError, match="not found"):
        agg.sum("NonExistent")


def test_no_headers_raises(table_no_headers):
    agg = TableAggregator(table_no_headers)
    with pytest.raises(AggregateError, match="no headers"):
        agg.sum("Score")


def test_non_numeric_values_skipped(table_with_non_numeric):
    agg = TableAggregator(table_with_non_numeric)
    assert agg.sum("Score") == 160.0
    assert agg.count("Score") == 2


def test_mean_no_numeric_raises(table_with_non_numeric):
    table = ScrapedTable(headers=["Name", "Score"], rows=[["Alice", "n/a"]])
    agg = TableAggregator(table)
    with pytest.raises(AggregateError, match="No numeric values"):
        agg.mean("Score")


def test_summarize_column_returns_all_stats(sample_table):
    agg = TableAggregator(sample_table)
    stats = agg.summarize_column("Score")
    assert stats["sum"] == 320.0
    assert stats["mean"] == 80.0
    assert stats["min"] == 70.0
    assert stats["max"] == 90.0
    assert stats["count"] == 4


def test_summarize_column_no_numeric_returns_none_stats():
    table = ScrapedTable(headers=["Name", "Score"], rows=[["Alice", "n/a"]])
    agg = TableAggregator(table)
    stats = agg.summarize_column("Score")
    assert stats["sum"] is None
    assert stats["count"] == 0

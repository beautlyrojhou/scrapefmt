import pytest

from scrapefmt.models import ScrapedTable
from scrapefmt.sampler import SampleError, TableSampler


@pytest.fixture
def sample_table() -> ScrapedTable:
    return ScrapedTable(
        headers=["name", "dept", "score"],
        rows=[
            ["Alice", "Engineering", "90"],
            ["Bob", "Marketing", "85"],
            ["Carol", "Engineering", "78"],
            ["Dave", "Marketing", "92"],
            ["Eve", "Engineering", "88"],
            ["Frank", "HR", "74"],
        ],
    )


@pytest.fixture
def table_no_headers() -> ScrapedTable:
    return ScrapedTable(
        headers=None,
        rows=[["x", "1"], ["y", "2"], ["z", "3"]],
    )


def test_sample_returns_correct_count(sample_table):
    sampler = TableSampler(seed=42)
    result = sampler.sample(sample_table, 3)
    assert len(result.rows) == 3


def test_sample_preserves_headers(sample_table):
    sampler = TableSampler(seed=0)
    result = sampler.sample(sample_table, 2)
    assert result.headers == sample_table.headers


def test_sample_negative_raises(sample_table):
    sampler = TableSampler()
    with pytest.raises(SampleError):
        sampler.sample(sample_table, -1)


def test_sample_exceeds_rows_raises(sample_table):
    sampler = TableSampler()
    with pytest.raises(SampleError):
        sampler.sample(sample_table, 100)


def test_sample_zero_returns_empty(sample_table):
    sampler = TableSampler()
    result = sampler.sample(sample_table, 0)
    assert result.rows == []
    assert result.headers == sample_table.headers


def test_sample_fraction_half(sample_table):
    sampler = TableSampler(seed=7)
    result = sampler.sample_fraction(sample_table, 0.5)
    assert len(result.rows) == 3


def test_sample_fraction_invalid_raises(sample_table):
    sampler = TableSampler()
    with pytest.raises(SampleError):
        sampler.sample_fraction(sample_table, 1.5)


def test_head_sample_returns_first_n(sample_table):
    sampler = TableSampler()
    result = sampler.head_sample(sample_table, 2)
    assert result.rows == sample_table.rows[:2]


def test_head_sample_negative_raises(sample_table):
    sampler = TableSampler()
    with pytest.raises(SampleError):
        sampler.head_sample(sample_table, -3)


def test_stratified_sample_limits_per_group(sample_table):
    sampler = TableSampler(seed=1)
    result = sampler.stratified_sample(sample_table, "dept", 1)
    depts = [row[1] for row in result.rows]
    assert depts.count("Engineering") <= 1
    assert depts.count("Marketing") <= 1
    assert depts.count("HR") <= 1


def test_stratified_sample_no_headers_raises(table_no_headers):
    sampler = TableSampler()
    with pytest.raises(SampleError):
        sampler.stratified_sample(table_no_headers, "dept", 1)


def test_stratified_sample_unknown_column_raises(sample_table):
    sampler = TableSampler()
    with pytest.raises(SampleError):
        sampler.stratified_sample(sample_table, "nonexistent", 1)


def test_seed_produces_deterministic_results(sample_table):
    s1 = TableSampler(seed=99)
    s2 = TableSampler(seed=99)
    assert s1.sample(sample_table, 3).rows == s2.sample(sample_table, 3).rows

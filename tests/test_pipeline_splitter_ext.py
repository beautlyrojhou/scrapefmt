import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.pipeline import ScrapePipeline
import scrapefmt.pipeline_splitter_ext  # noqa: F401 – registers mixin


HTML = """
<table>
  <tr><th>Name</th><th>Dept</th><th>Score</th></tr>
  <tr><td>Alice</td><td>Engineering</td><td>90</td></tr>
  <tr><td>Bob</td><td>Marketing</td><td>75</td></tr>
  <tr><td>Carol</td><td>Engineering</td><td>88</td></tr>
  <tr><td>Dave</td><td>Marketing</td><td>60</td></tr>
  <tr><td>Eve</td><td>Engineering</td><td>95</td></tr>
</table>
"""


@pytest.fixture
def pipeline():
    return ScrapePipeline.from_html(HTML)


def test_pipeline_split_by_size_returns_list(pipeline):
    chunks = pipeline.split_by_size(2)
    assert isinstance(chunks, list)


def test_pipeline_split_by_size_correct_count(pipeline):
    chunks = pipeline.split_by_size(2)
    assert len(chunks) == 3


def test_pipeline_split_by_size_each_is_pipeline(pipeline):
    chunks = pipeline.split_by_size(2)
    for chunk in chunks:
        assert isinstance(chunk, ScrapePipeline)


def test_pipeline_split_by_size_total_rows_preserved(pipeline):
    chunks = pipeline.split_by_size(2)
    total = sum(len(c._table.rows) for c in chunks)
    assert total == 5


def test_pipeline_split_by_predicate_matched(pipeline):
    matched, _ = pipeline.split_by_predicate(lambda row: row[1] == "Engineering")
    assert len(matched._table.rows) == 3


def test_pipeline_split_by_predicate_unmatched(pipeline):
    _, unmatched = pipeline.split_by_predicate(lambda row: row[1] == "Engineering")
    assert len(unmatched._table.rows) == 2


def test_pipeline_split_at_row_top(pipeline):
    top, _ = pipeline.split_at_row(3)
    assert len(top._table.rows) == 3


def test_pipeline_split_at_row_bottom(pipeline):
    _, bottom = pipeline.split_at_row(3)
    assert len(bottom._table.rows) == 2


def test_pipeline_split_at_row_headers_preserved(pipeline):
    top, bottom = pipeline.split_at_row(2)
    assert top._table.headers == ["Name", "Dept", "Score"]
    assert bottom._table.headers == ["Name", "Dept", "Score"]

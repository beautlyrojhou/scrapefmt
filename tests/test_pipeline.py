import pytest
from scrapefmt.pipeline import ScrapePipeline
from scrapefmt.models import ScrapedTable

SIMPLE_HTML = """
<html><body>
  <table>
    <tr><th>Name</th><th>Score</th></tr>
    <tr><td>Alice</td><td>90</td></tr>
    <tr><td>  Bob  </td><td>  85  </td></tr>
    <tr><td></td><td></td></tr>
  </table>
</body></html>
"""

TWO_TABLE_HTML = """
<html><body>
  <table><tr><th>A</th></tr><tr><td>1</td></tr></table>
  <table><tr><th>B</th></tr><tr><td>2</td></tr></table>
</body></html>
"""


def test_from_html_creates_pipeline():
    p = ScrapePipeline.from_html(SIMPLE_HTML)
    assert isinstance(p, ScrapePipeline)


def test_from_html_no_tables_raises():
    with pytest.raises(ValueError, match="No tables found"):
        ScrapePipeline.from_html("<html><body><p>nothing</p></body></html>")


def test_from_html_bad_index_raises():
    with pytest.raises(IndexError):
        ScrapePipeline.from_html(SIMPLE_HTML, table_index=5)


def test_strip_whitespace_in_pipeline():
    p = ScrapePipeline.from_html(SIMPLE_HTML).strip_whitespace()
    table = p.get_table()
    assert table.rows[1][0] == "Bob"
    assert table.rows[1][1] == "85"


def test_exclude_empty_rows_in_pipeline():
    p = ScrapePipeline.from_html(SIMPLE_HTML).exclude_empty_rows()
    table = p.get_table()
    assert table.num_rows() == 2


def test_second_table_selected():
    p = ScrapePipeline.from_html(TWO_TABLE_HTML, table_index=1)
    table = p.get_table()
    assert table.headers == ["B"]


def test_pipeline_summarize():
    p = ScrapePipeline.from_html(SIMPLE_HTML)
    summary = p.summarize()
    assert summary["num_rows"] == 3
    assert summary["num_columns"] == 2
    assert summary["has_headers"] is True
    assert summary["empty_row_count"] == 1


def test_pipeline_summarize_after_filter():
    p = ScrapePipeline.from_html(SIMPLE_HTML).exclude_empty_rows()
    summary = p.summarize()
    assert summary["empty_row_count"] == 0
    assert summary["num_rows"] == 2


def test_pipeline_chaining():
    p = (
        ScrapePipeline.from_html(SIMPLE_HTML)
        .strip_whitespace()
        .exclude_empty_rows()
    )
    table = p.get_table()
    assert table.num_rows() == 2
    assert table.rows[1][0] == "Bob"

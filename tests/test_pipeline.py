"""Tests for the ScrapePipeline with transformer integration."""

import pytest
from scrapefmt.pipeline import ScrapePipeline
from scrapefmt.models import ScrapedTable


SIMPLE_HTML = """
<html><body>
  <table>
    <tr><th>Name</th><th>Score</th><th>City</th></tr>
    <tr><td>  Alice  </td><td>95</td><td>New York</td></tr>
    <tr><td>Bob</td><td></td><td>  Boston  </td></tr>
    <tr><td></td><td></td><td></td></tr>
  </table>
</body></html>
"""


def test_from_html_creates_pipeline():
    pipeline = ScrapePipeline.from_html(SIMPLE_HTML)
    assert isinstance(pipeline.result(), ScrapedTable)


def test_from_html_no_tables_raises():
    with pytest.raises(ValueError, match="No tables found"):
        ScrapePipeline.from_html("<html><body><p>no table</p></body></html>")


def test_from_html_bad_index_raises():
    with pytest.raises(IndexError):
        ScrapePipeline.from_html(SIMPLE_HTML, table_index=5)


def test_strip_whitespace_in_pipeline():
    result = ScrapePipeline.from_html(SIMPLE_HTML).strip_whitespace().result()
    assert result.rows[0][0] == "Alice"
    assert result.rows[1][2] == "Boston"


def test_exclude_empty_rows_in_pipeline():
    result = ScrapePipeline.from_html(SIMPLE_HTML).exclude_empty_rows().result()
    assert result.num_rows() == 2


def test_fill_empty_in_pipeline():
    result = (
        ScrapePipeline.from_html(SIMPLE_HTML)
        .fill_empty(value="N/A", column="Score")
        .result()
    )
    assert result.rows[1][1] == "N/A"


def test_rename_columns_in_pipeline():
    result = (
        ScrapePipeline.from_html(SIMPLE_HTML)
        .rename_columns({"Name": "Full Name", "Score": "Points"})
        .result()
    )
    assert result.headers == ["Full Name", "Points", "City"]


def test_transform_column_in_pipeline():
    result = (
        ScrapePipeline.from_html(SIMPLE_HTML)
        .strip_whitespace()
        .transform_column("Name", str.upper)
        .result()
    )
    assert result.rows[0][0] == "ALICE"
    assert result.rows[1][0] == "BOB"


def test_full_chain():
    result = (
        ScrapePipeline.from_html(SIMPLE_HTML)
        .strip_whitespace()
        .exclude_empty_rows()
        .fill_empty(value="0", column="Score")
        .rename_columns({"Name": "Player"})
        .result()
    )
    assert result.headers[0] == "Player"
    assert result.num_rows() == 2
    assert result.rows[1][1] == "0"


def test_export_csv_from_pipeline():
    output = (
        ScrapePipeline.from_html(SIMPLE_HTML)
        .strip_whitespace()
        .exclude_empty_rows()
        .export("csv")
    )
    assert "Name" in output
    assert "Alice" in output

import pytest
from scrapefmt.pipeline import ScrapePipeline
from scrapefmt.models import ScrapedTable


HTML_SINGLE = """
<html><body>
<table>
  <tr><th>Name</th><th>Location</th><th>Score</th></tr>
  <tr><td>Alice</td><td>New York, USA</td><td>90</td></tr>
  <tr><td>Bob</td><td>London, UK</td><td>85</td></tr>
  <tr><td>Carol</td><td>Paris, France</td><td>92</td></tr>
</table>
</body></html>
"""


@pytest.fixture
def pipeline() -> ScrapePipeline:
    return ScrapePipeline.from_html(HTML_SINGLE)


@pytest.fixture
def sparse_table() -> ScrapedTable:
    return ScrapedTable(
        headers=["Group", "Value"],
        rows=[["A", "1"], ["", "2"], ["", "3"], ["B", "4"], ["", "5"]],
    )


def test_pipeline_split_column_removes_original(pipeline):
    result = pipeline.split_column("Location", ",", ["City", "Country"]).build()
    assert "Location" not in result.headers


def test_pipeline_split_column_adds_new_headers(pipeline):
    result = pipeline.split_column("Location", ",", ["City", "Country"]).build()
    assert "City" in result.headers
    assert "Country" in result.headers


def test_pipeline_split_column_correct_row_count(pipeline):
    result = pipeline.split_column("Location", ",", ["City", "Country"]).build()
    assert len(result.rows) == 3


def test_pipeline_split_column_values_are_stripped(pipeline):
    """Ensure split values have surrounding whitespace removed."""
    result = pipeline.split_column("Location", ",", ["City", "Country"]).build()
    city_idx = result.headers.index("City")
    country_idx = result.headers.index("Country")
    cities = [row[city_idx] for row in result.rows]
    countries = [row[country_idx] for row in result.rows]
    assert cities == ["New York", "London", "Paris"]
    assert countries == ["USA", "UK", "France"]


def test_pipeline_melt_expands_rows(pipeline):
    result = pipeline.melt(id_columns=["Name"]).build()
    # 3 rows x 2 value columns
    assert len(result.rows) == 6


def test_pipeline_melt_has_variable_header(pipeline):
    result = pipeline.melt(id_columns=["Name"]).build()
    assert "variable" in result.headers


def test_pipeline_melt_has_value_header(pipeline):
    result = pipeline.melt(id_columns=["Name"]).build()
    assert "value" in result.headers


def test_pipeline_fill_down_fills_blanks():
    pipeline = ScrapePipeline(ScrapedTable(
        headers=["Group", "Value"],
        rows=[["A", "1"], ["", "2"], ["B", "3"], ["", "4"]],
    ))
    result = pipeline.fill_down(column="Group").build()
    groups = [row[0] for row in result.rows]
    assert groups == ["A", "A", "B", "B"]


def test_pipeline_fill_down_preserves_headers():
    pipeline = ScrapePipeline(ScrapedTable(
        headers=["Group", "Value"],
        rows=[["A", "1"], ["", "2"]],
    ))
    result = pipeline.fill_down().build()
    assert result.headers == ["Group", "Value"]


def test_pipeline_fill_down_sparse_table(sparse_table):
    """Ensure fill_down correctly propagates values across multiple consecutive blanks."""
    result = ScrapePipeline(sparse_table).fill_down(column="Group").build()
    groups = [row[0] for row in result.rows]
    assert groups == ["A", "A", "A", "B", "B"]


def test_pipeline_chained_split_and_filter(pipeline):
    result = (
        pipeline
        .split_column("Location", ",", ["City", "Country"])
        .filter_columns(["Name", "City", "Score"])
        .build()
    )
    assert result.headers == ["Name", "City", "Score"]
    assert len(result.rows) == 3


def test_pipeline_to_dict_list_after_melt(pipeline):
    records = pipeline.melt(id_columns=["Name"]).to_dict_list()
    assert len(records) == 6
    assert "Name" in records[0]
    assert "variable" in records[0]
    assert "value" in records[0]

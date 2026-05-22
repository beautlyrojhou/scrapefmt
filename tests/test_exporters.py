"""Tests for scrapefmt exporters."""

import json
import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.exporters import CSVExporter, JSONExporter, MarkdownExporter


@pytest.fixture
def sample_table():
    return ScrapedTable(
        headers=["Name", "Age", "City"],
        rows=[
            ["Alice", "30", "New York"],
            ["Bob", "25", "London"],
            ["Charlie", "35", "Tokyo"],
        ],
    )


@pytest.fixture
def table_no_headers():
    return ScrapedTable(
        headers=[],
        rows=[["1", "2", "3"], ["4", "5", "6"]],
    )


def test_csv_export_with_headers(sample_table):
    exporter = CSVExporter()
    result = exporter.export(sample_table)
    lines = result.strip().splitlines()
    assert lines[0] == "Name,Age,City"
    assert lines[1] == "Alice,30,New York"
    assert lines[3] == "Charlie,35,Tokyo"


def test_csv_export_row_count(sample_table):
    exporter = CSVExporter()
    result = exporter.export(sample_table)
    lines = result.strip().splitlines()
    assert len(lines) == 4  # 1 header + 3 data rows


def test_csv_export_custom_delimiter(sample_table):
    exporter = CSVExporter(delimiter=";")
    result = exporter.export(sample_table)
    assert "Name;Age;City" in result


def test_json_export_structure(sample_table):
    exporter = JSONExporter()
    result = exporter.export(sample_table)
    data = json.loads(result)
    assert isinstance(data, list)
    assert len(data) == 3
    assert data[0] == {"Name": "Alice", "Age": "30", "City": "New York"}


def test_json_export_keys(sample_table):
    exporter = JSONExporter()
    result = exporter.export(sample_table)
    data = json.loads(result)
    assert list(data[0].keys()) == ["Name", "Age", "City"]


def test_markdown_export_headers(sample_table):
    exporter = MarkdownExporter()
    result = exporter.export(sample_table)
    lines = result.strip().splitlines()
    assert lines[0] == "| Name | Age | City |"
    assert lines[1] == "| --- | --- | --- |"


def test_markdown_export_rows(sample_table):
    exporter = MarkdownExporter()
    result = exporter.export(sample_table)
    lines = result.strip().splitlines()
    assert lines[2] == "| Alice | 30 | New York |"


def test_markdown_export_no_headers(table_no_headers):
    exporter = MarkdownExporter()
    result = exporter.export(table_no_headers)
    lines = result.strip().splitlines()
    assert "Col1" in lines[0]
    assert "Col2" in lines[0]


def test_csv_export_to_file(sample_table, tmp_path):
    exporter = CSVExporter()
    file_path = str(tmp_path / "output.csv")
    exporter.export(sample_table, file_path=file_path)
    with open(file_path, "r") as f:
        content = f.read()
    assert "Name,Age,City" in content


def test_json_export_to_file(sample_table, tmp_path):
    exporter = JSONExporter()
    file_path = str(tmp_path / "output.json")
    exporter.export(sample_table, file_path=file_path)
    with open(file_path, "r") as f:
        data = json.load(f)
    assert len(data) == 3

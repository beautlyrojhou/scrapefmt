"""Tests for the FormatRegistry."""

import pytest
from scrapefmt.format_registry import FormatRegistry, default_registry
from scrapefmt.exporters import CSVExporter, JSONExporter, MarkdownExporter
from scrapefmt.models import ScrapedTable


@pytest.fixture
def registry():
    return FormatRegistry()


def test_default_formats_available(registry):
    formats = registry.available_formats()
    assert "csv" in formats
    assert "json" in formats
    assert "md" in formats
    assert "markdown" in formats


def test_get_csv_exporter(registry):
    exporter_cls = registry.get("csv")
    assert exporter_cls is CSVExporter


def test_get_json_exporter(registry):
    exporter_cls = registry.get("json")
    assert exporter_cls is JSONExporter


def test_get_markdown_exporter(registry):
    assert registry.get("md") is MarkdownExporter
    assert registry.get("markdown") is MarkdownExporter


def test_get_case_insensitive(registry):
    assert registry.get("CSV") is CSVExporter
    assert registry.get("Json") is JSONExporter


def test_get_unknown_format_raises(registry):
    with pytest.raises(KeyError, match="Unknown format"):
        registry.get("xlsx")


def test_register_custom_exporter(registry):
    class TSVExporter:
        def export(self, table, file_path=None):
            return "\t".join(table.headers)

    registry.register("tsv", TSVExporter)
    assert registry.get("tsv") is TSVExporter
    assert "tsv" in registry.available_formats()


def test_register_invalid_exporter_raises(registry):
    class BadExporter:
        pass

    with pytest.raises(ValueError, match="export"):
        registry.register("bad", BadExporter)


def test_unregister_custom_format(registry):
    class TSVExporter:
        def export(self, table, file_path=None):
            return ""

    registry.register("tsv", TSVExporter)
    registry.unregister("tsv")
    assert "tsv" not in registry.available_formats()


def test_unregister_builtin_raises(registry):
    with pytest.raises(ValueError, match="built-in"):
        registry.unregister("csv")


def test_unregister_unknown_raises(registry):
    with pytest.raises(KeyError):
        registry.unregister("nonexistent")


def test_default_registry_is_instance():
    assert isinstance(default_registry, FormatRegistry)
    assert "csv" in default_registry.available_formats()


def test_registry_exporter_produces_output(registry):
    table = ScrapedTable(headers=["A", "B"], rows=[["1", "2"]])
    exporter_cls = registry.get("json")
    exporter = exporter_cls()
    result = exporter.export(table)
    assert "A" in result

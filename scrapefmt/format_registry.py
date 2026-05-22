"""Registry for managing and resolving export format handlers."""

from typing import Dict, Type, List
from scrapefmt.exporters import CSVExporter, JSONExporter, MarkdownExporter


class FormatRegistry:
    """Central registry mapping format names to exporter classes."""

    _default_formats: Dict[str, type] = {
        "csv": CSVExporter,
        "json": JSONExporter,
        "md": MarkdownExporter,
        "markdown": MarkdownExporter,
    }

    def __init__(self):
        self._formats: Dict[str, type] = dict(self._default_formats)

    def register(self, name: str, exporter_class: type) -> None:
        """Register a custom exporter under a format name."""
        if not callable(getattr(exporter_class, "export", None)):
            raise ValueError(
                f"Exporter class must implement an 'export' method: {exporter_class}"
            )
        self._formats[name.lower()] = exporter_class

    def get(self, name: str) -> type:
        """Retrieve an exporter class by format name."""
        key = name.lower()
        if key not in self._formats:
            raise KeyError(
                f"Unknown format '{name}'. Available: {self.available_formats()}"
            )
        return self._formats[key]

    def available_formats(self) -> List[str]:
        """Return list of all registered format names."""
        return sorted(self._formats.keys())

    def unregister(self, name: str) -> None:
        """Remove a format from the registry."""
        key = name.lower()
        if key in self._default_formats:
            raise ValueError(f"Cannot unregister built-in format '{name}'")
        if key not in self._formats:
            raise KeyError(f"Format '{name}' is not registered")
        del self._formats[key]


# Module-level default registry instance
default_registry = FormatRegistry()

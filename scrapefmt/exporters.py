"""Exporters for converting ScrapedTable data to various formats."""

import csv
import json
import io
from typing import List, Optional
from scrapefmt.models import ScrapedTable


class CSVExporter:
    """Export ScrapedTable data to CSV format."""

    def __init__(self, delimiter: str = ",", quotechar: str = '"'):
        self.delimiter = delimiter
        self.quotechar = quotechar

    def export(self, table: ScrapedTable, file_path: Optional[str] = None) -> str:
        """Export a ScrapedTable to CSV string or file."""
        output = io.StringIO()
        writer = csv.writer(
            output, delimiter=self.delimiter, quotechar=self.quotechar
        )

        if table.headers:
            writer.writerow(table.headers)

        for row in table.rows:
            writer.writerow(row)

        csv_content = output.getvalue()

        if file_path:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                f.write(csv_content)

        return csv_content


class JSONExporter:
    """Export ScrapedTable data to JSON format."""

    def __init__(self, indent: int = 2, ensure_ascii: bool = False):
        self.indent = indent
        self.ensure_ascii = ensure_ascii

    def export(self, table: ScrapedTable, file_path: Optional[str] = None) -> str:
        """Export a ScrapedTable to JSON string or file."""
        data = table.to_dict_list()
        json_content = json.dumps(data, indent=self.indent, ensure_ascii=self.ensure_ascii)

        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(json_content)

        return json_content


class MarkdownExporter:
    """Export ScrapedTable data to Markdown table format."""

    def export(self, table: ScrapedTable, file_path: Optional[str] = None) -> str:
        """Export a ScrapedTable to Markdown table string or file."""
        lines = []

        headers = table.headers or [f"Col{i+1}" for i in range(table.num_columns())]
        lines.append("| " + " | ".join(str(h) for h in headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

        for row in table.rows:
            lines.append("| " + " | ".join(str(cell) for cell in row) + " |")

        md_content = "\n".join(lines) + "\n"

        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(md_content)

        return md_content

import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.highlighter import TableHighlighter, HighlightError


@pytest.fixture
def sample_table() -> ScrapedTable:
    return ScrapedTable(
        headers=["Name", "Score", "Grade"],
        rows=[
            ["Alice", "95", "A"],
            ["Bob", "72", "C"],
            ["Carol", "88", "B"],
            ["Dave", "55", "F"],
        ],
    )


@pytest.fixture
def table_no_headers() -> ScrapedTable:
    return ScrapedTable(
        headers=None,
        rows=[["Alice", "95"], ["Bob", "72"]],
    )


@pytest.fixture
def highlighter(sample_table) -> TableHighlighter:
    return TableHighlighter(sample_table)


def test_highlight_column_returns_self(highlighter):
    result = highlighter.highlight_column("Grade", lambda v: v == "A")
    assert result is highlighter


def test_highlight_column_marks_correct_cells(highlighter):
    highlighter.highlight_column("Grade", lambda v: v == "A")
    cells = highlighter.highlighted_cells()
    assert len(cells) == 1
    assert cells[0]["value"] == "A"
    assert cells[0]["row_index"] == 0


def test_highlight_column_multiple_matches(highlighter):
    highlighter.highlight_column("Score", lambda v: int(v) >= 80)
    cells = highlighter.highlighted_cells()
    values = {c["value"] for c in cells}
    assert values == {"95", "88"}


def test_highlight_column_unknown_raises(highlighter):
    with pytest.raises(HighlightError, match="not found"):
        highlighter.highlight_column("Missing", lambda v: True)


def test_highlight_column_no_headers_raises(table_no_headers):
    h = TableHighlighter(table_no_headers)
    with pytest.raises(HighlightError, match="no headers"):
        h.highlight_column("Score", lambda v: True)


def test_highlight_row_marks_all_cells_in_row(highlighter):
    highlighter.highlight_row(lambda row: row[2] == "F")
    cells = highlighter.highlighted_cells()
    assert len(cells) == 3  # three columns in the failing row
    assert all(c["row_index"] == 3 for c in cells)


def test_highlight_row_returns_self(highlighter):
    result = highlighter.highlight_row(lambda row: False)
    assert result is highlighter


def test_highlighted_cells_filter_by_label(highlighter):
    highlighter.highlight_column("Grade", lambda v: v == "A", label="top")
    highlighter.highlight_column("Grade", lambda v: v == "F", label="fail")
    top_cells = highlighter.highlighted_cells(label="top")
    fail_cells = highlighter.highlighted_cells(label="fail")
    assert len(top_cells) == 1
    assert len(fail_cells) == 1
    assert top_cells[0]["value"] == "A"
    assert fail_cells[0]["value"] == "F"


def test_get_highlights_returns_dict(highlighter):
    highlighter.highlight_column("Score", lambda v: int(v) < 60, label="low")
    h = highlighter.get_highlights()
    assert isinstance(h, dict)
    assert all(v == "low" for v in h.values())


def test_clear_removes_all_highlights(highlighter):
    highlighter.highlight_column("Grade", lambda v: True)
    highlighter.clear()
    assert highlighter.highlighted_cells() == []


def test_clear_returns_self(highlighter):
    result = highlighter.clear()
    assert result is highlighter

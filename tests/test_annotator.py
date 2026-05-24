import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.annotator import TableAnnotator, AnnotateError


@pytest.fixture
def sample_table():
    return ScrapedTable(
        headers=["Name", "Score", "Grade"],
        rows=[
            ["Alice", "92", "A"],
            ["Bob", "75", "B"],
            ["Carol", "88", "A"],
            ["Dave", "60", "C"],
        ],
    )


@pytest.fixture
def table_no_headers():
    return ScrapedTable(
        headers=None,
        rows=[["Alice", "92"], ["Bob", "75"]],
    )


def test_annotate_column_returns_self(sample_table):
    annotator = TableAnnotator(sample_table)
    result = annotator.annotate_column("Score", "numeric", lambda v: v.isdigit())
    assert result is annotator


def test_annotate_column_correct_count(sample_table):
    annotator = TableAnnotator(sample_table)
    annotator.annotate_column("Score", "numeric", lambda v: v.isdigit())
    col_annotations = annotator.get_column_annotation("Score")
    assert len(col_annotations) == 4


def test_annotate_column_values_correct(sample_table):
    annotator = TableAnnotator(sample_table)
    annotator.annotate_column("Score", "as_int", lambda v: int(v))
    col_annotations = annotator.get_column_annotation("Score")
    assert col_annotations[0] == {"as_int": 92}
    assert col_annotations[1] == {"as_int": 75}


def test_annotate_column_unknown_raises(sample_table):
    annotator = TableAnnotator(sample_table)
    with pytest.raises(AnnotateError, match="not found in headers"):
        annotator.annotate_column("Missing", "key", lambda v: v)


def test_annotate_column_no_headers_raises(table_no_headers):
    annotator = TableAnnotator(table_no_headers)
    with pytest.raises(AnnotateError, match="no headers"):
        annotator.annotate_column("Score", "key", lambda v: v)


def test_annotate_row_returns_self(sample_table):
    annotator = TableAnnotator(sample_table)
    result = annotator.annotate_row(0, "checked", True)
    assert result is annotator


def test_annotate_row_stores_value(sample_table):
    annotator = TableAnnotator(sample_table)
    annotator.annotate_row(2, "reviewed", "yes")
    ann = annotator.get_row_annotation(2)
    assert ann["reviewed"] == "yes"


def test_annotate_row_out_of_range_raises(sample_table):
    annotator = TableAnnotator(sample_table)
    with pytest.raises(AnnotateError, match="out of range"):
        annotator.annotate_row(99, "key", "value")


def test_annotate_row_negative_raises(sample_table):
    annotator = TableAnnotator(sample_table)
    with pytest.raises(AnnotateError, match="out of range"):
        annotator.annotate_row(-1, "key", "value")


def test_annotate_rows_by_applies_to_all(sample_table):
    annotator = TableAnnotator(sample_table)
    annotator.annotate_rows_by("length", lambda row: len(row))
    for i in range(len(sample_table.rows)):
        ann = annotator.get_row_annotation(i)
        assert ann["length"] == 3


def test_get_annotations_returns_all(sample_table):
    annotator = TableAnnotator(sample_table)
    annotator.annotate_row(0, "flag", True)
    annotator.annotate_column("Grade", "upper", lambda v: v.upper())
    all_ann = annotator.get_annotations()
    assert "row:0" in all_ann
    assert "column:Grade" in all_ann


def test_get_column_annotation_empty_when_not_set(sample_table):
    annotator = TableAnnotator(sample_table)
    result = annotator.get_column_annotation("Name")
    assert result == []


def test_get_row_annotation_empty_when_not_set(sample_table):
    annotator = TableAnnotator(sample_table)
    result = annotator.get_row_annotation(1)
    assert result == {}

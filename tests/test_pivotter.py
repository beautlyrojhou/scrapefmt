import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.pivotter import TablePivotter, PivotError


@pytest.fixture
def sample_table() -> ScrapedTable:
    headers = ["name", "subject", "score"]
    rows = [
        ["Alice", "Math", "90"],
        ["Alice", "Science", "85"],
        ["Bob", "Math", "78"],
        ["Bob", "Science", "92"],
    ]
    return ScrapedTable(headers=headers, rows=rows)


@pytest.fixture
def table_no_headers() -> ScrapedTable:
    return ScrapedTable(headers=[], rows=[["a", "b"], ["c", "d"]])


@pytest.fixture
def simple_table() -> ScrapedTable:
    headers = ["col1", "col2"]
    rows = [["x", "y"], ["1", "2"]]
    return ScrapedTable(headers=headers, rows=rows)


def test_pivot_creates_correct_headers(sample_table):
    pivotter = TablePivotter(sample_table)
    result = pivotter.pivot("name", "subject", "score")
    assert result.headers == ["name", "Math", "Science"]


def test_pivot_creates_correct_row_count(sample_table):
    pivotter = TablePivotter(sample_table)
    result = pivotter.pivot("name", "subject", "score")
    assert result.num_rows == 2


def test_pivot_alice_row_values(sample_table):
    pivotter = TablePivotter(sample_table)
    result = pivotter.pivot("name", "subject", "score")
    alice_row = result.rows[0]
    assert alice_row[0] == "Alice"
    assert alice_row[1] == "90"   # Math
    assert alice_row[2] == "85"   # Science


def test_pivot_bob_row_values(sample_table):
    pivotter = TablePivotter(sample_table)
    result = pivotter.pivot("name", "subject", "score")
    bob_row = result.rows[1]
    assert bob_row[0] == "Bob"
    assert bob_row[1] == "78"
    assert bob_row[2] == "92"


def test_pivot_missing_column_raises(sample_table):
    pivotter = TablePivotter(sample_table)
    with pytest.raises(PivotError, match="Column 'nonexistent' not found"):
        pivotter.pivot("nonexistent", "subject", "score")


def test_pivot_no_headers_raises(table_no_headers):
    pivotter = TablePivotter(table_no_headers)
    with pytest.raises(PivotError, match="without headers"):
        pivotter.pivot("a", "b", "c")


def test_transpose_swaps_rows_and_columns(simple_table):
    pivotter = TablePivotter(simple_table)
    result = pivotter.transpose()
    # Original: headers=[col1,col2], rows=[[x,y],[1,2]]
    # All rows incl headers: [[col1,col2],[x,y],[1,2]]
    # Transposed: [[col1,x,1],[col2,y,2]]
    assert result.headers == ["col1", "x", "1"]
    assert result.rows[0] == ["col2", "y", "2"]


def test_transpose_row_count(simple_table):
    pivotter = TablePivotter(simple_table)
    result = pivotter.transpose()
    assert result.num_rows == 1
    assert result.num_columns == 3


def test_transpose_no_headers(table_no_headers):
    pivotter = TablePivotter(table_no_headers)
    result = pivotter.transpose()
    # rows [[a,b],[c,d]] -> transposed [[a,c],[b,d]]
    assert result.headers == ["a", "c"]
    assert result.rows[0] == ["b", "d"]


def test_transpose_empty_table():
    empty = ScrapedTable(headers=[], rows=[])
    pivotter = TablePivotter(empty)
    result = pivotter.transpose()
    assert result.headers == []
    assert result.rows == []

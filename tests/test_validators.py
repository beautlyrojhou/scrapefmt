import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.validators import TableValidator, ValidationError


@pytest.fixture
def sample_table():
    return ScrapedTable(
        headers=["Name", "Age", "City"],
        rows=[
            ["Alice", "30", "New York"],
            ["Bob", "25", "London"],
            ["Carol", "28", "Berlin"],
        ],
    )


@pytest.fixture
def empty_table():
    return ScrapedTable(headers=[], rows=[])


def test_valid_table_passes_default_validator(sample_table):
    validator = TableValidator()
    assert validator.is_valid(sample_table) is True


def test_min_rows_passes(sample_table):
    validator = TableValidator(min_rows=2)
    validator.validate(sample_table)  # should not raise


def test_min_rows_fails(sample_table):
    validator = TableValidator(min_rows=10)
    with pytest.raises(ValidationError, match="at least 10"):
        validator.validate(sample_table)


def test_max_rows_passes(sample_table):
    validator = TableValidator(max_rows=5)
    validator.validate(sample_table)


def test_max_rows_fails(sample_table):
    validator = TableValidator(max_rows=2)
    with pytest.raises(ValidationError, match="at most 2"):
        validator.validate(sample_table)


def test_min_columns_passes(sample_table):
    validator = TableValidator(min_columns=3)
    validator.validate(sample_table)


def test_min_columns_fails(sample_table):
    validator = TableValidator(min_columns=5)
    with pytest.raises(ValidationError, match="at least 5"):
        validator.validate(sample_table)


def test_required_headers_present(sample_table):
    validator = TableValidator(required_headers=["Name", "Age"])
    validator.validate(sample_table)


def test_required_headers_missing(sample_table):
    validator = TableValidator(required_headers=["Name", "Email"])
    with pytest.raises(ValidationError, match="Email"):
        validator.validate(sample_table)


def test_empty_headers_not_allowed():
    table = ScrapedTable(
        headers=["Name", "", "City"],
        rows=[["Alice", "30", "NY"]],
    )
    validator = TableValidator(allow_empty_headers=False)
    with pytest.raises(ValidationError, match="empty header"):
        validator.validate(table)


def test_empty_headers_allowed_by_default():
    table = ScrapedTable(
        headers=["Name", "", "City"],
        rows=[["Alice", "30", "NY"]],
    )
    validator = TableValidator()
    assert validator.is_valid(table) is True


def test_is_valid_returns_false_on_failure(sample_table):
    validator = TableValidator(min_rows=100)
    assert validator.is_valid(sample_table) is False


def test_empty_table_fails_min_rows():
    table = ScrapedTable(headers=[], rows=[])
    validator = TableValidator(min_rows=1)
    assert validator.is_valid(table) is False

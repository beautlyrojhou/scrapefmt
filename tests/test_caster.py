"""Tests for TableCaster."""

import pytest
from scrapefmt.models import ScrapedTable
from scrapefmt.caster import TableCaster, CastError


@pytest.fixture
def sample_table() -> ScrapedTable:
    return ScrapedTable(
        headers=["name", "age", "score", "active"],
        rows=[
            ["Alice", "30", "9.5", "true"],
            ["Bob", "25", "8.0", "false"],
            ["Carol", "40", "7.75", "yes"],
        ],
    )


@pytest.fixture
def table_no_headers() -> ScrapedTable:
    return ScrapedTable(headers=None, rows=[["Alice", "30"], ["Bob", "25"]])


def test_cast_int_converts_values(sample_table):
    caster = TableCaster(sample_table)
    result = caster.cast_int("age")
    ages = [row[1] for row in result.rows]
    assert ages == [30, 25, 40]
    assert all(isinstance(a, int) for a in ages)


def test_cast_float_converts_values(sample_table):
    caster = TableCaster(sample_table)
    result = caster.cast_float("score")
    scores = [row[2] for row in result.rows]
    assert scores == [9.5, 8.0, 7.75]
    assert all(isinstance(s, float) for s in scores)


def test_cast_bool_true_false(sample_table):
    caster = TableCaster(sample_table)
    result = caster.cast_bool("active")
    actives = [row[3] for row in result.rows]
    assert actives == [True, False, True]


def test_cast_int_invalid_raises(sample_table):
    bad_table = ScrapedTable(
        headers=["name", "age"],
        rows=[["Alice", "not-a-number"]],
    )
    caster = TableCaster(bad_table)
    with pytest.raises(CastError):
        caster.cast_int("age")


def test_cast_int_errors_ignore_leaves_value(sample_table):
    bad_table = ScrapedTable(
        headers=["name", "age"],
        rows=[["Alice", "n/a"], ["Bob", "25"]],
    )
    caster = TableCaster(bad_table)
    result = caster.cast_int("age", errors="ignore")
    assert result.rows[0][1] == "n/a"
    assert result.rows[1][1] == 25


def test_cast_int_errors_null_replaces_with_none(sample_table):
    bad_table = ScrapedTable(
        headers=["name", "age"],
        rows=[["Alice", "n/a"], ["Bob", "25"]],
    )
    caster = TableCaster(bad_table)
    result = caster.cast_int("age", errors="null")
    assert result.rows[0][1] is None
    assert result.rows[1][1] == 25


def test_cast_unknown_column_raises(sample_table):
    caster = TableCaster(sample_table)
    with pytest.raises(ValueError, match="not found"):
        caster.cast_int("nonexistent")


def test_cast_column_no_headers_raises(table_no_headers):
    caster = TableCaster(table_no_headers)
    with pytest.raises(ValueError, match="not found"):
        caster.cast_int("age")


def test_cast_does_not_mutate_original(sample_table):
    caster = TableCaster(sample_table)
    result = caster.cast_int("age")
    # Original rows should still contain strings
    assert sample_table.rows[0][1] == "30"
    assert result.rows[0][1] == 30


def test_cast_bool_custom_values():
    table = ScrapedTable(
        headers=["name", "active"],
        rows=[["Alice", "Y"], ["Bob", "N"]],
    )
    caster = TableCaster(table)
    result = caster.cast_bool("active", true_values=["Y"], false_values=["N"])
    assert result.rows[0][1] is True
    assert result.rows[1][1] is False

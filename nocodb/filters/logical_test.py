"""Tests for logical operators (And, Or, Not) using v3 API patterns.

v3 API uses:
- ~and for AND operator (no outer parentheses)
- ~or for OR operator (no outer parentheses)
- ~not for NOT operator
"""
from nocodb import filters


def test_or_with_two_filters():
    """Test Or logical operator with v3 format (no outer parentheses)."""
    filter1 = filters.EqFilter("column1", "value1")
    filter2 = filters.EqFilter("column2", "value2")
    or_filter = filters.Or(filter1, filter2)
    # v3 API: no outer parentheses on logical operators
    assert or_filter.get_where() == "(column1,eq,value1)~or(column2,eq,value2)"


def test_and_with_two_filters():
    """Test And logical operator with v3 format (no outer parentheses)."""
    filter1 = filters.And(filters.EqFilter("column1", "value1"))
    filter2 = filters.And(filters.EqFilter("column2", "value2"))
    and_filter = filters.And(filter1, filter2)
    # v3 API: no outer parentheses, flat structure
    assert and_filter.get_where() == "(column1,eq,value1)~and(column2,eq,value2)"


def test_not_filter():
    """Test Not logical operator."""
    basic_filter = filters.EqFilter("column", "value")
    not_filter = filters.Not(basic_filter)
    assert not_filter.get_where() == "~not(column,eq,value)"


def test_or_with_multiple_filters():
    """Test Or with more than two filters."""
    f1 = filters.EqFilter("a", "1")
    f2 = filters.EqFilter("b", "2")
    f3 = filters.EqFilter("c", "3")
    or_filter = filters.Or(f1, f2, f3)
    assert or_filter.get_where() == "(a,eq,1)~or(b,eq,2)~or(c,eq,3)"


def test_and_with_multiple_filters():
    """Test And with more than two filters."""
    f1 = filters.EqFilter("a", "1")
    f2 = filters.EqFilter("b", "2")
    f3 = filters.EqFilter("c", "3")
    and_filter = filters.And(f1, f2, f3)
    assert and_filter.get_where() == "(a,eq,1)~and(b,eq,2)~and(c,eq,3)"


def test_not_with_and_filter():
    """Test Not wrapping an And filter."""
    f1 = filters.EqFilter("status", "active")
    f2 = filters.EqFilter("role", "admin")
    and_filter = filters.And(f1, f2)
    not_filter = filters.Not(and_filter)
    assert not_filter.get_where() == "~not(status,eq,active)~and(role,eq,admin)"


def test_not_with_or_filter():
    """Test Not wrapping an Or filter."""
    f1 = filters.EqFilter("type", "spam")
    f2 = filters.EqFilter("type", "trash")
    or_filter = filters.Or(f1, f2)
    not_filter = filters.Not(or_filter)
    assert not_filter.get_where() == "~not(type,eq,spam)~or(type,eq,trash)"


def test_single_filter_in_and():
    """Test And with a single filter returns just that filter."""
    f1 = filters.EqFilter("column", "value")
    and_filter = filters.And(f1)
    assert and_filter.get_where() == "(column,eq,value)"


def test_single_filter_in_or():
    """Test Or with a single filter returns just that filter."""
    f1 = filters.EqFilter("column", "value")
    or_filter = filters.Or(f1)
    assert or_filter.get_where() == "(column,eq,value)"


def test_v3_operators_in_logical():
    """Test v3-specific operators (gte, lte) in logical combinations."""
    gte_filter = filters.GreaterOrEqualFilter("age", "18")
    lte_filter = filters.LessOrEqualFilter("age", "65")
    and_filter = filters.And(gte_filter, lte_filter)
    # v3 uses gte/lte (not ge/le) with ~and
    assert and_filter.get_where() == "(age,gte,18)~and(age,lte,65)"

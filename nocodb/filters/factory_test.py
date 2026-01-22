"""Tests for filter factory functions using v3 API patterns."""
from .factory import basic_filter_class_factory, raw_template_filter_class_factory


def test_basic_filter_class_factory():
    """Test basic filter factory with v3 eq operator."""
    FilterClass = basic_filter_class_factory('eq')
    assert FilterClass('column', 'value').get_where() == '(column,eq,value)'


def test_basic_filter_class_factory_v3_operators():
    """Test basic filter factory with v3-specific operators (gte, lte)."""
    # v3 API uses 'gte' instead of 'ge' and 'lte' instead of 'le'
    GteFilter = basic_filter_class_factory('gte')
    LteFilter = basic_filter_class_factory('lte')

    assert GteFilter('age', '18').get_where() == '(age,gte,18)'
    assert LteFilter('price', '100').get_where() == '(price,lte,100)'


def test_basic_filter_class_factory_nlike():
    """Test basic filter factory with v3 nlike operator (does not contain)."""
    NlikeFilter = basic_filter_class_factory('nlike')
    assert NlikeFilter('name', 'test').get_where() == '(name,nlike,test)'


def test_raw_template_filter_class_factory():
    """Test raw template filter factory."""
    FilterClassWithoutParams = raw_template_filter_class_factory('()')
    FilterClassWithParams = raw_template_filter_class_factory('({},{},{})')
    FilterClassWithKwargs = raw_template_filter_class_factory('({},{op},{})')
    assert FilterClassWithoutParams().get_where() == '()'
    assert FilterClassWithParams('1', '2', '3').get_where() == '(1,2,3)'
    assert FilterClassWithKwargs('1', '2', op='eq').get_where() == '(1,eq,2)'


def test_raw_template_filter_class_factory_v3_btw():
    """Test raw template filter factory for v3 between filter."""
    # v3 API 'btw' (between) operator format
    BtwFilter = raw_template_filter_class_factory('({},btw,{},{})')
    assert BtwFilter('date', '2024-01-01', '2024-12-31').get_where() == '(date,btw,2024-01-01,2024-12-31)'

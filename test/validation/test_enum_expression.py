"""
EnumExpressionのpytestテスト
"""

import pytest
from xlsx_value_picker.validation_common import ValidationContext
from xlsx_value_picker.config_loader import EnumExpression


@pytest.fixture
def context():
    return ValidationContext(
        cell_values={"color": "赤", "number": 1, "empty": "", "none": None},
        field_locations={"color": "Sheet1!A1", "number": "Sheet1!B1", "empty": "Sheet1!C1", "none": "Sheet1!D1"},
    )


def test_enum_valid(context):
    expr = EnumExpression(enum={"field": "color", "values": ["赤", "青", "緑"]})
    result = expr.validate(context, "{field}に無効な値が指定されています: {value}")
    assert result.is_valid


def test_enum_invalid(context):
    expr = EnumExpression(enum={"field": "color", "values": ["青", "緑"]})
    result = expr.validate(context, "{field}に無効な値が指定されています: {value}")
    assert not result.is_valid
    assert "colorに無効な値が指定されています" in result.error_message
    assert result.error_fields == ["color"]


def test_enum_with_number(context):
    expr = EnumExpression(enum={"field": "number", "values": [1, 2, 3]})
    result = expr.validate(context, "{field}に無効な値が指定されています")
    assert result.is_valid


def test_enum_with_none(context):
    expr = EnumExpression(enum={"field": "none", "values": ["値1", "値2"]})
    result = expr.validate(context, "{field}に無効な値が指定されています")
    assert result.is_valid  # Noneはスキップされる

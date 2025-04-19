"""
RequiredExpressionのpytestテスト
"""
import pytest
from xlsx_value_picker.validation_common import ValidationContext
from xlsx_value_picker.config_loader import RequiredExpression

@pytest.fixture
def context():
    return ValidationContext(
        cell_values={"name": "テスト", "empty": "", "none": None},
        field_locations={"name": "Sheet1!A1", "empty": "Sheet1!B1", "none": "Sheet1!C1", "missing": "Sheet1!D1"},
    )

def test_required_valid(context):
    expr = RequiredExpression(field="name", required=True)
    result = expr.validate(context, "{field}は必須項目です")
    assert result.is_valid

def test_required_invalid_empty_string(context):
    expr = RequiredExpression(field="empty", required=True)
    result = expr.validate(context, "{field}は必須項目です")
    assert not result.is_valid
    assert result.error_message == "emptyは必須項目です"
    assert result.error_fields == ["empty"]

def test_required_invalid_none(context):
    expr = RequiredExpression(field="none", required=True)
    result = expr.validate(context, "{field}は必須項目です")
    assert not result.is_valid
    assert result.error_fields == ["none"]

def test_required_invalid_missing(context):
    expr = RequiredExpression(field="missing", required=True)
    result = expr.validate(context, "{field}は必須項目です")
    assert not result.is_valid
    assert result.error_fields == ["missing"]

def test_not_required(context):
    expr = RequiredExpression(field="empty", required=False)
    result = expr.validate(context, "{field}は必須項目です")
    assert result.is_valid

    expr = RequiredExpression(field="none", required=False)
    result = expr.validate(context, "{field}は必須項目です")
    assert result.is_valid

    expr = RequiredExpression(field="missing", required=False)
    result = expr.validate(context, "{field}は必須項目です")
    assert result.is_valid

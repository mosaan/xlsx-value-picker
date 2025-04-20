"""
AllOfExpressionのpytestテスト
"""

import pytest

from xlsx_value_picker.config_loader import AllOfExpression, CompareExpression, RegexMatchExpression, RequiredExpression
from xlsx_value_picker.validation_common import ValidationContext


@pytest.fixture
def context():
    return ValidationContext(
        cell_values={"age": 25, "name": "テスト", "email": "test@example.com"},
        field_locations={"age": "Sheet1!A1", "name": "Sheet1!B1", "email": "Sheet1!C1"},
    )


def test_all_of_valid(context):
    expr = AllOfExpression(
        all_of=[
            CompareExpression(compare={"left": "age", "operator": ">=", "right": 20}),
            RequiredExpression(field="name", required=True),
            RegexMatchExpression(regex_match={"field": "email", "pattern": r"^[\w.-]+@[\w.-]+\.\w+$"}),
        ]
    )
    result = expr.validate(context, "すべての条件を満たしていません")
    assert result.is_valid


def test_all_of_invalid(context):
    expr = AllOfExpression(
        all_of=[
            CompareExpression(compare={"left": "age", "operator": ">=", "right": 30}),
            RequiredExpression(field="name", required=True),
        ]
    )
    result = expr.validate(context, "すべての条件を満たしていません")
    assert not result.is_valid
    assert result.error_message == "すべての条件を満たしていません"
    assert result.error_fields == ["age"]


def test_all_of_multiple_invalid(context):
    expr = AllOfExpression(
        all_of=[
            CompareExpression(compare={"left": "age", "operator": ">=", "right": 30}),
            RegexMatchExpression(regex_match={"field": "email", "pattern": r"^[\w]+$"}),
        ]
    )
    result = expr.validate(context, "すべての条件を満たしていません")
    assert not result.is_valid
    assert set(result.error_fields) == {"age", "email"}

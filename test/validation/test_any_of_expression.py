"""
AnyOfExpressionのpytestテスト
"""

import pytest

from xlsx_value_picker.config_loader import AnyOfExpression, CompareExpression, RegexMatchExpression, RequiredExpression
from xlsx_value_picker.validation_common import ValidationContext


@pytest.fixture
def context():
    return ValidationContext(
        cell_values={"age": 25, "name": "", "email": "invalid"},
        field_locations={"age": "Sheet1!A1", "name": "Sheet1!B1", "email": "Sheet1!C1"},
    )


def test_any_of_valid(context):
    expr = AnyOfExpression(
        any_of=[
            CompareExpression(compare={"left": "age", "operator": ">=", "right": 20}),
            RequiredExpression(field="name", required=True),
            RegexMatchExpression(regex_match={"field": "email", "pattern": r"^[\w.-]+@[\w.-]+\.\w+$"}),
        ]
    )
    result = expr.validate(context, "いずれかの条件を満たす必要があります")
    assert result.is_valid


def test_any_of_all_invalid(context):
    expr = AnyOfExpression(
        any_of=[
            CompareExpression(compare={"left": "age", "operator": ">=", "right": 30}),
            RequiredExpression(field="name", required=True),
            RegexMatchExpression(regex_match={"field": "email", "pattern": r"^[\w.-]+@[\w.-]+\.\w+$"}),
        ]
    )
    result = expr.validate(context, "いずれかの条件を満たす必要があります")
    assert not result.is_valid
    assert result.error_message == "いずれかの条件を満たす必要があります"
    assert set(result.error_fields) == {"age", "name", "email"}

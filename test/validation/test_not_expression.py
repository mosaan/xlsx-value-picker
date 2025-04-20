"""
NotExpressionのpytestテスト
"""

import pytest

from xlsx_value_picker.config_loader import CompareExpression, NotExpression
from xlsx_value_picker.validation_common import ValidationContext


@pytest.fixture
def context():
    return ValidationContext(
        cell_values={"age": 25, "status": "inactive"},
        field_locations={"age": "Sheet1!A1", "status": "Sheet1!B1"},
    )


def test_not_valid(context):
    # 修正：model_validateメソッドを使用してNotExpressionをインスタンス化
    expr = NotExpression.model_validate(
        {"not": CompareExpression(compare={"left": "age", "operator": "<", "right": 20})}
    )
    result = expr.validate(context, "条件に合致してはいけません")
    assert result.is_valid


def test_not_invalid(context):
    # 修正：model_validateメソッドを使用してNotExpressionをインスタンス化
    expr = NotExpression.model_validate(
        {"not": CompareExpression(compare={"left": "age", "operator": ">", "right": 20})}
    )
    result = expr.validate(context, "条件に合致してはいけません")
    assert not result.is_valid
    assert result.error_message == "条件に合致してはいけません"
    assert result.error_fields == []  # NotExpressionはエラーフィールドを指定しない

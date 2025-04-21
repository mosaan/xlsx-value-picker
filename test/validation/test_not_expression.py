"""
NotExpressionのpytestテスト
"""

# Expression関連は validation_expressions からインポート
from xlsx_value_picker.validation_expressions import CompareExpression, NotExpression


def test_not_valid(validation_context):  # Use the common fixture
    # The inner expression (age < 20) is False because age is 25.
    # So, NotExpression should be True.
    expr = NotExpression.model_validate(
        {"not": CompareExpression(compare={"left": "age", "operator": "<", "right": 20})}
    )
    result = expr.validate_in(validation_context, "条件に合致してはいけません")
    assert result.is_valid


def test_not_invalid(validation_context):  # Use the common fixture
    # The inner expression (age > 20) is True because age is 25.
    # So, NotExpression should be False.
    expr = NotExpression.model_validate(
        {"not": CompareExpression(compare={"left": "age", "operator": ">", "right": 20})}
    )
    result = expr.validate_in(validation_context, "条件に合致してはいけません")
    assert not result.is_valid
    assert result.error_message == "条件に合致してはいけません"
    # NotExpression itself doesn't add error fields, it relies on the inner expression's potential fields if needed,
    # but the logic here is just negation. The spec might need clarification if fields are expected.
    assert result.error_fields == []

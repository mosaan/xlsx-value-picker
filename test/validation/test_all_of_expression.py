"""
AllOfExpressionのpytestテスト
"""

# Expression関連は validation_expressions からインポート
from xlsx_value_picker.validation_expressions import (
    AllOfExpression,
    CompareExpression,
    RegexMatchExpression,
    RequiredFieldExpression,
)


def test_all_of_valid(validation_context):  # Use the common fixture
    expr = AllOfExpression(
        all_of=[
            CompareExpression(compare={"left_field": "age", "operator": ">=", "right": 20}),
            RequiredFieldExpression(field="name", required=True),
            RegexMatchExpression(regex_match={"field": "email", "pattern": r"^[\w.-]+@[\w.-]+\.\w+$"}),
        ]
    )
    result = expr.validate_in(validation_context, "すべての条件を満たしていません")
    assert result.is_valid


def test_all_of_invalid(validation_context):  # Use the common fixture
    # Modify context for this specific test case if needed
    validation_context.cell_values["age"] = 15  # Make age invalid
    expr = AllOfExpression(
        all_of=[
            CompareExpression(compare={"left_field": "age", "operator": ">=", "right": 30}),
            RequiredFieldExpression(field="name", required=True),
        ]
    )
    result = expr.validate_in(validation_context, "すべての条件を満たしていません")
    assert not result.is_valid
    assert result.error_message == "すべての条件を満たしていません"
    assert result.error_fields == ["age"]


def test_all_of_multiple_invalid(validation_context):  # Use the common fixture
    # Modify context for this specific test case
    validation_context.cell_values["age"] = 15  # Make age invalid
    validation_context.cell_values["email"] = "invalid-email"  # Make email invalid for the pattern below
    expr = AllOfExpression(
        all_of=[
            CompareExpression(compare={"left_field": "age", "operator": ">=", "right": 30}),
            RegexMatchExpression(
                regex_match={"field": "email", "pattern": r"^[\w]+$"}
            ),  # Pattern expects only word characters
        ]
    )
    result = expr.validate_in(validation_context, "すべての条件を満たしていません")
    assert not result.is_valid
    assert set(result.error_fields) == {"age", "email"}

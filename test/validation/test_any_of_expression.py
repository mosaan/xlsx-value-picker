"""
AnyOfExpressionのpytestテスト
"""

# Expression関連は validation_expressions からインポート
from xlsx_value_picker.validation_expressions import (
    AnyOfExpression,
    CompareExpression,
    RegexMatchExpression,
    RequiredFieldExpression,
)


def test_any_of_valid(validation_context):  # Use the common fixture
    # Ensure at least one condition is met by the default context
    expr = AnyOfExpression(
        any_of=[
            CompareExpression(compare={"left": "age", "operator": ">=", "right": 20}),  # This is true (25 >= 20)
            RequiredFieldExpression(field="name", required=True),  # This is true ("テスト" is not empty)
            RegexMatchExpression(regex_match={"field": "email", "pattern": r"^[\w.-]+@[\w.-]+\.\w+$"}),  # This is true
        ]
    )
    result = expr.validate_in(validation_context, "いずれかの条件を満たす必要があります")
    assert result.is_valid


def test_any_of_all_invalid(validation_context):  # Use the common fixture
    # Modify context to make all conditions invalid
    validation_context.cell_values["age"] = 15
    validation_context.cell_values["name"] = ""
    validation_context.cell_values["email"] = "invalid"
    expr = AnyOfExpression(
        any_of=[
            CompareExpression(compare={"left": "age", "operator": ">=", "right": 20}),  # False (15 < 20)
            RequiredFieldExpression(field="name", required=True),  # False ("" is empty)
            RegexMatchExpression(
                regex_match={"field": "email", "pattern": r"^[\w.-]+@[\w.-]+\.\w+$"}
            ),  # False ("invalid")
        ]
    )
    result = expr.validate_in(validation_context, "いずれかの条件を満たす必要があります")
    assert not result.is_valid
    assert result.error_message == "いずれかの条件を満たす必要があります"
    # In AnyOf, if all fail, which fields are reported? The design might need clarification.
    # Assuming it reports fields from all failed expressions for now.
    assert set(result.error_fields) == {"age", "name", "email"}

"""
Ruleのpytestテスト
"""

from xlsx_value_picker.config_loader import Rule  # Rule は config_loader に残る

# Expression関連は validation_expressions からインポート
from xlsx_value_picker.validator.validation_expressions import CompareExpression


def test_rule_valid(validation_context):  # Use the common fixture
    # The expression (age >= 20) is True because age is 25.
    rule = Rule(
        name="年齢チェック",
        expression=CompareExpression(compare={"left_field": "age", "operator": ">=", "right": 20}),
        error_message="{field}は20以上である必要があります",
    )
    result = rule.validate(validation_context)
    assert result.is_valid


def test_rule_invalid(validation_context):  # Use the common fixture
    # The expression (age >= 30) is False because age is 25.
    rule = Rule(
        name="年齢チェック",
        expression=CompareExpression(compare={"left_field": "age", "operator": ">=", "right": 30}),
        error_message="{field}は30以上である必要があります",
    )
    result = rule.validate(validation_context)
    assert not result.is_valid
    # The error message formatting depends on the expression's validate method
    # Assuming CompareExpression formats it like this:
    expected_message = "ageは30以上である必要があります"
    assert result.error_message == expected_message
    assert result.rule_name == "年齢チェック"
    assert result.error_fields == ["age"]
    assert result.error_locations == [validation_context.get_field_location("age")]

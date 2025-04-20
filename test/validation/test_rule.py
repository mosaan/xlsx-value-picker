"""
Ruleのpytestテスト
"""

import pytest

from xlsx_value_picker.config_loader import CompareExpression, Rule
from xlsx_value_picker.validation_common import ValidationContext


@pytest.fixture
def context():
    return ValidationContext(
        cell_values={"age": 25, "email": "test@example.com"},
        field_locations={"age": "Sheet1!A1", "email": "Sheet1!B1"},
    )


def test_rule_valid(context):
    rule = Rule(
        name="年齢チェック",
        expression=CompareExpression(compare={"left": "age", "operator": ">=", "right": 20}),
        error_message="{field}は20以上である必要があります",
    )
    result = rule.validate(context)
    assert result.is_valid


def test_rule_invalid(context):
    rule = Rule(
        name="年齢チェック",
        expression=CompareExpression(compare={"left": "age", "operator": ">=", "right": 30}),
        error_message="{field}は30以上である必要があります",
    )
    result = rule.validate(context)
    assert not result.is_valid
    assert result.error_message == "ageは30以上である必要があります"
    assert result.rule_name == "年齢チェック"

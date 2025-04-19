"""
ValidationEngineのpytestテスト
"""
import pytest
from unittest.mock import patch
from xlsx_value_picker.validation import ValidationEngine
from xlsx_value_picker.config_loader import Rule, CompareExpression, RegexMatchExpression

@patch('xlsx_value_picker.excel_processor.get_excel_values')
def test_validate(mock_get_excel_values):
    mock_get_excel_values.return_value = {"age": 25, "email": "invalid-email"}

    rule1 = Rule(
        name="年齢チェック",
        expression=CompareExpression(compare={"left": "age", "operator": ">=", "right": 20}),
        error_message="{field}は20以上である必要があります",
    )
    rule2 = Rule(
        name="メールアドレス形式チェック",
        expression=RegexMatchExpression(regex_match={"field": "email", "pattern": r"^[\w.-]+@[\w.-]+\.\w+$"}),
        error_message="{field}の形式が不正です: {value}",
    )
    engine = ValidationEngine([rule1, rule2])
    results = engine.validate("dummy.xlsx", {"age": "Sheet1!A1", "email": "Sheet1!B1"})
    assert len(results) == 1  # rule2のみがエラー
    assert results[0].error_fields == ["email"]
    assert "emailの形式が不正です" in results[0].error_message
    assert results[0].error_locations == ["Sheet1!B1"]

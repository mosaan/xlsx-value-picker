"""
CompareExpressionのテスト（pytestスタイル）
"""

import pytest

# Expression関連は validation_expressions からインポート
from xlsx_value_picker.validator.validation_expressions import CompareExpression


class TestCompareExpression:
    @pytest.mark.parametrize(
        "expression_params, expected_valid",
        [
            ({"left_field": "age", "operator": "==", "right": 25}, True),
            ({"left_field": "age", "operator": "==", "right": 30}, False),
            ({"left_field": "name", "operator": "==", "right": "テスト"}, True),
            ({"left_field": "name", "operator": "==", "right": "違うテスト"}, False),
            ({"left_field": "name", "operator": "==", "right_field": "name"}, True),
            ({"left_field": "age", "operator": "!=", "right": 30}, True),
            # ({"left_field": 30, "operator": "!=", "right": "age"}, True),
            ({"left_field": "age", "operator": "!=", "right": 25}, False),
            ({"left_field": "age", "operator": ">", "right": 20}, True),
            ({"left_field": "age", "operator": ">", "right": 25}, False),
            ({"left_field": "age", "operator": ">=", "right": 25}, True),
            ({"left_field": "age", "operator": ">=", "right": 26}, False),
            ({"left_field": "age", "operator": "<", "right": 30}, True),
            ({"left_field": "age", "operator": "<", "right": 25}, False),
            ({"left_field": "age", "operator": "<=", "right": 25}, True),
            ({"left_field": "age", "operator": "<=", "right": 24}, False),
            ({"left_field": "price", "operator": "==", "right": 1000}, True),
            ({"left_field": "price", "operator": ">", "right": 999}, True),
            ({"left_field": "price", "operator": "<", "right": 1001}, True),
            # === 直接Noneとの比較はできない仕様とする
            # ({"left_field": "none_value", "operator": "==", "right": None}, True),
            # ({"left_field": "none_value", "operator": "!=", "right": None}, False),
            # ({"left_field": "age", "operator": "==", "right": None}, False),
            ({"left_field": "missing_field", "operator": "==", "right": None}, True),
            ({"left_field": "missing_field", "operator": "!=", "right": None}, False),
        ],
    )
    def test_comparison_operators(self, validation_context, expression_params, expected_valid):
        """Test various comparison operators with different values."""
        expr = CompareExpression(compare=expression_params)
        result = expr.validate_in(validation_context, "{left_field} {operator} {right_value} の比較が失敗しました")
        assert result.is_valid == expected_valid
        if not expected_valid:
            assert result.error_fields == list(
                filter(
                    lambda v: v is not None, [expression_params.get("left_field"), expression_params.get("right_field")]
                )
            )

    def test_invalid_comparison_type_error(self, validation_context):
        """Test comparison that raises TypeError (e.g., comparing number and string)."""
        expr = CompareExpression(compare={"left_field": "age", "operator": ">", "right": "text"})
        result = expr.validate_in(validation_context, "比較エラー")
        assert not result.is_valid
        assert result.error_fields == ["age"]

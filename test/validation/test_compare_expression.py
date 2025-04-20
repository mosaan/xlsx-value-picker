"""
CompareExpressionのテスト（pytestスタイル）
"""

import pytest

from xlsx_value_picker.config_loader import CompareExpression


class TestCompareExpression:
    @pytest.mark.parametrize(
        "left_field, operator, right_value, expected_valid",
        [
            ("age", "==", 25, True),
            ("age", "==", 30, False),
            ("name", "==", "テスト", True),
            ("name", "==", "違うテスト", False),
            ("age", "!=", 30, True),
            ("age", "!=", 25, False),
            ("age", ">", 20, True),
            ("age", ">", 25, False),
            ("age", ">=", 25, True),
            ("age", ">=", 26, False),
            ("age", "<", 30, True),
            ("age", "<", 25, False),
            ("age", "<=", 25, True),
            ("age", "<=", 24, False),
            ("price", "==", 1000, True),
            ("price", ">", 999, True),
            ("price", "<", 1001, True),
            ("none_value", "==", None, True),
            ("none_value", "!=", None, False),
            ("age", "==", None, False),
            ("missing_field", "==", None, True),
            ("missing_field", "!=", None, False),
        ],
    )
    def test_comparison_operators(
        self, validation_context, left_field, operator, right_value, expected_valid
    ):
        """Test various comparison operators with different values."""
        expr = CompareExpression(compare={"left": left_field, "operator": operator, "right": right_value})
        result = expr.validate(
            validation_context, "{left_field} {operator} {right_value} の比較が失敗しました"
        )
        assert result.is_valid == expected_valid
        if not expected_valid:
            assert result.error_fields == [left_field]

    def test_invalid_comparison_type_error(self, validation_context):
        """Test comparison that raises TypeError (e.g., comparing number and string)."""
        expr = CompareExpression(compare={"left": "age", "operator": ">", "right": "text"})
        result = expr.validate(validation_context, "比較エラー")
        assert not result.is_valid
        assert result.error_fields == ["age"]

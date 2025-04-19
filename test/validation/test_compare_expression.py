"""
CompareExpressionのテスト（pytestスタイル）
"""
import pytest
from xlsx_value_picker.validation_common import ValidationContext
from xlsx_value_picker.config_loader import CompareExpression

class TestCompareExpression:
    @pytest.fixture(autouse=True)
    def setup_context(self):
        self.context = ValidationContext(
            cell_values={"age": 30, "price": 1000, "name": "テスト"},
            field_locations={"age": "Sheet1!A1", "price": "Sheet1!B1", "name": "Sheet1!C1"},
        )

    def test_equal_operator_valid(self):
        expr = CompareExpression(compare={"left": "age", "operator": "==", "right": 30})
        result = expr.validate(self.context, "値が一致しません: {left_field}={left_value}, 期待値={right_value}")
        assert result.is_valid

    def test_equal_operator_invalid(self):
        expr = CompareExpression(compare={"left": "age", "operator": "==", "right": 40})
        result = expr.validate(self.context, "値が一致しません: {left_field}={left_value}, 期待値={right_value}")
        assert not result.is_valid
        assert "値が一致しません" in result.error_message
        assert result.error_fields == ["age"]

    def test_not_equal_operator(self):
        expr = CompareExpression(compare={"left": "age", "operator": "!=", "right": 40})
        result = expr.validate(self.context, "エラーメッセージ")
        assert result.is_valid

        expr = CompareExpression(compare={"left": "age", "operator": "!=", "right": 30})
        result = expr.validate(self.context, "値が一致しています: {left_field}={left_value}")
        assert not result.is_valid
        assert "値が一致しています" in result.error_message

    def test_greater_than_operator(self):
        expr = CompareExpression(compare={"left": "age", "operator": ">", "right": 20})
        result = expr.validate(self.context, "エラーメッセージ")
        assert result.is_valid

        expr = CompareExpression(compare={"left": "age", "operator": ">", "right": 30})
        result = expr.validate(self.context, "値が小さすぎます: {left_field}={left_value}, 最小値={right_value}")
        assert not result.is_valid
        assert "値が小さすぎます" in result.error_message

    def test_greater_than_or_equal_operator(self):
        expr = CompareExpression(compare={"left": "age", "operator": ">=", "right": 30})
        result = expr.validate(self.context, "エラーメッセージ")
        assert result.is_valid

        expr = CompareExpression(compare={"left": "age", "operator": ">=", "right": 31})
        result = expr.validate(self.context, "値が小さすぎます: {left_field}={left_value}, 最小値={right_value}")
        assert not result.is_valid

    def test_less_than_operator(self):
        expr = CompareExpression(compare={"left": "age", "operator": "<", "right": 40})
        result = expr.validate(self.context, "エラーメッセージ")
        assert result.is_valid

        expr = CompareExpression(compare={"left": "age", "operator": "<", "right": 30})
        result = expr.validate(self.context, "値が大きすぎます: {left_field}={left_value}, 最大値={right_value}")
        assert not result.is_valid

    def test_less_than_or_equal_operator(self):
        expr = CompareExpression(compare={"left": "age", "operator": "<=", "right": 30})
        result = expr.validate(self.context, "エラーメッセージ")
        assert result.is_valid

        expr = CompareExpression(compare={"left": "age", "operator": "<=", "right": 29})
        result = expr.validate(self.context, "値が大きすぎます: {left_field}={left_value}, 最大値={right_value}")
        assert not result.is_valid

    def test_invalid_comparison(self):
        expr = CompareExpression(compare={"left": "name", "operator": "<", "right": 100})
        result = expr.validate(self.context, "比較が不可能です: {left_field}={left_value}")
        assert not result.is_valid

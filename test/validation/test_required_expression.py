"""
RequiredExpressionのpytestテスト
"""

import pytest

# Expression関連は validation_expressions からインポート
from xlsx_value_picker.validator.validation_expressions import RequiredExpression


@pytest.mark.parametrize(
    "field_spec, expected_valid, test_value_override",
    [
        # 単一フィールドのテスト
        ("name", True, None),  # 有効: フィールドが存在し、値が空でない
        ("empty_string", False, None),  # 無効: フィールドは存在するが空文字
        ("none_value", False, None),  # 無効: フィールドは存在するがNone
        ("missing_field", False, None),  # 無効: フィールドが存在しない
        # 複数フィールドのテスト
        (["name", "age"], True, None),  # 有効: 両方のフィールドが存在し、値が空でない
        (["name", "empty_string"], False, None),  # 無効: 片方が空文字
        (["name", "none_value"], False, None),  # 無効: 片方がNone
        (["name", "missing_field"], False, None),  # 無効: 片方が存在しない
        (["empty_string", "none_value"], False, None),  # 無効: 両方とも値が無効
    ],
)
def test_required_expression(validation_context, field_spec, expected_valid, test_value_override):
    """パラメータ化を使用して、RequiredExpressionの様々なシナリオをテストします。"""
    # テストケースで指定された場合、コンテキスト値をオーバーライド
    if test_value_override is not None:
        if isinstance(field_spec, str):
            validation_context.cell_values[field_spec] = test_value_override
        else:
            for field in field_spec:
                validation_context.cell_values[field] = test_value_override

    # 新形式のRequiredExpression構文を明示的に使用
    expr = RequiredExpression(required=field_spec)
    result = expr.validate_in(validation_context, "{field}は必須項目です")

    assert result.is_valid == expected_valid
    if not expected_valid:
        # 単一フィールドの場合
        if isinstance(field_spec, str):
            assert result.error_fields == [field_spec]
            expected_message = f"{field_spec}は必須項目です"
            assert result.error_message == expected_message
        # 複数フィールドの場合
        else:
            # 無効なフィールドのセットを作成
            error_fields_set = {
                field
                for field in field_spec
                if validation_context.get_field_value(field) is None or validation_context.get_field_value(field) == ""
            }
            # エラーフィールドのセットが一致するか確認
            assert set(result.error_fields) == error_fields_set

            # エラーメッセージに全てのエラーフィールド名が含まれているか確認
            for field in error_fields_set:
                assert field in result.error_message

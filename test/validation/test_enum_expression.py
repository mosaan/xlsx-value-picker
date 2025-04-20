"""
EnumExpressionのpytestテスト
"""

import pytest

from xlsx_value_picker.config_loader import EnumExpression
# Remove unused import: from xlsx_value_picker.validation_common import ValidationContext


# Remove the context fixture, it's now in conftest.py


@pytest.mark.parametrize(
    "field, values, expected_valid, test_value_override",
    [
        ("color", ["赤", "青", "緑"], True, None), # Valid case: '赤' is in the list
        ("color", ["黄", "紫"], False, None), # Invalid case: '赤' is not in the list
        ("number_value", [123, 456], True, None), # Valid case with number: 123 is in the list
        ("number_value", [789, 0], False, None), # Invalid case with number: 123 is not in the list
        ("none_value", ["A", "B", None], True, None), # Valid case with None: None is in the list
        ("none_value", ["A", "B"], False, None), # Invalid case with None: None is not in the list
        ("empty_string", ["", "Value"], True, None), # Valid case with empty string: "" is in the list
        ("empty_string", ["Value1", "Value2"], False, None), # Invalid case with empty string: "" is not in the list
        ("missing_field", ["A", "B"], False, None), # Invalid case: field is missing (value is None), None not in list
        ("missing_field", ["A", "B", None], True, None), # Valid case: field is missing (value is None), None is in list
    ],
)
def test_enum_expression(
    validation_context, field, values, expected_valid, test_value_override
):
    """Test EnumExpression with various scenarios using parametrization."""
    # Override context value if specified for the test case
    if test_value_override is not None:
        validation_context.cell_values[field] = test_value_override

    expr = EnumExpression(enum={"field": field, "values": values})
    result = expr.validate(validation_context, "{field}に無効な値が指定されています: {value}")

    assert result.is_valid == expected_valid
    if not expected_valid:
        assert result.error_fields == [field]
        # Check if the error message contains the invalid value
        # Note: The format might depend on how {value} is resolved for None/missing
        current_value = validation_context.get_field_value(field)
        expected_message_part = f"{field}に無効な値が指定されています: {current_value}"
        assert expected_message_part in result.error_message

# Remove individual test functions as they are covered by parametrization
# def test_enum_valid(context):
# def test_enum_invalid(context):
# def test_enum_with_number(context):
# def test_enum_with_none(context):

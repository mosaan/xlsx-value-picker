"""
RequiredExpressionのpytestテスト
"""

import pytest

from xlsx_value_picker.config_loader import RequiredExpression
# Remove unused import: from xlsx_value_picker.validation_common import ValidationContext


# Remove the context fixture, it's now in conftest.py


@pytest.mark.parametrize(
    "field, required, expected_valid, test_value_override",
    [
        # required=True cases
        ("name", True, True, None),         # Valid: field exists and is not empty
        ("empty_string", True, False, None), # Invalid: field exists but is empty string
        ("none_value", True, False, None),   # Invalid: field exists but is None
        ("missing_field", True, False, None),# Invalid: field does not exist in context
        # required=False cases
        ("name", False, True, None),         # Valid: field exists (value doesn't matter)
        ("empty_string", False, True, None), # Valid: field exists (value doesn't matter)
        ("none_value", False, True, None),   # Valid: field exists (value doesn't matter)
        ("missing_field", False, True, None),# Valid: field does not exist, but not required
    ],
)
def test_required_expression(
    validation_context, field, required, expected_valid, test_value_override
):
    """Test RequiredExpression with various scenarios using parametrization."""
    # Override context value if specified for the test case
    if test_value_override is not None:
        validation_context.cell_values[field] = test_value_override

    expr = RequiredExpression(field=field, required=required)
    result = expr.validate(validation_context, "{field}は必須項目です")

    assert result.is_valid == expected_valid
    if not expected_valid:
        assert result.error_fields == [field]
        expected_message = f"{field}は必須項目です"
        assert result.error_message == expected_message

# Remove individual test functions as they are covered by parametrization
# def test_required_valid(context):
# def test_required_invalid_empty_string(context):
# def test_required_invalid_none(context):
# def test_required_invalid_missing(context):
# def test_not_required(context):

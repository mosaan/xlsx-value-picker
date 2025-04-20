"""
RegexMatchExpressionのpytestテスト
"""

import pytest

# Expression関連は validation_expressions からインポート
from xlsx_value_picker.validation_expressions import RegexMatchExpression
from xlsx_value_picker.validation_common import ValidationContext, ValidationResult # これらは共通モジュールから


# Remove the context fixture, it's now in conftest.py


@pytest.mark.parametrize(
    "field, pattern, expected_valid, test_value_override",
    [
        ("email", r"^[\w.-]+@[\w.-]+\.\w+$", True, None), # Valid email
        ("invalid_email", r"^[\w.-]+@[\w.-]+\.\w+$", False, None), # Invalid email
        ("name", r"^テスト$", True, None), # Exact match
        ("name", r"^テス.$", True, None), # Wildcard match
        ("name", r"^T.*", False, None), # Case-sensitive mismatch
        ("number_value", r"^\d+$", True, None), # Number match (as string)
        ("number_value", r"^[a-z]+$", False, None), # Number mismatch (expects letters)
        ("empty_string", r".*", True, None), # Empty string matches any pattern allowing empty
        ("empty_string", r".+", False, None), # Empty string does not match pattern requiring at least one char
        ("none_value", r".*", False, None), # None value does not match (regex operates on strings)
        ("missing_field", r".*", False, None), # Missing field (None) does not match
    ],
)
def test_regex_match_expression(
    validation_context, field, pattern, expected_valid, test_value_override
):
    """Test RegexMatchExpression with various scenarios using parametrization."""
    # Override context value if specified for the test case
    if test_value_override is not None:
        validation_context.cell_values[field] = test_value_override

    expr = RegexMatchExpression(regex_match={"field": field, "pattern": pattern})
    result = expr.validate(validation_context, "{field}のフォーマットが不正です")

    assert result.is_valid == expected_valid
    if not expected_valid:
        assert result.error_fields == [field]

# Remove individual test functions as they are covered by parametrization
# def test_regex_match_valid(context):
# def test_regex_match_invalid(context):
# def test_regex_match_with_number(context):
# def test_regex_match_with_empty(context):
# def test_regex_match_with_none(context):

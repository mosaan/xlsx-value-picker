"""
RegexMatchExpressionのpytestテスト
"""

import pytest
from xlsx_value_picker.validation_common import ValidationContext
from xlsx_value_picker.config_loader import RegexMatchExpression


@pytest.fixture
def context():
    return ValidationContext(
        cell_values={
            "email": "test@example.com",
            "phone": "090-1234-5678",
            "number": 12345,
            "empty": "",
            "none": None,
        },
        field_locations={
            "email": "Sheet1!A1",
            "phone": "Sheet1!B1",
            "number": "Sheet1!C1",
            "empty": "Sheet1!D1",
            "none": "Sheet1!E1",
        },
    )


def test_regex_match_valid(context):
    expr = RegexMatchExpression(regex_match={"field": "email", "pattern": r"^[\w.-]+@[\w.-]+\.\w+$"})
    result = expr.validate(context, "{field}のフォーマットが不正です")
    assert result.is_valid


def test_regex_match_invalid(context):
    expr = RegexMatchExpression(regex_match={"field": "phone", "pattern": r"^\d{10,11}$"})
    result = expr.validate(context, "{field}のフォーマットが不正です: {value}")
    assert not result.is_valid
    assert "phoneのフォーマットが不正です" in result.error_message
    assert result.error_fields == ["phone"]


def test_regex_match_with_number(context):
    expr = RegexMatchExpression(regex_match={"field": "number", "pattern": r"^\d{5}$"})
    result = expr.validate(context, "{field}のフォーマットが不正です")
    assert result.is_valid  # 文字列に変換されてマッチする


def test_regex_match_with_empty(context):
    expr = RegexMatchExpression(regex_match={"field": "empty", "pattern": r".*"})
    result = expr.validate(context, "{field}のフォーマットが不正です")
    assert result.is_valid  # 空文字列はスキップされる


def test_regex_match_with_none(context):
    expr = RegexMatchExpression(regex_match={"field": "none", "pattern": r".*"})
    result = expr.validate(context, "{field}のフォーマットが不正です")
    assert result.is_valid  # Noneはスキップされる

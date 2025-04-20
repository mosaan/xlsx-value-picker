"""
ValidationResultのテスト（pytestスタイル）
"""

import pytest
from xlsx_value_picker.validation_common import ValidationResult


class TestValidationResult:
    def test_post_init_with_valid_result(self):
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert result.error_message is None
        assert result.error_fields is None
        assert result.error_locations is None
        assert result.severity == "error"

    def test_post_init_with_invalid_result(self):
        result = ValidationResult(is_valid=False, error_message="エラーが発生しました")
        assert result.is_valid is False
        assert result.error_message == "エラーが発生しました"
        assert result.error_fields == []
        assert result.error_locations == []
        assert result.severity == "error"

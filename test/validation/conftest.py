"""
pytest fixtures for validation tests.
"""

import pytest

from xlsx_value_picker.validation_common import ValidationContext


@pytest.fixture
def validation_context():
    """Provides a common ValidationContext for validation tests."""
    return ValidationContext(
        cell_values={
            "name": "テスト",
            "age": 25,
            "email": "test@example.com",
            "invalid_email": "invalid-email",
            "price": 1000,
            "color": "赤",
            "status": "active",
            "empty_string": "",
            "none_value": None,
            "number_value": 123,
            "selection": "その他",
            "comment": None,  # 初期値はNone
        },
        field_locations={
            "name": "Sheet1!A1",
            "age": "Sheet1!B1",
            "email": "Sheet1!C1",
            "invalid_email": "Sheet1!C2",
            "price": "Sheet1!D1",
            "color": "Sheet1!E1",
            "status": "Sheet1!F1",
            "empty_string": "Sheet1!G1",
            "none_value": "Sheet1!H1",
            "number_value": "Sheet1!I1",
            "missing_field": "Sheet1!J1",  # 存在しないフィールドの場所
            "selection": "Sheet1!K1",
            "comment": "Sheet1!L1",
        },
    )
